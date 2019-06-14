import rdflib
from ontologyTools import Ontology


if __name__ == "__main__":
    g = rdflib.Graph()
    result = g.parse("data/ontologies/relations_spatiales.owl")
    aa = Ontology.Ontology(g)