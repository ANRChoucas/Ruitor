"""
fichier main.py
"""

# Packages nécessaires pour la génération de l'api
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import StreamingResponse

from typing import Optional

# Import des schémas de données personnalisés
from api_schema import Indice, Operateur, Evaluator, EvaluationMetric

import logging
import logging.config

# Import des classes rasterio
import rasterio
from rasterio.io import MemoryFile

# Import des packages de la sdlib nécessaire
import io
import os
from functools import reduce

# Import des modules de ruitor
from fuzzyUtils.FuzzyRaster import FuzzyRaster
from fusion.Fusion import fusion
from ontologyTools import SROnto, ROOnto
from spatialisation import SpatialisationFactory
from parser import JSONParser


import numpy as np

import config



DESC_CONFIANCE = """La confiance est une valeur que le secouriste peut
définir pour donner une indication sur sa croyance en la véracité de
l'indice de localisation.

Cette valeur est optionelle. Si aucune valeur n'est fournie l'indice
est spatialisé avec une certitude maximale, 1.

La valeur de la confiance doit être comprise dans l'intervalle
[0,1]"""


logger = logging.getLogger(__name__)


# Fonctions d'initialisation
def set_proxy(url, port):
    """
    Fonction permettant la définition du proxy (usage ign)
    """
    
    proxy = "%s:%s" % (url, port)

    os.environ["http_proxy"] = proxy
    os.environ["HTTP_PROXY"] = proxy
    os.environ["https_proxy"] = proxy
    os.environ["HTTPS_PROXY"] = proxy
    
    logger.info("The proxy : %s is used" % proxy)


def load_mnt(params, name=None, precision=None):
    """
    Fonction permettant de charger le MNT pour la spatialisation
    """
    
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


# Initialisation

# Chargement de la configuration 
configuration(config)

# Chargement ontologie ORL
sro = load_ontology(config.ontology, "SRO")

# Import données
mnt = load_mnt(config.data, name="BR")

# Déclaration de l'api
app = FastAPI()

# Définition points entrée API

# Requête POST /spatialisation
@app.post(
    "/spatialisation",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"image/tiff": {}},
            "description": "Retourne un GeoTiff représentant la ZLC",
        }
    },
)
def spatialisation(
    indice: Indice,
    operateur: Operateur = None,
    confiance: Optional[float] = Query(
        1,
        ge=0,
        le=1,
        description=DESC_CONFIANCE,
    ),
):
    """La fonction prend en entrée un indice de localisation et renvoie la
      zlc correspondante sous la forme d'un GeoTiff.
    """

    print("DD")

    parser = JSONParser(indice, confiance)

    
    spatialisationParms = parser.values   
    
    factor = SpatialisationFactory(spatialisationParms, mnt, sro)

    test = list(factor.make_Spatialisation())

    raster_temp = test[0].compute()


    memory_file = MemoryFile()
    memory_fusion_gtiff = raster_temp.memory_write(memory_file)
    byte_gtiff = io.BytesIO(memory_fusion_gtiff.read())

    # Renvoi du résultat (lent, à voir)
    return StreamingResponse(byte_gtiff, media_type="image/tiff")




# Requête POST /fusion
@app.post(
    "/fusion",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"image/tiff": {}},
            "description": "Retourne un GeoTiff représentant la ZLP",
        }
    },
)
async def fusion(
    operator: Operateur = None,
    evaluator: Evaluator = None,
    evaluation_metric: EvaluationMetric = None,
    files: list[UploadFile] = File(...),
):
    """La fonction prend en entrée un ensemble de fichiers GeoTiff,
    chacun représentant une zlc, et renvoie un seul GeoTiff,
    représentant la zlp.

    **Le format de retour risque d'être modifié. En effet l'évaluation
      conduit à construire un nouveau raster, il est possible qu'a
      terme deux GeoTiff soient retournés, le premier correspondant à
      la ZLP et le second à l'évaluation de composantes de la ZLP.**

    Plusieurs paramètres optionels peuvent être ajoutés dans la
    requête. Il est possible d'évaluer la qualité de la zlp construite
    (améliorations nécessaires) à l'aide des paramètres `evaluator` et
    `evaluation_metric`. Il est également possible de sélectioner la
    t-norme qui sera utilisée pour la fusion, à l'aide du paramètre
    `operator`.

    """

    rasterio_files = []

    # Ouverture (en mémoire) des fichiers transmis par la requête
    for f in files:
        with MemoryFile(f.file) as memory_file:
            with memory_file.open() as dataset:
                # Création du raster correspondant
                f_raster = FuzzyRaster(raster=dataset)
                # Ajout du raster à la liste à fusioner
                rasterio_files.append(f_raster)

    # Réalisation de la fusion
    raster_fusion = reduce(lambda x, y: x | y, rasterio_files)

    # fusioner = fusion(cellsize=50)
    # fuzz, fuzz_note = fusioner.compute(fuzz_list, evaluate="note")

    # Mise en forme du résultat
    memory_file = MemoryFile()
    memory_fusion_gtiff = raster_fusion.memory_write(memory_file)
    byte_gtiff = io.BytesIO(memory_fusion_gtiff.read())

    # Renvoi du résultat (lent, à voir)
    return StreamingResponse(byte_gtiff, media_type="image/tiff")
