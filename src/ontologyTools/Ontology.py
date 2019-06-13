"""
Module contenant la classe principale du package, Ontology
"""


import rdflib
from .OntologyConstructor import OntologyConstructor


class Ontology:
    """
    Classe principale du package
    """

    default_ont_constr_strategy = OntologyConstructor

    def __init__(self, graph, ont_constr_strategy=None):
        self.graph = graph

        if ont_constr_strategy:
            self.ontology_constructor = ont_constr_strategy(self)
        else:
            self.ontology_constructor = self.default_ont_constr_strategy(self)

        # Construction des classes
        self._ontologyclasses = self.ontology_constructor.RdfClassesConstructor()
        # self.ontology_constructor.propertyConstructor()

    def append(self):
<<<<<<< HEAD
        pass
=======
        pass


if __name__ == "__main__":
    g = rdflib.Graph()
    result = g.parse("data/ontologies/relations_spatiales.owl")
    Ontology(g)
>>>>>>> 1913ee7853349e0bbb297608cd31b55de5d919fc
