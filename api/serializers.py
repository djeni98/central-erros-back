from rest_framework import serializers
from api.models import User, Event


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'last_login', 'password']


class EventModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'level', 'description', 'source',
            'datetime', 'details', 'user', 'archived'
        ]
