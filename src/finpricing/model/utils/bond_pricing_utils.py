from ...utils import *
import datetime
from typing import Union
import math

MINIMUM_DENOMINATOR = 1e-12


def hazard_rate_from_probs(
    start_p, end_p, start_date, end_date, day_count_type=DayCountTypes.ACT_ACT_ISDA
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


# def ir_from_discount_factors(
#     start_B, end_B, start_date, end_date, day_count_type=DayCountTypes.ACT_ACT_ISDA
# ):
#     day_counter = DayCount(day_count_type)
#     delta_time = day_counter.year_fraction(start_date, end_date)
#     return (1 / delta_time) * math.log(start_B / end_B)


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

    Args:
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
    survival_curve,
    discount_curve,
    accrual_start_date,
    accrual_end_date,
    granularity_in_days,
    R,
    day_count_type=DayCountTypes.ACT_ACT_ISDA
):
    """calculate the accrual of a coupon leg
    
    Args:
        start_date: start date of the calculation period
        granularity_in_days: granularity of the partition in days
        R: recovery rate
        survival_curve: survival curve
        discount_curve: discount curve
        accrual_start_date: accrual start date, the lower bound of the integral
        accrual_end_date: accrual end date, the upper bound of the integral
        
    Returns:
        The accrual value
    """
    # start_date = Date.convert_from_datetime(start_date)
    accrual_start_date = Date.convert_from_datetime(accrual_start_date)
    accrual_end_date = Date.convert_from_datetime(accrual_end_date)
    day_counter = DayCount(day_count_type)
    
    partition = []
    current_date = max(accrual_start_date, discount_curve.anchor_date)
    prev_factor = discount_curve.discount(current_date)
    prev_prob = survival_curve.survival(current_date)
    
    while current_date <= accrual_end_date:
        partition.append(current_date)
        current_date = current_date.add_days(granularity_in_days)
        
    if partition[-1] != accrual_end_date:
        partition.append(accrual_end_date)
        
    G = len(partition) - 1  # number of intervals in the partition
    sum_accrual = 0.
    
    for g in range(1, G + 1):
        partition_start = partition[g - 1]
        partition_end = partition[g]
        partition_length = day_counter.days_between(partition_start, partition_end)[0]
        next_factor = discount_curve.discount(partition_end)
        next_prob = survival_curve.survival(partition_end)
        
        h = math.log(prev_prob / next_prob) / partition_length
        r = math.log(prev_factor / next_factor) / partition_length
        h_over_r_plus_h = h / (r + h + MINIMUM_DENOMINATOR)
        h_over_r_plus_h_squared = h_over_r_plus_h / (r + h + MINIMUM_DENOMINATOR)
        
        prev_prob_factor = prev_prob * prev_factor
        next_prob_factor = next_prob * next_factor
        prob_factor_diff = prev_prob_factor - next_prob_factor
        
        term1 = prob_factor_diff * (h_over_r_plus_h * 0.5 + h_over_r_plus_h_squared)
        term2 = h_over_r_plus_h * (prev_prob_factor * day_counter.days_between(accrual_start_date, partition_start)[0] - \
                                   next_prob_factor * day_counter.days_between(accrual_start_date, partition_end)[0])
        integral_value = term1 + term2
        sum_accrual += R * integral_value
        
        prev_factor = next_factor
        prev_prob = next_prob

    return sum_accrual / day_counter.days_between(accrual_start_date, accrual_end_date)[0]