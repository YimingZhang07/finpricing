import pytest
import datetime
from finpricing.utils import *

class TestCDSUtils(object):
    def setup_class(self):
        self.date_generator = DateGenerator()
        
    def test_date_generator(self):
        dates = self.date_generator.generate_extended(
            start_date = datetime.date(2023, 9, 16),
            maturity_date = datetime.date(2028, 11, 15),
            time_interval = "3m",
            stub_at_end = True
        )
        assert dates[0] == datetime.date(2023, 9, 16)
        assert dates[-1] == datetime.date(2028, 12, 16)

        dates = self.date_generator.generate_cds(
            start_date = datetime.date(2023, 8, 15),
            maturity_date = datetime.date(2028, 11, 15),
            cds_style = CDSStyle.CORP_NA()
        )
        assert dates[0] == datetime.date(2023, 11, 15)
        assert dates[-1] == datetime.date(2028, 11, 15)