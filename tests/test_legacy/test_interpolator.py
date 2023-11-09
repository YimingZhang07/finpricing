from bisect import bisect_left
import numpy as np
from financepy.market.curves.interpolator import _uinterpolate, InterpTypes
from finpricing.utils.interpolator import Interpolator


def test_bisect_left():
    values = [1, 2, 3, 4, 5]
    assert bisect_left(values, 0) == 0
    assert bisect_left(values, 1.5) == 1
    assert bisect_left(values, 3.2) == 3
    assert bisect_left(values, -1) == 0
    assert bisect_left(values, 6) == 5


def test_interpolate_flat_fwd_curve_cross():
    dates = [0, 0.25, 0.5, 1, 2, 3, 4, 5]
    dfs = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]
    for t in np.linspace(0, 7, 50):
        val_1 = _uinterpolate(t, np.array(dates), np.array(dfs), InterpTypes.FLAT_FWD_RATES.value)
        val_2 = Interpolator(dates, dfs).eval(t)
        assert abs(val_1 - val_2) < 1e-10
