from enum import Enum
from .error import NotSupportedError
from .date import Date
from .bus_day_adj import BusDayAdjustTypes
from .holiday import Holiday, CalendarTypes


class DateGenRuleTypes(Enum):
    FORWARD = 1
    BACKWARD = 2


class Calendar:
    def __init__(self, calendarType: CalendarTypes) -> None:
        """
        I think holiday should be a class dependent on the calendar type.
        """
        if calendarType not in CalendarTypes:
            raise NotSupportedError("CalendarTypes is not supported")
        self._calendarType = calendarType
        self._holiday = Holiday(calendarType)

    def is_holiday(self, date: Date) -> bool:
        return self._holiday.is_holiday(date)

    def is_business_day(self, date: Date) -> bool:
        """Return True if the date is a business day

        Weekend or not is determined solely by the date itself.
        Holiday or not is determined by the calendar.
        """
        if date.is_weekend is False and self.is_holiday(date) is False:
            return True
        else:
            return False

    def adjust(self, date: Date, busDayAdjType: BusDayAdjustTypes) -> Date:
        """Return a new Date object by adjusting the date according to the Business Day Convention

        For details, https://jollycontrarian.com/index.php?title=Business_Day_Convention_-_ISDA_Definition
        """
        # no need to adjust if no calendar is specified
        if self._calendarType == CalendarTypes.NONE:
            return date
        # need to adjust but depend on the BusDayAdjustTypes
        if busDayAdjType == BusDayAdjustTypes.NONE:
            return date

        elif busDayAdjType == BusDayAdjustTypes.FOLLOWING:
            while self.is_business_day(date) is False:
                date = date.add_days(1)
            return date

        elif busDayAdjType == BusDayAdjustTypes.MODIFIED_FOLLOWING:
            initial_date = Date.from_tuple(date.to_tuple())
            while self.is_business_day(date) is False:
                date = date.add_days(1)
            # if the following business day is in the different month, find the previous business day
            if date.month != initial_date.month:
                date = initial_date
                while self.is_business_day(date) is False:
                    date = date.add_days(-1)
            return date

        elif busDayAdjType == BusDayAdjustTypes.PREVIOUS:
            while self.is_business_day(date) is False:
                date = date.add_days(-1)
            return date

        elif busDayAdjType == BusDayAdjustTypes.MODIFIED_PREVIOUS:
            initial_date = Date.from_tuple(date.to_tuple())
            while self.is_business_day(date) is False:
                date = date.add_days(-1)
            # if the previous business day is in the different month, find the next business day
            if date.month != initial_date.month:
                date = initial_date
                while self.is_business_day(date) is False:
                    date = date.add_days(1)
            return date
        else:
            raise NotSupportedError(
                "BusDayAdjustTypes is not supported, cannot adjust date")
