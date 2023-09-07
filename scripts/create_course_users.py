import os, sys

proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoref.settings")
sys.path.append(proj_path)

os.chdir(proj_path)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from django.contrib.auth.models import User
from georef_addenda.models import Profile, Organization


def main(n=10, reset=True):
    #user = User.objects.create_user(username="",email="",password="")
    org = Organization.objects.get(pk=1)
    if reset:
        for i in range(1, n + 1):
            nom_usuari = "curs_{0}".format(str(i))
            try:
                usr = User.objects.get(username=nom_usuari)
                usr.delete()
                print("Deleted user {0}".format(nom_usuari))
            except User.DoesNotExist:
                pass
    for i in range(1, n+1):
        nom_usuari = "curs_{0}".format( str(i) )
        email = nom_usuari + "@example.com"
        password = nom_usuari
        print("{0} {1} {2}".format( nom_usuari, email, password ))
        user = User.objects.create_user(username=nom_usuari, email=email, password=password, first_name=nom_usuari)
        user.profile.permission_filter_edition = True
        user.profile.permission_tesaure_edition = True
        user.profile.permission_recurs_edition = True
        user.profile.permission_toponim_edition = True
        user.profile.toponim_permission = '1'
        user.profile.organization = org
        user.profile.save()
        print("Created user {0}".format(nom_usuari))


if __name__ == '__main__':
    args = sys.argv[1:]
    n_args = len(args)
    if n_args != 2:
        print("Invalid n of arguments, passed {0}, required 2".format(n_args))
        sys.exit(2)
    else:
        print("{0} arguments".format(n_args))
        reset_users = False
        if args[0] == "1":
            reset_users = True
        n_users = int(args[1])
        main(n_users,reset_users)
        sys.exit(2)
