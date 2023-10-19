from enum import Enum
from math import log, exp
from bisect import bisect_left
from .error import NotSupportedError


class InterpTypes(Enum):
    FLAT_FWD_RATES = 1


class CurveInterpolator:
    def __init__(self):
        pass


class Interpolator(CurveInterpolator):
    def __init__(self,
                 times,
                 dfs,
                 method: InterpTypes = InterpTypes.FLAT_FWD_RATES) -> None:
        """Interpolate discount factors

        Args:
            times (list): list of times (fraction of year); monotonically increasing
            dfs (list): list of discount factors; same length as times
            method (InterpTypes): interpolation method
        """
        self._times = times
        self._dfs = dfs
        self._method = method
        self.validate()

    def __repr__(self) -> str:
        return f"Interpolator(method={self._method})"

    @property
    def times(self):
        return self._times

    @times.setter
    def times(self, times):
        self._times = times

    @property
    def dfs(self):
        return self._dfs

    @dfs.setter
    def dfs(self, dfs):
        self._dfs = dfs

    def validate(self) -> None:
        """Validate input data"""
        if len(self._times) != len(self._dfs):
            raise ValueError("Length of times and dfs must be the same")
        if not all([t1 < t2 for t1, t2 in zip(self._times[:-1], self._times[1:])]):
            raise ValueError("Times must be monotonically increasing")
        if self._times[0] != 0:
            raise ValueError("First time must be 0")
        if self._dfs[0] != 1:
            raise ValueError("First discount factor must be 1")
        if self._dfs[-1] <= 0:
            raise ValueError("Last discount factor must be positive")

    def eval(self, t: float) -> float:
        """Evaluate discount factor at time t

        Args:
            t (float): time (fraction of year)

        Returns:
            float: interpolated discount factor
        """
        if t == 0:
            return self._dfs[0]
        if self._method == InterpTypes.FLAT_FWD_RATES:
            idx = bisect_left(self._times, t)
            if idx == 1:
                rt = -log(self._dfs[1]) * t / self._times[1]
            # extrapolate the rate from the last two points
            elif idx == len(self._times):
                r_left = -log(self._dfs[-2])
                r_right = -log(self._dfs[-1])
                dt = self._times[-1] - self._times[-2]
                rt = ((self._times[-1] - t) * r_left + (t - self._times[-2]) * r_right) / dt
            else:
                r_left = -log(self._dfs[idx - 1])
                r_right = -log(self._dfs[idx])
                dt = self._times[idx] - self._times[idx - 1]
                rt = ((self._times[idx] - t) * r_left + (t - self._times[idx - 1]) * r_right) / dt
            return exp(-rt)
        else:
            raise NotSupportedError("Interpolation method is not supported")
