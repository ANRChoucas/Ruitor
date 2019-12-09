"""
Parser xml arguments
"""


from bs4 import BeautifulSoup
from .Validator import Validator
from .GeometryParser import GeometryParser


class Parser:
    """
    Classe Parser
    """

    default_validator_strategy = Validator
    default_geometryParser_strategy = GeometryParser

    def __init__(
        self, file, schema=None, validator_strategy=None, geometryParser_strategy=None
    ):
        """
        Fonction d'initialisation
        """

        if validator_strategy:
            self.validator = validator_strategy(self)
        else:
            self.validator = self.default_validator_strategy(self)

        if geometryParser_strategy:
            self.geometryParser = geometryParser_strategy(self)
        else:
            self.geometryParser = self.default_geometryParser_strategy(self)

        self._xml_dict = {}

        with open(file) as f:
            self.xml = BeautifulSoup(f, "xml")

        if schema:
            print(self.validation(file, schema))

        self.parse()

    def parse(self):

        # Calcul Zir
        if self.xml.zir:
            self._xml_dict["zir"] = self.parse_zir(self.xml.zir)

        # Parsage indices
        self._xml_dict["indices"] = self.parse_indices(self.xml.indices)

    @property
    def values(self):
        return self._xml_dict

    def validation(self, file, schema):
        return self.validator.validation(file, schema)

    def parse_indices(self, indices_xml, **kwargs):

        indice_key = kwargs.get("indice_key", "indice")

        indices = []

        for i in indices_xml.children:
            if i.name == indice_key:
                indices.append(self.parse_indice(i))

        return indices

    def parse_indice(self, indice_xml):

        indice_dict = {}

        confiance = self.parse_confiance(indice_xml.attrs.get("confiance"))
        relSpa = self.parse_relationSpatiale(indice_xml.relationSpatiale)
        cible = self.parse_cible(indice_xml.cible)
        site = self.parse_site(indice_xml.site)

        indice_dict["confiance"] = confiance
        indice_dict["relationSpatiale"] = relSpa
        indice_dict["cible"] = cible
        indice_dict["site"] = site

        return indice_dict

    def parse_cible(self, cible_xml):
        return "Nothing"

    def parse_relationSpatiale(self, relSpa_xml):
        relSpaDic = {}
        relSpaUri = relSpa_xml.attrs.get("about")

        relSpaDic["uri"] = relSpaUri

        for child in relSpa_xml.children:
            if child.name == "modifieurs":
                relSpaDic["modifieurs"] = self.parse_modifieur(child)

        return relSpaDic

    def parse_modifieur(self, mod_xml):
        outList = []
        for i in mod_xml:
            if i.name == "modifieur":
                dic = {}
                uri = i.attrs.get("about")
                dic["uri"] = uri
                value = i.string 
                if value:
                    dic["value"] = value
                outList.append(dic)
        return outList

    def parse_site(self, site_xml, **kwargs):

        site_key = kwargs.get("site_key", "featureMember")

        geom_counter = 0
        for child in site_xml.children:
            if child.name == site_key:
                yield (geom_counter, self.parse_geometry(child))
                geom_counter += 1

    def parse_geometry(self, geometry_gml):
        return self.geometryParser.parse_geometry(geometry_gml)

    def parse_confiance(self, confiance):
        if confiance:
            return float(confiance)
        else:
            return 1.0

    def parse_zir(self, zir_xml):
        """
        Zone initiale de recherche au format Bbox.
        zir = [[x1, y1], [x2, y2]] 
        """

        zir_coords = zir_xml.Envelope
        # Calcul Zir
        lc = zir_coords.lowerCorner
        up = zir_coords.upperCorner
        bbox = [[float(j) for j in i.string.split()] for i in (lc, up)]

        return bbox

    def __str__(self):
        return self._xml_dict
