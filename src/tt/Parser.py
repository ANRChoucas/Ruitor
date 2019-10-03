"""
Parser xml arguments
"""

from lxml import etree


class Parser(object):
    """
    Classe Parser
    """

    def __init__(self, file, schema=None):
        """
        Fonction d'initialisation
        """

        if schema:
            with open(schema) as f:
                ttSchema_doc = etree.parse(f)
                self.xmlSchema = etree.XMLSchema(ttSchema_doc)

        with open(file) as f:
            self.xml = etree.parse(f)

    def validation(self):
        self.xmlSchema.validate(self.xml)

    @property
    def zir(self):
        """
        Zone initiale de recherche au format Bbox.
        zir = [[ x1, y1], [x2, y2]] 
        """
        zir_coords = self.xml.xpath("/hypothèse/zir/boundedBy/Box/coord")
        bbox = [[float(i.text) for i in coord.getchildren()]
                for coord in zir_coords]
        return bbox
