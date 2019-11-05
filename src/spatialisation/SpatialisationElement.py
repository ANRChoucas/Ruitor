import logging

import numpy as np
from rasterio import features

import config
from fuzzyUtils import FuzzyRaster

from .AggregatorStrategies import FirstAggragator


class SpatialisationElement:
    """
    Classe spatialisationElement
    """

    def __init__(self, context, geom, metric, selector, *args, **kwargs):
        self.context = context
        self.geom = geom

        # Initialisation des objets Metric et Selector
        self._init_metric(metric, *args, **kwargs)
        self._init_selector(selector, *args, **kwargs)

    def _init_metric(self, metric, *args, **kwargs):
        self.metric = metric(self, *args, **kwargs)

    def _init_selector(self, selector, *args, **kwargs):
        self.selector = selector(self, *args, **kwargs)

    def rasterise(self):

        zi = np.zeros_like(self.context.raster.values)

        features.rasterize(
            [self.geom],
            out=zi,
            transform=self.context.raster.raster_meta["transform"],
            all_touched=True,
            dtype=self.context.raster.raster_meta["dtype"],
        )

        # FuzzyRaster(array=zi, meta=self.context.raster.raster_meta)
        return zi

    def compute(self, *args):
        # Rasterisation
        geom_raster = self.rasterise()
        tmp = self.metric.compute(geom_raster)
        # Fuzzyfication
        self.selector.compute(tmp)

        logging.debug("Element compute : %s " % self.metric.__class__)

        return tmp


class SpatialisationElementSequence(dict):

    default_aggregator_strategy = FirstAggragator

    def __init__(self, aggregator_strategy=None, *args, **kwargs):

        if aggregator_strategy:
            self.aggregator_strategy = aggregator_strategy(self)
        else:
            self.aggregator_strategy = self.default_aggregator_strategy(self)

        super().__init__(*args, **kwargs)

    def _get_partial(self, key, pos):
        for k in self.keys():
            if k[pos] == key:
                yield self[k]

    def element_compute(self, element):
        return element.compute()

    def compute(self, pools=6):
        """
        Fonction pour l'initialisation du calcul
        """
        return self.aggregator_strategy.compute()
