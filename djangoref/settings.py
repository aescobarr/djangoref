"""
Django settings for djangoref project.

Generated by 'django-admin startproject' using Django 1.11.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from django.utils.translation import gettext_lazy as _


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LANGUAGES = (
    ('ca', _('Catalan')),
    ('en', _('English')),
)

LOCALE_PATHS = (
   os.path.join(BASE_DIR, 'locale'),
)

# create language
# django-admin.py makemessages -l en
# django-admin.py makemessages -d djangojs -l en
# django-admin.py makemessages -l ca
# django-admin.py makemessages -d djangojs -l ca
# compile languages
# django-admin.py compilemessages

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# OVERRIDEN IN SETTINGS_LOCAL
SECRET_KEY = 'gx%(-$i!e@y9o-xa^=962t*f-ngn-!u+zf)m-$icedw8pzb@&s'

# SECURITY WARNING: don't run with debug turned on in production!
# OVERRIDEN IN SETTINGS_LOCAL
DEBUG = True

# OVERRIDEN IN SETTINGS_LOCAL
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    #'material',
    #'material.admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'bootstrap3',
    'georef',
    'georef_addenda',
    'djangobower',
    'ajaxuploader',
    'datetimewidget',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'georef.middleware.ForceDefaultLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djangoref.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'georef.context_processors.revision_number_processor',
                'georef.context_processors.version_number_processor',
                'georef.context_processors.custom_util_links_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangoref.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'ca'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# OVERRIDEN IN SETTINGS_LOCAL
STATIC_ROOT = '/home/webuser/dev/django/djangoref/static/'

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/'

LOGIN_URL = '/login'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
]

# ./manage.py bower install
BOWER_INSTALLED_APPS = (
    'jquery',
    'jquery-ui',
    'datatables.net',
    'datatables.net-dt',
    'popper.js',
    'bootstrap',
    'toastr',
    'jstree',
    'jquery-tagit',
)

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25
}

# OVERRIDEN IN SETTINGS_LOCAL
UPLOAD_DIR = BASE_DIR + "/uploads"
MEDIA_ROOT = UPLOAD_DIR
MEDIA_URL = "/media/"

from djangoref.settings_local import *

#5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

JAVASCRIPT_VERSION = 112

#Semver versioning - https://semver.org/
MAJOR="1"
MINOR="1"
PATCH="4"

# Links in utilities. Each element is "title","link"
# if title is blank, a separator is inserted
# CUSTOM_TOOL_LINKS = (
#     (_("Anar a google"), "https://www.google.es"),
#     (_("Anar a ICC"), "http://www.icgc.cat/"),
#     ("", ""),
#     (_("Conversió de coordenades - Convertbox"), "http://betaportal.icgc.cat/convertbox/#"),
#     (_("Conversió de coordenades - Earth Point: Convert coordinates"), "http://www.earthpoint.us/Convert.aspx"),
#     ("", ""),
#     (_("Georeferenciació - Geolocate"), "http://www.geo-locate.org/web/WebGeoref.aspx"),
#     (_("Georeferenciació - Georeferencing calculator"), "https://www.gbif.org/tool/81315/georeferencing-calculator"),
#     (_("Georeferenciació - Berkeley Mapper"), "http://berkeleymapper.berkeley.edu/#"),
# )
