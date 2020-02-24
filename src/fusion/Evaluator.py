from itertools import groupby
import numpy as np

from skimage.measure import label, regionprops
from skimage.morphology import square, closing

from fuzzyUtils.FuzzyRaster import FuzzyRaster


class Evaluator:
    def __init__(self, context):
        self.context = context

    def evaluate(self, zones, rank=False):
        values = zones.values[0]
        # Regroupement pixels par région
        regions = self.regionalize(values)
        # Calcul des descripteurs par région
        regions_descriptors = self.descriptors(regions, values)
        # Calcul des notes par région
        # le calcul de la note est délégué aux objets héritant de
        # la classe evaluator
        regions_notes = self._evaluate(regions, regions_descriptors)
        # Si souhaité on renvoie le rang de chaque zone en fonction de
        # la note précédement calculée
        if rank:
            # Calcul de la note
            ranked_regions = self.compute_range(regions_descriptors, regions_notes)
            # extraction des listes [rang] et [regions] pour construire
            # le raster des notes
            regions_notes, regions_descriptors = zip(*ranked_regions)
        # Génération du raster des notes contenant les notes ou le rang des régions
        # en fonction de la valeur du paramètre "rank"
        evalued_regions = self.region_value(regions_descriptors, regions_notes, zones)
        return evalued_regions

    def compute_range(self, descriptors, values):
        # Définition de la lambda utilisée comme clé pour l'ordonancement
        # des regions et leur regroupement. Comme les descripteurs et les valeurs
        # sont zippées la clé utilisée est la seconde valeur du tuple, i.e. la note
        key_fun = lambda t: t[1]
        # Ordonancement des regions en fct. le la note. Nécessaire pour le groupby
        ordored_values = sorted(zip(descriptors, values), reverse=True, key=key_fun)
        # Comme je ne veux pas donner un ordre arbitraire entre des zones avec la même
        # note (cas fréquent) je regroupe les valeurs en fonction de leur note pour
        # donner aux régions dont la note est identique le même rang
        grouped_values = groupby(ordored_values, key=key_fun)
        # Définition compteur rang
        rank = 1
        # Première boucle pour le groupe
        for _, regions in grouped_values:
            # seconde boucle pour les regions regroupées
            for region in regions:
                # On renvoie un générateur de tuples (rang, region)
                # À cause du zip plus haut obligation de
                # retrourner le premier élément du tuple 'region'
                yield (rank, region[0])
            rank += 1

    def regionalize(self, values):
        # Préparation image
        raster_closed = self.region_cleaner(values)
        # Définition des zones
        raster_label = label(raster_closed, connectivity=2)
        # On retire des zones labelisées les pixels dont le degré d'appartenance
        # est nul, pour ne pas biaiser les valeurs des descripteurs.
        raster_label[np.logical_and(raster_label != 0, values == 0)] = 0
        return raster_label

    def region_cleaner(self, raster, close=True, **kwargs):
        # Pour que l'algorithme d'ouverture/fermeture et de
        # regionalisation fasse bien son job transformation du raster
        # en image binaire (i.e. si différent de 0 alors 1)
        binary_raster = raster.copy()
        binary_raster[binary_raster > 0] = 1
        # -- On fait une ouverture/fermeture ?
        if close:
            # -- Oui monsieur, s'écria t-il d'un ton que l'interpréteur
            # ne put qualifier que de nonchalante.
            # Filtre utilisé pour l'érosion/dilatation
            closing_pattern = kwargs.get("closing_pattern", square(3))
            # Raster Closing
            return closing(binary_raster, closing_pattern)

        return binary_raster

    def descriptors(self, regions, values):
        return regionprops(regions, intensity_image=values, coordinates="rc")

    def region_value(self, descriptors, values, raster):

        output_array = np.zeros_like(raster.values[0])
        meta = raster.raster_meta

        for region, note in zip(descriptors, values):
            output_array[region["slice"]][region["image"]] = note

        output_array = output_array.astype(meta["dtype"])[np.newaxis]

        return FuzzyRaster(array=output_array, meta=meta)

    def _evaluate(self, region, descriptors):
        raise NotImplementedError
