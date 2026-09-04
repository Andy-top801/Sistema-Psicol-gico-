from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tenants.views import TenantViewSet

router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenants')

urlpatterns = [
    path('', include(router.urls)),
]
