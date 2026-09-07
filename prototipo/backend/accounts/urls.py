from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import (
    RegistroView, LoginView, LogoutView,
    PasswordResetRequestView, PasswordResetConfirmView,
    UsuarioViewSet, RolViewSet, PermisoListView, MeView
)

router = DefaultRouter()
router.register(r'users', UsuarioViewSet, basename='users')
router.register(r'roles', RolViewSet, basename='roles')

urlpatterns = [
    # Autenticación
    path('auth/register/', RegistroView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    
    # Permisos
    path('permisos/', PermisoListView.as_view(), name='permisos-list'),

    # Users & Roles CRUD
    path('', include(router.urls)),
]
