from ..utils.interpolator import InterpTypes, CurveInterpolator, Interpolator
from ..utils.day_count import DayCountTypes, DayCount
from ..utils.date import Date


class BaseCurve:
    """Abstract base class for any curve

    The basic curve class should have 1. valuation date, 2. day count convention to be used.
    TODO: raise error if valuation date is not provided.
    """

    def __init__(self,
                 valuation_date: Date = None,
                 day_count_type: DayCountTypes = DayCountTypes.ACT_365,
                 ) -> None:
        self._valuation_date = valuation_date
        self._day_count_type = day_count_type
        self._day_count = DayCount(day_count_type)

    def __repr__(self) -> str:
        return f"Valuation date: {self._valuation_date}\nDay count convention: {self._day_count_type}"

    def eval(self, t: float) -> float:
        """Evaluate discount factor at time t

        Args:
            t (float): time (fraction of year)

        Returns:
            float: interpolated discount factor
        """
        raise NotImplementedError("eval() is not implemented, you should implement it in the derived class")

    def dt(self, date: Date) -> float:
        """Get time from valuation date to fraction of year using the curve day count convention

        Args:
            date (Date): date

        Returns:
            float: time (fraction of year)
        """
        return self._day_count.year_fraction(self._valuation_date, date)

    def df(self, date: Date) -> float:
        """Get discount factor of date as of valuation date

        Args:
            date (Date): date
        Returns:
            float: discount factor
        """
        return self.eval(self.dt(date))

    def dtf(self, date: Date) -> tuple:
        """Get time and discount factor of date as of valuation date

        Args:
            date (Date): date
        Returns:
            tuple: time and discount factor
        """
        dt = self._day_count.year_fraction(self._valuation_date, date)
        df = self.eval(dt)
        return dt, df

    def year_frac(self, date1: Date, date2: Date) -> float:
        """Get year fraction between two dates using the curve day count convention

        Args:
            date1 (Date): date 1
            date2 (Date): date 2
        Returns:
            float: year fraction
        """
        return self._day_count.year_fraction(date1, date2)

    @property
    def day_counter(self) -> DayCount:
        """Return the day count object"""
        return self._day_count


class Curve(BaseCurve):
    """Discount curve class for curves that constructed with set of dates, discount factors and interpolation"""

    def __init__(self,
                 valuation_date: Date = None,
                 times: list[float] = None,
                 dfs: list[float] = None,
                 interpolator: CurveInterpolator = None,
                 day_count_type: DayCountTypes = DayCountTypes.ACT_ACT_ISDA) -> None:
        super().__init__(valuation_date, day_count_type)
        self._interpolator = interpolator
        self._times = times if times is not None else [0.]
        self._dfs = dfs if dfs is not None else [1.]

    @property
    def times(self) -> list[float]:
        """Return the times"""
        return self._times

    @property
    def dfs(self) -> list[float]:
        """Return the discount factors"""
        return self._dfs

    @classmethod
    def FromValues(cls,
                   times: list,
                   dfs: list,
                   valuation_date:
                   Date = None,
                   interp_type=InterpTypes.FLAT_FWD_RATES,
                   day_count_type: DayCountTypes = DayCountTypes.ACT_ACT_ISDA):
        """Construct a discount curve from a list of times and discount factors

        Since times and dfs are given, no bootstrapping is needed, only interpolation is performed.

        Args:
            valuation_date (Date): valuation date
            times (list(float)): list of times
            dfs (list(float)): list of discount factors
        """
        if times[0] != 0 or dfs[0] != 1:
            raise ValueError("The first time must be 0 and the first discount factor must be 1")

        # we don't need to check if times are sorted because Interpolator will do it for us
        return cls(interpolator=Interpolator(times, dfs, interp_type),
                   times=times,
                   dfs=dfs,
                   valuation_date=valuation_date,
                   day_count_type=day_count_type)

    def get_factor(self, t) -> float:
        """Get factor at time t

        This is just a wrapper of eval() method.
        """
        return self.eval(t)

    def eval(self, t: float) -> float:
        """Evaluate curve value at time t"""
        return self._interpolator.eval(t)

    def to_tuple(self) -> tuple:
        """Convert object attributes to a tuple"""
        return (self._valuation_date,
                tuple(self._times),
                tuple(self._dfs),
                self._interpolator,
                self._day_count_type)

    def __hash__(self) -> int:
        return hash(self.to_tuple())

    def __repr__(self) -> str:
        return super().__repr__() + f"\n{self._interpolator}"
