import datetime
from ..utils import *
from typing import List, Union
import math

class SurvivalCurveStep:
    def __init__(self,
                 anchor_date: Union[Date, datetime.date],
                 dates: List[Union[Date, datetime.date]],
                 hazard_rates: List[float],
                 day_count_type = DayCountTypes.ACT_ACT_ISDA):
        if len(dates) != len(hazard_rates):
            raise ValueError("Dates and hazard rates lists must have the same length")

        self.anchor_date = Date.convert_from_datetime(anchor_date)
        self.dates = Date.convert_from_datetimes(dates)
        self.hazard_rates = hazard_rates
        self.day_count_type = day_count_type
        # derived attributes
        self.day_counter = DayCount(self.day_count_type)

    def survival(self, date: Union[datetime.date, Date]) -> float:
        date = Date.convert_from_datetime(date)

        if date < self.anchor_date:
            raise ValueError("Target date should be on or after the anchor date")

        # If target date is the same as the anchor date, return 1
        if date == self.anchor_date:
            return 1

        survival_probability = 1
        prev_date = self.anchor_date
        
        if date <= self.dates[0]:
            days_in_interval = self.day_counter.days_between(prev_date, date)[0]
            return math.exp(-self.hazard_rates[0] * days_in_interval)

        for i, curr_date in enumerate(self.dates):
            # If the target date falls within this interval
            if prev_date < date <= curr_date:
                days_in_interval = self.day_counter.days_between(prev_date, date)[0]
                survival_probability *= math.exp(-self.hazard_rates[i - 1] * days_in_interval)
                return survival_probability

            # Calculate for the whole interval
            days_in_interval = self.day_counter.days_between(prev_date, curr_date)[0]
            survival_probability *= math.exp(-self.hazard_rates[i - 1] * days_in_interval)
            prev_date = curr_date

        # If the target date is beyond the last date in the list
        days = self.day_counter.days_between(prev_date, date)[0]
        survival_probability *= math.exp(-self.hazard_rates[-1] * days)

        return survival_probability
