"""
Fichier contenant l'ensemble des 
"""

from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, AnyUrl
from fastapi import File, UploadFile


# Types génériques
class Mnt(str, Enum):
    tt = "5"
    ttt = "50"
    tttt = "100"
    

# Types spatialisation
class Modifieur(BaseModel):
    """
    Classe trop cool
    """

    # Les modifieurs sont définis dans l'ontologie ORL. Pour
    # identifier le modifieur utrilisé il faut fournir son url
    uri: AnyUrl = Field(description="Uri du modifieur dans l'ontologie ORL")

    
class RelationLocalisation(BaseModel):
    """
    Documentation
    """

    # La relation spatiale est définie par une uri, qui permet
    # d'identifier le concept dans l'ontologie ORL. C'est dans cette
    # ontologie qu'est définie la méthode de spatialisation de la
    # relation de localisation
    uri: AnyUrl = Field(description="Uri de la relation de localisation dans l'ontologie ORL")
    # La spatialisation peut être modifié par l'ajout d'un, ou
    # plusieurs modifieurs. L'emploi des modifieurs est totalement
    # facultatif.
    modifieurs: Optional[list[Modifieur]] = Field(description="Liste des modifieurs à appliquer à la relation de localisation")

    
class Site(BaseModel):
    """
    Documentation
    """
    
    pass


class Indice(BaseModel):
    """
    Documentation
    """
    
    cible: Optional[str]
    relationLocalisation: RelationLocalisation
    site: Site
    # La confiance est une valeur que le secouriste peut définir pour
    # donner une indication sur sa croyance en la véracité de l'indice
    # de localisation.
    #
    # Cette valeur est optionelle. Si aucune valeur n'est fournie
    # l'indice est spatialisé avec une certitude maximale, 1.
    #
    # La valeur de la confiance doit être comprise dans l'intervalle
    # [0,1]
    confiance: Optional[float] = Field(description="Confiance",ge=0,le=1)

# Retour spatialisation


class Fuzzy:
    pass


# Types Fusion

## Corps Fusion
class Operateur(str, Enum):
    zadeh = "Zadeh"
    lukacewicz = "Lukacewiz"
    probabiliste = "Probabiliste"
    nilpotent = "Nilpotent"
    drastique = "Drastique"

    
class EvaluationMetric(str, Enum):
    note = "Note"
    zone = "Zone"
    rank = "Rank"

    
class Evaluator(str, Enum):
    fuzzy = "FIS"
    dst = "DST"

    
class Evaluation(BaseModel):
    Evaluator: Optional[Evaluator]
    Evaluation_Metric: EvaluationMetric
    


## Retour Fusion
