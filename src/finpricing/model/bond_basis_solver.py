from typing import Union
import scipy
from ..utils import *

BASIS_SOLVER_PARAMS = {
    'a'             : -0.1,
    'b'             : 0.1,
    'xtol'          : 1e-8,
    'rtol'          : 1e-8,
    'maxiter'       : 100,
    'full_output'   : False,
    'disp'          : True,
}

def BondBasisSolver(
    bond_pricer,
    valuation_date: Union[datetime.date, Date],
    dirty_price: float,
    survival_curve,
    discount_curve,
    recovery_rate: float = 0.4,
    basis_type: str='AdditiveZeroRates',
    basis_solver_params=BASIS_SOLVER_PARAMS
):
    def target_function(basis):
        price = bond_pricer.price_with_basis(
            valuation_date=valuation_date,
            survival_curve=survival_curve,
            discount_curve=discount_curve,
            recovery_rate=recovery_rate,
            basis=basis,
            basis_type=basis_type
        )
        return price - dirty_price
    
    root = scipy.optimize.brentq(
        f=target_function,
        **basis_solver_params
    )
    return root