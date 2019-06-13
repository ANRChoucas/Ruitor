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


class OwlThing(object):

    uri = None


class OwlNamedEntity(OwlThing):
    pass


class OwlObjectProperties(OwlThing):
    pass


class OwlClass(OwlThing):
    pass
    # subClassOf = []
