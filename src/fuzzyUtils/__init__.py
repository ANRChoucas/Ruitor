"""Documentation du package fuzzyUtils

FuzzyUtils est le âckage qui ajoute certaines fonctionalités à la
bibliothèque rasterio, pour lui permettre de travailler avec des
rasters flous.

"""

# Le fichier __init__.py est chargé par défaut à l'import de la
# biliothèque. C'est ce fichier qui permet de transformer un dossier
# de sources en une bibliothèque.

# Cette ligne permet d'importer silencieusement la classe FuzzyRaster
# définie dans le fichier FuzzyRaster à l'import de cette
# bibliotèque. Évitant ainsi des imports de la forme
# Fuzzyutils.FuzzyRaster. Sauf problèmes spécifiques il n'y a rien à
# toucher ici.
#
# Voir la documentation officielle pour plus d'informations
# https://docs.python.org/fr/3.9/tutorial/modules.html#packages

from .FuzzyRaster import FuzzyRaster
