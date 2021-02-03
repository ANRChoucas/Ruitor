"""
fichier main.py
"""

# Packages nécessaires pour la génération de l'api
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import StreamingResponse

from typing import Optional

# Import des schémas de données personnalisés
from api_schema import Indice, Operateur, Evaluator, EvaluationMetric

# Import des classes rasterio
import rasterio
from rasterio.io import MemoryFile

# Import des packages de la sdlib nécessaire
import io
from functools import reduce

# Import des modules de ruitor
from fuzzyUtils.FuzzyRaster import FuzzyRaster

import numpy as np


DESC_CONFIANCE = """La confiance est une valeur que le secouriste peut
définir pour donner une indication sur sa croyance en la véracité de
l'indice de localisation.

Cette valeur est optionelle. Si aucune valeur n'est fournie l'indice
est spatialisé avec une certitude maximale, 1.

La valeur de la confiance doit être comprise dans l'intervalle
[0,1]"""


# Initialisation


# Déclaration de l'api
app = FastAPI()

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
        None,
        ge=0,
        le=1,
        description=DESC_CONFIANCE,
    ),
):
    """La fonction prend en entrée un indice de localisation et renvoie la
      zlc correspondante sous la forme d'un GeoTiff.

    **Les arguments cette fonction ne sont pas encore fixés.**



    """

    raster_temp = FuzzyRaster(array=np.zeros((2, 2)))

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
