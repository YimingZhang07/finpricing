from typing import Union
import datetime
import math
from bisect import bisect_left
from ..utils.interpolator import InterpTypes
from ..utils.day_count import DayCountTypes, DayCount
from ..utils.date import Date


class DiscountCurve:
    def __init__(self) -> None:
        pass

    def discount(self, date: Union[Date, datetime.date]):
        """discount factor for date"""
        return NotImplementedError("Please implement factor() method in derived class")


class FlatForwardInterpolator:
    def __init__(self,
                 anchor_date: Union[Date, datetime.date],
                 spot_date,
                 dates,
                 rates,
                 day_counter,
                 continuous_compounding):
        self.anchor_date = anchor_date
        self.spot_date = spot_date
        self.day_counter = day_counter
        self.dates = dates
        self.rates = rates
        self.times = self.day_counter.convert_dates_to_times(self.anchor_date,
                                                             [self.anchor_date] + self.dates)
        self.times_relateive_to_spot = [t - self.day_counter.year_fraction(self.anchor_date, self.spot_date) for t in self.times]
        self.forwards = []
        self.cum_factors = []
        if continuous_compounding:
            self.run_continuous_flat_forward_rates()
            self.dicount_handle = self.continuous_discount
        else:
            self.run_annual_compounding()
            self.dicount_handle = self.annual_discount

    def run_continuous_flat_forward_rates(self):
        """"derive forward rates using ontinuous compounding"""
        for i, _ in enumerate(self.times_relateive_to_spot):
            if i == 0:
                self.forwards.append(self.rates[0])
                self.cum_factors.append(1.)
            elif i == len(self.times_relateive_to_spot) - 1:
                self.cum_factors.append(
                    self.cum_factors[-1] * math.exp(-1 * self.forwards[-1] * (self.times[i] - self.times[i-1])))
                self.forwards.append(self.forwards[-1])
            else:
                r1 = self.rates[i - 1]
                r2 = self.rates[i]
                t1 = self.times_relateive_to_spot[i]
                t2 = self.times_relateive_to_spot[i + 1]
                f = -math.log(math.exp(-t2 * r2) /
                              math.exp(-t1 * r1)) / (t2 - t1)
                self.cum_factors.append(
                    self.cum_factors[-1] * math.exp(-1 * self.forwards[-1] * (self.times[i] - self.times[i-1])))
                self.forwards.append(f)

    def continuous_discount(self, dt):
        """"discount using continuous compounding"""
        idx = max(min(bisect_left(self.times, dt) - 1, len(self.times) - 1), 0)
        return self.cum_factors[idx] * math.exp(-self.forwards[idx] * (dt - self.times[idx]))

    def _annual_discount(self, rate, time):
        return 1 / (1 + rate) ** time

    def run_annual_compounding(self):
        """derive forward rates using annual compounding"""
        for i, _ in enumerate(self.times_relateive_to_spot):
            if i == 0:
                self.forwards.append(self.rates[0])
                self.cum_factors.append(1.)
            elif i == len(self.times_relateive_to_spot) - 1:
                self.cum_factors.append(self.cum_factors[-1] * self._annual_discount(
                    self.forwards[-1], self.times[i] - self.times[i-1]))
                self.forwards.append(self.forwards[-1])
            else:
                r1 = self.rates[i - 1]
                r2 = self.rates[i]
                t1 = self.times_relateive_to_spot[i]
                t2 = self.times_relateive_to_spot[i + 1]
                f = (self._annual_discount(r1, t1) /
                     self._annual_discount(r2, t2)) ** (1/(t2 - t1)) - 1
                self.cum_factors.append(self.cum_factors[-1] * self._annual_discount(
                    self.forwards[-1], self.times[i] - self.times[i-1]))
                self.forwards.append(f)

    def annual_discount(self, dt):
        """discount using annual compounding"""
        idx = max(min(bisect_left(self.times, dt) - 1, len(self.times) - 1), 0)
        return self.cum_factors[idx] * self._annual_discount(self.forwards[idx], dt - self.times[idx])

    def eval(self, dt):
        """"evaluate discount factor for dt using the correct discounting method"""
        return self.dicount_handle(dt)


class DiscountCurveZeroRates(DiscountCurve):

    def __init__(self,
                 anchor_date=None,
                 dates: list[float] = None,
                 rates: list[float] = None,
                 spot_date=None,
                 continuous_compounding: bool = True,
                 interp_type=InterpTypes.FLAT_FWD_RATES,
                 day_count_type: DayCountTypes = DayCountTypes.ACT_365) -> None:
        self.anchor_date = Date.convert_from_datetime(anchor_date)
        self.dates = dates
        self.rates = rates
        self.interp_type = interp_type
        self.day_count_type = day_count_type
        if spot_date is None:
            self.spot_date = self.anchor_date
        else:
            self.spot_date = spot_date
        # derived
        self.day_counter = DayCount(self.day_count_type)
        if interp_type == InterpTypes.FLAT_FWD_RATES:
            self.interpolator = FlatForwardInterpolator(
                self.anchor_date,
                self.spot_date,
                self.dates,
                self.rates,
                self.day_counter,
                continuous_compounding=continuous_compounding
            )
        else:
            raise NotImplementedError(
                "This interp_type has not been supported.")

    def discount(self, date: Date):
        dt = self.day_counter.year_fraction(self.anchor_date, date)
        return self.interpolator.eval(dt)


class DiscountCurveZeroShifted:
    def __init__(self,
                 underlying_curve: DiscountCurveZeroRates,
                 alpha: float,
                 beta: float = 1.0,
                 day_count_type: DayCountTypes = DayCountTypes.ACT_365) -> None:
        self.underlying_curve = underlying_curve
        self.anchor_date = self.underlying_curve.anchor_date
        self.alpha = alpha
        self.beta = beta
        self.day_count_type = day_count_type
        # derived
        self.day_counter = DayCount(self.day_count_type)
        assert self.day_count_type == self.underlying_curve.day_count_type, \
            "Day_count_type must be the same as underlying_curve.day_count_type"

    def discount(self, date: Union[Date, datetime.date]):
        """discount factor for date"""
        factor = self.underlying_curve.discount(date)
        time = self.day_counter.year_fraction(
            self.underlying_curve.anchor_date, date)
        factor_adjusted = math.pow(
            factor, self.beta) * math.exp(-self.alpha * time)
        return factor_adjusted
