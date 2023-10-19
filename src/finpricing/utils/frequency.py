from enum import Enum


class FrequencyTypes(Enum):
    ANNUAL = 1
    SEMI_ANNUAL = 2
    QUARTERLY = 4
    MONTHLY = 12
    CONTINUOUS = 99
