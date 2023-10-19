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


class SwapFixedLeg:
    _valuation_vars = ['_accrual_start', '_accrual_end', '_accrual_days',
                       '_accrual_factor', '_cashflows', '_dt', '_df', '_pv', '_cum_pv']
    _instrument_vars = ['_start_date', '_maturity_date', '_coupon_rate', '_notional', '_principal', '_payment_lag',
                        '_freq_type', '_day_count_type', '_calendar_type', '_bus_day_adj_type', '_date_gen_rule_type']
    _derived_vars = ['_calendar', '_day_count', '_payment_dates']

    def __init__(self,
                 start_date: Date,
                 maturity_date_or_tenor: tuple((Date, str)),
                 coupon_rate: float,
                 notional: float = Literal.ONE_MILLION.value,
                 principal: float = 0.,
                 payment_lag: int = 0,
                 freq_type: FrequencyTypes = FrequencyTypes.SEMI_ANNUAL,
                 day_count_type: DayCountTypes = DayCountTypes.ACT_360,
                 calendar_type: CalendarTypes = CalendarTypes.WEEKEND,
                 bus_day_adj_type: BusDayAdjustTypes = BusDayAdjustTypes.FOLLOWING,
                 date_gen_rule_type: DateGenRuleTypes = DateGenRuleTypes.BACKWARD):
        self._start_date = start_date
        self._coupon_rate = coupon_rate
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

        # generate adjusted payment dates
        self._payment_dates = PaymentSchedule(self._start_date,
                                              self._maturity_date,
                                              self._freq_type,
                                              self._calendar_type,
                                              self._bus_day_adj_type,
                                              self._date_gen_rule_type).payment_dates

        # maturity date is adjusted after the schedule is generated
        self._maturity_date = self._calendar.adjust(self._maturity_date, self._bus_day_adj_type)
        self._accrual_start = []
        self._accrual_end = []
        self._accrual_days = []
        self._accrual_factor = []
        self._cashflows = []
        self._dt = []
        self._df = []
        self._pv = []
        self._cum_pv = []
        self.generate_cashflows()

    def generate_cashflows(self) -> None:
        """Generate cashflows"""
        num_payments = len(self._payment_dates)
        self._accrual_start.append(self._start_date)
        for i in range(num_payments):
            self._accrual_end.append(self._payment_dates[i])
            days, frac = self._day_count.days_between(self._accrual_start[-1], self._accrual_end[-1])
            self._accrual_days.append(days)
            self._accrual_factor.append(frac)
            # for the last payment, no need to add the next accrual start date
            if i != num_payments - 1:
                self._accrual_start.append(self._payment_dates[i])
            self._cashflows.append(self._notional * self._coupon_rate * frac)

    @property
    def cashflows_pv(self) -> list:
        """Return the cashflows present values"""
        return self._pv

    @ property
    def maturity_date(self) -> Date:
        """Return the maturity date"""
        return self._maturity_date

    def _reset_valuation_vars(self):
        """Reset the valuation intermediate variables"""
        for var in self._valuation_vars:
            setattr(self, var, [])

    @lru_cache(maxsize=1)
    def value(self,
              valuation_date: Date,
              discount_curve: BaseCurve) -> float:
        """Instrument valuation

        Args:
            valuation_date (Date): valuation date
            discount_curve (BaseCurve): discount curve
        """
        self._dt = [discount_curve.year_frac(valuation_date, date) for date in self._payment_dates]
        self._df = [discount_curve.eval(dt) if dt >= 0 else 0. for dt in self._dt]
        self._pv = [cf * df if df > 0 else 0. for cf, df in zip(self._cashflows, self._df)]
        self._cum_pv = [sum(self._pv[:i + 1]) for i in range(len(self._pv))]
        return sum(self._pv)

    def print_cashflows(self):
        """Print the cashflows intermediate results"""
        d = {'PAYMENT_DATE': self._payment_dates,
             'ACCRUAL_START': self._accrual_start,
             'ACCRUAL_END': self._accrual_end,
             'ACCRUAL_DAYS': self._accrual_days,
             'ACCRUAL_FACTOR': self._accrual_factor,
             'CASHFLOW': self._cashflows}
        print(prettyTableByColumn(d))

    def print_valuation(self):
        """Print the valuation intermediate results"""
        if self._dt is None:
            raise ValueError("You must call value() first")
        d = {'PAYMENT_DATE': self._payment_dates,
             'ACCRUAL_START': self._accrual_start,
             'ACCRUAL_END': self._accrual_end,
             'ACCRUAL_DAYS': self._accrual_days,
             'ACCRUAL_FACTOR': self._accrual_factor,
             'CASHFLOW': self._cashflows,
             'DT': self._dt,
             'DF': self._df,
             'PV': self._pv,
             'CUM_PV': self._cum_pv}
        print(prettyTableByColumn(d))

    def __repr__(self) -> str:
        return prettyTableByRow(self.as_dict())

    def as_dict(self) -> dict:
        d = {
            "INSTRUMENT": "SWAP_FIXED_LEG",
            "START_DATE": self._start_date,
            "MATURITY_DATE": self._maturity_date,
            "COUPON_RATE": self._coupon_rate,
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

    def __hash__(self) -> int:
        return hash(self.as_tuple())

    def debug_attrs_match(self) -> bool:
        """Check if the instance attributes match the class attributes we predefined"""
        for attrs in self.__dict__:
            if attrs in self._valuation_vars or attrs in self._instrument_vars or attrs in self._derived_vars:
                continue
            else:
                raise ValueError(f"Unknown attribute {attrs}")
        return True

    def pv01(self, valuation_date: Date, discount_curve: BaseCurve) -> float:
        """Calculate the PV01"""
        pv = self.value(valuation_date, discount_curve)
        coupon_per_year = self._coupon_rate * self._notional
        return abs(pv / coupon_per_year)
