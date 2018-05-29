from django.middleware.csrf import get_token
from ajaxuploader.views import AjaxFileUploader
from django.shortcuts import render
from rest_framework import status, viewsets
from georef.serializers import ToponimSerializer, FiltrejsonSerializer, RecursgeorefSerializer, ToponimVersioSerializer, \
    UserSerializer, ProfileSerializer, ParaulaClauSerializer, AutorSerializer, CapawmsSerializer, ToponimSearchSerializer, \
    QualificadorversioSerializer, PaisSerializer, TipusrecursgeorefSerializer, SuportSerializer, TipusToponimSerializer, \
    TipusunitatsSerializer
from georef.models import Toponim, Filtrejson, Recursgeoref, Paraulaclau, Autorrecursgeoref, Tipusunitats
from georef_addenda.models import Profile, Autor, GeometriaRecurs, GeometriaToponimVersio
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from querystring_parser import parser
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
import operator
import functools
from georef.models import Tipustoponim, Pais, Qualificadorversio, Toponimversio, Tipusrecursgeoref, ParaulaclauRecurs, \
    Suport, Capawms, Capesrecurs, PrefsVisibilitatCapes
import json
from json import dumps
import magic
import zipfile
from djangoref.settings import *
import glob, os
import ntpath
import shapefile
import djangoref.settings as conf
from django.core import serializers
from django.shortcuts import render, get_object_or_404
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from georef.forms import ToponimsUpdateForm, ToponimversioForm, ProfileForm, UserForm, ChangePasswordForm, NewUserForm, \
    RecursForm
from django.forms import formset_factory
from django.db import IntegrityError, transaction
from georef.tasks import compute_denormalized_toponim_tree_val, format_denormalized_toponimtree, \
    compute_denormalized_toponim_tree_val_to_root
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.staticfiles.templatetags.staticfiles import static
from owslib.wms import WebMapService
from django.contrib.gis.geos import Polygon, GEOSGeometry
from osgeo import gdal, osr, ogr
from django.conf import settings

from weasyprint import HTML, CSS
import csv
import xlwt
from tempfile import mkstemp
import os
import uuid

from geoserver.catalog import Catalog, ConflictingDataError
from requests.exceptions import ConnectionError
import geoserver.util
from shutil import rmtree
from georef.jsonprefs import JsonPrefsUtil
import pyproj
from georef.csv_import import check_file_structure, NumberOfColumnsException, EmptyFileException, process_line
from django.db import connection


def get_order_clause(params_dict, translation_dict=None):
    order_clause = []
    try:
        order = params_dict['order']
        if len(order) > 0:
            for key in order:
                sort_dict = order[key]
                column_index_str = sort_dict['column']
                if translation_dict:
                    column_name = translation_dict[params_dict['columns'][int(column_index_str)]['data']]
                else:
                    column_name = params_dict['columns'][int(column_index_str)]['data']
                direction = sort_dict['dir']
                if direction != 'asc':
                    order_clause.append('-' + column_name)
                else:
                    order_clause.append(column_name)
    except KeyError:
        pass
    return order_clause


def get_filter_clause(params_dict, fields, translation_dict=None):
    filter_clause = []
    try:
        q = params_dict['search']['value']
        if q != '':
            for field in fields:
                if translation_dict:
                    translated_field_name = translation_dict[field]
                    filter_clause.append(Q(**{translated_field_name + '__icontains': q}))
                else:
                    filter_clause.append(Q(**{field + '__icontains': q}))
    except KeyError:
        pass
    return filter_clause


"""
Request is a rest_framework request
"""


def generic_datatable_list_endpoint(request, search_field_list, queryClass, classSerializer,
                                    field_translation_dict=None, order_translation_dict=None, paginate=True):
    '''
    request.query_params works only for rest_framework requests, but not for WSGI requests. request.GET[key] works for
    both types of requests
    '''

    '''    
    draw = request.query_params.get('draw', -1)
    start = request.query_params.get('start', 0)
    '''
    draw = -1
    start = 0
    try:
        draw = request.GET['draw']
    except:
        pass
    try:
        start = request.GET['start']
    except:
        pass

    length = 25

    get_dict = parser.parse(request.GET.urlencode())

    order_clause = get_order_clause(get_dict, order_translation_dict)

    filter_clause = get_filter_clause(get_dict, search_field_list, field_translation_dict)

    q = None
    try:
        string_json = get_dict['filtrejson']
        json_filter_data = json.loads(string_json)
        q = queryClass.crea_query_de_filtre(json_filter_data['filtre'])
    except KeyError:
        pass

    queryset = queryClass.objects.all()

    if q:
        queryset = queryset.filter(q)

    if len(filter_clause) == 0:
        queryset = queryset.order_by(*order_clause)
    else:
        queryset = queryset.order_by(*order_clause).filter(functools.reduce(operator.or_, filter_clause))

    if paginate:
        paginator = Paginator(queryset, length)

        recordsTotal = queryset.count()
        recordsFiltered = recordsTotal
        page = int(start) / int(length) + 1

        serializer = classSerializer(paginator.page(page), many=True, context={'request': request})
    else:
        serializer = classSerializer(queryset, many=True, context={'request': request})
        recordsTotal = queryset.count()
        recordsFiltered = recordsTotal

    return Response(
        {'draw': draw, 'recordsTotal': recordsTotal, 'recordsFiltered': recordsFiltered, 'data': serializer.data})


def index(request):
    return render(request, 'georef/index.html')


class PaisViewSet(viewsets.ModelViewSet):
    serializer_class = PaisSerializer

    def get_queryset(self):
        queryset = Pais.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(nom__icontains=name)
        return queryset


class TipusUnitatsViewSet(viewsets.ModelViewSet):
    serializer_class = TipusunitatsSerializer

    def get_queryset(self):
        queryset = Tipusunitats.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(tipusunitat__icontains=name)
        return queryset

class TipusToponimViewSet(viewsets.ModelViewSet):
    serializer_class = TipusToponimSerializer

    def get_queryset(self):
        queryset = Tipustoponim.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(nom__icontains=name)
        return queryset


class TipusSuportViewSet(viewsets.ModelViewSet):
    serializer_class = SuportSerializer

    def get_queryset(self):
        queryset = Suport.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(nom__icontains=name)
        return queryset


class TipusrecursgeorefViewSet(viewsets.ModelViewSet):
    serializer_class = TipusrecursgeorefSerializer

    def get_queryset(self):
        queryset = Tipusrecursgeoref.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(nom__icontains=name)
        return queryset


class QualificadorViewSet(viewsets.ModelViewSet):
    serializer_class = QualificadorversioSerializer

    def get_queryset(self):
        queryset = Qualificadorversio.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(nom__icontains=name)
        return queryset


class AutorViewSet(viewsets.ModelViewSet):
    serializer_class = AutorSerializer

    def get_queryset(self):
        queryset = Autor.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(nom__icontains=name)
        return queryset


class ParaulaClauViewSet(viewsets.ModelViewSet):
    serializer_class = ParaulaClauSerializer

    def get_queryset(self):
        queryset = Paraulaclau.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(paraula__icontains=name)
        return queryset


class ToponimVersioViewSet(viewsets.ModelViewSet):
    queryset = Toponimversio.objects.all()
    serializer_class = ToponimVersioSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ToponimSearchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ToponimSearchSerializer

    def get_queryset(self):
        queryset = Toponim.objects.all()
        term = self.request.query_params.get('term', None)
        if term is not None:
            queryset = queryset.filter(nom__icontains=term).order_by('nom')
        return queryset

class ToponimViewSet(viewsets.ModelViewSet):
    serializer_class = ToponimSerializer

    def get_queryset(self):
        queryset = Toponim.objects.all()
        term = self.request.query_params.get('term', None)
        if term is not None:
            queryset = queryset.filter(nom__icontains=term).order_by('nom')
        return queryset


