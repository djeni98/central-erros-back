from rest_framework import permissions

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['email'] = user.email

        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


custom_token_obtain_pair = CustomTokenObtainPairView.as_view()


class DjangoModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self, *args, **kwargs):
        """Add 'view' permission in self.perms_map"""
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        super().__init__(*args, **kwargs)
