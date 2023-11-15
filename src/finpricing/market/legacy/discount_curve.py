from __future__ import annotations
from copy import deepcopy
from typing import TYPE_CHECKING
from ...utils.interpolator import Interpolator, InterpTypes
from ...utils.error import NotSupportedError
from ...utils.legacy.bootstrap_tools import swap_value_by_df, newton_solve
from .curve import Curve
if TYPE_CHECKING:
    from ...instrument.deposit import Deposit
    from ...instrument.vanilla_swap import VanillaInterestRateSwap
    from .curve import BaseCurve


class DiscountCurve(Curve):
    """Discount curve class that built from deposits and swaps"""

    def get_discount_factor(self, t):
        """Get survival probability"""
        return self.get_factor(t)

    def _check_maturity_date_order(self, instruments: list) -> bool:
        """Check if the maturity dates of the instruments are in ascending order"""
        for i in range(len(instruments) - 1):
            if instruments[i].maturity_date > instruments[i + 1].maturity_date:
                return False
        return True

    def _check_same_start_date(self, instruments: list) -> bool:
        """Check if the start dates of the instruments are the same"""
        for i in range(len(instruments) - 1):
            if instruments[i].start_date != instruments[i + 1].start_date:
                return False
        return True

    def add_deposits(self,
                     deposits: list[Deposit],
                     interp_type: InterpTypes = InterpTypes.FLAT_FWD_RATES):
        """Construct the discount curve from a list of deposits

        Deposits are usually within 1 year, and uses simple compounding. Still no bootstrapping is needed.
        We just need to construct discount factors from tenors and deposit rates.

        Times from the valuation date may use a different day count convention! For example, here, the convention is ACT/365.
        Though the accrual factors for deposits are usually ACT/360. 

        TODO: confirm the day count convention

        Args:
            deposits (list(Deposit)): list of deposits
            interp_type (InterpTypes): interpolation method for the synthetic deposit
        """
        if self._check_maturity_date_order(deposits) is False:
            raise NotSupportedError("The maturity dates of the deposits are not in ascending order")
        if self._check_same_start_date(deposits) is False:
            raise NotSupportedError("The start dates of the deposits are not the same")

        dcc = self._day_count
        # valuation date is usually before the first deposit start date, so we need to add a synthetic deposit to fill in the gap
        if self._valuation_date < deposits[0].start_date:
            synthetic_deposit = deepcopy(deposits[0])
            synthetic_deposit.start_date = self._valuation_date
            synthetic_deposit.maturity_date = deposits[0].start_date
            self._times.append(dcc.year_fraction(self._valuation_date, synthetic_deposit.maturity_date))
            self._dfs.append(synthetic_deposit.fwd_discount_factor)
            self._interpolator = Interpolator(self._times, self._dfs, interp_type)

        # construct the times and dfs
        for deposit in deposits:
            time_to_settlement = dcc.year_fraction(self._valuation_date, deposit.start_date)
            # self._times.append(time_to_settlement + deposit.accrual_days_factor[1])
            self._times.append(dcc.year_fraction(self._valuation_date, deposit.maturity_date))
            df_settlement = self._interpolator.eval(time_to_settlement)
            self._dfs.append(df_settlement * deposit.fwd_discount_factor)

    def add_swaps(self,
                  swaps: list[VanillaInterestRateSwap],
                  index_curve: BaseCurve = None):
        """Construct the discount curve from a list of swaps

        NOTE: swap valuation needs index curve specified. But it is also common to just use the discount curve as the index curve.
        Actual implementation is TBD.
        """
        if self._check_maturity_date_order(swaps) is False:
            raise NotSupportedError("The maturity dates of the swaps are not in ascending order")
        if self._check_same_start_date(swaps) is False:
            raise NotSupportedError("The start dates of the swaps are not the same")

        for swap in swaps:
            # this maturity date is adjusted
            this_matuity_date = swap.maturity_date
            time_to_this_maturity = self._day_count.year_fraction(self._valuation_date, this_matuity_date)
            self.times.append(time_to_this_maturity)
            # take the last discount factor as the intial guess
            self.dfs.append(self.dfs[-1])
            args = (swap, self._valuation_date, self, index_curve)
            newton_solve(swap_value_by_df, x0=self.dfs[-1], args=args)
