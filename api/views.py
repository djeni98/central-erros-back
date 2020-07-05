from rest_framework import viewsets

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from logs.models import User, Event, Agent
from api.serializers import (
    UserModelSerializer, EventModelSerializer, AgentModelSerializer
)

class UserAPIViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsAuthenticated]
    #authentication_classes = [JWTAuthentication]

    queryset = User.objects.all()
    serializer_class = UserModelSerializer


class EventAPIViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsAuthenticated]
    #authentication_classes = [JWTAuthentication]

    queryset = Event.objects.all()
    serializer_class = EventModelSerializer


class AgentAPIViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsAuthenticated]
    #authentication_classes = [JWTAuthentication]

    queryset = Agent.objects.all()
    serializer_class = AgentModelSerializer
