# ==============================================================================
# MÓDULO: finanzas/permissions.py
# DESCRIPCIÓN: Control de acceso RBAC para Caja Clínica (HU-52), Dashboard
#              Financiero Gerencial (HU-53) y Liquidación de Honorarios (HU-54).
# ==============================================================================
from rest_framework.permissions import BasePermission
from accounts.models import Rol


def _rol_lower(user) -> str:
    if not user or not getattr(user, 'is_authenticated', False):
        return ''
    if getattr(user, 'is_superuser', False):
        return 'superadmin'
    rol = getattr(user, 'rol', None)
    return (rol.nombre or '').lower() if rol else ''


def is_admin_financiero(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    rol = _rol_lower(user)
    return (
        'admin' in rol
        or 'coordinador' in rol
        or (user.rol and user.rol.nombre == Rol.SUPERADMIN)
    )


def is_caja_staff(user) -> bool:
    if is_admin_financiero(user):
        return True
    rol = _rol_lower(user)
    return 'recep' in rol or 'caja' in rol


class IsCajaStaff(BasePermission):
    """Permite operar caja a Recepcionista, Coordinador, Admin Centro y SuperAdmin."""
    message = 'Acceso denegado: Se requiere rol de Recepcionista o Administrador para operar Caja Clínica.'

    def has_permission(self, request, view):
        return is_caja_staff(request.user)


class IsAdminFinanciero(BasePermission):
    """Permite acceso gerencial exclusivo a Admin Centro, Coordinador y SuperAdmin."""
    message = 'Acceso denegado: Solo administradores del centro pueden acceder a la información financiera gerencial.'

    def has_permission(self, request, view):
        return is_admin_financiero(request.user)


class IsAdminOrOwnerPsychologist(BasePermission):
    """
    Admin financiero tiene acceso total a liquidaciones.
    Psicólogo puede consultar (GET) únicamente sus propias liquidaciones y boletas PDF.
    """
    message = 'Acceso denegado: Solo puede consultar sus propias liquidaciones de honorarios.'

    def has_permission(self, request, view):
        if is_admin_financiero(request.user):
            return True
        rol = _rol_lower(request.user)
        if request.method in ('GET', 'HEAD', 'OPTIONS') and 'psic' in rol:
            return hasattr(request.user, 'perfil_psicologo')
        return False

    def has_object_permission(self, request, view, obj):
        if is_admin_financiero(request.user):
            return True
        if request.method in ('GET', 'HEAD', 'OPTIONS') and hasattr(request.user, 'perfil_psicologo'):
            return obj.psicologo_id == request.user.perfil_psicologo.id
        return False


class IsCajaOrOwnerPaciente(BasePermission):
    """
    Personal de caja/admin tiene acceso total.
    Paciente puede consultar (GET) su propia cuenta, recibos y extracto.
    """
    message = 'Acceso denegado: Solo puede consultar su propio estado de cuenta.'

    def has_permission(self, request, view):
        if is_caja_staff(request.user):
            return True
        rol = _rol_lower(request.user)
        if request.method in ('GET', 'HEAD', 'OPTIONS') and 'paciente' in rol:
            return hasattr(request.user, 'perfil_paciente')
        return False
