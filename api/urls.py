from django.urls import include, path

from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserAPIViewSet)
router.register(r'events', views.EventAPIViewSet)
router.register(r'agents', views.AgentAPIViewSet)

urlpatterns = [
    path('', include(router.urls))
]
