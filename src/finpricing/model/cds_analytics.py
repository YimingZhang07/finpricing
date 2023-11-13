import datetime
from typing import Union, List
from ..utils import Date, CDSStyle
from ..market import CDSCurve, RecoveryCurve
from .cds_pricer import CDSPricer
from ..instrument.cds import CreditDefaultSwap


def cds_market_spread(
    discount_curve,
    survival_curve,
    recovery_rate: RecoveryCurve,
    expiry: Union[datetime.date, Date],
    cds_style: Union[CDSStyle, str]="CORP_NA",
    granularity: int = 14,
):
    """Calculate CDS market spread from discount curve, survival curve and recovery curve
    """
    _cds_style = CDSStyle(cds_style)
    
    cds = CreditDefaultSwap.make_standard(
        effective_date=discount_curve.anchor_date,
        maturity_date=expiry,
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
    pv_annuity = pricer.pv_annuity() - accrued_interest * upfront_df
    spread = -1 * pricer.pv_contingent_leg() / pv_annuity
        
    return spread
