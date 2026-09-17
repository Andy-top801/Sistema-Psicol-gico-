# ==============================================================================
# MÓDULO: clinica/permissions.py
# CASO DE USO: CU15 (Control de Acceso RBAC Clínico / HU-26)
# DESCRIPCIÓN: Valida que sólo el psicólogo tratante asignado, coordinador o admin
#              tengan acceso al expediente médico-legal del paciente.
# ==============================================================================
from rest_framework.permissions import BasePermission
from accounts.models import Rol
from audit.services import write_event

class IsTreatingPsychologistOrAdmin(BasePermission):
    """
    Permite acceso clínico exclusivo a:
    1. SuperAdministrador o Administrador/Coordinador del Centro (con auditoría).
    2. Psicólogo tratante asignado al paciente (mediante cita activa o apertura de HC).
    Bloquea con HTTP 403 a psicólogos no asignados y a roles administrativos sin facultad clínica.
    """
    message = "Acceso denegado: El expediente clínico está protegido y reservado al terapeuta tratante asignado."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        
        rol_nombre = request.user.rol.nombre.lower() if request.user.rol else ""
        if 'admin' in rol_nombre or 'coordinador' in rol_nombre or request.user.rol.nombre == Rol.SUPERADMIN:
            return True
        
        # Permitir a psicólogos y pacientes según corresponda
        if 'psic' in rol_nombre or 'paciente' in rol_nombre:
            return True
            
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True

        rol_nombre = user.rol.nombre.lower() if user.rol else ""

        # Administrador / Director Clínico puede auditar y supervisar
        if 'admin' in rol_nombre or 'coordinador' in rol_nombre:
            return True

        # Obtener el paciente objetivo según el tipo de entidad
        paciente = None
        if hasattr(obj, 'paciente'):
            paciente = obj.paciente
        elif hasattr(obj, 'historia_clinica') and hasattr(obj.historia_clinica, 'paciente'):
            paciente = obj.historia_clinica.paciente
        elif hasattr(obj, 'codigo_historia') and hasattr(obj, 'paciente'):
            paciente = obj.paciente
        elif hasattr(obj, 'codigo_expediente'):
            paciente = obj

        # Si el usuario es Paciente, solo accede a su propio registro
        if 'paciente' in rol_nombre:
            if paciente and hasattr(user, 'perfil_paciente') and user.perfil_paciente == paciente:
                return True
            return False

        # Si el usuario es Psicólogo, validar que sea terapeuta asignado
        if 'psic' in rol_nombre and hasattr(user, 'perfil_psicologo'):
            psico = user.perfil_psicologo

            # 1. ¿Es el psicólogo de apertura de la historia clínica?
            if hasattr(obj, 'psicologo_apertura') and obj.psicologo_apertura == psico:
                return True

            # 2. ¿Es el creador de la nota o tarea?
            if hasattr(obj, 'psicologo') and obj.psicologo == psico:
                return True
            if hasattr(obj, 'psicologo_emisor') and obj.psicologo_emisor == psico:
                return True

            # 3. ¿Tiene citas asignadas con este paciente?
            if paciente and paciente.citas.filter(psicologo=psico).exists():
                return True

            # Si no está asignado: registrar auditoría del intento no autorizado y bloquear (HU-26 criterio a)
            try:
                write_event({
                    "action": "RBAC_CLINICO_BLOQUEADO",
                    "user": user.email,
                    "target": str(getattr(obj, 'id', 'desconocido')),
                    "motivo": "Intento de acceso a expediente de paciente no asignado"
                })
            except Exception:
                pass
            return False

        return False
