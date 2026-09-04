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
]
