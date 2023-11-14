import datetime
from typing import Union, List
from ..utils import Date, CDSStyle, DateGenerator, datetimeToDates
from ..market import CDSCurve, RecoveryCurve
from .cds_pricer import CDSPricer
from ..instrument.cds import CreditDefaultSwap


@datetimeToDates
def cds_market_spread(
    discount_curve,
    survival_curve,
    recovery_rate: float,
    expiry: Union[datetime.date, Date],
    cds_style: Union[CDSStyle, str]="CORP_NA",
    granularity: int = 14,
):
    """Calculate CDS market spread
    
    NOTE this returns the par spread of a temporary CDS contract and priced by the given discount curve \
        and survival curve
    """
    _cds_style = CDSStyle(cds_style)
    
    cdsEffectiveDate = DateGenerator.generate_cds_effective_date(discount_curve.anchor_date,
                                                                 expiry,
                                                                 _cds_style)
    cdsMaturityDate = DateGenerator.generate_cds_maturity_date(discount_curve.anchor_date,
                                                               expiry,
                                                               _cds_style.cds_term_style)
    
    cds = CreditDefaultSwap.make_standard(
        effective_date=cdsEffectiveDate,
        maturity_date=cdsMaturityDate,
        spread=1.0,
        notional=1.0,
        cds_style=_cds_style,
    )
    
    pricer = CDSPricer.from_cds(
        cds=cds,
        discount_curve=discount_curve,
        survival_curve=survival_curve,
        recovery_rate=recovery_rate,
        granularity=granularity,
    )
    
    upfront_payment_date = pricer.generate_upfront_payment_date()
    upfront_df = discount_curve.discount(upfront_payment_date)
    accrued_interest = pricer.coupon_leg_accrued_interest()
    pv_annuity = pricer.pv_annuity()
    pv_annuity -= accrued_interest * upfront_df
    spread = -1 * pricer.pv_contingent_leg() / pv_annuity
        
    return spread

def cds_market_spreads(discount_curve,
                       survival_curve,
                       recovery_rate: float,
                       expiries: List[Union[datetime.date, Date]],
                       **kwargs):
    """Calculate CDS market spreads for a list of expiries"""
    return [cds_market_spread(discount_curve, survival_curve, recovery_rate, expiry, **kwargs) for expiry in expiries]
