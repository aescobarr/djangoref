import os, sys

proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoref.settings")
sys.path.append(proj_path)

os.chdir(proj_path)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from georef.models import Toponimversio, Toponim
from georef_addenda.models import GeometriaToponimVersio
from georef.sec_calculation import *
from georef.views import extract_coords, haversine
from django.core.exceptions import ObjectDoesNotExist

def calc_method_0_centroid(geometry):
    params = {}
    centroid = geometry.centroid
    centroid_haversine = (centroid.y, centroid.x)
    dist_max = 0
    vertexes = extract_coords(geometry.coords)
    for vertex in vertexes:
        vertex_haversine = (vertex.y, vertex.x)
        dist = haversine(centroid_haversine, vertex_haversine, unit='m')
        if dist > dist_max:
            dist_max = dist
    params['coordenada_x_centroide'] = centroid.x
    params['coordenada_y_centroide'] = centroid.y
    params['precisio_h'] = dist_max
    return params

def fix_problema_punt_poligon(issues):
    punt = issues['point']
    polygon = issues['polygon'].geometria
    tv = punt.idversio
    toponim = tv.idtoponim
    print("Fixing point/polygon mix issue with toponim id {0} - {1}".format( toponim.id, toponim ))
    centroid_calc_method = tv.centroid_calc_method
    if centroid_calc_method == 0:
        params = calc_method_0_centroid(polygon)
        tv.coordenada_x_centroide = params['coordenada_x_centroide']
        tv.coordenada_y_centroide = params['coordenada_y_centroide']
        tv.precisio_h = params['precisio_h']
        punt.delete()
        print("...fixed")
    else:
        print("... not fixed, unkown centroid method {0}".format(centroid_calc_method))

def genera_geometria_valida(geometria):
    with connection.cursor() as cursor:
        sql = """
            select
                ST_AsText(ST_MakeValid(ST_GeomFromText(%s)))
        """
        cursor.execute(sql, [geometria.wkt])
        results = cursor.fetchone()
        return GEOSGeometry(results[0])

def problema_geometria_no_valida(toponim):
    issues = {}
    versions = Toponimversio.objects.filter(idtoponim=toponim)
    for t in versions:
        for g in t.geometries.all():
            if not g.geometria.valid:
                issues['invalid'] = g.geometria
                issues['valid'] = genera_geometria_valida(g.geometria)
                issues['geometriatoponim'] = g
                return issues
    return None

def fix_geometria_no_valida(issues):
    # Polygon -> Polygon overwrite original with valid
    # Polygon -> MultiPolygon overwrite original with valid
    # Polygon -> Linestring ???
    # Polygon -> Geometrycollection if collection is Linestring/Polygon, delete linestring save Polygon as valid

    geometria_invalida = issues['invalid']
    geometria_valida = issues['valid']
    geometriatoponim = issues['geometriatoponim']
    if geometria_invalida.geom_type == geometria_valida.geom_type and geometria_valida.geom_type == 'Polygon':
        print("Fixing...")
        geometriatoponim.geometria = geometria_valida
        geometriatoponim.save()
    elif geometria_invalida.geom_type == 'Polygon' and geometria_valida.geom_type == 'MultiPolygon':
        print("Fixing...")
        geometriatoponim.geometria = geometria_valida
        geometriatoponim.save()
    elif geometria_invalida.geom_type == 'Polygon' and geometria_valida.geom_type == 'GeometryCollection':
        for feature in geometria_valida:
            if feature.geom_type == 'Polygon':
                print("Fixing...")
                geometriatoponim.geometria = feature
                geometriatoponim.save()


def problema_punt_poligon(toponim):
    versions = Toponimversio.objects.filter(idtoponim=toponim)
    for t in versions:
        n_geoms_versio = t.geometries.all().count()
        if n_geoms_versio > 1:
            s = set()
            multiple_geoms = {}
            for g in t.geometries.all():
                s.add(g.geometria.geom_type)
                multiple_geoms[g.geometria.geom_type] = g
            if len(s) > 1 and 'Point' in s and 'Polygon' in s:
                return {'point': multiple_geoms['Point'], 'polygon': multiple_geoms['Polygon']}
    return None


def fix_aiguafreda():
    try:
        g = GeometriaToponimVersio.objects.get(pk=3019)
        g.delete()
    except ObjectDoesNotExist:
        print("Nothing to do")


def fix_vallibierna():
    try:
        g = GeometriaToponimVersio.objects.get(pk=4224)
        g.delete()
        g = GeometriaToponimVersio.objects.get(pk=4225)
        new_geom = GEOSGeometry('POINT (0.58951 42.62226499999999)')
        g.geometria = new_geom
        g.save()
        tv = g.idversio
        tv.coordenada_x_centroide = new_geom.x
        tv.coordenada_y_centroide = new_geom.y
        tv.precisio_h = 1044.23632925535
        tv.save()
    except ObjectDoesNotExist:
        print("Nothing to do")


