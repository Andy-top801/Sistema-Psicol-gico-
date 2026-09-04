from django.contrib import admin
from django.urls import path, include
from accounts.views import LoginView, RegistroView, LogoutView, MeView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Endpoints de autenticación para SuperAdmin en esquema public
    path('api/auth/login/', LoginView.as_view(), name='public-login'),
    path('api/auth/register/', RegistroView.as_view(), name='public-register'),
    path('api/auth/logout/', LogoutView.as_view(), name='public-logout'),
    path('api/auth/me/', MeView.as_view(), name='public-me'),
    # Endpoints de gestión de Tenants
    path('api/', include('tenants.urls')),
]
