"""
Module Selector
"""
from fuzzyUtils.FuzzyRaster import FuzzyRaster


class Selector:
    """
    Classe Selector
    """

    def __init__(self, context):
        self.context = context

    def compute(self):
        ff_params = self.compute_ff_params()
        self.context.raster.fuzzyfication(ff_params)

    def compute_ff_params(self, *args):
        return self._compute_ff_params(*args)

    def _compute_ff_params(self, *args):
        return [(50, 0.0), (100, 1.0), (150, 0.0)]
