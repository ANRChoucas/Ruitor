# RUITOR

## Mise en place


### Installation classique

**Pour windows priviliégier l'installation docker**

Prérequis:
- Python 3.9

1. Télécharger le dépôt

```sh
git clone https://github.com/MBunel/Ruitor/
cd ./Ruitor
# On utilise la branche "API" (temporaire)
git checkout API 
```

2. Création et activation de l'environnement virtuel

```sh
python -m venv ./venv
```
 On active l'environnement virtuel :

```sh
# Sous linux
source ./venv/bin/activate

# Sous windows
.\venv\Scripts\activate
```

3. Téléchargement et installation des dépendances

```sh
pip install -r ./requirements.txt
```

**NB :** à l'IGN il est nécessaire d'utiliser pip avec l'option ```--proxy```


```sh
pip install -r ./requirements.txt --proxy=http://proxy.ign.fr:3128
```

**NB :** Sous windows certaines dépendances (notamment `rasterio`) peuvent ne pas s'installer. Il faut donc installer manuellement `rasterio 1.2.1` et `gdal 3.2.2` en passant par les `wheels`, puis executer ```pip install -r ./requirements.txt --proxy=http://proxy.ign.fr:3128```. [La documention de rasterio](https://pypi.org/project/rasterio/#windows) détaille la procédure et donne le lien des wheels.

**NB 2 :** Sous windows le package `uvloop` (qui est dans les `requirements` et qui est demandé par `uvicorn`) ne fonctione pas, il faut donc le retirer du `requierement.txt`

#### Lancement du serveur

```sh
cd ./Ruitor
source ./venv/bin/activate
cd ./src
python -m uvicorn main:app --reload 
```

### Avec Docker

Prérequis:
- Docker

**NB :** Sur les ordinateurs IGN il est nécessaire de configurer le proxy pour pour pouvoir utiliser Docker. La procédure à suivre (sous linux avec `systemd`) est :

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



1. Télécharger le dépôt

```sh
git clone https://github.com/MBunel/Ruitor/
cd ./Ruitor
# On utilise la branche "API" (temporaire)
git checkout API 
```

2. Consruire l'image Docker

```sh
# Peut prendre beaucoup de temps
sudo docker build -t ruitor .
```

**NB :** Dans le cas où cette instruction est effectuée à l'IGN il est nécessaire de préciser (*une nouvelle fois*) le proxy. La commande à utiliser est donc :

```sh
# Variante de la commande pour le proxy IGN
sudo docker build --build-arg http_proxy=http://proxy.ign.3128 --build-arg https_proxy=http://proxy.ign.fr:3128 -t ruitor .
```

#### Lancement du serveur

```sh
sudo docker run -d --name ruitor_cont -p 8000:80 ruitor
```

**NB :** Par défaut Ruitor effectue ses calculs en parrallèle. `docker run` propose plusieurs options pour gérer la manière dont le conteneur utilise le CPU (voir   [la documentation de docker](https://docs.docker.com/config/containers/resource_constraints/#cpu))

## API

Une fois le serveur lancé on peut utiliser Ruitor à l'aide d'une API REST, décrite [ici](https://github.com/MBunel/Ruitor-Api).

Par défaut (que Ruitor soit installé par Docker ou non) le serveur écoute sur localhost:8000


## Documentation

Le code est documenté, pour construire la documentation il faut installer le paquet `sphinx` (qui n'est pas dans le `requirement.txt`), puis exécuter le code suivant :

```sh
cd ./Ruitor/doc
make html

firefox ./_build/html/index.html 
```

## À venir

## Pour plus de détails

- Bunel (2021), *Modélisation et raisonnement spatial flou pour l'aide de la localisation de victimes en montagne,* Thèse de doctorat. (publication à venir)
