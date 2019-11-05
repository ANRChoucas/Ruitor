"""
Module Selector
"""


class Selector:
    """
    Classe Selector
    """

    def __init__(self, context, *args, **kwargs):
        self.context = context

    def compute(self, raster):
        ff_params = self.compute_ff_params()
        raster.fuzzyfication(ff_params)

    def compute_ff_params(self, *args):
        return self._compute_ff_params(*args)

    def _compute_ff_params(self, *args):
        raise EnvironmentError


class SelectorNull(Selector):

    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def compute(self, raster):
        pass


class SelectorX(Selector):

    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute_ff_params(self, *args):
        return [(5, 1.0), (25, 0.0)]


class SelectorX2(Selector):

    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute_ff_params(self, *args):
        return [(160, 0.0), (180, 1.0), (200, 0.0)]


class SelectorX3(Selector):

    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute_ff_params(self, *args):
        return [(-5, 1.0), (5, 0.0)]
