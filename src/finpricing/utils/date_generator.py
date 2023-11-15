import datetime
from bisect import bisect_left
from typing import Union, List

from finpricing.utils.date import TimeInterval, Date
from finpricing.utils.cds_style import CDSStyle, CDSStubType, CDSTermStyle
from finpricing.utils.tools import datetimeToDates
from finpricing.utils.calendar import Calendar

class DateGenerator:
    def __init__(self):
        pass

    @staticmethod
    @datetimeToDates
    def generate_extended(
        start_date: Union[datetime.date, Date],
        maturity_date: Union[datetime.date, Date],
        time_interval: Union[TimeInterval, str],
        stub_at_end: bool
    ):
        """generate a list of dates from start_date to maturity_date with given time_interval
        
        NOTE:
            if stub_at_end is True, the dates will be generated from start_date and roll forward until and after maturity_date
            if stub_at_end is False, the dates will be generated from maturity_date and roll backward until and before start_date
        
        Args:
            start_date (Union[datetime.date, Date]): start date
            maturity_date (Union[datetime.date, Date]): maturity date
            time_interval (Union[TimeInterval, str]): time interval
            stub_at_end (bool): whether the stub is at the end of the period
        """
        if isinstance(time_interval, str):
            time_interval = TimeInterval.from_string(time_interval)

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
    @datetimeToDates
    def generate_cds(
        start_date,
        maturity_date,
        cds_style: CDSStyle,
        stub_at_end: bool=False
    ):
        """generate a list of dates from start_date to maturity_date with given cds_style
        
        NOTE:
            Most likely, the stub is at the end of the period. In a NO_STUB case, the first date will be removed. \
                So the first date will be after start_date.
        """
        time_interval = TimeInterval(int(12 / cds_style.frequency_type.value), "m")
        unadjust_dates = DateGenerator.generate_extended(start_date,
                                            maturity_date,
                                            time_interval,
                                            stub_at_end)
        if cds_style.cds_stub_length == CDSStubType.NO_STUB:
            return unadjust_dates[1:]
        else:
            raise NotImplementedError("Given CDS Stub Type is not implemented yet.")
        
    @staticmethod
    @datetimeToDates
    def generate_cds_adjust(
        start_date,
        maturity_date,
        cds_style: CDSStyle,
        stub_at_end: bool=False
    ):
        """generate accrual start dates, accrual end dates, and calendar adjusted payment dates for a cds contract
        
        NOTE only the payment dates are adjusted!
        """
        # generate unadjusted dates
        dates = DateGenerator.generate_cds(start_date, maturity_date, cds_style, stub_at_end)
        # calendar type considers the holidays, and business day adjustment type considers the following, previous, etc.
        calendar = Calendar(cds_style.calendar_type)
        bus_adj_type = cds_style.bus_day_adj_type
        
        accrual_start_dates = list()
        accrual_end_dates = list()
        payment_dates = list()
        
        this_accrual_start_date = start_date
        for x in dates:
            this_accrual_end_date = x
            this_payment_date = calendar.adjust(this_accrual_end_date, bus_adj_type)
            if this_accrual_end_date < maturity_date:
                this_accrual_end_date = this_payment_date
            accrual_start_dates.append(this_accrual_start_date)
            accrual_end_dates.append(this_accrual_end_date)
            payment_dates.append(this_payment_date)
            
            this_accrual_start_date = this_accrual_end_date
        assert this_accrual_start_date == maturity_date
        return accrual_start_dates, accrual_end_dates, payment_dates
    
    @staticmethod
    def generate_cds_maturity_date(market_date: Union[Date, datetime.date],
                                   maturity_date: Union[Date, datetime.date],
                                   term_style: str=None):
        """return the adjusted maturity date for a cds contract by its term style
        
        FIXME This is not effectively implemented yet. It seems IMM CORPORATE returns the same maturity date as the input.
        """
        if term_style == CDSTermStyle.IMM_CORPORATE:
            return maturity_date
        else:
            raise NotImplementedError("CDS maturity date: given CDS Term Style is not implemented yet.")

    @staticmethod
    @datetimeToDates
    def generate_cds_effective_date(market_date: Union[Date, datetime.date],
                                    maturity_date: Union[Date, datetime.date],
                                    cds_style: Union[CDSStyle, str]):
        """generate the effective date for a cds contract when market date is in between coupon dates
        """
        step_in_date = market_date.add_tenor("1d")
        time_interval = TimeInterval(int(12 / cds_style.frequency_type.value), "m")
        
        safe_start_date = step_in_date.add_interval(-3 * time_interval)
        dates = DateGenerator.generate_cds(safe_start_date, maturity_date, cds_style, stub_at_end=False)
        
        # business day adjustment
        calendar = Calendar(cds_style.calendar_type)
        bus_adj_type = cds_style.bus_day_adj_type
        dates = [calendar.adjust(x, bus_adj_type) for x in dates]
        
        # find the previous valid date before step_in_date
        idx_effective_date = bisect_left(dates, step_in_date) - 1
        return dates[idx_effective_date]
