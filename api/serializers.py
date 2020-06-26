from django.contrib.auth import password_validation

from rest_framework import serializers

from api.models import User, Event


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'created_at', 'last_login', 'password']
        read_only_fields = ['created_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if 'password' in rep:
            del rep['password']
        return rep


class EventModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'level', 'description', 'source',
            'datetime', 'details', 'user', 'archived'
        ]
