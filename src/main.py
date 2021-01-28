"""
fichier main.py
"""

from fastapi import FastAPI, File, UploadFile

from fastapi.responses import StreamingResponse

from typing import Optional
from api_schema import Indice, Operateur, Evaluation

import rasterio
from rasterio.io import MemoryFile
import io

from fuzzyUtils.FuzzyRaster import FuzzyRaster

from functools import reduce

# Initialisation


# Déclaration de l'api
app = FastAPI()

# Requête POST /spatialisation
@app.post("/spatialisation")
def spatialisation(indice: Indice, operateur: Optional[Operateur]):
    return {"Hello": "World"}


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
    operateur: Operateur = None,
    evaluation: Evaluation = None,
    files: list[UploadFile] = File(...),
):

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
    await StreamingResponse(byte_gtiff, media_type="image/tiff")
