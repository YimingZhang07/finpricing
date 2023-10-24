from ..utils.date import Date
from ..utils.literal import Literal
from ..utils.day_count import DayCountTypes, DayCount
from ..utils.holiday import CalendarTypes
from ..utils.calendar import Calendar, DateGenRuleTypes
from ..utils.frequency import FrequencyTypes
from ..utils.bus_day_adj import BusDayAdjustTypes
from ..utils.tools import prettyTableByColumn, prettyTableByRow, ClassUtil
from ..utils.payment_schedule import PaymentSchedule
from typing import Union
import datetime

class FixedCouponLeg(ClassUtil):
    def __init__(self,
                 start_date: Union[Date, datetime.date],
                 maturity_date_or_tenor: Union[Date, datetime.date, str],
                 coupon_rate: float,
                 notional: float = Literal.ONE_HUNDRED.value,
                 freq_type: FrequencyTypes = FrequencyTypes.SEMI_ANNUAL,
                 day_count_type: DayCountTypes = DayCountTypes.THIRTY_360,
                 calendar_type: CalendarTypes = CalendarTypes.WEEKEND,
                 bus_day_adj_type: BusDayAdjustTypes = BusDayAdjustTypes.NONE,
                 date_gen_rule_type: DateGenRuleTypes = DateGenRuleTypes.BACKWARD) -> None:
        
        self.save_attributes(ignore=["start_date", "maturity_date_or_tenor"])
        self.resolve_dates(start_date, maturity_date_or_tenor)
        
        # derived attributes
        self.calendar = Calendar(self.calendar_type)
        self.day_counter = DayCount(self.day_count_type)
        
        # generate schedule
        self._payment_schedule_helper = PaymentSchedule(self.start_date,
                                                        self.maturity_date,
                                                        self.freq_type,
                                                        self.calendar_type,
                                                        self.bus_day_adj_type,
                                                        self.date_gen_rule_type,
                                                        extended=True).payment_dates
        
        self.maturity_date = self.calendar.adjust(self.maturity_date, self.bus_day_adj_type)
        self.payment_dates = []
        self.accrual_start = []
        self.accrual_end = []
        self.accrual_days = []
        self.accrual_factors = []
        self.payment_amounts = []
        self.generate_cashflows()
        
    @property
    def cashflows(self) -> list:
        return list(zip(self.payment_dates, self.payment_amounts))
        
    def generate_cashflows(self) -> None:
        """Generate the cashflows for the fixed coupon leg"""
        self.payment_dates = self._payment_schedule_helper[1:]
        self.accrual_start = self._payment_schedule_helper[:-1]
        self.accrual_end = self._payment_schedule_helper[1:]
        
        num_payments = len(self.payment_dates)
        for i in range(num_payments):
            days, frac = self.day_counter.days_between(self.accrual_start[i], self.accrual_end[i])
            self.accrual_days.append(days)
            self.accrual_factors.append(frac)
            self.payment_amounts.append(self.coupon_rate * self.accrual_factors[i] * self.notional)
            
    def print_cashflows(self):
        d = {   "Payment Date": self.payment_dates,
                "Cashflow": self.cashflows,
                "Accrual Start": self.accrual_start,
                "Accrual End": self.accrual_end,
                "Accrual Days": self.accrual_days,
                "Accrual Factor": self.accrual_factors  }
        print(prettyTableByColumn(d))