# coding=utf-8
import os, sys

########################################################################
# CREATES THE PRE_PROCESSED TOPONIMS TABLE TO BE CONSUMED BY THE API   #
########################################################################

proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoref.settings")
sys.path.append(proj_path)

os.chdir(proj_path)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from georef.models import Toponimversio, Toponim
from django.db import connection
from georef.geom_utils import *

rows_insert = []
for toponim in Toponim.objects.all():
    id = toponim.id
    nomtoponim = toponim.nom
    nom = toponim.nom_str
    aquatic = toponim.aquatic_bool
    tipus = toponim.idtipustoponim

    tv = toponim.get_darrera_versio()

    datacaptura = None
    coordenadaxcentroide = None
    coordenadaycentroide = None
    incertesa = None

    #print(id)

    if tv is not None:
        datacaptura = tv.datacaptura
        centroid_specs = extract_centroid_specs(tv)
        coordenadaxcentroide = centroid_specs['x']
        coordenadaycentroide = centroid_specs['y']
        #incertesa = centroid_specs['h']
        incertesa = tv.georefcalc_uncertainty

    rows_insert.append([id, nomtoponim, nom, aquatic, tipus.nom, tipus.id, datacaptura, coordenadaxcentroide, coordenadaycentroide, incertesa])



cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS toponims_api cascade")

cursor.execute("""
    create table toponims_api(
        id character varying(200) NOT NULL PRIMARY KEY,
        nomtoponim character varying(255),
        nom character varying(500),
        aquatic boolean,
        tipus character varying(255),
        idtipus character varying(255),
        datacaptura date,
        coordenadaxcentroide double precision,
        coordenadaycentroide double precision,
        incertesa double precision
    )
""")

for row in rows_insert:
    cursor.execute("""
        INSERT INTO toponims_api
        (id,nomtoponim,nom,aquatic,tipus,idtipus,datacaptura,coordenadaxcentroide,coordenadaycentroide,incertesa)
        values
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],) )

cursor.execute("""
            CREATE INDEX idtipus_toponimapi_idx ON toponims_api (idtipus)
            """)

cursor.execute("""
            CREATE INDEX nomtoponim_toponimapi_idx ON toponims_api (nomtoponim)
        """)
