from pandas.tseries.holiday import (
    AbstractHolidayCalendar,
    Holiday,
    USMartinLutherKingJr,
    USPresidentsDay,
    USMemorialDay,
    USLaborDay,
    USColumbusDay,
    USThanksgivingDay,
    sunday_to_monday,
)

# The established US holidays are fixed, and are sure to be on weekdays. Adjustments are easy.
# Those floating holidays, and if they fall on weekends, they are moved based on an observed rule.
# The US Bank Holidays seem to only move from Sunday to Monday.

class USBankHolidaysCalendar(AbstractHolidayCalendar):
    # https://www.federalreserve.gov/aboutthefed/k8.htm
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#holidays-holiday-calendars
    # https://en.wikipedia.org/wiki/Federal_holidays_in_the_United_States
    rules = [
        Holiday('New Years Day', month=1, day=1, observance=sunday_to_monday),
        USMartinLutherKingJr,
        USPresidentsDay,
        USMemorialDay,
        Holiday(
            "Juneteenth National Independence Day",
            month=6,
            day=19,
            start_date="2021-06-18",
            observance=sunday_to_monday,
        ),
        Holiday("Independence Day", month=7, day=4, observance=sunday_to_monday),
        USLaborDay,
        USColumbusDay,
        Holiday("Veterans Day", month=11, day=11, observance=sunday_to_monday),
        USThanksgivingDay,
        Holiday("Christmas Day", month=12, day=25, observance=sunday_to_monday),
    ]
