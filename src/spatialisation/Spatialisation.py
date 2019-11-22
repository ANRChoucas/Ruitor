"""
Spatialisation
"""


import numpy as np
from itertools import product
from more_itertools import chunked
from rasterio import features
from rasterio.windows import Window

from fuzzyUtils import FuzzyRaster

from .Metric import Angle, Cell_Distance, DeltaVal, DAlt, Distance, Metric, Nothing
from .Selector import SelectorNull, SelectorX, SelectorX2, SelectorX3
from .SpatialisationElement import SpatialisationElement, SpatialisationElementSequence


class SpatialisationFactory:
    """
    """

    def __init__(self, spaParms, raster, sro):
        self.sro = sro
        self.indices = spaParms["indices"]
        self.raster = raster

        if "zir" in spaParms:
            self.zir = self.set_zir(self.raster, spaParms["zir"])
        else:
            self.zir = None

    def make_Spatialisation(self):

        for indice in self.indices:

            spatialRelationUri = indice["relationSpatiale"]["uri"]
            spatialRelation = self.sro.get_from_iri(spatialRelationUri)
            spatialRelationDecomp = self.sro.decompose_spatial_relation(spatialRelation)

            site = indice["site"]

            yield Spatialisation(spatialRelationDecomp, site, self.raster, self.zir)

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

    def _init_obj(self):
        pass

    def indice_parsing(self, indice, *args):
        pass

    def site_parsing(self, site):
        pass

    def cible_parsing(self, cible):
        pass


class Spatialisation:
    """
    Classe spatialisation

    Destinée à modéliser UN élément de localisation
    """

    def __init__(self, relationSpatiale, site, raster, zir):
        """
        Fonction d'initialisation de la classe Spatialisation
        """

        # Récupération des paramètres
        # Création du raster flou résultat
        self.raster = FuzzyRaster(raster=raster, window=zir)
        self.spaElms = self.SpatialisationElementSequence_init(relationSpatiale, site)

    def SpatialisationElementSequence_init(self, dic, site):
        spaSeq = SpatialisationElementSequence()

        for geom, rsaDic in product(site, dic.items()):
            gCounter, geometry = geom
            rsaName, rsaDec = rsaDic

            metric = globals()[rsaDec["metric"]["name"]]
            selector = globals()[rsaDec["selector"]["name"]]

            if issubclass(metric, DeltaVal):
                values_raster = self.raster
            else:
                values_raster = None

            spaSeq[(gCounter, 0, rsaName)] = SpatialisationElement(
                self, geometry, metric, selector, values_raster
            )

        return spaSeq

    def compute(self, *args):
        return self.spaElms.compute()

