import numpy as np
from typing import Union
import datetime
from ..utils.interpolator import InterpTypes, Interpolator
from ..utils.day_count import DayCountTypes, DayCount
from ..utils.date import Date

class DiscountCurve:
    def __init__(self) -> None:
        pass  
    
    def discount(date: Date):
        return NotImplementedError("Please implement factor() method in derived class")
    
    
class DiscountCurveZeroRates(DiscountCurve):
    
    def __init__(self,
                 anchor_date = None,
                 dates: list[float] = None,
                 rates: list[float] = None,
                 interp_type = InterpTypes.FLAT_FWD_RATES,
                 day_count_type: DayCountTypes = DayCountTypes.ACT_365) -> None:
        self.anchor_date = anchor_date
        self.dates = dates
        self.rates = rates
        self.interp_type = interp_type
        self.day_count_type = day_count_type
        
        # derived
        self.day_counter    = DayCount(self.day_count_type)
        self.times          = self.day_counter.convert_dates_to_times(self.anchor_date, self.dates)
        self.factors        = np.exp( -np.multiply(self.times, self.rates) ).tolist()
        self.interpolator   = Interpolator([0.] + self.times, [1.] + self.factors, self.interp_type)
        
        
    def discount(self, date: Date):
        dt                  = self.day_counter.year_frac(self.anchor_date, date)
        return self.interpolator.eval(dt)
    

class DiscountCurveZeroShifted:
    def __init__(self,
                 underlying_curve: DiscountCurveZeroRates,
                 alpha: float,
                 beta: float=1.0,
                 day_count_type: DayCountTypes=DayCountTypes.ACT_365) -> None:
        self.underlying_curve = underlying_curve
        self.alpha = alpha
        self.beta = beta
        self.day_count_type = day_count_type
        # derived
        self.day_counter    = DayCount(self.day_count_type)
        assert self.day_count_type == self.underlying_curve.day_count_type, "DiscountCurveZeroShifted: day_count_type must be the same as underlying_curve.day_count_type"
        
    def discount(self, date: Union[Date, datetime.date]):
        factor = self.underlying_curve.discount(date)
        time   = self.day_counter.year_fraction(self.underlying_curve.anchor_date, date)
        factor_adjusted = np.power(factor, self.beta) * np.exp(-self.alpha * time)
        return factor_adjusted
        