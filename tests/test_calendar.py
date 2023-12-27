from finpricing.utils.calendar import CalendarTypes, Calendar
from finpricing.utils.date import Date
from finpricing.utils.bus_day_adj import BusDayAdjustTypes


def test_is_holiday():
    calendar = Calendar(CalendarTypes.NONE)
    assert calendar.is_holiday(Date(2020, 1, 1)) is False
    assert calendar.is_holiday(Date(2020, 1, 2)) is False
    assert calendar.is_holiday(Date(2020, 1, 3)) is False
    assert calendar.is_holiday(Date(2020, 1, 4)) is False
    assert calendar.is_holiday(Date(2020, 1, 5)) is False
    assert calendar.is_holiday(Date(2020, 1, 6)) is False
    assert calendar.is_holiday(Date(2020, 1, 7)) is False
    assert calendar.is_holiday(Date(2020, 1, 8)) is False
    assert calendar.is_holiday(Date(2020, 1, 9)) is False
    assert calendar.is_holiday(Date(2020, 1, 10)) is False
    assert calendar.is_holiday(Date(2020, 1, 11)) is False
    assert calendar.is_holiday(Date(2020, 1, 12)) is False
    assert calendar.is_holiday(Date(2020, 1, 13)) is False
    assert calendar.is_holiday(Date(2020, 1, 14)) is False
    calendar = Calendar(CalendarTypes.WEEKEND)
    assert calendar.is_holiday(Date(2020, 1, 1)) is False
    assert calendar.is_holiday(Date(2020, 1, 2)) is False
    assert calendar.is_holiday(Date(2020, 1, 3)) is False
    assert calendar.is_holiday(Date(2020, 1, 4)) is True
    assert calendar.is_holiday(Date(2020, 1, 5)) is True
    assert calendar.is_holiday(Date(2023, 6, 25)) is True
    assert calendar.is_holiday(Date(2023, 6, 26)) is False
    calendar = Calendar(CalendarTypes.UNITED_STATES)
    assert calendar.is_holiday(Date(2023, 7, 4)) is True
    assert calendar.is_holiday(Date(2023, 7, 5)) is False
    assert calendar.is_holiday(Date(2023, 1, 1)) is True


def test_adjust():
    calendar = Calendar(CalendarTypes.UNITED_STATES)
    assert calendar.adjust(Date(2023, 7, 4), BusDayAdjustTypes.NONE) == Date(2023, 7, 4)
    assert calendar.adjust(Date(2023, 7, 4), BusDayAdjustTypes.FOLLOWING) == Date(2023, 7, 5)
    assert calendar.adjust(Date(2023, 6, 25), BusDayAdjustTypes.FOLLOWING) == Date(2023, 6, 26)
    assert calendar.adjust(Date(2023, 6, 25), BusDayAdjustTypes.PREVIOUS) == Date(2023, 6, 23)