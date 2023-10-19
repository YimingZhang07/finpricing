from enum import Enum
from .date import Date
from .error import NotSupportedError


class CalendarTypes(Enum):
    NONE = 0
    WEEKEND = 1
    UNITED_STATES = 2


class Holiday:
    def __init__(self, calendarType: CalendarTypes) -> None:
        self._calendarType = calendarType

    def is_holiday(self, date: Date) -> bool:
        if self._calendarType == CalendarTypes.NONE:
            return False
        elif self._calendarType == CalendarTypes.WEEKEND:
            return date.is_weekend
        elif self._calendarType == CalendarTypes.UNITED_STATES:
            return self.holiday_united_states(date)
        else:
            raise NotSupportedError("CalendarTypes is not supported")

    def holiday_united_states(self, date: Date) -> bool:
        """Return True if the date is a holiday in the United States, False otherwise

        Need to verify and enhance the dates.
        Reference: https://github.com/domokane/FinancePy/blob/master/financepy/utils/calendar.py#L830
        """

        m, d, weekday = date.month, date.day, date.weekday

        if m == 1 and d == 1:  # NYD
            return True

        if m == 1 and d == 2 and weekday == Date.MON:  # NYD
            return True

        if m == 1 and d == 3 and weekday == Date.MON:  # NYD
            return True

        if m == 1 and d >= 15 and d < 22 and weekday == Date.MON:  # MLK
            return True

        if m == 2 and d >= 15 and d < 22 and weekday == Date.MON:  # George Washington
            return True

        if m == 5 and d >= 25 and d <= 31 and weekday == Date.MON:  # Memorial day
            return True

        if m == 7 and d == 4:  # Indep day
            return True

        if m == 7 and d == 5 and weekday == Date.MON:  # Indep day
            return True

        if m == 7 and d == 3 and weekday == Date.FRI:  # Indep day
            return True

        if m == 9 and d >= 1 and d < 8 and weekday == Date.MON:  # Labor day
            return True

        if m == 10 and d >= 8 and d < 15 and weekday == Date.MON:  # Colombus Day
            return True

        if m == 11 and d == 11:  # Veterans day
            return True

        if m == 11 and d == 12 and weekday == Date.MON:  # Vets
            return True

        if m == 11 and d == 10 and weekday == Date.FRI:  # Vets
            return True

        if m == 11 and d >= 22 and d < 29 and weekday == Date.THU:  # Thanksgiving
            return True

        if m == 12 and d == 24 and weekday == Date.FRI:  # Xmas holiday
            return True

        if m == 12 and d == 25:  # Xmas holiday
            return True

        if m == 12 and d == 26 and weekday == Date.MON:  # Xmas holiday
            return True

        if m == 12 and d == 31 and weekday == Date.FRI:
            return True

        return False
