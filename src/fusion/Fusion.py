from .DSTEvaluator import HypothesisSet
from .FuzzyEvaluator import FuzzyEvaluator

from functools import reduce


class fusion(object):

    default_evaluation_strategy = FuzzyEvaluator

    def __init__(self, evaluation_strategy=None, **kwargs):
        if evaluation_strategy:
            self.evaluation_strategy = evaluation_strategy(self, **kwargs)
        else:
            self.evaluation_strategy = self.default_evaluation_strategy(self, **kwargs)

    def compute(self, indices, evaluate="rank"):

        f_indices = reduce(lambda x, y: x & y, indices)

        if evaluate == "rank":
            evaluation_output = self.evaluate(f_indices, rank=True)
        elif evaluate == "note":
            evaluation_output = self.evaluate(f_indices, rank=False)
        else:
            evaluation_output = None

        return f_indices, evaluation_output

    def evaluate(self, zone, rank):
        return self.evaluation_strategy.evaluate(zone, rank)
