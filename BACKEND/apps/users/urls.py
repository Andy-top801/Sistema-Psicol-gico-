from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UsuarioViewSet,
    RolViewSet,
    PermisoViewSet,
    EspecialidadViewSet,
    PsicologoViewSet,
    DisponibilidadPsicologoViewSet,
    PasswordResetViewSet,
    MeView,
    RegisterView,
    PasswordResetRequestView,
    PasswordResetVerifyView,
    PasswordResetConfirmView,
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'roles', RolViewSet)
router.register(r'permisos', PermisoViewSet)
router.register(r'especialidades', EspecialidadViewSet)
router.register(r'psicologos', PsicologoViewSet)
router.register(r'disponibilidades-psicologo', DisponibilidadPsicologoViewSet)
router.register(r'auth/password-reset', PasswordResetViewSet, basename='password-reset')

app_name = 'users'

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path(
        'auth/password-reset-verify/',
        PasswordResetVerifyView.as_view(),
        name='password_reset_verify',
    ),
    path(
        'auth/password-reset-confirm/',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path('me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]
