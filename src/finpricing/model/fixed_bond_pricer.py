import datetime
from typing import Union
from ..utils import *
from ..market.discount_curve_zero import DiscountCurveZeroShifted
from ..instrument.fixed_bond import FixedBond
from .utils.bond_pricing_utils import principal_integral, accrual_integral
from .bond_basis_solver import BondBasisSolver, BASIS_SOLVER_PARAMS

class FixedBondPricer(ClassUtil):
    def __init__(self, inst: FixedBond) -> None:
        self.inst = inst

    @property
    def principal_amount(self):
        return self.inst.principal_leg.principal_amount

    @property
    def coupon_cashflows(self):
        return self.inst.fixed_coupon_leg.cashflows

    def principal_pv(self, valuation_date, discount_curve, survival_curve, recovery_rate):
        # principal leg value 
        principal_date = self.inst.principal_leg.maturity_date
        principal_amount = self.principal_amount

        df = discount_curve.discount(principal_date)
        q  = survival_curve.survival(principal_date)

        principal_contingent = principal_integral(
            N=principal_amount,
            R=recovery_rate,
            valuation_date=valuation_date,
            maturity_date=principal_date,
            granularity_in_days=14,
            survival_curve=survival_curve,
            discount_curve=discount_curve,
        )

        return df * q * principal_amount + principal_contingent

    def price(self,
              valuation_date: Union[datetime.date, Date],
              survival_curve,
              discount_curve,
              recovery_rate: float = 0.4) -> float:
        """risky pricing of a fixed bond
        
        Args:
            valuation_date: valuation date
            survival_curve: survival curve
            discount_curve: discount curve
            recovery_rate: recovery rate
            
        Returns:
            Dirty price of the bond.
        """
        valuation_date = Date.convert_from_datetime(valuation_date)

        pv = 0.0

        for i, item in enumerate(self.coupon_cashflows):
            date = item[0]
            amount = item[1]
            accrual_start_date = self.inst.fixed_coupon_leg.accrual_start[i].add_tenor("-1d")
            accrual_end_date = self.inst.fixed_coupon_leg.accrual_end[i].add_tenor("-1d")

            if date > valuation_date:
                df = discount_curve.discount(date)
        
                pv += df * survival_curve.survival(date.add_tenor("-1d")) * amount

                pv += amount * accrual_integral(
                    granularity_in_days=14,
                    R=recovery_rate,
                    survival_curve=survival_curve,
                    discount_curve=discount_curve,
                    accrual_start_date=accrual_start_date,
                    accrual_end_date=accrual_end_date
                )

        pv += self.principal_pv(valuation_date, discount_curve, survival_curve, recovery_rate)
        
        return pv

    def price_with_basis(self,
                         valuation_date: Union[datetime.date, Date],
                         survival_curve,
                         discount_curve,
                         recovery_rate: float = 0.4,
                         basis: float = 0.0,
                         basis_type: str='AdditiveZeroRates') -> float:
        
        discount_curve_used = discount_curve
        survival_curve_used = survival_curve
        if basis_type == 'AdditiveZeroRates':
            discount_curve_used = DiscountCurveZeroShifted(discount_curve, basis)
            
        return self.price(valuation_date, survival_curve_used, discount_curve_used, recovery_rate)
    
    def solve_basis(self,
                    valuation_date: Union[datetime.date, Date],
                    dirty_price: float,
                    survival_curve,
                    discount_curve,
                    settlement_date: Union[datetime.date, Date]=None,
                    recovery_rate: float = 0.4,
                    basis_type: str='AdditiveZeroRates',
                    basis_solver_params=BASIS_SOLVER_PARAMS) -> float:
        if settlement_date is None:
            settlement_date = valuation_date
        return BondBasisSolver(
            bond_pricer=self,
            valuation_date=valuation_date,
            dirty_price=dirty_price * discount_curve.discount(settlement_date),
            survival_curve=survival_curve,
            discount_curve=discount_curve,
            recovery_rate=recovery_rate,
            basis_type=basis_type,
            basis_solver_params=basis_solver_params
        )