"""
"""

import numpy as np
from rasterio import features


class Rasterizer:
    """
    """

    def __init__(self, context):
        self.context = context

    def rasterize(self):
        """
        """
        geom = self._treat_geom(self.context.geom)
        return self._rasterize(geom)

    def _treat_geom(self, geom):
        raise NotImplementedError

    def _rasterize(self, geom):
        out_raster = np.zeros_like(self.context.context.raster.values)

        features.rasterize(
            geom,
            out=out_raster,
            transform=self.context.context.raster.raster_meta["transform"],
            all_touched=True,
            dtype=self.context.context.raster.raster_meta["dtype"],
        )

        return out_raster


class CentroidRasterizer(Rasterizer):
    """
    """

    def _treat_geom(self, geom):
        return [geom.centroid]


class ExteriorRasterizer(Rasterizer):
    """
    """

    def _treat_geom(self, geom):
        return [geom.exterior]


class GeometryRasterizer(Rasterizer):
    """
    """

    def _treat_geom(self, geom):
        return [geom]
