from finpricing.market.discount_curve_zero import DiscountCurveZeroRates, DiscountCurveZeroShifted
import datetime
import pytest
import os
import pickle

def test_discount():
    
    anchor_date = datetime.date(2023, 10, 9)
    
    dates       = [
        datetime.date(2023, 12, 31),
        datetime.date(2024, 12, 31),
    ]
    
    rates      = [
        .05,
        .06
    ]
    
    discountCurve = DiscountCurveZeroRates(anchor_date, dates, rates)
    
    assert discountCurve.discount(datetime.date(2023, 10, 9)) == pytest.approx(1.)
    assert discountCurve.discount(datetime.date(2023, 10, 10)) == pytest.approx(.9998630230808251)
    assert discountCurve.discount(datetime.date(2023, 10, 31)) == pytest.approx(.9969908380010889)
    assert discountCurve.discount(datetime.date(2025, 10, 31)) == pytest.approx(.8819061927598262)
    
def test_discount_2():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'test_data/discount_curve_rates_20231009.pickle')
    with open(file_path, 'rb') as f:
        dates_rates = pickle.load(f)
        
    discount_curve = DiscountCurveZeroRates(
        anchor_date=datetime.date(2023, 10, 9),
        dates=[x[0] for x in dates_rates],
        rates=[x[1] for x in dates_rates],
    )
    
    discount_curve.discount(datetime.date(2023, 10, 31)) == pytest.approx(0.9967383750912533)
    discount_curve.discount(datetime.date(2025, 10, 31)) == pytest.approx(0.9022576658755044)
    discount_curve.discount(datetime.date(2028, 10, 31)) == pytest.approx(0.7890060517290453)
    discount_curve.discount(datetime.date(2035, 10, 31)) == pytest.approx(0.5597111228433488)
    
def test_discount_curve_zero_shifted():
    anchor_date = datetime.date(2023, 10, 9)
    
    dates       = [
        datetime.date(2023, 12, 31),
        datetime.date(2024, 12, 31),
    ]
    
    rates      = [
        .05,
        .06
    ]
    
    discountCurve = DiscountCurveZeroRates(anchor_date, dates, rates)
    assert discountCurve.discount(datetime.date(2025, 12, 31)) == pytest.approx(.8727763175237739)
    
    discountCurveShifted = DiscountCurveZeroShifted(discountCurve, alpha=.025, beta=1.0)
    assert discountCurveShifted.discount(datetime.date(2025, 12, 31)) == pytest.approx(.8254476750488948)