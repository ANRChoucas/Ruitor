"""
Module metric
"""

from fuzzyUtils import FuzzyRaster

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
        self.values = self.context.raster.values

    def compute(self, *args):
        # params = self.paramsCalc()
        self.values = self._compute(*args)
        return FuzzyRaster(array=self.values, meta=self.context.raster.raster_meta)

    def _compute(self, *args):
        raise NotImplementedError


class Nothing(Metric):
    def __init__(self, context):
        super().__init__(context)

    def _compute(self, *args):
        return self.values


class Cell_Distance(Metric):
    """
    Classe Distance

    Hérite de la classe Metric. Destinée à calculer la
    distance à un point
    """

    default_structure = scipy.ndimage.generate_binary_structure(3, 1)

    def __init__(self, context, structure=None):
        super().__init__(context)
        # Définition du voisinage
        if structure:
            self.structure = structure
        else:
            self.structure = self.default_structure

    def _compute(self, *args):

        aa = np.zeros_like(self.values)
        bb = self.values + aa

        while np.min(bb) == 0:
            scipy.ndimage.binary_dilation(
                bb, structure=self.structure, output=aa)
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

        computeraster = np.empty_like(self.values)
        notnullcells = np.argwhere(self.values != 0)

        # Définition de l'itérateur
        it = np.nditer(self.values, flags=['multi_index'])
        while not it.finished:
            # Calcul de la distance au plus proche voisin
            computeraster[it.multi_index] = np.sqrt(
                np.min(np.sum(np.square(notnullcells - it.multi_index), axis=1)))
            it.iternext()

        return computeraster


class Angle(Metric):
    """
    Classe Angle

    Hérite de la classe Metric. Destinée à calculer un angle.
    """

    def __init__(self, context):
        super().__init__(context)

    def _compute(self, angle=0, *args):

        computeraster = np.empty_like(self.values)
        # Calcule l'angle par rapport à la première coordonée
        # de l'objet. A refaire
        notnullcells = np.argwhere(self.values != 0)[0]

        ang = angle - 90

        # Définition de l'itérateur
        it = np.nditer(self.values, flags=['multi_index'])
        while not it.finished:
            computeraster[it.multi_index] = np.arctan2(
                *np.split((notnullcells - it.multi_index)[1:], 2))
            it.iternext()

        computeraster = (np.degrees(computeraster) + ang) % 360

        return computeraster


class DAlt(Metric):
    """
    Classe DAlt

    Hérite de la classe Metric. Destinée à calculer la 
    différence d'altitude
    """

    def __init__(self, context):
        super().__init__(context)

    def _compute(self, *args):

        computeraster = np.empty_like(self.values)
        notnullcells = np.argwhere(self.values != 0)

        # Todo

        return computeraster
