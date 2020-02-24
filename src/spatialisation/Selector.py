"""
Module Selector
"""


class Selector:
    """
    Classe Selector
    """

    def __init__(self, context, modifiers):
        self.context = context
        self.modifiers = [mod(self) for mod in modifiers]

    def compute(self, raster):
        """
        Todo
        """
        ff_params = self.compute_ff_params()
        raster.fuzzyfication(ff_params)

        for mod in self.modifiers:
            raster.values = mod.modifing(raster.values)

    def compute_ff_params(self, *args):
        """
        Todo
        """
        return self._compute_ff_params(*args)

    def _compute_ff_params(self, *args):
        raise NotImplementedError


class SelectorNull(Selector):
    """
    Todo
    """

    def compute(self, raster):
        pass


class CompareVal(Selector):
    """
    Todo
    """

    def __init__(self, context, modifiers, value, *args, **kwargs):
        self.value = value
        super().__init__(context, modifiers, *args, **kwargs)

    def _compute_ff_params(self, *args):
        raise NotImplementedError


class InfVal(CompareVal):
    """
    Todo
    """

    def _compute_ff_params(self, *args):
        bsup = self.value

        return [(self.value - 5, 1.0), (bsup, 0.0)]


class SupVal(CompareVal):
    """
    Todo
    """

    def _compute_ff_params(self, *args):
        binf = self.value - 25
        return [(binf, 0.0), (self.value, 1.0)]


class EqVal(CompareVal):
    """
    Todo
    """

    def __init__(self, *args, **kwargs):
        self.step = kwargs.pop("step", 10)
        super().__init__(*args, **kwargs)

    def _compute_ff_params(self, *args, **kwargs):
        bsup = self.value + self.step
        binf = self.value - self.step
        return [(binf, 0.0), (self.value, 1.0), (bsup, 0.0)]


class SelectorX(Selector):
    """
    Todo
    """

    def _compute_ff_params(self, *args):
        return [(50, 1.0), (250, 0.0)]


class SelectorX1(Selector):
    """
    Todo
    """

    def _compute_ff_params(self, *args):
        return [(0, 0.0), (2, 1.0)]


class SelectorX2(Selector):
    """
    Todo
    """

    def _compute_ff_params(self, *args):
        return [(0, 1.0), (2, 0.0)]


class SelectorX3(Selector):
    """
    Todo
    """

    def _compute_ff_params(self, *args):
        return [(-5, 1.0), (5, 0.0)]


class SelectorX4(Selector):
    def _compute_ff_params(self, *args):
        return [(25, 0.0), (50, 1.0), (150, 1.0), (300, 0.0)]


class SelectorX5(Selector):
    def _compute_ff_params(self, *args):
        return [(3600 * 0.5, 0.0), (3600 * 2, 1.0), (3600 * 5, 1.0), (3600 * 12, 0.0)]


class DistHuez(Selector):
    def _compute_ff_params(self, *args):
        return [(7000, 1.0), (10000, 0.0)]


class Dist2alpes(Selector):
    def _compute_ff_params(self, *args):
        return [(9000, 1.0), (12000, 0.0)]


class DistOz(Selector):
    def _compute_ff_params(self, *args):
        return [(9000, 1.0), (12000, 0.0)]


class DistVaujany(Selector):
    def _compute_ff_params(self, *args):
        return [(12000, 1.0), (15000, 0.0)]


class DistOrnon(Selector):
    def _compute_ff_params(self, *args):
        return [(6000, 1.0), (9000, 0.0)]


class DistChamrousse(Selector):
    def _compute_ff_params(self, *args):
        return [(14000, 1.0), (28000, 0.0)]


class DistReculas(Selector):
    def _compute_ff_params(self, *args):
        return [(4500, 1.0), (8000, 0.0)]


class DistGrandserre(Selector):
    def _compute_ff_params(self, *args):
        return [(14000, 1.0), (28000, 0.0)]


class DistAuris(Selector):
    def _compute_ff_params(self, *args):
        return [(4000, 1.0), (6000, 0.0)]

class Direction(Selector):
    def _compute_ff_params(self, *args):
        return [(0, 1.0), (2500, 0.0)]