from finpricing.utils.payment_schedule import PaymentSchedule
from finpricing.utils.calendar import CalendarTypes, DateGenRuleTypes
from finpricing.utils.date import Date
from finpricing.utils.bus_day_adj import BusDayAdjustTypes
from finpricing.utils.frequency import FrequencyTypes


def test_fixed_leg():
    """
    Example from: https://github.com/domokane/FinancePy/blob/master/notebooks/products/rates/FINIBORSWAP_ComparisonWithQLExample.ipynb
    """
    ps = PaymentSchedule(Date(2015, 10, 27),
                         "10Y",
                         freq_type=FrequencyTypes.SEMI_ANNUAL,
                         calendar_type=CalendarTypes.UNITED_STATES,
                         bus_day_adj_type=BusDayAdjustTypes.MODIFIED_FOLLOWING,
                         date_gen_rule_type=DateGenRuleTypes.FORWARD)

    assert ps.payment_dates == [Date(2016, 4, 27), Date(2016, 10, 27), Date(2017, 4, 27), Date(2017, 10, 27),
                                Date(2018, 4, 27), Date(2018, 10, 29), Date(2019, 4, 29), Date(2019, 10, 28),
                                Date(2020, 4, 27), Date(2020, 10, 27), Date(2021, 4, 27), Date(2021, 10, 27),
                                Date(2022, 4, 27), Date(2022, 10, 27), Date(2023, 4, 27), Date(2023, 10, 27),
                                Date(2024, 4, 29), Date(2024, 10, 28), Date(2025, 4, 28), Date(2025, 10, 27)]
