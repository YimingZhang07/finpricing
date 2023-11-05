import datetime
import pytest
import json
import pickle
import os
from finpricing.market.discount_curve_zero import DiscountCurveZeroRates
from finpricing.market.survival_curve_ns import SurvivalCurveNelsonSiegel
from finpricing.model.bond_curve_solver import BondCurveAnalyticsHelper
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

        self.bonds, self.dirty_prices = parse_bond_info(self.valuation_date, bonds_info_dict)

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
            spot_date=self.valuation_date,
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

    def test_get_bond_bases_no_survival(self):
        helper = BondCurveAnalyticsHelper(self.bonds)
        helper.dirty_prices = self.dirty_prices
        helper.discount_curves = self.discount_curve
        helper.survival_curves = self.dummy_survial_curve
        helper.recovery_rates = [0.4] * len(self.bonds)
        helper.settlement_dates = [self.spot_date] * len(self.bonds)
        bases = helper.get_bond_bases(self.valuation_date)
        # it's hard for the solver the match exactly, so a 10 basis point tolerance is used
        for i in range(len(bases)):
            assert bases[i] == pytest.approx(self.bases_no_survival[i], abs=10e-4)


# if __name__ == "__main__":
#     test = TestPricer()
#     test.setup_class()
#     test.test_get_bond_bases_no_survival()
