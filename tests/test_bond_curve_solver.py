import datetime
from finpricing.market.discount_curve_zero import DiscountCurveZeroRates
from finpricing.instrument.fixed_bond import FixedBond
from finpricing.instrument.fixed_coupon_leg import FixedCouponLeg
from finpricing.instrument.principal_leg import PrincipalLeg
from finpricing.market.survival_curve_ns import SurvivalCurveNelsonSiegel
from finpricing.model.bond_curve_solver import BondCurveAnalyticsHelper
import finpricing.utils as utils
import pytest
import json
import pickle
import os




class TestPricer(object):
    def setup_class(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.valuation_date             = datetime.date(2023, 10, 9)
        
        file_path = os.path.join(script_dir, 'test_data/bondcurve_portfolio.json')
        with open(file_path, 'rb') as json_data:
            bondsDict = json.load(json_data)
            json_data.close()
        
        self.bonds = []
        self.dirty_prices = []
        for bond in bondsDict:
            fixed_coupon_leg = FixedCouponLeg(
                start_date                  = self.valuation_date,
                maturity_date_or_tenor      = datetime.date.fromisoformat(bondsDict[bond]['MaturityDate']),
                coupon_rate                 = float(bondsDict[bond]['CouponRate']) / 100,
                freq_type                   = utils.FrequencyTypes.SEMI_ANNUAL,
                day_count_type              = utils.DayCountTypes.THIRTY_360,
                bus_day_adj_type            = utils.BusDayAdjustTypes.NONE,
                date_gen_rule_type          = utils.DateGenRuleTypes.BACKWARD,
            )
            principal_leg = PrincipalLeg(
                maturity_date        = datetime.date.fromisoformat(bondsDict[bond]['MaturityDate']),
                principal_amount     = 100.
            )
            bond_inst = FixedBond(
                fixed_coupon_leg    = fixed_coupon_leg,
                principal_leg       = principal_leg
            )
            self.bonds.append(bond_inst)
            self.dirty_prices.append(float(bondsDict[bond]['DirtyPrice']))
            
            
        file_path = os.path.join(script_dir, 'test_data/discount_curve_rates_20231009.pickle')
        with open(file_path, 'rb') as f:
            dates_rates = pickle.load(f)
            
        self.discount_curve = DiscountCurveZeroRates(
            anchor_date=self.valuation_date,
            dates=[x[0] for x in dates_rates],
            rates=[x[1] for x in dates_rates],
        )
        
        self.survival_curve1 = SurvivalCurveNelsonSiegel(
            anchor_date=self.valuation_date,
            pivot_dates=[datetime.date(2025, 6, 15), datetime.date(2029, 5, 15)],
            params=[9.30273031482991e-5,
                    -0.0651474500507758,
                    0.045888893535975]
        )
        
        self.survival_curve2 = SurvivalCurveNelsonSiegel(
            anchor_date=self.valuation_date,
            pivot_dates=[datetime.date(2025, 6, 15), datetime.date(2029, 5, 15)],
            params=[0., 0., 0.])
        
    def test_bond_analytics_helper(self):
        helper = BondCurveAnalyticsHelper(self.bonds)
        helper.dirty_prices = self.dirty_prices
        helper.discount_curves = self.discount_curve
        helper.survival_curves = self.survival_curve2
        helper.recovery_rates = [0.4] * len(self.bonds)
        bases = helper.get_bond_bases(self.valuation_date)
        assert bases[-1] == pytest.approx(0.007313280104532152)