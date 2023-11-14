import datetime
from typing import List, Union
from ..utils import Date, CDSStyle


class CDSCurve:
    def __init__(self,
                 market_date: Union[datetime.date, Date],
                 expiries: List[Union[datetime.date, Date]],
                 spreads: List[float],
                 upfronts: List[float],
                 cds_style: Union[CDSStyle, str],):
        self.market_date = Date.convert_from_datetime(market_date)
        self.expiries = Date.convert_from_datetimes(expiries)
        self.spreads = spreads
        self.upfronts = upfronts
        self.cds_style = CDSStyle(cds_style)
