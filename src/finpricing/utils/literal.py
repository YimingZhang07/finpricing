from enum import Enum


class Literal(Enum):
    """Literal constants"""
    ONE_BASIS_POINT = 0.0001
    ONE_PERCENT     = 0.01
    ZERO            = 0
    UNIT            = 1
    ONE_HUNDRED     = 100
    ONE_THOUSAND    = 1000
    ONE_MILLION     = 1000_000
    ONE_BILLION     = 1000_000_000
