import datetime
from typing import Union
from ..utils import Date


class LGDCurve:
    def __init__(self, *args, **kwargs):
        if len(kwargs) == 1 and "lgd" in kwargs:
            self.curve = LGDCurveConstant(kwargs["lgd"])
        elif len(kwargs) == 1 and "recovery_rate" in kwargs:
            self.curve = LGDCurveConstant.from_recovery_rate(kwargs["recovery_rate"])
        else:
            raise TypeError("Invalid LGDCurve initialization")

    def loss(self, date: Union[Date, datetime.date]):
        return self.curve.loss(date)
    
class LGDCurveConstant:
    def __init__(self, lgd: float):
        self.lgd = lgd
    
    @classmethod
    def from_recovery_rate(cls, recovery_rate: float):
        return cls(1 - recovery_rate)
    
    def loss(self, date: Union[Date, datetime.date]):
        return self.lgd