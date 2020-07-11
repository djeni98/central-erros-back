from rest_framework import viewsets, generics

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# I had to override rest_framework.permissions.DjangoModelPermissions
# to apply view permissions
from api.auth import DjangoModelPermissions

from logs.models import Permission, Group, User, Event, Agent

from api.serializers import (
    PermissionModelSerializer, GroupModelSerializer,
    UserModelSerializer, EventModelSerializer, AgentModelSerializer
)
from api.serializers import UserCreateSerializer as RegisterSerializer


class PermissionAPIViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    authentication_classes = [JWTAuthentication]

    queryset = Permission.objects.all()
    serializer_class = PermissionModelSerializer


class GroupAPIViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    authentication_classes = [JWTAuthentication]

    queryset = Group.objects.all()
    serializer_class = GroupModelSerializer


class UserAPIViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    authentication_classes = [JWTAuthentication]

    queryset = User.objects.all()
    serializer_class = UserModelSerializer


class EventAPIViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    authentication_classes = [JWTAuthentication]

    queryset = Event.objects.all()
    serializer_class = EventModelSerializer


class AgentAPIViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    authentication_classes = [JWTAuthentication]

    queryset = Agent.objects.all()
    serializer_class = AgentModelSerializer


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

register = RegisterAPIView.as_view()
