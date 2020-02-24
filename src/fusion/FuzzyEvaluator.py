from functools import reduce
import numpy as np
import skfuzzy as fuzz

from .Evaluator import Evaluator


class FuzzyEvaluator(Evaluator):
    def __init__(self, context, cellsize):

        self.note = Note()

        self.linguistic_variable = {}
        self.linguistic_variable["dmax"] = DegreeMax()
        self.linguistic_variable["dmed"] = DegreeMedian()
        self.linguistic_variable["dstd"] = DegreeStd()
        self.linguistic_variable["gcvt"] = GeometryConcavity()
        self.linguistic_variable["gedt"] = GeometryEquivalentDiameter(cellsize)

        super().__init__(context)

    def _evaluate(self, region, descriptors):

        for descriptor in descriptors:

            # Variables
            val_max = descriptor["max_intensity"]
            val_med = np.median(descriptor["intensity_image"][descriptor["image"]])
            val_std = np.std(descriptor["intensity_image"][descriptor["image"]])
            val_cnv = descriptor["filled_area"] / descriptor["convex_area"]
            val_ed = np.abs(10 - descriptor["equivalent_diameter"]) * 50

            # Fuzzyfication
            vmax_dict = self.linguistic_variable["dmax"](val_max)
            vmed_dict = self.linguistic_variable["dmed"](val_med)
            vstd_dict = self.linguistic_variable["dstd"](val_std)
            vcnv_dict = self.linguistic_variable["gcvt"](val_cnv)
            ved_dict = self.linguistic_variable["gedt"](val_ed)

            act_notes = reduce(
                lambda x, y: self.aggregator(x, y),
                [vmax_dict, vmed_dict, vstd_dict, vcnv_dict, ved_dict],
            )

            act_notes_x = (
                np.fmin(self.note.levels["faible"], act_notes["faible"]),
                np.fmin(self.note.levels["moyen"], act_notes["moyen"]),
                np.fmin(self.note.levels["fort"], act_notes["fort"]),
            )

            # Aggrégation
            aggregated = reduce(lambda x, y: np.fmax(x, y), act_notes_x)
            # Defuzzyfication
            note = fuzz.defuzz(self.note.domain, aggregated, "centroid")
            yield note

    def aggregator(self, dic1, dic2, rule="strong"):

        if rule == "strong":
            aggregated_vals = self._strong_aggregator(dic1, dic2)
        elif rule == "weak":
            aggregated_vals = self._weak_aggregator(dic1, dic2)
        elif rule == "compromise":
            aggregated_vals = self._compromise_aggregator(dic1, dic2)
        else:
            raise ValueError("Rule wrong")

        return aggregated_vals

    def _weak_aggregator(self, dic1, dic2):
        vfaible = np.fmin(dic1["faible"], dic2["faible"])
        vfort = np.fmax(dic1["fort"], dic2["fort"])
        vmoyen = np.fmin(np.fmax(dic1["moyen"], dic2["moyen"]), (1 - vfort))

        return {"faible": vfaible, "moyen": vmoyen, "fort": vfort}

    def _strong_aggregator(self, dic1, dic2):
        vfaible = np.fmax(dic1["faible"], dic2["faible"])
        vmoyen = np.fmin(np.fmax(dic1["moyen"], dic2["moyen"]), (1 - vfaible))
        vfort = np.fmin(dic1["fort"], dic2["fort"])

        return {"faible": vfaible, "moyen": vmoyen, "fort": vfort}

    def _compromise_aggregator(self, dic1, dic2):
        vfaible = np.fmin(dic1["faible"], dic2["faible"])
        vfort = np.fmin(
            np.fmax(dic1["fort"], dic2["fort"]),
            (1 - (np.fmax(dic1["faible"], dic2["faible"]))),
        )
        vmoyen = 1 - np.fmin(vfaible, vfort)

        return {"faible": vfaible, "moyen": vmoyen, "fort": vfort}


class LinguisticVariable:
    domain = np.arange(0, 1.1, 0.01)

    def __init__(self):
        self.levels = {}

    def __call__(self, value):
        return {
            i: fuzz.interp_membership(self.domain, v, value)
            for i, v in self.levels.items()
        }

    def __and__(self, other):
        return (
            np.fmin(self.levels["faible"], other.levels["faible"]),
            np.fmin(self.levels["moyen"], other.levels["moyen"]),
            np.fmin(self.levels["fort"], other.levels["fort"]),
        )

    def __or__(self, other):
        return (
            np.fmax(self.levels["faible"], other.levels["faible"]),
            np.fmax(self.levels["moyen"], other.levels["moyen"]),
            np.fmax(self.levels["fort"], other.levels["fort"]),
        )


class Note(LinguisticVariable):
    def __init__(self):
        super().__init__()
        self.levels["faible"] = fuzz.trimf(self.domain, [0, 0, 0.5])
        self.levels["moyen"] = fuzz.trimf(self.domain, [0, 0.5, 1])
        self.levels["fort"] = fuzz.trimf(self.domain, [0.5, 1, 1])


class DegreeMax(LinguisticVariable):
    def __init__(self):
        super().__init__()
        self.levels["faible"] = fuzz.trapmf(self.domain, [0, 0, 0.25, 0.5])
        self.levels["moyen"] = fuzz.trimf(self.domain, [0.25, 0.5, 0.75])
        self.levels["fort"] = fuzz.trapmf(self.domain, [0.5, 0.75, 1, 1])


class DegreeMedian(LinguisticVariable):
    def __init__(self):
        super().__init__()
        self.levels["faible"] = fuzz.trimf(self.domain, [0, 0, 0.2])
        self.levels["moyen"] = fuzz.trimf(self.domain, [0, 0.2, 0.4])
        self.levels["fort"] = fuzz.trapmf(self.domain, [0.2, 0.4, 1, 1])


class DegreeStd(LinguisticVariable):
    def __init__(self):
        super().__init__()
        self.levels["faible"] = fuzz.trimf(self.domain, [0, 0, 0.1])
        self.levels["moyen"] = fuzz.trimf(self.domain, [0, 0.1, 0.2])
        self.levels["fort"] = fuzz.trapmf(self.domain, [0.1, 0.2, 1, 1])


class GeometryConcavity(LinguisticVariable):
    def __init__(self):
        super().__init__()
        self.levels["faible"] = fuzz.trapmf(self.domain, [0, 0, 0.2, 0.4])
        self.levels["moyen"] = fuzz.trimf(self.domain, [0.2, 0.4, 0.6])
        self.levels["fort"] = fuzz.trapmf(self.domain, [0.4, 0.6, 1, 1])


class GeometryEquivalentDiameter(LinguisticVariable):
    def __init__(self, cellsize):
        super().__init__()
        self.domain = np.arange(0, 1000 * cellsize, 1)
        self.levels["moyen"] = fuzz.trapmf(
            self.domain, [2 * cellsize, 3 * cellsize, 4 * cellsize, 5 * cellsize]
        )
        self.levels["fort"] = fuzz.trapmf(
            self.domain, [0, 0, 2 * cellsize, 3 * cellsize]
        )
        self.levels["faible"] = fuzz.trapmf(
            self.domain, [4 * cellsize, 5 * cellsize, 1000 * cellsize, 1000 * cellsize]
        )
