import datetime
import finpricing.utils as utils
from finpricing.market.survival_curve_step import SurvivalCurveStep
import pytest
import math

class TestSurvivalCurveStep:
    def test_survival_curve_step1(self):
        valuation_date = datetime.date(2023, 10, 9)
        survival_curve = SurvivalCurveStep(
            anchor_date=valuation_date,
            dates=[
                datetime.date(2023, 12, 31),
                datetime.date(2024, 12, 31),
            ],
            hazard_rates=[0.0, 0.0],
        )
        assert survival_curve.survival(valuation_date) == pytest.approx(1.0)
        assert survival_curve.survival(datetime.date(2024, 12, 31)) == pytest.approx(1.0)
        
    def test_survival_curve_step2(self):
        valuation_date = datetime.date(2023, 10, 9)
        survival_curve = SurvivalCurveStep(
            anchor_date=valuation_date,
            dates=[
                datetime.date(2023, 12, 31),
                datetime.date(2024, 12, 31),
            ],
            hazard_rates=[0.2, 0.4],
        )
        assert survival_curve.survival(valuation_date) == pytest.approx(1.0)
        assert survival_curve.survival(datetime.date(2023, 10, 10)) == pytest.approx(math.exp(-0.2))
        assert survival_curve.survival(datetime.date(2023, 10, 31)) == pytest.approx(math.exp(-0.2 * 22))
        assert survival_curve.survival(datetime.date(2023, 11, 30)) == pytest.approx(math.exp(-0.2 * 52))
        assert survival_curve.survival(datetime.date(2023, 12, 31)) == pytest.approx(math.exp(-0.2 * 83))