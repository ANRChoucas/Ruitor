"""
Module FuzzyOperators. 

Contient la classe générique FuzzyOperators et des
spécialisations. 
"""

import numpy as np


class FuzzyOperators:
    """
    Classe d'opérateurs flous générique 
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
        return self._norm(other)

    def conorm(self, other):
        """
        Calcule la conorme de deux ensembles flous
        """

        self._check_operators(other)
        return self._conorm(other)

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
        res_array[test_arr] = np.minimum(
            self.context.values, other.values)[test_arr]

        return res_array

    def _conorm(self, other):
        # Définirion de l'array a renvoyer
        res_array = np.empty_like(self.context.values)
        # Construction de l'array test: True si a + b < 1
        test_arr = self.context.values + other.values < 1
        # 1 si a + b >= 1
        res_array[~test_arr] = 1
        # max(a,b) si a+b < 1
        res_array[test_arr] = np.maximum(
            self.context.values, other.values)[test_arr]

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
        res_array = np.empty_like(self.context.values)
        # Construction des arrays test, a == 1 & b == 1
        test_arr_self = self.context.values == 1
        test_arr_other = other.values == 1
        # b si a == 1 b & a si b == 1
        res_array[test_arr_self] = other.values[test_arr_self]
        res_array[test_arr_other] = self.context.values[test_arr_other]
        # 0 si a != 1 ou b != 1 i.e. tous les autres cas
        res_array[~(test_arr_self | test_arr_other)] = 0

        return res_array

    def _conorm(self, other):
        # Définirion de l'array a renvoyer
        res_array = np.empty_like(self.context.values)
        # Construction des arrays test, a == 0 & b == 0
        test_arr_self = self.context.values == 0
        test_arr_other = other.values == 0
        # b si a == 0 b & a si b == 0
        res_array[test_arr_self] = other.values[test_arr_self]
        res_array[test_arr_other] = self.context.values[test_arr_other]
        # 1 si a != 0 ou b != 0 i.e. tous les autres cas
        res_array[~(test_arr_self | test_arr_other)] = 1

        return res_array
