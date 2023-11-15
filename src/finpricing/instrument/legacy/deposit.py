# from math import log, exp, ceil
from ..utils.date import Date
from ..utils.bus_day_adj import BusDayAdjustTypes
from ..utils.holiday import CalendarTypes
from ..utils.calendar import Calendar
from ..utils.day_count import DayCountTypes, DayCount
from ..utils.literal import Literal
from ..market.legacy.discount_curve import DiscountCurve
from ..utils.tools import dict_to_obj_str


class Deposit:
    def __init__(self,
                 start_date: Date,
                 maturity_date_or_tenor: tuple((Date, str)),
                 deposit_rate: float,
                 notional: float = Literal.ONE_HUNDRED.value,
                 day_count_type: DayCountTypes = DayCountTypes.ACT_360,
                 calendar_type: CalendarTypes = CalendarTypes.WEEKEND,
                 bus_day_adj_type: BusDayAdjustTypes = BusDayAdjustTypes.FOLLOWING):

        self._start_date = start_date
        self._deposit_rate = deposit_rate
        self._notional = notional
        self._bus_day_adj_type = bus_day_adj_type
        if isinstance(maturity_date_or_tenor, Date):
            self._maturity_date = maturity_date_or_tenor
        elif isinstance(maturity_date_or_tenor, str):
            self._maturity_date = start_date.add_tenor(maturity_date_or_tenor)
        else:
            raise TypeError("maturity_date_or_tenor must be either Date or str")
        # derived attributes
        self._calendar = Calendar(calendar_type)
        self._day_count = DayCount(day_count_type)
        # adjust the maturity date
        self._maturity_date = self._calendar.adjust(self._maturity_date, self._bus_day_adj_type)

    @property
    def start_date(self) -> Date:
        """Return the start date"""
        return self._start_date

    @start_date.setter
    def start_date(self, start_date: Date) -> None:
        """Set the start date"""
        self._start_date = start_date

    @property
    def maturity_date(self) -> Date:
        """Return the maturity date"""
        return self._maturity_date

    @maturity_date.setter
    def maturity_date(self, maturity_date: Date) -> None:
        """Set the maturity date"""
        self._maturity_date = maturity_date

    @property
    def day_count_func(self) -> DayCount:
        """Return the day count function"""
        return self._day_count

    @property
    def accrual_days_factor(self) -> float:
        """Return the accrual factor between the start date and the maturity date"""
        return self._day_count.days_between(self._start_date, self._maturity_date)

    @property
    def fwd_discount_factor(self) -> float:
        """Return the forward discount factor from the start date to the maturity date

        NOTE:
            1. This is not to discount back to the valuation date!
            2. This factor is based on day count type of the deposit object itself.
        """
        return 1 / (1 + self._deposit_rate * self.accrual_days_factor[1])

    def value(self, valuation_date: Date, discount_curve: DiscountCurve) -> float:
        """Return the value of the deposit

        TODO:
            It is unclear which date is this discounted to.
        """
        time_to_settlement = self._day_count.year_fraction(valuation_date, self._start_date)
        time_to_maturity = self._day_count.year_fraction(valuation_date, self._maturity_date)
        accrual_factor = self.accrual_days_factor[1]
        df_settlement = discount_curve.get_discount_factor(time_to_settlement)
        df_maturity = discount_curve.get_discount_factor(time_to_maturity)
        payoff = (1 + self._deposit_rate * accrual_factor) * self._notional
        value = payoff * df_maturity / df_settlement
        return value

    def __repr__(self) -> str:
        """Return the string representation of the object"""
        repr_dict = {
            "OBJECT TYPE": type(self).__name__,
            "START DATE": self._start_date,
            "MATURITY DATE": self._maturity_date,
            "DEPOSIT RATE": self._deposit_rate,
            "NOTIONAL": self._notional,
            "ACCRUAL DAYS FACTOR": self.accrual_days_factor,
            "DAY COUNT TYPE": self._day_count,
            "CALENDAR": self._calendar,
            "BUS DAY ADJ TYPE": self._bus_day_adj_type
        }
        return dict_to_obj_str(repr_dict)
