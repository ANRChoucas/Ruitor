FROM python:3-alpine

WORKDIR /usr/src/app

# Installation des dépendances
# Dépendances pour lxml
RUN apk add libxml2 libxml2-dev libxslt libxslt-dev

# Dépendances matplotlib
RUN apk add freetype-dev fribidi-dev harfbuzz-dev jpeg-dev lcms2-dev openjpeg-dev tcl-dev tiff-dev tk-dev zlib-dev

# Dépendances numpy
RUN apk add gcc gfortran build-base wget freetype-dev libpng-dev openblas-dev

# Dépendances rasterio
RUN apk add gdal gdal-dev

# Installation des paquets python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Nettoyage des paquets inutiles après compilation des dépendances
RUN apk del gcc gfortran build-base

# Copie des sources de RUITOR
COPY . .
WORKDIR /usr/src/app/src

# Démarage du serveur
EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
