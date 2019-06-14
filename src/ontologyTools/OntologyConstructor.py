"""
Module contenant la classe destinée à transformer une ontologie RDFLib en un
ensemble d'objets. Cette classe est destinée à être appelée par une classe de 
type "Ontology".
"""


import rdflib
from rdflib import RDF, OWL
from .OwlClasses import OwlClass, OwlObjectProperties


class RDFDic(dict):

    def __init__(self, *args, **kwargs):

        graph = kwargs.get('graph')

        if graph:
            self.__dict__ = {}
            for i in graph:
                sub, prd, obj = i
                if sub in self.__dict__:
                    if prd in self.__dict__[sub]:
                        self.__dict__[sub][prd].append(obj)
                    else:
                        self.__dict__[sub].update({prd: [obj]})
                else:
                    self.__dict__[sub] = {prd: [obj]}
        else:
            self.__dict__ = {**kwargs}

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __contains__(self, item):
        if item in self.__dict__:
            return True

        for v in self.values():
            if item in v.keys():
                return True

        for _, v in self.items():
            for _, w in v.items():
                if item in w:
                    return True

        return False

    def __iter__(self):
        return iter(self.__dict__)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def get_subject(self, sub, default=None):
        return self.get(sub, default)

    def get_predicate(self, pred, default=None):
        return RDFDic(**{i: {pred: v.get(pred, default)} for i, v in self.items()})

    def get_object(self, obj):
        return RDFDic(**{i: {j: obj} for i, v in self.items() for j, w in v.items() if obj in w})

    def show(self):
        for i, v in self.items():
            print("\n", type(i), i)
            for j, w in v.items():
                print('\t', type(j), j)
                for x in w:
                    print('\t\t', type(x), x)


class OntologyConstructor:
    """
    Constructeur d'ontologies
    """

    def __init__(self, context):
        self.context = context
        self._ontologyclasses = {}

    def uriToName(self, uri, *args, **kwargs):

        uriDelimiter = kwargs.get("uriDelimiter", "#")

        swich = {
            rdflib.term.URIRef: lambda x: x.partition(uriDelimiter)[2],
            rdflib.term.BNode: lambda x: x.toPython()
        }

        return swich.get(type(uri), None)(uri)


class BasicOntologyConstructor(OntologyConstructor):
    """
    Constructeur d'ontologies
    """

    def __init__(self, context):
        super().__init__(context)

    def _subClassConstructor(self, uri):

        # Définition uri subClass
        rdf_subClassOf_uri = rdflib.term.URIRef(
            'http://www.w3.org/2000/01/rdf-schema#subClassOf')

        # Extraction des objets qui sont des sous-classes de la
        # classe traitée
        subclasses = self.context.graph.triples(
            (uri, rdf_subClassOf_uri, None))
        subclasses_instances = []

        for subclass in subclasses:
            # Récupération de l'uri des sous-classes
            subclass_uri = subclass[2]
            # Création du nom
            subclass_name = self.uriToName(subclass_uri)

            # Si la classe n'existe pas on la crée
            if subclass_name not in self._ontologyclasses:
                print(subclass_name)
                self.RdfClassConstructor(subclass_uri)

            # Ajout de la classe créée dans le dictionnaire des attribus
            if subclass_name not in subclasses_instances:
                subclass_instance = self._ontologyclasses.get(
                    subclass_name, None)
                subclasses_instances.append(subclass_instance)
            else:
                raise Exception("fuck")

            print("sub: %s" % (subclass,))

        return subclasses_instances

    def _supClassConstructor(self, cls):
        # Ajout des supclass
        for supClass in cls.supClasses:
            print(supClass)
            supClass.subClasses.append(cls)

    def RdfClassesConstructor(self):

        classes_dct = {}

        # On appele le constructeur de classe pour chaque classe de l'ontologie
        for triple in self.context.graph.triples((None, RDF.type, OWL.Class)):
            key, dct = self.RdfClassConstructor(triple[0])

            if key in classes_dct:
                # Fusion paramètres.
                raise Exception("Todo")
            else:
                classes_dct[key] = dct

        # Création des classes
        for i, v in classes_dct.items():
            # Création de la classe
            newclass = type(i, (OwlClass,), v)
            # Ajout de la classe dans le dictionnaire des classes
            self._ontologyclasses[i] = newclass

        return self._ontologyclasses

    def RdfClassConstructor(self, uri):

        # Nom de la classe
        name = self.uriToName(uri)

        # Attributs de la classe
        dct = {
            "uri": uri,
            "label": "Je suis le label",
            "subClasses": [],
            "supClasses": []
        }

        # subclasses_instances = self._subClassConstructor(uri)
        # dct["supClasses"].extend(subclasses_instances)

        # Ajout des supclass
        # self._supClassConstructor(newclass)

        return (name, dct)

    def propertyConstructor(self):

        self._ontologyproperties = {}

        rdf_subPropertyOf_uri = rdflib.term.URIRef(
            'http://www.w3.org/2000/01/rdf-schema#subPropertyOf')
        rdf_domain_uri = rdflib.term.URIRef(
            'http://www.w3.org/2000/01/rdf-schema#domain')
        rdf_range_uri = rdflib.term.URIRef(
            'http://www.w3.org/2000/01/rdf-schema#range')

        def _propertyConstructor(uri):

            name = self.uriToName(uri)

            dct = {
                "uri": uri,
                "subPropertyOf": set(),
                "supPropertyOf": set(),
                "domain": set(),
                "range": set()
            }

            # Range
            try:
                property_range = list(
                    zip(*self.context.context.graph.triples((uri, rdf_range_uri, None))))[-1]
            except IndexError:
                property_range = []
            property_range = {
                self._ontologyclasses[self.uriToName(i)] for i in property_range}
            dct["range"] = property_range

            # Domain
            try:
                property_domain = list(
                    zip(*self.context.graph.triples((uri, rdf_domain_uri, None))))[-1]
            except IndexError:
                property_domain = []
            property_domain = {
                self._ontologyclasses[self.uriToName(i)] for i in property_domain}
            dct["domain"] = property_domain

            # subProperty
            subproperties = self.context.graph.triples(
                (uri, rdf_subPropertyOf_uri, None))
            for subproperty in subproperties:
                subproperty_uri = subproperty[2]
                subproperty_name = self.uriToName(subproperty_uri)
                if not subproperty_name in self._ontologyproperties:
                    _propertyConstructor(subproperty_uri)
                dct["subPropertyOf"].add(
                    self._ontologyproperties[subproperty_name])

            # Class generation
            newproperty = type(name, (OwlObjectProperties,), dct)
            self._ontologyproperties[name] = newproperty

            # supProperty
            for supProperty in newproperty.subPropertyOf:
                supProperty.supPropertyOf.add(newproperty)

        for a in self.context.graph.triples((None, RDF.type, OWL.ObjectProperty)):
            _propertyConstructor(a[0])
