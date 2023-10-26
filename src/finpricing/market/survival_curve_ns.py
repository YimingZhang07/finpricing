from ..utils.date import Date
import datetime
import math
import scipy
import numpy as np
from typing import Union

class SurvivalCurve:
    def __init__(self, anchor_date) -> None:
        self.anchor_date = anchor_date
        
    def survival(self, date: Union[Date, datetime.date]):
        return NotImplementedError("Please implement survival() method in derived class")
    
    
class SurvivalCurveNelsonSiegel(SurvivalCurve):
    def __init__(self,
                 anchor_date: Union[Date, datetime.date],
                 pivot_dates: list[Union[Date, datetime.date]],
                 params: list[float]) -> None:
        anchor_date = Date.convert_from_datetime(anchor_date)
        super().__init__(anchor_date)
        self.pivot_dates = Date.convert_from_datetimes(pivot_dates)
        self.params = params
        
        # derived attributes
        self.pivots = [ date - anchor_date for date in self.pivot_dates ]
        
    @staticmethod
    def f(t, a):
        threshold = 1e-1
        if t < threshold:
            return 1.0 / a - t / ( 2 * a ** 2 ) + t ** 2 / ( 6 * a ** 3 )
        else:
            return ( 1.0 - math.exp( -t / a ) ) / t
        
    @staticmethod
    def f_integral(t, a):
        return math.log( t / a ) + scipy.special.exp1( t / a ) + np.euler_gamma
    
    def hazard_rates(self, t: float) -> float:
        return self.params[0] + sum(param * self.f(t, pivot) for param, pivot in zip(self.params[1:], self.pivots))
    
    def survival(self, date: Union[Date, datetime.date]):
        date = Date.convert_from_datetime(date)
        tenor = date - self.anchor_date
        
        if tenor == 0:
            return 1.0
        
        integral = self.params[0] * tenor
        for i, p in enumerate(self.pivots):
            integral += self.params[i + 1] * self.f_integral(tenor, p)
            
        return math.exp(-integral)