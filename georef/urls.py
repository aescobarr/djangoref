from django.urls import re_path, include
from django.conf.urls.static import static
from rest_framework import routers
from georef import views
from django.conf import settings

from . import views
from django.views.i18n import JavaScriptCatalog

router = routers.DefaultRouter()
router.register(r'toponims', views.ToponimViewSet, basename='toponims')
router.register(r'toponimsearch', views.ToponimSearchViewSet, basename='toponimsearch')
router.register(r'toponimparesearch', views.ToponimPareSearchViewSet, basename='toponimparesearch')
router.register(r'filtres', views.FiltrejsonViewSet, basename='filtres')
router.register(r'recursgeoref', views.RecursGeoRefViewSet, basename='recursgeoref')
router.register(r'versions', views.ToponimVersioViewSet, basename='versions')
router.register(r'users', views.UsersViewSet, basename='users')
router.register(r'paraulesclau', views.ParaulaClauViewSet, basename='paraulesclau')
router.register(r'protocols', views.ProtocolsViewSet, basename='protocols')
router.register(r'autors', views.AutorViewSet, basename='autors')
router.register(r'qualificadorsversio', views.QualificadorViewSet, basename='qualificadorsversio')
router.register(r'organizations', views.OrganizationViewSet, basename='organizations')
router.register(r'tipusrecurs', views.TipusrecursgeorefViewSet, basename='tipusrecurs')
router.register(r'tipussuport', views.TipusSuportViewSet, basename='tipussuport')
router.register(r'tipustoponim', views.TipusToponimViewSet, basename='tipustoponim')
router.register(r'tipusunitats', views.TipusUnitatsViewSet, basename='tipusunitats')
router.register(r'sistemareferenciamm', views.SistemaReferenciammViewSet, basename='sistemareferenciamm')
router.register(r'paisos', views.PaisViewSet, basename='paisos')
router.register(r'menuitems', views.MenuItemViewSet, basename='menuitems')

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^Zoologia/', views.index, name='index'),

    re_path(r'^api_internal/',include(router.urls)),

    re_path(r'^datatabletoponims/list$', views.toponims_datatable_list, name='toponims_datatable_list'),
    re_path(r'^datatablerecursos/list$', views.recursos_datatable_list, name='recursos_datatable_list'),
    re_path(r'^datatableusers/list$', views.users_datatable_list, name='users_datatable_list'),
    re_path(r'^datatabletoponimfilters/list$', views.filters_datatable_list, name='toponimfilters_datatable_list'),
    re_path(r'^datatablerecursfilters/list$', views.filters_datatable_list, name='recursfilters_datatable_list'),
    re_path(r'^datatablecapeswmslocals/list$', views.capeswmslocals_datatable_list, name='capeswmslocals_datatable_list'),
    re_path(r'^datatablequalificadors/list$', views.qualificadors_datatable_list, name='qualificadors_datatable_list'),
    re_path(r'^datatableautors/list$', views.autors_datatable_list, name='autors_datatable_list'),
    re_path(r'^datatablepaisos/list$', views.paisos_datatable_list, name='paisos_datatable_list'),
    re_path(r'^datatableorganizations/list$', views.organizations_datatable_list, name='organizations_datatable_list'),
    re_path(r'^datatableprotocols/list$', views.protocol_datatable_list, name='protocol_datatable_list'),
    re_path(r'^datatableparaulesclau/list$', views.paraulaclau_datatable_list, name='paraulaclau_datatable_list'),
    re_path(r'^datatabletipusrecurs/list$', views.tipusrecurs_datatable_list, name='tipusrecurs_datatable_list'),
    re_path(r'^datatablesuport/list$', views.suport_datatable_list, name='suport_datatable_list'),
    re_path(r'^datatabletipustoponim/list$', views.tipustoponim_datatable_list, name='tipustoponim_datatable_list'),
    re_path(r'^datatabletipusunitats/list$', views.tipusunitats_datatable_list, name='tipusunitats_datatable_list'),

    re_path(r'^filtres/check$', views.check_filtre, name='check_filtre'),
    re_path(r'^wmsmetadata/$', views.wmsmetadata, name='wmsmetadata'),
    re_path(r'^wmslocal/create/$', views.wmslocal_create, name='wmslocal_create'),
    re_path(r'^wmslocal/delete/$', views.wmslocal_delete, name='wmslocal_delete_noparam'),
    re_path(r'^wmslocal/delete/(?P<id>[0-9A-Za-z_\-]+)/$', views.wmslocal_delete, name='wmslocal_delete'),
    re_path(r'^prefsvisualitzaciowms/$', views.prefsvisualitzaciowms, name='prefsvisualitzaciowms'),
    re_path(r'^prefsvisualitzaciowms/toggle/$', views.toggle_prefs_wms, name='toggle_prefs_wms'),
    re_path(r'^georef_layers/$', views.georef_layers, name='georef_layers'),
    re_path(r'^help/$', views.help, name='help'),
    re_path(r'^help/delete/(?P<iddoc>[0-9A-Za-z_\-]+)/$', views.help_delete, name='help_delete'),
    re_path(r'^create_menu_link/', views.create_menu_link, name='create_menu_link'),
    re_path(r'^save_menu_links/', views.save_menu_links, name='save_menu_links'),

    re_path(r'^toponims$', views.toponims, name='toponims'),
    re_path(r'^toponims/update/(?P<id>[0-9A-Za-z_\-]+)/$', views.toponims_update, name='toponims_update'),
    re_path(r'^toponims/update/(?P<idtoponim>[0-9A-Za-z_\-]+)/(?P<idversio>[0-9A-Za-z_\-]+)/$', views.toponims_update_2, name='toponims_update_2'),
    re_path(r'^toponims/create/$', views.toponims_create, name='toponims_create'),
    re_path(r'^toponims/search/$', views.toponims_search, name='toponims_search'),
    re_path(r'^toponims/list/pdf/$', views.toponims_list_pdf, name='toponims_list_pdf'),
    re_path(r'^toponims/detail/pdf/(?P<idtoponim>[0-9A-Za-z_\-]+)/$', views.toponims_detail_pdf, name='toponims_detail_pdf'),
    re_path(r'^toponims/list/csv/$', views.toponims_list_csv, name='toponims_list_csv'),
    re_path(r'^toponims/list/xls/$', views.toponims_list_xls, name='toponims_list_xls'),
    re_path(r'^toponims/import/$', views.toponims_import, name='toponims_import'),

    re_path(r'^recursos$', views.recursos, name='recursos'),
    re_path(r'^recursos/create/$', views.recursos_create, name='recursos_create'),
    re_path(r'^recursos/update/(?P<id>[0-9A-Za-z_\-]+)/$', views.recursos_update, name='recursos_update'),
    re_path(r'^recursos/capeswms/$', views.recursos_capeswms, name='recursos_capeswms'),
    re_path(r'^recursos/list/xls/$', views.recursos_list_xls, name='recursos_list_xls'),
    re_path(r'^recursos/list/csv/$', views.recursos_list_csv, name='recursos_list_csv'),
    re_path(r'^recursos/list/pdf/$', views.recursos_list_pdf, name='recursos_list_pdf'),
    re_path(r'^recursos/sistrefassociat/$', views.sistrefassociat, name='sistrefassociat'),

    re_path(r'^thesaurus/authors/$', views.t_authors, name='t_authors'),
    re_path(r'^thesaurus/organizations/$', views.t_organizations, name='t_organizations'),
    re_path(r'^thesaurus/qualificadors/$', views.t_qualificadors, name='t_qualificadors'),
    re_path(r'^thesaurus/paisos/$', views.t_paisos, name='t_paisos'),
    re_path(r'^thesaurus/protocols/$', views.t_protocols, name='t_protocols'),
    re_path(r'^thesaurus/paraulesclau/$', views.t_paraulesclau, name='t_paraulesclau'),
    re_path(r'^thesaurus/tipusrecurs/$', views.t_tipuscontingut, name='t_tipuscontingut'),
    re_path(r'^thesaurus/tipussuport/$', views.t_tipussuport, name='t_tipussuport'),
    re_path(r'^thesaurus/tipustoponim/$', views.t_tipustoponim, name='t_tipustoponim'),
    re_path(r'^thesaurus/tipusunitats/$', views.t_tipusunitats, name='t_tipusunitats'),
    re_path(r'^thesaurus/checkdelete/$', views.t_checkdelete, name='t_checkdelete'),
    re_path(r'^thesaurus/description/edit/(?P<id>[0-9]+)/$', views.t_description_edit, name='t_description_edit'),
    re_path(r'^thesaurus/description/new/$', views.t_description_new, name='t_description_new'),

    re_path(r'^users/list/$', views.users_list, name='users_list'),

    re_path(r'^geojson_site_geom/$', views.geojson_site_geom, name='geojson_site_geom'),
    re_path(r'^copy_version$', views.copy_version, name='copy_version'),
    re_path(r'^graphs$', views.graphs, name='graphs'),
    re_path(r'^check_site_name/$', views.check_site_name, name='check_site_name'),
    re_path(r'^toponimstree$', views.toponimstree, name='toponimstree'),
    re_path(r'^toponim_node_search$', views.toponim_node_search, name='toponimnodesearch'),
    re_path(r'^calculcentroides', views.calculcentroides, name='calculcentroides'),
    re_path(r'^computecentroid/(?P<file_name>[\w.]{0,256})$', views.compute_shapefile_centroid, name='compute_shapefile_centroid'),
    re_path(r'^computecentroid/$', views.compute_shapefile_centroid, name='compute_shapefile_centroid_noparams'),
    re_path(r'^compute_centroid', views.compute_centroid, name='compute_centroid'),
    re_path(r'^importtoponims/(?P<file_name>[\w.]{0,256})$', views.import_toponims, name='import_toponims'),
    re_path(r'^importtoponims/$', views.import_toponims, name='import_toponims'),
    #re_path(r'^toponimstree/(?P<node_id>[\w\-]+)/$', views.toponimstreenode, name='toponimstreenode'),
    re_path(r'^toponimstree/$', views.toponimstreenode, name='toponimstreenode'),
    re_path(r'^statedata/$', views.statedata, name='statedata'),
    re_path(r'^toponimfilters$', views.toponimfilters, name='toponimfilters'),
    re_path(r'^recursfilters$', views.recursfilters, name='recursfilters'),
    re_path(r'^menu_edit$', views.menu_edit, name='menu_edit'),
    re_path(r'^user/my_profile/$', views.my_profile, name='my_profile'),
    re_path(r'^user/profile/$', views.user_profile, name='user_profile'),
    re_path(r'^user/profile/(?P<user_id>[0-9A-Za-z_\-]+)/$', views.user_profile, name='user_profile'),
    re_path(r'^user/new/$', views.user_new, name='user_new'),
    re_path(r'^user/block_user/$', views.block_user, name='block_user'),
    re_path(r'^switch_user_language/$', views.switch_user_language, name='switch_user_language'),
    re_path(r'^user/password/change_mine$', views.change_my_password, name='change_my_password'),
    re_path(r'^user/password/change$', views.change_password, name='change_password'),
    re_path(r'^user/password/change/(?P<user_id>[0-9A-Za-z_\-]+)/$', views.change_password, name='change_password'),
    re_path(r'ajax-upload$', views.import_uploader, name='ajax_upload'),
    re_path(r'ajax-process-shapefile$', views.process_shapefile, name='process_shapefile'),
    re_path(r'^jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
    re_path(r'^about/', views.about, name='about'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