class FiltrejsonViewSet(viewsets.ModelViewSet):
    serializer_class = FiltrejsonSerializer

    def get_queryset(self):
        queryset = Filtrejson.objects.all()
        term = self.request.query_params.get('term', None)
        modul = self.request.query_params.get('modul', None)
        if term is not None:
            queryset = queryset.filter(nomfiltre__icontains=term)
        if modul is not None:
            queryset = queryset.filter(modul=modul)
        return queryset

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RecursGeoRefViewSet(viewsets.ModelViewSet):
    queryset = Recursgeoref.objects.all()
    serializer_class = RecursgeorefSerializer


@api_view(['GET'])
def check_filtre(request):
    if request.method == 'GET':
        nomfiltre = request.query_params.get('nomfiltre', None)
        modul = request.query_params.get('modul', None)
        if nomfiltre is None:
            content = {'status': 'KO', 'detail': 'mandatory param missing'}
            return Response(data=content, status=400)
        if modul is None:
            content = {'status': 'KO', 'detail': 'mandatory param missing'}
            return Response(data=content, status=400)
        else:
            try:
                f = Filtrejson.objects.get(nomfiltre=nomfiltre, modul=modul)
                content = {'status': 'OK', 'detail': f.idfiltre}
                return Response(data=content, status=400)
            except Filtrejson.DoesNotExist:
                content = {'status': 'KO', 'detail': 'exists_not'}
                return Response(data=content, status=200)


@api_view(['GET'])
def users_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('user.username', 'user.first_name', 'user.last_name', 'user.email')
        sort_translation_list = {'user.username': 'user__username', 'user.first_name': 'user__first_name',
                                 'user.last_name': 'user__last_name', 'user.email': 'user__email'}
        field_translation_list = {'user.username': 'user__username', 'user.first_name': 'user__first_name',
                                  'user.last_name': 'user__last_name', 'user.email': 'user__email'}
        response = generic_datatable_list_endpoint(request, search_field_list, Profile, ProfileSerializer,
                                                   field_translation_list, sort_translation_list)
        return response


@api_view(['GET'])
def recursos_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('nom',)
        sort_translation_list = {}
        field_translation_list = {}
        response = generic_datatable_list_endpoint(request, search_field_list, Recursgeoref, RecursgeorefSerializer,
                                                   field_translation_list, sort_translation_list)
        return response


@api_view(['GET'])
def toponims_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('nom_str', 'aquatic_str', 'idtipustoponim.nom')
        sort_translation_list = {'nom_str': 'nom', 'aquatic_str': 'aquatic',
                                 'idtipustoponim.nom': 'idtipustoponim__nom'}
        field_translation_list = {'nom_str': 'nom', 'aquatic_str': 'aquatic',
                                  'idtipustoponim.nom': 'idtipustoponim__nom'}
        response = generic_datatable_list_endpoint(request, search_field_list, Toponim, ToponimSerializer,
                                                   field_translation_list, sort_translation_list)
        return response


@api_view(['GET'])
def tipusunitats_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('tipusunitat',)
        response = generic_datatable_list_endpoint(request, search_field_list, Tipusunitats, TipusunitatsSerializer)
        return response


@api_view(['GET'])
def tipustoponim_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('nom',)
        response = generic_datatable_list_endpoint(request, search_field_list, Tipustoponim, TipusToponimSerializer)
        return response


@api_view(['GET'])
def suport_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('nom',)
        response = generic_datatable_list_endpoint(request, search_field_list, Suport, SuportSerializer)
        return response


@api_view(['GET'])
def tipusrecurs_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('nom',)
        response = generic_datatable_list_endpoint(request, search_field_list, Tipusrecursgeoref, TipusrecursgeorefSerializer)
        return response


@api_view(['GET'])
def paraulaclau_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('paraula',)
        response = generic_datatable_list_endpoint(request, search_field_list, Paraulaclau, ParaulaClauSerializer)
        return response


@api_view(['GET'])
def paisos_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('nom',)
        response = generic_datatable_list_endpoint(request, search_field_list, Pais, PaisSerializer)
        return response


@api_view(['GET'])
def autors_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('nom',)
        response = generic_datatable_list_endpoint(request, search_field_list, Autor, AutorSerializer)
        return response


@api_view(['GET'])
def capeswmslocals_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('name', 'label',)
        response = generic_datatable_list_endpoint(request, search_field_list, Capawms, CapawmsSerializer)
        return response


@api_view(['GET'])
def qualificadors_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('qualificador',)
        response = generic_datatable_list_endpoint(request, search_field_list, Qualificadorversio, QualificadorversioSerializer)
        return response


@api_view(['GET'])
def filters_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('nomfiltre',)
        response = generic_datatable_list_endpoint(request, search_field_list, Filtrejson, FiltrejsonSerializer)
        return response


@api_view(['GET'])
def process_shapefile(request):
    if request.method == 'GET':
        path = request.query_params.get('path', None)
        if path is None:
            content = {'success': False, 'detail': 'Ruta de fitxer incorrecta o fitxer no trobat!'}
            return Response(data=content, status=400)
        else:
            filepath = path
            filename = ntpath.basename(os.path.splitext(filepath)[0])
            presumed_zipfile = magic.from_file(filepath)
            if not presumed_zipfile.lower().startswith('zip archive'):
                content = {'success': False, 'detail': 'No sembla que el fitxer sigui un zip correcte'}
                return Response(data=content, status=400)
            else:
                # Extract file
                zip_ref = zipfile.ZipFile(filepath, 'r')
                zip_ref.extractall(BASE_DIR + "/uploads/" + filename)
                zip_ref.close()
                # Find and import shapefile
                os.chdir(BASE_DIR + "/uploads/" + filename)
                for file in glob.glob("*.shp"):
                    presumed_shapefile = magic.from_file(BASE_DIR + "/uploads/" + filename + "/" + file)
                    if presumed_shapefile.lower().startswith('esri shapefile'):
                        sf = shapefile.Reader(BASE_DIR + "/uploads/" + filename + "/" + file)
                        fields = sf.fields[1:]
                        field_names = [field[0] for field in fields]
                        buffer = []
                        for sr in sf.shapeRecords():
                            atr = dict(zip(field_names, sr.record))
                            geom = sr.shape.__geo_interface__
                            buffer.append(dict(type="Feature", geometry=geom, properties=atr))
                        geojson = dumps({"type": "FeatureCollection", "features": buffer})
                        content = {'success': True, 'detail': geojson}
                        return Response(data=content, status=200)
                    else:
                        content = {'success': False, 'detail': 'El fitxer shapefile té un format incorrecte'}
                        return Response(data=content, status=200)
                content = {'success': False,
                           'detail': 'No he trobat cap fitxer amb extensió *.shp dins del zip, no puc importar res.'}
                return Response(data=content, status=200)


@login_required
def recursfilters(request):
    csrf_token = get_token(request)
    return render(request, 'georef/recursfilters_list.html', context={'csrf_token': csrf_token})


@login_required
def toponimfilters(request):
    csrf_token = get_token(request)
    return render(request, 'georef/toponimfilters_list.html', context={'csrf_token': csrf_token})


@login_required
def users_list(request):
    if request.user.profile and request.user.profile.permission_administrative == False:
        return HttpResponse(reverse(index))
    else:
        return render(request, 'georef/user_list.html')


@login_required
def recursos(request):
    csrf_token = get_token(request)
    llista_tipus = Suport.objects.order_by('nom')
    wms_url = conf.GEOSERVER_WMS_URL
    return render(request, 'georef/recursos_list.html',
                  context={'llista_tipus': llista_tipus, 'wms_url': wms_url, 'csrf_token': csrf_token})


@login_required
def toponims(request):
    csrf_token = get_token(request)
    wms_url = conf.GEOSERVER_WMS_URL
    llista_tipus = Tipustoponim.objects.order_by('nom')
    llista_paisos = Pais.objects.order_by('nom')
    return render(request, 'georef/toponims_list.html',
                  context={'llista_tipus': llista_tipus, 'llista_paisos': llista_paisos, 'csrf_token': csrf_token,
                           'wms_url': wms_url})

@login_required
def calculcentroides(request):
    return render(request, 'georef/calculcentroides.html')


@login_required
def toponimstree(request):
    return render(request, 'georef/toponimstree.html')


