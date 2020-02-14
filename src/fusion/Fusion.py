from functools import reduce
from .Evaluation import tt


class fusion(object):

    default_evaluation_strategy = tt

    def __init__(self, evaluation_strategy=None, **kwargs):
        pass

        if evaluation_strategy:
            self.evaluation_strategy = evaluation_strategy(self)
        else:
            self.evaluation_strategy = self.default_evaluation_strategy(self)

    def compute(self, indices, evaluate=False):

        f_indices = reduce(lambda x, y: x & y, indices)

        if evaluate:
            return self.evaluate(f_indices)

        return f_indices

    def evaluate(self, zone):
        return self.evaluation_strategy.evaluate(zone)