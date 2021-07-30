import logging


from .AggregatorStrategies import FirstAggregator, ParallelAggregator


logger = logging.getLogger(__name__)


class SpatialisationElement:
    """
    Classe spatialisationElement
    """

    def __init__(
        self, context, geom, metric, selector, rasterizer, modifier, *args, **kwargs
    ):

        self.context = context
        self.geom = geom
        # Initialisation des objets Metric et Selector
        self._init_metric(metric, **kwargs.get("metric_params"))
        self._init_selector(
            selector, kwargs.get("modifiers"), **kwargs.get("selector_params")
        )
        self._init_rasterizer(rasterizer, **kwargs.get("rasterizer_params"))

        if modifier:
            self._init_modifier(modifier)
        else:
            self.modifier = None

    def _init_rasterizer(self, rasteriser, *args, **kwargs):
        self.rasteriser = rasteriser(self, *args, **kwargs)

    def _init_metric(self, metric, *args, **kwargs):
        self.metric = metric(self, *args, **kwargs)

    def _init_selector(self, selector, modifiers, *args, **kwargs):
        self.selector = selector(self, modifiers, *args, **kwargs)

    def _init_modifier(self, modifier, *args, **kwargs):
        self.modifier = modifier(self)

    def rasterise(self):
        return self.rasteriser.rasterize()

    def compute(self, *args, **kwargs):
        # Rasterisation
        geom_raster = self.rasterise()
        tmp_res = self.metric.compute(geom_raster)
        # Fuzzyfication
        self.selector.compute(tmp_res)

        if self.modifier:
            tmp_res = self.modifier.modifing(tmp_res)

        logger.debug("Element computed : %s " % self.metric)
        return tmp_res


class SpatialisationElementB(SpatialisationElement):
    
    def compute(self, *args, **kwargs):
        # Rasterisation
        geom_raster = self.rasterise()
        tmp_res = self.metric.compute(geom_raster)
        # Fuzzyfication
        self.selector.compute(tmp_res)

        if self.modifier:
            tmp_res = self.modifier.modifing(tmp_res)

        logger.debug("Element computed : %s " % self.metric)
        return tmp_res


class SpatialisationElementSequence(dict):

    default_aggregator_strategy = ParallelAggregator

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


class t_SpatialisationElementSequence(list):
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

    def element_compute(self, element):
        return element.compute()

    def compute(self):
        return self.aggregator_strategy.compute()
