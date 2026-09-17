from django.urls import path, include
from rest_framework.routers import DefaultRouter
from clinica.views import (
    EspecialidadViewSet,
    PsicologoViewSet,
    DisponibilidadViewSet,
    PacienteViewSet,
    FormularioPreConsultaViewSet,
    RespuestaPreConsultaViewSet,
    CIE10ViewSet,
    HistoriaClinicaViewSet,
    DiagnosticoCIEViewSet,
    NotaSesionViewSet,
    EvolucionClinicaViewSet,
    TareaTerapeuticaViewSet,
    EvidenciaTareaViewSet,
    ConsentimientoInformadoViewSet,
    FirmaConsentimientoViewSet,
    DerivacionCasoViewSet,
    IAPreconsultaViewSet
)

router = DefaultRouter()
router.register(r'especialidades', EspecialidadViewSet, basename='especialidad')
router.register(r'psicologos', PsicologoViewSet, basename='psicologo')
router.register(r'disponibilidad', DisponibilidadViewSet, basename='disponibilidad')
router.register(r'pacientes', PacienteViewSet, basename='paciente')

# Rutas Incremento Sprint 2
router.register(r'formularios-preconsulta', FormularioPreConsultaViewSet, basename='formulario-preconsulta')
router.register(r'respuestas-preconsulta', RespuestaPreConsultaViewSet, basename='respuesta-preconsulta')
router.register(r'cie10', CIE10ViewSet, basename='cie10')
router.register(r'historias-clinicas', HistoriaClinicaViewSet, basename='historia-clinica')
router.register(r'diagnosticos-cie', DiagnosticoCIEViewSet, basename='diagnostico-cie')
router.register(r'notas-sesion', NotaSesionViewSet, basename='nota-sesion')
router.register(r'evoluciones', EvolucionClinicaViewSet, basename='evolucion-clinica')
router.register(r'tareas', TareaTerapeuticaViewSet, basename='tarea-terapeutica')
router.register(r'evidencias-tarea', EvidenciaTareaViewSet, basename='evidencia-tarea')
router.register(r'consentimientos', ConsentimientoInformadoViewSet, basename='consentimiento-informado')
router.register(r'firmas-consentimiento', FirmaConsentimientoViewSet, basename='firma-consentimiento')
router.register(r'derivaciones', DerivacionCasoViewSet, basename='derivacion-caso')
router.register(r'ia/preconsulta', IAPreconsultaViewSet, basename='ia-preconsulta')

urlpatterns = [
    path('', include(router.urls)),
]

