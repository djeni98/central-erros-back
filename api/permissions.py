from rest_framework import permissions


class DjangoModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self, *args, **kwargs):
        """Add 'view' permission in self.perms_map"""
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        super().__init__(*args, **kwargs)


class TokenUserMatchesUsername(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.username == request.data.get('username'))
