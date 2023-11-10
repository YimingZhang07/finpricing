import datetime
from typing import Union
from ..utils import ClassUtil, Date
from ..instrument.cds import CDSFixedCouponLeg, CDSContingentLeg, CreditDefaultSwap
from ..model.utils.bond_pricing_utils import accrual_integral

class CDSPricer(ClassUtil):
    def __init__(self,
                 fixed_coupon_leg: CDSFixedCouponLeg,
                 contingent_leg: CDSContingentLeg,
                 discount_curve,
                 survival_curve,
                 recovery_rate,
                 granularity,
                 include_accrued: bool) -> None:
        self.save_attributes()
    
    @classmethod
    def from_cds(cls,
                 cds: CreditDefaultSwap,
                 discount_curve,
                 survival_curve,
                 recovery_rate,
                 granularity,
                 include_accrued: bool):
        return cls(
            fixed_coupon_leg=cds.fixed_coupon_leg,
            contingent_leg=cds.contingent_leg,
            discount_curve=discount_curve,
            survival_curve=survival_curve,
            recovery_rate=recovery_rate,
            granularity=granularity,
            include_accrued=include_accrued
        )
    
    @property
    def coupon_cashflows(self):
        return self.fixed_coupon_leg.cashflows
    
    def pv_coupon_leg(self,
              valuation_date: Union[datetime.date, Date] = None,
              survival_curve = None,
              discount_curve = None,
              recovery_rate: float = 0.4) -> float:
        """risky pricing of a fixed bond
        
        Args:
            valuation_date: valuation date
            survival_curve: survival curve
            discount_curve: discount curve
            recovery_rate: recovery rate
            
        Returns:
            Dirty price of the bond.
        """
        discount_curve = self.first_valid(discount_curve, self.discount_curve)
        survival_curve = self.first_valid(survival_curve, self.survival_curve)
        recovery_rate  = self.first_valid(recovery_rate, self.recovery_rate)
        valuation_date = self.first_valid(valuation_date, discount_curve.anchor_date)
        
        valuation_date = Date.convert_from_datetime(valuation_date)

        pv = 0.0

        for i, item in enumerate(self.coupon_cashflows):
            date = item[0]
            amount = item[1]
            accrual_start_date = self.fixed_coupon_leg.accrual_start[i].add_tenor("-1d")
            accrual_end_date = self.fixed_coupon_leg.accrual_end[i].add_tenor("-1d")
            # period_start_date = max(valuation_date, accrual_start_date)

            if date > valuation_date:
                df = discount_curve.discount(date)
        
                discounted_amount = df * survival_curve.survival(date.add_tenor("-1d")) * amount
                
                accrual = amount * accrual_integral(
                    start_date=None,
                    granularity_in_days=14,
                    R=1.,
                    survival_curve=survival_curve,
                    discount_curve=discount_curve,
                    accrual_start_date=accrual_start_date,
                    accrual_end_date=accrual_end_date
                )

                print(f"{amount:.12f}\t{df:.12f}\t{discounted_amount:.12f}\t{accrual:.12f}\t{discounted_amount+accrual:.12f}")
                pv = pv + discounted_amount + accrual
        return pv
