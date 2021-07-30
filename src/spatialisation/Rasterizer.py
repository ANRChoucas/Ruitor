"""
"""
import logging
import numpy as np
from rasterio import features

LOGGER = logging.getLogger(__name__)


class Rasterizer:
    """
    Classe Rasterizer

    Destinée à gérér la rasterisation d'une géométrie. 
    Il s'agit d'une classe abstraite n'implémentant pas la méthode
    _treat_geom transformant une géométrie avant de la rasteriser
    """

    def __init__(self, context):
        self.context = context

    def rasterize(self):
        """
        Fonction de rasterisation

        Destinée à être appelée par une instance de spatialisation Element
        pour construire un fuzzy raster
        """
        try:
            geom = self._treat_geom(self.context.geom)
            out_raster = self._rasterize(geom)
        except TypeError:
            out_raster = []
            for g in self.context.geom:
                geom = self._treat_geom(g)
                out_raster.append(self._rasterize(geom))

        return out_raster

    def _treat_geom(self, geom):
        raise NotImplementedError

    def _rasterize(self, geom, all_touched=True):
        out_raster = np.zeros_like(self.context.context.raster.values)

        features.rasterize(
            geom,
            out=out_raster,
            transform=self.context.context.raster.raster_meta["transform"],
            all_touched=all_touched,
            dtype=self.context.context.raster.raster_meta["dtype"],
        )

        return out_raster


class Boundary(Rasterizer):
    """
    Classe Boundary

    Surcharge la fonction _treat_geom de la
    classe rasterizer.

    La géométrie est modifiée avant rasterisation.
    Seules les frontières sont rasterisées. Dans le
    cas de polygones possédant un intérieur les frontières
    intérieures sont également rasterisées (contrairement à 
    la classe Exterior)
    """

    def _treat_geom(self, geom):
        return [geom.boundary]


class Centroid(Rasterizer):
    """
    Classe Centroid

    Surcharge la fonction _treat_geom de la
    classe rasterizer.

    Seul le centroide de la géométrie est rasterisé
    """

    def _treat_geom(self, geom):
        return [geom.centroid]


class ConvexHull(Rasterizer):
    """
    Classe Boundary

    Surcharge la fonction _treat_geom de la
    classe rasterizer

    L'enveloppe convexte de la géométrie est
    rasterisé (intérieur inclus)
    """

    def _treat_geom(self, geom):
        return [geom.convex_hull]


class Envelope(Rasterizer):
    """
    Classe Boundary

    Surcharge la fonction _treat_geom de la
    classe rasterizer

    La bbox de la géométrie est
    rasterisé (intérieur inclus)
    """

    def _treat_geom(self, geom):
        return [geom.envelope]


class Exterior(Rasterizer):
    """
    Classe Boundary

    Surcharge la fonction _treat_geom de la
    classe rasterizer

    Seule la frontière extérieure est rastérisée.
    Dans le cas où l'objet n'a pas d'extérieur (Point, LineString)
    c'est la géométrie initiale qui est retournée
    """

    def _treat_geom(self, geom):
        try:
            exterior = geom.exterior
        except AttributeError:
            exterior = geom
        return [exterior]


class Geometry(Rasterizer):
    """
    Classe Boundary

    Surcharge la fonction _treat_geom de la
    classe rasterizer

    Aucune modification avant rasterisation
    """

    def _treat_geom(self, geom):
        return [geom]


class Interior(Rasterizer):
    """
    Classe Boundary

    Surcharge la fonction _treat_geom de la
    classe rasterizer

    Seule les frontières intérieures de l'objet
    est rasterisée. Dans le cas où l'objet
    n'a pas de frontière intérieures, c'est la
    frontière extérieure qui est spatialisée.

    Dans le cas où l'objet est de type Point ou
    LineString c'est la géométrie initiale qui
    est retournée.
    """

    def _treat_geom(self, geom):
        try:
            interior = geom.interiors
            if interior:
                return [*interior]
            else:
                return [geom.exterior]
        except AttributeError:
            return [geom]
