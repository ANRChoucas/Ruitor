"""
Module contenant la classe principale du package, Ontology
"""

import logging
import ast
from owlready2 import get_ontology

logger = logging.getLogger(__name__)


class Ontology:
    """
    Classe principale du package
    """

    def __init__(self, path):
        self.ontho = get_ontology(path)
        self.ontho.load()
        logger.info("ontology namespace: %s" % self.ontho.base_iri)

    def get_from_iri(self, uri):
        try:
            return self.ontho.search_one(iri=uri)
        except:
            logger.debug("%s unknown" % (uri,))

    def _pythonAnotationParsing(self, owlcls):
        """
        """
        pythonName = owlcls.pythonName[0]
        try:
            pythonParameter = ast.literal_eval(owlcls.pythonParameter[0])
        except IndexError:
            pythonParameter = {}
        outDic = {"name": pythonName, "kwargs": pythonParameter}

        return outDic


class SROnto(Ontology):
    def __init__(self, path):
        logger.debug("SRO ontology made")
        super().__init__(path)

    def decompose_spatial_relation(self, spatial_relation):

        logger.info("%s : extraction" % (spatial_relation,))

        outDic = {}

        for rsa in self.get_atomic_spatial_relation(spatial_relation):
            metric = self.get_metric(rsa)
            selector = self.get_selector(rsa)
            outDic[rsa.name] = {"metric": metric, "selector": selector}

            logger.debug("%s metric : %s" % (rsa, metric["name"]))
            logger.debug("%s selector : %s" % (rsa, selector["name"]))
        return outDic

    def get_atomic_spatial_relation(self, spatial_relation):
        rsa = spatial_relation.hasRelationSpatialeAtomique
        if not rsa:
            raise ValueError(
                "No hasRelationSpatialeAtomique for %s" % (spatial_relation,)
            )
        return rsa

    def get_modifier(self, modifier):
        return self._pythonAnotationParsing(modifier)

    def get_metric(self, atomic_spatial_relation):
        metricList = atomic_spatial_relation.hasMetric
        return self._pythonAnotationParsing(metricList)

    def get_selector(self, atomic_spatial_relation):
        selectorList = atomic_spatial_relation.hasSelector
        return self._pythonAnotationParsing(selectorList)


class ROOnto(Ontology):
    def __init__(self, path):
        logger.debug("ROO ontology made")
        super().__init__(path)
