from django.conf import settings
from georef_addenda.models import MenuItem

def revision_number_processor(request):
    if settings.DEBUG:
        return {'revision': ''}
    else:
        return {'revision': settings.JAVASCRIPT_VERSION}

def version_number_processor(request):
    version_string = '.'.join((settings.MAJOR, settings.MINOR, settings.PATCH))
    return {'version': version_string}

def custom_util_links_processor(request):
    lang = request.LANGUAGE_CODE
    menuitems = MenuItem.objects.filter(language=lang).order_by('order')
    return {'custom_tool_links': menuitems}
    #return { 'custom_tool_links': settings.CUSTOM_TOOL_LINKS }