def get_node_from_toponim(toponim):
    if Toponim.objects.filter(idpare=toponim.id).exists():
        toponim_node = {'text': toponim.nom_str, 'id': toponim.id, 'children': True}
    else:
        toponim_node = {'text': toponim.nom_str, 'id': toponim.id}
    return toponim_node


@login_required
def graphs(request):
    cursor = connection.cursor()

    cursor.execute("""
        select count(idtoponim), u.last_name || ', ' || u.first_name
        from 
        toponimversio t,
        auth_user u
        where 
        iduser is not null AND
        t.iduser = u.id
        group by u.last_name || ', ' || u.first_name order by 1 desc     
    """)

    toponims_georeferenciador = cursor.fetchall()

    cursor.execute("""
        select
        p.nom, count(t.id) from
        toponim t, pais p 
        where idpais is not null AND t.idpais = p.id group by p.nom order by 2 desc
    """)

    toponims_pais = cursor.fetchall()

    cursor.execute("""
        select tp.nom, count(t.id)
        from 
        toponim t,
        tipustoponim tp
        where idpais is not null AND
        t.idtipustoponim = tp.id
        group by tp.nom order by 2 desc;
    """)

    toponims_tipus = cursor.fetchall()

    cursor.execute("""
        select aquatic,count(id)
        from 
        toponim t
        group by aquatic
    """)

    toponims_aquatic = cursor.fetchall()

    cursor.execute("""
        select t.nom, count(r.id)
        from 
        recursgeoref r,
        tipusrecursgeoref t
        where 
        r.idtipusrecursgeoref = t.id
        group by t.nom order by 2 desc
    """)

    recursos_tipus = cursor.fetchall()

    context = {
        'toponims_georeferenciador': json.dumps(toponims_georeferenciador),
        'toponims_pais': json.dumps(toponims_pais),
        'toponims_tipus': json.dumps(toponims_tipus),
        'toponims_aquatic': json.dumps(toponims_aquatic),
        'recursos_tipus' : json.dumps(recursos_tipus),
    }

    return render(request, 'georef/graphs.html', context)


@api_view(['GET'])
def toponimstreenode(request):
    if request.method == 'GET':
        toponims = None
        data = []
        node_id = request.query_params.get('id', None)
        if node_id == '#':
            elem = {'text': 'Tots els topònims', 'id': '1', 'parent': '#', 'children': True}
            return Response(data=elem, status=200)
        elif node_id == '1':
            toponims = Toponim.objects.filter(idpare__isnull=True).order_by('nom')
        else:
            toponims = Toponim.objects.filter(idpare=node_id).order_by('nom')
        for toponim in toponims:
            elem = get_node_from_toponim(toponim)
            data.append(elem)
        return Response(data=data, status=200)


'''
@login_required
def toponims_update(request, id=None):
    if id:
        toponim = get_object_or_404(Toponim,pk=id)
    else:
        raise forms.ValidationError("No existeix aquest topònim")
    form = ToponimsUpdateForm(request.POST or None, instance=toponim)
    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('toponims'))
    return render(request, 'georef/toponim_update.html', {'form': form, 'id' : id, 'nodelist_full': toponim.get_denormalized_toponimtree(), 'nodelist': toponim.get_denormalized_toponimtree_clean()})
'''


@login_required
def recursos_create(request):
    if request.method == 'POST':
        form = RecursForm(request.POST or None)
        if form.is_valid():
            with transaction.atomic():
                recurs = form.save(commit=False)
                paraules_clau_string = request.POST.get("paraulesclau", "")
                autors_string = request.POST.get("autors", "")
                capeswms_string = request.POST.get("capeswms", "")
                paraules_clau = paraules_clau_string.split(',')
                autors = autors_string.split(',')
                capeswms_tokens = capeswms_string.split(',')

                recurs.paraulesclau.clear()
                recurs.autors.clear()
                recurs.capes_wms_recurs.clear()
                recurs.save()

                for paraula in paraules_clau:
                    if paraula != '':
                        try:
                            p = Paraulaclau.objects.get(paraula=paraula)
                        except Paraulaclau.DoesNotExist:
                            p = Paraulaclau(paraula=paraula)
                            p.save()
                        pcr = ParaulaclauRecurs(idparaula=p, idrecursgeoref=recurs)
                        pcr.save()

                for autor in autors:
                    if autor != '':
                        try:
                            a = Autor.objects.get(nom=autor)
                        except Autor.DoesNotExist:
                            a = Autor(nom=autor)
                            a.save()
                        arg = Autorrecursgeoref(autor=a, recurs=recurs)
                        arg.save()

                for capa in capeswms_tokens:
                    if capa != '':
                        c = Capawms.objects.get(pk=capa)
                        cr = Capesrecurs(idcapa=c, idrecurs=recurs)
                        cr.save()

                url = reverse('recursos')
                return HttpResponseRedirect(url)
    else:
        form = RecursForm()
    return render(request, 'georef/recurs_create.html', {'form': form})


def toponims_search(request):
    context = {}
    return render(request, 'georef/toponim_search.html', context)

@login_required
def toponims_create(request):
    if request.method == 'POST':
        form = ToponimsUpdateForm(request.POST or None)
        if form.is_valid():
            form.save()
            url = reverse('toponims_update_2', kwargs={'idtoponim': form.instance.id, 'idversio': '-1'})
            return HttpResponseRedirect(url)
    else:
        this_user = request.user
        id_toponim = request.user.profile.toponim_permission
        try:
            toponim = Toponim.objects.get(pk=id_toponim)
            node_ini = toponim.id
            nodelist_full = format_denormalized_toponimtree(compute_denormalized_toponim_tree_val(toponim))
        except Toponim.DoesNotExist:
            node_ini = '1'
            nodelist_full = ['1']
        form = ToponimsUpdateForm()
    return render(request, 'georef/toponim_create.html',
                  {'form': form, 'wms_url': conf.GEOSERVER_WMS_URL, 'node_ini': node_ini,
                   'nodelist_full': nodelist_full})


def recursgeoref_geometries_to_geojson(recurs):
    geometries = recurs.geometries.all()
    geos = []
    for geom in geometries:
        geos.append({'type': 'Feature', 'properties': {}, 'geometry': json.loads(geom.geometria.json)})
    features = {
        'type': 'FeatureCollection',
        'features': geos
    }
    return json.dumps(features)


def toponimversio_geometries_to_geojson(toponimversio):
    geometries = toponimversio.geometries.all()
    geos = []
    for geom in geometries:
        geos.append({'type': 'Feature', 'properties': {}, 'geometry': json.loads(geom.geometria.json)})
    features = {
        'type': 'FeatureCollection',
        'features': geos
    }
    return json.dumps(features)


