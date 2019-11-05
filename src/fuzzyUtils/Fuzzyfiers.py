"""
Fuzzyfiers

sdqd
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


class Fuzzyfier:
    """
    Classe permettant la fuzzification d'un raster net
    """

    def __init__(self, context):
        self.context = context

    def __str__(self):
        description_string = """fuzzyfier class  : {}
        parameters : {}
        uncertainty : {}
        """

        try:
            str_params = self.fuzzyfication_parameters
        except AttributeError:
            str_params = "no parameter"

        try:
            unc_params = self.certainty_parameters
        except AttributeError:
            unc_params = "no parameter"

        return description_string.format(
            self.__class__.__name__, str_params, unc_params
        )

    def fuzzyfy(self, raster, fuzzyfication_parameters, certainty=0.0):
        self.fuzzyfication_parameters = fuzzyfication_parameters
        self.certainty_parameters = certainty

        self.fuzzyfication_function = self.def_fuzzyfy_function(
            *self.fuzzyfication_parameters
        )

        # Calcul des valeurs
        fuzzyfied_raster = self.fuzzyfication_function(raster)
        self.set_uncertainty(fuzzyfied_raster, self.certainty_parameters)

        return fuzzyfied_raster

    def def_fuzzyfy_function(self, *args, **kwargs):
        raise NotImplementedError("No fuzzyfycation function constructor")

    def set_uncertainty(self, raster, certainty=0.0):
        if certainty != 0.0:
            raster[raster < certainty] = certainty


class FirstFuzzyfier(Fuzzyfier):
    """
    Classe permettant la fuzzification d'un raster net
    """

    def __init__(self, context):
        super().__init__(context)

    def fuzzyfy(self, raster, parameters):
        self.fuzzyfication_parameters = parameters
        self.fuzzyfication_function = self.def_fuzzyfy_function(*parameters)

        # Calcul des valeurs
        # Approche vraiment lente, à modifier
        vfun = np.vectorize(self.fuzzyfication_function, otypes=[raster.dtype])

        return vfun(raster)

    def def_fuzzyfy_function(self, *args, **kwargs):

        sorted(args, key=lambda x: x[0])

        # Définition de la fonction
        # Todo réduire à l'occasion
        if len(args) == 2:

            def fun(x):
                if x < args[0][0]:
                    out = args[0][1]
                elif x < args[1][0]:
                    a = (args[1][1] - args[0][1]) / (args[1][0] - args[0][0])
                    b = -(args[0][0] * a - args[0][1])
                    out = a * x + b
                else:
                    out = args[1][1]
                return out

        elif len(args) == 3:

            def fun(x):
                if x < args[0][0]:
                    out = args[0][1]
                elif x < args[1][0]:
                    a = (args[1][1] - args[0][1]) / (args[1][0] - args[0][0])
                    b = args[0][1]
                    out = a * x + b
                elif x < args[2][0]:
                    a = (args[2][1] - args[1][1]) / (args[2][0] - args[1][0])
                    b = args[1][1]
                    out = a * x + b
                else:
                    out = args[1][1]
                return out

        elif len(args) == 4:

            def fun(x):
                if x < args[0][0]:
                    out = args[0][1]
                elif x < args[1][0]:
                    a = (args[1][1] - args[0][1]) / (args[1][0] - args[0][0])
                    b = args[0][1]
                    out = a * x + b
                elif x < args[2][0]:
                    out = args[2][1]
                elif x < args[3][0]:
                    a = (args[3][1] - args[2][1]) / (args[3][0] - args[2][0])
                    b = args[2][1]
                    out = a * x + b
                else:
                    out = args[3][1]
                return out

        else:
            raise ValueError("2, 3 or 4 values accepted")

        return fun


class FuzzyfierMoreSpeeeeed(Fuzzyfier):
    def __init__(self, context):
        super().__init__(context)

    def def_fuzzyfy_function(self, *args, **kwargs):
        """
        fonction chargée de la génération de la fonction "fuzzy_fun".
        "fuzzy_fun" crée une copie fuzzyfiée du raster donné en entrée.
        """

        # Tri des paramètres
        sorted(args, key=lambda x: x[0])
        largs = len(args)
        # Définition de la fonction
        # Liste de patterns en fonction du nombre de paramètres
        fun_rules = {
            # Cas crisp
            1: (self._inf_vals,),
            # Cas où la fonction est une droite
            2: (self._inf_vals, self._fst_slp, self._sup_vals),
            # la fonction est de forme triangulaire
            3: (self._inf_vals, self._fst_slp, self._lst_slp, self._sup_vals),
            # forme trapézoidale
            4: (
                self._inf_vals,
                self._fst_slp,
                self._cnt_flt,
                self._lst_slp,
                self._sup_vals,
            ),
        }

        # Caneva de la fonction "fuzzy fun"
        def fuzzy_fun(raster):
            raster_copy = np.zeros_like(raster)
            try:
                # On récupère la liste d'instruction correspondant au nombre d'arguments
                for ins in fun_rules[largs]:
                    # On applique les fonctions, dans l'ordre du tuple "fun_rules[largs]"
                    ins(raster, raster_copy, *args)
                return raster_copy
            except KeyError:
                raise ValueError("2, 3 or 4 parameters needed")

        # Renvoi de la fonction générée
        return fuzzy_fun

    def _inf_vals(self, r, r_copy, *args):
        # degré flou des valeurs inf au plus petit paramètre
        r_copy[r < args[0][0]] = args[0][1]

    def _fst_slp(self, r, r_copy, *args):
        # degré flou des valeurs par la première pente
        a = (args[1][1] - args[0][1]) / (args[1][0] - args[0][0])
        b = -(args[0][0] * a - args[0][1])
        r_copy[(r >= args[0][0]) & (r < args[1][0])] = (
            r[(r >= args[0][0]) & (r < args[1][0])] * a + b
        )

    def _cnt_flt(self, r, r_copy, *args):
        # degré flou des valeurs par le plat central
        r_copy[(r >= args[1][0]) & (r < args[-2][0])] = args[-2][1]

    def _lst_slp(self, r, r_copy, *args):
        # degré flou des valeurs par la seconde pente
        lv = args[-1]
        alv = args[-2]
        a = (lv[1] - alv[1]) / (lv[0] - alv[0])
        b = -(alv[0] * a - alv[1])
        r_copy[(r >= alv[0]) & (r < lv[0])] = r[(r >= alv[0]) & (r < lv[0])] * a + b

    def _sup_vals(self, r, r_copy, *args):
        # degré flou des valeurs sup au plus grand paramètre
        r_copy[r >= args[-1][0]] = args[-1][1]
