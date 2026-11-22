# ==============================================================================
# TEST: tests/test_sprint4_fase3_saas.py
# FASE 3 (Sprint 4): HU-55 Panel SuperAdmin SaaS (USD), FacturaSaaS idempotente
#                    y validación de cupos max_psicologos / max_pacientes.
# ==============================================================================
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from django_tenants.utils import get_public_schema_name, schema_context
from tenants.models import Tenant
from subscriptions.models import Suscripcion, FacturaSaaS
from subscriptions.services import obtener_dashboard_saas, registrar_factura_saas_idempotente
from subscriptions.quotas import validar_cupo_psicologos, obtener_uso_cupos_tenant


def test_hu55_dashboard_saas_y_facturas_usd():
    data = obtener_dashboard_saas()
    assert data['moneda'] == 'USD'
    assert data['kpis']['tenants_totales'] >= 12
    assert data['kpis']['tenants_activos'] >= 12
    assert data['kpis']['mrr_usd'] > 0
    assert len(data['tenants']) >= 12
    # Cada centro debe tener factura inicial y cupos
    first_t = data['tenants'][0]
    assert 'cupos' in first_t and 'facturas' in first_t
    assert len(first_t['facturas']) >= 1


def test_hu55_idempotencia_factura_saas():
    with schema_context(get_public_schema_name()):
        susc = Suscripcion.objects.first()
        assert susc is not None
        session_id = 'cs_test_idempotente_hu55_999'
        FacturaSaaS.objects.filter(stripe_session_id=session_id).delete()

        f1, created1 = registrar_factura_saas_idempotente(susc, stripe_session_id=session_id)
        f2, created2 = registrar_factura_saas_idempotente(susc, stripe_session_id=session_id)

        assert created1 is True
        assert created2 is False
        assert f1.id == f2.id
        assert FacturaSaaS.objects.filter(stripe_session_id=session_id).count() == 1

        # Limpiar factura de prueba
        FacturaSaaS.objects.filter(stripe_session_id=session_id).delete()


def test_hu55_cupos_plan_basico_bloquea_4to_psicologo():
    with schema_context(get_public_schema_name()):
        tenant = Tenant.objects.get(schema_name='centro_esperanza')
        plan_original = tenant.plan

    try:
        # Forzar temporalmente plan BASICO (max_psicologos = 3) donde centro_esperanza tiene >= 5 psicólogos
        with schema_context(get_public_schema_name()):
            tenant.plan = 'BASICO'
            tenant.save(update_fields=['plan'])

        with schema_context('centro_esperanza'):
            ok, err = validar_cupo_psicologos(tenant)
            assert ok is False
            assert err['code'] == 'PLAN_QUOTA_EXCEEDED'
            assert err['limite_actual'] == 3
            assert err['plan_sugerido'] == 'profesional'
            assert 'Profesional' in err['detail']

        uso = obtener_uso_cupos_tenant(tenant)
        assert uso['alerta_cupo_psicologos'] is True
    finally:
        with schema_context(get_public_schema_name()):
            tenant.plan = plan_original
            tenant.save(update_fields=['plan'])


if __name__ == '__main__':
    test_hu55_dashboard_saas_y_facturas_usd()
    print('[OK] HU-55 (a): Consola SuperAdmin SaaS, MRR USD y FacturaSaaS por tenant')
    test_hu55_idempotencia_factura_saas()
    print('[OK] HU-55 (c): Idempotencia de stripe_session_id sin facturas duplicadas')
    test_hu55_cupos_plan_basico_bloquea_4to_psicologo()
    print('[OK] HU-55 (b): Bloqueo de cupo en Plan Básico (>3 psicólogos) con sugerencia a Profesional')
    print('ALL SPRINT 4 FASE 3 TESTS PASSED [OK]')
