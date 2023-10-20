from finpricing.market.discount_curve_zero import DiscountCurveZeroRates
import datetime
import pytest

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