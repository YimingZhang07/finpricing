from ..utils import *
from typing import Union

class PrincipalLeg(ClassUtil):
    def __init__(self,
                 maturity_date: Union[datetime.date, Date],
                 principal_amount: float):
        self.maturity_date = Date.convert_from_datetime(maturity_date)
        self.principal_amount = principal_amount