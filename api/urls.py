from django.urls import include, path

from rest_framework import routers

from rest_framework_simplejwt.views import token_refresh

from api import views
from api.auth import custom_token_obtain_pair

router = routers.DefaultRouter()
router.register(r'users', views.UserAPIViewSet)
router.register(r'events', views.EventAPIViewSet)
router.register(r'agents', views.AgentAPIViewSet)
router.register(r'groups', views.GroupAPIViewSet)
router.register(r'permissions', views.PermissionAPIViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', custom_token_obtain_pair),
    path('refresh/', token_refresh),
    path('register/', views.register, name='register')
]
