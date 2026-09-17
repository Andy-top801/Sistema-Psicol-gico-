# ==============================================================================
# MÓDULO: subscriptions/plans.py
# DESCRIPCIÓN: Definición de los planes de suscripción SaaS disponibles para SIGEPSI.
#              Incluye precios, límites y características de cada plan.
# PUNTO 7+8: Modelo SaaS en la nube — Web/Móvil con pasarela de pagos Stripe
# ==============================================================================

PLANES = {
    'basico': {
        'id': 'basico',
        'nombre': 'Básico',
        'precio_mensual': 2900,  # En centavos USD ($29.00)
        'moneda': 'usd',
        'max_psicologos': 3,
        'max_pacientes': 50,
        'recomendado': False,
        'features': [
            'Hasta 3 psicólogos',
            'Hasta 50 pacientes activos',
            'Historias clínicas digitales',
            'Agenda y citas',
            'Reportes básicos',
            'Soporte por email',
        ],
    },
    'profesional': {
        'id': 'profesional',
        'nombre': 'Profesional',
        'precio_mensual': 5900,  # En centavos USD ($59.00)
        'moneda': 'usd',
        'max_psicologos': 10,
        'max_pacientes': 200,
        'recomendado': True,
        'features': [
            'Hasta 10 psicólogos',
            'Hasta 200 pacientes activos',
            'Historias clínicas digitales',
            'Agenda y citas',
            'Teleconsulta integrada',
            'Reportes personalizables',
            'Notas SOAP y consentimientos',
            'Soporte prioritario',
        ],
    },
    'empresarial': {
        'id': 'empresarial',
        'nombre': 'Empresarial',
        'precio_mensual': 9900,  # En centavos USD ($99.00)
        'moneda': 'usd',
        'max_psicologos': 9999,
        'max_pacientes': 99999,
        'recomendado': False,
        'features': [
            'Psicólogos ilimitados',
            'Pacientes ilimitados',
            'Historias clínicas digitales',
            'Agenda y citas',
            'Teleconsulta integrada',
            'Reportes personalizables',
            'Notas SOAP y consentimientos',
            'Derivaciones y tareas terapéuticas',
            'Backup/Restore automático',
            'Soporte dedicado 24/7',
        ],
    },
}


def get_plan(plan_id: str) -> dict | None:
    """Retorna un plan por su ID o None si no existe."""
    return PLANES.get(plan_id)


def get_all_plans() -> list[dict]:
    """Retorna todos los planes disponibles como lista."""
    return list(PLANES.values())
