import json
from django.contrib.gis.geos import GEOSGeometry, Point, MultiPoint
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.db import connection
import random
import sys

# params = {
#     'simplify_threshold':  10000,
#     'tolerance': 500,
#     'sample_size': 50
# }

def get_vertex_n(geometry):
    return geometry.num_coords


def wgs_to_azimuthal_eq(geometry):
    to_transform = geometry.clone()
    srs_aeqd = SpatialReference("+proj=aeqd +lat_0={0} +lon_0={1} +x_0=0 +y_0=0 +R=6371000 +units=m +no_defs +type=crs".format(geometry.centroid.x, geometry.centroid.y))
    srs_4326 = SpatialReference("WGS84")
    ct = CoordTransform(srs_4326, srs_aeqd)
    to_transform.transform(ct)
    return to_transform


def geometry_from_json(geojson):
    features = json.loads(geojson)
    union_geometry = None
    for feature in features:
        if union_geometry is None:
            union_geometry = GEOSGeometry(json.dumps(feature['geometry']))
        else:
            union_geometry = union_geometry.union(GEOSGeometry(json.dumps(feature['geometry'])))
    return union_geometry


def simplify_geometry(geometry, tolerance):
    simplified = geometry.simplify(tolerance=tolerance,preserve_topology=True)
    return simplified


def get_minimum_bounding_circle(geometry):
    with connection.cursor() as cursor:
        sql = """
            select st_astext(center), radius from ST_MinimumBoundingRadius(%s)
        """
        cursor.execute(sql,[ geometry.wkt ])
        results = cursor.fetchone()
        center = GEOSGeometry(results[0])
        radius = results[1]
        return { 'center': center, 'radius': radius }


def point_is_in_geometry(point, geometry):
    return point.intersects(geometry)


def flatten(test_tuple):
    if isinstance(test_tuple, tuple) and len(test_tuple) == 2 and not isinstance(test_tuple[0], tuple):
        res = [test_tuple]
        return tuple(res)
    res = []
    for sub in test_tuple:
        res += flatten(sub)
    return tuple(res)


def sample_geometry(geometry, sample_size):
    coords = []
    flattened_coords = flatten(geometry.coords)
    for coord in flattened_coords:
        coords.append(coord)
    if geometry.num_coords <= sample_size:
        return coords
    else:
        return random.sample(coords, sample_size)


def closest_point_on_geometry(point, geometry):
    with connection.cursor() as cursor:
        sql = """
            select ST_Astext(ST_ClosestPoint(ST_GeomFromText(%s), ST_GeomFromText(%s))) as closest
        """
        cursor.execute(sql, [geometry.wkt, point.wkt])
        results = cursor.fetchone()
        closest_point = results[0]
        return closest_point


def closest_vertex_on_geometry(point, geometry):
    with connection.cursor() as cursor:
        sql = """
            with d as (
                SELECT ST_Astext(ST_Union((d).geom)) FROM ST_DumpPoints(%s) as d
            )
            select st_astext as multipoint from d;
        """
        cursor.execute(sql, [geometry.wkt])
        results = cursor.fetchone()
        multipoint_wkt = results[0]
        sql = """
            select ST_Astext(ST_ClosestPoint(ST_GeomFromText(%s), ST_GeomFromText(%s))) as closest
        """
        cursor.execute(sql, [multipoint_wkt, point.wkt])
        results = cursor.fetchone()
        closest_point = results[0]
        return closest_point


def n_closest_points(point, geometry, n):
    with connection.cursor() as cursor:
        sql = """
            with d as (
                SELECT ST_Astext(ST_Union((d).geom)) FROM ST_DumpPoints(%s) as d
            )
            select st_astext as multipoint from d;
        """
        cursor.execute(sql, [geometry.wkt])
        results = cursor.fetchone()
        multipoint_wkt = results[0]
        sql = """
            select
                ST_AsText((ST_Dump(ST_GeomFromText(%s))).geom),
                (ST_Dump(ST_GeomFromText(%s))).geom <-> ST_GeomFromText(%s) as dist
            order by dist
            limit %s
        """
        cursor.execute(sql, [multipoint_wkt, multipoint_wkt, point.wkt, n])
        results = cursor.fetchall()
        return results


def get_further_point_in_geometry(point, geometry):
    with connection.cursor() as cursor:
        sql = """
            with d as (
                SELECT ST_Astext(ST_Union((d).geom)) FROM ST_DumpPoints(%s) as d
            )
            select st_astext as multipoint from d;
        """
        cursor.execute(sql, [geometry.wkt])
        results = cursor.fetchone()
        multipoint_wkt = results[0]
        sql = """
            select
                ST_AsText((ST_Dump(ST_GeomFromText(%s))).geom),
                (ST_Dump(ST_GeomFromText(%s))).geom <-> ST_GeomFromText(%s) as dist
            order by dist desc
        """
        cursor.execute(sql, [multipoint_wkt, multipoint_wkt, point.wkt])
        results = cursor.fetchone()
        return {'center': point, 'radius': results[1]}


def multipoint_from_coordinate_list(coordinate_list):
    points = [ Point(a[0],a[1]) for a in coordinate_list]
    return MultiPoint(points)


def centroid_is_in_geom(centroid, geom):
    return centroid.intersects(geom) or centroid.distance(geom) < 1


def get_best_sec(candidates, geometry):
    best_sec = None
    best_distance = sys.float_info.max
    for c in candidates:
        current_point = GEOSGeometry(c[0])
        current_sec = get_further_point_in_geometry(current_point, geometry)
        if current_sec['radius'] < best_distance:
            best_distance = current_sec['radius']
            best_sec = current_sec
    return best_sec

def compute_sec(geometry, max_points_polygon, tolerance, sample_size, n_nearest):
    # Get Centroid to determine lat_0 and long_0 parameters for projecting to the
    # Azimuthal Equidistant Projection centered on the geometry
    # Project site to parameterized AEQD
    aeqd_geometry = wgs_to_azimuthal_eq(geometry)

    # Check if polygon is too large, if it has more than 10000 points. If so we
    # simplify with a tolerance of 500 meters
    if get_vertex_n(geometry) > max_points_polygon:
        aeqd_geometry = simplify_geometry( aeqd_geometry, tolerance=tolerance )

    # Calculate MBC and centroid on projected site
    sec = get_minimum_bounding_circle(aeqd_geometry)
    # Get uncertainty, i.e. from centroid to any point in circle
    centroid = sec['center']
    # uncertainty = sec['radius']

    # If centroid is not on top of geometry (on top of line or inside polygon), we approximate best SEC
    if not centroid_is_in_geom(centroid, aeqd_geometry):
        closest_to_centroid = closest_point_on_geometry(centroid, aeqd_geometry)
        candidates = sample_geometry(aeqd_geometry, sample_size)
        candidates.append( GEOSGeometry(closest_to_centroid) )
        closest_candidates = n_closest_points( GEOSGeometry(closest_to_centroid) , multipoint_from_coordinate_list(candidates), n_nearest )
        best_sec = get_best_sec(closest_candidates, aeqd_geometry)
        return best_sec
    else:
        return sec
