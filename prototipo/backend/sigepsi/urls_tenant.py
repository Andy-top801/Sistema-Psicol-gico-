from django.contrib import admin
from django.urls import path, include
from finanzas.views import CalificacionCRMListCreateView, CalificacionCRMSeguimientoView, EstadisticasCRMView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Endpoints de cuentas, autenticación, roles, permisos y usuarios
    path('api/', include('accounts.urls')),
    # Endpoints de configuración institucional del centro
    path('api/', include('core.urls')),
    # Endpoints de centros (para selector público)
    path('api/', include('tenants.urls')),
    # Endpoints de clínica (Sprint 1, Sprint 2 y Sprint 3)
    path('api/clinica/', include('clinica.urls')),
    path('api/v1/clinica/', include('clinica.urls')),
    path('api/v1/', include('clinica.urls')),
    # Endpoints de agenda (citas, teleconsulta, dashboard, alertas, FCM)
    path('api/agenda/', include('agenda.urls')),
    path('api/v1/agenda/', include('agenda.urls')),
    path('api/v1/', include('agenda.urls')),
    # Endpoints de cuentas / JWT v1
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/', include('accounts.urls')),
    path('api/', include('audit.urls')),
    # Endpoints de reportes personalizables - Sprint 2
    path('api/reportes/', include('reportes.urls')),
    path('api/v1/reportes/', include('reportes.urls')),
    # Endpoints de finanzas clínicas y honorarios (Bs.) - Sprint 4
    path('api/finanzas/', include('finanzas.urls')),
    path('api/v1/finanzas/', include('finanzas.urls')),
    # Endpoints directos CRM 1-5 estrellas (CU26-CRM / HU-55)
    path('api/crm/calificaciones/', CalificacionCRMListCreateView.as_view(), name='crm-calificaciones-root'),
    path('api/v1/crm/calificaciones/', CalificacionCRMListCreateView.as_view(), name='crm-calificaciones-v1'),
    path('api/v1/crm/calificaciones/<uuid:calificacion_id>/atender/', CalificacionCRMSeguimientoView.as_view(), name='crm-atender-v1'),
    path('api/crm/estadisticas/', EstadisticasCRMView.as_view(), name='crm-estadisticas-root'),
    path('api/v1/crm/estadisticas/', EstadisticasCRMView.as_view(), name='crm-estadisticas-v1'),
    # Endpoints de suscripciones y pagos Stripe (Punto 7+8)
    path('api/subscriptions/', include('subscriptions.urls')),
]
