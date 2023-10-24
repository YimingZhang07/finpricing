from ..utils import *
from typing import Union

class PrincipalLeg(ClassUtil):
    def __init__(self,
                 date: Union[datetime.date, Date],
                 amount: float):
        self.date = Date.convert_from_datetime(date)
        self.amount = amount