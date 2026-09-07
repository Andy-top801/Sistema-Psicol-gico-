from django.urls import path, include
from rest_framework.routers import DefaultRouter
from agenda.views import (
    CitaViewSet,
    TeleconsultaAccessView,
    TeleconsultaFinishView,
    DashboardKPIsView,
    AlertaViewSet
)

router = DefaultRouter()
router.register(r'citas', CitaViewSet, basename='cita')
router.register(r'alertas', AlertaViewSet, basename='alerta')

urlpatterns = [
    path('teleconsulta/<uuid:cita_id>/access/', TeleconsultaAccessView.as_view(), name='teleconsulta-access'),
    path('teleconsulta/<uuid:cita_id>/finish/', TeleconsultaFinishView.as_view(), name='teleconsulta-finish'),
    path('dashboard/kpis/', DashboardKPIsView.as_view(), name='dashboard-kpis'),
    path('', include(router.urls)),
]
