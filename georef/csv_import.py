from georef.models import Toponim, Tipustoponim, Pais, Qualificadorversio, Recursgeoref, Toponimversio
from django.contrib.auth.models import User
from datetime import datetime
from dateutil import parser
from django.db.models import Q
import operator, functools
import re

class NumberOfColumnsException(Exception):
    pass


class EmptyFileException(Exception):
    pass


FIELD_MAP = {
    'name': { 'index': 0, 'mandatory': True },
    'type': { 'index': 1, 'mandatory': True },
    'aquatic': { 'index': 2, 'mandatory': True },
    'parent_node': { 'index': 3, 'mandatory': True },
    'version_number': { 'index': 4, 'mandatory': True },
    'version_qualifier': { 'index': 5, 'mandatory': True },
    'version_captured_from_resource': { 'index': 6, 'mandatory': True },
    'site_name_on_resource': { 'index': 7, 'mandatory': False },
    'date': { 'index': 8, 'mandatory': False },
    'original_x': { 'index': 9, 'mandatory': True },
    'original_y': { 'index': 10, 'mandatory': True },
    'depth_max_height': { 'index': 11, 'mandatory': False },
    'depth_min_height': { 'index': 12, 'mandatory': False },
    'coordinate_uncertainty': { 'index': 13, 'mandatory': True },
    'georeferencer': { 'index': 14, 'mandatory': True },
    'observations': { 'index': 15, 'mandatory': False }
}

def check_file_structure(file_array):
    if len(file_array) < 2:
        raise EmptyFileException()
    numlinia = 1
    for rows in file_array:
        if len(rows) != len(FIELD_MAP):
            raise NumberOfColumnsException({"numrow": str(numlinia), "numcols": str(len(rows))})
        numlinia = numlinia + 1


def toponim_exists(line):
    try:
        return Toponim.objects.get(linia_fitxer_importacio=line)
    except Toponim.DoesNotExist:
        return None


def get_georeferencer_by_name_simple(name):
    name_parts = name.split(' ')
    name_fusioned = ('').join( [u.strip().lower() for u in name_parts] )
    for u in User.objects.all():
        username_parts = u.first_name.strip().lower().split(' ') + u.last_name.strip().lower().split(' ')
        username_fusioned = ('').join( username_parts )
        if name_fusioned == username_fusioned:
            return u
    return None


def get_georeferencer_by_name(name):
    name_parts = name.split(' ')
    filter_clause = []
    if len(name_parts) > 0:
        first_name = name_parts[0]
        filter_clause.append( Q(**{ 'first_name__iexact': first_name }) )
        if len(name_parts) > 1:
            last_name = name_parts[1]
            filter_clause.append( Q(**{'last_name__iexact': last_name }) )
            try:
                return User.objects.get(functools.reduce(operator.and_, filter_clause))
            except User.DoesNotExist:
                pass
    return None


def get_model_by_attribute(attribute_name, attribute_value, model_name):
    try:
        filter_clause = Q(**{ attribute_name + '__iexact' : attribute_value } )
        return model_name.objects.get(filter_clause)
    except model_name.DoesNotExist:
        return None


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

def get_toponim_nom_estructurat(nom_toponim):
    if nom_toponim != '':
        if 'terrestre' in nom_toponim.lower() or 'aquàtic' in nom_toponim.lower():
            filter_clause = []
            sep_character_apparitions = [i for i in find_all(nom_toponim,'-')]
            if len(sep_character_apparitions) > 1:
                last_index_sep = sep_character_apparitions[-1]
                nom_info_addicional = []
                nom_info_addicional.append(nom_toponim[:last_index_sep].strip())
                nom_info_addicional.append(nom_toponim[(last_index_sep + 1):].strip())
            else:
                nom_info_addicional = nom_toponim.split('-')
            nom = nom_info_addicional[0].strip()
            info_addicional = nom_info_addicional[1].strip().split('(')
            pais = info_addicional[0].strip().lower()
            tipusToponim = info_addicional[1].replace(")", "").strip().lower()
            aquatic = info_addicional[2].replace(")", "").strip().lower() != 'terrestre'
            aquatic_string = ''
            if aquatic == True:
                aquatic_string = 'S'
            else:
                aquatic_string = 'N'
            p = get_model_by_attribute('nom', pais, Pais)
            tt = get_model_by_attribute('nom', tipusToponim, Tipustoponim)
            if p is not None:
                filter_clause.append( Q(**{ 'idpais' : p } ) )
            if tt is not None:
                filter_clause.append(Q(**{ 'idtipustoponim' : tt } ) )
            filter_clause.append(Q(**{ 'aquatic' : aquatic_string } ) )
            filter_clause.append(Q(**{'nom': nom}))
            return Toponim.objects.filter(functools.reduce(operator.and_, filter_clause))
        else:
            return Toponim.objects.filter(nom__icontains=nom_toponim)
    return None


