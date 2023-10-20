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


if __name__ == "__main__":
    test_cashflows()
