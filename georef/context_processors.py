from django.conf import settings

def revision_number_processor(request):
    return {'revision': settings.JAVASCRIPT_VERSION}

def version_number_processor(request):
    version_string = '.'.join((settings.MAJOR, settings.MINOR, settings.PATCH))
    return {'version': version_string}

def custom_util_links_processor(request):
    return { 'custom_tool_links': settings.CUSTOM_TOOL_LINKS }
