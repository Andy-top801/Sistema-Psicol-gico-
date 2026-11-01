from django.contrib import admin
from django.urls import path, include

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
    # Endpoints de suscripciones y pagos Stripe (Punto 7+8)
    path('api/subscriptions/', include('subscriptions.urls')),
]
