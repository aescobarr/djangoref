import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoref.settings')
django.setup()

from django.contrib.auth.management.commands.createsuperuser import get_user_model
from django.contrib.auth.models import User
from georef_addenda.models import Profile
from georef_addenda.models import Organization
from georef.models import Toponim

admin_user=os.environ.get("DJANGO_ADMIN_USER", "")
admin_email=os.environ.get("DJANGO_ADMIN_EMAIL", "")
admin_password=os.environ.get("DJANGO_ADMIN_PASSWORD", "")

regular_user=os.environ.get("DJANGO_REGULAR_USER", "")
regular_email=os.environ.get("DJANGO_REGULAR_EMAIL", "")
regular_password=os.environ.get("DJANGO_REGULAR_PASSWORD", "")

if admin_user != "" and admin_email != "" and admin_password != "" and not User.objects.filter(username=admin_user).exists():
    current_user = get_user_model()._default_manager.db_manager('default').create_superuser( 
        username=admin_user, 
        email=admin_email,
        password=admin_password
    )
    current_user.profile.organization = Organization.objects.get(pk=1)
    current_user.profile.toponim_permission = '1'
    current_user.profile.permission_recurs_edition = True
    current_user.profile.permission_toponim_edition = True
    current_user.profile.permission_tesaure_edition = True
    current_user.profile.permission_administrative = True
    current_user.profile.permission_filter_edition = True
    current_user.profile.save()

if regular_user != "" and regular_email != "" and regular_password != "" and not User.objects.filter(username=regular_user).exists():
    current_user = User.objects.create_user(username=regular_user, email=regular_email, password=regular_password)
    current_user.profile.organization = Organization.objects.get(pk=1)
    current_user.profile.toponim_permission = '1'
    current_user.profile.permission_recurs_edition = True
    current_user.profile.permission_toponim_edition = True
    current_user.profile.permission_tesaure_edition = True
    current_user.profile.permission_administrative = False
    current_user.profile.permission_filter_edition = True
    current_user.profile.save()

t = Toponim.objects.get(pk='0')
t.idorganization=Organization.objects.get(pk=1)
t.save()
