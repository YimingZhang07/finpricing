import datetime
import json
import os
import pickle
import finpricing.utils as utils
from finpricing.instrument.fixed_coupon_leg import FixedCouponLeg
from finpricing.instrument.fixed_bond import FixedBond
from finpricing.instrument.principal_leg import PrincipalLeg
from finpricing.market.discount_curve_zero import DiscountCurveZeroRates
from finpricing.utils.tools import read_private_params_for_key, load_and_decrypt_data

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
project_dir = os.path.dirname(parent_dir)

def parse_bond_info(valuation_date,
                    bonds_info_dict,
                    sort_by_maturity=True,
                    include_balance=False):
    bonds = []
    dirty_prices = []
    balance = []
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
        balance.append(float(bonds_info_dict[bond]["AmountOutstanding"]))
    if sort_by_maturity:
        tmp = sorted(list(zip(bonds, dirty_prices, balance)), key = lambda x: x[0].maturity_date)
        bonds = [x[0] for x in tmp]
        dirty_prices = [x[1] for x in tmp]
        balance = [x[2] for x in tmp]
    if include_balance:
        return bonds, dirty_prices, balance
    else:
        return bonds, dirty_prices

# def get_sample_bonds_portfolio(valuation_date=datetime.date(2023, 10, 9),
#                                rel_file_path='testing_data/bondcurve_portfolio.json',
#                                **kwargs):
#     assert valuation_date == datetime.date(2023, 10, 9), "All bonds information is as of 2023-10-09."
#     file_path = os.path.join(parent_dir, rel_file_path)
#     with open(file_path, "rb") as json_data:
#         bonds_info_dict = json.load(json_data)
#         json_data.close()

#     return parse_bond_info(valuation_date, bonds_info_dict, **kwargs)

def get_sample_bonds_portfolio(valuation_date=datetime.date(2023, 10, 9),
                               rel_file_path='testing_data/bondcurve_portfolio_20231009.pkl',
                               **kwargs):
    assert valuation_date == datetime.date(2023, 10, 9), "All bonds information is as of 2023-10-09."
    private_params_path = os.path.join(project_dir, 'private_params.yml')
    key = read_private_params_for_key(private_params_path)
    file_path = os.path.join(parent_dir, rel_file_path)
    bonds_info_dict = load_and_decrypt_data(file_path, key)
    return parse_bond_info(valuation_date, bonds_info_dict, **kwargs)

# def get_sample_discount_curve(valuation_date=datetime.date(2023, 10, 9),
#                               spot_date=datetime.date(2023, 10, 11),
#                               rel_file_path='testing_data/discount_curve_rates_20231009.pickle'):
#     file_path = os.path.join(parent_dir, rel_file_path)
#     with open(file_path, "rb") as f:
#         dates_rates = pickle.load(f)

#     discount_curve = DiscountCurveZeroRates(
#         anchor_date=valuation_date,
#         dates=[x[0] for x in dates_rates],
#         rates=[x[1] for x in dates_rates],
#         spot_date=spot_date,
#         continuous_compounding=False,
#     )
#     return discount_curve

def get_sample_discount_curve(valuation_date=datetime.date(2023, 10, 9),
                              spot_date=datetime.date(2023, 10, 11),
                              rel_file_path='testing_data/discount_curve_20231009.pkl'):

    private_params_path = os.path.join(project_dir, 'private_params.yml')
    key = read_private_params_for_key(private_params_path)
    file_path = os.path.join(parent_dir, rel_file_path)
    dates_rates = load_and_decrypt_data(file_path, key)
    discount_curve = DiscountCurveZeroRates(
        anchor_date=valuation_date,
        dates=[x[0] for x in dates_rates],
        rates=[x[1] for x in dates_rates],
        spot_date=spot_date,
        continuous_compounding=False,
    )
    return discount_curve
