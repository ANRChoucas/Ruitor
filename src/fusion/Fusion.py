from .DSTEvaluator import HypothesisSet
from .FuzzyEvaluator import FuzzyEvaluator

from functools import reduce
import numpy as np


class fusion(object):

    default_evaluation_strategy = FuzzyEvaluator

    def __init__(self, evaluation_strategy=None, **kwargs):
        if evaluation_strategy:
            self.evaluation_strategy = evaluation_strategy(self, **kwargs)
        else:
            self.evaluation_strategy = self.default_evaluation_strategy(self, **kwargs)

    def compute(self, indices, evaluate="rank"):
        f_indices = self.aggregation(indices)
        evaluation_output = self.evaluate(f_indices, rank=evaluate)
        return f_indices, evaluation_output

    def aggregation(self, indices):
        #import ipdb; ipdb.set_trace()
        #return reduce(lambda x, y: x & y, indices)
        xx =  indices[0]
        xx.values = np.argmin(np.stack([i.values for i in indices], axis=0), axis=0).astype(np.float32)
        return  xx

    def evaluate(self, zone, rank):
        return self.evaluation_strategy.evaluate(zone, rank)
