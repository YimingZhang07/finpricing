from .curve import Curve


class SurvivalCurve(Curve):

    def get_survival_prob(self, t):
        """Get survival probability"""
        return self.get_factor(t)
