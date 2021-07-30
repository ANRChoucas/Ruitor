# RUITOR

## Mise en place

Deux modes d'installation sont possibles. 

1. Installation classique, avec un environement virtuel python
2. Utilisation d'une image Docker

**NB :** La première méthode d'installation peut être difficile à utiliser sous windows, il vaut mieux privilégier docker (nécessite Windows X)

### Installation "classique"

#### Prérequis:
- Python 3.9 [**Windows :** le python de Qgis ne compte pas]
- Visual C++ [Uniquement pour **Windows** et l'installation des dépendances]

#### Installation :

1. Télécharger le dépôt

La commande ```git clone``` permet de télécharger un dépôt distant

```sh
git clone https://github.com/MBunel/Ruitor/
cd ./Ruitor
```

**NB IGN :** Pour fonctioner derrière le proxy IGN il peut être nécessaire de modifier la configuration de git. En cas d'erreur de la forme : ```unable to access '...' Couldn't resolve host '...'``` voir ce document : [Configure Git to use a proxy](https://gist.github.com/evantoli/f8c23a37eb3558ab8765).

La version la plus récente de Ruitor se trouve dans la branche "API", il faut donc utiliser git pour passer sur la bonne branche.

```sh
# On utilise la branche "API" (temporaire)
git checkout API 
```

2. Création et activation de l'environnement virtuel

```sh
# Attention à bien être dans le dossier de Ruitor
python -m venv ./venv
```

**NB Windows :** Si windows indique ne pas trouver python alors qu'il est bien installé c'est probablement car l'exécutable python n'est pas dans le path windows. Dans ce cas suivre les instructions de [ce post sur stackowerflow](https://stackoverflow.com/a/54934172).

 On active l'environnement virtuel :

- Sous linux :

```sh
# Attention à bien être dans le dossier de Ruitor
source ./venv/bin/activate
```

- Sous windows :
```
# Attention à bien être dans le dossier de Ruitor
.\venv\Scripts\activate
```

Si l'activation s'est bien passée le prompt du terminal doit être préfixé de ```(venv)```. Par exemple : ```(venv) /Ruitor $```

3. Téléchargement et installation des dépendances

```sh
# Attention à bien être dans le dossier de Ruitor
pip install -r ./requirements.txt
```

**NB IGN:** à l'IGN il est nécessaire d'utiliser pip avec l'option ```--proxy``` :

```sh
# Attention à bien être dans le dossier de Ruitor
pip install -r ./requirements.txt --proxy=http://proxy.ign.fr:3128
```

**NB Windows:** Certaines dépendances (notamment `rasterio`) peuvent ne pas s'installer. Il faut donc installer manuellement `rasterio 1.2.1` et `gdal 3.2.2` en passant par les `wheels`, puis executer ```pip install -r ./requirements.txt --proxy=http://proxy.ign.fr:3128```. [La documention de rasterio](https://pypi.org/project/rasterio/#windows) détaille la procédure et donne le lien des wheels.

**NB Windows 2:** Le package `uvloop` (qui est dans les `requirements` et qui est demandé par `uvicorn`) ne fonctione pas, il faut donc le retirer du `requierement.txt`

### Avec Docker

#### Prérequis:
- Docker

**NB IGN:** Il est nécessaire de configurer le proxy pour pour pouvoir utiliser Docker. La procédure à suivre (sous linux avec `systemd`) est :

- Sous Windows :

Le proxy est configurable dans les options du client graphique Docker

- Sous Linux :

1. Créer le dossier `docker.service.d`

```sh
mkdir /etc/systemd/system/docker.service.d
```

2. Créer le fichier `http-proxy.conf` dans ce dossier et y ajouter les lignes suivantes :

```sh
[Service]
Environment="HTTP_PROXY=http://proxy.ign.fr:3128/"
Environment="HTTPS_PROXY=http://proxy.ign.fr:3128/"
```

3. Redémarer le service docker

```sh
systemctl daemon-reload
systemctl restart docker
```

Source : [ce forum](https://stackoverflow.com/a/38386911).

#### Installation

1. Télécharger le dépôt

La commande ```git clone``` permet de télécharger un dépôt distant

```sh
git clone https://github.com/MBunel/Ruitor/
cd ./Ruitor
```

**NB IGN :** Pour fonctioner derrière le proxy IGN il peut être nécessaire de modifier la configuration de git. En cas d'erreur de la forme : ```unable to access '...' Couldn't resolve host '...'``` voir ce document : [Configure Git to use a proxy](https://gist.github.com/evantoli/f8c23a37eb3558ab8765).

La version la plus récente de Ruitor se trouve dans la branche "API", il faut donc utiliser git pour passer sur la bonne branche.

```sh
# On utilise la branche "API" (temporaire)
git checkout API 
```

2. Consruire l'image Docker

```sh
# Peut prendre beaucoup de temps
docker build -t ruitor .
```

**NB Linux:** Les commandes Docker peuvent nécessiter les droits superutilisateur (utiliser ```sudo```)

**NB IGN:** Il est nécessaire de préciser (*une nouvelle fois*) le proxy. La commande à utiliser est donc :

```sh
# Variante de la commande pour le proxy IGN
docker build --build-arg http_proxy=http://proxy.ign.3128 --build-arg https_proxy=http://proxy.ign.fr:3128 -t ruitor .
```

## Lancement du serveur

- Si l'installation a été faite "normalement"

```sh
cd ./Ruitor
source ./venv/bin/activate
cd ./src
python -m uvicorn main:app --reload 
```

- Si l'installation a été faite par docker

```sh
docker run -d --name ruitor_cont -p 8000:80 ruitor
```

**NB :** Par défaut Ruitor effectue ses calculs en parrallèle. `docker run` propose plusieurs options pour gérer la manière dont le conteneur utilise le CPU (voir   [la documentation de docker](https://docs.docker.com/config/containers/resource_constraints/#cpu))

## API

Une fois le serveur lancé on peut utiliser Ruitor à l'aide d'une API REST, décrite [ici](https://github.com/MBunel/Ruitor-Api).

Par défaut (que Ruitor soit installé par Docker ou non) le serveur écoute sur localhost:8000

## Documentation

Le code est documenté, pour construire la documentation il faut installer le paquet `sphinx` (qui n'est pas dans le `requirement.txt`), puis exécuter le code suivant :

```sh
cd 
make html
```

Le fichier d'index de la documention est : ```./Ruitor/doc/_build/html/index.html ```

## À venir

- Ajouter une requête pour connaitre l'emprise de la zone du calcul
- Clarifier la documentation sur le système de coordonées utilisé
- Régler le problème des CORS
- Maj documentation

## Pour plus de détails

- Bunel (2021), [*Modélisation et raisonnement spatial flou pour l'aide de la localisation de victimes en montagne,*](https://tel.archives-ouvertes.fr/tel-03298717) Thèse de doctorat.
