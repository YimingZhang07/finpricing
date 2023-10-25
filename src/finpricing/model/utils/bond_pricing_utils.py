from ...utils import *
import datetime
from typing import Union
import math

MINIMUM_DENOMINATOR = 1e-10


def hazard_rate_from_probs(
    start_p, end_p, start_date, end_date, day_count_type=DayCountTypes.ACT_365
):
    """
    Calculate the constant hazard rate given the survival probabilities at two time points.

    Args:
        start_p: Survival probability at start date
        end_p: Survival probability at end date
        start_date: Start date.
        end_date: End date.

    Returns:
        The hazard rate.
    """
    day_counter = DayCount(day_count_type)
    delta_time = day_counter.year_fraction(start_date, end_date)
    return (1 / delta_time) * math.log(start_p / end_p)


def ir_from_discount_factors(
    start_B, end_B, start_date, end_date, day_count_type=DayCountTypes.ACT_365
):
    day_counter = DayCount(day_count_type)
    delta_time = day_counter.year_fraction(start_date, end_date)
    return (1 / delta_time) * math.log(start_B / end_B)


def principal_integral(
    N,
    R,
    valuation_date: Union[datetime.date, Date],
    maturity_date: Union[datetime.date, Date],
    granularity_in_days: int,
    survival_curve,
    discount_curve,
):
    """
    Calculate the principal integral.

    Parameters:
        N: Total notional.
        R: Recovery rate.
        end_date: End date.
        granularity_in_days: The granularity parameter in days.
        survival_curve: Function that returns the survival probability at a given date.
        discount_curve: Function that returns the bond price at a given date.

    Returns:
        The principal integral value.
    """
    # Create the partition based on end_date and granularity_in_days

    valuation_date = Date.convert_from_datetime(valuation_date)
    maturity_date = Date.convert_from_datetime(maturity_date)

    partition = []
    current_date = valuation_date
    while current_date <= maturity_date:
        partition.append(current_date)
        current_date = current_date.add_days(granularity_in_days)

    if partition[-1] != maturity_date:
        partition.append(maturity_date)

    G = len(partition) - 1  # number of intervals in the partition
    sum_PV = 0

    for g in range(1, G + 1):
        tau_g_minus_1 = partition[g - 1]
        tau_g = partition[g]

        log_ratio_p = math.log(
            survival_curve.survival(tau_g_minus_1) / survival_curve.survival(tau_g)
        )
        log_ratio_B = math.log(
            discount_curve.discount(tau_g_minus_1) / discount_curve.discount(tau_g)
        )

        coefficient = log_ratio_p / (log_ratio_p + log_ratio_B + MINIMUM_DENOMINATOR)
        sum_PV += coefficient * (
            survival_curve.survival(tau_g_minus_1)
            * discount_curve.discount(tau_g_minus_1)
            - survival_curve.survival(tau_g) * discount_curve.discount(tau_g)
        )

    return N * R * sum_PV


def accrual_integral(
    start_date, end_date, granularity_in_days, R, survival_curve, discount_curve, day_count_type=DayCountTypes.ACT_365
):
    """
    Calculate the accrual integral.

    Parameters:
        start_date: Start date of the interval.
        end_date: End date of the interval.
        granularity_in_days: The granularity parameter in days.
        R: Recovery rate.
        survival_curve: Function that returns the survival probability at a given date.
        discount_curve: Function that returns the bond price at a given date.

    Returns:
        The accrual integral value.
    """
    start_date = Date.convert_from_datetime(start_date)
    end_date = Date.convert_from_datetime(end_date)
    day_counter = DayCount(day_count_type)

    # Create the partition based on start_date, end_date, and granularity_in_days
    partition = []
    current_date = start_date
    while current_date <= end_date:
        partition.append(current_date)
        current_date = current_date.add_days(granularity_in_days)

    if partition[-1] != end_date:
        partition.append(end_date)

    G = len(partition) - 1  # number of intervals in the partition
    sum_accrual = 0

    for g in range(1, G + 1):
        tau_g_minus_1 = partition[g - 1]
        tau_g = partition[g]

        h_tau_g = hazard_rate_from_probs(
            survival_curve.survival(tau_g_minus_1),
            survival_curve.survival(tau_g),
            tau_g_minus_1,
            tau_g,
        )
        r_tau_g = ir_from_discount_factors(
            discount_curve.discount(tau_g_minus_1),
            discount_curve.discount(tau_g),
            tau_g_minus_1,
            tau_g,
        )

        multiplier = h_tau_g / (h_tau_g + r_tau_g + MINIMUM_DENOMINATOR) ** 2

        term_1 = (
            (1 + (h_tau_g + r_tau_g) * (day_counter.year_fraction(start_date, tau_g_minus_1) + 0.5))
            * survival_curve.survival(tau_g_minus_1)
            * discount_curve.discount(tau_g_minus_1)
        )
        term_2 = (
            (1 + (h_tau_g + r_tau_g) * (day_counter.year_fraction(start_date, tau_g) + 0.5))
            * survival_curve.survival(tau_g)
            * discount_curve.discount(tau_g)
        )

        integral_value = multiplier * (term_1 - term_2)

        sum_accrual += R * integral_value

    return sum_accrual
