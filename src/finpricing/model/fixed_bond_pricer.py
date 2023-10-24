from ..utils import *
from ..instrument.fixed_bond import FixedBond
import datetime
from typing import Union

class FixedBondPricer(ClassUtil):
    def __init__(self, inst: FixedBond) -> None:
        self.inst = inst
        
    def Price(self,
              valuation_date: Union[datetime.date, Date],
              survival_curve,
              discount_curve,
              recovery_rate: float = 0.4) -> float:
        
        valuation_date = Date.convert_from_datetime(valuation_date)
        
        pv = 0.0
        prev_q = 1.0
        
        for date, amount in self.inst.fixed_coupon_leg.cashflows:
            if date > valuation_date:
                df = discount_curve.discount(date)
                q  = survival_curve.survival(date)
                
                pv += df * q * amount
                dq = q - prev_q
                
                pv += 0.5 * dq * self.inst.principal_leg.amount * (prev_q + q) * recovery_rate
                
                prev_q = q
                
        principal_date = self.inst.principal_leg.date
        principal_amount = self.inst.principal_leg.amount
        df = discount_curve.discount(principal_date)
        q  = survival_curve.survival(principal_date)
        pv += df * q * principal_amount
        
        return pv