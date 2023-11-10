import datetime
from typing import Union
from ..utils import ClassUtil, Date, DayCount
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
    
    def _generate_fixed_payments(self,
                                coupon_leg: CDSFixedCouponLeg):
        """generate customized fixed payments for a cds fixed coupon leg
        
        NOTE    this is not a general purpose function, and should be considered as a workaround.
                The last accrual period of a CDS has an additional day added to the accrual end date.
        """
        if isinstance(coupon_leg, CDSFixedCouponLeg) is False:
            raise TypeError("coupon_leg must be a CDSFixedCouponLeg object")
        accrual_start = coupon_leg.accrual_start
        accrual_end = coupon_leg.accrual_end.copy()
        payment_dates = accrual_end.copy()
        accrual_end[-1] = accrual_end[-1].add_tenor("1d")
        day_counter = DayCount(coupon_leg.day_count_type)
        cashflows = []
        for s, e, p in zip(accrual_start, accrual_end, payment_dates):
            fraction = day_counter.days_between(s, e)[1]
            amount = coupon_leg.coupon_rate * fraction * coupon_leg.notional
            cashflows.append((p, amount))
        return accrual_start, accrual_end, cashflows
        
    
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
        
        accrual_start, accrual_end, coupon_cashflows = \
            self._generate_fixed_payments(self.fixed_coupon_leg)
            
        """
        NOTE    date is the payment date, for which the discount factor refers to
                accrual_end_date is the date for which the survival probability refers to and has an additional day\
                    as adjusted above
                amount is also determined by the accrual period, so impacted by the last accrual adjustment
        """
        
        for i, item in enumerate(coupon_cashflows):
            date = item[0]
            amount = item[1]
            accrual_start_date = accrual_start[i].add_tenor("-1d")
            accrual_end_date = accrual_end[i].add_tenor("-1d")

            if date > valuation_date:
                df = discount_curve.discount(date)
                discounted_amount = df * survival_curve.survival(accrual_end_date) * amount
                
                # NOTE the recovery rate is set to be 1.0 as a convention
                accrual = amount * accrual_integral(
                    granularity_in_days=14,
                    R=1.,
                    survival_curve=survival_curve,
                    discount_curve=discount_curve,
                    accrual_start_date=accrual_start_date,
                    accrual_end_date=accrual_end_date
                )
                pv = pv + discounted_amount + accrual
        return pv
