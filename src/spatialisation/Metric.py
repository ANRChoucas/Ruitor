"""
Module metric
"""

import numpy as np
import scipy.ndimage


class Metric:
    """
    Classe Metric

    Classe générique permetant de définir des
    Métriques utilisées pour la spatialisation.
    La classe n'est pas destinée à être utilisée
    indépendanment, mais pour être un composant
    de Spatialisation.
    """

    def __init__(self, context):
        self.context = context
        self.raster = self.context.raster

    def compute(self, *args):
        # params = self.paramsCalc()
        self.raster.crisp_values = self._compute(*args)
        self.raster.values = self.raster.crisp_values

    def _compute(self, *args):
        raise NotImplementedError


class Nothing(Metric):
    def __init__(self, context):
        super().__init__(context)

    def _compute(self, *args):
        return self.raster.values


class Cell_Distance(Metric):
    """
    Classe Distance

    Hérite de la classe Metric. Destinée à calculer la
    distance à un point
    """

    def __init__(self, context):
        super().__init__(context)

    def _compute(self, *args):

        aa = np.zeros_like(self.raster.values)
        bb = self.raster.values + aa

        while np.min(bb) == 0:
            scipy.ndimage.binary_dilation(bb, output=aa)
            bb = bb + aa

        computeraster = (np.max(bb) - bb)

        return computeraster


class Distance(Metric):
    """
    Classe Distance

    Hérite de la classe Metric. Destinée à calculer la 
    distance à un point
    """

    def __init__(self, context):
        super().__init__(context)

    def _compute(self, *args):

        computeraster = np.empty_like(self.raster.values)
        notnullcells = np.argwhere(self.raster.values != 0)

        # Définition de l'itérateur
        it = np.nditer(self.raster.values, flags=['multi_index'])
        while not it.finished:
            # Calcul de la distance au plus proche voisin
            computeraster[it.multi_index] = np.sqrt(
                np.min(np.sum(np.square(notnullcells - it.multi_index), axis=1)))
            it.iternext()

        return computeraster
