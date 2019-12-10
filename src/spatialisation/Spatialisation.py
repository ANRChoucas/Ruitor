"""
Spatialisation
"""


import sys
from itertools import product, chain

from rasterio.windows import Window

from fuzzyUtils import FuzzyRaster

import spatialisation.Metric
import spatialisation.Selector
import spatialisation.Modificator


from .SpatialisationElement import SpatialisationElement, SpatialisationElementSequence


class SpatialisationFactory:
    """
    """

    def __init__(self, spaParms, raster, sro, roo=None):
        # Lien vers les ontologies
        self.sro = sro
        self.roo = roo

        # extraction du xml pour les indices
        self.indices = spaParms["indices"]

        # raster
        self.raster = raster

        # Définition de la zir
        if "zir" in spaParms:
            self.zir = self.set_zir(self.raster, spaParms["zir"])
        else:
            self.zir = None

    def make_modifieurs(self, xml_modifieurs):
        # On vérifie si les modifieurs sont des modifieurs globaux
        # i.e. des sous-classes de "modifieur" dans l'ontologie ou
        # des paramètres

        outDic = {}
        ModList = []
        ParamList = []

        for mod in xml_modifieurs:

            mod_uri = mod["uri"]
            mod_value = mod.get("value")
            modClass = self.sro.get_from_iri(mod_uri)

            dic = {"uri": mod_uri}
            if mod_value:
                dic["value"] = mod_value

            # Si modifieur
            if self.sro.Modifieur in modClass.is_a:
                ModList.append(dic)
                # self.make_global_modifieurs(modClass, mod_value)
            # Si paramètre
            elif self.sro.Parametre in modClass.is_a:
                ParamList.append(dic)
                # self.make_parameters(modClass, mod_value)
            # Si ni l'un ni l'autre
            else:
                raise ValueError(
                    "%s is a %s, not a Modifieur or a Parametre"
                    % (modClass, modClass.is_a)
                )

        outDic["Modifiers"] = ModList
        outDic["Parameters"] = ParamList

        return outDic
        # metPrms = [v["metric"].get("parameters") for k, v in spatialRelDec.items()]
        # selPrms = [v["selector"].get("parameters") for k, v in spatialRelDec.items()]

        # ontoPrmsList = [i["uri"] for i in chain(metPrms, selPrms)]

        # Test

    def add_parameters(self, spatialRelDec, xml_parameters):

        for k_spa, v_spa in spatialRelDec.items():
            for k_cmp, v_cmp in v_spa.items():
                prms = v_cmp.get("parameters")
                for prm in prms:
                    xx = [i for i in xml_parameters if i.get("uri") == prm["uri"]]
                    # import pdb; pdb.set_trace()

        # if ontology_class.hasParameter:
        #     pass
        #     # print(ontology_class, mod_value)
        # else:
        #     pass

    def make_spatial_relation(self, spatial_rel_uri, xml_parameters=None):
        spatialRel = self.sro.get_from_iri(spatial_rel_uri)
        spatialRelDec = self.sro.treat_spatial_relation(spatialRel)
        # spatialRelDec = self.add_parameters(spatialRelDec, xml_parameters)
        return spatialRelDec

    def make_indice(self, indice):

        spatialisationParmsDic = {}

        # confiance
        conf = indice.get("confiance", None)

        # Ajout modifieurs si présents dans le xml
        xmlModList = indice["relationSpatiale"].get("modifieurs")
        if xmlModList:
            extractModList = self.make_modifieurs(xmlModList)
            # Ajout modifieurs globaux
            modifiersList = extractModList.get("Modifiers")
            global_modifiers = []
            for modifier in modifiersList:
                modUri = modifier["uri"]
                mod = self.sro.get_from_iri(modUri)
                modDic = self.sro.get_modifier(mod)
                global_modifiers.append(modDic)

            spatialisationParmsDic["global_modifiers"] = global_modifiers
        else:
            extractModList = None

        # décomposition relations spatiales
        spatialRelUri = indice["relationSpatiale"]["uri"]
        spatialRelDec = self.make_spatial_relation(spatialRelUri)
        spatialisationParmsDic["rsa"] = spatialRelDec

        # Ajout des modifieurs
        # modifieurs = []
        # try:
        #     modifieurs = indice["relationSpatiale"]["modifieurs"]
        #     for modif in modifieurs:
        #         import pdb; pdb.set_trace()
        #         modUri = modif['uri']
        #         mod = self.sro.get_from_iri(modUri)
        #         modDic = self.sro.get_modifier(mod)
        #         if not modDic in modifieurs:
        #             modifieurs.append(modDic)
        # except KeyError:
        #     pass

        for k, v in spatialisationParmsDic["rsa"].items():
            v["selector"].update({"modifieurs": []})

        # Ajout site
        site = indice["site"]

        return Spatialisation(spatialisationParmsDic, site, self.raster, self.zir, conf)

    def make_Spatialisation(self):
        for indice in self.indices:
            yield self.make_indice(indice)

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

    def __init__(self, spatialisationParms, site, raster, zir, confiance=None):
        """
        Fonction d'initialisation de la classe Spatialisation
        """

        # Récupération des paramètres
        # Création du raster flou résultat
        self.raster = FuzzyRaster(raster=raster, window=zir)

        rsa = spatialisationParms["rsa"]
        self.spaElms = self.SpatialisationElementSequence_init(rsa, site, confiance)

        modifieurs = spatialisationParms.get("global_modifiers")
        self.modifiers = self.modifiers_init(modifieurs)

    def modifiers_init(self, modifiers):
        mod = []

        try:
            for modifier in modifiers:
                modCls = getattr(sys.modules["spatialisation.Modificator"], modifier["name"])
                modKargs = modifier.get("kwargs", {})
                modObj = modCls(self, **modKargs)
                mod.append(modObj)
        except TypeError:
            pass

        return mod

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
        tempRes = self.spaElms.compute()

        for mod in self.modifiers:
            tempRes = mod.modifing(tempRes)
            
        return tempRes

