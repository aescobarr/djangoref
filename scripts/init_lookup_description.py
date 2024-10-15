# coding=utf-8
import os, sys

########################################################################
# INITIALIZES THE LOOKUP TABLE DESCRIPTIONS                            #
########################################################################

proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoref.settings")
sys.path.append(proj_path)

os.chdir(proj_path)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from georef.models import Toponimversio, Toponim
from georef_addenda.models import Autor, LookupDescription
from django.db import connection
from georef.geom_utils import *
from django.utils.translation import gettext_lazy as _
from django.utils import translation


lookups = (
    ('Autor', 'georef_addenda.Autor',"Autors, personals o institucionals, dels recursos cartogràfics; la sintaxi és simple i ratifica la forma en què es presenti el nom de l'autor en el propi recurs cartogràfic."),
    ('Organització', 'georef_addenda.Organization',"Institucions a les quals pertanyen les persones que editen continguts de Georef. Els topònims queden assignats a l'organització de pertinença de qui hagi afegit l'última versió."),
    ('País', 'georef.Pais',"Vocabulari inicialment importat per descriure topònims, però que admet modificacions amb les tres funcions d’editar."),
    ('Paraula clau', 'georef.Paraulaclau',"Vocabulari en desenvolupament per descriure recursos cartogràfics; sintaxi simple perquè es tracta de conceptes molt clars."),
    ('Qualificador versió', 'georef.Qualificadorversio',"Vocabulari en desenvolupament per descriure versions de topònims; sintaxi simple perquè es tracta de conceptes molt clars."),
    ('Tipus de contingut', 'georef.Tipusrecursgeoref',"Vocabulari per classificar recursos cartogràfics."),
    ('Tipus de suport', 'georef.Suport',"Vocabulari per descriure com es presenten els recursos cartogràfics."),
    ('Tipus de topònim', 'georef.Tipustoponim',"Vocabulari que assenyala el nivell administratiu o territorial d’un topònim."),
    ("Tipus d'unitats", 'georef.Tipusunitats',"Vocabulari amb les categories d’unitats en què els recursos cartogràfics proporcionen les coordenades dels topònims.")
)

def get_translation_in(language, s):
    with translation.override(language):
        return translation.gettext(s)

def main():
    LookupDescription.objects.all().delete()
    for lang in ['ca', 'en']:
        for l in lookups:
            look = LookupDescription()
            look.locale = lang
            look.model_fully_qualified_name = l[1]
            look.model_label = get_translation_in(lang, l[0])
            if lang == 'ca':
                look.description = l[2]
            look.save()


if __name__ == "__main__":
    main()
