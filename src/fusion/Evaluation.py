from skimage.measure import label, regionprops
from fuzzyUtils.FuzzyRaster import FuzzyRaster
import csv
import numpy as np

class Evaluator(object):
    def __init__(self, context):
        self.context = context

    def evaluate(self, zones):
        values = zones.values[0]
        meta = zones.raster_meta

        regions = self.regionalize(values)
        regions_descriptors = self.descriptors(regions)
        evalued_regions = self._evaluate(regions, regions_descriptors)

        temp_rt_val = evalued_regions.astype(meta["dtype"])[np.newaxis]

        return FuzzyRaster(array=temp_rt_val, meta=meta)

    def regionalize(self, raster_values):
        # Image binaire
        raster_values[raster_values > 0] = 1
        return label(raster_values, connectivity=2, background=0)

    def descriptors(self, regions):
        return regionprops(regions)

    def _evaluate(self, region, descriptors):
        raise NotImplementedError


class tt(Evaluator):
    def _evaluate(self, region, descriptors):
        self.write_descriptors("./out.csv", descriptors)
        return region

    def write_descriptors(self, file, descriptors):
        desc = [
            "area",
            "bbox",
            "bbox_area",
            "centroid",
            "convex_area",
            "eccentricity",
            "equivalent_diameter",
            "euler_number",
            "extent",
            "filled_area",
            "label",
            "major_axis_length",
            "minor_axis_length",
            "orientation",
            "perimeter",
            "solidity",
        ]

        with open(file, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=desc)
            writer.writerow({k:k for k in desc})
            for row in descriptors:
                writer.writerow({k:row[k] for k in desc})