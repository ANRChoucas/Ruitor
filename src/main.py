"""
fichier main.py
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from typing import Optional
from api_schema import Indice, Operateur

import rasterio
from rasterio.io import MemoryFile
import io

from fuzzyUtils.FuzzyRaster import FuzzyRaster

from functools import reduce

app = FastAPI()


@app.post("/spatialisation")
def read_root(indice: Indice, operateur: Optional[Operateur]):
    return {"Hello": "World"}


@app.post("/fusion")#, response_model=StreamingResponse)
async def testouille(operateur: Optional[Operateur], files:
                     list[UploadFile] = File(...)):

    rasterio_files = []
    
    for f in files:
        # Ouverture fichier
        with MemoryFile(f.file) as memory_file:
            with memory_file.open() as dataset:
                f_raster = FuzzyRaster(raster=dataset)
                rasterio_files.append(f_raster)

    raster_fusion = reduce(lambda x, y: x | y, rasterio_files)
    
    mf = MemoryFile()
    tt = raster_fusion.memory_write(mf)
    
    return StreamingResponse(io.BytesIO(tt.read()), media_type="image/tiff")

