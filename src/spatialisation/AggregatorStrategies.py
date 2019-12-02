import logging
from functools import reduce
from itertools import groupby
from operator import itemgetter
import numpy as np

from pathos.multiprocessing import ProcessingPool as Pool
from pathos.helpers import mp

import config

logger = logging.getLogger(__name__)


class AggregatorStrategy:
    def __init__(self, context, confiance=None):
        self.context = context
        if confiance:
            self.uncertainty = (1.0 - confiance)
        self.pools = config.multiprocessing["pools"]

    def _elem_reduce(self, function, values, pools=6, chuncks=12):
        return reduce(function, values)

    def _agg_objects(self, agg):
        logger.debug("agg_obj : Begin")
        res = self._elem_reduce(lambda x, y: x | y, agg.values())
        if self.uncertainty:
            logger.debug("uncertainty : %s" % (self.uncertainty,))
            res.values = np.maximum(res.values, self.uncertainty)
        logger.info("agg_obj : Done")
        return res


class OptimizedAggregator(AggregatorStrategy):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def worker1(self, input_queue, output_queue):
        tmp = []
        for gr in iter(input_queue.get, "STOP"):
            for i in list(gr):
                print(self.context[i].compute())
                # tmp.append(self.context[i].compute())

    def compute(self):

        keys = list(self.context.keys())
        keys.sort(key=itemgetter(0))

        for k, gr in groupby(keys, key=itemgetter(0)):
            sp_queue.put(gr)

        # for proc in range(2):
        hop = mp.Process(target=self.worker1, args=(sp_queue, cmp_queue))
        hop.start()

        hop.join()


class ParallelAggregator(AggregatorStrategy):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def worker1(self, input):
        tmp = {}
        # calc
        for i in input:
            tmp[i] = self.context[i].compute()

        logger.debug("agg_spa_rel : Begin")
        keysList = list(tmp.keys())
        keysList.sort(key=itemgetter(0, 1))

        tmp2 = {}
        grouper = groupby(keysList, key=itemgetter(0, 1))
        for gr in grouper:
            val = itemgetter(*gr[1])(tmp)
            try:
                tmp2[gr[0]] = self._elem_reduce(lambda x, y: x & y, val)
            except TypeError:
                tmp2[gr[0]] = val

        tmp3 = {}
        logger.debug("agg_obj_part : Begin")
        keysList = list(tmp2.keys())
        keysList.sort(key=itemgetter(0))

        grouper = groupby(keysList, key=itemgetter(0))
        for gr in grouper:
            val = itemgetter(*gr[1])(tmp2)
            try:
                tmp3[gr[0]] = self._elem_reduce(lambda x, y: x | y, val)
            except TypeError:
                tmp3[gr[0]] = val

        out = list(tmp3.values())

        if len(out) > 1:
            print(tmp3)
            raise Exception

        return out[0]

    def _agg_objects(self, agg):
        logger.debug("agg_obj : Begin")
        res = self._elem_reduce(lambda x, y: x | y, agg)
        if self.uncertainty:
            logger.debug("uncertainty : %s" % (self.uncertainty,))
            res.values = np.maximum(res.values, self.uncertainty)
        logger.info("agg_obj : Done")
        return res


    def compute(self):

        keys = list(self.context.keys())
        keys.sort(key=itemgetter(0))

        grouper = groupby(keys, key=itemgetter(0))
        gr = [list(gr) for i, gr in grouper]

        with Pool(processes=self.pools) as t:
            cmp_res = t.map(self.worker1, gr)

        return self._agg_objects(cmp_res)


class FirstAggregator(AggregatorStrategy):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

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

    def compute(self):
        """
        Fonction pour l'initialisation du calcul
        """

        # Définition pool pour traitement //
        # des rasters
        sp_list = list(zip(*self.context.items()))

        # sp_list[1][0].compute()

        logger.info("Compute : Begin")

        #with Pool(processes=self.pools) as t:
        #    cmp_res = t.map(self.context.element_compute, sp_list[1])

        # Version debug
        cmp_res = map(self.context.element_compute, sp_list[1])

        logger.info("Compute : Done")

        cmp_dic = {k: v for k, v in zip(sp_list[0], cmp_res)}
        zou = self._agg_spa_rel(cmp_dic)
        zi = self._agg_objects_part(zou)
        zu = self._agg_objects(zi)

        if config.log["int_files"]:

            logger.info("Writing tempfiles : Begin")

            logger.debug("Spatial relations writing: Begin")

            for k, v in cmp_dic.items():
                f_name = "obj%s_part%s_rel%s" % k
                v.write("./_outTest/%s.tif" % f_name)
                logger.debug("Spatial relation %s writing : Done", f_name)

            logger.debug("Spatial relations writing : Done")

            logger.debug("Objects Parts writing : Begin")

            for k, v in zou.items():
                f_name = "obj%s_part%s" % k
                v.write("./_outTest/%s.tif" % f_name)
                logger.debug("Object part %s writing  : Done", f_name)

            logger.debug("Objects Parts writing : Done")

            logger.info("Writing tempfiles writing : Done")

        return zu

    def _agg_objects_part(self, agg):
        """
        """
        res = {}

        logger.debug("agg_obj_part : Begin")

        keysList = list(agg.keys())
        keysList.sort(key=itemgetter(0))

        grouper = groupby(keysList, key=itemgetter(0))
        for gr in grouper:
            val = itemgetter(*gr[1])(agg)
            try:
                res[gr[0]] = self._elem_reduce(lambda x, y: x | y, val)
            except TypeError:
                res[gr[0]] = val

        logger.info("agg_obj_part : Done")

        return res

    def _agg_spa_rel(self, agg):
        """
        """
        res = {}

        logger.debug("agg_spa_rel : Begin")

        keysList = list(agg.keys())
        keysList.sort(key=itemgetter(0, 1))

        grouper = groupby(keysList, key=itemgetter(0, 1))
        for gr in grouper:
            val = itemgetter(*gr[1])(agg)
            try:
                res[gr[0]] = self._elem_reduce(lambda x, y: x & y, val)
            except TypeError:
                res[gr[0]] = val

        logger.info("agg_spa_rel : Done")

        return res
