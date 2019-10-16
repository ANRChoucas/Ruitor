"""
Module Selector
"""


class Selector:
    """
    Classe Selector
    """

    def __init__(self, context):
        self.context = context

    def compute(self, raster):
        ff_params = self.compute_ff_params()
        raster.fuzzyfication(ff_params)

    def compute_ff_params(self, *args):
        return self._compute_ff_params(*args)

    def _compute_ff_params(self, *args):
        return [(0, 1.0), (45, 0.0), (315, 0.0), (360, 1.0)]
