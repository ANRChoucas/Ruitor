"""Fichier Fusion.py
"""

from .DSTEvaluator import HypothesisSet
from .FuzzyEvaluator import FuzzyEvaluator

from functools import reduce
import numpy as np


class fusion(object):
    """Classe Fusion"""

    default_evaluation_strategy = FuzzyEvaluator

    def __init__(self, evaluation_strategy=None, **kwargs):
        """
        Fonction d'initialisation
        """

        if evaluation_strategy:
            self.evaluation_strategy = evaluation_strategy(self, **kwargs)
        else:
            self.evaluation_strategy = self.default_evaluation_strategy(self, **kwargs)

    def compute(self, indices, evaluate=None):
        """
        Fonction de calcul de la fusion
        """

        # Caclcul de la fusion
        f_indices = self.fusion(indices)

        # Réalisation de l'évaluation
        if evaluate:
            evaluation_output = self.evaluate(f_indices, rank=evaluate)
        else:
            evaluation_output = None

        return f_indices, evaluation_output

    def fusion(self, indices):
        """
        Clacul de la fusion
        """
        return reduce(lambda x, y: x & y, indices)

    def evaluate(self, zone, rank):
        """
        Fonction d'évaluation
        """

        return self.evaluation_strategy.evaluate(zone, rank)
