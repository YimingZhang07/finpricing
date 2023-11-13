# from ..utils.interpolator import DummyInterpolator
import math
from ...utils.day_count import DayCountTypes
from .curve import BaseCurve
from ...utils.date import Date
from ...utils.frequency import FrequencyTypes


class DummyCurve(BaseCurve):
    """Dummy curve class

    This is a simple discount curve with a constant rate. The frequency type decides the compounding frequency.
    """

    def __init__(self,
                 rate: float = 0.0,
                 valuation_date: Date = None,
                 day_count_type: DayCountTypes = DayCountTypes.ACT_ACT_ISDA,
                 freq_type: FrequencyTypes = FrequencyTypes.CONTINUOUS) -> None:
        """
        Args:
            rate (float): constant rate
            valuation_date (Date): valuation date
            day_count_type (DayCountTypes): day count convention
            freq_type (FrequencyTypes): frequency type
        """
        super().__init__(valuation_date, day_count_type)
        self._rate = rate
        self._freq_type = freq_type

    def eval(self, t: float) -> float:
        if self._freq_type == FrequencyTypes.CONTINUOUS:
            return math.exp(-self._rate * t)
        else:
            return 1 / math.pow(1 + self._rate / self._freq_type.value, self._freq_type.value * t)

    def eval_by_date(self, date: Date) -> float:
        """Evaluate discount factor at date.

        DEPRECATED: use df() instead.
        
        Args:
            date (Date): date
        
        Returns:
            float: discount factor
        """
        return self.df(date)

    def to_tuple(self) -> tuple:
        """Convert object attributes to a tuple"""
        return (self._rate, self._valuation_date, self._day_count_type, self._freq_type)
    
    def __repr__(self) -> str:
        return f"DummyCurve({self._rate})"

    def __hash__(self) -> int:
        return hash(self.to_tuple())
