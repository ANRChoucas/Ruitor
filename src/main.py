"""
fichier main.py
"""

import logging
import logging.config
import os
import time
from parser import Parser
from functools import reduce
import rasterio

import config
from ontologyTools import SROnto, ROOnto
from spatialisation import SpatialisationFactory


logger = logging.getLogger(__name__)


def set_proxy(url, port):
    proxy = "%s:%s" % (url, port)

    os.environ["http_proxy"] = proxy
    os.environ["HTTP_PROXY"] = proxy
    os.environ["https_proxy"] = proxy
    os.environ["HTTPS_PROXY"] = proxy

    logger.info("The proxy : %s is used" % proxy)


def load_mnt(params, name=None, precision=None):
    if name:
        rasters = [i for i in params["MNT"] if i["name"] == name]
    elif precision:
        rasters = [i for i in params["MNT"] if i["precision"] == precision]
    else:
        raise ValueError("No Mnt corresponding")
    mntfile = get_file(rasters[0])

    logger.debug(
        "Used MNT : %s (precision %s)" % (rasters[0]["name"], rasters[0]["precision"])
    )

    return rasterio.open(mntfile)


def get_file(params):
    file_folder = params["path"]
    file_name = params["filename"]
    file = os.path.join(file_folder, file_name)

    return file


def load_ontology(params, onto_type):
    onto_dispacher = {"SRO": SROnto, "ROO": ROOnto}
    ontology = [i for i in params if i["type"] == onto_type]
    ontology_file = get_file(ontology[0])

    logger.debug("Used ontology : %s" % ontology[0]["type"])

    return onto_dispacher[onto_type](ontology_file)


def configuration(config):
    # Configuration logging
    logging.config.dictConfig(config.logging_configuration)

    # Définition proxy
    try:
        set_proxy(**config.proxy)
    except AttributeError:
        logger.debug("No proxy used")


if __name__ == "__main__":
    # Import paramètres
    configuration(config)

    # Chargement ontologie
    sro = load_ontology(config.ontology, "SRO")

    # Import données
    mnt = load_mnt(config.data, name="MR")

    # Parsing requête
    parser = Parser("tests/xml/FilRouge.xml")
    spatialisationParms = parser.values
    factor = SpatialisationFactory(spatialisationParms, mnt, sro)
    test = list(factor.make_Spatialisation())

    # parser2 = Parser("tests/xml/GrandVeymont_entre.xml")
    # spatialisationParms2 = parser2.values
    # factor2 = SpatialisationFactory(spatialisationParms2, mnt, sro)
    # test2 = list(factor2.make_Spatialisation())

    # parser3 = Parser("tests/xml/GrandVeymont_auDela.xml")
    # spatialisationParms3 = parser3.values
    # factor3 = SpatialisationFactory(spatialisationParms3, mnt, sro)
    # test3 = list(factor3.make_Spatialisation())

    tc1 = time.time()
    logger.info("Computation")

    #fuzz1 = reduce(lambda x, y: x & y, (i.compute() for i in test[:-2]))
    #fuzz2 = reduce(lambda x, y: x & y, (i.compute() for i in test2))
    #fuzz3 = reduce(lambda x, y: x & y, (i.compute() for i in test3))

    #fuzz = fuzz3#fuzz1 & fuzz2 & fuzz3 
    fuzz = reduce(lambda x, y: x & y, (i.compute() for i in test))

    logger.info("Computation : Done")
    tc2 = time.time()

    # Test convolution
    # from scipy import ndimage
    # import numpy as np
    # k = np.array([[[0,1,0],[0,1,0],[0,1,0]]])
    # fuzz.values = ndimage.convolve(fuzz.values, k)

    # Export
    fuzz.write("_outTest/spatialisationResult.tif")

    logger.info("Done in %s seconds", tc2 - tc1)
    os.system("notify-send Ruitor done")
