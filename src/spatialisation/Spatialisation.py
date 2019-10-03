"""
Spatialisation
"""

from fuzzyUtils.FuzzyRaster import FuzzyRaster
from .Metric import Metric, Distance, Nothing
from .Selector import Selector

import rasterio
from rasterio.windows import Window
import numpy as np


class Spatialisation:
    """
    Classe spatialisation
    """

    def __init__(self, triplet, raster, zir=None):
        self.triplet = triplet

        self._init_raster(raster, zir)

        self._init_metric()
        self._init_selector()

    def _init_metric(self):
        self.metric = Distance(self)

    def _init_selector(self):
        self.selector = Selector(self)

    def _init_raster(self, raster, zir):

        wnd = self.set_zir(raster, zir)
        self.raster = FuzzyRaster(raster=raster, window=wnd)

    def set_zir(self, raster, zir, padding={'x': 10, 'y': 10}):
        """
        todo
        """

        if zir:
            # Calcul des numéros de ligne et de colonne correspondant aux
            # deux points de la bbox
            row_ind, col_ind = zip(*map(lambda x: raster.index(*x), zir))
            # Extraction du numéro de ligne/colonne minimum
            row_min, col_min = min(row_ind), min(col_ind)
            # Calcul du nombre de lignes/colonnes
            row_num = abs(max(row_ind) - row_min) + padding['x']
            col_num = abs(max(col_ind) - col_min) + padding['y']
            # Définition de la fenètre de travail
            return Window(col_min, row_min, col_num, row_num)
        else:
            return None

    def compute(self, *args):
        self.metric.compute()
        self.selector.compute()

        return self.raster
