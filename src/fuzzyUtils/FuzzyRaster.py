"""
FuzzyRaster

Module décrivant la classe FuzzyRaster.

Ce module est le centre du package FuzzyUtils.

"""

from . import Fuzzyfiers
from . import FuzzyOperators

import numpy as np
import matplotlib.pyplot as pyplot

import rasterio
from rasterio.windows import get_data_window

from shapely import affinity
from shapely.geometry import LineString


class FuzzyRaster:
    """Classe FuzzyRaster
    
    La classe FuzzyRaster est une extension de la classe raster pour
    traiter des rasters flous. Elle permet d'éffectuer des opérations
    ensemblistes floues entre deux rasters de même emprise
    (mapAlgebra).

    Les rasters flous peuvent être créés de deux façons. Soit à partir
    d'un raster rasterio, soit à partir d'un array numpy et d'un
    ensemble de métadonnées géographiques.

    :Example:

    # D'après un raster rasterio
    >>> import rasterio
    >>> from fuzzyUtils.FuzzyRaster import FuzzyRaster
    >>> dataset = rasterio.open('example.tif')
    >>> FuzzyRaster(raster=dataset)

    # D'après un array numpy
    >>> import numpy as np
    >>> from fuzzyUtils.FuzzyRaster import FuzzyRaster
    # Raster exemple
    >>> dataset = np.zeros((2, 3))
    >>> FuzzyRaster(array=dataset)

    # D'après un array numpy, avec fuzzyfication
    >>> import numpy as np
    >>> from fuzzyUtils.FuzzyRaster import FuzzyRaster
    # Raster exemple
    >>> dataset = np.zeros((2, 3))
    >>> FuzzyRaster(array=dataset, fuzzyfication_parameters=[(0,0),(10,1)])

    """

    # Ce module fait souvent appel au design pattern strategy
    # (cf. https://en.wikipedia.org/wiki/Strategy_pattern). Certaines
    # fonctions de la classe sont déléguées à des méthodes d'autres
    # objets par composition.
    #
    # L'intêret de cette approche est qu'il est possible de définir de
    # nouveaux comportements en changeant les relations de composition
    # à la création de l'objet.
    #
    # Dans le cas de cette classe deux grandes fonctions sont délégués
    # à d'autres objets : la fuzzyfication, qui est opérée par des
    # objets dont la classe hérite de Fuzzyfier (classe définie dans
    # le fichier Fuzzyfiers.py), et les opérations inter-raster, qui
    # sont opérées par des objets héritant de la classe FuzzyOperators
    # (classe définie dans le fichier FuzzyOperators.py).

    # C'est deux variables de classe définissent les "strategies" par
    # défaut. C'est-à-dire que (sans modification) chaque instance de
    # la classe FuzzyRaster sera spatialisée à l'aide du fuzzyficateur
    # Fuzzyfiers.FuzzyfierMoreSpeeeeed et utilisera les opérateurs de
    # Zadeh, définis par la classe FuzzyOperators.ZadehOperators.
    default_fuzzy_operators_strategy = FuzzyOperators.ZadehOperators
    default_fuzzyfier_strategy = Fuzzyfiers.FuzzyfierMoreSpeeeeed

    def __init__(
        self, fuzzy_operators_strategy=None, fuzzyfier_strategy=None, **kwargs
    ):
        """Initialisation de l'objet

        :param fuzzy_operators_strategy: Strategie d'opérateurs flous
        :param fuzzyfier_strategy: Strategie de fuzzyfication

        :return: Une instance de FuzzyRaster

        Cette fonction permet la création de rasters flous. Elle prend
        deux paramètres nommés, fuzzy_operators_strategy et
        fuzzyfier_strategy qui permettent de surcharger les stategies
        de fuzzyfication et les opérateurs flous à la création de l'objet.

        Les paramètres de création de l'instance sont a fournir dans
        le kwargs, ils ne sont pas nommés car deux configurations sont
        possibles. Soit l'utilisateur renseigne le paramètre "raster"
        et le paramètre "window" (optionel), soit il renseigne le
        paramètre "array" et le paramètre "meta" (optionel).

        Dans le cas où l'utilisateur le demande, on peut directement
        fuzzyfier le raster. Pour ça il faut renseigner le paramétre
        "fuzzyfication_parameters". Ce paramètre prend en entrée une
        liste de tuples. Pour chaque tuple la première valeur donne le
        x et la seconde le y (nécessairement compris entre 0 et
        1). Une liste de deux valeurs (eg. [(10,0),(15.2,1)]) permet
        de créer une fonction croissante, une liste de trois valeurs
        (eg. [(5,0),(10,0),(15.2,1)]) une fonction triangulaire et une
        liste de quatre valeurs une fonction trapézoidale. Pour plus
        d'informations voir la documentation de la classe "Fuzzyfier".

        """

        # Définition des opérateurs flous Si une statégie alternative
        # est donnée ("fuzzy_operators_strategy" != de None) alors on
        # l'utilise, sinon on utilise la valeur de la variable de
        # classe "default_fuzzy_operators_strategy".
        if fuzzy_operators_strategy:
            self.fuzzy_operators = fuzzy_operators_strategy(self)
        else:
            self.fuzzy_operators = self.default_fuzzy_operators_strategy(self)

        # Stratégie de fuzzyfication
        # Fonctione de la même manière que ci-dessus
        if fuzzyfier_strategy:
            self.fuzzyfier = fuzzyfier_strategy(self)
        else:
            self.fuzzyfier = self.default_fuzzyfier_strategy(self)

        # Construction raster flou Premier cas, le raster flou est
        # crée à partir d'un objet raster issu de rasterio
        #
        # Si le paramètre "raster" est renseigné alors on utilise la
        # fonction de création à partir d'un objet rasterio
        if "raster" in kwargs:
            # On récupère le raster
            raster = kwargs.get("raster")
            # On récupére la valeur du paramètre "window" (peut-être
            # vide) Le contenu de window doit être un objet window de
            # rasterio
            window = kwargs.get("window", None)
            # On utilise la méthode de création d'une instance de
            # FuzzyRaster à partir d'un raster rasterio
            self._init_from_rasterio(raster, window=window)
        # Si le paramètre "array" est renseigné
        elif "array" in kwargs:
            # On renvoie un avertissement dans le cas où l'on cherche
            # à utiliser une window avec un array (ne fonctionne pas).
            if "window" in kwargs:
                raise Warning("Cannot use a window with a numpy array")
            array = kwargs.get("array")
            # On récupére le contenu de meta (optionel)
            meta = kwargs.get("meta", None)
            # On appelle la méthode permettant de crée un FuzzyRaster
            # à partir d'un array numpu
            self._init_from_numpy(array, meta)
        else:
            # Dans tous les autrs cas on renvoie une exception
            raise ValueError("Bad parameters")

        # On fuzzyfie le raster si le paramètre
        # "fuzzyfication_parameters" est renseigné.
        if "fuzzyfication_parameters" in kwargs:
            fuzzyfication_parameters = kwargs.get("fuzzyfication_parameters")
            # On fuzzyfie
            self.fuzzyfication(fuzzyfication_parameters)

    def fuzzyfication(self, parameters):
        """Fonction de fuzzyfication.

        Prend en paramètre une liste de tuples. Pour chaque tuple la
        première valeur donne le x et la seconde le y (nécessairement
        compris entre 0 et 1). Une liste de deux valeurs
        (eg. [(10,0),(15.2,1)]) permet de créer une fonction
        croissante, une liste de trois valeurs
        (eg. [(5,0),(10,0),(15.2,1)]) une fonction triangulaire et une
        liste de quatre valeurs une fonction trapézoidale. Pour plus
        d'informations voir la documentation de la classe "Fuzzyfier".

        :param parameters: liste de tuples contenant les paramètres de fuzzyfication
        :type parameters: liste de 2-uples

        :return: None

        """
        # self.fuzzy_values = self.fuzzyfier.fuzzyfy(
        #     self.crisp_values, parameters)
        # self.values = self.fuzzy_values

        # On  
        self.values = self.fuzzyfier.fuzzyfy(self.values, parameters)

    def _init_from_rasterio(self, raster, window=None):
        """
        Fonction d'initialisation à partir d'un raster rasterio	
        """

        # self.crisp_values = raster.read(window=window)
        # self.values = self.crisp_values  #[0]

        self.values = raster.read(window=window)

        if window:

            self.raster_meta = raster.meta.copy()
            nw_transform = rasterio.windows.transform(
                window, self.raster_meta["transform"]
            )

            self.raster_meta.update(
                {
                    "height": window.height,
                    "width": window.width,
                    "transform": nw_transform,
                }
            )

        else:
            self.raster_meta = raster.meta

    def _init_from_numpy(self, array, meta=None):
        """
        Fonction d'initialisation à partir d'un array numpy	
        """

        # self.crisp_values = array
        # self.values = self.crisp_values
        self.values = array

        if meta:
            self.raster_meta = meta
        else:
            try:
                count = array.shape[2]
            except IndexError:
                count = 1

            self.raster_meta = {
                "count": count,
                "crs": None,
                "driver": "GTiff",
                "dtype": array.dtype,
                "height": array.shape[0],
                "width": array.shape[1],
                "nodata": -99999.0,
                "transform": None,
            }

    # @property
    # def values(self):
    #   return self.values[self.values != self.raster_meta['nodata']]

    def plot(self):
        pyplot.matshow(self.values, cmap="gray")

    def contour(self, max_val=1, by=0.1):
        """
        Génère les isolignes du raster
        """
        cs = pyplot.contour(self.values[0], np.arange(0, max_val, by))

        a, b, xoff, d, e, yoff = tuple(self.raster_meta["transform"])[:-3]
        affine = a, b, d, e, xoff, yoff

        lines = []

        for col, val in zip(cs.collections, cs.cvalues):
            for path in col.get_paths():
                if len(path) > 1:
                    v = path.vertices
                    x, y = v[:, 0], v[:, 1]
                    line = LineString([(j[0], j[1]) for j in zip(x, y)])
                    line = affinity.affine_transform(line, affine)
                    lines.append((line, val))
        return lines

    def summarize(self):

        nodata = self.raster_meta["nodata"]
        nodata_ind = self.values == nodata
        nodata_c = np.count_nonzero(nodata_ind)
        count = np.size(self.values)
        nodata_p = (nodata_c / count) * 100

        rastmin = self.values[~nodata_ind].min()
        rastmed = np.median(self.values[~nodata_ind])
        rastmax = self.values[~nodata_ind].max()

        description_string = """
        min    : {:.4f}
        median : {:.4f}
        max    : {:.4f}
        -------------------------------
        nodata : {} ({:.2f} %)
        cells  : {}
        -------------------------------
        {}
        -------------------------------
        {}
        """.format(
            rastmin,
            rastmed,
            rastmax,
            nodata_c,
            nodata_p,
            count,
            self.fuzzy_operators,
            self.fuzzyfier,
        )

        print(description_string)

    def __and__(self, other):
        """
        blabla	
        """
        # La gestion des opérations inter-raster est pas top à revoir
        # -> construire les paramètres du raster construit
        return FuzzyRaster(
            array=self.fuzzy_operators.norm(other),
            meta=self.raster_meta,
            fuzzy_operators_strategy=self.fuzzy_operators.__class__,
        )

    def __or__(self, other):
        return FuzzyRaster(
            array=self.fuzzy_operators.conorm(other),
            meta=self.raster_meta,
            fuzzy_operators_strategy=self.fuzzy_operators.__class__,
        )

    def __invert__(self):
        return FuzzyRaster(
            array=(1 - self.values),
            meta=self.raster_meta,
            fuzzy_operators_strategy=self.fuzzy_operators.__class__,
        )

    def __sub__(self, other):
        return FuzzyRaster(
            array=(self.values - other.values),
            meta=self.raster_meta,
            fuzzy_operators_strategy=self.fuzzy_operators.__class__,
        )

    def write(self, path, write_params=None, write_window=None):
        """
        Enregistrement du raster

        Par défaut, la fonction utilise les paramètres de self.raster_meta

        :param path: Emplacement du fichier
        :param write_params: Paramètres d'enregistrement
        """

        if not write_params:
            write_params = self.raster_meta

        write_params["driver"] = "GTiff"

        # Ecriture du raster avec les paramètres initaux
        with rasterio.open(path, "w", **write_params) as dst:
            dst.write(self.values, window=write_window)
