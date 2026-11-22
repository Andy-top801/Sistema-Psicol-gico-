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
    CTR_MatchingController,
    RegistroAnimoViewSet
)
from clinica.ia_longitudinal_views import (
    PacienteResumenIAListCreateView,
    ResumenIAAprobarHITLView,
    ResumenIAPDFView,
    AlertasRiesgoIAListView,
    AlertasRiesgoIAEvaluarView,
    AlertaRiesgoIATransicionView,
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
# CU22-paso 2: GET matching/sugerencias/ · CU22-paso 21: POST matching/{id}/aprobar/ ·
# CU22-paso 31: POST matching/{id}/rechazar_y_reasignar/
router.register(r'matching', CTR_MatchingController, basename='matching')
router.register(r'registro-animo', RegistroAnimoViewSet, basename='registro-animo')

urlpatterns = [
    path('triaje/alertas/', AlertasCrisisView.as_view(), name='triaje-alertas'),
    path('triaje/<uuid:paciente_id>/sugerir-matching/', GenerarMatchingView.as_view(), name='triaje-sugerir-matching'),
    path('triaje/asignar/', AsignarPsicologoHITLView.as_view(), name='triaje-asignar'),
    path('intake/respuestas/', RespuestaPreConsultaViewSet.as_view({'post': 'create', 'get': 'list'}), name='intake-respuestas'),
    path('intake/<uuid:pk>/clasificar/', ClasificarIntakeView.as_view(), name='intake-clasificar'),
    # CU21-paso 2: POST /api/v1/ia/clasificar-triaje/ (payload) → CTR_ClasificacionIAController
    path('ia/clasificar-triaje/', ClasificarIntakeView.as_view(), name='ia-clasificar-triaje'),
    path('ia/sugerir-psicologo/<uuid:paciente_id>/', GenerarMatchingView.as_view(), name='ia-sugerir-psicologo'),
    path('ia/confirmar-asignacion/', AsignarPsicologoHITLView.as_view(), name='ia-confirmar-asignacion'),
    path('ia/asignacion-manual/', AsignarPsicologoHITLView.as_view(), name='ia-asignacion-manual'),
    # Rutas Incremento Sprint 4 (CU23 HU-49 Resumen IA HITL + CU24 HU-50/HU-51 Alertas Riesgo IA)
    path('pacientes/<uuid:paciente_id>/resumenes-ia/', PacienteResumenIAListCreateView.as_view(), name='paciente-resumenes-ia'),
    path('resumenes-ia/<uuid:resumen_id>/aprobar/', ResumenIAAprobarHITLView.as_view(), name='resumen-ia-aprobar'),
    path('resumenes-ia/<uuid:resumen_id>/pdf/', ResumenIAPDFView.as_view(), name='resumen-ia-pdf'),
    path('alertas-riesgo/', AlertasRiesgoIAListView.as_view(), name='alertas-riesgo-list'),
    path('alertas-riesgo/evaluar/', AlertasRiesgoIAEvaluarView.as_view(), name='alertas-riesgo-evaluar'),
    path('alertas-riesgo/<uuid:alerta_id>/transicion/', AlertaRiesgoIATransicionView.as_view(), name='alerta-riesgo-transicion'),
    path('', include(router.urls)),
]
