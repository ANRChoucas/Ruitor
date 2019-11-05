"""
Module contenant un ensemble de classes telles que définies par
les normes owl et rdf
"""


class _RDFMeta(type):
    def __new__(cls, name, bases, dct):
        def __init__(cls, graph):
            super(bases[0], cls).__init__(graph)

        dct["__init__"] = __init__

        return super().__new__(cls, name, bases, dct)


class RdfRessource(object):
    uri = None

    def __str__(self):
        try:
            return self.label
        except AttributeError:
            return "%s" % (__class__.__name__)


class OwlNamedEntity(RdfRessource):
    pass


class OwlObjectProperties(RdfRessource):
    pass


class OwlClass(RdfRessource):
    pass


class OwlDataType(RdfRessource):
    pass


class OwlAnnotation(RdfRessource):
    pass


class OwlOntology(RdfRessource):
    pass
