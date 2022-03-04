from rest_framework import permissions
from django.utils.translation import gettext_lazy as _


class HasAdministrativePermission(permissions.BasePermission):
    message = _('Edició d\'usuaris no permesa.')

    def has_permission(self, request, view):
        current_user = request.user
        return current_user.profile and current_user.profile.permission_administrative

