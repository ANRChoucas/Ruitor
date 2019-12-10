"""
Module Selector
"""


class Selector:
    """
    Classe Selector
    """

    def __init__(self, context, modifiers, *args, **kwargs):
        self.context = context

        self.modifiers = [mod(self) for mod in modifiers]

    def compute(self, raster):
        ff_params = self.compute_ff_params()
        raster.fuzzyfication(ff_params)

        for mod in self.modifiers:
            raster.values = mod.modifing(raster.values)

    def compute_ff_params(self, *args):
        return self._compute_ff_params(*args)

    def _compute_ff_params(self, *args):
        raise NotImplementedError


class SelectorNull(Selector):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def compute(self, raster):
        pass


class CompareVal(Selector):
    def __init__(self, context, modifiers, value, *args, **kwargs):
        self.value = value
        super().__init__(context, modifiers, *args, **kwargs)

    def _compute_ff_params(self, *args):
        raise NotImplementedError


class InfVal(CompareVal):
    def __init__(self, context, modifiers, value, *args, **kwargs):
        super().__init__(context, modifiers, value, *args, **kwargs)

    def _compute_ff_params(self, *args):
        bsup = self.value + 50
        return [(self.value, 1.0), (bsup, 0.0)]


class SupVal(CompareVal):
    def __init__(self, context, modifiers, value, *args, **kwargs):
        super().__init__(context, modifiers, value, *args, **kwargs)

    def _compute_ff_params(self, *args):
        binf = self.value - 50
        return [(binf, 0.0), (self.value, 1.0)]


class EqVal(CompareVal):
    def __init__(self, context, modifiers, value, *args, **kwargs):
        super().__init__(context, modifiers, value, *args, **kwargs)

    def _compute_ff_params(self, *args):
        bsup = self.value + 60
        binf = self.value - 60
        return [(binf, 0.0), (self.value, 1.0), (bsup, 0.0)]


class SelectorX(Selector):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute_ff_params(self, *args):
        return [(0, 1.0), (10, 0.0)]


class SelectorX1(Selector):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute_ff_params(self, *args):
        return [(0, 0.0), (2, 1.0)]


class SelectorX2(Selector):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute_ff_params(self, *args):
        return [(0, 1.0), (2, 0.0)]


class SelectorX3(Selector):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute_ff_params(self, *args):
        return [(-5, 1.0), (5, 0.0)]
