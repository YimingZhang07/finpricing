from finpricing.market.discount_curve import DiscountCurve
from finpricing.utils.date import Date
from finpricing.instrument.deposit import Deposit
from finpricing.market.dummy_curve import DummyCurve
from finpricing.utils.frequency import FrequencyTypes
from finpricing.utils.day_count import DayCountTypes
from finpricing.instrument.vanilla_swap import VanillaInterestRateSwap, SwapCounterpartyTypes
import numpy as np
from numpy import linalg as LA


def createVanillaSwap(settlement_date, tenor, fixed_rate):
    swap = VanillaInterestRateSwap(settlement_date,
                                   tenor,
                                   counterparty_type=SwapCounterpartyTypes.FIXED_RATE_PAYER,
                                   fixed_rate=fixed_rate,
                                   fixed_freq_type=FrequencyTypes.SEMI_ANNUAL, fixed_day_count_type=DayCountTypes.Thirty_E_360,
                                   float_spread=0.0,
                                   float_freq_type=FrequencyTypes.QUARTERLY,
                                   float_day_count_type=DayCountTypes.Thirty_E_360)
    return swap


def test_add_deposits():
    valuation_date = Date(2019, 11, 21)
    settlement_date = Date(2019, 11, 22)
    depo1 = Deposit(settlement_date, "1M", 0.017156)
    depo2 = Deposit(settlement_date, "2M", 0.018335)
    depo3 = Deposit(settlement_date, "3M", 0.018988)
    depo4 = Deposit(settlement_date, "6M", 0.018911)
    depo5 = Deposit(settlement_date, "12M", 0.019093)
    depos = [depo1, depo2, depo3, depo4, depo5]
    dc = DiscountCurve(valuation_date=valuation_date, day_count_type=DayCountTypes.ACT_365)
    dc.add_deposits(depos)
    assert LA.norm(np.array(dc.times) - np.array([0., 0.00273973, 0.08767123, 0.16986301, 0.26027397,
                                                  0.50136986, 1.00821918])) < 1e-8
    assert LA.norm(np.array(dc.dfs) - np.array([1.,
                                                0.99995235,
                                                0.99847727,
                                                0.99685535,
                                                0.99501906,
                                                0.99048278,
                                                0.98086063])) < 1e-8


def test_add_swaps():
    # testing source: https://github.com/domokane/FinancePy/blob/master/notebooks/products/credit/FINCDS_ValuingCDSCompareToMarkit.ipynb
    valuation_date = Date(2019, 11, 21)
    settlement_date = Date(2019, 11, 22)
    depo1 = Deposit(settlement_date, "1M", 0.017156)
    depo2 = Deposit(settlement_date, "2M", 0.018335)
    depo3 = Deposit(settlement_date, "3M", 0.018988)
    depo4 = Deposit(settlement_date, "6M", 0.018911)
    depo5 = Deposit(settlement_date, "12M", 0.019093)
    depos = [depo1, depo2, depo3, depo4, depo5]
    dc = DiscountCurve(valuation_date=valuation_date, day_count_type=DayCountTypes.ACT_365)
    dc.add_deposits(depos)

    tenors = ["2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y", "10Y", "12Y"]
    rates = [0.015630, 0.015140, 0.015065, 0.015140, 0.015270, 0.015470, 0.015720, 0.016000, 0.016285, 0.01670]
    swaps = [createVanillaSwap(settlement_date, t, r) for t, r in zip(tenors, rates)]
    dc.add_swaps(swaps)

    financePy_res = np.array([1., 0.9999523467153882, 0.9984772740500503,
                              0.9968553525037839, 0.9950190643060934, 0.990482775609669,
                              0.9808606275215394, 0.9693176050274088, 0.9557494198077587,
                              0.9417262468046818, 0.9273057235779231, 0.9126062316422543,
                              0.8975545571045467, 0.882009279554562, 0.8659476816506717,
                              0.8496506642270819, 0.8180318219704973])
    assert LA.norm(np.array(dc.dfs) - financePy_res) < 1e-4


def test_dummy_curve():
    curve = DummyCurve(rate=0.05, freq_type=FrequencyTypes.SEMI_ANNUAL)
    assert curve.eval(0.5) == 1 / np.power(1 + 0.05 / 2, 2 * 0.5)


def test_precision():
    # testing source: https://github.com/domokane/FinancePy/blob/master/notebooks/products/credit/FINCDS_ValuingCDSCompareToMarkit.ipynb
    # testing notebook: docs/example_discount_curve.ipynb
    times = [0.,  0.0027397260273972603,  0.08767123287671233,
             0.16986301369863013,  0.2602739726027397,  0.5013698630136987,
             1.0082191780821919,  2.0054794520547947,  3.0054794520547947,
             4.005479452054795,  5.008219178082192,  6.013698630136986,
             7.010958904109589,  8.008219178082191,  9.01095890410959,
             10.01095890410959, 12.016438356164384]
    dfs = [1., 0.9999523467153882, 0.9984772740500503,
           0.9968553525037839, 0.9950190643060934, 0.990482775609669,
           0.9808606275215394, 0.9693176050274088, 0.9557494198077587,
           0.9417262468046818, 0.9273057235779231, 0.9126062316422543,
           0.8975545571045467, 0.882009279554562, 0.8659476816506717,
           0.8496506642270819, 0.8180318219704973]
    discount_curve = DiscountCurve.FromValues(
        times, dfs, valuation_date=Date(2019, 11, 21), day_count_type=DayCountTypes.ACT_ACT_ISDA)
    assert discount_curve.df(Date(2019, 11, 22)) == 0.9999523467153882
    assert discount_curve.df(Date(2020, 2, 24)) == 0.9950272667059037
