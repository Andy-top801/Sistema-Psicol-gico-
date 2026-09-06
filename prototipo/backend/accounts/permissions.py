from rest_framework.permissions import BasePermission
from accounts.models import Rol

class EsSuperAdmin(BasePermission):
    """Permite el acceso únicamente al SuperAdministrador."""
    message = "Acceso denegado: se requieren permisos de SuperAdministrador."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if request.user.rol and request.user.rol.nombre == Rol.SUPERADMIN:
            return True
        return False


class EsAdminCentro(BasePermission):
    """Permite el acceso a Administradores del Centro o SuperAdmin."""
    message = "Acceso denegado: se requieren permisos de Administrador de Centro."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if request.user.rol and request.user.rol.nombre in [Rol.ADMIN_CENTRO, Rol.SUPERADMIN]:
            return True
        return False


class RequierePermiso(BasePermission):
    """
    Permiso dinámico basado en RBAC.
    Verifica que el usuario autenticado posea el permiso especificado en 'permiso_codigo' de la vista.
    """
    message = "Acceso denegado: no cuenta con el permiso requerido para esta acción."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        
        # Obtener permiso requerido por la vista
        permiso_requerido = getattr(view, 'permiso_codigo', None)
        if not permiso_requerido:
            # Si no se especifica permiso puntual, basta con estar autenticado
            return True
        
        return request.user.tiene_permiso(permiso_requerido)
