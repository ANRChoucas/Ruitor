"""
Module contenant la classe principale du package, Ontology
"""


import rdflib
from . import OntologyConstructor


class Ontology:
    """
    Classe principale du package
    """

    default_ont_constr_strategy = OntologyConstructor.BasicOntologyConstructor

    def __init__(self, graph: rdflib.Graph, ont_constr_strategy=None):
        # Référence au graph rdflib
        self.graph = graph

        if ont_constr_strategy:
            self.ontology_constructor = ont_constr_strategy(self)
        else:
            self.ontology_constructor = self.default_ont_constr_strategy(self)

        # Construction des classes
        self._ontologyclasses = self.ontology_constructor.RdfClassesConstructor()
        # self.ontology_constructor.propertyConstructor()

    def append(self):
        pass
