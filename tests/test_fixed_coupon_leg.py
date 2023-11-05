from finpricing.instrument.fixed_coupon_leg import FixedCouponLeg
import finpricing.utils as utils
import datetime


def test_cashflows():
    inst = FixedCouponLeg(
        datetime.date(2023, 10, 9),
        maturity_date_or_tenor=datetime.date(2028, 11, 15),
        coupon_rate=0.05875,
        freq_type=utils.FrequencyTypes.SEMI_ANNUAL,
        day_count_type=utils.DayCountTypes.THIRTY_360,
        bus_day_adj_type=utils.BusDayAdjustTypes.NONE,
        date_gen_rule_type=utils.DateGenRuleTypes.BACKWARD,
    )

    inst.print_cashflows()
    
def test_classmethod_from_cashflows():
    inst = FixedCouponLeg.from_cashflows(
        coupon_rate=0.05875,
        accrual_start=[datetime.date(2023, 4, 15),
                       datetime.date(2023, 10, 15),
                       datetime.date(2024, 4, 15),
                       datetime.date(2024, 10, 15),],
        accrual_end=[datetime.date(2023, 10, 15),
                     datetime.date(2024, 4, 15),
                     datetime.date(2024, 10, 15),
                     datetime.date(2025, 2, 15),],
        payment_dates=[datetime.date(2023, 10, 15),
                       datetime.date(2024, 4, 15),
                       datetime.date(2024, 10, 15),
                       datetime.date(2025, 2, 15),],
        notional=100.
    )
    inst.print_cashflows()


if __name__ == "__main__":
    test_classmethod_from_cashflows()
