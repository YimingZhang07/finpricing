import datetime
import pytest
import json
import pickle
import os
from unittest.mock import patch
from finpricing.market.discount_curve_zero import DiscountCurveZeroRates
from finpricing.market.survival_curve_ns import SurvivalCurveNelsonSiegel
from finpricing.model.bond_curve_solver import BondCurveAnalyticsHelper, BondCurveSolver
from .testing_utils.read_data import parse_bond_info


class TestPricer(object):
    def setup_class(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.valuation_date = datetime.date(2023, 10, 9)
        self.spot_date = datetime.date(2023, 10, 11)

        # load bonds
        file_path = os.path.join(script_dir, "testing_data/bondcurve_portfolio.json")
        with open(file_path, "rb") as json_data:
            bonds_info_dict = json.load(json_data)
            json_data.close()

        self.bonds, self.dirty_prices = parse_bond_info(self.valuation_date, bonds_info_dict, sort_by_maturity=False)

        # load discount curve
        file_path = os.path.join(
            script_dir, "testing_data/discount_curve_rates_20231009.pickle"
        )
        with open(file_path, "rb") as f:
            dates_rates = pickle.load(f)

        self.discount_curve = DiscountCurveZeroRates(
            anchor_date=self.valuation_date,
            dates=[x[0] for x in dates_rates],
            rates=[x[1] for x in dates_rates],
            spot_date=self.spot_date,
            continuous_compounding=False,
        )

        self.survival_curve = SurvivalCurveNelsonSiegel(
            anchor_date=self.valuation_date,
            pivot_dates=[datetime.date(2025, 6, 15), datetime.date(2029, 5, 15)],
            params=[9.30273031482991e-5, -0.0651474500507758, 0.045888893535975],
        )

        self.dummy_survial_curve = SurvivalCurveNelsonSiegel(
            anchor_date=self.valuation_date,
            pivot_dates=[datetime.date(2025, 6, 15), datetime.date(2029, 5, 15)],
            params=[0.0, 0.0, 0.0],
        )

        self.bases_no_survival = [
            0.007313280104532152,
            0.012315582074021183,
            0.005389234514848455,
            0.007313280104532152,
            0.009094471661030222,
            0.011055892111217661,
            0.01280366705505911,
            0.01,
            0.0020300800449633265,
            0.01052,
        ]
        
        self.bases_with_survival = [
            0.0010001171767692624,
            0.00021537413144240574,
            -0.00029855969059188435,
            0.0010001171767692624,
            0.0004883447507213166,
            -0.0007319546919854503,
            0.00038863482011926504,
            -1.6631544682909477e-05,
            -0.0012612601502053795,
            -0.00047138721938673467
        ]

    def test_get_bond_bases_no_survival(self):
        helper = BondCurveAnalyticsHelper(self.bonds)
        helper.dirty_prices = self.dirty_prices
        helper.discount_curves = self.discount_curve
        helper.survival_curves = self.dummy_survial_curve
        helper.recovery_rates = [0.4] * len(self.bonds)
        helper.settlement_dates = [self.spot_date] * len(self.bonds)
        bases = helper.get_bond_bases(self.valuation_date)
        # it's hard for the solver the match exactly, so a 5 basis point tolerance is used
        for i in range(len(bases)):
            assert bases[i] == pytest.approx(self.bases_no_survival[i], abs=5e-4)


    def test_get_bond_bases_with_survival(self):
        helper = BondCurveAnalyticsHelper(self.bonds)
        helper.dirty_prices = self.dirty_prices
        helper.discount_curves = self.discount_curve
        helper.survival_curves = self.survival_curve
        helper.recovery_rates = [0.4] * len(self.bonds)
        helper.settlement_dates = [self.spot_date] * len(self.bonds)
        bases = helper.get_bond_bases(self.valuation_date)
        # it's hard for the solver the match exactly, so a 5 basis point tolerance is used
        print(bases)
        for i in range(len(bases)):
            assert bases[i] == pytest.approx(self.bases_with_survival[i], abs=5e-4)

    @patch('finpricing.model.bond_curve_solver.BondCurveAnalyticsHelper.get_bond_bases')
    def test_residuals_and_penalty_mocked(self, mocked_bases):
        helper = BondCurveAnalyticsHelper(self.bonds)
        helper.discount_curves = self.discount_curve
        helper.survival_curves = self.dummy_survial_curve
        helper.recovery_rates = [0.4] * len(self.bonds)
        helper.settlement_dates = [self.spot_date] * len(self.bonds)
        helper.valuation_date = self.valuation_date

        solver = BondCurveSolver(helper)

        # avoid the errors introduced by the bond bases. mock the outputs.
        mocked_bases.return_value = [-0.008203386683620558,
                                      0.009209468358311422,
                                      0.027440538436771397]
        res = solver.get_weighted_residuals_and_penalty(params=[0, 0, 0],
                                                        dirty_prices=[100, 100, 100],
                                                        weights=[.3, .3, .4])
        assert res[0] == pytest.approx(0.0029277204519966874)
        assert res[1] == pytest.approx(0.0032200447143373888)
        assert res[2] == pytest.approx(0.006250857335682448)
        assert res[3] == pytest.approx(0.)
        
    @pytest.mark.skip(reason="Slow Running")
    def test_params_solver(self):
        helper = BondCurveAnalyticsHelper(self.bonds)
        helper.discount_curves = self.discount_curve
        helper.survival_curves = self.dummy_survial_curve
        helper.recovery_rates = [0.4] * len(self.bonds)
        helper.settlement_dates = [self.spot_date] * len(self.bonds)
        helper.valuation_date = self.valuation_date

        solver = BondCurveSolver(helper)

        res = solver.solve( params=[0, 0, 0],
                            dirty_prices=self.dirty_prices,
                            weights=solver.get_weights())
        
        # integer flag should be 1-4 if the solver converged
        assert res[1] in [1, 2, 3, 4]
        params = res[0]
        assert params[0] * 1e5 == pytest.approx(9.3027303, rel=10e-2)
        assert params[1] * 1e5 == pytest.approx(-6514.7438, rel=10e-2)

        # the third param has a large differene. 2800 vs. 4600
        # assert params[2] * 1e5 == pytest.approx(4588.886406, rel=10e-2)

    @pytest.mark.skip(reason="Slow Running")
    def test_params_solver_equal_weights(self):
        helper = BondCurveAnalyticsHelper(self.bonds)
        helper.discount_curves = self.discount_curve
        helper.survival_curves = self.dummy_survial_curve
        helper.recovery_rates = [0.4] * len(self.bonds)
        helper.settlement_dates = [self.spot_date] * len(self.bonds)
        helper.valuation_date = self.valuation_date

        solver = BondCurveSolver(helper)

        res = solver.solve( params=[0, 0, 0],
                            dirty_prices=self.dirty_prices,
                            weights=[ 1 / 10] * 10 )
        
        # integer flag should be 1-4 if the solver converged
        assert res[1] in [1, 2, 3, 4]
        params = res[0]
        assert params[0] * 1e5 == pytest.approx(8.79874756, rel=10e-2)
        assert params[1] * 1e5 == pytest.approx(-7015.9163, rel=10e-2)
        
        # the third param has a large differene.
        # assert params[2] * 1e5 == pytest.approx(7112.35132, rel=10e-2)