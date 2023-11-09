from enum import Enum
from finpricing.utils import (
    TimeInterval,
    FrequencyTypes,
    BusDayAdjustTypes,
    ClassUtil,
    CalendarTypes,
    DayCountTypes
)


class CDSStubType(Enum):
    NO_STUB = "NO_STUB"


class CDSEffectiveDateStyle(Enum):
    PCD = "PCD"


class CDSTermStyle(Enum):
    IMM_CORPORATE = "IMM_CORPORATE"

class CDSStyle(ClassUtil):
    def __init__(
        self,
        name,
        day_count_type,
        frequency_type,
        bus_day_adj_type,
        cds_term_style,
        cds_effective_date_style,
        cds_stub_length,
        minimal_stub_period: int,
        eom_adj: bool,
        calendar_type
    ):
        self.save_attributes()

    @classmethod
    def CORP_NA(cls):
        return cls(
            name="CORP_NA",
            day_count_type=DayCountTypes.ACT_360,
            frequency_type=FrequencyTypes.QUARTERLY,
            bus_day_adj_type=BusDayAdjustTypes.FOLLOWING,
            cds_term_style=CDSTermStyle.IMM_CORPORATE,
            cds_effective_date_style=CDSEffectiveDateStyle.PCD,
            cds_stub_length=CDSStubType.NO_STUB,
            minimal_stub_period=TimeInterval(0, "d"),
            eom_adj=True,
            calendar_type=CalendarTypes.WEEKEND,
        )
        
    @classmethod
    def from_name(cls, name):
        """Return a CDSStyle instance from a string of name"""
        # if the name is already a CDSStyle instance, return it
        if isinstance(name, cls):
            return name
        if name == "CORP_NA":
            return cls.CORP_NA()
        else:
            raise ValueError(f"Unknown CDSStyle name: {name}")
