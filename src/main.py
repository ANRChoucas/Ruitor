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
import csv
import glob

from rasterio.windows import Window


import config
from ontologyTools import SROnto, ROOnto
from spatialisation import SpatialisationFactory
from fusion.Fusion import fusion
from fuzzyUtils.FuzzyRaster import FuzzyRaster

import messager


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


def set_zir(raster, zir):
    # Spécification du padding
    padding = {"x": 10, "y": 10}
    # Calcul Zir
    # Calcul des numéros de ligne et de colonne correspondant aux
    # deux points de la bbox
    row_ind, col_ind = zip(*map(lambda x: raster.index(*x), zir))
    # Extraction du numéro de ligne/colonne minimum
    row_min, col_min = min(row_ind), min(col_ind)
    # Calcul du nombre de lignes/colonnes
    row_num = abs(max(row_ind) - row_min) + padding["x"]
    col_num = abs(max(col_ind) - col_min) + padding["y"]
    # Définition de la fenêtre de travail
    return Window(col_min, row_min, col_num, row_num)


if __name__ == "__main__":
    # Import paramètres
    configuration(config)

    # Chargement ontologie
    sro = load_ontology(config.ontology, "SRO")

    # Import données
    mnt = load_mnt(config.data, name="BR")

    # Parsing requête
    parser = Parser("tests/xml/FilRouge.xml")
    spatialisationParms = parser.values
    factor = SpatialisationFactory(spatialisationParms, mnt, sro)
    test = list(factor.make_Spatialisation())

    parser2 = Parser("tests/xml/Debug.xml")
    spatialisationParms2 = parser2.values
    factor2 = SpatialisationFactory(spatialisationParms2, mnt, sro)
    test2 = list(factor2.make_Spatialisation())

    # Import MNT visibilité
    visibility_rasters_files = [
        rasterio.open(i) for i in glob.glob("data/visibility/*.tif")
    ]
    zir = [set_zir(i, parser2.values["zir"]) for i in visibility_rasters_files]
    rast_visib = [
        FuzzyRaster(raster=i, window=v) for i, v in zip(visibility_rasters_files, zir)
    ]
    fuzzy_prm = [(0, 0), (0.1, 1.0), (0.9, 1.0), (1, 0)]
    _ = [i.fuzzyfication(fuzzy_prm) for i in rast_visib]

    parser4 = Parser("tests/xml/FilRouge_direction.xml")
    spatialisationParms4 = parser4.values
    factor4 = SpatialisationFactory(spatialisationParms4, mnt, sro)
    test4 = list(factor4.make_Spatialisation())

    tc1 = time.time()
    logger.info("Computation")

    fuzz1 = (i.compute() for i in test)
    # Direction ski
    fuzz2 = test4[0].compute()
    # Temps marche
    fuzz3 = test2[0].compute()
    # visibilité
    fuzz4 = reduce(lambda x, y: x | y, rast_visib)

    # Agrégation des indices
    fuzz_list = [*fuzz1, fuzz2, fuzz3, fuzz4]
    fusioner = fusion(cellsize=50)
    fuzz, fuzz_note = fusioner.compute(fuzz_list, evaluate="rank")

    fuzz.summarize()
    fuzz_note.summarize()

    logger.info("Computation : Done")
    tc2 = time.time()

    # Export
    fuzz.write("_outTest/spatialisationResult.tif")
    fuzz_note.write("_outTest/spatialisationResult_eval.tif")

    # [
    #     i.write("_outTest/fuzz%s.tif" % (c + 1))
    #     for i, c in zip(fuzz_list, range(len(fuzz_list)))
    # ]

    if True:
        fuzzCnt = fuzz.contour()
        with open("_outTest/spatialisationResultIso.csv", "w") as csvfile:
            fieldnames = ["isoline", "value"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for row in fuzzCnt:
                writer.writerow({"isoline": row[0].wkt, "value": row[1]})

    time = tc2 - tc1

    logger.info("Done in %.2fs seconds", time)
    os.system("notify-send Ruitor done")

    if time > 120:
        messager.send_sms("Ruitor done in %.2f" % time)