@login_required
def toponims_update_2(request, idtoponim=None, idversio=None):
    versio = None
    geometries_json = None
    id_darrera_versio = None
    toponim = get_object_or_404(Toponim, pk=idtoponim)
    nodelist_full = format_denormalized_toponimtree(compute_denormalized_toponim_tree_val(toponim))
    toponimsversio = Toponimversio.objects.filter(idtoponim=toponim).order_by('-numero_versio')
    this_user = request.user
    node_ini = '1'
    if this_user.profile.permission_toponim_edition == False:
        return HttpResponse('No tens permís per editar topònims. Operació no permesa.')
    else:
        if toponim.can_i_edit(this_user.profile.toponim_permission):
            node_ini = this_user.profile.toponim_permission
        else:
            toponim_mes_alt = Toponim.objects.get(pk=this_user.profile.toponim_permission)
            message = (
                          'No tens permís per editar aquest topònim. El topònim més alt a l\'arbre que pots editar és %s i aquest està jeràrquicament per sobre. Operació no permesa.') % (
                          toponim_mes_alt.nom_str)
            return HttpResponse(message)
    if request.method == 'GET':
        if idversio == '-1':
            if (len(toponimsversio) > 0):
                versio = toponimsversio[0]
                id_darrera_versio = versio.id
        elif idversio == '-2':  # Afegint nova versió
            id_darrera_versio = '-2'
        else:
            versio = get_object_or_404(Toponimversio, pk=idversio)
            id_darrera_versio = idversio
        toponim_form = ToponimsUpdateForm(request.GET or None, instance=toponim)
        if versio:
            toponimversio_form = ToponimversioForm(request.GET or None, instance=versio)
            geometries_json = toponimversio_geometries_to_geojson(versio)
        else:
            toponimversio_form = ToponimversioForm(request.GET or None)
        context = {
            'geometries_json': geometries_json,
            'form': toponim_form,
            'toponimversio_form': toponimversio_form,
            'idtoponim': idtoponim,
            'idversio': idversio,
            'nodelist_full': nodelist_full,
            'versions': toponimsversio,
            'id_darrera_versio': id_darrera_versio,
            'node_ini': node_ini
        }
        return render(request, 'georef/toponim_update_2.html', context)
    elif request.method == 'POST':
        if 'save_toponim_from_toponimversio' in request.POST:
            form = ToponimsUpdateForm(request.POST or None, instance=toponim)
            if form.is_valid():
                form.save()
                url = reverse('toponims_update_2', kwargs={'idtoponim': form.instance.id, 'idversio': idversio})
                return HttpResponseRedirect(url)
            else:
                if idversio == '-1':
                    if (len(toponimsversio) > 0):
                        versio = toponimsversio[0]
                        id_darrera_versio = versio.id
                else:
                    versio = get_object_or_404(Toponimversio, pk=idversio)
                    id_darrera_versio = idversio
                if versio:
                    toponimversio_form = ToponimversioForm(request.GET or None, instance=versio)
                    geometries_json = toponimversio_geometries_to_geojson(versio)
                else:
                    toponimversio_form = ToponimversioForm(request.GET or None)
                context = {
                    'geometries_json': geometries_json,
                    'form': form,
                    'toponimversio_form': toponimversio_form,
                    'idtoponim': idtoponim,
                    'idversio': idversio,
                    'nodelist_full': nodelist_full,
                    'versions': toponimsversio,
                    'id_darrera_versio': id_darrera_versio,
                    'node_ini': node_ini
                }
                return render(request, 'georef/toponim_update_2.html', context)
        elif 'save_versio_from_toponimversio' in request.POST:
            if idversio == '-1':
                if (len(toponimsversio) > 0):
                    versio = toponimsversio[0]
                    id_darrera_versio = versio.id
                else:
                    id_darrera_versio = -1
            elif idversio == '-2':
                id_darrera_versio = -2
            else:
                versio = get_object_or_404(Toponimversio, pk=idversio)
                id_darrera_versio = idversio
            if versio:
                toponimversio_form = ToponimversioForm(request.POST or None, instance=versio)
                geometries_json = toponimversio_geometries_to_geojson(versio)
            else:
                toponimversio_form = ToponimversioForm(request.POST or None)
            form = ToponimsUpdateForm(request.POST or None, instance=toponim)
            if toponimversio_form.is_valid():
                toponimversio = toponimversio_form.save(commit=False)
                toponimversio.geometries.clear()
                idversio = toponimversio.id
                toponimversio.idtoponim = toponim
                toponimversio.iduser = this_user
                toponimversio.save()

                toponimversio.geometries.clear()
                toponimversio.save()

                json_geometry_string = request.POST["geometria"]
                json_geometry = json.loads(json_geometry_string)
                for feature in json_geometry['features']:
                    feature_geometry = GEOSGeometry(json.dumps(feature['geometry']))
                    g = GeometriaToponimVersio(idversio=toponimversio, geometria=feature_geometry)
                    g.save()

                url = reverse('toponims_update_2', kwargs={'idtoponim': form.instance.id, 'idversio': idversio})
                return HttpResponseRedirect(url)
            else:
                context = {
                    'geometries_json': geometries_json,
                    'form': form,
                    'toponimversio_form': toponimversio_form,
                    'idtoponim': idtoponim,
                    'idversio': idversio,
                    'nodelist_full': nodelist_full,
                    'versions': toponimsversio,
                    'id_darrera_versio': id_darrera_versio,
                    'node_ini': node_ini
                }
                return render(request, 'georef/toponim_update_2.html', context)


@login_required
def recursos_list_csv(request):
    search_field_list = ('nom',)
    sort_translation_list = {}
    field_translation_list = {}
    data = generic_datatable_list_endpoint(request, search_field_list, Recursgeoref, RecursgeorefSerializer,
                                           field_translation_list, sort_translation_list, paginate=False)

    records = data.data['data']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['nom'])
    for record in records:
        writer.writerow([record['nom']])

    return response


@login_required
def recursos_list_xls(request):
    search_field_list = ('nom',)
    sort_translation_list = {}
    field_translation_list = {}
    data = generic_datatable_list_endpoint(request, search_field_list, Recursgeoref, RecursgeorefSerializer,
                                           field_translation_list, sort_translation_list, paginate=False)
    records = data.data['data']

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="recursos.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Recursos')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Nom', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    for record in records:
        row_num += 1
        ws.write(row_num, 0, record['nom'], font_style)

    wb.save(response)
    return response

@login_required
def toponims_import(request):
    context = {}
    return render(request, 'georef/toponims_import.html', context)

@login_required
def toponims_list_xls(request):
    search_field_list = ('nom_str', 'aquatic_str', 'idtipustoponim.nom')
    sort_translation_list = {'nom_str': 'nom', 'aquatic_str': 'aquatic', 'idtipustoponim.nom': 'idtipustoponim__nom'}
    field_translation_list = {'nom_str': 'nom', 'aquatic_str': 'aquatic', 'idtipustoponim.nom': 'idtipustoponim__nom'}
    data = generic_datatable_list_endpoint(request, search_field_list, Toponim, ToponimSerializer,
                                           field_translation_list, sort_translation_list, paginate=False)
    records = data.data['data']

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="toponims.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Toponims')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Nom', 'Aquàtic?', 'Tipus', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    for record in records:
        row_num += 1
        ws.write(row_num, 0, record['nom_str'], font_style)
        ws.write(row_num, 1, record['aquatic'], font_style)
        ws.write(row_num, 2, record['idtipustoponim']['nom'], font_style)

    wb.save(response)
    return response


