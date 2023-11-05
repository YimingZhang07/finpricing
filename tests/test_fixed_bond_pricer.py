import datetime
from finpricing.market.discount_curve_zero import DiscountCurveZeroRates
from finpricing.market.survival_curve_step import SurvivalCurveStep
from finpricing.instrument.fixed_bond import FixedBond
from finpricing.instrument.fixed_coupon_leg import FixedCouponLeg
from finpricing.instrument.principal_leg import PrincipalLeg
from finpricing.model.fixed_bond_pricer import FixedBondPricer
import finpricing.utils as utils
import pytest
import os
import pickle


class TestPricer(object):
    def setup_class(self):
        self.valuation_date             = datetime.date(2023, 10, 9)
        self.spot_date                  = datetime.date(2023, 10, 11)
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
            maturity_date        = datetime.date(2028, 11, 15),
            principal_amount     = 100.0
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

        self.example_survival_curve = SurvivalCurveStep(
            anchor_date=self.valuation_date,
            dates=[
                datetime.date(2023, 10, 9),
                datetime.date(2023, 12, 31),
                datetime.date(2024, 12, 31),
            ],
            hazard_rates=[0.02, 0.02, 0.04],
        )

        self.example_survival_curve2 = SurvivalCurveStep(
            anchor_date=self.valuation_date,
            dates=[
                datetime.date(2023, 10, 9),
                datetime.date(2023, 12, 31),
                datetime.date(2024, 12, 31),
            ],
            hazard_rates=[0.0001, 0.0002, 0.0003],
        )
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'testing_data/discount_curve_rates_20231009.pickle')
        with open(file_path, 'rb') as f:
            dates_rates = pickle.load(f)
            
        self.real_discount_curve = DiscountCurveZeroRates(
            anchor_date=self.valuation_date,
            dates=[x[0] for x in dates_rates],
            rates=[x[1] for x in dates_rates],
            spot_date=self.spot_date,
            continuous_compounding=False,
        )

    def test_dummy_curves(self):
        res = self.fixed_bond_pricer.price(
            valuation_date=self.valuation_date,
            discount_curve=self.dummy_discount_curve,
            survival_curve=self.dummy_survival_curve,
        )
        assert res == pytest.approx(132.3125)
        
    def test_dummy_survival_curve(self):
        res = self.fixed_bond_pricer.price(
            valuation_date=self.valuation_date,
            discount_curve=self.example_discount_curve,
            survival_curve=self.dummy_survival_curve,
        )
        assert res == pytest.approx(100.64875434603033)

    def test_dummy_discount_curve_no_recovery(self):
        res = self.fixed_bond_pricer.price(
            valuation_date=self.valuation_date,
            discount_curve=self.dummy_discount_curve,
            survival_curve=self.example_survival_curve,
            recovery_rate=0.
        )
        assert res == pytest.approx(1.4683197878320822)
        
    def test_dummy_discount_curve_with_recovery(self):
        res = self.fixed_bond_pricer.price(
            valuation_date=self.valuation_date,
            discount_curve=self.dummy_discount_curve,
            survival_curve=self.example_survival_curve,
            recovery_rate=0.4
        )
        assert res == pytest.approx(42.15024760233873)
        
    def test_principal_only_with_recovery(self):
        fixed_coupon_leg = FixedCouponLeg(
            start_date                  = self.valuation_date,
            maturity_date_or_tenor      = datetime.date(2028, 11, 15),
            coupon_rate                 = 0.0,
            freq_type                   = utils.FrequencyTypes.SEMI_ANNUAL,
            day_count_type              = utils.DayCountTypes.THIRTY_360,
            bus_day_adj_type            = utils.BusDayAdjustTypes.NONE,
            date_gen_rule_type          = utils.DateGenRuleTypes.BACKWARD,
        )
        principal_leg = PrincipalLeg(
            maturity_date        = datetime.date(2028, 11, 15),
            principal_amount     = 100.0
        )
        fixed_bond = FixedBond(
            fixed_coupon_leg    = fixed_coupon_leg,
            principal_leg       = principal_leg
        )
        
        fixed_bond_pricer = FixedBondPricer(inst=fixed_bond)
        
        res = fixed_bond_pricer.price(
            valuation_date=self.valuation_date,
            discount_curve=self.dummy_discount_curve,
            survival_curve=self.example_survival_curve2,
            recovery_rate=0.4
        )
        
        assert res == pytest.approx(76.17414229023053)
        
    def test_principal_only_real_discount_curve(self):
        fixed_coupon_leg = FixedCouponLeg(
            start_date                  = self.valuation_date,
            maturity_date_or_tenor      = datetime.date(2028, 11, 15),
            coupon_rate                 = 0.0,
            freq_type                   = utils.FrequencyTypes.SEMI_ANNUAL,
            day_count_type              = utils.DayCountTypes.THIRTY_360,
            bus_day_adj_type            = utils.BusDayAdjustTypes.NONE,
            date_gen_rule_type          = utils.DateGenRuleTypes.BACKWARD,
        )
        principal_leg = PrincipalLeg(
            maturity_date        = datetime.date(2028, 11, 15),
            principal_amount     = 100.0
        )
        fixed_bond = FixedBond(
            fixed_coupon_leg    = fixed_coupon_leg,
            principal_leg       = principal_leg
        )
        
        fixed_bond_pricer = FixedBondPricer(inst=fixed_bond)
        
        res = fixed_bond_pricer.price(
            valuation_date=self.valuation_date,
            discount_curve=self.real_discount_curve,
            survival_curve=self.example_survival_curve2,
            recovery_rate=0.4
        )
        
        assert res == pytest.approx(61.539278472988656)
        
    def test_coupon_only_real_discount_curve(self):
        fixed_coupon_leg = FixedCouponLeg(
            start_date                  = self.valuation_date,
            maturity_date_or_tenor      = datetime.date(2028, 11, 15),
            coupon_rate                 = 0.05875,
            freq_type                   = utils.FrequencyTypes.SEMI_ANNUAL,
            day_count_type              = utils.DayCountTypes.THIRTY_360,
            bus_day_adj_type            = utils.BusDayAdjustTypes.NONE,
            date_gen_rule_type          = utils.DateGenRuleTypes.BACKWARD,
        )
        principal_leg = PrincipalLeg(
            maturity_date        = datetime.date(2028, 11, 15),
            principal_amount     = 0.0
        )
        fixed_bond = FixedBond(
            fixed_coupon_leg    = fixed_coupon_leg,
            principal_leg       = principal_leg
        )

        fixed_bond_pricer = FixedBondPricer(inst=fixed_bond)

        res = fixed_bond_pricer.price(
            valuation_date=self.valuation_date,
            discount_curve=self.real_discount_curve,
            survival_curve=self.example_survival_curve2,
            recovery_rate=0.4
        )

        assert res == pytest.approx(23.3110949812719)

    def test_with_recovery(self):
        res = self.fixed_bond_pricer.price(
            valuation_date=self.valuation_date,
            discount_curve=self.dummy_discount_curve,
            survival_curve=self.example_survival_curve2,
            recovery_rate=0.4
        )
        assert res == pytest.approx(102.2173149463539)
        
    def test_price_with_zero_basis(self):
        res = self.fixed_bond_pricer.price_with_basis(
            valuation_date=self.valuation_date,
            discount_curve=self.real_discount_curve,
            survival_curve=self.dummy_survival_curve,
            recovery_rate=0.0,
            basis=0.,
            basis_type='AdditiveZeroRates'
        )
        assert res == pytest.approx(107.33706046370256)
        
        res = self.fixed_bond_pricer.price(
            valuation_date=self.valuation_date,
            discount_curve=self.real_discount_curve,
            survival_curve=self.dummy_survival_curve,
            recovery_rate=0.4,
        )
        assert res == pytest.approx(107.33706046370256)
        
        res = self.fixed_bond_pricer.price_with_basis(
            valuation_date=self.valuation_date,
            discount_curve=self.real_discount_curve,
            survival_curve=self.example_survival_curve2,
            recovery_rate=0.4,
            basis=0.,
            basis_type='AdditiveZeroRates'
        )
        assert res == pytest.approx(84.85037345426056)
        
    def test_price_with_basis(self):
        res = self.fixed_bond_pricer.price_with_basis(
            valuation_date=self.valuation_date,
            discount_curve=self.real_discount_curve,
            survival_curve=self.example_survival_curve2,
            recovery_rate=0.4,
            basis=0.1,
            basis_type='AdditiveZeroRates'
        )
        assert res == pytest.approx(58.42861698488711)
        
        res = self.fixed_bond_pricer.price_with_basis(
            valuation_date=self.valuation_date,
            discount_curve=self.real_discount_curve,
            survival_curve=self.dummy_survival_curve,
            recovery_rate=0.4,
            basis=0.01023578384368944,
            basis_type='AdditiveZeroRates'
        )
        assert res == pytest.approx(102.61128947664841)
        
    def test_bond_basis_solver(self):
        basis = self.fixed_bond_pricer.solve_basis(
            valuation_date=self.valuation_date,
            dirty_price=102.61128888888888,
            discount_curve=self.example_discount_curve,
            survival_curve=self.example_survival_curve2,
            recovery_rate=0.4,
            basis_type='AdditiveZeroRates'
        )
        
        assert basis == pytest.approx(-0.06254360955435342)
        
        basis = self.fixed_bond_pricer.solve_basis(
            valuation_date=self.valuation_date,
            dirty_price=102.61128888888888,
            discount_curve=self.real_discount_curve,
            survival_curve=self.example_survival_curve2,
            recovery_rate=0.8,
            basis_type='AdditiveZeroRates'
        )
        assert basis == pytest.approx(-0.009357610588586696)
        
        basis = self.fixed_bond_pricer.solve_basis(
            valuation_date=self.valuation_date,
            dirty_price=102.61128888888888,
            discount_curve=self.real_discount_curve,
            survival_curve=self.dummy_survival_curve,
            recovery_rate=0.4,
            basis_type='AdditiveZeroRates'
        )
        assert basis == pytest.approx(0.01023578384368944)
        
        basis = self.fixed_bond_pricer.solve_basis(
            valuation_date=self.valuation_date,
            dirty_price=102.61128888888888,
            discount_curve=self.real_discount_curve,
            survival_curve=self.example_survival_curve2,
            recovery_rate=0.4,
            basis_type='AdditiveZeroRates'
        )
        assert basis == pytest.approx(-0.04811155472849047)