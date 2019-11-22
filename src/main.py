# import rdflib
from ontologyTools import SROnto, ROOnto
import logging
import logging.config
import os
from parser import Parser

import config
import rasterio
from spatialisation import Spatialisation

logger = logging.getLogger(__name__)


def set_proxy(url, port):
    proxy = "%s:%s" % (url, port)

    os.environ["http_proxy"] = proxy
    os.environ["HTTP_PROXY"] = proxy
    os.environ["https_proxy"] = proxy
    os.environ["HTTPS_PROXY"] = proxy

    logger.info("The proxy : %s is used" % proxy)


def load_mnt(params, precision):
    rasters = [i for i in params["MNT"] if i["precision"] == precision]
    mntfile = get_file(rasters[0])

    logger.debug("Used MNT : %s" % rasters[0]["name"])

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

    temp = sro.get_from_iri(
        "http://www.semanticweb.org/mbunel/ontologies/Ornitho#Proximal"
    )
    tt = sro.fun(temp)

    # Parsing requête
    parser = Parser("data/xml/exemple4.xml")
    parameters = parser.values

    # Import données
    mnt = load_mnt(config.data, 25)

    if False:
        res = []

        for indice in parameters["indices"]:
            prm = {"zir": parameters["zir"], "indices": indice}
            res.append(Spatialisation(prm, t1))

    test = Spatialisation(parameters, mnt)

    logger.info("Computation")
    fuzz = test.compute()
    logger.info("Computation : Done")

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
    logger.info("Done")
