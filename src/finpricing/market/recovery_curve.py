import datetime
from typing import Union
from finpricing.utils.date import Date


class RecoveryCurve:
    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], float):
            return RecoveryCurveConstant(args[0])
        else:
            raise TypeError("Invalid RecoveryCurve initialization")
    
class RecoveryCurveConstant:
    def __init__(self, recovery_rate: float):
        self.recovery_rate = recovery_rate
    
    @classmethod
    def from_recovery_rate(cls, recovery_rate: float):
        return cls(recovery_rate)
    
    def loss(self, date: Union[Date, datetime.date]):
        return self.recovery_rate
