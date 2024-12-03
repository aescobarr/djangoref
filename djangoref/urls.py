from django.conf import settings
from django.conf.urls.static import static
"""djangoref URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, re_path
from django.contrib import admin
from georef import views
#from django.contrib.auth.views import login,logout
#from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    re_path('^', include('django.contrib.auth.urls')),
    re_path('^', include('georef.urls')),
    #url(r'^georef/', include('georef.urls')),
    #url(r'^accounts/login/$', login, name='login'),
    #url(r'^logout/$', logout, {'next_page': '/accounts/login'}, name='logout'),
    re_path(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