def fix_grecia():
    try:
        g_3769 = GeometriaToponimVersio.objects.get(pk=3769)
        g_3770 = GeometriaToponimVersio.objects.get(pk=3770)
        g_3771 = GeometriaToponimVersio.objects.get(pk=3771)
        g_3769.delete()
        g_3771.delete()
        file = proj_path + "/scripts/files/grecia.wkt"
        f = open(file, "r")
        g = GEOSGeometry(f.read(), srid=4326)
        g_3770.geometria = g
        g_3770.save()
    except ObjectDoesNotExist:
        print("Nothing to do")


def fix_ribagorza():
    try:
        file = proj_path + "/scripts/files/ribagorza.wkt"
        f = open(file, "r")
        g = GEOSGeometry(f.read(), srid=4326)
        GeometriaToponimVersio.objects.get(pk=5059).delete()
        modif = GeometriaToponimVersio.objects.get(pk=5058)
        modif.geometria = g
        modif.save()
    except ObjectDoesNotExist:
        print("Nothing to do")


def fix_nusa_kambangan():
    try:
        GeometriaToponimVersio.objects.get(pk='1158').delete()
    except ObjectDoesNotExist:
        print("Nothing to do")


def fix_almadra():
    try:
        GeometriaToponimVersio.objects.get(pk=9414).delete()
    except ObjectDoesNotExist:
        print("Nothing to do")

def fix_cami_degotalls():
    try:
        GeometriaToponimVersio.objects.get(pk=8781).delete()
    except ObjectDoesNotExist:
        print("Nothing to do")

def fix_barranco_irene():
    try:
        GeometriaToponimVersio.objects.get(pk=4470).delete()
    except ObjectDoesNotExist:
        print("Nothing to do")

def fix_riu_llobregat():
    try:
        GeometriaToponimVersio.objects.get(pk=1465).delete()
    except ObjectDoesNotExist:
        print("Nothing to do")
    try:
        GeometriaToponimVersio.objects.get(pk=1466).delete()
    except ObjectDoesNotExist:
        print("Nothing to do")

def fix_cami_pep():
    try:
        GeometriaToponimVersio.objects.get(pk=8646).delete()
    except ObjectDoesNotExist:
        print("Nothing to do")


def fix_particular_cases():
    fix_aiguafreda()
    fix_vallibierna()
    fix_grecia()
    fix_nusa_kambangan()
    fix_ribagorza()
    fix_almadra()
    fix_cami_degotalls()
    fix_barranco_irene()
    fix_riu_llobregat()
    fix_cami_pep()


def do_fix_non_valid_geom():
    for top in Toponim.objects.all():
        issues = problema_geometria_no_valida(top)
        if issues is not None:
            geometria_valida = issues['valid']
            tipus_original = issues['invalid'].geom_type
            tipus_valid = geometria_valida.geom_type
            print("Toponim {0} te problema amb geometria {1}, geometria valida és {2}".format( top, tipus_original, tipus_valid ))
            fix_geometria_no_valida(issues)


def do_fix_polygon_point_issue():
    for top in Toponim.objects.all():
        issue = problema_punt_poligon(top)
        if issue is not None:
            fix_problema_punt_poligon(issue)


def do_fix_multipoint_to_point():
    for top in Toponim.objects.all():
        versions = Toponimversio.objects.filter(idtoponim=top)
        for t in versions:
            geom = t.union_geometry()
            if geom is not None:
                if geom.geom_type == 'MultiPoint':
                    c_x = t.get_coordenada_x_centroide
                    c_y = t.get_coordenada_y_centroide
                    radius = t.get_incertesa_centroide
                    print("{0}".format(t))
                    centroid = None
                    for point in geom:
                        candidate = GEOSGeometry('POINT({0} {1})'.format(c_x,c_y))
                        if point.equals_exact(candidate, tolerance=0.0001):
                            centroid = candidate
                    if candidate is not None:
                        gt = GeometriaToponimVersio.objects.filter(idversio=t)
                        if gt.count() == 1:
                            gt[0].geometria = centroid
                            gt[0].save()
                        else:
                            saved = False
                            for gtn in gt:
                                if not saved:
                                    gtn.geometria = centroid
                                    gtn.save()
                                    saved = True
                                else:
                                    gtn.delete()

def main():
    fix_particular_cases()
    for x in range(2):
        do_fix_polygon_point_issue()
    for x in range(2):
        do_fix_non_valid_geom()
    do_fix_multipoint_to_point()


if __name__ == '__main__':
    main()

