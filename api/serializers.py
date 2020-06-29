from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from api.models import User, Event, Agent


class UserModelSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['created_at', 'last_login']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if 'password' in rep:
            del rep['password']
        return rep

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        if validated_data['password']:
            instance.set_password(validated_data['password'])
            instance.save()
        return instance


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