@login_required
def recursos_list_pdf(request):
    search_field_list = ('nom',)
    sort_translation_list = {}
    field_translation_list = {}
    data = generic_datatable_list_endpoint(request, search_field_list, Recursgeoref, RecursgeorefSerializer,
                                           field_translation_list, sort_translation_list, paginate=False)

    records = data.data['data']
    html_string = render_to_string('georef/reports/recursos_list_pdf.html',
                                   {'title': 'Llistat de Recursos de georeferenciació', 'records': records})

    html = HTML(string=html_string)
    html.write_pdf(target='/tmp/mypdf.pdf');

    fs = FileSystemStorage('/tmp')
    with fs.open('mypdf.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'
        return response

    return response


@login_required
def toponims_list_pdf(request):
    search_field_list = ('nom_str', 'aquatic_str', 'idtipustoponim.nom')
    sort_translation_list = {'nom_str': 'nom', 'aquatic_str': 'aquatic', 'idtipustoponim.nom': 'idtipustoponim__nom'}
    field_translation_list = {'nom_str': 'nom', 'aquatic_str': 'aquatic', 'idtipustoponim.nom': 'idtipustoponim__nom'}
    data = generic_datatable_list_endpoint(request, search_field_list, Toponim, ToponimSerializer,
                                           field_translation_list, sort_translation_list, paginate=False)

    records = data.data['data']
    html_string = render_to_string('georef/reports/toponims_list_pdf.html',
                                   {'title': 'Llistat de topònims', 'records': records})

    html = HTML(string=html_string)
    html.write_pdf(target='/tmp/mypdf.pdf');

    fs = FileSystemStorage('/tmp')
    with fs.open('mypdf.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'
        return response

    return response


@login_required
def toponims_detail_pdf(request, idtoponim=None):
    toponim = get_object_or_404(Toponim, pk=idtoponim)

    html_string = render_to_string('georef/reports/toponim_detail_pdf.html', {'toponim': toponim})
    georef_css = CSS('georef/static/georef/css/georef.css')
    # simple_grid = CSS('georef/static/georef/css/grid/simple-grid.css')
    # styles = [simple_grid, georef_css]
    styles = [georef_css]

    html = HTML(string=html_string)
    html.write_pdf(target='/tmp/mypdf.pdf', stylesheets=styles)

    fs = FileSystemStorage('/tmp')
    with fs.open('mypdf.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'
        return response

    return response


@login_required
def toponims_list_csv(request):
    search_field_list = ('nom_str', 'aquatic_str', 'idtipustoponim.nom')
    sort_translation_list = {'nom_str': 'nom', 'aquatic_str': 'aquatic', 'idtipustoponim.nom': 'idtipustoponim__nom'}
    field_translation_list = {'nom_str': 'nom', 'aquatic_str': 'aquatic', 'idtipustoponim.nom': 'idtipustoponim__nom'}
    data = generic_datatable_list_endpoint(request, search_field_list, Toponim, ToponimSerializer,
                                           field_translation_list, sort_translation_list, paginate=False)

    records = data.data['data']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['nom_toponim', 'aquatic?', 'tipus_toponim'])
    for record in records:
        writer.writerow([record['nom_str'], record['aquatic'], record['idtipustoponim']['nom']])

    return response


@login_required
def my_profile(request):
    successfully_saved = False
    this_user = request.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=this_user)
        if user_form.is_valid():
            user_form.save()
            successfully_saved = True
        else:
            successfully_saved = False
    else:
        user_form = UserForm(instance=this_user)
    return render(request, 'georef/profile.html', {'user_form': user_form, 'successfully_saved': successfully_saved})


@user_passes_test(lambda u: u.is_superuser)
@login_required
@transaction.atomic
def user_profile(request, user_id=None):
    nodelist_full = []
    this_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=this_user)
        profile_form = ProfileForm(request.POST, instance=this_user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            url = reverse('users_list')
            return HttpResponseRedirect(url)
    else:
        user_form = UserForm(instance=this_user)
        profile_form = ProfileForm(instance=this_user.profile)

    if this_user and this_user.profile and this_user.profile.toponim_permission:
        if this_user.profile.toponim_permission == '1':
            nodelist_full = ['1']
        else:
            toponim = get_object_or_404(Toponim, pk=this_user.profile.toponim_permission)
            nodelist_full = format_denormalized_toponimtree(compute_denormalized_toponim_tree_val_to_root(toponim, []))
    return render(request, 'georef/user_profile.html',
                  {'user_id': this_user.id, 'user_form': user_form, 'profile_form': profile_form,
                   'nodelist_full': nodelist_full})


@login_required
def change_my_password(request):
    this_user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password_1']
            this_user.set_password(password)
            this_user.save()
            url = reverse('index')
            return HttpResponseRedirect(url)
    else:
        form = ChangePasswordForm()
    return render(request, 'georef/change_password.html', {'form': form, 'edited_user': None})


@user_passes_test(lambda u: u.is_superuser)
@login_required
def change_password(request, user_id=None):
    this_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password_1']
            this_user.set_password(password)
            this_user.save()
            url = reverse('users_list')
            return HttpResponseRedirect(url)
    else:
        form = ChangePasswordForm()
    return render(request, 'georef/change_password.html', {'form': form, 'edited_user': this_user})


@user_passes_test(lambda u: u.is_superuser)
@login_required
@transaction.atomic
def user_new(request):
    nodelist_full = []
    if request.method == 'POST':
        user_form = NewUserForm(request.POST or None)
        profile_form = ProfileForm(request.POST or None)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            profile = profile_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            user.profile.toponim_permission = profile.toponim_permission
            user.profile.permission_toponim_edition = profile.permission_toponim_edition
            user.profile.permission_administrative = profile.permission_administrative
            user.profile.permission_filter_edition = profile.permission_filter_edition
            user.profile.permission_recurs_edition = profile.permission_recurs_edition
            user.profile.permission_tesaure_edition = profile.permission_tesaure_edition
            user.save()
            url = reverse('users_list')
            return HttpResponseRedirect(url)
    else:
        user_form = NewUserForm()
        profile_form = ProfileForm()
    return render(request, 'georef/user_new.html',
                  {'user_form': user_form, 'profile_form': profile_form, 'nodelist_full': nodelist_full})


@login_required
def recursos_update(request, id=None):
    recurs = get_object_or_404(Recursgeoref, pk=id)
    wms_url = conf.GEOSERVER_WMS_URL
    geometries_json = recursgeoref_geometries_to_geojson(recurs)
    queryset = Toponimversio.objects.filter(idrecursgeoref=recurs).order_by('nom')
    toponimsversio = queryset
    moretoponims = len(queryset) > 20
    capeswms = recurs.capes_wms_recurs.all()
    form = RecursForm(request.POST or None, instance=recurs)
    context = {'form': form, 'paraulesclau': recurs.paraulesclau_str(), 'capeswms': capeswms,
               'autors': recurs.autors_str(), 'toponims_basats_recurs': toponimsversio, 'moretoponims': moretoponims,
               'wms_url': wms_url, 'geometries_json': geometries_json}
    if request.method == 'POST':
        if form.is_valid():
            with transaction.atomic():
                recurs = form.save(commit=False)
                capeswms_string = request.POST.get("capeswms", "")
                paraules_clau_string = request.POST.get("paraulesclau", "")
                autors_string = request.POST.get("autors", "")
                paraules_clau = paraules_clau_string.split(',')
                autors = autors_string.split(',')
                capeswms_tokens = capeswms_string.split(',')

                recurs.paraulesclau.clear()
                recurs.autors.clear()
                recurs.geometries.clear()
                recurs.capes_wms_recurs.clear()

                recurs.save()

                json_geometry_string = request.POST["geometria"]
                json_geometry = json.loads(json_geometry_string)
                for feature in json_geometry['features']:
                    feature_geometry = GEOSGeometry(json.dumps(feature['geometry']))
                    g = GeometriaRecurs(idrecurs=recurs, geometria=feature_geometry)
                    g.save()

                for paraula in paraules_clau:
                    if paraula != '':
                        try:
                            p = Paraulaclau.objects.get(paraula=paraula)
                        except Paraulaclau.DoesNotExist:
                            p = Paraulaclau(paraula=paraula)
                            p.save()
                        pcr = ParaulaclauRecurs(idparaula=p, idrecursgeoref=recurs)
                        pcr.save()

                for autor in autors:
                    if autor != '':
                        try:
                            a = Autor.objects.get(nom=autor)
                        except Autor.DoesNotExist:
                            a = Autor(nom=autor)
                            a.save()
                        arg = Autorrecursgeoref(autor=a, recurs=recurs)
                        arg.save()

                for capa in capeswms_tokens:
                    if capa != '':
                        c = Capawms.objects.get(pk=capa)
                        cr = Capesrecurs(idcapa=c, idrecurs=recurs)
                        cr.save()

                url = reverse('recursos_update', kwargs={'id': form.instance.id})
                return HttpResponseRedirect(url)

    return render(request, 'georef/recurs_update.html', context)


@api_view(['GET'])
def wmsmetadata(request):
    if request.method == 'GET':
        url = request.query_params.get('url', None)
        if url is None:
            content = {'status': 'KO', 'detail': 'mandatory param missing'}
            return Response(data=content, status=400)
        else:
            try:
                wms = WebMapService(url)
                layers = list(wms.contents)
                records = []
                for layer in layers:
                    bounds = wms[layer].boundingBoxWGS84
                    p = Polygon.from_bbox(bounds)
                    p_g = GEOSGeometry(str(p), srid=4326)
                    try:
                        cached_layer = Capawms.objects.get(baseurlservidor=url, name=wms[layer].name,
                                                           label=wms[layer].title)
                        cached_layer.minx = bounds[0]
                        cached_layer.miny = bounds[1]
                        cached_layer.maxx = bounds[2]
                        cached_layer.maxy = bounds[3]
                        cached_layer.boundary = p_g
                    except Capawms.DoesNotExist:
                        cached_layer = Capawms(baseurlservidor=url, name=wms[layer].name, label=wms[layer].title,
                                               minx=bounds[0], miny=bounds[1], maxx=bounds[2], maxy=bounds[3],
                                               boundary=p_g)

                    cached_layer.save()

                    records.append({'id': cached_layer.id, 'name': cached_layer.name, 'title': cached_layer.label,
                                    'minx': cached_layer.minx, 'miny': cached_layer.miny, 'maxx': cached_layer.maxx,
                                    'maxy': cached_layer.maxy})
                content = {'status': 'OK', 'detail': records}
                return Response(data=content, status=200)
            except Exception as e:
                content = {'status': 'KO', 'detail': 'Unexpected exception ' + str(e)}
                return Response(data=content, status=400)


@login_required
def toponims_update(request, id=None):
    toponim = get_object_or_404(Toponim, pk=id)
    nodelist_full = format_denormalized_toponimtree(compute_denormalized_toponim_tree_val(toponim))
    desat_amb_exit = False
    ToponimversioFormSet = formset_factory(ToponimversioForm, extra=0)
    toponimsversio = Toponimversio.objects.filter(idtoponim=toponim).order_by('-numero_versio')
    toponimsversio_data = [
        {
            'numero_versio': versio.numero_versio,
            'idqualificador': versio.idqualificador,
            'idrecursgeoref': versio.idrecursgeoref,
            'nom': versio.nom,
            'datacaptura': versio.datacaptura,
            'coordenada_x_origen': versio.coordenada_x_origen,
            'coordenada_y_origen': versio.coordenada_y_origen,
            'coordenada_z_origen': versio.coordenada_z_origen,
            'precisio_z_origen': versio.precisio_z_origen
        } for versio in toponimsversio
    ]
    toponim_form = ToponimsUpdateForm(request.POST or None, instance=toponim)
    toponimversio_form = ToponimversioFormSet(request.POST or None, initial=toponimsversio_data)
    if request.method == 'POST':
        if toponim_form.is_valid() and toponimversio_form.is_valid():
            toponim_form.save()
            versions = []
            for form in toponimversio_form:
                # toponimversio = form.instance
                toponimversio = Toponimversio(
                    numero_versio=form.cleaned_data.get('numero_versio'),
                    idqualificador=form.cleaned_data.get('idqualificador'),
                    idrecursgeoref=form.cleaned_data.get('idrecursgeoref'),
                    nom=form.cleaned_data.get('nom'),
                    datacaptura=form.cleaned_data.get('datacaptura'),
                    coordenada_x_origen=form.cleaned_data.get('coordenada_x_origen'),
                    coordenada_y_origen=form.cleaned_data.get('coordenada_y_origen'),
                    coordenada_z_origen=form.cleaned_data.get('coordenada_z_origen'),
                    precisio_z_origen=form.cleaned_data.get('precisio_z_origen'),
                    idtoponim=toponim
                )
                versions.append(toponimversio)
                try:
                    with transaction.atomic():
                        Toponimversio.objects.filter(idtoponim=toponim).delete()
                        Toponimversio.objects.bulk_create(versions)
                        desat_amb_exit = True
                except IntegrityError as e:
                    print(e)
    context = {
        'form': toponim_form,
        'tv_form': toponimversio_form,
        'id': id,
        'nodelist_full': nodelist_full,
        'saved_success': desat_amb_exit,
        'wms_url': conf.GEOSERVER_WMS_URL
    }
    return render(request, 'georef/toponim_update.html', context)


import_uploader = AjaxFileUploader()


@login_required
def recursos_capeswms(request):
    context = {}
    return render(request, 'georef/capes_wms.html', context)


@login_required
def prefsvisualitzaciowms(request):
    context = {}
    return render(request, 'georef/prefsvisualitzaciowms.html', context)


@login_required
def georef_layers(request):
    wms_url = conf.GEOSERVER_WMS_URL
    context = {'wms_url' : wms_url}
    return render(request, 'georef/georef_layers.html', context)


@api_view(['POST'])
def toggle_prefs_wms(request):
    if request.method == 'POST':
        current_user = request.user
        id = request.POST.get('id', None)
        value = request.POST.get('value', None)
        if id is None:
            content = {'status': 'KO', 'detail': 'mandatory param missing'}
            return Response(data=content, status=400)
        if value is None:
            content = {'status': 'KO', 'detail': 'mandatory param missing'}
            return Response(data=content, status=400)
        else:
            if value == 'true':
                b_val = True
            else:
                b_val = False
        try:
            prefs = PrefsVisibilitatCapes.objects.get(iduser=current_user)
        except PrefsVisibilitatCapes.DoesNotExist as e:
            prefs = PrefsVisibilitatCapes(iduser=current_user, prefscapesjson='[]')
            prefs.save()
        json_prefs = JsonPrefsUtil(prefs.prefscapesjson)
        if b_val:
            # Add layer to json
            json_prefs.set_layer_to_visible(id)
        else:
            json_prefs.set_layer_not_visible(id)
        prefs.prefscapesjson = json_prefs.to_string()
        prefs.save()
        content = {'status': 'OK', 'detail': 'all cool'}
        return Response(data=content, status=200)


@api_view(['DELETE'])
def wmslocal_delete(request, id=None):
    if request.method == 'DELETE':
        if id is None:
            content = {'status': 'KO', 'detail': 'mandatory param missing'}
            return Response(data=content, status=400)
        try:
            c = Capawms.objects.get(pk=id)
        except Capawms.DoesNotExist as e:
            content = {'status': 'KO', 'detail': 'object does not exist'}
            return Response(data=content, status=400)

        try:
            r = Recursgeoref.objects.get(pk='mz_recursgeoref_r')
        except Recursgeoref.DoesNotExist as e:
            content = {'status': 'KO', 'detail': 'recurs does not exist'}
            return Response(data=content, status=400)

        try:
            cr = Capesrecurs(idcapa=c, idrecurs=r)
        except Capesrecurs.DoesNotExist as e:
            # Not critical
            pass

        ## REMOVE FROM GEOSERVER ##
        try:
            cat = Catalog(conf.GEOSERVER_REST_URL, conf.GEOSERVER_USER, conf.GEOSERVER_PASSWORD)
            st = cat.get_store(c.name)
            # Load layer
            layer = cat.get_layer(c.name)
            # Delete layer
            cat.delete(layer)
            # Reload catalog to make it aware it no longer contains the layer
            cat.reload()
            # Remove store
            cat.delete(st)
        except ConnectionError as ce:
            content = {'status': 'KO', 'detail': 'Error de connexio amb la instancia de geoserver'}
            return Response(data=content, status=400)

        ## REMOVE FROM DATABASE ##
        try:
            with transaction.atomic():
                if cr is not None:
                    cr.delete()
                c.delete()
        except Exception as e:
            content = {'status': 'KO', 'detail': 'unexpected error: ' + str(e)}
            return Response(data=content, status=400)

        content = {'status': 'OK', 'detail': 'deleted'}
        return Response(data=content, status=200)


def get_max_distance(coords, centroid):
    max_dist = 0
    geod = pyproj.Geod(ellps='WGS84')
    for coord in coords:
        angle1, angle2, distance = geod.inv(centroid.x, centroid.y, coord[0], coord[1])
        if distance >= 0:
            max_dist = distance
    return max_dist


@api_view(['POST'])
def import_toponims(request, file_name=None):
    if file_name is None or file_name.strip() == '':
        content = {'status': 'KO', 'detail': 'mandatory param missing'}
        return Response(data=content, status=400)
    filepath = UPLOAD_DIR + '/' + file_name
    filename = ntpath.basename(os.path.splitext(filepath)[0])
    file_type = magic.from_file(filepath)
    if not 'text' in file_type:
        content = {'status': 'KO', 'detail': file_type}
        return Response(data=content, status=400)
    else: #seems to be text file
        #read file
        file_array = []
        raw_lines = []
        errors = []
        with open(filepath) as f:
            raw_lines = f.readlines()
        raw_lines = [x.strip() for x in raw_lines]
        with open(filepath,'rt') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.reader(csvfile,dialect)
            for row in reader:
                file_array.append(row)
            try:
                check_file_structure(file_array)
            except NumberOfColumnsException as n:
                details = n.args[0]
                msg = "Problema amb l'estructura del fitxer. S'esperaven 17 columnes i se n'han trobat " + details["numcols"] + " a la fila " + details["numrow"]
                errors.append(msg)
            except EmptyFileException as e:
                msg = "Sembla que el fitxer té menys de 2 línies"
                errors.append(msg)

            contador_fila = 1
            toponims_exist = []
            toponims_to_create = []
            problems = {}
            if len(errors) == 0:
                for fila, linia in zip(file_array[1:], raw_lines[1:]):
                    process_line(fila, linia, errors, toponims_exist, toponims_to_create, contador_fila, problems, filename)
                    contador_fila += 1

        if len(errors) > 0:
            content = {'status': 'KO', 'detail': errors}
            return Response(data=content, status=400)
        else:
            for toponim_and_versio in toponims_to_create:
                t = toponim_and_versio['toponim']
                v = toponim_and_versio['versio']
                t.save()
                v.idtoponim = t
                v.save()
            success_report = create_success_report(toponims_to_create, toponims_exist)
            filelink = create_result_csv(toponims_to_create, toponims_exist, request)
            content = {'status': 'OK', 'detail': file_type, 'results': success_report, 'fileLink': filelink}
            return Response(data=content, status=200)


def create_result_csv(toponims_to_create, toponims_exist, request):
    file_name = str(uuid.uuid4()) + ".csv"
    file_path = UPLOAD_DIR + "/" + file_name
    with open(file_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter = ';', quotechar='"')
        csvwriter.writerow(['Nom topònim', 'Enllaç al topònim' , 'Afegit o existent?'])
        for info_elem in toponims_to_create:
            toponim_url = request.build_absolute_uri( reverse('toponims_update_2', args=[info_elem['toponim'].id,'-1']) )
            csvwriter.writerow([info_elem['toponim'].nom, toponim_url,'afegit'])
        for toponim in toponims_exist:
            toponim_url = request.build_absolute_uri( reverse('toponims_update_2', args=[toponim.id, '-1']) )
            csvwriter.writerow([toponim.nom, toponim_url, 'existent'])
    csvfile.close()
    return "/" + settings.MEDIA_URL + file_name


def create_success_report(toponims_to_create, toponims_exist):
    report = []
    report.append({'numToponimsCreats': len(toponims_to_create) })
    report.append({'numToponimsJaExisteixen': len(toponims_exist)})
    created = []
    existing = []
    for info_elem in toponims_to_create:
        created.append({ 'id': info_elem['toponim'].id, 'nom': info_elem['toponim'].nom })
    report.append( { 'creats': created } )
    for toponim in toponims_exist:
        existing.append( { 'id': toponim.id, 'nom': toponim.nom } )
    report.append({'existents': existing })
    return report


@api_view(['POST'])
def compute_shapefile_centroid(request, file_name=None):
    if file_name is None:
        content = {'status': 'KO', 'detail': 'mandatory param missing'}
        return Response(data=content, status=400)
    filepath = UPLOAD_DIR + '/' + file_name
    filename = ntpath.basename(os.path.splitext(filepath)[0])
    file_type = magic.from_file(filepath)
    if file_type.lower().startswith('zip archive'):
        # decompress, check shapefile
        # Extract file
        zip_ref = zipfile.ZipFile(filepath, 'r')
        zip_ref.extractall(UPLOAD_DIR + '/' + filename)
        zip_ref.close()
        # Check shapefile
        # Find and import shapefile
        os.chdir(UPLOAD_DIR + '/' + filename)
        for file in glob.glob("*.shp"):
            presumed_shapefile = magic.from_file(UPLOAD_DIR + '/' + filename + "/" + file)
            if presumed_shapefile.lower().startswith('esri shapefile'):
                # OK, apparently is a shapefile. Let's check if the projection is ok
                infile = ogr.Open(UPLOAD_DIR + '/' + filename + '/' + file)
                layer = infile.GetLayer()
                spatialRef = layer.GetSpatialRef()
                authority = spatialRef.GetAttrValue('authority', 0)
                srs_code = spatialRef.GetAttrValue('authority', 1)
                if authority == 'EPSG' and srs_code == '4326':
                    sf = shapefile.Reader(BASE_DIR + "/uploads/" + filename + "/" + file)
                    fields = sf.fields[1:]
                    field_names = [field[0] for field in fields]
                    buffer = []
                    geometry_union = None
                    coords = []
                    for sr in sf.shapeRecords():
                        atr = dict(zip(field_names, sr.record))
                        geom = sr.shape.__geo_interface__
                        geometry = GEOSGeometry(dumps(geom))
                        if geometry.geom_type == 'LineString':
                            for coord in geometry.coords:
                                coords.append(coord)
                        elif geometry.geom_type == 'Point':
                            coords.append(geometry.coords)
                        elif geometry.geom_type == 'Polygon':
                            for linestring in geometry.coords:
                                for coord in linestring:
                                    coords.append(coord)
                        else:
                            content = {'status': 'KO', 'detail': 'Tipus de geometria desconegut: ' + geometry.geom_type}
                            return Response(data=content, status=400)
                        if geometry_union is None:
                            geometry_union = geometry
                        else:
                            geometry_union = geometry_union.union(geometry)
                    if geometry_union is None:
                        content = {'status': 'KO','detail': 'El fitxer shapefile no conté geometria. No puc calcular res.'}
                        return Response(data=content, status=400)
                    else:
                        centroid = geometry_union.centroid
                        radi_incertesa = get_max_distance(coords, centroid)
                        results = { 'centroid_x': centroid.x, 'centroid_y': centroid.y, 'inc': radi_incertesa}
                        content = {'status': 'OK', 'detail': results}
                        return Response(data=content, status=200)
                else:
                    # Delete exploded zip
                    rmtree(UPLOAD_DIR + '/' + filename)
                    content = {'status': 'KO',
                               'detail': 'Projecció {}:{} no suportada. Cal que el shapefile estigui en EPSG:4326'.format(
                                   authority, srs_code)}
                    return Response(data=content, status=400)

    else:
        os.remove(filepath)
        content = {'status': 'KO', 'detail': 'Tipus de fitxer no identificat: "{}"'.format(file_type)}
        return Response(data=content, status=400)

@api_view(['POST'])
def wmslocal_create(request):
    file_name = request.POST.get('filename', None)
    title = request.POST.get('title', None)
    if file_name is None:
        content = {'status': 'KO', 'detail': 'mandatory param missing'}
        return Response(data=content, status=400)
    filepath = UPLOAD_DIR + '/' + file_name
    filename = ntpath.basename(os.path.splitext(filepath)[0])
    layer_name = filename
    store_name = filename
    file_type = magic.from_file(filepath)
    if file_type.lower().startswith('zip archive'):
        # decompress, check shapefile
        # Extract file
        zip_ref = zipfile.ZipFile(filepath, 'r')
        zip_ref.extractall(UPLOAD_DIR + '/' + filename)
        zip_ref.close()
        # Check shapefile
        # Find and import shapefile
        os.chdir(UPLOAD_DIR + '/' + filename)
        for file in glob.glob("*.shp"):
            presumed_shapefile = magic.from_file(UPLOAD_DIR + '/' + filename + "/" + file)
            if presumed_shapefile.lower().startswith('esri shapefile'):
                # OK, apparently is a shapefile. Let's check if the projection is ok
                infile = ogr.Open(UPLOAD_DIR + '/' + filename + '/' + file)
                layer = infile.GetLayer()
                spatialRef = layer.GetSpatialRef()
                authority = spatialRef.GetAttrValue('authority', 0)
                srs_code = spatialRef.GetAttrValue('authority', 1)
                if authority == 'EPSG' and srs_code == '4326':
                    try:
                        cat = Catalog(conf.GEOSERVER_REST_URL, conf.GEOSERVER_USER, conf.GEOSERVER_PASSWORD)
                        ws = cat.get_workspace(conf.GEOSERVER_WORKSPACE)
                        # create_featurestore takes as parameter the whole zipped file
                        ft = cat.create_featurestore(ntpath.basename(os.path.splitext(file)[0]), filepath, ws)
                        resource = cat.get_resource(ntpath.basename(os.path.splitext(file)[0]),
                                                    workspace=conf.GEOSERVER_WORKSPACE)
                        resource.title = title
                        cat.save(resource)
                        # create associated capawms
                        wms = WebMapService(conf.GEOSERVER_WMS_URL_CLEAN)
                        wms_layer = wms.contents[
                            conf.GEOSERVER_WORKSPACE + ':' + ntpath.basename(os.path.splitext(file)[0])]
                        bounds = wms_layer.boundingBoxWGS84
                        p = Polygon.from_bbox(bounds)
                        p_g = GEOSGeometry(str(p), srid=4326)
                        with transaction.atomic():
                            capawms = Capawms(baseurlservidor=conf.GEOSERVER_WMS_URL_CLEAN,
                                              name=ntpath.basename(os.path.splitext(file)[0]), label=wms_layer.title,
                                              minx=bounds[0], miny=bounds[1], maxx=bounds[2], maxy=bounds[3],
                                              boundary=p_g)
                            capawms.save()
                            recurs = Recursgeoref.objects.get(pk='mz_recursgeoref_r')
                            cr = Capesrecurs(idcapa=capawms, idrecurs=recurs)
                            cr.save()
                        # cleanup
                        # Delete exploded zip
                        rmtree(UPLOAD_DIR + '/' + filename)
                        content = {'status': 'OK', 'detail': 'its a shapefile, called {}'.format(
                            UPLOAD_DIR + '/' + filename + "/" + file)}
                        return Response(data=content, status=200)
                    except ConflictingDataError as ce:
                        # Delete exploded zip
                        rmtree(UPLOAD_DIR + '/' + filename)
                        content = {'status': 'KO',
                                   'detail': 'Ja existeix una capa amb el nom {}:{} al servidor geoserver'.format(
                                       conf.GEOSERVER_WORKSPACE, layer_name)}
                        return Response(data=content, status=400)
                    except ConnectionError as ce:
                        # Delete exploded zip
                        rmtree(UPLOAD_DIR + '/' + filename)
                        content = {'status': 'KO',
                                   'detail': 'Error de connexió amb el servidor geoserver. L\'adreça {} ha deixat de respondre.'.format(
                                       conf.GEOSERVER_REST_URL)}
                        return Response(data=content, status=400)
                    except Exception as e:
                        # Delete exploded zip
                        rmtree(UPLOAD_DIR + '/' + filename)
                        content = {'status': 'KO', 'detail': 'Error no esperat'}
                        return Response(data=content, status=400)
                else:
                    # Delete exploded zip
                    rmtree(UPLOAD_DIR + '/' + filename)
                    content = {'status': 'KO',
                               'detail': 'Projecció {}:{} no suportada. Cal que el shapefile estigui en EPSG:4326'.format(
                                   authority, srs_code)}
                    return Response(data=content, status=400)
        pass
    elif file_type.lower().startswith('tiff image data'):
        # check projection
        ds = gdal.Open(filepath)
        prj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        authority = srs.GetAttrValue('authority', 0)
        srs_code = srs.GetAttrValue('authority', 1)
        if authority == 'EPSG' and srs_code == '4326':
            cat = Catalog(conf.GEOSERVER_REST_URL, conf.GEOSERVER_USER, conf.GEOSERVER_PASSWORD)
            try:
                ws = cat.get_workspace(conf.GEOSERVER_WORKSPACE)
                cat.create_coveragestore(filename, filepath, ws)
                resource = cat.get_resource(filename, workspace=conf.GEOSERVER_WORKSPACE)
                resource.title = title
                cat.save(resource)
                # create associated capawms
                wms = WebMapService(conf.GEOSERVER_WMS_URL_CLEAN)
                wms_layer = wms.contents[conf.GEOSERVER_WORKSPACE + ':' + layer_name]
                bounds = wms_layer.boundingBoxWGS84
                p = Polygon.from_bbox(bounds)
                p_g = GEOSGeometry(str(p), srid=4326)
                with transaction.atomic():
                    capawms = Capawms(baseurlservidor=conf.GEOSERVER_WMS_URL_CLEAN, name=layer_name,
                                      label=wms_layer.title, minx=bounds[0], miny=bounds[1], maxx=bounds[2],
                                      maxy=bounds[3], boundary=p_g)
                    capawms.save()
                    recurs = Recursgeoref.objects.get(pk='mz_recursgeoref_r')
                    cr = Capesrecurs(idcapa=capawms, idrecurs=recurs)
                    cr.save()
                os.remove(filepath)
                content = {'status': 'OK',
                           'detail': 'layer name will be {}, store name will be {}'.format(layer_name, store_name)}
                return Response(data=content, status=200)
            except ConnectionError as ce:
                os.remove(filepath)
                content = {'status': 'KO',
                           'detail': 'Error de connexió amb el servidor geoserver. L\'adreça {} ha deixat de respondre.'.format(
                               conf.GEOSERVER_REST_URL)}
                return Response(data=content, status=400)
            except Exception as e:
                os.remove(filepath)
                content = {'status': 'KO', 'detail': 'Error no esperat'}
                return Response(data=content, status=400)
        else:
            os.remove(filepath)
            content = {'status': 'KO',
                       'detail': 'La projecció {}:{}, del ràster no està suportada. Cal que el ràster estigui en EPSG:4326'.format(
                           authority, srs_code)}
            return Response(data=content, status=400)
    else:
        os.remove(filepath)
        content = {'status': 'KO', 'detail': 'Tipus de fitxer no identificat {}'.format(file_type)}
        return Response(data=content, status=400)


@login_required
def t_authors(request):
    context = {
        'text_field_name' : 'nom',
        'column_name': 'Nom autor',
        'class_name_sing': 'Autor',
        'crud_url': reverse('autors-list'),
        'list_url': reverse('autors_datatable_list'),
    }
    return render(request, 'georef/t_generic.html', context)


@login_required
def t_qualificadors(request):
    context = {
        'text_field_name' : 'qualificador',
        'column_name': 'Nom qualificador',
        'class_name_sing': 'Qualificador versió',
        'crud_url': reverse('qualificadorsversio-list'),
        'list_url': reverse('qualificadors_datatable_list'),
    }
    return render(request, 'georef/t_generic.html', context)


@login_required
def t_paisos(request):
    context = {
        'text_field_name' : 'nom',
        'column_name': 'Nom país',
        'class_name_sing': 'País',
        'crud_url': reverse('paisos-list'),
        'list_url': reverse('paisos_datatable_list'),
    }
    return render(request, 'georef/t_generic.html', context)


@login_required
def t_paraulesclau(request):
    context = {
        'text_field_name' : 'paraula',
        'column_name': 'Paraula clau',
        'class_name_sing': 'Paraula clau',
        'crud_url': reverse('paraulesclau-list'),
        'list_url': reverse('paraulaclau_datatable_list'),
    }
    return render(request, 'georef/t_generic.html', context)


@login_required
def t_tipuscontingut(request):
    context = {
        'text_field_name' : 'nom',
        'column_name': 'Tipus de contingut',
        'class_name_sing': 'Tipus de contingut',
        'crud_url': reverse('tipusrecurs-list'),
        'list_url': reverse('tipusrecurs_datatable_list'),
    }
    return render(request, 'georef/t_generic.html', context)


@login_required
def t_tipussuport(request):
    context = {
        'text_field_name' : 'nom',
        'column_name': 'Tipus de suport',
        'class_name_sing': 'Tipus de suport',
        'crud_url': reverse('tipussuport-list'),
        'list_url': reverse('suport_datatable_list'),
    }
    return render(request, 'georef/t_generic.html', context)


@login_required
def t_tipustoponim(request):
    context = {
        'text_field_name' : 'nom',
        'column_name': 'Tipus de topònim',
        'class_name_sing': 'Tipus de topònim',
        'crud_url': reverse('tipustoponim-list'),
        'list_url': reverse('tipustoponim_datatable_list'),
    }
    return render(request, 'georef/t_generic.html', context)

@login_required
def t_tipusunitats(request):
    context = {
        'text_field_name' : 'tipusunitat',
        'column_name': "Tipus d'unitats",
        'class_name_sing': "Tipus d'unitats",
        'crud_url': reverse('tipusunitats-list'),
        'list_url': reverse('tipusunitats_datatable_list'),
    }
    return render(request, 'georef/t_generic.html', context)