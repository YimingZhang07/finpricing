# from math import log, exp, ceil
from ..utils.date import Date
from ..utils.bus_day_adj import BusDayAdjustTypes
from ..utils.holiday import CalendarTypes
from ..utils.calendar import Calendar, DateGenRuleTypes
from ..utils.frequency import FrequencyTypes
from ..utils.error import NotSupportedError


class PaymentSchedule:
    """Generate a list of adjusted payment dates according to the given parameters.

    Aims to provide most naive implementation, independent of any instrument.
    """

    def __init__(self,
                 start_date: Date,
                 maturity_date_or_tenor: tuple((Date, str)),
                 freq_type: FrequencyTypes = FrequencyTypes.QUARTERLY,
                 calendar_type: CalendarTypes = CalendarTypes.WEEKEND,
                 bus_day_adj_type: BusDayAdjustTypes = BusDayAdjustTypes.FOLLOWING,
                 date_gen_rule_type: DateGenRuleTypes = DateGenRuleTypes.BACKWARD,
                 adjust_maturity_date: bool = False,
                 extended: bool = False):
        """
        NOTE
            1. when generating raw payment schedule (using backward or forward), the maturity date is not adjusted. This will be adjusted to business day after the raw schedule is generated.
            2. If the first payment date is the start date, it is not included in the payment schedule.

        Args:
            extended: If True, In a FORWARD schedule, the start date and NCD after maturity date are included. In a BACKWARD schedule, the PCD before start date is included.
        """
        self._start_date = start_date
        if isinstance(maturity_date_or_tenor, Date):
            self._maturity_date = maturity_date_or_tenor
        elif isinstance(maturity_date_or_tenor, str):
            self._maturity_date = start_date.add_tenor(maturity_date_or_tenor)
        else:
            raise NotSupportedError("maturity_date_or_tenor must be either Date or str")
        self._freq_type = freq_type
        self._calendar = Calendar(calendar_type)
        self._bus_day_adj_type = bus_day_adj_type
        self._date_gen_rule_type = date_gen_rule_type
        self._extended = extended
        # adjust the maturity date before generating payment dates?
        if adjust_maturity_date:
            self._maturity_date = self._calendar.adjust(self._maturity_date, self._bus_day_adj_type)
        # declare other attributes
        self._payment_dates = []
        # generate payment dates
        self._generate_adj_payment_dates()

    @property
    def payment_dates(self) -> list:
        """Return the payment dates"""
        return self._payment_dates

    def _generate_unadj_payment_dates(self) -> list:
        """Generate unadjusted payment dates"""
        if self._date_gen_rule_type == DateGenRuleTypes.FORWARD:
            payment_dates = []
            next_date = self._start_date
            interval = int(12 / self._freq_type.value)
            while next_date <= self._maturity_date:
                payment_dates.append(next_date)
                next_date = next_date.add_months(interval)
            # add the next coupon date after maturity date
            payment_dates.append(next_date)
            return payment_dates if self._extended else payment_dates[1:-1]
        elif self._date_gen_rule_type == DateGenRuleTypes.BACKWARD:
            payment_dates = []
            next_date = self._maturity_date
            interval = int(12 / self._freq_type.value)
            while next_date >= self._start_date:
                payment_dates.append(next_date)
                next_date = next_date.add_months(-interval)
            # add the previous coupon date
            payment_dates.append(next_date)
            return payment_dates[::-1] if self._extended else payment_dates[::-1][1:]
        else:
            raise NotSupportedError(
                "Generate payment dates failed as DateGenRuleTypes is not supported")

    def _generate_adj_payment_dates(self) -> list:
        """Return a list of adjusted payment dates"""
        unadj_payment_dates = self._generate_unadj_payment_dates()
        adj_payment_dates = [self._calendar.adjust(date, self._bus_day_adj_type) for date in unadj_payment_dates]
        # remove the first payment date if it is the start date, there is no cashflow on the start date
        if adj_payment_dates[0] == self._start_date:
            adj_payment_dates = adj_payment_dates[1:]
        self._payment_dates = adj_payment_dates
        return adj_payment_dates

    def __repr__(self) -> str:
        """Return the string representation of the object"""
        return str(self.payment_dates)
