from typing import Union, List
import datetime
import math
import scipy
from dataclasses import dataclass
from ..utils.date import Date
from .fixed_bond_pricer import FixedBondPricer

class BondCurveAnalyticsHelper:
    def __init__(self, bonds) -> None:
        if isinstance(bonds, list):
            self.bonds = bonds
        else:
            raise TypeError('bonds must be a list of bonds.')
        self.bond_pricers = list(map(lambda x: FixedBondPricer(x), self.bonds))
        self.n_underlyings = len(self.bonds)
        self._dirty_prices = None
        self._discount_curves = None
        self._survival_curves = None
        self._recovery_rates = None
        self._settlement_dates = None
        self._valuation_date = None
        
    @property
    def recovery_rates(self):
        if self._recovery_rates is None:
            return [0.4] * len(self.bonds)
        else:
            return self._recovery_rates
    
    @recovery_rates.setter
    def recovery_rates(self, values: List):
        if isinstance(values, list) and len(values) == len(self.bonds):
            self._recovery_rates = values
        elif isinstance(values, float):
            self._recovery_rates = [values] * len(self.bonds)
        else:
            raise TypeError('recovery_rates must be a list of floats.')
        
    @property
    def dirty_prices(self):
        if self._dirty_prices is None:
            raise ValueError('dirty_prices must be set before use.')
        else:
            return self._dirty_prices
    
    @dirty_prices.setter
    def dirty_prices(self, values: List):
        if isinstance(values, list) and len(values) == len(self.bonds):
            self._dirty_prices = values
        else:
            raise TypeError('dirty_prices must be a list of floats.')
        
    @property
    def discount_curves(self):
        if self._discount_curves is None:
            return [None] * len(self.bonds)
        else:
            return self._discount_curves
        
    @discount_curves.setter
    def discount_curves(self, curve):
        if isinstance(curve, list):
            raise NotImplementedError('list of discount curves not implemented yet.')
        else:
            self._discount_curves = [curve] * len(self.bonds)
            
    @property
    def survival_curves(self):
        if self._survival_curves is None:
            return [None] * len(self.bonds)
        else:
            return self._survival_curves
        
    @survival_curves.setter
    def survival_curves(self, curve):
        if isinstance(curve, list):
            raise NotImplementedError('list of survival curves not implemented yet.')
        else:
            self._survival_curves = [curve] * len(self.bonds)
            
    @property
    def settlement_dates(self):
        if self._settlement_dates is None:
            return [None] * len(self.bonds)
        else:
            return self._settlement_dates
    
    @settlement_dates.setter
    def settlement_dates(self, values: List):
        if isinstance(values, list) and len(values) == len(self.bonds):
            self._settlement_dates = values
        elif isinstance(values, datetime.date, Date) or isinstance(values, Date):
            self._settlement_dates = [values] * len(self.bonds)
        else:
            raise TypeError('settlement_dates must be a list of dates.')
        
    @property
    def valuation_date(self):
        if self._valuation_date is None:
            raise ValueError('valuation_date must be set before use.')
        else:
            return self._valuation_date
        
    @valuation_date.setter
    def valuation_date(self, value):
        if isinstance(value, datetime.date) or isinstance(value, Date):
            self._valuation_date = value
        else:
            raise TypeError('valuation_date must be a date.')
        
    @property
    def maturity_dates(self):
        return [bond.maturity_date for bond in self.bonds]
    
    @property
    def maturity_span(self):
        """maximum maturity minus minimum maturity in years"""
        return (max(self.maturity_dates) - min(self.maturity_dates)) / 365
        
    def get_bond_bases(self,
                       valuation_date: Union[datetime.date, Date]=None,
                       dirty_prices: List[float]=None,
                       survival_curves=None,
                       basis_type: str='AdditiveZeroRates'):
        
        if valuation_date is None:
            valuation_date = self.valuation_date

        if dirty_prices is None:
            dirty_prices = self.dirty_prices
            
        if survival_curves is None:
            survival_curves = self.survival_curves
            
        assert isinstance(dirty_prices, list), \
            "dirty_prices must be a list of floats."
        assert isinstance(survival_curves, list), \
            "survival_curves must be a list of survival curves."
        
        def f(i):
            return self.bond_pricers[i].solve_basis(
                valuation_date  = valuation_date,
                dirty_price     = dirty_prices[i],
                survival_curve  = survival_curves[i],
                discount_curve  = self.discount_curves[i],
                recovery_rate   = self.recovery_rates[i],
                settlement_date = self.settlement_dates[i],
                basis_type      = basis_type
            )
        return [f(i) for i in range(len(dirty_prices))]

