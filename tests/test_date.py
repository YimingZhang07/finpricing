from finpricing.utils.date import Date, TimeInterval


def test_is_weekend():
    assert Date(2020, 1, 1).is_weekend is False
    assert Date(2020, 1, 2).is_weekend is False
    assert Date(2020, 1, 3).is_weekend is False
    assert Date(2020, 1, 4).is_weekend is True
    assert Date(2020, 1, 5).is_weekend is True
    assert Date(2020, 1, 6).is_weekend is False
    assert Date(2020, 1, 7).is_weekend is False
    assert Date(2020, 1, 8).is_weekend is False
    assert Date(2020, 1, 9).is_weekend is False
    assert Date(2020, 1, 10).is_weekend is False
    assert Date(2020, 1, 11).is_weekend is True
    assert Date(2020, 1, 12).is_weekend is True
    assert Date(2020, 1, 13).is_weekend is False
    assert Date(2020, 1, 14).is_weekend is False


def test_operations():
    assert Date(2020, 1, 1).add_days(1) == Date(2020, 1, 2)
    assert Date(2020, 1, 1).add_days(2) == Date(2020, 1, 3)
    assert Date(2022, 5, 3).add_days(3) == Date(2022, 5, 6)
    assert Date(2020, 1, 1) - Date(2020, 1, 1) == 0
    assert Date(2020, 1, 2) - Date(2020, 1, 1) == 1
    assert Date(2020, 1, 1) == Date(2020, 1, 1)
    assert Date(2020, 1, 1) != Date(2020, 1, 2)
    assert Date(2010, 3, 20) >= Date(2009, 2, 20)


def test_add_tenor():
    """Test add_tenors() method together with add_months(), add_years() etc.

    Using the datetime module, the leap year is handled automatically.
    """
    assert Date(2020, 1, 1).add_months(1) == Date(2020, 2, 1)
    assert Date(2020, 12, 1).add_months(2) == Date(2021, 2, 1)
    assert Date(2020, 1, 30).add_months(1) == Date(2020, 2, 29)
    assert Date(2021, 1, 31).add_months(1) == Date(2021, 2, 28)
    assert Date(2020, 1, 1).add_tenor("1Y") == Date(2021, 1, 1)
    assert Date(2020, 1, 1).add_tenor("2Y") == Date(2022, 1, 1)
    assert Date(2023, 6, 28).add_tenor("15d") == Date(2023, 7, 13)
    assert Date(2023, 6, 28).add_tenor("1m") == Date(2023, 7, 28)
    assert Date(2023, 2, 28).add_tenor("1M") == Date(2023, 3, 28)
    assert Date(2023, 2, 28).add_tenor("1W") == Date(2023, 3, 7)
    
def test_time_interval():
    interval = TimeInterval.from_string("3m")
    assert repr(3 * interval) == "9m"
