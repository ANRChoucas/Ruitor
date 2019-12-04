"""
Module Geometry parser
"""

from bs4 import BeautifulSoup
from shapely.geometry import Point, LineString, Polygon


class GeometryParser:
    """
    Classe destinée à parser les géometies. 

    Appelée par le parser.
    """

    def __init__(self, context):
        self.context = context

    def parse_geometry(self, geometry_gml):

        geometry_property = geometry_gml.geometryProperty

        if geometry_property.find("exterior", recursive=False):
            geometry = self.parse_polygon(geometry_property)
        elif geometry_property.find("LineString", recursive=False):
            geometry = self.parse_lineString(geometry_gml)
        elif geometry_property.find("Point", recursive=False):
            geometry = self.parse_point(geometry_gml)
        else:
            raise ValueError("Unkwon type")

        return geometry

    def parse_coordinates(self, coordinates_gml):
        """
        Transforme la balise <gml:coordinates/> en une liste de coordonées
        """
        coords = coordinates_gml.text.split()
        parsed_coords = []

        for coord in coords:
            coord_split = coord.split(",")
            coord_convert = [float(i) for i in coord_split]
            parsed_coords.append(coord_convert)

        return parsed_coords

    def parse_polygon(self, polygon_gml):

        # Calcul coordonées enveloppe
        ext_coordinates = self.parse_coordinates(polygon_gml.exterior.coordinates)

        # Calcul coordonées interieur
        if polygon_gml.innerBoundaryIs:
            int_coordinates = []
            for inter in polygon_gml.find_all("innerBoundaryIs"):
                int_coordinates.append(self.parse_coordinates(inter.coordinates))
        else:
            int_coordinates = None

        # Construction du polygone
        out_polygon = Polygon(shell=ext_coordinates, holes=int_coordinates)
        return out_polygon

    def parse_point(self, point_gml):
        coordinates = self.parse_coordinates(point_gml.coordinates)
        out_point = Point(*coordinates)

        return out_point

    def parse_lineString(self, lineString_gml):
        coordinates = self.parse_coordinates(lineString_gml.coordinates)
        out_Line = LineString(coordinates)

        return out_Line