@dataclass
class PenaltyParameter:
    penalty_ridge_tuning: float = 0.0001
    penalize_sample_size: bool = True
    penalize_maturity_span: bool = True
    penalize_inverted_curve: bool = True
    penalty_inverted_tuning: float = 0.2
    penalty_inverted_threshold: float = 0.01
    median_dummy_curve_level: float = 0.0097304346928168781
    
class BondCurveSolver:
    def __init__(self,
                 bondAnalyticsHelper: BondCurveAnalyticsHelper,
                 initial_params=None,
                 penalty_params: PenaltyParameter=None) -> None:
        if initial_params is None:
            self.initial_params = [0.0, 0.0, 0.0]
        if penalty_params is None:
            self.penalty_params = PenaltyParameter()
        self.helper = bondAnalyticsHelper
        self.survival_curve_generator = self.getSurvivalCurveGenerator(self.helper)
        self.weights = self.get_weights()
        
    def getSurvivalCurveGenerator(self, bondAnalyticsHelper: BondCurveAnalyticsHelper):
        """return a survival curve generator that can generate survival curves from parameters
        
        This is actually not a true generator, but a survival curve that has the method to recreate\
            a new survival curve with the same anchor date and pivot dates but different parameters.
        """
        survival_curves_set = set(bondAnalyticsHelper.survival_curves)
        if len(survival_curves_set) != 1:
            raise ValueError('Survival curves must be the same for all bonds to use bond curve solver.')
        return survival_curves_set.pop()
        
    def get_weights(self):
        fake = [0.07679328308116748,
                0.09058956234521516,
                0.10346082175856133,
                0.0768401250707676,
                0.09767649270635165,
                0.0844079519326119,
                0.09482679241380954,
                0.14687480949360318,
                0.06274016230573569,
                0.16578999889217658]
        return fake
    
    @staticmethod
    def welsch_loss(x):
        c = math.sqrt(2) * 0.01
        loss = 0.5 * c ** 2 * (1 - math.exp(-x ** 2 / c ** 2))
        return loss
        
    def get_penalty(self, params: List[float]):
        assert len(params) == 3, "params must be a list of length 3."
        tuning_scalar = self.penalty_params.penalty_ridge_tuning
        if self.penalty_params.penalize_sample_size:
            tuning_scalar /= len(self.helper.bonds)
        if self.penalty_params.penalize_maturity_span:
            tuning_scalar /= self.helper.maturity_span
        penalty = tuning_scalar * sum([param ** 2 for param in params[1:]])
        # inverted curve penalty
        if self.penalty_params.penalize_inverted_curve:
            tuning_scalar = self._get_tuning_scalar()
            derivative_at_zero = self._get_hazard_rate_derivative_at_zero(params)
            penalty += tuning_scalar * max(0., -1 * derivative_at_zero)
            
        return penalty
            
    def _get_tuning_scalar(self):
        tuning_factor = self.penalty_params.penalty_inverted_tuning
        median_dummy_curve_level = self.penalty_params.median_dummy_curve_level
        threshold = self.penalty_params.penalty_inverted_threshold
        tuning_scalar = tuning_factor / math.sinh(median_dummy_curve_level / threshold)
        return tuning_scalar
    
    def _get_hazard_rate_derivative_at_zero(self, params: List[float]):
        pivots = self.survival_curve_generator.getSurvivalCurve(params).pivots
        derivative_at_zero = -1 * sum([param / (2 * pivot ** 2) for param, pivot in zip(params[1:], pivots)])
        return derivative_at_zero
        
    def solve(self, dirty_prices, weights, params):
        res = scipy.optimize.leastsq(self.get_weighted_residuals_and_penalty,
                                     params,
                                     args = (dirty_prices, weights),
                                     xtol = 1e-15,
                                     ftol = 1e-15,
                                     full_output=False)
        return res
    
    def get_weighted_residuals_and_penalty(self,
                                           params: List[float],
                                           dirty_prices: List[float],
                                           weights: List[float],
                                           valuation_date: Union[datetime.date, Date]=None,
                                           basis_type: str='AdditiveZeroRates'):
        
        new_survival_curve = self.survival_curve_generator.getSurvivalCurve(params)
        
        bases = self.helper.get_bond_bases(valuation_date=valuation_date,
                                           dirty_prices=dirty_prices,
                                           survival_curves=[new_survival_curve] * len(dirty_prices),
                                           basis_type=basis_type)

        assert len(dirty_prices) == len(weights), "Input dirty_prices and weights must have the same length."
        loss = [self.welsch_loss(basis) for basis in bases]
        weighted_loss = [ math.sqrt(weight * loss) for weight, loss in zip(weights, loss) ]
        regularization_penalty = weighted_loss + [ math.sqrt( self.get_penalty( params ) ) ]
        return regularization_penalty