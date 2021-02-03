"""
Fichier contenant l'ensemble des 
"""

from typing import Optional, Union, Tuple, List
from enum import Enum
from pydantic import BaseModel, Field, AnyUrl
from geojson_pydantic import features, utils
from fastapi import File, UploadFile


DESC_SITE = """Site utilisé pour la spatialisation de l'indice de localisaition.

Le site peut être de plusieurs types, en fonctions des paramètres de
la relation de localisation utilisée.

Si la relation ne demande qu'un site (cas classique), le site fourni
dans le corps de la requête doit être une `FeatureCollection`
geojson. Chacune des features de cette collection est traitée comme un
site séparé et la fonction de spatialisation renvoie la zone qui
correspond à **l'union** des ZLC construites pour chacun de ces sites.

Dans le cas où la relaiton nécessite deux (ou plus) sites
(p. ex. `orl#EntreXEtY`) alors le site fourni dans le cœur de la
requête doit être une liste de liste de Features. La liste la plus
"profonde" contient toutes les sites qui seront passés à la fonction
de spatialisation lors de la spatialisation pour une configuration
donnée. La liste de plus haut niveau contient toutes les listes de
sites qui seront utilisées pour générer les ZLC, lesquelles seront
ensuite unies pour créer la ZLC finale (elles jouent le même rôle que
la FeatureCollection dans le premier cas).


#### Dans le cas d'une relation simple (proche), avec un objet
```site = FeatureCollection(geom1)```

####  Dans le cas d'une relation simple (proche), avec plusieurs objets
```site = FeatureCollection(geom1, geom2, ...)```

####  Dans le cas d'une relation complexe (entre), avec un objet
```site = [[site1, site2]]```

####  Dans le cas d'une relation complexe (entre), avec plusieurs objets
```site = [[site1, site2], [site2, site3], ...]```

"""

# Types génériques
class Mnt(str, Enum):
    tt = "5"
    ttt = "50"
    tttt = "100"


# Types spatialisation
class Modifieur(BaseModel):
    """
    Classe définissant le type modifieur
    """

    # Les modifieurs sont définis dans l'ontologie ORL. Pour
    # identifier le modifieur utrilisé il faut fournir son url
    uri: AnyUrl = Field(description="Uri du modifieur dans l'ontologie ORL")


class RelationLocalisation(BaseModel):
    """Relation de localisation utilisée pour l'indice de localisation
    spatialisé

    """

    # La relation spatiale est définie par une uri, qui permet
    # d'identifier le concept dans l'ontologie ORL. C'est dans cette
    # ontologie qu'est définie la méthode de spatialisation de la
    # relation de localisation
    uri: AnyUrl = Field(
        description="Uri de la relation de localisation dans l'ontologie ORL"
    )
    # La spatialisation peut être modifié par l'ajout d'un, ou
    # plusieurs modifieurs. L'emploi des modifieurs est totalement
    # facultatif.
    modifieurs: Optional[list[Modifieur]] = Field(
        description="Liste des modifieurs à appliquer à la relation de localisation"
    )


class Indice(BaseModel):
    """
    Documentation
    """

    zir: utils.BBox = Field(
        description="Boundig Box de la Zone initiale de recherche (ZIR)"
    )
    # cible: Optional[str]
    relationLocalisation: RelationLocalisation
    site: Union[List[Tuple[features.Feature, ...]], features.FeatureCollection] = Field(
        description=DESC_SITE
    )


# Types Fusion

## Corps Fusion
class Operateur(str, Enum):
    """Défini la famille d'opérateurs flous utilisés pour les opérations
    d'intersection et d'union inter-raster flous.

    Les opérateurs flous sont décrits dans les Chapitres 3 et 8 de la
    la thèse. Le changement des opérateurs de construction a une
    influence considérable sur la ZLC ou la ZLP obtenue. En cas de
    doute se référer au chapitre 8 de la thèse.

    **Bien que cela demeure possible, il n'est pas conseillé de changer
    d'opérateurs entre la spatialisation et la fusion.**

    ```"Zadeh"``` est le paramètre par défaut. Lorsque l'on utilise ce
    paramètre les intersections sont calculés à l'aide de la *t-norme*
    de Zadeh, dont la définition est la suivante :
    t-norme(a,b)=min(a,b) et les unions à l'aide de la t-conorme de
    Zadeh, dont la définition est : t-conorme(a,b)=max(a,b).

    Lorsque la valeur du paramètre est ```"Lukacewiz"``` alors les
    intersections sont calculées à l'aide de la t-norme de Lukacewiz,
    dont la définition est : t-norme(a,b) = max(a+b-1,0) et les union
    à l'aide de la t-conorme de Lukacewicz dont la définition est :
    t-conorme(a,b) = min(a+b,1).

    La valeur ```"Probabiliste"``` permet d'utiliser la t-norme
    probabiliste dont la définition est : t-norme(a,b)=a*b et la
    t-conorme probabiliste dont la définition est :
    t-conorme(a,b)=a+b-a*b.

    La valeur ```"Nilpotent"``` permet d'utiliser la t-norme
    nilpotente dont la définition est : t-norme(a,b)= min(a,b) si a+
    b>1, 0 sinon; et la t-conorme nipotente dont la définition est :
    t-conorme(a,b)=max(a,b) si a+b < 1, 1 sinon.

    La valeur ```"Drastique"``` permet d'utiliser la t-norme
    drastique, dont la définition est : t-norme(a,b) = b si a = 1, a
    si b = 1, 0 sinon; et la t-conorme probabiliste dont la définition
    est : t-conorme(a,b) = b si a = 0, a si b=0; 1 sinon.

    """

    zadeh = "Zadeh"
    lukacewicz = "Lukacewiz"
    probabiliste = "Probabiliste"
    nilpotent = "Nilpotent"
    drastique = "Drastique"


class EvaluationMetric(str, Enum):
    """Définition de la valeur retournée par l'évaluateur.

    **Cette fonctionalité est encore expérimentale, elle ne devrait pas
    être utilisée.**

    ```"Note"``` calcule une note, en fonction de l'évaluateur choisi.

    ```"Rank"``` calcule une note, en fonction de l'évaluateur choisi
    et retourne le rang des zones en fonctions de la valeur
    décroissante de cette note.

    ```"Zone"``` Renvoie l'id de chaque zone. Ce paramètre n'est
    destité qu'au débugage.

    """

    note = "Note"
    zone = "Zone"
    rank = "Rank"


class Evaluator(str, Enum):
    """Défini la méthode utilisée pour l'évaluation de la qualité.

    **Cette fonctionalité est encore expérimentale, elle ne devrait pas
    être utilisée.**

    ```"FIS"``` permet d'évaluer la qualité à l'aide d'un système d'inférence flou.

    ```"DST"``` permet d'évaluer la qualité à l'aide d'un évaluateur
    utilisant la théorie des fonctions de croyances (Beta).

    """

    fuzzy = "FIS"
    dst = "DST"


## Retour Fusion
