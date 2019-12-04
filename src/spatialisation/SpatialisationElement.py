import logging

import numpy as np
from rasterio import features

import config
from fuzzyUtils import FuzzyRaster

from .AggregatorStrategies import FirstAggregator, ParallelAggregator


logger = logging.getLogger(__name__)


class SpatialisationElement:
    """
    Classe spatialisationElement
    """

    def __init__(self, context, geom, metric, selector, *args, **kwargs):
        self.context = context
        self.geom = geom
        # Initialisation des objets Metric et Selector
        self._init_metric(metric, **kwargs.get("metric_params"))
        self._init_selector(
            selector, kwargs.get("modifiers"), **kwargs.get("selector_params")
        )

    def _init_metric(self, metric, *args, **kwargs):
        self.metric = metric(self, *args, **kwargs)

    def _init_selector(self, selector, modifiers, *args, **kwargs):
        self.selector = selector(self, modifiers, *args, **kwargs)

    def rasterise(self):

        zi = np.zeros_like(self.context.raster.values)

        # Possibilité d'utiliser geom.exterior ou geom.centroid
        features.rasterize(
            [self.geom],
            out=zi,
            transform=self.context.raster.raster_meta["transform"],
            all_touched=True,
            dtype=self.context.raster.raster_meta["dtype"],
        )

        #FuzzyRaster(array=zi, meta=self.context.raster.raster_meta).write("./_outTest/xx.tif")
        return zi

    def compute(self, *args):
        # Rasterisation
        geom_raster = self.rasterise()
        tmp = self.metric.compute(geom_raster)
        # Fuzzyfication
        self.selector.compute(tmp)

        logger.debug("Element computed : %s " % self.metric)

        return tmp


class SpatialisationElementSequence(dict):

    default_aggregator_strategy = FirstAggregator

    def __init__(self, aggregator_strategy=None, confiance=None, *args, **kwargs):

        if aggregator_strategy:
            print(aggregator_strategy)
            self.aggregator_strategy = aggregator_strategy(self, confiance)
        else:
            self.aggregator_strategy = self.default_aggregator_strategy(self, confiance)

        logger.debug(
            "Aggregator strategy : %s" % (self.aggregator_strategy.__class__.__name__,)
        )

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
