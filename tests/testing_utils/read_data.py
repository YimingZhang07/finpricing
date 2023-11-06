import datetime
import finpricing.utils as utils
from finpricing.instrument.fixed_coupon_leg import FixedCouponLeg
from finpricing.instrument.fixed_bond import FixedBond
from finpricing.instrument.principal_leg import PrincipalLeg

def parse_bond_info(valuation_date, bonds_info_dict):
    bonds = []
    dirty_prices = []
    for bond in bonds_info_dict:
        if bond == "bond3":
            fixed_coupon_leg = FixedCouponLeg.from_cashflows(
                coupon_rate=float(bonds_info_dict[bond]["CouponRate"]) / 100,
                accrual_start=[
                    datetime.date(2023, 4, 15),
                    datetime.date(2023, 10, 15),
                    datetime.date(2024, 4, 15),
                    datetime.date(2024, 10, 15),
                ],
                accrual_end=[
                    datetime.date(2023, 10, 15),
                    datetime.date(2024, 4, 15),
                    datetime.date(2024, 10, 15),
                    datetime.date(2025, 2, 15),
                ],
                payment_dates=[
                    datetime.date(2023, 10, 15),
                    datetime.date(2024, 4, 15),
                    datetime.date(2024, 10, 15),
                    datetime.date(2025, 2, 15),
                ]
            )
        elif bond == "bond2":
            tmp_dates = [
                datetime.date(2023, 6, 15),
                datetime.date(2023, 12, 15),
                datetime.date(2024, 6, 15),
                datetime.date(2024, 12, 15),
                datetime.date(2025, 6, 15),
                datetime.date(2025, 12, 15),
                datetime.date(2026, 6, 15),
                datetime.date(2026, 12, 15),
                datetime.date(2027, 6, 15),
                datetime.date(2027, 12, 15),
                datetime.date(2028, 6, 15),
                datetime.date(2028, 12, 15),
                datetime.date(2029, 6, 15),
                datetime.date(2029, 11, 15),
            ]
            fixed_coupon_leg = FixedCouponLeg.from_cashflows(
                coupon_rate=float(bonds_info_dict[bond]["CouponRate"]) / 100,
                accrual_start=tmp_dates[:-1],
                accrual_end=tmp_dates[1:],
                payment_dates=tmp_dates[1:]
            )
        else:
            fixed_coupon_leg = FixedCouponLeg(
                start_date=valuation_date,
                maturity_date_or_tenor=datetime.date.fromisoformat(
                    bonds_info_dict[bond]["MaturityDate"]
                ),
                coupon_rate=float(bonds_info_dict[bond]["CouponRate"]) / 100,
                freq_type=utils.FrequencyTypes.SEMI_ANNUAL,
                day_count_type=utils.DayCountTypes.THIRTY_360,
                bus_day_adj_type=utils.BusDayAdjustTypes.NONE,
                date_gen_rule_type=utils.DateGenRuleTypes.BACKWARD,
            )
        principal_leg = PrincipalLeg(
            maturity_date=datetime.date.fromisoformat(
                bonds_info_dict[bond]["MaturityDate"]
            ),
            principal_amount=100.0,
        )
        bond_inst = FixedBond(
            fixed_coupon_leg=fixed_coupon_leg, principal_leg=principal_leg
        )
        bonds.append(bond_inst)
        dirty_prices.append(float(bonds_info_dict[bond]["DirtyPrice"]))
    return bonds, dirty_prices