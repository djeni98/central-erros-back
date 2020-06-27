from django.contrib.auth import password_validation

from rest_framework import serializers
from rest_framework.fields import Field

from api.models import User, Event, Agent


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['created_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if 'password' in rep:
            del rep['password']
        return rep

class AgentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'


class EventModelSerializer(serializers.ModelSerializer):
    source = serializers.CharField(read_only=True)
    collected_by = serializers.CharField(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
