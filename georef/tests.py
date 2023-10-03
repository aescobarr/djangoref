from django.test import TestCase
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry
import sys

from georef.sec_calculation import geometry_from_json, wgs_to_azimuthal_eq, get_vertex_n, \
    simplify_geometry, get_minimum_bounding_circle, point_is_in_geometry, sample_geometry, closest_vertex_on_geometry, \
    n_closest_points, closest_point_on_geometry, compute_sec, centroid_is_in_geom, multipoint_from_coordinate_list, \
    get_best_sec, get_further_point_in_geometry, flatten

test_params = {
    'simplify_threshold':  1000,
    'tolerance': 500,
    'sample_size': 8,
    'n_nearest': 3,
    'output_print': False
}

small_c_polygon = "./georef/test_files/c_polygon.shp"
big_c_polygon = "./georef/test_files/c_polygon_1000.shp"
spain_polygon = "./georef/test_files/spain.shp"
line = "./georef/test_files/c_line.shp"
multi_line = "./georef/test_files/multi_line.shp"

all_geoms = [small_c_polygon, big_c_polygon, spain_polygon, line, multi_line]

geojson_single_poly = '[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[1.153564,41.996107],[1.494141,41.877605],[1.461182,41.623518],[1.148071,41.570115],[0.906372,41.758883],[0.906372,41.93484],[1.153564,41.996107]]]}}]'
geojson_multi_poly = '[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[1.153564,41.996107],[1.494141,41.877605],[1.461182,41.623518],[1.148071,41.570115],[0.906372,41.758883],[0.906372,41.93484],[1.153564,41.996107]]]}},{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[1.763306,41.855174],[1.636963,41.932865],[1.683655,42.024746],[1.820984,42.008421],[1.829224,41.910385],[1.763306,41.855174]]]}}]'
geojson_potato_geometry =  '[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[1.153564,41.996107],[1.494141,41.877605],[1.461182,41.623518],[1.148071,41.570115],[0.906372,41.758883],[0.906372,41.93484],[1.153564,41.996107]]]}}]'


def get_geometry_from_file(filename):
    shape_reader = DataSource(filename)
    union_geometry = None
    for feat in shape_reader[0]:
        g = GEOSGeometry(feat.geom.wkt, srid=4326)
        if union_geometry is None:
            union_geometry = g
        else:
            union_geometry = union_geometry.union(g)
    return union_geometry



