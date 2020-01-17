"""
Module metric
"""

from fuzzyUtils import FuzzyRaster

import numpy as np
import scipy.ndimage
import scipy.spatial
import scipy.interpolate


class Metric:
    """
    Classe Metric

    Classe générique permetant de définir des
    Métriques utilisées pour la spatialisation.
    La classe n'est pas destinée à être utilisée
    indépendanment, mais pour être un composant
    de Spatialisation.
    """

    def __init__(self, context, *args, **kwargs):
        self.context = context
        # self.values = self.context.raster.values

    def __str__(self):
        return self.__class__.__name__

    def compute(self, values, *args):
        # params = self.paramsCalc()
        values = self._compute(values, *args)
        return FuzzyRaster(array=values, meta=self.context.context.raster.raster_meta)

    def _compute(self, values, *args):
        raise NotImplementedError


class Nothing(Metric):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute(self, values, *args):
        return values


class Cell_Distance(Metric):
    """
    Classe Distance

    Hérite de la classe Metric. Destinée à calculer la
    distance à un point
    """

    default_structure = scipy.ndimage.generate_binary_structure(3, 1)

    def __init__(self, context, structure=None, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        # Définition du voisinage
        if structure:
            self.structure = structure
        else:
            self.structure = self.default_structure

    def _compute(self, values, *args):

        aa = np.zeros_like(values)
        bb = values + aa

        while np.min(bb) == 0:
            scipy.ndimage.binary_dilation(bb, structure=self.structure, output=aa)
            bb = bb + aa

        computeraster = np.max(bb) - bb

        return computeraster


class Cell_DistanceT(Cell_Distance):
    default_structure = scipy.ndimage.generate_binary_structure(3, 2)

    def __init__(self, context, structure=None, *args, **kwargs):
        super().__init__(context, *args, **kwargs)


class Distance(Metric):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute(self, values, *args):

        shape = values.shape
        notnullcells = np.argwhere(values != 0)

        if len(notnullcells) > 5:
            # version indexée, uniquement si le nombre
            # de valeurs non nulles est important
            z, y, x = np.indices(shape)
            indices = list(zip(np.ravel(z), np.ravel(y), np.ravel(x)))
            # Calcul de l'index
            tree = scipy.spatial.cKDTree(notnullcells)
            # Calcul de la distance
            dist, index = tree.query(indices)
            # Mise en forme du raster de sortie
            computeraster = dist.reshape(shape).astype(values.dtype)
        else:
            # version bruteforce sinon
            indices = np.indices(shape).transpose((1, 2, 3, 0))
            calc = notnullcells - indices[:, :, :, np.newaxis]
            calc_sqrt = np.square(calc).sum(4)
            # Mise en forme du raster de sortie
            computeraster = np.sqrt(np.min(calc_sqrt, 3), dtype=values.dtype)

        return computeraster


class Angle(Metric):
    """
    Classe Angle

    Hérite de la classe Metric. Destinée à calculer un angle.
    """

    def __init__(self, context, angle=0, *args, **kwargs):
        self.angle = angle
        super().__init__(context, *args, **kwargs)

    def _compute(self, values, *args):
        # Calcule l'angle par rapport à la première coordonée
        # de l'objet. A refaire
        angle = self.angle
        notnullcells = np.argwhere(values != 0)[0]
        shape = values.shape
        ang = angle + 90

        # Calcul [drow, dcol]
        # calc_delta =
        indices = np.indices(shape).transpose((1, 2, 3, 0))
        *_, x, y = np.split(notnullcells - indices, 3, axis=3)
        # Calcul atan
        calc_atan = np.squeeze(np.arctan2(x, y, dtype=values.dtype), axis=3)
        # conversion degrés
        computeraster = (np.degrees(calc_atan) - ang) % 360

        return computeraster


class EcartAngulaire(Angle):
    """
    Classe EcartAngulaire

    Hérite de la classe Angle. Modifie le résultat de la classe
    Angle pour obtenir une valeur entre -180 et 180 degrés, centrée
    sur l'angle fourni en paramètre lors de la création de la classe.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _compute(self, values, *args):
        ang = super()._compute(values, *args)
        angUp = ang
        angUp[angUp > 180] = angUp[angUp > 180] - 360
        return angUp


class DeltaVal(Metric):
    """
    Classe DeltaVal

    Hérite de la classe Metric. Destinée à calculer une différence de valeur
    """

    def __init__(self, context, values_raster, *args, **kwargs):
        self.values_raster = values_raster
        super().__init__(context, *args, **kwargs)

    def _compute(self, values, *args):
        ref_value = self._compute_refValue(values)
        computeraster = self.values_raster.values - ref_value
        return computeraster

    def _compute_refValue(self, values, *args):
        raise NotImplementedError


class DeltaMeanVal(DeltaVal):
    """
    Classe DeltaMeanVal

    Hérite de la classe DeltaVal. Calcule une différence de valeur à partir 
    de la moyenne des valeurs == 1 sur le raster net
    """

    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute_refValue(self, values):
        # Metric Altitude moyenne
        val = self.values_raster.values[values == 1.0]
        refVal = np.mean(val)
        return refVal


class DeltaMaxVal(DeltaVal):
    """
    Classe DeltaMaxVal

    Hérite de la classe DeltaVal. Calcule une différence de valeur à partir 
    du maximum des valeurs == 1 sur le raster net
    """

    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute_refValue(self, values):
        # Metric Altitude max
        val = self.values_raster.values[values == 1.0]
        refVal = np.max(val)
        return refVal


class DeltaMinVal(DeltaVal):
    """
    Classe DeltaMinVal

    Hérite de la classe DeltaVal. Calcule une différence de valeur à partir 
    du minimum des valeurs == 1 sur le raster net
    """

    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute_refValue(self, values):
        # Metric Altitude min
        val = self.values_raster.values[values == 1.0]
        refVal = np.min(val)
        return refVal


class DeltaNearestVal(DeltaVal):
    """
    Classe DeltaNearestVal
    """

    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

    def _compute_refValue(self, values):

        shape = values.shape
        notnullcells = np.argwhere(values != 0)
        z, y, x = np.indices(shape)

        notnullcells_val = self.values_raster.values.take(
            np.ravel_multi_index(notnullcells.T, shape)
        )
        computeraster = scipy.interpolate.griddata(
            notnullcells, notnullcells_val, (z, y, x), method="nearest"
        )

        return computeraster

