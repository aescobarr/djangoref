from django.contrib.gis.geos import GEOSGeometry, Point
from shapely.ops import nearest_points
from shapely.geometry import shape, mapping
import json

def closest_point_on_geometry(centroid, geometry):
    shp_centroid = shape(json.loads(centroid.json))
    shp_geometry = shape(json.loads(geometry.json))
    contacts = nearest_points( shp_centroid, shp_geometry )
    geos_geom = GEOSGeometry( json.dumps( mapping(contacts[1]) ) )
    return geos_geom


def centroid_is_in_geometry(centroid, geometry):
    shp_centroid = shape(json.loads(centroid.json))
    shp_geometry = shape(json.loads(geometry.json))
    return shp_geometry.contains(shp_centroid)

def search_level(level, retVal):
    if len(level) == 0:
        return
    elif len(level) == 1:
        search_level(level[0], retVal)
    elif len(level) == 2:
        #probably a coordinate
        retVal.append( Point(x=level[0], y=level[1]) )
    else:
        for next_level in level:
            search_level(next_level, retVal)


def extract_coords(coords):
    retVal = []
    if len(coords) == 2 and type(coords[0]).__name__ == 'float':
        retVal.append(Point(x=coords[0], y=coords[1]))
    else:
        for level in coords:
            search_level(level,retVal)
    return retVal


def extract_centroid_specs(toponimversio):
    coordenadaX = None
    coordenadaY = None
    incertesa = None

    coordenadaXCentroideAutomatic = None
    coordenadaYCentroideAutomatic = None
    incertesaAutomatic = None

    coordenadaXCentroideModificada = None
    coordenadaYCentroideModificada = None
    incertesaModificada = None

    if toponimversio.centroide_x is not None and toponimversio.centroide_y is not None:
        coordenadaXCentroideAutomatic = toponimversio.centroide_x
        coordenadaYCentroideAutomatic = toponimversio.centroide_y

    if toponimversio.get_incertesa_centroide is not None:
        incertesaAutomatic = toponimversio.get_incertesa_centroide

    if toponimversio.coordenada_x_centroide is not None:
        try:
            coordenadaXCentroideModificada = float(toponimversio.coordenada_x_centroide)
        except ValueError:
            pass

    if toponimversio.coordenada_y_centroide is not None:
        try:
            coordenadaYCentroideModificada = float(toponimversio.coordenada_y_centroide)
        except ValueError:
            pass

    if toponimversio.precisio_h is not None:
        try:
            incertesaModificada = float(toponimversio.precisio_h)
        except ValueError:
            pass

    if coordenadaXCentroideModificada is not None and coordenadaYCentroideModificada is not None:
        coordenadaX = coordenadaXCentroideModificada
        coordenadaY = coordenadaYCentroideModificada
        incertesa = incertesaModificada
    else:
        coordenadaX = coordenadaXCentroideAutomatic
        coordenadaY = coordenadaYCentroideAutomatic
        incertesa = incertesaAutomatic

    return { "x":coordenadaX, "y":coordenadaY, "h":incertesa }
