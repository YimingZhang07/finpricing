import math
import datetime
from bisect import bisect_left
from typing import Union, List
from ..utils import ClassUtil, Date, DayCount
from ..instrument.cds import CDSFixedCouponLeg, CDSContingentLeg, CreditDefaultSwap
from ..model.utils.bond_pricing_utils import accrual_integral
from ..market.lgd_curve import LGDCurve

class CDSPricer(ClassUtil):
    def __init__(self,
                 fixed_coupon_leg: CDSFixedCouponLeg,
                 contingent_leg: CDSContingentLeg,
                 discount_curve,
                 survival_curve,
                 recovery_rate,
                 granularity: int=14,
                 include_accrued: bool=True) -> None:
        self.save_attributes()
    
    @classmethod
    def from_cds(cls,
                 cds: CreditDefaultSwap,
                 discount_curve,
                 survival_curve,
                 recovery_rate,
                 granularity: int=14,
                 include_accrued: bool=True):
        return cls(
            fixed_coupon_leg=cds.fixed_coupon_leg,
            contingent_leg=cds.contingent_leg,
            discount_curve=discount_curve,
            survival_curve=survival_curve,
            recovery_rate=recovery_rate,
            granularity=granularity,
            include_accrued=include_accrued
        )
    
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
              discount_curve = None,) -> float:
        """calculate the present value of a coupon leg
        
        NOTE the recovery rate seems to be not needed in this function, maybe because the CDS will pay the full notional
                
        Returns:
            Dirty price of coupon leg.
        """
        discount_curve = self.first_valid(discount_curve, self.discount_curve)
        survival_curve = self.first_valid(survival_curve, self.survival_curve)
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
                    granularity_in_days=self.granularity,
                    R=1.,
                    survival_curve=survival_curve,
                    discount_curve=discount_curve,
                    accrual_start_date=accrual_start_date,
                    accrual_end_date=accrual_end_date
                )
                pv = pv + discounted_amount + accrual
        return pv
    
    def pv_contingent_leg_unit_notional(self,
                                        discount_curve,
                                        survival_curve,
                                        lgd_curve: LGDCurve,
                                        start_date: Union[datetime.date, Date],
                                        end_date: Union[datetime.date, Date],
                                        granularity: int,
                                        special_dates: List,
                                        is_first_period: bool):
        maturity_date = max(end_date, discount_curve.anchor_date)
        partition_start = start_date if is_first_period else start_date.add_tenor("-1d")
        partition_start = max(partition_start, discount_curve.anchor_date)
        
        prev_factor = discount_curve.discount(partition_start)
        prev_prob = survival_curve.survival(partition_start)
        prev_lgd = lgd_curve.loss(partition_start)
        
        PV = 0.0
        
        idx_special_date = bisect_left(special_dates, partition_start) - 1
        special_date = special_dates[idx_special_date]
        
        while partition_start < maturity_date:
            partition_end = min(partition_start.add_days(granularity), maturity_date)
            
            if special_date != special_dates[-1] and special_date <= partition_end:
                partition_end = special_date
                idx_special_date += 1
                special_date = special_dates[idx_special_date]
            
            next_prob = survival_curve.survival(partition_end)
            next_factor = discount_curve.discount(partition_end)
            next_lgd = lgd_curve.loss(partition_end)
            log_prob = math.log(prev_prob / next_prob)
            log_factor = math.log(prev_factor / next_factor)
            lgd_used = (prev_lgd + next_lgd) / 2
            
            if (log_prob + log_factor) < 1e-9:
                # linear approximation
                PV += lgd_used * prev_prob * prev_factor * log_prob * (1 + 0.5 * (log_prob + log_factor))
            else:
                PV += lgd_used * (prev_prob * prev_factor - next_prob * next_factor) * log_prob / (log_prob + log_factor)
            
            prev_factor = next_factor
            prev_prob = next_prob
            prev_lgd = next_lgd
            partition_start = partition_end
        return PV
    
    def pv_contingent_leg(self,
                          valuation_date: Union[datetime.date, Date] = None,
                          discount_curve = None,
                          survival_curve = None,
                          recovery_rate = None,):
        
        discount_curve = self.first_valid(discount_curve, self.discount_curve)
        survival_curve = self.first_valid(survival_curve, self.survival_curve)
        recovery_rate = self.first_valid(recovery_rate, self.recovery_rate)
        valuation_date = self.first_valid(valuation_date, discount_curve.anchor_date)
        
        valuation_date = Date.convert_from_datetime(valuation_date)
        
        lgd_curve = LGDCurve(recovery_rate=recovery_rate)

        start_date = self.contingent_leg.protection_start_date
        end_date = self.contingent_leg.protection_end_date
        PV = 0.0
        
        if self.contingent_leg.pay_at_end:
            raise NotImplementedError("pay_at_end is not implemented")
        else:
            special_dates = self.fixed_coupon_leg.accrual_end
            PV = self.pv_contingent_leg_unit_notional(
                discount_curve=discount_curve,
                survival_curve=survival_curve,
                lgd_curve=lgd_curve,
                start_date=start_date,
                end_date=end_date,
                granularity=self.granularity,
                special_dates=special_dates,
                is_first_period=True
            )
            
            PV = PV * self.contingent_leg.notional
            
        return PV
    
    def par_spread(self):
        return -self.pv_contingent_leg / self.pv_coupon_leg