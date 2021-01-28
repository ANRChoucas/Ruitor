"""
fichier main.py
"""

# Packages nécessaires pour la génération de l'api
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse

# Import des schémas de données personnalisés
from api_schema import Indice, Operateur, Evaluation

# Import des classes rasterio
import rasterio
from rasterio.io import MemoryFile

# Import des packages de la sdlib nécessaire
import io
from functools import reduce

# Import des modules de ruitor
from fuzzyUtils.FuzzyRaster import FuzzyRaster


# Initialisation


# Déclaration de l'api
app = FastAPI()

# Requête POST /spatialisation
@app.post("/spatialisation")
def spatialisation(indice: Indice, operateur: Operateur = None):
    """La fonction prend en entrée un indice de localisation et renvoie
    la zlc correspondante sous la forme d'un GeoTiff.
    """
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
    """
    La fonction prend en entrée un ensemble de fichiers GeoTiff,
    chacun représentant une zlc, et renvoie un seul GeoTiff,
    représentant la zlp.

    Plusieurs paramètres optionels peuvent être ajoutés dans la
    requête. Il est possible d'évaluer la qualité de la zlp construite
    (améliorations nécessaires) à l'aide du paramétre `evaluation`. Il
    est également possible de sélectioner la t-norme qui sera utilisée
    pour la fusion, à l'aide du paramètre `operateur`.

    test
    ----

    .. todo::
        - Implémentation de l'évaluation

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
    await StreamingResponse(byte_gtiff, media_type="image/tiff")
