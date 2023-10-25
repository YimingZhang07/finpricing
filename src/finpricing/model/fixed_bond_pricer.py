import datetime
from typing import Union
from ..utils import *
from ..instrument.fixed_bond import FixedBond
from .utils.bond_pricing_utils import principal_integral, accrual_integral

class FixedBondPricer(ClassUtil):
    def __init__(self, inst: FixedBond) -> None:
        self.inst = inst
        
    @property
    def principal_amount(self):
        return self.inst.principal_leg.principal_amount
    
    @property
    def coupon_cashflows(self):
        return self.inst.fixed_coupon_leg.cashflows
    
    def principal_pv(self, valuation_date, recovery_rate, discount_curve, survival_curve):
        # principal leg value 
        principal_date = self.inst.principal_leg.maturity_date
        principal_amount = self.principal_amount
        
        df = discount_curve.discount(principal_date)
        q  = survival_curve.survival(principal_date)
        
        principal_contingent = principal_integral(
            N=principal_amount,
            R=recovery_rate,
            valuation_date=valuation_date,
            maturity_date=principal_date,
            granularity_in_days=14,
            survival_curve=survival_curve,
            discount_curve=discount_curve,
        )
        
        return df * q * principal_amount + principal_contingent
        
    def Price(self,
              valuation_date: Union[datetime.date, Date],
              survival_curve,
              discount_curve,
              recovery_rate: float = 0.4) -> float:
        """risky discounting of a fixed bond"""
        valuation_date = Date.convert_from_datetime(valuation_date)
        
        pv = 0.0
        prev_date = valuation_date
        
        for date, amount in self.coupon_cashflows:
            if date > valuation_date:
                df = discount_curve.discount(date)
                
                # here the survival date is moved 1 day back as convention for the non-integral part
                pv += df * survival_curve.survival(date.add_tenor("-1d")) * amount
                
                pv += amount * accrual_integral(
                    start_date=prev_date,
                    end_date=date,
                    granularity_in_days=14,
                    R=recovery_rate,
                    survival_curve=survival_curve,
                    discount_curve=discount_curve,
                )
            prev_date = date
            
        pv += self.principal_pv(valuation_date, recovery_rate, discount_curve, survival_curve)
        
        return pv