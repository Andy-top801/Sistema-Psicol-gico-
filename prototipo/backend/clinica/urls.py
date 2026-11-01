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
    IAPreconsultaViewSet,
    ChatbotViewSet,
    ClasificacionIAViewSet,
    ClasificarIntakeView,
    AlertasCrisisView,
    SugerenciaMatchingViewSet,
    GenerarMatchingView,
    AsignarPsicologoHITLView,
    RegistroAnimoViewSet
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
router.register(r'consentimientos-plantillas', ConsentimientoInformadoViewSet, basename='consentimiento-plantillas')
router.register(r'firmas-consentimiento', FirmaConsentimientoViewSet, basename='firma-consentimiento')
router.register(r'consentimientos-firmas', FirmaConsentimientoViewSet, basename='consentimientos-firmas')
router.register(r'derivaciones', DerivacionCasoViewSet, basename='derivacion-caso')
router.register(r'ia/preconsulta', IAPreconsultaViewSet, basename='ia-preconsulta')
router.register(r'chatbot', ChatbotViewSet, basename='chatbot')

# Rutas Incremento Sprint 3
router.register(r'clasificacion-ia', ClasificacionIAViewSet, basename='clasificacion-ia')
router.register(r'sugerencias-matching', SugerenciaMatchingViewSet, basename='sugerencias-matching')
router.register(r'registro-animo', RegistroAnimoViewSet, basename='registro-animo')

urlpatterns = [
    path('triaje/alertas/', AlertasCrisisView.as_view(), name='triaje-alertas'),
    path('triaje/<uuid:paciente_id>/sugerir-matching/', GenerarMatchingView.as_view(), name='triaje-sugerir-matching'),
    path('triaje/asignar/', AsignarPsicologoHITLView.as_view(), name='triaje-asignar'),
    path('intake/respuestas/', RespuestaPreConsultaViewSet.as_view({'post': 'create', 'get': 'list'}), name='intake-respuestas'),
    path('intake/<uuid:pk>/clasificar/', ClasificarIntakeView.as_view(), name='intake-clasificar'),
    path('ia/sugerir-psicologo/<uuid:paciente_id>/', GenerarMatchingView.as_view(), name='ia-sugerir-psicologo'),
    path('ia/confirmar-asignacion/', AsignarPsicologoHITLView.as_view(), name='ia-confirmar-asignacion'),
    path('ia/asignacion-manual/', AsignarPsicologoHITLView.as_view(), name='ia-asignacion-manual'),
    path('', include(router.urls)),
]
