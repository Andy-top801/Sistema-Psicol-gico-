# ==============================================================================
# MÓDULO: subscriptions/quotas.py
# CASO DE USO: CU26 (HU-55) Validación automática de cupos operativos por plan SaaS
# DESCRIPCIÓN: Valida max_psicologos y max_pacientes del tenant según su plan
#              vigente (Básico $29, Profesional $59, Empresarial $99).
# ==============================================================================
from django_tenants.utils import get_public_schema_name, schema_context
from subscriptions.plans import PLANES, get_plan


def _normalizar_plan_id(raw_plan: str | None) -> str:
    val = (raw_plan or 'profesional').strip().lower()
    if val in PLANES:
        return val
    if 'basic' in val or 'básic' in val:
        return 'basico'
    if 'empres' in val or 'enterp' in val:
        return 'empresarial'
    return 'profesional'


def _siguiente_plan(plan_id: str) -> dict | None:
    if plan_id == 'basico':
        return PLANES['profesional']
    if plan_id == 'profesional':
        return PLANES['empresarial']
    return None


def obtener_plan_tenant(tenant) -> dict:
    """Resuelve el diccionario oficial de PLANES para el tenant actual."""
    plan_raw = getattr(tenant, 'plan', None)
    plan_id = _normalizar_plan_id(plan_raw)
    return get_plan(plan_id) or PLANES['profesional']


def validar_cupo_psicologos(tenant) -> tuple[bool, dict | None]:
    """
    HU-55 (b): Verifica si el tenant puede registrar un nuevo psicólogo activo
    respetando max_psicologos de su plan SaaS.
    """
    if not tenant or getattr(tenant, 'schema_name', None) == get_public_schema_name():
        return True, None

    plan = obtener_plan_tenant(tenant)
    max_psico = int(plan['max_psicologos'])

    from clinica.models import Psicologo
    actuales = Psicologo.objects.filter(activo=True).count()
    if actuales >= max_psico:
        siguiente = _siguiente_plan(plan['id'])
        sugerencia = (
            f"Actualice al plan {siguiente['nombre']} (${siguiente['precio_mensual'] / 100:.0f}/mes)."
            if siguiente else "Contacte a soporte comercial para ampliar su cupo."
        )
        return False, {
            'code': 'PLAN_QUOTA_EXCEEDED',
            'recurso': 'psicologos',
            'plan_actual': plan['nombre'],
            'limite_actual': max_psico,
            'uso_actual': actuales,
            'plan_sugerido': siguiente['id'] if siguiente else None,
            'detail': (
                f"Límite del plan {plan['nombre']} alcanzado ({actuales}/{max_psico} psicólogos activos). "
                f"{sugerencia}"
            ),
        }
    return True, None


def validar_cupo_pacientes(tenant) -> tuple[bool, dict | None]:
    """
    HU-55 (b): Verifica si el tenant puede registrar un nuevo paciente
    respetando max_pacientes de su plan SaaS.
    """
    if not tenant or getattr(tenant, 'schema_name', None) == get_public_schema_name():
        return True, None

    plan = obtener_plan_tenant(tenant)
    max_pac = int(plan['max_pacientes'])

    from clinica.models import Paciente
    actuales = Paciente.objects.count()
    if actuales >= max_pac:
        siguiente = _siguiente_plan(plan['id'])
        sugerencia = (
            f"Actualice al plan {siguiente['nombre']} (${siguiente['precio_mensual'] / 100:.0f}/mes)."
            if siguiente else "Contacte a soporte comercial para ampliar su cupo."
        )
        return False, {
            'code': 'PLAN_QUOTA_EXCEEDED',
            'recurso': 'pacientes',
            'plan_actual': plan['nombre'],
            'limite_actual': max_pac,
            'uso_actual': actuales,
            'plan_sugerido': siguiente['id'] if siguiente else None,
            'detail': (
                f"Límite del plan {plan['nombre']} alcanzado ({actuales}/{max_pac} pacientes activos). "
                f"{sugerencia}"
            ),
        }
    return True, None


def obtener_uso_cupos_tenant(tenant) -> dict:
    """Devuelve el uso actual de psicólogos y pacientes frente a los límites del plan."""
    plan = obtener_plan_tenant(tenant)
    with schema_context(tenant.schema_name):
        from clinica.models import Psicologo, Paciente
        psicologos_activos = Psicologo.objects.filter(activo=True).count()
        pacientes_activos = Paciente.objects.count()

    return {
        'plan_id': plan['id'],
        'plan_nombre': plan['nombre'],
        'precio_mensual_usd': round(plan['precio_mensual'] / 100.0, 2),
        'psicologos_activos': psicologos_activos,
        'max_psicologos': plan['max_psicologos'],
        'pacientes_activos': pacientes_activos,
        'max_pacientes': plan['max_pacientes'],
        'alerta_cupo_psicologos': psicologos_activos >= plan['max_psicologos'],
        'alerta_cupo_pacientes': pacientes_activos >= plan['max_pacientes'],
    }
