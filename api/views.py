from rest_framework import viewsets, generics

from rest_framework.response import Response
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)

from rest_framework.reverse import reverse

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import EventFilterClass, EventSearchFilter

# I had to override DjangoModelPermissions to apply view permissions
from api.permissions import DjangoModelPermissions, TokenUserMatchesUsername

from api.auth import JWTAuthByQueryParams

from logs.models import Permission, Group, User, Event, Agent

from api.serializers import (
    PermissionModelSerializer, GroupModelSerializer,
    UserModelSerializer, EventModelSerializer, AgentModelSerializer,
    UserCreateSerializer as RegisterSerializer,
    RecoverFormSerializer, ResetPasswordFormSerializer
)

from api.email_templates import subject, message, html_message


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

    filter_backends = [SearchFilter]
    search_fields = ['name']


class UserAPIViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    authentication_classes = [JWTAuthentication]

    queryset = User.objects.all()
    serializer_class = UserModelSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_superuser', 'is_staff', 'is_active']
    search_fields = ['username', 'email']


class EventAPIViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    authentication_classes = [JWTAuthentication]

    queryset = Event.objects.all()
    serializer_class = EventModelSerializer

    filter_backends = [
        DjangoFilterBackend,
        EventSearchFilter,
        OrderingFilter
    ]
    filterset_class = EventFilterClass
    search_fields = ['level', 'description', 'source']
    ordering_fields = ['level', 'datetime']
    ordering = ['-datetime']


class AgentAPIViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    authentication_classes = [JWTAuthentication]

    queryset = Agent.objects.all()
    serializer_class = AgentModelSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'environment']
    search_fields = ['name', 'environment']


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


register = RegisterAPIView.as_view()


@api_view(['POST'])
def request_recover(request):
    email = request.data.get('email', '')
    base_link = request.data.get(
        'link', reverse('reset-password', request=request)
    )

    serializer = RecoverFormSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    unit_time = '1 dia'

    try:
        user = User.objects.get(email=email)
        token = AccessToken.for_user(user)

        link = base_link + '?token=' + str(token)
        format_message = {
            'email': email, 'link': link, 'unit_time': unit_time
        }
        user.email_user(
            subject,
            message.format(**format_message),
            html_message=html_message.format(**format_message)
        )
    except User.DoesNotExist:
        pass

    return Response({'detail': 'Email will be sent if it is a valid user.'})


@api_view(['POST'])
@authentication_classes([JWTAuthentication, JWTAuthByQueryParams])
@permission_classes([TokenUserMatchesUsername])
def reset_password(request):
    serializer = ResetPasswordFormSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.data.get('username')
    password = serializer.data.get('password')

    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()

    return Response({'detail': 'Your password has been changed.'})
