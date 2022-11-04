import os, sys

proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoref.settings")
sys.path.append(proj_path)

os.chdir(proj_path)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from georef_addenda.models import GeometriaToponimVersio
from georef.geom_utils import extract_coords, closest_point_on_geometry, centroid_is_in_geometry
from haversine import haversine
import json


def centroid_calc(geometry, calc_method):
    if calc_method == 0:
        corrected_centroid = geometry.centroid
    elif calc_method == 1:
        original_centroid = geometry.centroid
        corrected_centroid = closest_point_on_geometry( original_centroid, geometry )
        print(centroid_is_in_geometry( corrected_centroid, geometry ))
    else:
        raise Exception("Calculation method not implemented")
    if corrected_centroid is not None:
        centroid_haversine = (corrected_centroid.y, corrected_centroid.x)
        dist_max = 0
        vertexes = extract_coords(geometry.coords)
        for vertex in vertexes:
            vertex_haversine = (vertex.y, vertex.x)
            dist = haversine(centroid_haversine, vertex_haversine, unit='m')
            if dist > dist_max:
                dist_max = dist
        # return dist_max
        geom_struct = {
            "type": "Feature",
            "properties": {},
            "geometry": json.loads(corrected_centroid.json)
        }
        return {'status': 'OK', 'detail': {'centroid': geom_struct, 'radius': dist_max}, 'calc_method': calc_method}


def main():
    geoms = GeometriaToponimVersio.objects.all()
    for geom in geoms:
        if geom.geometria.geom_type != 'Point':
            centroid_in_geometry = centroid_is_in_geometry(geom.geometria.centroid, geom.geometria)
            # if centroid_in_geometry:
            #     calc_method = 0
            # else:
            #     calc_method = 1
            calc_method = 1
            if not centroid_in_geometry and geom.geometria.geom_type == 'Polygon':
                result = centroid_calc(geom.geometria, calc_method)
                print( "{0} {1} {2} {3} {4} {5}".format( geom.geometria.geom_type, geom.id, result['detail']['centroid']['geometry']['coordinates'][0], result['detail']['centroid']['geometry']['coordinates'][1], result['detail']['radius'], calc_method ) )


if __name__ == '__main__':
    main()
