import datetime
from ..utils import Date
from typing import List, Union
import math

class SurvivalCurveStep:
    def __init__(self,
                 anchor_date: Union[Date, datetime.date],
                 dates: List[Union[Date, datetime.date]],
                 hazard_rates: List[float]):
        if len(dates) != len(hazard_rates):
            raise ValueError("Dates and hazard rates lists must have the same length")

        self.anchor_date = Date.convert_from_datetime(anchor_date)
        self.dates = Date.convert_from_datetimes(dates)
        self.hazard_rates = hazard_rates

    def survival(self, date: Union[datetime.date, Date]) -> float:
        date = Date.convert_from_datetime(date)

        if date < self.anchor_date:
            raise ValueError("Target date should be on or after the anchor date")

        # If target date is the same as the anchor date, return 1
        if date == self.anchor_date:
            return 1

        survival_probability = 1
        prev_date = self.anchor_date

        for i, curr_date in enumerate(self.dates):
            # If the target date falls within this interval
            if prev_date <= date < curr_date:
                days_in_interval = date - prev_date
                survival_probability *= math.exp(-self.hazard_rates[i] * days_in_interval)
                return survival_probability

            # Calculate for the whole interval
            days_in_interval = curr_date - prev_date
            survival_probability *= math.exp(-self.hazard_rates[i] * days_in_interval)
            prev_date = curr_date

        # If the target date is beyond the last date in the list
        days = date - prev_date
        survival_probability *= math.exp(-self.hazard_rates[-1] * days)

        return survival_probability
