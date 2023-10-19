from functools import lru_cache
from ..utils.date import Date
from ..utils.bus_day_adj import BusDayAdjustTypes
from ..utils.holiday import CalendarTypes
from ..utils.calendar import Calendar, DateGenRuleTypes
from ..utils.day_count import DayCountTypes, DayCount
from ..utils.frequency import FrequencyTypes
from ..utils.literal import Literal
from ..utils.payment_schedule import PaymentSchedule
from ..utils.error import NotSupportedError
from ..utils.tools import prettyTableByColumn, prettyTableByRow
from ..market.curve import BaseCurve


class SwapFloatLeg:
    # reference: https://stackoverflow.com/questions/57439169/best-way-to-intelligently-reset-memoized-property-values-in-python-when-depend
    # storing the valuation variables to facilitate reset
    # TODO: the payment dates should be stored in the valuation variables... but it will be reset, which leads failure of value() function
    _valuation_vars = ['_accrual_start', '_accrual_end', '_accrual_days',
                       '_accrual_factor', '_cashflows', '_float_rate', '_dt', '_df', '_pv', '_cum_pv']
    _instrument_vars = ['_start_date', '_maturity_date', '_spread', '_notional', '_principal', '_payment_lag',
                        '_freq_type', '_day_count_type', '_calendar_type', '_bus_day_adj_type', '_date_gen_rule_type']
    _derived_vars = ['_calendar', '_day_count', '_payment_dates']

    def __init__(self,
                 start_date: Date,
                 maturity_date_or_tenor: tuple((Date, str)),
                 spread: float,
                 notional: float = Literal.ONE_MILLION.value,
                 principal: float = 0.,
                 payment_lag: int = 0,
                 freq_type: FrequencyTypes = FrequencyTypes.QUARTERLY,
                 day_count_type: DayCountTypes = DayCountTypes.ACT_360,
                 calendar_type: CalendarTypes = CalendarTypes.WEEKEND,
                 bus_day_adj_type: BusDayAdjustTypes = BusDayAdjustTypes.FOLLOWING,
                 date_gen_rule_type: DateGenRuleTypes = DateGenRuleTypes.BACKWARD):
        self._start_date = start_date
        self._spread = spread
        self._notional = notional
        self._principal = principal
        self._payment_lag = payment_lag
        if isinstance(maturity_date_or_tenor, Date):
            self._maturity_date = maturity_date_or_tenor
        elif isinstance(maturity_date_or_tenor, str):
            self._maturity_date = start_date.add_tenor(maturity_date_or_tenor)
        else:
            raise NotSupportedError("maturity_date_or_tenor must be either Date or str")
        self._calendar_type = calendar_type
        self._day_count_type = day_count_type
        self._freq_type = freq_type
        self._bus_day_adj_type = bus_day_adj_type
        self._date_gen_rule_type = date_gen_rule_type

        # derived attributes
        self._calendar = Calendar(calendar_type)
        self._day_count = DayCount(day_count_type)

        # generate payment dates (adjusted)
        self._payment_dates = PaymentSchedule(self._start_date,
                                              self._maturity_date,
                                              self._freq_type,
                                              self._calendar_type,
                                              self._bus_day_adj_type,
                                              self._date_gen_rule_type).payment_dates
        # NOTE: below initialization is not needed, and can be substituted by _reset_valuation_vars()
        # This is for the system to recognize the attributes
        self._accrual_start = []
        self._accrual_end = []
        self._accrual_days = []
        self._accrual_factor = []
        self._cashflows = []
        self._float_rate = []
        self._dt = []
        self._df = []
        self._pv = []
        self._cum_pv = []

    @property
    def spread(self) -> list:
        return self._spread

    @spread.setter
    def spread(self, spread: float):
        if not isinstance(spread, float):
            raise ValueError("spread must be float")
        self._spread = spread

    def _reset_valuation_vars(self):
        """Reset the valuation intermediate variables"""
        for var in self._valuation_vars:
            setattr(self, var, [])

    @lru_cache(maxsize=1)
    def value(self,
              valuation_date: Date,
              discount_curve: BaseCurve,
              index_curve: BaseCurve) -> float:
        """Calculate the fair value of the float leg

        NOTE: the value function is decorated with lru_cache. Relevant work is done by defining __hash__ for all dependent objects.
        # When this function is called instead of the cached result, the intermediate variables in valuation are reset.
        # The maximum size of the cache is 1, which means only the latest result is cached.
        # This is because even earlier valuation was cached before, we still need correct intermediate variables. So we will only cache the latest only.

        Args:
            valuation_date (Date): valuation date
            discount_curve (BaseCurve): discount curve
            index_curve (BaseCurve): index curve
        Returns:
            float: fair value
        """
        self._reset_valuation_vars()
        self._accrual_start.append(self._start_date)
        valuation_df = discount_curve.df(valuation_date)
        for date in self._payment_dates:
            # accrual is controled by the instrument day count convention
            self._accrual_end.append(date)
            days, factor = self._day_count.days_between(self._accrual_start[-1], self._accrual_end[-1])
            self._accrual_days.append(days)
            self._accrual_factor.append(factor)
            # float rate is controled by the index day count convention
            accrual_start_df = index_curve.df(self._accrual_start[-1])
            accrual_end_df = index_curve.df(self._accrual_end[-1])
            index_tau = index_curve.year_frac(self._accrual_start[-1], self._accrual_end[-1])
            float_rate = (accrual_start_df / accrual_end_df - 1) / index_tau + self._spread
            self._float_rate.append(float_rate)
            # calculate the cashflow
            self._cashflows.append(self._notional * float_rate * self._accrual_factor[-1])
            # discount the cashflow but depends on whether payment date is after the valuation date
            self._dt.append(discount_curve.dt(date))
            if self._dt[-1] <= 0:
                self._df.append(0.)
            else:
                self._df.append(discount_curve.df(date) / valuation_df)
            self._pv.append(self._cashflows[-1] * self._df[-1])
            # update accrual start except for the last payment date
            if date != self._payment_dates[-1]:
                self._accrual_start.append(date)
        self._cum_pv = [sum(self._pv[:i + 1]) for i in range(len(self._pv))]
        return sum(self._pv)

    def print_cashflows(self):
        """Print the cashflows intermediate results"""
        # if len(self._dt) is 0, essentially means value() is not called
        if len(self._dt) == 0:
            raise ValueError("You must call value() before calling print_cashflows()")
        d = {'PAYMENT_DATE': self._payment_dates,
             'ACCRUAL_START': self._accrual_start,
             'ACCRUAL_END': self._accrual_end,
             'ACCRUAL_DAYS': self._accrual_days,
             'ACCRUAL_FACTOR': self._accrual_factor,
             'FLOAT_RATE': self._float_rate,
             'CASHFLOW': self._cashflows}
        print(prettyTableByColumn(d))

    def print_valuation(self):
        """Print the valuation intermediate results"""
        if self._dt is None:
            raise ValueError("You must call value() before calling print_valuation()")
        d = {'PAYMENT_DATE': self._payment_dates,
             'ACCRUAL_START': self._accrual_start,
             'ACCRUAL_END': self._accrual_end,
             'ACCRUAL_DAYS': self._accrual_days,
             'ACCRUAL_FACTOR': self._accrual_factor,
             'FLOAT_RATE': self._float_rate,
             'CASHFLOW': self._cashflows,
             'DT': self._dt,
             'DF': self._df,
             'PV': self._pv,
             'CUM_PV': self._cum_pv}
        print(prettyTableByColumn(d))

    def as_dict(self) -> dict:
        d = {
            "INSTRUMENT": "SWAP_FLOAT_LEG",
            "START_DATE": self._start_date,
            "MATURITY_DATE": self._maturity_date,
            "SPREAD": self._spread,
            "NOTIONAL": self._notional,
            "PRINCIPAL": self._principal,
            "PAYMENT_LAG": self._payment_lag,
            "FREQUENCY": self._freq_type,
            "DAY_COUNT": self._day_count_type,
            "CALENDAR": self._calendar_type,
            "BUS_DAY_ADJ": self._bus_day_adj_type,
            "DATE_GEN_RULE": self._date_gen_rule_type,
        }
        return d

    def as_tuple(self) -> tuple:
        return tuple(self.as_dict().values())

    def __repr__(self) -> str:
        return prettyTableByRow(self.as_dict())

    def __hash__(self) -> int:
        """Hash function for the class"""
        return hash(self.as_tuple())

    def debug_attrs_match(self) -> bool:
        """Check if the instance attributes match the class attributeswe predefined"""
        for attrs in self.__dict__:
            if attrs in self._valuation_vars or attrs in self._instrument_vars or attrs in self._derived_vars:
                continue
            else:
                raise ValueError(f"Unknown attribute {attrs}")
        return True
