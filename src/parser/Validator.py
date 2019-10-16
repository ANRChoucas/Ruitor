"""
Module validator
"""


from lxml import etree


class Validator:
    """
    Classe Validator
    """

    def __init__(self, context):
        self.context = context

    def validation(self, xmlfile, xsdfile):

        with open(xmlfile) as f:
            xml = etree.parse(f)

        with open(xsdfile) as f:
            ttSchema_doc = etree.parse(f)
            xsd = etree.XMLSchema(ttSchema_doc)

        return xsd.validate(xml)
