from finpricing.model.utils.bond_pricing_utils import hazard_rate_from_probs, principal_integral
from finpricing.market.discount_curve_zero import DiscountCurveZeroRates
from finpricing.market.survival_curve_step import SurvivalCurveStep
from finpricing.utils import *
import datetime
import pytest
import math

class TestBondPricingUtils(object):
    def setup_class(self):
        
        self.valuation_date = datetime.date(2023, 10, 9)
        
        self.dummy_discount_curve   = DiscountCurveZeroRates(
            anchor_date=self.valuation_date,
            dates=[
                datetime.date(2023, 12, 31),
                datetime.date(2024, 12, 31),
            ],
            rates=[0.0, 0.0],
        )
        
        self.dummy_survival_curve = SurvivalCurveStep(
            anchor_date=self.valuation_date,
            dates=[
                datetime.date(2023, 12, 31),
                datetime.date(2024, 12, 31),
            ],
            hazard_rates=[0.0, 0.0],
            
        )

    def test_hazard_rate_from_probs(self):
        res = hazard_rate_from_probs(
            0.9,
            0.8,
            datetime.date(2020, 1, 1),
            datetime.date(2021, 1, 1),
            DayCountTypes.ACT_ACT_ISDA
        )
        
        assert res == pytest.approx(math.log(0.9 / 0.8))
        
    def test_principal_integral(self):
        res = principal_integral(
            N=100,
            R=0.8,
            valuation_date=self.valuation_date,
            maturity_date=datetime.date(2024, 12, 31),
            granularity_in_days=14,
            survival_curve=self.dummy_survival_curve,
            discount_curve=self.dummy_discount_curve,
        )
        
        assert res == pytest.approx(0)