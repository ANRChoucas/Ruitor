# import rdflib
# from ontologyTools import Ontology
import logging
import logging.config
import os
from parser import Parser

import rasterio

import config
from spatialisation import Spatialisation

logger = logging.getLogger(__name__)


def set_proxy(url, port):
    proxy = "%s:%s" % (url, port)
    os.environ['http_proxy'] = proxy
    os.environ['HTTP_PROXY'] = proxy
    os.environ['https_proxy'] = proxy
    os.environ['HTTPS_PROXY'] = proxy

    logger.debug('Used proxy : %s' % proxy)


def load_mnt(params):
    file_folder = params['path']
    file_name = params['filename']
    file = os.path.join(file_folder, file_name)
    
    return rasterio.open(file)


def load_data(params, precision):
    rasters = [i for i in params['MNT'] if i['precision'] == precision]
    mnt = load_mnt(rasters[0])

    logger.debug('Used MNT : %s' % rasters[0]['name'])

    return mnt


if __name__ == "__main__":

    logging.config.dictConfig(config.logging_configuration)

    # Import paramètres
    set_proxy(**config.proxy)

    parser = Parser("data/xml/exemple3.xml")
    parameters = parser.values

    # Import données
    mnt = load_data(config.data, 25)
    #tt = rasterio.open("/home/mbunel/Bureau/tt.tif")

    t1 = rasterio.open("data/raster/test1.tif")

    if False:
        res = []

        for indice in parameters['indices']:
            prm = {
                'zir': parameters['zir'],
                'indices': indice
            }
            res.append(Spatialisation(prm, t1))

    test = Spatialisation(parameters, mnt)

    logger.info('Computation')
    fuzz = test.compute()
    logger.info('Computation : Done')

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
    logger.info('Done')
