# RUITOR

## Mise en place

### Installation

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

### Lancement du serveur

```sh
cd ./Ruitor
source ./venv/bin/activate
cd ./src
python -m uvicorn main:app --reload 
```

## API

Une fois le serveur lancé on peut utiliser Ruitor à l'aide d'une API REST, décrite [ici](https://github.com/MBunel/Ruitor-Api). 

## Documentation

Le code est documenté, pour construire la documentation :

```sh
cd ./Ruitor
source ./venv/bin/activate

pip install sphinx

cd ./doc
make html

firefox ./_build/html/index.html 
```

## À venir

## Pour plus de détails

- Bunel (2021), *Modélisation et raisonnement spatial flou pour l'aide de la localisation de victimes en montagne,* Thèse de doctorat. (publication à venir)
