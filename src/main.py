# import rdflib
# from ontologyTools import Ontology
import os
from parser import Parser

import rasterio

import config
from spatialisation import Spatialisation


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

    parser = Parser("data/xml/exemple3.xml")
    parameters = parser.values

    # Import données
    mnt = load_data(config.data)
    #tt = rasterio.open("/home/mbunel/Bureau/tt.tif")

    t1 = rasterio.open("data/raster/test1.tif")


    if False:
        res = []

        for indice in parameters['indices']:
            prm = {
                'zir': parameters['zir'],
                'indice': indice
            }
            res.append(Spatialisation(prm, t1))

    test = Spatialisation(parameters, mnt)
    fuzz = test.compute()

    # # Test convolution
    # from scipy import ndimage
    # import numpy as np
    # k = np.array([[[1,1,1],[1,1,1],[1,1,1]]])
    # fuzz.values = ndimage.convolve(fuzz.values, k)

    # Export
    fuzz.write("_outTest/test.tif")

    # g = rdflib.Graph()
    # result = g.parse("data/ontologies/relations_spatiales.owl")
    # aa = Ontology.Ontology(g)
    print("ok")
