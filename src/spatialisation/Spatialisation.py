from fuzzyUtils import FuzzyRaster
import numpy as np


class Spatialisation:

    def __init__(self, raster, modifier=None):
        self.raster = raster
        if modifier:
            self.modifier = modifier

    def compute(self, *args):
        params = self.paramsCalc()
        return self._compute(*args, params)

    def _compute(self, *args):
        raise NotImplementedError

    def paramsCalc(self, *args):
        return self._paramsCalc(self, *args)

    def _paramsCalc(self, *args):
        raise NotImplementedError


class Proximity(Spatialisation):

    def __init__(self, raster, modifier=None):
        super().__init__(raster, modifier)

    def _paramsCalc(self):
        return  [(5, 1.0), (10, 0.0)]

    def _compute(self, fuzzyparams):

        computeraster = np.empty_like(self.raster)
        notnullcells = np.argwhere(self.raster != 0)

        # Définition de l'itérateur
        it = np.nditer(self.raster, flags=['multi_index'])
        while not it.finished:
            # Calcul de la distance au plus proche voisin
            computeraster[it.multi_index] = np.sqrt(
                np.min(np.sum(np.square(notnullcells - it.multi_index), axis=1)))
            it.iternext()

        out = FuzzyRaster.FuzzyRaster(
            array=computeraster,  # meta=self.raster.raster_meta,
            fuzzyfication_parameters=fuzzyparams)

        return out
