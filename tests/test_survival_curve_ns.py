from finpricing.market.survival_curve_ns import SurvivalCurveNelsonSiegel
import datetime
import pytest

def test_survival():
    
    anchor_date = datetime.date(2023, 10, 9)
    pivot_dates = [
        datetime.date(2025, 6, 15),
        datetime.date(2029, 5, 15),
    ]
    params     = [
        9.30273031e-05,
        -0.0651474,
        0.04588889,
    ]
    
    survCurve = SurvivalCurveNelsonSiegel(anchor_date, pivot_dates, params)
    
    assert survCurve.survival(datetime.date(2023, 10, 9)) == pytest.approx(1.)
    assert survCurve.survival(datetime.date(2030, 10, 10)) == pytest.approx(.8600481704)