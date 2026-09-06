"""
Utilidades compartidas para la siembra de datos de tenant.
Usadas tanto por el comando seed_data como por el TenantSerializer al crear nuevos centros.
"""
from accounts.models import Rol, Permiso, RolPermiso


def seed_tenant_roles_and_permissions():
    """
    Crea todos los permisos del sistema y los roles con sus asignaciones.
    Debe llamarse dentro de un schema_context del tenant correspondiente.
    Retorna un diccionario con los roles creados: { nombre_rol: instancia_Rol }.
    """

    # A. Permisos del sistema
    permisos_def = [
        ("Gestionar Usuarios", "gestionar_usuarios", "Usuarios y Seguridad",
         "Crear, listar, editar y cambiar estado de usuarios"),
        ("Gestionar Roles", "gestionar_roles", "Usuarios y Seguridad",
         "Crear y modificar roles institucionales"),
        ("Asignar Permisos", "asignar_permisos", "Usuarios y Seguridad",
         "Asignar matriz de permisos a roles"),
        ("Ver Dashboard", "ver_dashboard", "Panel de Control",
         "Visualizar KPIs y estadísticas operativas"),
        ("Ver Alertas de Prioridad", "ver_alertas", "Panel de Control",
         "Atender alertas clínicas y de abandono"),
        ("Gestionar Citas", "gestionar_citas", "Agenda",
         "Agendar, reprogramar, confirmar y cancelar citas"),
        ("Ver Agenda", "ver_agenda", "Agenda",
         "Consultar calendario de disponibilidad"),
        ("Teleconsulta", "teleconsulta", "Agenda",
         "Iniciar y participar en videollamadas seguras"),
        ("Ver Historia Clínica", "ver_historia_clinica", "Área Clínica",
         "Consultar expediente y antecedentes del paciente"),
        ("Registrar Notas de Sesión", "registrar_notas_sesion", "Área Clínica",
         "Documentar evolución y observaciones clínicas"),
        ("Gestionar Tareas Terapéuticas", "gestionar_tareas", "Área Clínica",
         "Asignar y evaluar tareas entre sesiones"),
        ("Configurar Centro", "configurar_centro", "Administración",
         "Editar datos institucionales, horarios y políticas"),
    ]

    permisos_map = {}
    for nom, cod, mod, desc in permisos_def:
        p, _ = Permiso.objects.get_or_create(
            codigo=cod,
            defaults={"nombre": nom, "modulo": mod, "descripcion": desc}
        )
        permisos_map[cod] = p

    # B. Roles y asignación de permisos
    roles_config = {
        Rol.ADMIN_CENTRO: {
            "desc": "Administrador total del centro psicológico",
            "permisos": list(permisos_map.keys())  # Todos los permisos
        },
        Rol.COORDINADOR: {
            "desc": "Supervisión clínica, asignaciones y triage",
            "permisos": ["ver_dashboard", "ver_alertas", "gestionar_citas",
                         "ver_agenda", "ver_historia_clinica"]
        },
        Rol.PSICOLOGO: {
            "desc": "Profesional de atención terapéutica",
            "permisos": ["ver_agenda", "gestionar_citas", "ver_historia_clinica",
                         "registrar_notas_sesion", "gestionar_tareas", "teleconsulta"]
        },
        Rol.RECEPCIONISTA: {
            "desc": "Atención al paciente y agendamiento",
            "permisos": ["ver_dashboard", "gestionar_citas", "ver_agenda",
                         "gestionar_usuarios"]
        },
        Rol.PACIENTE: {
            "desc": "Paciente del centro",
            "permisos": ["ver_agenda", "gestionar_citas", "gestionar_tareas"]
        },
    }

    roles_map = {}
    for rol_nombre, config in roles_config.items():
        rol, _ = Rol.objects.get_or_create(
            nombre=rol_nombre,
            defaults={"descripcion": config["desc"]}
        )
        roles_map[rol_nombre] = rol

        # Asignar permisos
        for p_cod in config["permisos"]:
            p = permisos_map.get(p_cod)
            if p:
                RolPermiso.objects.get_or_create(rol=rol, permiso=p)

    return roles_map
