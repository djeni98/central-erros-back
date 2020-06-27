from django.shortcuts import get_object_or_404
from django.contrib.auth import hashers
from django.contrib.auth.password_validation import validate_password

from rest_framework import status, viewsets
from rest_framework.response import Response

from api.models import User, Event, Agent
from api.serializers import (
    UserModelSerializer, EventModelSerializer, AgentModelSerializer
)

class UserAPIViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer

    def create_password(self, password):
        validate_password(password)
        return hashers.make_password(password)

    def create(self, request):
        user = request.data.dict()
        user['last_login'] = None
        user['password'] = self.create_password(user.get('password'))

        serializer = UserModelSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # https://github.com/encode/django-rest-framework/.../mixins.py#L59
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.data

        password = user.get('password')
        if password:
            user['password'] = self.create_password(password)

        serializer = UserModelSerializer(
            instance, data=user, partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class EventAPIViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventModelSerializer

class AgentAPIViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentModelSerializer
