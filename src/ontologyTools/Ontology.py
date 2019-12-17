"""
Module contenant la classe principale du package, Ontology
"""

import logging
import ast
from owlready2 import get_ontology

LOGGER = logging.getLogger(__name__)


class Ontology:
    """
    Classe principale du package
    """

    def __init__(self, path):
        self.ontho = get_ontology(path)
        self.ontho.load()
        LOGGER.info("ontology namespace: %s", self.ontho.base_iri)

    def __getattr__(self, name):
        return self.ontho.__getattr__(name)

    def get_from_iri(self, uri):
        """
        """
        try:
            return self.ontho.search_one(iri=uri)
        except ValueError:
            LOGGER.debug("%s unknown", uri)

    def _pythonAnotationParsing(self, owlcls):
        """
        """
        python_name = owlcls.pythonName[0]
        try:
            python_parameter = ast.literal_eval(owlcls.pythonParameter[0])
        except IndexError:
            python_parameter = {}
        out_dic = {"name": python_name, "kwargs": python_parameter}

        return out_dic


class SROnto(Ontology):
    """
    Classe SROnto
    """

    def __init__(self, path):
        LOGGER.debug("SRO ontology made")
        super().__init__(path)

    def treat_spatial_relation(self, spatial_relation):
        """
        """

        LOGGER.info("%s : extraction", spatial_relation)

        try:
            rsas = self.get_atomic_spatial_relations(spatial_relation)
        except ValueError:
            rsas = (spatial_relation,)

        rsa_gen = (self.treat_rsa(rsa) for rsa in rsas)
        out_dic = {k: v for k, v in rsa_gen}
        return out_dic

    def treat_rsa(self, spatial_atomic_relation):

        metric = self.get_metric(spatial_atomic_relation)
        selector = self.get_selector(spatial_atomic_relation)
        rasterizer = self.get_rasterizer(spatial_atomic_relation)
        try:
            modifier = self.get_modifier(spatial_atomic_relation.hasModifieur)
        except AttributeError:
            modifier = None

        out_dic = {
            "metric": metric,
            "selector": selector,
            "rasterizer": rasterizer,
        }

        if modifier:
            out_dic["modifieur"] = modifier
            name = modifier.get("name")
        else:
            name = "No modifier"

        LOGGER.debug(
            "%s, metric: %s, selector: %s, rasterizer: %s, modifiers: %s",
            spatial_atomic_relation,
            metric["name"],
            selector["name"],
            rasterizer["name"],
            name,
        )

        return (spatial_atomic_relation.name, out_dic)

    def get_atomic_spatial_relations(self, spatial_relation):
        """
        """
        rsa = spatial_relation.hasRelationSpatialeAtomique
        if not rsa:
            LOGGER.error("No hasRelationSpatialeAtomique for %s", spatial_relation)
            raise ValueError
        return rsa

    def get_modifier(self, modifier):
        """
        """
        modifier_dic = self._pythonAnotationParsing(modifier)
        modifier_out_dic = self._add_parameter(modifier, modifier_dic)
        return modifier_out_dic
   
    def _add_parameter(self, obj, dic):
        parameters_dic = {**dic}

        try:
            metric_parameter = self.get_parameter(obj)
            parameters_dic.update({"parameters": metric_parameter})
        except AttributeError:
            pass

        return parameters_dic

    def get_rasterizer(self, atomic_spatial_relation):
        rasterizer = atomic_spatial_relation.hasRasterizer
        rasterizer_dic = self._pythonAnotationParsing(rasterizer)
        rasterizer_out_dic = self._add_parameter(rasterizer, rasterizer_dic)
        return rasterizer_out_dic

    def get_metric(self, atomic_spatial_relation):
        """
        """
        metric_list = atomic_spatial_relation.hasMetric
        metric_dic = self._pythonAnotationParsing(metric_list)
        metric_out_dic = self._add_parameter(metric_list, metric_dic)
        return metric_out_dic

    def get_selector(self, atomic_spatial_relation):
        """
        """
        selector_list = atomic_spatial_relation.hasSelector
        selector_dic = self._pythonAnotationParsing(selector_list)
        selector_outr_dic = self._add_parameter(selector_list, selector_dic)
        return selector_outr_dic

    def get_parameter(self, python_object):
        """
        """
        prm_list = python_object.hasParameter
        out_list = []
        for i in prm_list:
            anot = self._pythonAnotationParsing(i)
            uri = i.get_iri(i)
            out_list.append({"uri": uri, **anot})
        return out_list


class ROOnto(Ontology):
    """
    Classe ROOnto
    """

    def __init__(self, path):
        LOGGER.debug("ROO ontology made")
        super().__init__(path)
