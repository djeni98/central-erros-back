from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from logs.models import Permission, Group, User, Event, Agent

class PermissionModelSerializer(serializers.ModelSerializer):
    permission = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        exclude = ['content_type']

    def get_permission(self, obj):
        return f'{obj.content_type.app_labeled_name} | {obj.name}'


class GroupModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if 'password' in rep:
            del rep['password']
        return rep

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class UserModelSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['last_login']

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        user_permissions = validated_data.pop('user_permissions', [])

        user = User.objects.create(**validated_data)
        user.set_password(validated_data.get('password'))

        user.groups.set(groups)
        user.user_permissions.set(user_permissions)
        user.save()
        return user

    def update(self, instance, validated_data):
        for item in ('groups', 'user_permissions'):
            value = validated_data.pop(item, None)
            if value:
                getattr(instance, item).set(value)

        if validated_data.get('password'):
            instance.set_password(validated_data.pop('password'))

        for key, value in validated_data.items():
            setattr(instance, key, value)


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


class RecoverFormSerializer(serializers.Serializer):
    email = serializers.EmailField()
    link = serializers.CharField(required=False)


class ResetPasswordFormSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150, validators=[UnicodeUsernameValidator()]
    )
    password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
