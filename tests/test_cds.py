import pytest
import datetime
from finpricing.utils import *
from finpricing.instrument.cds import *
from finpricing.model.cds_pricer import CDSPricer
from finpricing.model.cds_analytics import cds_market_spread
from finpricing.market.survival_curve_ns import SurvivalCurveNelsonSiegel
from .testing_utils.read_data import get_sample_discount_curve

# import sys
# sys.path.append(r'./')
# from testing_utils.read_data import get_sample_discount_curve


class TestCDSUtils(object):
    def setup_class(self):
        self.date_generator = DateGenerator()

    def test_date_generator(self):
        dates = self.date_generator.generate_extended(
            start_date=datetime.date(2023, 9, 16),
            maturity_date=datetime.date(2028, 11, 15),
            time_interval="3m",
            stub_at_end=True,
        )
        assert dates[0] == datetime.date(2023, 9, 16)
        assert dates[-1] == datetime.date(2028, 12, 16)

        dates = self.date_generator.generate_cds(
            start_date=datetime.date(2023, 8, 15),
            maturity_date=datetime.date(2028, 11, 15),
            cds_style=CDSStyle("CORP_NA"),
        )
        assert dates[0] == datetime.date(2023, 11, 15)
        assert dates[-1] == datetime.date(2028, 11, 15)

    def test_generate_cds_adjust(self):
        (
            accrual_start,
            accrual_end,
            payment_dates,
        ) = self.date_generator.generate_cds_adjust(
            start_date=datetime.date(2023, 8, 15),
            maturity_date=datetime.date(2028, 11, 15),
            cds_style=CDSStyle("CORP_NA"),
        )
        
        assert datetime.date(2025, 2, 17) in accrual_start
        assert datetime.date(2026, 11, 16) in accrual_start
        assert datetime.date(2027, 5, 17) in accrual_start
        assert accrual_start[0] == datetime.date(2023, 8, 15)
        assert accrual_end[0] == datetime.date(2023, 11, 15)
        assert payment_dates[-1] == datetime.date(2028, 11, 15)


class TestCDSInstrument:
    def setup_class(self):
        self.effective_date = datetime.date(2023, 8, 15)
        self.maturity_date = datetime.date(2028, 11, 15)
        self.cds_style = "CORP_NA"
    
    def test_make_cds(self):
        cds = CreditDefaultSwap.make_standard(
            effective_date=self.effective_date,
            maturity_date=self.maturity_date,
            spread=1.,
            notional=1.,
            cds_style=self.cds_style
        )
        
        cds.fixed_coupon_leg.print_cashflows()
        
        assert cds.contingent_leg.protection_start_date == datetime.date(2023, 8, 15)
        assert cds.fixed_coupon_leg.payment_dates[-1] == datetime.date(2028, 11, 15)
        assert cds.fixed_coupon_leg.accrual_start[-1] == datetime.date(2028, 8, 15)
        
        
class TestCDSPricer:
    def setup_class(self):
        self.valuation_date = datetime.date(2023, 10, 9)
        self.discount_curve = get_sample_discount_curve()
        self.survival_curve = SurvivalCurveNelsonSiegel(
            anchor_date=self.valuation_date,
            pivot_dates=[datetime.date(2025, 6, 15), datetime.date(2029, 5, 15)],
            params=[9.302730314829907e-05, -0.06514745005077575, 0.045888893535974966],
        )
        self.cds = CreditDefaultSwap.make_standard(
            effective_date=datetime.date(2023, 8, 15),
            maturity_date=datetime.date(2028, 11, 15),
            spread=1.,
            notional=1.,
            cds_style="CORP_NA"
        )
        self.cds_pricer = CDSPricer.from_cds(cds=self.cds,
                                             discount_curve=self.discount_curve,
                                             survival_curve=self.survival_curve,
                                             recovery_rate=0.4,
                                             granularity=14,
                                             include_accrued=True)
    def test_pv(self):
        assert self.cds_pricer.pv_coupon_leg() == pytest.approx(4.553353410660466)
        assert self.cds_pricer.pv_contingent_leg(recovery_rate=0.0) ==\
            pytest.approx(-0.07993120902753376)
        assert self.cds_pricer.pv_contingent_leg(recovery_rate=0.4) ==\
            pytest.approx(-0.04795872541652026)
        assert self.cds_pricer.pv_contingent_leg(recovery_rate=1.0) ==\
            pytest.approx(0.0)
        assert self.cds_pricer.par_spread() == pytest.approx(0.010532616533616227)
            
    def test_accrued_interest(self):
        assert self.cds_pricer.coupon_leg_accrued_interest() == pytest.approx(0.15555555555555556)
        
class TestCDSAnalytics:
    def setup_class(self):
        self.valuation_date = datetime.date(2023, 10, 9)
        self.discount_curve = get_sample_discount_curve()
        self.survival_curve = SurvivalCurveNelsonSiegel(
            anchor_date=self.valuation_date,
            pivot_dates=[datetime.date(2025, 6, 15), datetime.date(2029, 5, 15)],
            params=[9.302730314829907e-05, -0.06514745005077575, 0.045888893535974966],
        )
        self.cds = CreditDefaultSwap.make_standard(
            effective_date=datetime.date(2023, 8, 15),
            maturity_date=datetime.date(2028, 11, 15),
            spread=1.,
            notional=1.,
            cds_style="CORP_NA"
        )
        self.cds_pricer = CDSPricer.from_cds(cds=self.cds,
                                             discount_curve=self.discount_curve,
                                             survival_curve=self.survival_curve,
                                             recovery_rate=0.4,
                                             granularity=14,
                                             include_accrued=True)
        
    def test_cds_market_spread(self):
        assert cds_market_spread(
            discount_curve=self.discount_curve,
            survival_curve=self.survival_curve,
            recovery_rate=0.4,
            cds_style="CORP_NA",
            expiry=datetime.date(2028, 11, 15),
            granularity=14,
        ) == pytest.approx(0.01090499740022582)
        
        
if __name__ == "__main__":
    test = TestCDSPricer()
    test.setup_class()
    test.test_pv()
    