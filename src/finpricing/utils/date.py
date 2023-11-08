import datetime
from dateutil.relativedelta import relativedelta
from typing import Union

class Date:
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6

    def __init__(self, year: int, month: int, day: int) -> None:
        self._date = datetime.date(year, month, day)
        self.year = year
        self.month = month
        self.day = day
        self.weekday = self._date.weekday()

    def to_tuple(self) -> tuple:
        """Return a tuple of (year, month, day)"""
        return self._date.year, self._date.month, self._date.day
    
    @classmethod
    def convert_from_datetime(cls, date: Union[datetime.date, 'Date']) -> 'Date':
        """Return a Date object from a datetime.date object"""
        if isinstance(date, Date):
            return date
        return cls.from_datetime(date)
    
    @classmethod
    def convert_from_datetimes(cls, dates: list[Union[datetime.date, 'Date']]) -> list['Date']:
        """Return a list of Date objects from a list of datetime.date objects"""
        return [cls.convert_from_datetime(date) for date in dates]

    @classmethod
    def from_datetime(cls, date: datetime.date) -> 'Date':
        """Return a Date object from a datetime.date object"""
        return cls(date.year, date.month, date.day)

    @classmethod
    def from_tuple(cls, date_tuple: tuple) -> 'Date':
        """Return a Date object from a tuple of (year, month, day)"""
        return cls(date_tuple[0], date_tuple[1], date_tuple[2])

    def __sub__(self, other: 'Date') -> int:
        return (self._date - other._date).days

    def __add__(self, days: int) -> 'Date':
        return self.add_days(days)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Date) is False:
            return False
        return self._date == other._date

    def __le__(self, other: object) -> bool:
        if isinstance(other, Date) is False:
            return False
        return self._date <= other._date

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Date) is False:
            return False
        return self._date < other._date

    def __ge__(self, other: object) -> bool:
        if isinstance(other, Date) is False:
            return False
        return self._date >= other._date

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Date) is False:
            return False
        return self._date > other._date

    def __repr__(self) -> str:
        # return "Date({0}, {1:>2s}, {2:>2s})".format(self.year, str(self.month), str(self.day))
        return self._date.strftime("%a (%Y, %m, %d)")

    @property
    def is_weekend(self) -> bool:
        """Return True if the date is a weekend, False otherwise

        Monday is 0 and Sunday is 6.
        """
        return self.weekday >= 5

    def add_days(self, days: int) -> 'Date':
        """Return a new Date object by adding days to self"""
        if isinstance(days, int) is False:
            raise TypeError("days must be an integer")
        return Date.from_datetime(self._date + datetime.timedelta(days=days))

    def add_months(self, months: int) -> 'Date':
        """Return a new Date object by adding months to self"""
        if isinstance(months, int) is False:
            raise TypeError("months must be an integer")
        return Date.from_datetime(self._date + relativedelta(months=months))

    def add_weeks(self, weeks: int) -> 'Date':
        """Return a new Date object by adding weeks to self"""
        if isinstance(weeks, int) is False:
            raise TypeError("weeks must be an integer")
        return Date.from_datetime(self._date + relativedelta(weeks=weeks))

    def add_years(self, years: int) -> 'Date':
        """Return a new Date object by adding years to self"""
        if isinstance(years, int) is False:
            raise TypeError("years must be an integer")
        return Date.from_datetime(self._date + relativedelta(years=years))

    def add_tenor(self, tenor: str) -> 'Date':
        """Return a new Date object by adding tenor to self"""
        if isinstance(tenor, str) is False:
            raise TypeError("tenor must be a string")
        if tenor[-1] == 'd' or tenor[-1] == 'D':
            return self.add_days(int(tenor[:-1]))
        elif tenor[-1] == 'w' or tenor[-1] == 'W':
            return self.add_weeks(int(tenor[:-1]))
        elif tenor[-1] == 'm' or tenor[-1] == 'M':
            return self.add_months(int(tenor[:-1]))
        elif tenor[-1] == 'y' or tenor[-1] == 'Y':
            return self.add_years(int(tenor[:-1]))
        else:
            raise ValueError("tenor must be one of 'd', 'w', 'm', 'y'")
        
    def strftime(self, fmt: str) -> str:
        """Return a string representing the date, controlled by an explicit format string"""
        return self._date.strftime(fmt)

    def __hash__(self) -> int:
        return hash(self._date)
