FROM python:3

WORKDIR /usr/src/app


# Installation des paquets python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie des sources de RUITOR
COPY ./src ./src
COPY ./data ./data

WORKDIR /usr/src/app/src

# Démarage du serveur
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