class SECTests(TestCase):
    def test_geojson_to_geom_single_poly(self):
        single_poly_geom = geometry_from_json(geojson_single_poly)
        self.assertTrue(single_poly_geom.geom_type == 'Polygon', "Geometry should be polygon, is {0}".format(single_poly_geom.geom_type))
        self.assertTrue(single_poly_geom.valid, "Geometry should be valid, is not because {0}".format(single_poly_geom.valid_reason))
        self.assertTrue(single_poly_geom.simple, "Geometry should be simple, is not")

    def test_geojson_to_geom_multi_poly(self):
        multi_poly_geom = geometry_from_json(geojson_multi_poly)
        self.assertTrue(multi_poly_geom.geom_type == 'MultiPolygon', "Geometry should be MultiPolygon, is {0}".format(multi_poly_geom.geom_type))
        self.assertTrue(multi_poly_geom.valid, "Geometry should be valid, is not because {0}".format(multi_poly_geom.valid_reason))
        self.assertTrue(multi_poly_geom.simple, "Geometry should be simple, is not")

    def test_vertex_number(self):
        single_poly_geom_wgs84 = geometry_from_json(geojson_single_poly)
        n = get_vertex_n(single_poly_geom_wgs84)
        self.assertTrue(n == 7, "Polygon geometry should have 7 vertexes, has {0}".format(n))

    def test_reproject(self):
        single_poly_geom_wgs84 = geometry_from_json(geojson_single_poly)
        single_poly_geom_aeqd = wgs_to_azimuthal_eq(single_poly_geom_wgs84)

    def test_simplify(self):
        union_geometry = get_geometry_from_file(spain_polygon)
        original_n_vertices = get_vertex_n(union_geometry)
        geometry_should_be_simplified = original_n_vertices > test_params['simplify_threshold']
        self.assertTrue( geometry_should_be_simplified, "Geometry should be simplified" )
        simplified_geometry = simplify_geometry( union_geometry, tolerance=test_params['tolerance'] )
        simplified_vertices = get_vertex_n( simplified_geometry )
        self.assertTrue( simplified_vertices < original_n_vertices, "Simplified geometry n of vertices is equal or bigger than original vertices n ({0}>={1}".format( simplified_vertices, original_n_vertices ) )

    def test_compute_sec(self):
        single_poly_geom_wgs84 = geometry_from_json(geojson_single_poly)
        single_poly_geom_aeqd = wgs_to_azimuthal_eq(single_poly_geom_wgs84)
        sec = get_minimum_bounding_circle( single_poly_geom_aeqd )
        if test_params['output_print']:
            print( "SEC center x={0}, y={1}, radius={2}".format( sec['center'].x, sec['center'].y, sec['radius'] ))

    def test_center_in_geometry(self):
        c_geometry = get_geometry_from_file(small_c_polygon)
        sec = get_minimum_bounding_circle(c_geometry)
        its_in_c = point_is_in_geometry( sec['center'], c_geometry )
        self.assertFalse( its_in_c, "Centroid should not be in geometry of c polygon, it is" )

        potato_geometry_wgs84 = geometry_from_json(geojson_potato_geometry)
        potato_geometry_aeqd = wgs_to_azimuthal_eq(potato_geometry_wgs84)

        sec_potato = get_minimum_bounding_circle(potato_geometry_aeqd)
        its_in_potato = point_is_in_geometry(sec_potato['center'], potato_geometry_aeqd)
        self.assertTrue( its_in_potato, "Centroid should be in geometry of potato polygon, it's not")

    def test_sample(self):
        for file in all_geoms:
            geom = get_geometry_from_file(file)
            geom_aeqd = wgs_to_azimuthal_eq(geom)
            original_n_coords = get_vertex_n(geom_aeqd)
            coords_sampled = sample_geometry(geom_aeqd, original_n_coords - 1)
            self.assertTrue(len(coords_sampled) < original_n_coords,"Number of sampled coordinates {0} should be less than total coordinates {1}".format(original_n_coords - 1, len(coords_sampled)))
            self.assertTrue(len(coords_sampled) == original_n_coords - 1, "Number of sampled coordinates should be {0}, is {1}".format(original_n_coords - 1, len(coords_sampled)))

    def test_closest_point(self):
        for file in all_geoms:
            geom = get_geometry_from_file(file)
            c_geom_aeqd = wgs_to_azimuthal_eq(geom)
            centroid = c_geom_aeqd.centroid
            closestpoint_by_postgis = closest_point_on_geometry(centroid, c_geom_aeqd)
            coords = []
            flattened_coords = flatten(c_geom_aeqd.coords)
            for point in flattened_coords:
                coords.append(GEOSGeometry("POINT( {} {} )".format(point[0], point[1])))
            distance = sys.float_info.max
            nearest_point = None
            for point in coords:
                current_dist = point.distance(centroid)
                if current_dist < distance:
                    distance = current_dist
                    nearest_point = point
            self.assertFalse(nearest_point.equals_exact(GEOSGeometry(closestpoint_by_postgis), tolerance=0.00000001), "Closest point should not be a vertex, it appears to be")

    def test_closest_vertex(self):
        for file in all_geoms:
            c_geometry = get_geometry_from_file(file)
            c_geom_aeqd = wgs_to_azimuthal_eq(c_geometry)
            centroid = c_geom_aeqd.centroid
            closestpoint_by_postgis = closest_vertex_on_geometry(centroid, c_geom_aeqd)
            coords = []
            flattened_coords = flatten(c_geom_aeqd.coords)
            for point in flattened_coords:
                coords.append(GEOSGeometry("POINT( {} {} )".format(point[0],point[1])))
            distance = sys.float_info.max
            nearest_point = None
            for point in coords:
                current_dist = point.distance(centroid)
                if current_dist < distance:
                    distance = current_dist
                    nearest_point = point
            self.assertTrue( nearest_point.equals_exact( GEOSGeometry(closestpoint_by_postgis), tolerance=0.00000001 ), "Brute force and postgis results are not the same" )

    def test_n_closest_points(self):
        for file in all_geoms:
            c_geometry = get_geometry_from_file(file)
            c_geom_aeqd = wgs_to_azimuthal_eq(c_geometry)
            centroid = c_geom_aeqd.centroid
            closestpoint_by_postgis = closest_vertex_on_geometry(centroid, c_geom_aeqd)
            closest_point_in_geometry = GEOSGeometry(closestpoint_by_postgis)
            closest_points = n_closest_points( closest_point_in_geometry, c_geom_aeqd, test_params['sample_size'])
            coords = []
            flattened_coords = flatten(c_geom_aeqd.coords)
            for point in flattened_coords:
                coords.append(GEOSGeometry("POINT( {} {} )".format(point[0], point[1])))
            sorted_distance_list = []
            for point in coords:
                current_dist = point.distance(closest_point_in_geometry)
                sorted_distance_list.append( ( point.wkt, current_dist ) )
            sorted_distance_list = sorted( sorted_distance_list, key=lambda x: x[1])
            for i in range(len(closest_points)):
                geom_closest_points_i = GEOSGeometry(closest_points[i][0])
                geom_sorted_distance_list_i = GEOSGeometry(sorted_distance_list[i][0])
                if test_params['output_print']:
                    print("Brute force - {0} || Closest points function - {1}".format( sorted_distance_list[i], closest_points[i] ))
                self.assertTrue(geom_closest_points_i.equals_exact(geom_sorted_distance_list_i, tolerance=0.00000001), "Brute force and postgis results are not the same for point {0} (brute force), {1} (closest points function)".format( geom_sorted_distance_list_i.wkt, geom_closest_points_i.wkt ))

    def test_compute_sec_executes_ok(self):
        c_geometry = get_geometry_from_file(small_c_polygon)
        sec = compute_sec(c_geometry, test_params['simplify_threshold'], test_params['tolerance'], test_params['sample_size'], test_params['n_nearest'])
        if test_params['output_print']:
            print(sec)

    def test_compute_sec_algo(self):
        for file in all_geoms:
            geom = get_geometry_from_file(file)
            aeqd_geometry = wgs_to_azimuthal_eq(geom)
            #should not be simplified
            n = get_vertex_n(aeqd_geometry)
            if n > test_params['simplify_threshold']:
                aeqd_geometry = simplify_geometry( aeqd_geometry, test_params['tolerance'] )
                n_new = get_vertex_n(aeqd_geometry)
                self.assertTrue(n_new < n, "Simplified polygon ({0} vertexes) should have less vertexes, has {1}".format(n_new, n))
            # self.assertTrue( n < test_params['simplify_threshold'], "C polygon should be under {0}, vertexes, has {1}".format( test_params['simplify_threshold'], n) )

            sec = get_minimum_bounding_circle(aeqd_geometry)
            centroid = sec['center']
            centroid_is_in_geometry = centroid.intersects(aeqd_geometry)
            if not centroid_is_in_geometry:
                self.assertFalse( centroid.intersects(aeqd_geometry), "It's a c_polygon, centroid should not intersect original geometry" )
                closest_to_centroid = closest_point_on_geometry(centroid, aeqd_geometry)
                #It should be on the polygon hull
                closest_to_centroid_g = GEOSGeometry(closest_to_centroid)
                self.assertTrue( centroid_is_in_geom(closest_to_centroid_g, aeqd_geometry), "closest_to_centroid should be on the original geometry hull or inside")
                #Sample nearby points for optimum SEC
                candidates = sample_geometry(aeqd_geometry, test_params['sample_size'])
                self.assertTrue(len(candidates) <= test_params['sample_size'], "Number of candidate points {0} should be equal to sample size {1}".format( len(candidates), test_params['sample_size']))
                candidates.append(closest_to_centroid_g)
                closest_candidates = n_closest_points(closest_to_centroid_g, multipoint_from_coordinate_list(candidates), test_params['n_nearest'])
                self.assertTrue(len(closest_candidates) == test_params['n_nearest'], "Number of close to centroid candidate points {0} should be equal to n_nearest param {1}".format(len(closest_candidates),test_params['n_nearest']))
                best_sec = get_best_sec(closest_candidates, aeqd_geometry)
                best_sec_centroid = best_sec['center']
                best_sec_radius = best_sec['radius']
                for c in closest_candidates:
                    worst_sec_point = GEOSGeometry(c[0])
                    worst_d = get_further_point_in_geometry(worst_sec_point, aeqd_geometry)
                    if not worst_sec_point.equals_exact(best_sec_centroid, tolerance=0.00000001):
                        self.assertTrue( best_sec_radius < worst_d['radius'], "Uncertainty radius of non optimal solution {0} should be grater than optimal solution {1}".format(worst_d, best_sec_radius))
