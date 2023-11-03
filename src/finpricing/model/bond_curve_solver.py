from typing import Union, List
from ..utils.date import Date
import datetime
from .fixed_bond_pricer import FixedBondPricer

class BondCurveAnalyticsHelper:
    def __init__(self, bonds) -> None:
        if isinstance(bonds, list):
            self.bonds = bonds
        else:
            raise TypeError('bonds must be a list of bonds.')
        self.bond_pricers = list(map(lambda x: FixedBondPricer(x), self.bonds))
        
        self._dirty_prices = None
        self._discount_curves = None
        self._survival_curves = None
        self._recovery_rates = None
        
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
        
    def get_bond_bases(self,
                     valuation_date: Union[datetime.date, Date],
                     basis_type: str='AdditiveZeroRates'):
        def f(i):
            return self.bond_pricers[i].solve_basis(
                valuation_date,
                self.dirty_prices[i],
                self.survival_curves[i],
                self.discount_curves[i],
                self.recovery_rates[i],
                basis_type
            )
        return [f(i) for i in range(len(self.bonds))]

class BondCurveSolver:
    def __init__(self) -> None:
        pass