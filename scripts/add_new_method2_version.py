import os, sys

proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoref.settings")
sys.path.append(proj_path)

os.chdir(proj_path)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from georef.models import Toponim
from georef.sec_calculation import *

excluded_list = [
    'adiaz14249140202392592015', # Nusa Kambangan Island
    'xisabal193819556837562931529', # Ribagorza
    'mlozano5135736533235221564', # Grècia
]

def main():
    toponims = Toponim.objects.all()
    for t in toponims:
        if t.id not in excluded_list:
            darrera_versio = t.get_darrera_versio()
            if darrera_versio is not None:
                geom = darrera_versio.union_geometry()
                if geom is not None:
                    if geom.geom_type == 'Point':
                        pass
                        #print("Point, nothing to do")
                    else:
                        print("{0}".format(t))
                        print("{0}, create new version".format(geom.geom_type))
                        sec = compute_sec(geom, max_points_polygon=10000, tolerance=500, sample_size=50, n_nearest=10)
                        print("Versio original - x=>{0} y=>{1} radi=>{2}".format( darrera_versio.get_coordenada_x_centroide, darrera_versio.get_coordenada_y_centroide, darrera_versio.get_incertesa_centroide ))
                        nou_x = sec['center_wgs84'].x
                        nou_y = sec['center_wgs84'].y
                        radi = sec['radius']
                        print("Versio corregida - x=>{0} y=>{1} radi=>{2}".format(nou_x, nou_y, radi))


if __name__ == '__main__':
    main()
