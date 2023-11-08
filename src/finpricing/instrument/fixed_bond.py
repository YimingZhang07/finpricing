from ..utils import *
from .fixed_coupon_leg import FixedCouponLeg
from .principal_leg import PrincipalLeg

class FixedBond(ClassUtil):
    def __init__(self,
                 fixed_coupon_leg: FixedCouponLeg,
                 principal_leg: PrincipalLeg):
        self.save_attributes()
        
    @property
    def maturity_date(self):
        # this is better to be the latest maturity date of all legs
        return self.principal_leg.maturity_date
    
    @property
    def coupon_rate(self):
        return self.fixed_coupon_leg.coupon_rate
    
    def __repr__(self) -> str:
        return f"{self.coupon_rate:.3%} {self.maturity_date.strftime(r'%m/%d/%y')}"