import numpy as np
from numpy import linalg as LA
from finpricing.utils.date import Date
from finpricing.utils.day_count import DayCountTypes
from finpricing.utils.frequency import FrequencyTypes
from finpricing.utils.calendar import CalendarTypes, DateGenRuleTypes
from finpricing.utils.bus_day_adj import BusDayAdjustTypes
from finpricing.utils.literal import Literal
from finpricing.instrument.swap_fixed_leg import SwapFixedLeg
from finpricing.instrument.swap_float_leg import SwapFloatLeg
from finpricing.instrument.vanilla_swap import VanillaInterestRateSwap, SwapCounterpartyTypes
from finpricing.market.dummy_curve import DummyCurve


def test_fixed_leg():
    # benchmark: https://github.com/domokane/FinancePy/blob/master/notebooks/products/rates/FINIBORSINGLECURVE_ReplicatingQuantlibExample.ipynb
    fixed_leg = SwapFixedLeg(start_date=Date(2015, 10, 27),
                             maturity_date_or_tenor="10Y",
                             coupon_rate=0.025,
                             notional=10 * Literal.ONE_MILLION.value,
                             freq_type=FrequencyTypes.SEMI_ANNUAL,
                             day_count_type=DayCountTypes.ACT_360,
                             calendar_type=CalendarTypes.UNITED_STATES,
                             bus_day_adj_type=BusDayAdjustTypes.MODIFIED_FOLLOWING,
                             date_gen_rule_type=DateGenRuleTypes.FORWARD)
    discount_curve = DummyCurve(rate=1e-2,
                                day_count_type=DayCountTypes.ACT_365)
    assert fixed_leg.value(discount_curve=discount_curve,
                           valuation_date=Date(2015, 10, 20)) == 2407495.2348627322
    expected_pv = np.array([126423.52245885087,
                            125791.25933031435,
                            124481.62243394127,
                            124539.6153870762,
                            123243.00959555026,
                            124641.14130444454,
                            122010.03549625739,
                            121403.17095126382,
                            120799.32488400833,
                            120855.60234448605,
                            119597.35151842418,
                            119653.06900881398,
                            118407.33798765666,
                            118462.50107975402,
                            117229.16528936104,
                            117283.77949952112,
                            117966.14104540742,
                            115475.94081436281,
                            114901.57614021955,
                            114330.06829301859])
    assert LA.norm(np.array(fixed_leg.cashflows_pv) - expected_pv) < 1e-8
    assert fixed_leg.debug_attrs_match() is True


def test_float_leg():
    # benchmark: https://github.com/domokane/FinancePy/blob/master/notebooks/products/rates/FINIBORSINGLECURVE_ReplicatingQuantlibExample.ipynb
    float_leg = SwapFloatLeg(start_date=Date(2015, 10, 27),
                             maturity_date_or_tenor="10Y",
                             spread=0.004,
                             notional=10 * Literal.ONE_MILLION.value,
                             freq_type=FrequencyTypes.QUARTERLY,
                             day_count_type=DayCountTypes.ACT_360,
                             calendar_type=CalendarTypes.UNITED_STATES,
                             bus_day_adj_type=BusDayAdjustTypes.MODIFIED_FOLLOWING,
                             date_gen_rule_type=DateGenRuleTypes.FORWARD)
    valuation_date = Date(2015, 10, 20)
    index_curve = DummyCurve(valuation_date=valuation_date, rate=0.02, day_count_type=DayCountTypes.ACT_365)
    discount_curve = DummyCurve(valuation_date=valuation_date, rate=0.01, day_count_type=DayCountTypes.ACT_365)
    assert float_leg.value(valuation_date, discount_curve, index_curve) == 2318923.971387784
    assert float_leg.debug_attrs_match() is True


def test_swap():
    # benchmark: https://github.com/domokane/FinancePy/blob/master/notebooks/products/rates/FINIBORSWAP_DefiningAFixedFloatingSwap.ipynb
    fixed_leg_cashflows_pv = np.array([0,
                                       0,
                                       497155.7900373393,
                                       469413.12362177763,
                                       448021.6253327725,
                                       426433.432797404,
                                       406981.9985065608,
                                       388339.4068002361])
    start_date = Date(2018, 6, 20)
    maturity_date = Date(2025, 9, 20)
    swap = VanillaInterestRateSwap(start_date=start_date,
                                   maturity_date_or_tenor=maturity_date,
                                   fixed_rate=0.05,
                                   float_spread=0.0,
                                   notional=10 * Literal.ONE_MILLION.value,
                                   counterparty_type=SwapCounterpartyTypes.FIXED_RATE_RECEIVER,
                                   fixed_freq_type=FrequencyTypes.ANNUAL,
                                   fixed_day_count_type=DayCountTypes.ACT_360,
                                   float_freq_type=FrequencyTypes.SEMI_ANNUAL,
                                   float_day_count_type=DayCountTypes.ACT_360,
                                   calendar_type=CalendarTypes.UNITED_STATES,
                                   bus_day_adj_type=BusDayAdjustTypes.FOLLOWING,
                                   date_gen_rule_type=DateGenRuleTypes.BACKWARD)
    valuation_date = Date(2020, 3, 20)
    discount_curve = DummyCurve(valuation_date=valuation_date, rate=0.05, freq_type=FrequencyTypes.SEMI_ANNUAL)
    index_curve = DummyCurve(valuation_date=valuation_date, rate=0.05, freq_type=FrequencyTypes.SEMI_ANNUAL)
    swap.value(valuation_date, discount_curve, index_curve)
    assert LA.norm(np.array(swap.fixed_leg.cashflows_pv) - fixed_leg_cashflows_pv) < 1e-8
    assert abs(swap.pv01(valuation_date, discount_curve) - 5.272690754192439) < 1e-8
    assert abs(swap.swap_rate(valuation_date, discount_curve) - 0.04516388971357023) < 1e8


def test_swap_hash():
    start_date = Date(2018, 6, 20)
    maturity_date = Date(2025, 9, 20)
    swap = VanillaInterestRateSwap(start_date=start_date,
                                   maturity_date_or_tenor=maturity_date,
                                   fixed_rate=0.05,
                                   float_spread=0.0,
                                   notional=10 * Literal.ONE_MILLION.value,
                                   counterparty_type=SwapCounterpartyTypes.FIXED_RATE_RECEIVER,
                                   fixed_freq_type=FrequencyTypes.ANNUAL,
                                   fixed_day_count_type=DayCountTypes.ACT_360,
                                   float_freq_type=FrequencyTypes.SEMI_ANNUAL,
                                   float_day_count_type=DayCountTypes.ACT_360,
                                   calendar_type=CalendarTypes.UNITED_STATES,
                                   bus_day_adj_type=BusDayAdjustTypes.FOLLOWING,
                                   date_gen_rule_type=DateGenRuleTypes.BACKWARD)
    hash1 = hash(swap)
    swap.float_leg.spread = 0.01
    hash2 = hash(swap)
    assert hash1 != hash2
    swap.float_leg.spread = 0.0
    hash3 = hash(swap)
    assert hash1 == hash3
