from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CentroViewSet

router = DefaultRouter()
router.register(r'', CentroViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