def register_error(num_line, message, problems):
    lineNums = []
    try:
        lineNums = problems[message]
        lineNums.append(num_line)
        problems[message] = lineNums
    except KeyError:
        lineNums.append(num_line)
        problems[message] = lineNums


def process_line(line, line_string, errors, toponims_exist, toponims_to_create, line_counter, problemes, nomFitxer):
    t = toponim_exists(line_string)
    if t is None:
        # [0] - Nom toponim --> Cap comprovacio(comprovar blancs)
        nom = ''
        # [1] - Tipus toponim --> Buscar toponim per nom TipusToponim
        tt = None
        # [2] - Aquatic --> Cap comprovacio
        aquatic = 'N'
        # [3] - Node superior --> Buscar toponim per nom(multiples resultats?)
        pare = None
        # [4] - Numero de versio
        numeroVersio = -1
        # [5] - Qualificador de la versió
        qv = None
        # [6] - Versio capturada del recurs RecursGeoreferenciacio
        rg = None
        # [7] - Nom del toponim al recurs
        nomToponimRecurs = None
        # [8] - Data
        data = None
        # [9] - Coord x original
        coordX_original = None
        # [10] - Coord y original
        coordY_original = None
        # [11] - depth_max_height
        depth_max_height = None
        # [12] - depth_min_height
        depth_min_height = None
        # [13] - Incertesa de coordenada
        precisioH = None
        # [13] - Incertesa h
        #precisioZ = None
        # [14] - Georeferenciador
        georeferenciador = None
        # [15] - Observacions
        observacions = None

        errorsALinia = False
        errorsLinia = []
        errorsLiniaActual = []

        if line[FIELD_MAP['name']['index']] == '' or line[FIELD_MAP['name']['index']].strip() == '':
            errorsALinia = True
            errorsLiniaActual.append("Nom de toponim en blanc a la columna 1")
            register_error(line_counter, "Nom de toponim en blanc a la columna 1", problemes)
        else:
            nom = line[FIELD_MAP['name']['index']].strip()

        if line[FIELD_MAP['type']['index']] == '' or line[FIELD_MAP['type']['index']].strip() == '':
            errorsALinia = True
            errorsLiniaActual.append("Tipus de toponim en blanc a la columna 2")
            register_error(line_counter, "Tipus de toponim en blanc a la columna 2", problemes)
        else:
            tt = get_model_by_attribute('nom', line[FIELD_MAP['type']['index']].strip(), Tipustoponim)
            if tt is None:
                errorsALinia = True
                errorsLiniaActual.append("No s'ha trobat el tipus de toponim '" + line[FIELD_MAP['type']['index']] + "' a la columna 2")
                register_error(line_counter, "No s'ha trobat el tipus de toponim '" + line[FIELD_MAP['type']['index']] + "' a la columna 2", problemes)

        if line[FIELD_MAP['aquatic']['index']] == '' or line[FIELD_MAP['aquatic']['index']].strip() == '':
            errorsALinia = True
            errorsLiniaActual.append("Aquatic en blanc a la columna 3")
            register_error(line_counter, "Aquatic en blanc a la columna 3", problemes)
        else:
            if line[FIELD_MAP['aquatic']['index']].strip().lower() in ['true', 'cert', 'sí', 'si', '1', 'cierto', 'verdadero']:
                aquatic = 'S'

        if line[FIELD_MAP['parent_node']['index']] == '' or line[FIELD_MAP['parent_node']['index']].strip() == "":
            pare = None
        else:
            ts = get_toponim_nom_estructurat(line[FIELD_MAP['parent_node']['index']])
            if len(ts) == 0:
                errorsALinia = True
                errorsLiniaActual.append("No trobo cap topònim node superior amb nom '" + line[FIELD_MAP['parent_node']['index']] + "' a la columna 4")
                register_error(line_counter, "No trobo cap topònim node superior amb nom '" + line[FIELD_MAP['parent_node']['index']] + "' a la columna 4", problemes)
            elif len(ts) == 1:
                pare = ts[0]
            else:
                errorsALinia = True
                errorsLiniaActual.append("Hi ha múltiples topònims  node superior amb nom '" + line[FIELD_MAP['parent_node']['index']] + "' a la columna 4")
                register_error(line_counter, "Hi ha múltiples topònims  node superior amb nom '" + line[FIELD_MAP['parent_node']['index']] + "' a la columna 4", problemes)

        if line[FIELD_MAP['version_number']['index']] == '' or line[FIELD_MAP['version_number']['index']].strip().lower() == '':
            errorsALinia = True
            errorsLiniaActual.append("Número de versió en blanc a la columna 5")
            register_error(line_counter, "Número de versió en blanc a la columna 5", problemes)
        else:
            try:
                numeroVersio = int(line[FIELD_MAP['version_number']['index']])
            except ValueError:
                errorsALinia = True
                errorsLiniaActual.append("No sé convertir en nombre '" + line[FIELD_MAP['version_number']['index']] + "' a la columna 5")
                register_error(line_counter, "No sé convertir en nombre '" + line[FIELD_MAP['version_number']['index']] + "' a la columna 5", problemes)

        if line[FIELD_MAP['version_qualifier']['index']] is None or line[FIELD_MAP['version_qualifier']['index']].strip().lower() == '':
            qv = None # No és obligatori
        else:
            qv = get_model_by_attribute('qualificador', line[FIELD_MAP['version_qualifier']['index']].strip(), Qualificadorversio)
            if qv is None:
                errorsALinia = True
                errorsLiniaActual.append("No trobo el qualificador de versió '" + line[FIELD_MAP['version_qualifier']['index']] + "' a la columna 6")
                register_error(line_counter, "No trobo el qualificador de versió '" + line[FIELD_MAP['version_qualifier']['index']] + "' a la columna 6", problemes)

        if line[FIELD_MAP['version_captured_from_resource']['index']] is None or line[FIELD_MAP['version_captured_from_resource']['index']].strip().lower() == '':
            errorsALinia = True
            errorsLiniaActual.append("El recurs de georeferenciacio en que es basa el recurs està en blanc a la columna 7")
            register_error(line_counter, "El recurs de georeferenciacio en que es basa el recurs està en blanc a la columna 7", problemes)
        else:
            rg = get_model_by_attribute('nom', line[FIELD_MAP['version_captured_from_resource']['index']].strip(), Recursgeoref)
            if rg is None:
                errorsALinia = True
                errorsLiniaActual.append("No trobo el recurs de georeferenciació '" + line[FIELD_MAP['version_captured_from_resource']['index']] + "' a la columna 7")
                register_error(line_counter, "No trobo el recurs de georeferenciació '" + line[FIELD_MAP['version_captured_from_resource']['index']] + "' a la columna 7", problemes)

        if line[FIELD_MAP['site_name_on_resource']['index']] is None or line[FIELD_MAP['site_name_on_resource']['index']].strip().lower() == '':
            errorsALinia = True
            errorsLiniaActual.append("El nom del topònim al recurs de georeferenciacio està en blanc a la columna 8")
            register_error(line_counter, "El nom del topònim al recurs de georeferenciacio està en blanc a la columna 8", problemes)
        else:
            nomToponimRecurs = line[FIELD_MAP['site_name_on_resource']['index']]

        if line[FIELD_MAP['date']['index']] is None or line[FIELD_MAP['date']['index']].strip().lower() == '':
            data = None
        else:
            try:
                #data = datetime.strptime(line[8].strip(), '%d/%m/%Y')
                data = parser.parse(line[8].strip())
            except ValueError:
                errorsALinia = True
                errorsLiniaActual.append("Error convertint " + line[FIELD_MAP['date']['index']] + " a format data a  la columna 9")
                register_error(line_counter, "Error convertint " + line[FIELD_MAP['date']['index']] + " a format data a  la columna 9", problemes)

        #x coord
        if line[FIELD_MAP['original_x']['index']] is None or line[FIELD_MAP['original_x']['index']].strip().lower() == '':
            errorsALinia = True
            errorsLiniaActual.append("La coordenada x original està en blanc a la columna 11")
            register_error(line_counter, "La coordenada x original està en blanc a la columna 11", problemes)
        else:
            coordX_original = None
            try:
                float(line[FIELD_MAP['original_x']['index']].strip().replace(",", "."))
                coordX_original = line[FIELD_MAP['original_x']['index']].strip().replace(",", ".")
            except ValueError:
                errorsALinia = True
                errorsLiniaActual.append("Error de conversió a la coordenada x original " + line[FIELD_MAP['original_x']['index']] +  ", columna 11")
                register_error(line_counter, "Error de conversió a la coordenada x original " + line[FIELD_MAP['original_x']['index']] +  ", columna 11", problemes)

        # coord y
        if line[FIELD_MAP['original_y']['index']] is None or line[FIELD_MAP['original_y']['index']].strip().lower() == '':
            errorsALinia = True
            errorsLiniaActual.append("La coordenada y original està en blanc a la columna 12")
            register_error(line_counter, "La coordenada y original està en blanc a la columna 12", problemes)
        else:
            try:
                float(line[FIELD_MAP['original_y']['index']].strip().replace(",", "."))
                coordY_original = line[FIELD_MAP['original_y']['index']].replace(",", ".")
            except ValueError:
                errorsALinia = True
                errorsLiniaActual.append("Error de conversió a la coordenada y original " + line[FIELD_MAP['original_y']['index']] +  ", columna 11")
                register_error(line_counter, "Error de conversió a la coordenada y original " + line[FIELD_MAP['original_y']['index']] +  ", columna 11", problemes)

        # depth_max_height
        if line[FIELD_MAP['depth_max_height']['index']] is None or line[FIELD_MAP['depth_max_height']['index']].strip().lower() == '':
            depth_max_height = None
        else:
            try:
                float(line[FIELD_MAP['depth_max_height']['index']].strip().replace(",", "."))
                depth_max_height = line[FIELD_MAP['depth_max_height']['index']].replace(",", ".")
            except ValueError:
                errorsALinia = True
                errorsLiniaActual.append("Error de conversió a l'altitud de profunditat màxima (m) " + line[FIELD_MAP['depth_max_height']['index']] +  ", columna 12")
                register_error(line_counter, "Error de conversió a l'altitud de profunditat màxima (m)" + line[FIELD_MAP['depth_max_height']['index']] +  ", columna 12", problemes)

        # depth_min_height
        if line[FIELD_MAP['depth_max_height']['index']] is None or line[FIELD_MAP['depth_max_height']['index']].strip().lower() == '':
            depth_max_height = None
        else:
            try:
                float(line[FIELD_MAP['depth_max_height']['index']].strip().replace(",", "."))
                depth_max_height = line[FIELD_MAP['depth_max_height']['index']].replace(",", ".")
            except ValueError:
                errorsALinia = True
                errorsLiniaActual.append("Error de conversió a l'altitud de profunditat màxima (m) " + line[FIELD_MAP['depth_max_height']['index']] +  ", columna 12")
                register_error(line_counter, "Error de conversió a l'altitud de profunditat màxima (m)" + line[FIELD_MAP['depth_max_height']['index']] +  ", columna 12", problemes)

        # coord z
        # if line[11] is None or line[11].strip().lower() == '':
        #     errorsALinia = True
        #     errorsLiniaActual.append("La coordenada z original està en blanc a la columna 13")
        #     register_error(line_counter, "La coordenada z original està en blanc a la columna 13", problemes)
        # else:
        #     try:
        #         float(line[11].replace(",", "."))
        #         coordZ_original = line[11].replace(",", ".")
        #     except ValueError:
        #         errorsALinia = True
        #         errorsLiniaActual.append("Error de conversió a la coordenada z original " + line[11] +  ", columna 13")
        #         register_error(line_counter, "Error de conversió a la coordenada z original " + line[11] +  ", columna 13", problemes)


        # incertesa coordenades h
        if line[FIELD_MAP['coordinate_uncertainty']['index']] is not None and not line[FIELD_MAP['coordinate_uncertainty']['index']].strip().lower() == '':
            try:
                precisioH = float(line[FIELD_MAP['coordinate_uncertainty']['index']].strip().replace(",", "."))
            except ValueError:
                errorsALinia = True
                errorsLiniaActual.append("Error de conversió a incertesa de coordenades " + line[FIELD_MAP['coordinate_uncertainty']['index']] +  ", columna 14")
                register_error(line_counter, "Error de conversió a incertesa de coordenades " + line[FIELD_MAP['coordinate_uncertainty']['index']] +  ", columna 14", problemes)

        # incertesa coordenades z
        # if line[13] is None or line[13].strip().lower() == '':
        #     precisioZ = None
        # else:
        #     try:
        #         float(line[13].strip().replace(",", "."))
        #         precisioZ = line[13]
        #     except ValueError:
        #         errorsALinia = True
        #         errorsLiniaActual.append("Error de conversió a incertesa d'altitud " + line[13] +  ", columna 15")
        #         register_error(line_counter, "Error de conversió a incertesa d'altitud " + line[13] +  ", columna 15", problemes)

        # georeferenciador versio
        if line[FIELD_MAP['georeferencer']['index']] is None or line[FIELD_MAP['georeferencer']['index']].strip().lower() == '':
            errorsALinia = True
            errorsLiniaActual.append("Georeferenciador en blanc a la columna 15")
            register_error(line_counter, "Georeferenciador en blanc a la columna 15", problemes)
        else:
            georeferenciador = get_georeferencer_by_name_simple(line[FIELD_MAP['georeferencer']['index']].strip())
            if georeferenciador is None:
                errorsALinia = True
                errorsLiniaActual.append("No trobo el georeferenciador " + line[FIELD_MAP['georeferencer']['index']] +  ", columna 15")
                register_error(line_counter, "No trobo el georeferenciador " + line[FIELD_MAP['georeferencer']['index']] +  ", columna 15", problemes)

        if len(line) > 15:
            observacions = line[FIELD_MAP['observations']['index']]
        else:
            observacions = ''

        if errorsALinia:
            errorsLinia.insert(0, line_counter)
            errorsLinia.append(errorsLiniaActual)
            errors.append(errorsLinia)
        else:
            t = Toponim()
            t.nom = nom
            t.idtipustoponim = tt
            t.aquatic = aquatic
            t.idpare = pare

            t.nom_fitxer_importacio = nomFitxer
            t.linia_fitxer_importacio = line_string

            tv = Toponimversio()

            tv.numero_versio = numeroVersio
            tv.nom = nomToponimRecurs;
            tv.datacaptura = data
            tv.coordenada_x_origen = coordX_original
            tv.coordenada_y_origen = coordY_original
            tv.altitud_profunditat_maxima = depth_max_height
            tv.altitud_profunditat_minima = depth_min_height
            tv.observacions = observacions

            tv.iduser = georeferenciador
            if precisioH is not None:
                tv.precisio_h = precisioH
            tv.idqualificador = qv
            tv.idrecursgeoref = rg
            tv.idtoponim = t

            #t.versions.add(tv)

            toponims_to_create.append({ 'toponim': t, 'versio': tv })
    else:
        toponims_exist.append(t)
