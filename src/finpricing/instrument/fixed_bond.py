from ..utils import *
from .fixed_coupon_leg import FixedCouponLeg
from .principal_leg import PrincipalLeg

class FixedBond(ClassUtil):
    def __init__(self,
                 fixed_coupon_leg: FixedCouponLeg,
                 principal_leg: PrincipalLeg):
        self.save_attributes()