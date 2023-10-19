from enum import Enum

# Reference: https://jollycontrarian.com/index.php?title=Business_Day_Convention_-_ISDA_Definition


class BusDayAdjustTypes(Enum):
    NONE = 1
    FOLLOWING = 2
    MODIFIED_FOLLOWING = 3
    PREVIOUS = 4
    MODIFIED_PREVIOUS = 5
