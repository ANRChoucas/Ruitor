"""
Spatialisation
"""


import sys
from itertools import product

from rasterio.windows import Window

from fuzzyUtils import FuzzyRaster

import spatialisation.Metric
import spatialisation.Selector
import spatialisation.Modificator


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

            # confiance
            conf = indice.get("confiance", None)

            # relations spatiales
            spatialRelUri = indice["relationSpatiale"]["uri"]
            spatialRel = self.sro.get_from_iri(spatialRelUri)
            spatialRelDec = self.sro.treat_spatial_relation(spatialRel)
            #self.sro.decompose_spatial_relation(spatialRel)

            # Ajout des modifieurs
            modifieurs = []
            try:
                modifieursUri = indice["relationSpatiale"]["modifieurs"]
                for modUri in modifieursUri:
                    mod = self.sro.get_from_iri(modUri)
                    modDic = self.sro.get_modifier(mod)
                    if not modDic in modifieurs:
                        modifieurs.append(modDic)
            except KeyError:
                pass

            for k, v in spatialRelDec.items():
                v["selector"].update({"modifieurs": modifieurs})
            

            # traitement du site
            site = indice["site"]

            #print(indice)
            #import pdb; pdb.set_trace()

            yield Spatialisation(spatialRelDec, site, self.raster, self.zir, conf)

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

    def __init__(self, relationSpatiale, site, raster, zir, confiance=None):
        """
        Fonction d'initialisation de la classe Spatialisation
        """

        # Récupération des paramètres
        # Création du raster flou résultat
        self.raster = FuzzyRaster(raster=raster, window=zir)
        self.spaElms = self.SpatialisationElementSequence_init(
            relationSpatiale, site, confiance
        )

    def SpatialisationElementSequence_init(self, dic, site, confiance):
        spaSeq = SpatialisationElementSequence(confiance=confiance)

        for geom, rsaDic in product(site, dic.items()):
            gCounter, geometry = geom
            rsaName, rsaDec = rsaDic

            metric = getattr(
                sys.modules["spatialisation.Metric"], rsaDec["metric"]["name"]
            )
            selector = getattr(
                sys.modules["spatialisation.Selector"], rsaDec["selector"]["name"]
            )

            modifieurs = []
            for mod in rsaDec["selector"]["modifieurs"]:
                modObj = getattr(sys.modules["spatialisation.Modificator"], mod["name"])
                modifieurs.append(modObj)

            prms = {
                "metric_params": rsaDec["metric"]["kwargs"],
                "selector_params": rsaDec["selector"]["kwargs"],
                "modifiers": modifieurs,
            }

            if issubclass(metric, spatialisation.Metric.DeltaVal):
                prms["metric_params"]["values_raster"] = self.raster

            spaSeq[(gCounter, 0, rsaName)] = SpatialisationElement(
                self, geometry, metric, selector, **prms
            )

        return spaSeq

    def compute(self, *args):
        return self.spaElms.compute()

