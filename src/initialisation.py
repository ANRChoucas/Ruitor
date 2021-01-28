"""Fonctions d'initialisation
"""


def set_proxy(url, port):
    """Fonction de définition du proxy

    Cette fonction permet de définir un proxy dans le cas où le code
    est utilisé dans un contexte qui le nécessite.

    Telle quelle cette fonction ne permet pas d'attribuer une url
    différente aux variables d'environnement "HTTP_PROXY" et
    "HTTPS_PROXY". Il faut modifier la fonction si nécessaire.

    Cette fonction n'a été testée que sous linux

    :param url: l'url du proxy
    :type url: srt

    :param port: le port du proxy
    :type url: int

    """

    # On crée une sring à partir des paramètres
    proxy = "%s:%s" % (url, port)

    # On défini les variables
    os.environ["http_proxy"] = proxy
    os.environ["HTTP_PROXY"] = proxy
    os.environ["https_proxy"] = proxy
    os.environ["HTTPS_PROXY"] = proxy

    # On logue la définition
    logger.info("The proxy : %s is used" % proxy)


def load_mnt(params, name=None, precision=None):
    if name:
        rasters = [i for i in params["MNT"] if i["name"] == name]
    elif precision:
        rasters = [i for i in params["MNT"] if i["precision"] == precision]
    else:
        raise ValueError("No Mnt corresponding")
    mntfile = get_file(rasters[0])

    logger.debug(
        "Used MNT : %s (precision %s)" % (rasters[0]["name"], rasters[0]["precision"])
    )

    return rasterio.open(mntfile)


def get_file(params):
    file_folder = params["path"]
    file_name = params["filename"]
    file = os.path.join(file_folder, file_name)

    return file


def load_ontology(params, onto_type):
    onto_dispacher = {"SRO": SROnto, "ROO": ROOnto}
    ontology = [i for i in params if i["type"] == onto_type]
    ontology_file = get_file(ontology[0])

    logger.debug("Used ontology : %s" % ontology[0]["type"])

    return onto_dispacher[onto_type](ontology_file)


def configuration(config):
    # Configuration logging
    logging.config.dictConfig(config.logging_configuration)

    # Définition proxy
    try:
        set_proxy(**config.proxy)
    except AttributeError:
        logger.debug("No proxy used")


def set_zir(raster, zir):
    """Fonction qui permet de transformer une zir donnée sous la forme
    d'une bbox en un objet window de rasterio

    :param raster: un raster rasterio
    :type raster: rasterio.Raster

    :param zir: bbox de la zone traitée
    :type zir: [[float, float], [float, float]]

    """
    
    # Spécification du padding
    padding = {"x": 10, "y": 10}
    
    # Calcul Zir
    # Calcul des numéros de ligne et de colonne correspondant aux
    # deux points de la bbox
    
    row_ind, col_ind = zip(*map(lambda x: raster.index(*x), zir))

    # Extraction du numéro de ligne/colonne minimum
    row_min, col_min = min(row_ind), min(col_ind)

    # Calcul du nombre de lignes/colonnes
    row_num = abs(max(row_ind) - row_min) + padding["x"]
    col_num = abs(max(col_ind) - col_min) + padding["y"]

    # Définition de la fenêtre de travail
    return Window(col_min, row_min, col_num, row_num)

