from enum import Enum
from ..utils.date import Date
from ..utils.bus_day_adj import BusDayAdjustTypes
from ..utils.holiday import CalendarTypes
from ..utils.calendar import DateGenRuleTypes
from ..utils.day_count import DayCountTypes
from ..utils.frequency import FrequencyTypes
from ..utils.literal import Literal
from ..utils.error import NotSupportedError
from .swap_fixed_leg import SwapFixedLeg
from .swap_float_leg import SwapFloatLeg
from ..market.curve import BaseCurve

# Reference: https://www.quantlib.org/reference/class_quant_lib_1_1_vanilla_swap.html
# Reference: https://quant.opengamma.io/Interest-Rate-Instruments-and-Market-Conventions.pdf
# Reference: https://insight.factset.com/hubfs/Resources/White%20Papers/Interest_Rate_Swap_Valuation_WP.pdf


class SwapCounterpartyTypes(Enum):
    """Swap counterparty types"""
    FIXED_RATE_PAYER = 0
    FIXED_RATE_RECEIVER = 1


class VanillaInterestRateSwap:
    """A standard fixed vs floating interest rate swap"""

    def __init__(self,
                 start_date: Date,
                 maturity_date_or_tenor: tuple((Date, str)),
                 fixed_rate: float,
                 float_spread: float = 0.,
                 notional: float = Literal.ONE_MILLION.value,
                 counterparty_type: SwapCounterpartyTypes = SwapCounterpartyTypes.FIXED_RATE_PAYER,
                 fixed_freq_type: FrequencyTypes = FrequencyTypes.QUARTERLY,
                 fixed_day_count_type: DayCountTypes = DayCountTypes.Thirty_360,
                 float_freq_type: FrequencyTypes = FrequencyTypes.QUARTERLY,
                 float_day_count_type: DayCountTypes = DayCountTypes.Thirty_E_360,
                 calendar_type: CalendarTypes = CalendarTypes.WEEKEND,
                 bus_day_adj_type: BusDayAdjustTypes = BusDayAdjustTypes.FOLLOWING,
                 date_gen_rule_type: DateGenRuleTypes = DateGenRuleTypes.BACKWARD):
        self._start_date = start_date
        self._fixed_rate = fixed_rate
        self._float_spread = float_spread
        self._notional = notional
        self._counterparty_type = counterparty_type
        self._fixed_freq_type = fixed_freq_type
        self._fixed_day_count_type = fixed_day_count_type
        self._float_freq_type = float_freq_type
        self._float_day_count_type = float_day_count_type
        self._calendar_type = calendar_type
        self._bus_day_adj_type = bus_day_adj_type
        self._date_gen_rule_type = date_gen_rule_type
        if isinstance(maturity_date_or_tenor, Date):
            self._maturity_date = maturity_date_or_tenor
        elif isinstance(maturity_date_or_tenor, str):
            self._maturity_date = start_date.add_tenor(maturity_date_or_tenor)
        else:
            raise NotSupportedError("maturity_date_or_tenor must be either Date or str")

        # derived attributes
        self.fixed_leg = SwapFixedLeg(start_date=self._start_date,
                                      maturity_date_or_tenor=self._maturity_date,
                                      coupon_rate=self._fixed_rate,
                                      notional=self._notional,
                                      principal=0.,
                                      payment_lag=0,
                                      freq_type=self._fixed_freq_type,
                                      day_count_type=self._fixed_day_count_type,
                                      calendar_type=self._calendar_type,
                                      bus_day_adj_type=self._bus_day_adj_type,
                                      date_gen_rule_type=self._date_gen_rule_type)

        self.float_leg = SwapFloatLeg(start_date=self._start_date,
                                      maturity_date_or_tenor=self._maturity_date,
                                      spread=self._float_spread,
                                      notional=self._notional,
                                      principal=0.,
                                      payment_lag=0,
                                      freq_type=self._float_freq_type,
                                      day_count_type=self._float_day_count_type,
                                      calendar_type=self._calendar_type,
                                      bus_day_adj_type=self._bus_day_adj_type,
                                      date_gen_rule_type=self._date_gen_rule_type)

    @property
    def notional(self):
        return self._notional

    @property
    def start_date(self):
        return self._start_date

    @property
    def maturity_date(self):
        """Maturity date of the swap

        This maturity date is supposed to be the actual last payment date (adjusted).

        TODO: check if the float leg maturity date is the same as the fixed leg maturity date and has been adjusted.
        """
        return self.fixed_leg.maturity_date

    def value(self,
              valuation_date: Date,
              discount_curve: BaseCurve,
              index_curve: BaseCurve,
              ) -> float:
        """Value the swap

        This method calls the value() method of the fixed leg and the float leg.
        Args:
            valuation_date (Date): valuation date
            discount_curve (BaseCurve): discount curve
            index_curve (BaseCurve): index curve
        Returns:
            float: swap value
        """
        fixed_leg_vale = self.fixed_leg.value(valuation_date, discount_curve)
        float_leg_vale = self.float_leg.value(valuation_date, discount_curve, index_curve)
        if self._counterparty_type == SwapCounterpartyTypes.FIXED_RATE_PAYER:
            return float_leg_vale - fixed_leg_vale
        else:
            return fixed_leg_vale - float_leg_vale

    def __repr__(self):
        """Representation of the swap"""
        s = "VANILLA INTEREST RATE SWAP\n"
        s += self.fixed_leg.__repr__() + "\n" + self.float_leg.__repr__()
        return s

    def __hash__(self) -> int:
        """Hash of the swap"""
        return hash(tuple(self.__dict__.values()))

    def pv01(self, valuation_date: Date, discount_curve: BaseCurve) -> float:
        """PV01 of the swap fixed leg.

        TODO: implement this method using repricing approach and test

        This is defined as the present value of an annualized coupon of 1 dollar on the fixed leg only.
        This could be achieved by bumping the coupon rate by 1 basis point and repricing the swap.
        Alternatively, this is the average swap value on yearly total dollar payment.   
        """
        return self.fixed_leg.pv01(valuation_date, discount_curve)

    def swap_rate(self, valuation_date: Date, discount_curve: BaseCurve, index_curve: BaseCurve = None) -> float:
        """Swap rate

        This is the fixed rate that makes the swap value zero.

        reference: Modeling single name and multi-name credit derivatives, 2008, p. 20
        """
        if valuation_date < self._start_date:
            df0 = discount_curve.df(self._start_date)
        else:
            df0 = discount_curve.df(valuation_date)

        if index_curve is None:
            df_t = discount_curve.df(self._maturity_date)
            float_leg_pv = df0 - df_t
        else:
            float_leg_pv = self.float_leg.value(valuation_date, discount_curve, index_curve)
            float_leg_pv = float_leg_pv / self._notional

        pv01 = self.pv01(valuation_date, discount_curve)
        return float_leg_pv / pv01
