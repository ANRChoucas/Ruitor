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

    def __getattr__(self, name):
        return self.ontho.__getattr__(name)

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

    def treat_spatial_relation(self, spatial_relation):

        logger.info("%s : extraction" % (spatial_relation,))

        outDic = {}

        try:
            rsas = self.get_atomic_spatial_relation(spatial_relation)
        except ValueError:
            rsas = (spatial_relation,)

        for rsa in rsas:
            metric = self.get_metric(rsa)
            selector = self.get_selector(rsa)
            outDic[rsa.name] = {"metric": metric, "selector": selector}

            logger.debug(
                "%s, metric : %s, selector : %s"
                % (rsa, metric["name"], selector["name"])
            )
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

    def _add_parameter(self, obj, dic):
        parametersDic = {**dic}

        try:
            metricParameter = self.get_parameter(obj)
            parametersDic.update({"parameters": metricParameter})
        except AttributeError:
            pass

        return parametersDic

    def get_metric(self, atomic_spatial_relation):
        metricList = atomic_spatial_relation.hasMetric
        metricDic = self._pythonAnotationParsing(metricList)
        metricOutDic = self._add_parameter(metricList, metricDic)
        return metricOutDic

    def get_selector(self, atomic_spatial_relation):
        selectorList = atomic_spatial_relation.hasSelector
        selectorDic = self._pythonAnotationParsing(selectorList)
        selectorOutrDic = self._add_parameter(selectorList, selectorDic)
        return selectorOutrDic

    def get_parameter(self, python_object):
        prmList = python_object.hasParameter

        outList = []
        for i in prmList:
            anot = self._pythonAnotationParsing(i)
            uri = i.get_iri(i)

            try:
                tp = i.pythonType[0]
            except IndexError:
                tp = None

            outList.append({"uri": uri, "type": tp, **anot})

        return outList


class ROOnto(Ontology):
    def __init__(self, path):
        logger.debug("ROO ontology made")
        super().__init__(path)
