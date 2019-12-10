# import rdflib
from ontologyTools import SROnto, ROOnto
import logging
import logging.config
import os
from parser import Parser

import config
import rasterio
from spatialisation import SpatialisationFactory

from functools import reduce

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


def load_ontology(params, type):
    ontoDispacher = {"SRO": SROnto, "ROO": ROOnto}
    ontology = [i for i in params if i["type"] == type]
    ontologyFile = get_file(ontology[0])

    logger.debug("Used ontology : %s" % ontology[0]["type"])

    return ontoDispacher[type](ontologyFile)


def configuration(configuration):
    # Configuration logging
    logging.config.dictConfig(configuration.logging_configuration)

    # Définition proxy
    try:
        set_proxy(**configuration.proxy)
    except AttributeError:
        logger.debug("No proxy used")


if __name__ == "__main__":
    # Import paramètres
    configuration(config)

    # Chargement ontologie
    sro = load_ontology(config.ontology, "SRO")

    # Parsing requête
    parser = Parser("tests/xml/GrandVeymont_entre.xml")
    spatialisationParms = parser.values

    # Import données
    mnt = load_mnt(config.data, name="HR_Veymont")

    factor = SpatialisationFactory(spatialisationParms, mnt, sro)
    test = list(factor.make_Spatialisation())

    if False:
        res = []

        for indice in parameters["indices"]:
            prm = {"zir": parameters["zir"], "indices": indice}
            res.append(Spatialisation(prm, t1))

    # test = Spatialisation(parameters, mnt)

    logger.info("Computation")
    fuzz = reduce(lambda x, y: x & y, (i.compute() for i in test))
    logger.info("Computation : Done")

    # # Test convolution
    # from scipy import ndimage
    # import numpy as np
    # k = np.array([[[1,1,1],[1,1,1],[1,1,1]]])
    # fuzz.values = ndimage.convolve(fuzz.values, k)

    # Export
    fuzz.write("_outTest/spatialisationResult.tif")

    # g = rdflib.Graph()
    # result = g.parse("data/ontologies/relations_spatiales.owl")
    # aa = Ontology.Ontology(g)
    logger.info("Done")
