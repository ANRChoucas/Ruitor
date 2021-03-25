# RUITOR

## Mise en place


### Installation classique

Prérequis:
- Python 3.9

1. Télécharger le dépôt

```sh
git clone https://github.com/MBunel/Ruitor/
cd ./Ruitor
# On utilise la branche "API" (temporaire)
git checkout API 
```

2. Création de l'environnement virtuel

```sh
python -m venv ./venv
```

3. Téléchargement et installation des dépendances

```sh
source ./venv/bin/activate
pip install -r ./requirements.txt
```

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

**NB :** Sur les ordinateurs IGN il est nécessaire de configurer le proxy pour pour pouvoir utiliser Docker. [Ce forum](https://stackoverflow.com/a/38386911) explique la procédure à suivre sous ubuntu.



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
