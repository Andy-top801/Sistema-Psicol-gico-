from django.urls import path, include
from rest_framework.routers import DefaultRouter
from clinica.views import (
    EspecialidadViewSet,
    PsicologoViewSet,
    DisponibilidadViewSet,
    PacienteViewSet
)

router = DefaultRouter()
router.register(r'especialidades', EspecialidadViewSet, basename='especialidad')
router.register(r'psicologos', PsicologoViewSet, basename='psicologo')
router.register(r'disponibilidad', DisponibilidadViewSet, basename='disponibilidad')
router.register(r'pacientes', PacienteViewSet, basename='paciente')

urlpatterns = [
    path('', include(router.urls)),
]
