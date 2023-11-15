import numpy as np
from financepy.products.rates.ibor_single_curve import IborSingleCurve
from ..market.legacy.discount_curve import DiscountCurve
from .tools import prettyTableByColumn


def discount_curve_recon(finpricing_curve: DiscountCurve,
                         financepy_curve: IborSingleCurve) -> dict:
    """Compare discount factors of two curves

     Args:
          finpricing_curve (DiscountCurve): finpricing discount curve
          financepy_curve (IborSingleCurve): financepy discount curve
     Returns:
          dict: dictionary of times, finpricing discount factors, financepy discount factors and difference
    """
    times = np.linspace(0, 2, 10)
    df1 = np.array([finpricing_curve.eval(t) for t in times])
    df2 = np.array([financepy_curve._df(float(t)) for t in times])
    diff = df1 - df2
    d = {'TIMES': times,
         'FINPRICING_DF': df1,
         'FINANCEPY_DF': df2,
         'DIFF': diff}
    print(prettyTableByColumn(d))
    return d
