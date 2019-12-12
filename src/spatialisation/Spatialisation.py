"""
Spatialisation
"""


import ast
import copy
import logging
import sys
from itertools import product

from rasterio.windows import Window
import spatialisation.Metric
import spatialisation.Modificator
import spatialisation.Selector
from fuzzyUtils import FuzzyRaster

from .SpatialisationElement import SpatialisationElement, SpatialisationElementSequence


LOGGER = logging.getLogger(__name__)


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

    def make_modifieurs(self, xml_modifieurs=None):
        """
        """
        # On vérifie si les modifieurs sont des modifieurs globaux
        # i.e. des sous-classes de "modifieur" dans l'ontologie ou
        # des paramètres

        outDic = {}

        if xml_modifieurs:
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
                        "%s is a %s, not a Modifieur or a Parameter"
                        % (modClass, modClass.is_a)
                    )

            outDic["Modifiers"] = ModList
            outDic["Parameters"] = ParamList

        return outDic

    def get_prms(self, spatial_relation):
        """
        """
        for k_spa, v_spa in spatial_relation.items():
            for k_cmp, v_cmp in v_spa.items():
                prms = v_cmp.pop("parameters")
                for prm in prms:
                    yield (k_spa, k_cmp), prm

    def add_parameters(self, spatial_relation_decomposition, xml_parameters):
        """
        Todo
        """

        spatial_relation = copy.deepcopy(spatial_relation_decomposition)

        for prm in self.get_prms(spatial_relation):
            k_rsa, k_comp = prm[0]
            prm_copy = prm[1].copy()
            default_values = spatial_relation[k_rsa][k_comp]['kwargs'].get(
                prm_copy["name"])

            try:
                uri_correspondances = (
                    i for i in xml_parameters if i.get("uri") == prm_copy["uri"]
                )

                xml_prm_value, *other_values = uri_correspondances

                # Traitement valeur:
                try:
                    casted_value = ast.literal_eval(xml_prm_value['value'])
                except TypeError:
                    casted_value = xml_prm_value

                prm_values = {
                    prm_copy['name']: casted_value,
                    **prm_copy['kwargs']
                }

                spatial_relation[k_rsa][k_comp]['kwargs'].update(prm_values)

                try:
                    xml_parameters.remove(xml_prm_value)
                except AttributeError:
                    pass

                if other_values:
                    # Message si other_values n'est pas nul
                    # i.e. s'il y a plus d'un paramètre possible
                    LOGGER.warning(
                        "Multiple values, I take the first: %s", xml_prm_value["value"])

                if xml_parameters:
                    # Message d'alerte si paramètres non utilisés
                    LOGGER.warning("Unused parameters %s", xml_parameters)

            except (TypeError, ValueError) as err:
                # Message si uri_correspondances est vide
                # ou si xml_parameters est vide
                # i.e. qu'aucun paramètre ne correspond ou que
                # les paramètres n'ont pas étés renseignés

                if default_values:
                    uri_correspondances = [default_values]
                    LOGGER.info(
                        "Parameter '%s' unset, I take the default value (%s)",
                        prm_copy["name"],
                        uri_correspondances[0])
                else:
                    LOGGER.critical("Parameter '%s'. No default value",
                                    prm_copy["name"])
                    raise err

        return spatial_relation

    def make_spatial_relation(self, spatial_rel_uri, xml_parameters=None):
        """
        Todo
        """
        spatial_rel = self.sro.get_from_iri(spatial_rel_uri)
        spatial_rel_dec = self.sro.treat_spatial_relation(spatial_rel)
        spatial_rel_dec = self.add_parameters(spatial_rel_dec, xml_parameters)
        return spatial_rel_dec

    def make_global_modifieurs(self, modifiers=None):
        """
        """
        global_modifiers = []

        if modifiers:
            for modifier in modifiers:
                mod_uri = modifier["uri"]
                mod = self.sro.get_from_iri(mod_uri)
                mod_dic = self.sro.get_modifier(mod)
                mod_value = modifier.get("value")
                if mod_value:
                    mod_dic["kwargs"]["value"] = ast.literal_eval(mod_value)
                global_modifiers.append(mod_dic)

        return global_modifiers

    def make_indice(self, indice):
        """
        """

        spatialisationParmsDic = {}

        # confiance
        conf = indice.get("confiance", None)

        # Ajout modifieurs si présents dans le xml
        xmlModList = indice["relationSpatiale"].get("modifieurs")
        extractModList = self.make_modifieurs(xmlModList)

        # Ajout modifieurs globaux
        global_modifiersList = extractModList.get("Modifiers")
        spatialisationParmsDic["global_modifiers"] = self.make_global_modifieurs(
            global_modifiersList
        )

        # décomposition relations spatiales
        spatialRelUri = indice["relationSpatiale"]["uri"]
        rsa_parameters = extractModList.get("Parameters")
        spatialRelDec = self.make_spatial_relation(
            spatialRelUri, rsa_parameters)
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
        self.spaElms = self.SpatialisationElementSequence_init(
            rsa, site, confiance)

        modifieurs = spatialisationParms.get("global_modifiers")
        self.modifiers = self.modifiers_init(modifieurs)

    def modifiers_init(self, modifiers):
        mod = []

        if modifiers:
            for modifier in modifiers:
                modCls = getattr(
                    sys.modules["spatialisation.Modificator"], modifier["name"]
                )
                modKargs = modifier.get("kwargs", {})
                modObj = modCls(self, **modKargs)
                mod.append(modObj)
        else:
            LOGGER.info("No modifiers")

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
                modObj = getattr(
                    sys.modules["spatialisation.Modificator"], mod["name"])
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
        temp_res = self.spaElms.compute()

        for mod in self.modifiers:
            temp_res = mod.modifing(temp_res)

        return temp_res
