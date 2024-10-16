from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
from georef import views
from django.conf import settings

from . import views
from django.views.i18n import JavaScriptCatalog

router = routers.DefaultRouter()
router.register(r'toponims', views.ToponimViewSet, base_name='toponims')
router.register(r'toponimsearch', views.ToponimSearchViewSet, base_name='toponimsearch')
router.register(r'toponimparesearch', views.ToponimPareSearchViewSet, base_name='toponimparesearch')
router.register(r'filtres', views.FiltrejsonViewSet, base_name='filtres')
router.register(r'recursgeoref', views.RecursGeoRefViewSet, base_name='recursgeoref')
router.register(r'versions', views.ToponimVersioViewSet, base_name='versions')
router.register(r'users', views.UsersViewSet, base_name='users')
router.register(r'paraulesclau', views.ParaulaClauViewSet, base_name='paraulesclau')
router.register(r'autors', views.AutorViewSet, base_name='autors')
router.register(r'qualificadorsversio', views.QualificadorViewSet, base_name='qualificadorsversio')
router.register(r'organizations', views.OrganizationViewSet, base_name='organizations')
router.register(r'tipusrecurs', views.TipusrecursgeorefViewSet, base_name='tipusrecurs')
router.register(r'tipussuport', views.TipusSuportViewSet, base_name='tipussuport')
router.register(r'tipustoponim', views.TipusToponimViewSet, base_name='tipustoponim')
router.register(r'tipusunitats', views.TipusUnitatsViewSet, base_name='tipusunitats')
router.register(r'sistemareferenciamm', views.SistemaReferenciammViewSet, base_name='sistemareferenciamm')
router.register(r'paisos', views.PaisViewSet, base_name='paisos')
router.register(r'menuitems', views.MenuItemViewSet, base_name='menuitems')

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^Zoologia/', views.index, name='index'),

    url(r'^api_internal/',include(router.urls)),

    url(r'^datatabletoponims/list$', views.toponims_datatable_list, name='toponims_datatable_list'),
    url(r'^datatablerecursos/list$', views.recursos_datatable_list, name='recursos_datatable_list'),
    url(r'^datatableusers/list$', views.users_datatable_list, name='users_datatable_list'),
    url(r'^datatabletoponimfilters/list$', views.filters_datatable_list, name='toponimfilters_datatable_list'),
    url(r'^datatablerecursfilters/list$', views.filters_datatable_list, name='recursfilters_datatable_list'),
    url(r'^datatablecapeswmslocals/list$', views.capeswmslocals_datatable_list, name='capeswmslocals_datatable_list'),
    url(r'^datatablequalificadors/list$', views.qualificadors_datatable_list, name='qualificadors_datatable_list'),
    url(r'^datatableautors/list$', views.autors_datatable_list, name='autors_datatable_list'),
    url(r'^datatablepaisos/list$', views.paisos_datatable_list, name='paisos_datatable_list'),
    url(r'^datatableorganizations/list$', views.organizations_datatable_list, name='organizations_datatable_list'),
    url(r'^datatableparaulesclau/list$', views.paraulaclau_datatable_list, name='paraulaclau_datatable_list'),
    url(r'^datatabletipusrecurs/list$', views.tipusrecurs_datatable_list, name='tipusrecurs_datatable_list'),
    url(r'^datatablesuport/list$', views.suport_datatable_list, name='suport_datatable_list'),
    url(r'^datatabletipustoponim/list$', views.tipustoponim_datatable_list, name='tipustoponim_datatable_list'),
    url(r'^datatabletipusunitats/list$', views.tipusunitats_datatable_list, name='tipusunitats_datatable_list'),

    url(r'^filtres/check$', views.check_filtre, name='check_filtre'),
    url(r'^wmsmetadata/$', views.wmsmetadata, name='wmsmetadata'),
    url(r'^wmslocal/create/$', views.wmslocal_create, name='wmslocal_create'),
    url(r'^wmslocal/delete/$', views.wmslocal_delete, name='wmslocal_delete_noparam'),
    url(r'^wmslocal/delete/(?P<id>[0-9A-Za-z_\-]+)/$', views.wmslocal_delete, name='wmslocal_delete'),
    url(r'^prefsvisualitzaciowms/$', views.prefsvisualitzaciowms, name='prefsvisualitzaciowms'),
    url(r'^prefsvisualitzaciowms/toggle/$', views.toggle_prefs_wms, name='toggle_prefs_wms'),
    url(r'^georef_layers/$', views.georef_layers, name='georef_layers'),
    url(r'^help/$', views.help, name='help'),
    url(r'^help/delete/(?P<iddoc>[0-9A-Za-z_\-]+)/$', views.help_delete, name='help_delete'),
    url(r'^create_menu_link/', views.create_menu_link, name='create_menu_link'),
    url(r'^save_menu_links/', views.save_menu_links, name='save_menu_links'),

    url(r'^toponims$', views.toponims, name='toponims'),
    url(r'^toponims/update/(?P<id>[0-9A-Za-z_\-]+)/$', views.toponims_update, name='toponims_update'),
    url(r'^toponims/update/(?P<idtoponim>[0-9A-Za-z_\-]+)/(?P<idversio>[0-9A-Za-z_\-]+)/$', views.toponims_update_2, name='toponims_update_2'),
    url(r'^toponims/create/$', views.toponims_create, name='toponims_create'),
    url(r'^toponims/search/$', views.toponims_search, name='toponims_search'),
    url(r'^toponims/list/pdf/$', views.toponims_list_pdf, name='toponims_list_pdf'),
    url(r'^toponims/detail/pdf/(?P<idtoponim>[0-9A-Za-z_\-]+)/$', views.toponims_detail_pdf, name='toponims_detail_pdf'),
    url(r'^toponims/list/csv/$', views.toponims_list_csv, name='toponims_list_csv'),
    url(r'^toponims/list/xls/$', views.toponims_list_xls, name='toponims_list_xls'),
    url(r'^toponims/import/$', views.toponims_import, name='toponims_import'),

    url(r'^recursos$', views.recursos, name='recursos'),
    url(r'^recursos/create/$', views.recursos_create, name='recursos_create'),
    url(r'^recursos/update/(?P<id>[0-9A-Za-z_\-]+)/$', views.recursos_update, name='recursos_update'),
    url(r'^recursos/capeswms/$', views.recursos_capeswms, name='recursos_capeswms'),
    url(r'^recursos/list/xls/$', views.recursos_list_xls, name='recursos_list_xls'),
    url(r'^recursos/list/csv/$', views.recursos_list_csv, name='recursos_list_csv'),
    url(r'^recursos/list/pdf/$', views.recursos_list_pdf, name='recursos_list_pdf'),
    url(r'^recursos/sistrefassociat/$', views.sistrefassociat, name='sistrefassociat'),

    url(r'^thesaurus/authors/$', views.t_authors, name='t_authors'),
    url(r'^thesaurus/organizations/$', views.t_organizations, name='t_organizations'),
    url(r'^thesaurus/qualificadors/$', views.t_qualificadors, name='t_qualificadors'),
    url(r'^thesaurus/paisos/$', views.t_paisos, name='t_paisos'),
    url(r'^thesaurus/paraulesclau/$', views.t_paraulesclau, name='t_paraulesclau'),
    url(r'^thesaurus/tipusrecurs/$', views.t_tipuscontingut, name='t_tipuscontingut'),
    url(r'^thesaurus/tipussuport/$', views.t_tipussuport, name='t_tipussuport'),
    url(r'^thesaurus/tipustoponim/$', views.t_tipustoponim, name='t_tipustoponim'),
    url(r'^thesaurus/tipusunitats/$', views.t_tipusunitats, name='t_tipusunitats'),
    url(r'^thesaurus/checkdelete/$', views.t_checkdelete, name='t_checkdelete'),
    url(r'^thesaurus/description/edit/(?P<id>[0-9]+)/$', views.t_description_edit, name='t_description_edit'),
    url(r'^thesaurus/description/new/$', views.t_description_new, name='t_description_new'),

    url(r'^users/list/$', views.users_list, name='users_list'),

    url(r'^graphs$', views.graphs, name='graphs'),
    url(r'^check_site_name/$', views.check_site_name, name='check_site_name'),
    url(r'^toponimstree$', views.toponimstree, name='toponimstree'),
    url(r'^toponim_node_search$', views.toponim_node_search, name='toponimnodesearch'),
    url(r'^calculcentroides', views.calculcentroides, name='calculcentroides'),
    url(r'^computecentroid/(?P<file_name>[\w.]{0,256})$', views.compute_shapefile_centroid, name='compute_shapefile_centroid'),
    url(r'^computecentroid/$', views.compute_shapefile_centroid, name='compute_shapefile_centroid_noparams'),
    url(r'^compute_centroid', views.compute_centroid, name='compute_centroid'),
    url(r'^importtoponims/(?P<file_name>[\w.]{0,256})$', views.import_toponims, name='import_toponims'),
    url(r'^importtoponims/$', views.import_toponims, name='import_toponims'),
    #url(r'^toponimstree/(?P<node_id>[\w\-]+)/$', views.toponimstreenode, name='toponimstreenode'),
    url(r'^toponimstree/$', views.toponimstreenode, name='toponimstreenode'),
    url(r'^statedata/$', views.statedata, name='statedata'),
    url(r'^toponimfilters$', views.toponimfilters, name='toponimfilters'),
    url(r'^recursfilters$', views.recursfilters, name='recursfilters'),
    url(r'^menu_edit$', views.menu_edit, name='menu_edit'),
    url(r'^user/my_profile/$', views.my_profile, name='my_profile'),
    url(r'^user/profile/$', views.user_profile, name='user_profile'),
    url(r'^user/profile/(?P<user_id>[0-9A-Za-z_\-]+)/$', views.user_profile, name='user_profile'),
    url(r'^user/new/$', views.user_new, name='user_new'),
    url(r'^user/block_user/$', views.block_user, name='block_user'),
    url(r'^switch_user_language/$', views.switch_user_language, name='switch_user_language'),
    url(r'^user/password/change_mine$', views.change_my_password, name='change_my_password'),
    url(r'^user/password/change$', views.change_password, name='change_password'),
    url(r'^user/password/change/(?P<user_id>[0-9A-Za-z_\-]+)/$', views.change_password, name='change_password'),
    url(r'ajax-upload$', views.import_uploader, name='ajax_upload'),
    url(r'ajax-process-shapefile$', views.process_shapefile, name='process_shapefile'),
    url(r'^jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^about/', views.about, name='about'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
