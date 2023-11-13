from math import log, exp, ceil
from ...utils.date import Date
from ...utils.bus_day_adj import BusDayAdjustTypes
from ...utils.holiday import CalendarTypes
from ...utils.calendar import Calendar, DateGenRuleTypes
from ...utils.day_count import DayCountTypes, DayCount
from ...utils.frequency import FrequencyTypes
from ...utils.literal import Literal
from ...utils.error import NotSupportedError
from ...market.legacy.discount_curve import DiscountCurve
from ...market.legacy.survival_curve import SurvivalCurve


class SingleNameCDS:
    def __init__(self,
                 step_in_date: Date,
                 maturity_date: Date,
                 contract_spread: float,
                 notional: float = Literal.ONE_MILLION.value,
                 freq_type: FrequencyTypes = FrequencyTypes.QUARTERLY,
                 day_count_type: DayCountTypes = DayCountTypes.ACT_360,
                 calendar_type: CalendarTypes = CalendarTypes.WEEKEND,
                 date_gen_rule_type: DateGenRuleTypes = DateGenRuleTypes.BACKWARD,
                 bus_day_adj_type: BusDayAdjustTypes = BusDayAdjustTypes.FOLLOWING) -> None:
        """Initialize a Single Name CDS contract

        Args:
            step_in_date (Date): settlement date / protection effective date
            maturity_date (Date): maturity date / protection termination date
            contract_spread (float): contract spread in decimal / coupon rate
            notional (float, optional): notional amount. Defaults to Literal.ONE_MILLION.value.
            freq_type (FrequencyTypes, optional): coupon frequency. Defaults to FrequencyTypes.QUARTERLY.
            day_count_type (DayCountTypes, optional): day count convention. Defaults to DayCountTypes.ACT_360.
            calendar_type (CalendarTypes, optional): calendar type. Defaults to CalendarTypes.WEEKEND.
            date_gen_rule_type (DateGenRuleTypes, optional): date generation rule type. Defaults to DateGenRuleTypes.BACKWARD.
            bus_day_adj_type (BusDayAdjustTypes, optional): business day adjustment type. Defaults to BusDayAdjustTypes.FOLLOWING.
        """
        self._step_in_date = step_in_date
        self._maturity_date = maturity_date
        self._contract_spread = contract_spread
        self._notional = notional
        self._freq_type = freq_type
        self._day_count_type = day_count_type
        self._calendar_type = calendar_type
        self._date_gen_rule_type = date_gen_rule_type
        self._bus_day_adj_type = bus_day_adj_type
        # derived attributes
        self._calendar = Calendar(calendar_type)
        self._day_count = DayCount(day_count_type)
        self._payment_dates = []
        self._accrual_days = []
        self._accrual_factors = []
        self._premium_cashflows = []
        # actions on initialization
        self.generate_adj_payment_dates()
        self.generate_cashflows()

    @ property
    def accrual_days(self) -> list:
        """Return a list of accrual days"""
        return self._accrual_days

    def _generate_unadj_payment_dates(self) -> list:
        """Return a list of unadjusted payment dates

        NOTE:
            when using the "backward" date generation rule, a previous coupon date is also included in the list.
            This is for the easier calculation of accrued interest.

        Reference of a standard CDS contract:
            1. https://www.cdsmodel.com/documentation.html?#
            2. https://www.cdsmodel.com/assets/cds-model/docs/Standard%20CDS%20Examples%20Updated%20Oct%202012.pdf
            3. https://www.cdsmodel.com/assets/cds-model/docs/Standard%20CDS%20Contract%20Specification.pdf

        For a standard CDS contract, the payment dates are generated backward from the maturity date, adjusted "following" to the business day.
        """
        if self._date_gen_rule_type == DateGenRuleTypes.FORWARD:
            payment_dates = []
            next_date = self._step_in_date
            interval = int(12 / self._freq_type.value)
            while next_date <= self._maturity_date:
                payment_dates.append(next_date)
                next_date = next_date.add_months(interval)
            # add the next coupon date after maturity date
            payment_dates.append(next_date)
            return payment_dates
        elif self._date_gen_rule_type == DateGenRuleTypes.BACKWARD:
            payment_dates = []
            next_date = self._maturity_date
            interval = int(12 / self._freq_type.value)
            while next_date >= self._step_in_date:
                payment_dates.append(next_date)
                next_date = next_date.add_months(-interval)
            # add the previous coupon date
            payment_dates.append(next_date)
            return payment_dates[::-1]
        else:
            raise NotSupportedError(
                "Generate payment dates failed as DateGenRuleTypes is not supported")

    def generate_adj_payment_dates(self) -> list:
        """Return a list of adjusted payment dates"""
        unadj_payment_dates = self._generate_unadj_payment_dates()
        # for the last payment date, it needs to be adjusted to T + 1 and then adjusted to the business day
        unadj_payment_dates[-1] = unadj_payment_dates[-1].add_days(1)
        adj_payment_dates = [self._calendar.adjust(date, self._bus_day_adj_type) for date in unadj_payment_dates]
        self._payment_dates = adj_payment_dates
        return adj_payment_dates

    def generate_cashflows(self):
        """Generate the premium cashflows of the CDS contract"""
        num_payments = len(self._payment_dates)
        # note that we define the first payment date as the previous coupon date
        # accrual i is from payment_dates[i-1] to payment_dates[i]
        # so we need to insert dummy values for the first payment, i is meaning full from 1.
        self._accrual_days.append(0)
        self._accrual_factors.append(0)
        self._premium_cashflows.append(0)
        # according to the standard CDS contract, the accrual days are from last payment date to current payment date, except for the maturity one
        for i in range(1, num_payments-1):
            start_date = self._payment_dates[i-1]
            end_date = self._payment_dates[i]
            accrual_days, accrual_factor = self._day_count.days_between(start_date, end_date)
            premium_amount = accrual_factor * self._contract_spread * self._notional
            self._premium_cashflows.append(premium_amount)
            self._accrual_days.append(accrual_days)
            self._accrual_factors.append(accrual_factor)
        # though the last payment date is business day adjusted, the accrual ends at maturity date
        last_accrual_days, last_accrual_factor = \
            self._day_count.days_between(self._payment_dates[-2], self._maturity_date, include_end=True)
        self._accrual_days.append(last_accrual_days)
        self._accrual_factors.append(last_accrual_factor)
        self._premium_cashflows.append(last_accrual_factor * self._contract_spread * self._notional)

    def print_cashflows(self):
        num_rows = len(self._payment_dates)
        print("{0:20s} {1:>20s} {2:>20s} {3:>20s}".format(
            "Payment Date", "Accrual Days From Last", "Year Fraction", "Premium Amount"))
        for i in range(num_rows):
            print("{0:20s} {1:>20s} {2:>20.4f} {3:>20.4f}".format(str(self._payment_dates[i]),
                                                                  str(self._accrual_days[i]),
                                                                  self._accrual_factors[i],
                                                                  self._premium_cashflows[i]))

    @ property
    def accrued_from_last_coupon(self) -> dict:
        """Accrued information from the previous coupon date to the step-in date

        NOTE:
            This can be confused with the accrued interest due to default between two coupon dates in the future.
            Here, this is the accrued amount due to entering the contract in the middle of the accrual period.
        """
        preivous_coupon_date = self._payment_dates[0]
        accrued_days, accrued_factor = self._day_count.days_between(preivous_coupon_date, self._step_in_date)
        accrued_interest = accrued_factor * self._contract_spread * self._notional
        return {
            "days": accrued_days,
            "factor": accrued_factor,
            "interest": accrued_interest,
        }

    def risky_pv01(self,
                   valuation_date: Date,
                   discount_curve: DiscountCurve,
                   survival_curve: SurvivalCurve,
                   method=1) -> dict:
        """Calculate the risky PV01 of the Premium Leg

        Unlike what can be represented in some texts, this pv01 excludes the notional and the contract spread.

        Args:
            valuation_date (Date): valuation date
            discount_curve (object): discount curve object
            survival_curve (object): survival curve object
            method (int): 0 for the Halfway Approximation, 1 for flat hazard rate integral

        Returns:
            dict: risky PV01 of the Premium Leg, clean and dirty
        """
        # 1. need to find time to payment from valuation date for discounting practice
        # The discounting convention is using ACT_365, different from the accrual convention
        discount_dcc = DayCount(DayCountTypes.ACT_365)
        payment_times = [discount_dcc.year_fraction(valuation_date, payment_date) for payment_date in self._payment_dates]
        # 2. get the accrued interest
        accrued_from_last_coupon = self.accrued_from_last_coupon
        # 3. calculate the time to step-in date from value date
        time_to_effective = discount_dcc.year_fraction(valuation_date, self._step_in_date)
        return self.risky_pv01_helper(
            payment_times,
            accrued_from_last_coupon,
            time_to_effective,
            discount_curve,
            survival_curve,
            method,
        )

    def risky_pv01_helper(self,
                          payment_times: list,
                          accrued_from_last_coupon: dict,
                          time_to_effective: float,
                          discount_curve,
                          survival_curve,
                          method=1) -> dict:
        """Actual calculation of the risky PV01 of the Premium Leg

        The flat hazard rate method integral is a bit involved, please refer to the math and implementation notes for derivation.

        Args:
            payment_times (list): list of payment times in year fraction using discount convention (ACT_365); relative to the valuation date
            accrued_from_last_coupon (dict): accrued information from the previous coupon date to the step-in date
            time_to_effective (float): time to step-in date from valuation date
            discount_curve (object): discount curve object
            survival_curve (object): survival curve object

        Returns:
            dict: risky PV01 of the Premium Leg, clean and dirty
        """
        if method not in [0, 1]:
            raise NotSupportedError("RPV01 Method not supported")

        # special calculation for the first payment, as the accrual from last coupon date to step-in date is risk free
        # note that the first payment date is the previous coupon date, so we want to use the second payment date as next coupon date
        # time here are relative to the valuation date
        q_step_in = survival_curve.get_survival_prob(time_to_effective)
        q1 = survival_curve.get_survival_prob(payment_times[1])
        z1 = discount_curve.get_discount_factor(payment_times[1])
        accrued_factor = accrued_from_last_coupon.get("factor")
        accrual_factor = self._accrual_factors

        # regular coupon payment at the end of the period
        fullRPV01 = q1 * z1 * accrual_factor[1]
        # risky free accrued interest
        fullRPV01 += z1 * (q_step_in - q1) * accrued_factor
        # risky accrued interest assuming halfway default and discount from end of the period
        # accrual_factor[1] is the accrual factor from previous coupon date to next coupon date
        fullRPV01 += 0.5 * z1 * (q_step_in - q1) * (accrual_factor[1] - accrued_factor)

        # Rest of the payments
        for it in range(2, len(payment_times)):
            t2 = payment_times[it]
            q2 = survival_curve.get_survival_prob(t2)
            z2 = discount_curve.get_discount_factor(t2)
            delta = accrual_factor[it]
            # regular coupon payment at the end of the period
            fullRPV01 += q2 * z2 * delta
            # risky discount of the accrued interest
            if method == 0:
                fullRPV01 += 0.5 * (q2 - q1) * z2 * delta
            elif method == 1:
                h = -log(q2 / q1) / delta
                r = -log(z2 / z1) / delta
                alpha = h + r
                term1 = h * q1 * z1
                term2 = (1 - exp(-alpha * delta) * (1 + alpha * delta)) / (alpha ** 2)
                fullRPV01 += term1 * term2
            else:
                raise NotSupportedError("RPV01 Method not supported")
            q1 = q2

        cleanRPV01 = fullRPV01 - accrued_factor
        return {'clean': cleanRPV01, 'dirty': fullRPV01}

    def premium_leg_pv(self, valuation_date: Date, discount_curve, survival_curve, method=1) -> dict:
        """Calculate the PV of the Premium Leg

        Args:
            valuation_date (Date): valuation date
            discount_curve (object): discount curve object
            survival_curve (object): survival curve object
            method (int): 0 for the Halfway Approximation, 1 for flat hazard rate

        Returns:
            dict: PV of the Premium Leg, clean and dirty
        """
        RPV01 = self.risky_pv01(valuation_date, discount_curve, survival_curve, method)
        pv_dirty = RPV01.get('dirty') * self._contract_spread * self._notional
        pv_clean = RPV01.get('clean') * self._contract_spread * self._notional
        return {"clean": pv_clean, "dirty": pv_dirty}

    def protection_leg_pv(self,
                          valuation_date: Date,
                          discount_curve,
                          survival_curve,
                          method: int = 1,
                          recovery_rate: float = 0.4,
                          num_steps_per_year: int = 25) -> float:
        """Calculate the PV of the Protection Leg

        For flat hazard rate integral, please refer to the math and implementation notes for derivation.

        Args:
            valuation_date (Date): valuation date
            discount_curve (object): discount curve object
            survival_curve (object): survival curve object
            method (int): 0 for the Halfway Approximation, 1 for flat hazard rate
            recovery_rate (float): recovery rate
            num_steps_per_year (int): number of steps per year for the integration

        Returns:
            float: PV of the Protection Leg
        """
        discount_dcc = DayCount(DayCountTypes.ACT_365)
        time_to_valuation = discount_dcc.year_fraction(valuation_date, self._step_in_date)
        time_to_mat = discount_dcc.year_fraction(valuation_date, self._maturity_date)
        dt = 1 / num_steps_per_year
        t = time_to_valuation
        total_steps = ceil((time_to_mat - time_to_valuation) * num_steps_per_year)
        z1 = discount_curve.get_discount_factor(time_to_valuation)
        q1 = survival_curve.get_survival_prob(time_to_valuation)
        pv = 0
        for _ in range(total_steps):
            dt = min(dt, time_to_mat - t)
            t += dt
            z2 = discount_curve.get_discount_factor(t)
            q2 = survival_curve.get_survival_prob(t)
            # A halway default, discount immediatly from the middle of the period
            if method == 0:
                pv += 0.5 * (q1 - q2) * (z1 + z2) * dt
            # A flat hazard rate integral
            elif method == 1:
                h = -log(q2 / q1) / dt
                r = -log(z2 / z1) / dt
                alpha = h + r
                term1 = h * q1 * z1
                term2 = (1 - exp(-alpha * dt)) / alpha
                pv += term1 * term2
            else:
                raise NotSupportedError("Protection Leg PV Method not supported")
            q1 = q2
            z1 = z2
        # add the recovery component
        pv *= (1 - recovery_rate)
        return pv * self._notional

    def value(self,
              valuation_date: Date,
              discount_curve,
              survival_curve,
              premium_method: int = 1,
              protection_method: int = 1,
              recovery_rate: float = 0.4,
              num_steps_per_year: int = 25,
              price_type='dirty'):
        """Value the CDS contract

        Args:
            valuation_date (Date): valuation date
            discount_curve (object): discount curve object
            survival_curve (object): survival curve object
            premium_method (int): 0 for the Halfway Approximation, 1 for flat hazard rate
            protection_method (int): 0 for the Halfway Approximation, 1 for flat hazard rate
            recovery_rate (float): recovery rate
            num_steps_per_year (int): number of steps per year for the integration
            price_type (str): 'dirty', 'clean', 'both', 'detail'

        Returns:
            float or dict: price of the CDS contract, clean, dirty and legs
        """
        premium_pv = self.premium_leg_pv(valuation_date, discount_curve, survival_curve, premium_method)
        protection_pv = self.protection_leg_pv(valuation_date, discount_curve,
                                               survival_curve, protection_method, recovery_rate, num_steps_per_year)
        clean_pv = protection_pv - premium_pv.get("clean")
        dirty_pv = protection_pv - premium_pv.get("dirty")
        if price_type == 'dirty':
            return dirty_pv
        elif price_type == 'clean':
            return clean_pv
        elif price_type == 'both':
            return {"clean": clean_pv, "dirty": dirty_pv}
        elif price_type == 'detail':
            return {"premium": premium_pv, "protection": protection_pv, "clean": clean_pv, "dirty": dirty_pv}
        else:
            raise NotSupportedError("Price type not supported")

