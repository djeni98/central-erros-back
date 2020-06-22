from django.shortcuts import get_object_or_404
from django.contrib.auth import hashers
from django.contrib.auth.password_validation import validate_password

from rest_framework import status, viewsets
from rest_framework.response import Response

from api.models import User, Event
from api.serializers import UserModelSerializer, EventModelSerializer


class UserAPIViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer
    fields = 'id', 'name', 'email', 'last_login'

    def list(self, request):
        users = User.objects.values(*self.fields)
        return Response(users)

    def create(self, request):
        user = request.data.dict()
        last_login = request.data.get('last_login')
        user['last_login'] = last_login if last_login else None

        password = request.data.get('password', '')
        validate_password(password)
        user['password'] = hashers.make_password(password)

        serializer = UserModelSerializer(data=user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserModelSerializer(user)
        result = serializer.data
        del result['password']

        return Response(result)


class EventAPIViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventModelSerializer
