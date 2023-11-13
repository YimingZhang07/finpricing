from finpricing.instrument.legacy.cds import SingleNameCDS
from finpricing.utils.date import Date
from finpricing.market.legacy.discount_curve import DiscountCurve
from finpricing.market.legacy.survival_curve import SurvivalCurve


def test_cds_payment_dates():
    cds = SingleNameCDS(Date(2019, 11, 22), Date(2024, 12, 20), 0.05)
    res1 = [Date(2019, 9, 20),
            Date(2019, 12, 20),
            Date(2020, 3, 20),
            Date(2020, 6, 22),
            Date(2020, 9, 21),
            Date(2020, 12, 21),
            Date(2021, 3, 22),
            Date(2021, 6, 21),
            Date(2021, 9, 20),
            Date(2021, 12, 20),
            Date(2022, 3, 21),
            Date(2022, 6, 20),
            Date(2022, 9, 20),
            Date(2022, 12, 20),
            Date(2023, 3, 20),
            Date(2023, 6, 20),
            Date(2023, 9, 20),
            Date(2023, 12, 20),
            Date(2024, 3, 20),
            Date(2024, 6, 20),
            Date(2024, 9, 20),
            Date(2024, 12, 23)]
    assert cds.generate_adj_payment_dates() == res1

    isda_example_cds = SingleNameCDS(
        Date(2009, 2, 20), Date(2010, 3, 20), 0.05)
    res2 = [Date(2008, 12, 22),
            Date(2009, 3, 20),
            Date(2009, 6, 22),
            Date(2009, 9, 21),
            Date(2009, 12, 21),
            Date(2010, 3, 22)]
    assert isda_example_cds.generate_adj_payment_dates() == res2



def test_cds_value():
    cds1 = SingleNameCDS(Date(2009, 2, 20), Date(2010, 3, 20), 0.01, notional=36e6)
    assert cds1.accrual_days == [0, 88, 94, 91, 91, 90]

    # a markit example
    d_times = [0.00000000e+00, 2.73972603e-03, 8.76712329e-02, 1.69863014e-01,
               2.60273973e-01, 5.01369863e-01, 1.00821918e+00, 2.00547945e+00,
               3.00547945e+00, 4.00547945e+00, 5.00821918e+00, 6.01369863e+00,
               7.01095890e+00, 8.00821918e+00, 9.01095890e+00, 1.00109589e+01,
               1.20164384e+01]
    d_values = [1., 0.99995235, 0.99847727, 0.99685535, 0.99501906,
                0.99048278, 0.98086063, 0.96931761, 0.95574942, 0.94172625,
                0.92730572, 0.91260623, 0.89755456, 0.88200928, 0.86594768,
                0.84965066, 0.81803182]
    s_times = [0.,  1.08219178,  2.08219178,  3.08219178,  4.08219178,
               5.08493151,  7.08493151, 10.08767123, 15.09041096]
    s_values = [1., 0.98187795, 0.96545124, 0.94930328, 0.93342666,
                0.91777397, 0.88733764, 0.84353542, 0.77530807]
    dc = DiscountCurve.FromValues(d_times, d_values)
    sc = SurvivalCurve.FromValues(s_times, s_values)
    cds2 = SingleNameCDS(Date(2019, 11, 22), Date(2024, 12, 20), 0.05)

    # check accrued interest
    assert cds2.accrued_from_last_coupon == {'days': 63, 'factor': 0.175, 'interest': 8750.0}

    # valuation assertion
    value_res = cds2.value(Date(2019, 11, 21), dc, sc, price_type='detail')
    assert abs(value_res.get('premium').get("dirty") - 245977.52053862155) < 2
    assert abs(value_res.get('dirty') + 198532.0164564617) < 2
    assert abs(value_res.get('clean') + 189782.01645646163) < 2
    assert abs(value_res.get('protection') - 47445.50408215988) < 2

    # check risky pv01
    my_res = cds2.risky_pv01(Date(2019, 11, 21), dc, sc)
    financepy_res = {'full_rpv01': 4.91955041077243, 'clean_rpv01': 4.744550410772431}
    assert abs(my_res.get('clean') - financepy_res.get('clean_rpv01')) < 1e-4
    assert abs(my_res.get('dirty') - financepy_res.get('full_rpv01')) < 1e-4
