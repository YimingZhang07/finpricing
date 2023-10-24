import datetime
from finpricing.market.discount_curve_zero import DiscountCurveZeroRates
from finpricing.market.survival_curve_step import SurvivalCurveStep
from finpricing.instrument.fixed_bond import FixedBond
from finpricing.instrument.fixed_coupon_leg import FixedCouponLeg
from finpricing.instrument.principal_leg import PrincipalLeg
from finpricing.model.fixed_bond_pricer import FixedBondPricer
import finpricing.utils as utils
import pytest


class TestPricer(object):
    def setup_class(self):
        self.valuation_date             = datetime.date(2023, 10, 9)
        self.fixed_coupon_leg           = FixedCouponLeg(
            start_date                  = self.valuation_date,
            maturity_date_or_tenor      = datetime.date(2028, 11, 15),
            coupon_rate                 = 0.05875,
            freq_type                   = utils.FrequencyTypes.SEMI_ANNUAL,
            day_count_type              = utils.DayCountTypes.THIRTY_360,
            bus_day_adj_type            = utils.BusDayAdjustTypes.NONE,
            date_gen_rule_type          = utils.DateGenRuleTypes.BACKWARD,
        )
        self.principal_leg = PrincipalLeg(
            date        = datetime.date(2028, 11, 15),
            amount      = 100.0
        )
        self.fixed_bond = FixedBond(
            fixed_coupon_leg    = self.fixed_coupon_leg,
            principal_leg       = self.principal_leg
        )
        self.fixed_bond_pricer      = FixedBondPricer(inst=self.fixed_bond)
        
        self.dummy_discount_curve   = DiscountCurveZeroRates(
            anchor_date=self.valuation_date,
            dates=[
                datetime.date(2023, 12, 31),
                datetime.date(2024, 12, 31),
            ],
            rates=[0.0, 0.0],
        )
        
        self.example_discount_curve = DiscountCurveZeroRates(
            anchor_date=self.valuation_date,
            dates=[
                datetime.date(2023, 12, 31),
                datetime.date(2024, 12, 31),
            ],
            rates=[0.05, 0.06],
        )
        self.dummy_survival_curve = SurvivalCurveStep(
            anchor_date=self.valuation_date,
            dates=[
                datetime.date(2023, 12, 31),
                datetime.date(2024, 12, 31),
            ],
            hazard_rates=[0.0, 0.0],
            
        )

    def test_dummy_curves(self):
        res = self.fixed_bond_pricer.Price(
            valuation_date=self.valuation_date,
            discount_curve=self.dummy_discount_curve,
            survival_curve=self.dummy_survival_curve,
        )
        assert res == pytest.approx(132.3125)
        
    def test_dummy_survival_curve(self):
        res = self.fixed_bond_pricer.Price(
            valuation_date=self.valuation_date,
            discount_curve=self.example_discount_curve,
            survival_curve=self.dummy_survival_curve,
        )
        assert res == pytest.approx(100.64875434603033)

    # def test_dummy_discount_curve(self):
    #     res = self.fixed_bond_pricer.Price(
    #         valuation_date=self.valuation_date,
    #         discount_curve=self.dummy_discount_curve,
    #         survival_curve=self.example_survival_curve,
    #     )
    #     assert res == pytest.approx(132.3125)