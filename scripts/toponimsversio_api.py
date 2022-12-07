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
for toponimversio in Toponimversio.objects.all():

    centroide = extract_centroid_specs(toponimversio)
    nom = None
    tipus = None
    qualificadorVersio = None
    recursCaptura = None
    sistRefRecurs = None
    georeferenciatPer = None
    idtoponim = None

    id = toponimversio.id
    if toponimversio.idtoponim:
        nom = toponimversio.idtoponim.nom_str

    nomtoponim = toponimversio.nom
    if toponimversio.idtoponim and toponimversio.idtoponim.idtipustoponim:
        tipus = toponimversio.idtoponim.idtipustoponim.nom

    versio = toponimversio.numero_versio
    if toponimversio.idqualificador:
        qualificadorVersio = toponimversio.idqualificador.qualificador

    if toponimversio.idrecursgeoref:
        recursCaptura = toponimversio.idrecursgeoref.nom

    if toponimversio.idsistemareferenciarecurs:
        sistRefRecurs = toponimversio.idsistemareferenciarecurs.sistemareferencia

    dataCaptura = toponimversio.datacaptura
    coordXOriginal = toponimversio.coordenada_x_origen
    coordYOriginal = toponimversio.coordenada_y_origen
    coordZ = toponimversio.coordenada_z
    incertesaZ = toponimversio.precisio_z
    if toponimversio.iduser:
        georeferenciatPer = toponimversio.iduser.last_name + ", " + toponimversio.iduser.first_name

    observacions = toponimversio.observacions
    coordXCentroide = centroide['x']
    coordYCentroide = centroide['y']
    #incertesaCoord = centroide['h']
    incertesaCoord = toponimversio.georefcalc_uncertainty
    if toponimversio.idtoponim:
        idtoponim = toponimversio.idtoponim.id


    rows_insert.append([
        id, #'furibe-MZOOLOGIA-15626593901221-293'
        nom, #'Anglesola - Espanya (municipi) (Terrestre)'
        nomtoponim, #'Anglesola'
        tipus, #'municipi'
        versio, # 1
        qualificadorVersio, # ''
        recursCaptura, # 'Catalunya Municipis PuntRadi'
        sistRefRecurs, # '<html>[Sistema referencia: Longitud-Latitud i UTM 31]<br>[Datum: WGS 84 | World Geodetic System 84, Pico de las Nieves,ED 50]<br>[Unitats: diverses]<br>[Altitud: ]</html>'
        dataCaptura, # datetime.date(2010, 12, 1)
        coordXOriginal, # '338603.674613'
        coordYOriginal, # '4614662.875'
        coordZ, # None
        incertesaZ, # None
        georeferenciatPer, # 'Castells Rafel'
        observacions, # ''
        coordXCentroide, # 1.060217
        coordYCentroide, # 41.665531
        incertesaCoord, # 4701.06
        idtoponim #'furibe-MZOOLOGIA-15626584502547-288'
    ])

cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS toponimsversio_api cascade")

cursor.execute("""
    create table toponimsversio_api(
        id character varying(200) NOT NULL PRIMARY KEY,
        nom character varying(500),
        nomtoponim character varying(255),
        tipus character varying(100),
        versio integer,
        qualificadorVersio character varying(500),
        recursCaptura character varying(500),
        sistRefRecurs character varying(1000),
        dataCaptura date,
        coordXOriginal character varying(100),
        coordYOriginal character varying(100),
        coordZ double precision,
        incertesaZ double precision,
        georeferenciatPer character varying(500),
        observacions text,
        coordXCentroide double precision,
        coordYCentroide double precision,
        incertesaCoord double precision,
        idtoponim character varying(200)
    )
""")

for row in rows_insert:
    print(row)
    cursor.execute("""
        INSERT INTO toponimsversio_api
        (id, nom, nomtoponim, tipus, versio, qualificadorVersio, recursCaptura, sistRefRecurs, dataCaptura, coordXOriginal, coordYOriginal, coordZ, incertesaZ, georeferenciatPer, observacions, coordXCentroide, coordYCentroide, incertesaCoord, idtoponim)
        values
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],) )


cursor.execute("""
    CREATE INDEX idtoponim_toponimvapi_idx ON toponimsversio_api (idtoponim)
""")
