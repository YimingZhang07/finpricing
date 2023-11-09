from typing import Union, List
from finpricing.utils import TimeInterval, CDSStyle, CDSStubType, Date

class DateGenerator:
    def __init__(self):
        pass

    @staticmethod
    def generate_extended(
        start_date,
        maturity_date,
        time_interval: TimeInterval,
        stub_at_end: bool
    ):
        if isinstance(time_interval, str):
            time_interval = TimeInterval.from_string(time_interval)

        start_date=Date.convert_from_datetime(start_date)
        maturity_date=Date.convert_from_datetime(maturity_date)

        dates = list()
        if stub_at_end:
            next_date = start_date
            while next_date < maturity_date:
                dates.append(next_date)
                next_date = next_date.add_interval(time_interval)
            dates.append(next_date)
        else:
            prev_date = maturity_date
            while prev_date > start_date:
                dates.append(prev_date)
                prev_date = prev_date.add_interval(-time_interval)
            dates.append(prev_date)
            dates.reverse()
        return dates

    @staticmethod
    def generate_cds(
        start_date,
        maturity_date,
        cds_style: CDSStyle,
        stub_at_end: bool=False
    ):
        start_date=Date.convert_from_datetime(start_date)
        maturity_date=Date.convert_from_datetime(maturity_date)

        time_interval = TimeInterval(int(12 / cds_style.frequency_type.value), "m")
        unadjust_dates = DateGenerator.generate_extended(start_date,
                                            maturity_date,
                                            time_interval,
                                            stub_at_end)
        if cds_style.cds_stub_length == CDSStubType.NO_STUB:
            return unadjust_dates[1:]
        else:
            raise NotImplementedError("Given CDS Stub Type is not implemented yet.")