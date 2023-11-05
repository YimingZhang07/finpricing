from finpricing.market.discount_curve_zero import DiscountCurveZeroRates, DiscountCurveZeroShifted
import datetime
import pytest
import os
import pickle

def test_discount():
    anchor_date = datetime.date(2023, 10, 9)
    dates       = [datetime.date(2023, 12, 31), datetime.date(2024, 12, 31)] 
    rates       = [.05, .06]
    discountCurve = DiscountCurveZeroRates(anchor_date, dates, rates)
    assert discountCurve.discount(datetime.date(2023, 10, 9))   == pytest.approx(1.)
    assert discountCurve.discount(datetime.date(2023, 10, 10))  == pytest.approx(.9998630230808251)
    assert discountCurve.discount(datetime.date(2023, 10, 31))  == pytest.approx(.9969908380010889)
    assert discountCurve.discount(datetime.date(2025, 10, 31))  == pytest.approx(.8819061927598262)

def test_forwards():
    anchor_date = datetime.date(2023, 10, 9)
    dates = [datetime.date(2023, 10, 11), datetime.date(2023, 10, 31), datetime.date(2023, 12, 31)]
    rates = [0.05, 0.07, 0.09]
    discountCurve = DiscountCurveZeroRates(anchor_date, dates, rates, spot_date=datetime.date(2023, 12, 15))
    assert discountCurve.interpolator.forwards[0]   == 0.05
    assert discountCurve.interpolator.forwards[1]   == pytest.approx(0.005)
    assert discountCurve.interpolator.forwards[2]   == pytest.approx(0.07524590163934353)
    assert discountCurve.interpolator.forwards[3]   == pytest.approx(0.07524590163934353)
    assert len(discountCurve.interpolator.forwards) == 4

    assert discountCurve.interpolator.cum_factors[0] == pytest.approx(1.)
    assert discountCurve.interpolator.cum_factors[1] == pytest.approx(0.9997260649243265)
    assert discountCurve.interpolator.cum_factors[2] == pytest.approx(0.9994522048890787)
    assert discountCurve.interpolator.cum_factors[3] == pytest.approx(0.986962447217427)
    assert len(discountCurve.interpolator.cum_factors) == 4

    assert discountCurve.discount(datetime.date(2023, 10, 9))   == pytest.approx(1.)
    assert discountCurve.discount(datetime.date(2023, 11, 12))  == pytest.approx(0.9969827779235936)
    assert discountCurve.discount(datetime.date(2023, 12, 23))  == pytest.approx(0.9885915135771349)
    assert discountCurve.discount(datetime.date(2024, 1, 2))    == pytest.approx(0.9865556002509076)

def test_forwards_annual_compounding():
    anchor_date = datetime.date(2023, 10, 9)
    dates = [datetime.date(2023, 10, 11), datetime.date(2023, 10, 31), datetime.date(2023, 12, 31)]
    rates = [0.05, 0.07, 0.09]
    discountCurve = DiscountCurveZeroRates(anchor_date, dates, rates, spot_date=datetime.date(2023, 12, 15), continuous_compounding=False)
    assert discountCurve.interpolator.forwards[0]   == 0.05
    assert discountCurve.interpolator.forwards[1]   == pytest.approx(0.00635618986625186)
    assert discountCurve.interpolator.forwards[2]   == pytest.approx(0.07521012073226463)
    assert discountCurve.interpolator.forwards[3]   == pytest.approx(0.07521012073226463)
    assert len(discountCurve.interpolator.forwards) == 4

    assert discountCurve.interpolator.cum_factors[0] == pytest.approx(1.)
    assert discountCurve.interpolator.cum_factors[1] == pytest.approx(0.9997326923677412)
    assert discountCurve.interpolator.cum_factors[2] == pytest.approx(0.9993856632532903)
    assert discountCurve.interpolator.cum_factors[3] == pytest.approx(0.9873470747853555)
    assert len(discountCurve.interpolator.cum_factors) == 4

    assert discountCurve.discount(datetime.date(2024, 1, 2))    == pytest.approx(0.9869548318270954)
    
def test_real_discount_curve():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'testing_data/discount_curve_rates_20231009.pickle')
    with open(file_path, 'rb') as f:
        dates_rates = pickle.load(f)

    assert sum([x[1] for x in dates_rates]) == pytest.approx(4.425019106569014)

    discount_curve = DiscountCurveZeroRates(
        anchor_date=datetime.date(2023, 10, 9),
        dates=[x[0] for x in dates_rates],
        rates=[x[1] for x in dates_rates],
        spot_date=datetime.date(2023, 10, 9)
    )

    assert discount_curve.discount(datetime.date(2023, 10, 10)) == pytest.approx(0.9998483072290358)
    assert discount_curve.discount(datetime.date(2023, 10, 15)) == pytest.approx(0.9990878513334494)
    assert discount_curve.discount(datetime.date(2023, 10, 31)) == pytest.approx(0.9966533032824298)
    assert discount_curve.discount(datetime.date(2023, 12, 14)) == pytest.approx(0.9899236991398519)
    assert discount_curve.discount(datetime.date(2024, 12, 14)) == pytest.approx(0.937780040455758)
    assert discount_curve.discount(datetime.date(2030, 12, 14)) == pytest.approx(0.7070846804385454)

    discount_curve = DiscountCurveZeroRates(
        anchor_date=datetime.date(2023, 10, 9),
        dates=[x[0] for x in dates_rates],
        rates=[x[1] for x in dates_rates],
        spot_date=datetime.date(2023, 10, 11)
    )

    assert discount_curve.discount(datetime.date(2030, 12, 5))  == pytest.approx(0.7079006399757061)
    assert discount_curve.discount(datetime.date(2023, 12, 14)) == pytest.approx(0.9899271035639946)


def test_real_discount_curve_annual_compounding():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'testing_data/discount_curve_rates_20231009.pickle')
    with open(file_path, 'rb') as f:
        dates_rates = pickle.load(f)

    assert sum([x[1] for x in dates_rates]) == pytest.approx(4.425019106569014)

    discount_curve = DiscountCurveZeroRates(
        anchor_date=datetime.date(2023, 10, 9),
        dates=[x[0] for x in dates_rates],
        rates=[x[1] for x in dates_rates],
        spot_date=datetime.date(2023, 10, 11),
        continuous_compounding=False
    )

    assert discount_curve.discount(datetime.date(2023, 12, 5))  == pytest.approx(0.9915392586857317)
    assert discount_curve.discount(datetime.date(2025, 12, 14)) == pytest.approx(0.8975920708568521)
    assert discount_curve.discount(datetime.date(2045, 12, 14)) == pytest.approx(0.31953615079478853)

def test_discount_curve_zero_shifted():
    anchor_date = datetime.date(2023, 10, 9)
    dates       = [datetime.date(2023, 12, 31), datetime.date(2024, 12, 31),]
    rates      = [.05, .06]
    
    discountCurve = DiscountCurveZeroRates(anchor_date, dates, rates)
    assert discountCurve.discount(datetime.date(2025, 12, 31)) == pytest.approx(.8727763175237739)
    
    discountCurveShifted = DiscountCurveZeroShifted(discountCurve, alpha=.025, beta=1.0)
    assert discountCurveShifted.discount(datetime.date(2025, 12, 31)) == pytest.approx(.8254476750488948)