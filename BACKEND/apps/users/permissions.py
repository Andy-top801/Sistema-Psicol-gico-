"""Permisos basados en el nombre del rol (`Rol.name`).

El modelo `Usuario` usa `roles = ManyToManyField(Rol)` — no hay un campo de rol
único. `IsAdminUser` (que exige `is_staff`) dejaba fuera a psicólogos, pacientes
y recepcionistas reales. Estas clases resuelven el permiso por el nombre del rol,
tolerando acentos, espacios y mayúsculas.
"""
import unicodedata

from rest_framework.permissions import BasePermission, SAFE_METHODS


def normalize_role(name: str) -> str:
    n = unicodedata.normalize('NFD', name or '')
    n = ''.join(c for c in n if unicodedata.category(c) != 'Mn')
    return n.lower().replace(' ', '')


# Alias tolerantes → rol canónico
_ALIASES = {
    'superadmin': 'superadmin',
    'superadministrador': 'superadmin',
    'adminplataforma': 'superadmin',
    'admincentro': 'admincentro',
    'administrador': 'admincentro',
    'administradordelcentro': 'admincentro',
    'admin': 'admincentro',
    'coordinador': 'coordinador',
    'coordinadorclinico': 'coordinador',
    'psicologo': 'psicologo',
    'psiquiatra': 'psicologo',
    'recepcionista': 'recepcionista',
    'paciente': 'paciente',
}

STAFF_ROLES = {
    'superadmin',
    'admincentro',
    'coordinador',
    'psicologo',
    'recepcionista',
}


def user_roles(user) -> set:
    """Conjunto de roles canónicos del usuario (+ superadmin si is_superuser)."""
    if not user or not getattr(user, 'is_authenticated', False):
        return set()
    roles = set()
    for name in user.roles.values_list('name', flat=True):
        roles.add(_ALIASES.get(normalize_role(name), normalize_role(name)))
    if getattr(user, 'is_superuser', False):
        roles.add('superadmin')
    return roles


class HasAnyRole(BasePermission):
    """Permite el acceso si el usuario tiene alguno de los roles declarados en
    la vista (`read_roles` para GET/HEAD/OPTIONS, `write_roles` para el resto;
    `required_roles` como fallback). `superadmin` siempre pasa."""

    def has_permission(self, request, view):
        roles = user_roles(request.user)
        if not roles:
            return False
        if 'superadmin' in roles:
            return True
        if request.method in SAFE_METHODS:
            allowed = getattr(view, 'read_roles', None)
        else:
            allowed = getattr(view, 'write_roles', None)
        if allowed is None:
            allowed = getattr(view, 'required_roles', STAFF_ROLES)
        return bool(roles & set(allowed))


class IsStaffRole(HasAnyRole):
    required_roles = STAFF_ROLES


class IsSelfPacienteOrStaff(BasePermission):
    """Objeto: el paciente solo puede ver/editar su propio expediente; el staff
    puede con cualquiera."""

    def has_object_permission(self, request, view, obj):
        roles = user_roles(request.user)
        if roles & STAFF_ROLES or 'superadmin' in roles:
            return True
        usuario = getattr(obj, 'usuario', None)
        return usuario is not None and usuario == request.user
