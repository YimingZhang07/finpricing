from enum import Enum
import calendar
import datetime
from .date import Date
from .error import NotSupportedError
from typing import Union


# reference: http://www.eclipsesoftware.biz/DayCountConventions.html#x3_01a
# reference: https://en.wikipedia.org/wiki/Day_count_convention
# ISDA: https://www.rbccm.com/assets/rbccm/docs/legal/doddfrank/Documents/ISDALibrary/2006%20ISDA%20Definitions.pdf
# OpenGamma: https://quant.opengamma.io/Interest-Rate-Instruments-and-Market-Conventions.pdf


class DayCountTypes(Enum):
    ACT_360 = 0
    ACT_365 = 1
    # ISDA 4.16(f)
    Thirty_360 = 2
    ACT_ACT_ISDA = 3
    # ISDA 4.16(g)
    Thirty_E_360 = 4
    # ISDA 4.16(h)
    Thirty_E_360_ISDA = 5


class DayCount:
    def __init__(self, dccType: DayCountTypes) -> None:
        self._dccType = dccType

    def days_between(self, start_date: Date, end_date: Date, include_end=False) -> tuple:
        """Return the number of days and year fraction using a specific day count convention

        Returns:
            tuple: (days, fraction of year)
        """
        if self._dccType == DayCountTypes.ACT_360:
            if include_end:
                days = end_date - start_date + 1
            else:
                days = end_date - start_date
            denominator = 360
            frac = days / denominator
        elif self._dccType == DayCountTypes.ACT_365:
            if include_end:
                days = end_date - start_date + 1
            else:
                days = end_date - start_date
            denominator = 365
            frac = days / denominator
        # This follows the ISDA 4.16(f) definition
        elif self._dccType == DayCountTypes.Thirty_360:
            y1, m1, d1 = start_date.to_tuple()
            y2, m2, d2 = end_date.to_tuple()
            d1 = 30 if d1 == 31 else d1
            d2 = 30 if d2 == 31 and (d1 in [30, 31]) else d2
            days = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
            denominator = 360
            frac = days / denominator
        # This follows the ISDA 4.16(g) definition
        elif self._dccType == DayCountTypes.Thirty_E_360:
            y1, m1, d1 = start_date.to_tuple()
            y2, m2, d2 = end_date.to_tuple()
            d1 = 30 if d1 == 31 else d1
            d2 = 30 if d2 == 31 else d2
            days = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
            denominator = 360
            frac = days / denominator
        # elif self._dccType == DayCountTypes.Thirty_E_360_ISDA:
        #     y1, m1, d1 = start_date.to_tuple()
        #     y2, m2, d2 = end_date.to_tuple()
        #     d1 = 30 if d1 == 31 else d1
        #     d2 = 30 if d2 == 31 else d2
        #     days = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
        #     denominator = 360
        #     frac = days / denominator
        # This considers leap years in partial year calculation
        elif self._dccType == DayCountTypes.ACT_ACT_ISDA:
            denom1 = 365 + calendar.isleap(start_date.year)
            denom2 = 365 + calendar.isleap(end_date.year)
            if start_date.year == end_date.year:
                days = end_date - start_date
                frac = days / denom1
            else:
                days1 = Date(start_date.year + 1, 1, 1) - start_date
                frac = days1 / denom1
                days2 = end_date - Date(end_date.year, 1, 1)
                frac += days2 / denom2
                days = end_date - start_date
                frac += end_date.year - start_date.year - 1
        else:
            raise NotSupportedError("DayCountTypes is not supported")
        return (days, frac)

    def year_fraction(self,
                      start_date: Union[Date, datetime.date], 
                      end_date: Union[Date, datetime.date],
                      next_coupon_date: Date = None) -> float:
        """Return the fraction of year between two dates using a specific day count convention

        The actual calculation is done in days_between() method.

        Args:
            start_date (Date): start date of the accrual period
            end_date (Date): end date of the accrual period. For a bond trade, it is the settlement date of the trade.
            next_coupon_date (Date): next coupon date of the bond / maturity date of the bond if no more coupon payment
        """
        if isinstance(start_date, datetime.date):
            start_date = Date.from_datetime(start_date)
        if isinstance(end_date, datetime.date):
            end_date = Date.from_datetime(end_date)
        
        frac = self.days_between(start_date, end_date)[1]
        return frac
    
    def convert_dates_to_times(self, anchor_date: Date, dates: list[Date]) -> list[float]:
        """Return a list of time fraction (year fraction) between anchor date and each date in the list

        Args:
            anchor_date (Date): anchor date
            dates (list[Date]): list of dates

        Returns:
            list[float]: list of time fraction (year fraction)
        """
        return [self.year_fraction(anchor_date, date) for date in dates]

    def __repr__(self) -> str:
        """Return the string representation of the object"""
        return f"DayCount({self._dccType})"

    # create an alias for year_fraction
    year_frac = year_fraction
