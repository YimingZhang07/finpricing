from ..utils.interpolator import InterpTypes, Interpolator
from ..utils.day_count import DayCountTypes, DayCount
from ..utils.date import Date
import numpy as np

class DiscountCurve:
    def __init__(self) -> None:
        pass  
    
    def factor(date: Date):
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