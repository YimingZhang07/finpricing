from enum import Enum
from finpricing.utils import TimeInterval, FrequencyTypes, BusDayAdjustTypes, ClassUtil


class CDSStubType(Enum):
    NO_STUB = "NO_STUB"

class CDSEffectiveDateStyle(Enum):
    PCD = "PCD"

class CDSTermStyle(Enum):
    IMM_CORPORATE = "IMM_CORPORATE"

class CDSStyle(ClassUtil):
    def __init__(self,
                 name,
                 frequency_type,
                 bus_day_adj_type,
                 cds_term_style,
                 cds_effective_date_style,
                 cds_stub_length,
                 minimal_stub_period: int,
                 eom_adj: bool
    ):
        self.save_attributes()
        

    @classmethod
    def CORP_NA(cls):
        return cls(
            name = "CORP_NA",
            frequency_type = FrequencyTypes.QUARTERLY,
            bus_day_adj_type = BusDayAdjustTypes.FOLLOWING,
            cds_term_style = CDSTermStyle.IMM_CORPORATE,
            cds_effective_date_style = CDSEffectiveDateStyle.PCD,
            cds_stub_length = CDSStubType.NO_STUB,
            minimal_stub_period = TimeInterval(0, "d"),
            eom_adj = True
        )