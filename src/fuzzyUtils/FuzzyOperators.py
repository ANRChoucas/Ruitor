"""Module FuzzyOperators. 

Contient la classe générique FuzzyOperators et ses
spécialisations. 


La classe FuzzyOperators est destinée à être l’ancêtre de toutes les
classes implémentant les opérateurs inter-ensemble.

Pour créer de nouveaux opérateurs il convient de créer une classe
héritant de FuzzyOperators et surchargeant les méthodes privées
"_norm" et "_conorm"

:Example:
# Création de nouveaux opérateurs

>>> class MyOperators(FuzzyOperators):
>>> 
>>>     def __init__(self, context):
>>>         super().__init__(context)
>>> 
>>>     def _norm(self, other):
>>>         return self.context.values * other.values
>>> 
>>>     def _conorm(self, other):
>>>         return self.context.values + other.values - self.context.values * other.values

"""

import numpy as np


class FuzzyOperators:
    """Classe d'opérateurs flous générique

    Cette classe défini l'ensemble des méthodes permettant de faire
    des union et des intersections entre rasters flous.

    Cette classe n'est pas destinée à être utilisée directement, elle
    sert d’ancêtre aux classes implémentant les t-normes et les
    t-conormes.

    """

    def __init__(self, context):
        self.context = context

    def _check_operators(self, other):
        if type(self.context.fuzzy_operators) != type(other.fuzzy_operators):
            raise ValueError("Incompatibles Fuzzy Operators")

    def __str__(self):
        return "fuzzy operator : %s" % (self.__class__.__name__)

    def norm(self, other):
        """
        Calcule la norme de deux ensembles flous
        """

        self._check_operators(other)
        # Récupération des valeurs 'nodata'
        nodata_self = self.context.raster_meta["nodata"]
        notada_other = other.raster_meta["nodata"]
        # Calcul de la norme
        norm = self._norm(other)
        # Ajout des 'nodata' dans le cas ou il manque des valeurs
        nodata_vals = np.logical_or(
            self.context.values == nodata_self, other.values == notada_other
        )
        norm[nodata_vals] = nodata_self
        return norm

    def conorm(self, other):
        """
        Calcule la conorme de deux ensembles flous
        """

        self._check_operators(other)
        # Récupération des valeurs 'nodata'
        nodata_self = self.context.raster_meta["nodata"]
        notada_other = other.raster_meta["nodata"]
        # Calcul de la conorme
        conorm = self._conorm(other)
        # Ajout des 'nodata' dans le cas ou il manque des valeurs
        nodata_vals = np.logical_or(
            self.context.values == nodata_self, other.values == notada_other
        )
        conorm[nodata_vals] = nodata_self
        return conorm

    def _norm(self, other):
        raise NotImplementedError("No t-norm defined")

    def _conorm(self, other):
        raise NotImplementedError("No t-norm defined")


class ZadehOperators(FuzzyOperators):
    """
    Opérateurs flous tels que formalisés par Zadeh

    t-norme(a,b) = min(a,b)
    t-conorme(a,b) = max(a,b)
    """

    def __init__(self, context):
        super().__init__(context)

    def _norm(self, other):
        return np.minimum(self.context.values, other.values)

    def _conorm(self, other):
        return np.maximum(self.context.values, other.values)


class LukasiewiczOperators(FuzzyOperators):
    """
    Opérateurs flous tels que formalisés par Lukasiewicz

    t-norme(a,b) = max(a+b-1, 0)
    t-conorme(a,b) = min(a+b, 1)
    """

    def __init__(self, context):
        super().__init__(context)

    def _norm(self, other):
        return np.maximum(self.context.values + other.values - 1.0, 0.0)

    def _conorm(self, other):
        return np.minimum(self.context.values + other.values, 1.0)


class ProbabilityOperators(FuzzyOperators):
    """
    Opérateurs probabilistes flous

    t-norme(a,b) = a*b
    t-conorme(a,b) = a+b-a*b
    """

    def __init__(self, context):
        super().__init__(context)

    def _norm(self, other):
        return self.context.values * other.values

    def _conorm(self, other):
        return self.context.values + other.values - self.context.values * other.values


class NilpotentOperators(FuzzyOperators):
    """
    Opérateurs nilpotents

    t-norme(a,b) = min(a,b) si a+b > 1; 0 sinon
    t-conorme(a,b) = max(a,b) si a+b < 1; 1 sinon
    """

    def __init__(self, context):
        super().__init__(context)

    def _norm(self, other):
        # Définirion de l'array a renvoyer
        res_array = np.empty_like(self.context.values)
        # Construction de l'array test: True si a + b > 1
        test_arr = self.context.values + other.values > 1
        # 0 si a+b <= 0
        res_array[~test_arr] = 0
        # min(a,b) si a+b > 1
        res_array[test_arr] = np.minimum(self.context.values, other.values)[test_arr]

        return res_array

    def _conorm(self, other):
        # Définirion de l'array a renvoyer
        res_array = np.empty_like(self.context.values)
        # Construction de l'array test: True si a + b < 1
        test_arr = self.context.values + other.values < 1
        # 1 si a + b >= 1
        res_array[~test_arr] = 1
        # max(a,b) si a+b < 1
        res_array[test_arr] = np.maximum(self.context.values, other.values)[test_arr]

        return res_array


class DrasticOperators(FuzzyOperators):
    """
    Opérateurs drastiques

    t-norme(a,b) = b si a = 1; a si b = 1; 0 sinon
    t-conorme(a,b) = b si a = 0; a si b = 0; 1 sinon
    """

    def __init__(self, context):
        super().__init__(context)

    def _norm(self, other):
        # Définirion de l'array a renvoyer
        # 0 si a != 1 ou b != 1 i.e. tous les autres cas
        res_array = np.zeros_like(self.context.values)
        # Construction des arrays test, a == 1 & b == 1
        test_arr_self = self.context.values == 1
        test_arr_other = other.values == 1
        # b si a == 1 b & a si b == 1
        res_array[test_arr_self] = other.values[test_arr_self]
        res_array[test_arr_other] = self.context.values[test_arr_other]

        return res_array

    def _conorm(self, other):
        # Définirion de l'array a renvoyer
        # 1 si a != 0 ou b != 0 i.e. tous les autres cas
        res_array = np.ones_like(self.context.values)
        # Construction des arrays test, a == 0 & b == 0
        test_arr_self = self.context.values == 0
        test_arr_other = other.values == 0
        # b si a == 0 b & a si b == 0
        res_array[test_arr_self] = other.values[test_arr_self]
        res_array[test_arr_other] = self.context.values[test_arr_other]

        return res_array
