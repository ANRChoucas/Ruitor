"""
Spatialisation
"""


import numpy as np
from more_itertools import chunked
from rasterio import features
from rasterio.windows import Window

from fuzzyUtils import FuzzyRaster

from .Metric import Angle, Cell_Distance, DAlt, Distance, Metric, Nothing
from .Selector import SelectorNull, SelectorX, SelectorX2, SelectorX3
from .SpatialisationElement import SpatialisationElement, SpatialisationElementSequence


class Spatialisation:
    """
    Classe spatialisation

    Destinée à modéliser UN élément de localisation
    """

    def __init__(self, parameters, raster):
        """
        Fonction d'initialisation de la classe Spatialisation
        """

        # Récupération des paramètres
        self.params = parameters
        self.spaElms = SpatialisationElementSequence()

        # Définition zone initiale de recherche
        if "zir" in self.params:
            self.zir = self.set_zir(raster, self.params["zir"])
        else:
            self.zir = None

        # Création du raster flou résultat
        self.raster = FuzzyRaster(raster=raster, window=self.zir)

        self.indice_parsing(self.params["indices"])

    def _init_obj(self):
        pass

    def indice_parsing(self, indice, *args):
        """
        """

        indice = indice[0]

        site_counter = 0

        # tmpdir = mkdtemp()

        for geom in indice["site"]:
            # filename = path.join(tmpdir, 'obj_%s.dat' % site_counter)
            # zi = np.memmap(filename, mode='w+', dtype=self.raster.values.dtype, shape=self.raster.values.shape)

            self.spaElms[(site_counter, 0, 0)] = SpatialisationElement(
                self, geom, metric=Angle, selector=SelectorX2
            )
            self.spaElms[(site_counter, 0, 1)] = SpatialisationElement(
                self, geom, metric=Distance, selector=SelectorX
            )
            self.spaElms[(site_counter, 0, 2)] = SpatialisationElement(
                self, geom, metric=DAlt, selector=SelectorX3, values_raster=self.raster
            )

            site_counter += 1

    def site_parsing(self, site):
        pass

    def cible_parsing(self, cible):
        pass

    def compute(self, *args):
        return self.spaElms.compute()

    def set_zir(self, raster, zir, *args, **kwargs):
        """
        Crée une fenêtre rasterio à partir d'une liste de 
        deux coordonnées.

        Permet de travailler sur une petite zone en lieu et 
        place de tout le raster.

        Possibilité de spécifier un padding
        """
        # Spécification du padding
        if "padding" in kwargs:
            padding = kwargs["padding"]
        else:
            padding = {"x": 10, "y": 10}
        # Calcul Zir
        # Calcul des numéros de ligne et de colonne correspondant aux
        # deux points de la bbox
        row_ind, col_ind = zip(*map(lambda x: raster.index(*x), zir))
        # Extraction du numéro de ligne/colonne minimum
        row_min, col_min = min(row_ind), min(col_ind)
        # Calcul du nombre de lignes/colonnes
        row_num = abs(max(row_ind) - row_min) + padding["x"]
        col_num = abs(max(col_ind) - col_min) + padding["y"]
        # Définition de la fenêtre de travail
        return Window(col_min, row_min, col_num, row_num)
