# import rdflib
# from ontologyTools import Ontology
import os
import rasterio
from tt.Parser import Parser
from rasterio.windows import Window
from fuzzyUtils.FuzzyRaster import FuzzyRaster
from spatialisation.Spatialisation import Spatialisation

import config


def set_proxy(url, port):
    proxy = "%s:%s" % (url, port)
    os.environ['http_proxy'] = proxy
    os.environ['HTTP_PROXY'] = proxy
    os.environ['https_proxy'] = proxy
    os.environ['HTTPS_PROXY'] = proxy


def load_mnt(params):
    file_folder = params['path']
    file_name = params['name']
    file = os.path.join(file_folder, file_name)
    return rasterio.open(file)


def load_data(params):
    mnt = load_mnt(params['MNT'])
    return mnt


if __name__ == "__main__":

    # Import paramètres
    set_proxy(**config.proxy)

    parser = Parser("src/tt/exemple2.xml")

    # Import données
    mnt = load_data(config.data)

    tt = rasterio.open("/home/mbunel/Bureau/tt.tif")

    test = Spatialisation("aa", tt, parser.zir)
    fuzz = test.compute()

     # Export
    fuzz.raster_meta['driver'] = 'GTiff'
    fuzz.write("/home/mbunel/Bureau/test.tif")

    # g = rdflib.Graph()
    # result = g.parse("data/ontologies/relations_spatiales.owl")
    # aa = Ontology.Ontology(g)
    print("ok")
