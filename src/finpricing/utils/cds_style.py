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
    
class CDSAccruedStyle(Enum):
    SNAC = "SNAC"  # use standard North American CDS accrual convention, T+1
    CONVENTIONAL = "CONVENTIONAL"  # use conventional CDS accrual convention, T

class CDSStyle(ClassUtil):
    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], str):
            return cls.from_name(args[0])
        elif len(args) == 1 and isinstance(args[0], CDSStyleBase):
            return args[0]
        else:
            raise TypeError("Invalid CDSStyle initialization")
        
    def __init__(self) -> None:
        pass
    
    @classmethod
    def from_name(cls, name):
        """Return a CDSStyle instance from a string of name"""
        # if the name is already a CDSStyle instance, return it
        if name == "CORP_NA":
            return CDSStyleCorpNA()
        else:
            raise ValueError(f"Unknown CDSStyle name: {name}")
        
    @classmethod
    def CORP_NA(cls):
        return CDSStyleCorpNA()

class CDSStyleBase(ClassUtil):
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
        calendar_type,
        accrued_style
    ):
        self.save_attributes()
        
class CDSStyleCorpNA(CDSStyleBase):
    def __init__(self):
        super().__init__(
            name="CORP_NA",
            day_count_type=DayCountTypes.ACT_360,
            frequency_type=FrequencyTypes.QUARTERLY,
            bus_day_adj_type=BusDayAdjustTypes.FOLLOWING,
            cds_term_style=CDSTermStyle.IMM_CORPORATE,
            cds_effective_date_style=CDSEffectiveDateStyle.PCD,
            cds_stub_length=CDSStubType.NO_STUB,
            minimal_stub_period=TimeInterval(0, "d"),
            eom_adj=True,
            # calendar_type controls the holidays
            calendar_type=CalendarTypes.WEEKEND,
            # this is additional parameter I make for simplicity for CDSStyle
            accrued_style=CDSAccruedStyle.SNAC
        )
