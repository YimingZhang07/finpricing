from typing import Union, List
import datetime

from ..utils import (
    Literal,
    Date,
    CDSStyle,
    DateGenerator,
    DayCountTypes,
    ClassUtil
)

from .fixed_coupon_leg import FixedCouponLegBase

class CDSFixedCouponLeg(FixedCouponLegBase):
    def __init__(self,
                 effective_date: Union[Date, datetime.date],
                 maturity_date: Union[Date, datetime.date],
                 spread: float,
                 notional: float = Literal.UNIT.value,
                 cds_style: CDSStyle = CDSStyle.CORP_NA(),
                 pay_day_delay: int = 0,):
        """
        TODO: add pay_day_delay to generate_cds_adjust
        """
        accrual_start, accrual_end, payment_dates = \
            DateGenerator.generate_cds_adjust(
                start_date=effective_date,
                maturity_date=maturity_date,
                cds_style=cds_style,
                stub_at_end=False,
        )
        super().__init__(
            coupon_rate=spread,
            payment_dates=payment_dates,
            accrual_start=accrual_start,
            accrual_end=accrual_end,
            notional=notional,
            day_count_type=DayCountTypes.ACT_360,
        )
        
    @property
    def spread(self):
        return self.coupon_rate
    
class CDSContingentLeg(ClassUtil):
    def __init__(self,
                 protection_start_date: Union[Date, datetime.date],
                 protection_end_date: Union[Date, datetime.date],
                 notional: float,
                 fixed_recovery: bool,
                 recovery_rate: float,
                 pay_at_end: bool,
                 payment_date: Union[Date, datetime.date],):
        self.save_attributes()
        
    @classmethod
    def make_simple(cls,
                    protection_start_date: Union[Date, datetime.date],
                    protection_end_date: Union[Date, datetime.date],
                    notional: float = Literal.UNIT.value,):
        return cls(
            protection_start_date=protection_start_date,
            protection_end_date=protection_end_date,
            notional=notional,
            fixed_recovery=False,
            recovery_rate=Literal.ZERO.value,
            pay_at_end=False,
            payment_date=None,
        )
        
class CreditDefaultSwap:
    def __init__(self,
                 fixed_coupon_leg: CDSFixedCouponLeg,
                 contingent_leg: CDSContingentLeg) -> None:
        self.fixed_coupon_leg = fixed_coupon_leg
        self.contingent_leg = contingent_leg
    
    @classmethod
    def make_standard(cls,
                      effective_date: Union[Date, datetime.date],
                      maturity_date: Union[Date, datetime.date],
                      spread: float,
                      notional: float = Literal.UNIT.value,
                      cds_style: Union[CDSStyle, str] = "CORP_NA",
                      pay_day_delay: int = 0,):
        fixed_coupon_leg = CDSFixedCouponLeg(
            effective_date=effective_date,
            maturity_date=maturity_date,
            spread=spread,
            notional=notional,
            cds_style=CDSStyle.from_name(cds_style),
            pay_day_delay=pay_day_delay,
        )
        contingent_leg = CDSContingentLeg.make_simple(
            protection_start_date=effective_date,
            protection_end_date=maturity_date,
            notional=-notional,
        )
        return cls(
            fixed_coupon_leg=fixed_coupon_leg,
            contingent_leg=contingent_leg,
        )