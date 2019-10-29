"""
Spatialisation
"""

import numpy as np

from pathos.multiprocessing import ProcessingPool as Pool
from functools import reduce
from itertools import groupby
from operator import itemgetter
from more_itertools import chunked

from rasterio import features
from rasterio.windows import Window

from fuzzyUtils import FuzzyRaster
from .Metric import Cell_Distance, Distance, Metric, Nothing, Angle
from .Selector import Selector, Selector2


class SpatialisationElement:
    """
    Classe spatialisationElement
    """

    def __init__(self, context, raster, metric, selector):
        self.context = context
        self.raster = raster
        # Initialisation des objets Metric et Selector
        self._init_metric(metric)
        self._init_selector(selector)

    def _init_metric(self, metric=Angle):
        self.metric = metric(self)

    def _init_selector(self, selector=Selector):
        self.selector = selector(self)

    def compute(self, *args):
        tmp = self.metric.compute()
        self.selector.compute(tmp)
        return tmp


class SpatialisationElementSequence(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_partial(self, key, pos):
        for k in self.keys():
            if k[pos] == key:
                yield self[k]

    def _elem_reduce(self, function, values, pools=6, chuncks=12):
        return reduce(function, values)
        # Ne marche pas a refaire
        # _tempRes = []
        # p = Pool(processes=pools)
        # def _par_reduce(pool, function, values):
        #     def fun(x): return reduce(function, x)
        #     res = p.map(fun, chuncked(values, chuncks))
        #     return res
        # _tempRes.append(_par_reduce(p, function, valusq))
        # if len(_tempRes) > chuncks:
        #     _par_reduce(p, function, _tempRes)
        # else:
        #     return reduce(function, _tempRes)

    def element_compute(self, element):
        return element.compute()

    def _agg_objects(self, agg):
        res = self._elem_reduce(lambda x, y: x | y, agg.values())

        if __debug__:
            print("agg_obj : Done")

        return res

    def _agg_objects_part(self, agg):
        """
        """
        res = {}
        keysList = list(agg.keys())
        keysList.sort(key=itemgetter(0))

        grouper = groupby(keysList, key=itemgetter(0))
        for gr in grouper:
            val = itemgetter(*gr[1])(agg)
            try:
                res[gr[0]] = self._elem_reduce(lambda x, y: x | y, val)
            except TypeError:
                res[gr[0]] = val

        if __debug__:
            print("agg_obj_part : Done")

        return res

    def _agg_spa_rel(self, agg):
        """
        """
        res = {}

        keysList = list(agg.keys())
        keysList.sort(key=itemgetter(0, 1))

        grouper = groupby(keysList, key=itemgetter(0, 1))
        for gr in grouper:
            val = itemgetter(*gr[1])(agg)
            try:
                res[gr[0]] = self._elem_reduce(lambda x, y: x & y, val)
            except TypeError:
                res[gr[0]] = val

        if __debug__:
            print("agg_spa_rel : Done")

        return res

    def compute(self, pools=6):
        """
        Fonction pour l'initialisation du calcul
        """

        # Définition pool pour traitement //
        # des rasters
        sp_list = list(zip(*self.items()))

        with Pool(processes=pools) as t:
            cmp_res = t.map(self.element_compute, sp_list[1])

        cmp_dic = {k: v for k, v in zip(sp_list[0], cmp_res)}
        zou = self._agg_spa_rel(cmp_dic)
        zi = self._agg_objects_part(zou)
        zu = self._agg_objects(zi)

        if __debug__:
            print("writing tempfiles")
            for k, v in cmp_dic.items():
                f_name = "obj%s_part%s_rel%s" % k
                v.write("./_outTest/%s.tif" % f_name)

            for k, v in zou.items():
                f_name = "obj%s_part%s" % k
                v.write("./_outTest/%s.tif" % f_name)

        return zu


class Spatialisation:
    """
    Classe spatialisation

    Destinée à modéliser UN élément de localisation
    """

    def __init__(self, parameters, raster, raster2):
        """
        Fonction d'initialisation de la classe Spatialisation
        """

        # Récupération des paramètres
        self.params = parameters
        self.spaElms = SpatialisationElementSequence()

        # Définition zone initiale de recherche
        if "zir" in self.params:
            self.zir = self.set_zir(raster, self.params["zir"])
        else:
            self.zir = None

        # Création du raster flou résultat
        self.raster = FuzzyRaster(raster=raster, window=self.zir)
        self.raster2 = FuzzyRaster(raster=raster2[0], window=self.zir)
        self.raster3 = FuzzyRaster(raster=raster2[1], window=self.zir)

        self.indice_parsing(self.params['indices'])

    def _init_obj(self):
        pass

    def indice_parsing(self, indice, *args):
        """
        """

        indice = indice[0]

        site_counter = 0
        for s in indice['site']:
            zi = np.zeros_like(self.raster.values)

            features.rasterize(
                [s], out=zi,
                transform=self.raster.raster_meta['transform'],
                all_touched=True,
                dtype=self.raster.raster_meta['dtype'])

            fuzz = FuzzyRaster(array=zi, meta=self.raster.raster_meta)

            self.spaElms[(site_counter, 0, 0)
                         ] = SpatialisationElement(self, fuzz, metric=Cell_Distance, selector=Selector2)
            self.spaElms[(site_counter, 0, 1)
                         ] = SpatialisationElement(self, fuzz, metric=Distance, selector=Selector2)

            site_counter += 1

        # aa = SpatialisationElement(self, self.raster)
        # bb = SpatialisationElement(self, self.raster2)
        # cc = SpatialisationElement(self, self.raster3)

        # self.spaElms[(0, 0, 0)] = aa
        # self.spaElms[(1, 0, 0)] = bb
        # self.spaElms[(2, 0, 0)] = cc

    def site_parsing(self, site):
        pass

    def cible_parsing(self, cible):
        pass

    def compute(self, *args):
        return self.spaElms.compute()

    def set_zir(self, raster, zir, *args, **kwargs):
        """
        Crée une fenêtre rasterio à partir d'une liste de 
        deux coordonnées.

        Permet de travailler sur une petite zone en lieu et 
        place de tout le raster.

        Possibilité de spécifier un padding
        """
        # Spécification du padding
        if 'padding' in kwargs:
            padding = kwargs['padding']
        else:
            padding = {'x': 10, 'y': 10}
        # Calcul Zir
        # Calcul des numéros de ligne et de colonne correspondant aux
        # deux points de la bbox
        row_ind, col_ind = zip(*map(lambda x: raster.index(*x), zir))
        # Extraction du numéro de ligne/colonne minimum
        row_min, col_min = min(row_ind), min(col_ind)
        # Calcul du nombre de lignes/colonnes
        row_num = abs(max(row_ind) - row_min) + padding['x']
        col_num = abs(max(col_ind) - col_min) + padding['y']
        # Définition de la fenêtre de travail
        return Window(col_min, row_min, col_num, row_num)
