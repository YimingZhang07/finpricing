from scipy.optimize import brentq, newton
from ..instrument.vanilla_swap import VanillaInterestRateSwap
from ..utils.date import Date
from ..market.curve import BaseCurve


def swap_value_by_df(df_input: float,
                     swap: VanillaInterestRateSwap,
                     valuation_date: Date,
                     discount_curve: BaseCurve,
                     index_curve: BaseCurve = None) -> float:
    """Value the swap by tweaking the last discount factor in discount curve. Returns the value with unit notional.

    This is used as a helper function for bootstraping the discount curve.
    """
    discount_curve.dfs[-1] = df_input
    if index_curve is None:
        value = swap.value(valuation_date, discount_curve, discount_curve)
    else:
        value = swap.value(valuation_date, discount_curve, index_curve)
    return value / swap.notional


def brent_solve(f: callable,
                left: float,
                right: float,
                args: tuple = (),
                max_iter: int = 50) -> float:
    """Solve f(x) = 0 by Brent's method."""
    return brentq(f, a=left, b=right, args=args, maxiter=max_iter)


def newton_solve(f: callable,
                 x0: float,
                 args: tuple = (),
                 max_iter: int = 50) -> float:
    """Solve f(x) = 0 by Newton's method."""
    res = newton(f, x0=x0, args=args, maxiter=max_iter, tol=1e-14)
    return res
