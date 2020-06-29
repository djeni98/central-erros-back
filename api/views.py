from rest_framework import viewsets

from api.models import User, Event, Agent
from api.serializers import (
    UserModelSerializer, EventModelSerializer, AgentModelSerializer
)

class UserAPIViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer


class EventAPIViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventModelSerializer


class AgentAPIViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentModelSerializer
