# ==============================================================================
# TEST: tests/test_sprint4_fase6_estres_multitenant.py
# FASE 6 (Sprint 4): HU-56 Certificación final de estrés concurrente (30+ reqs),
#                    aislamiento multi-tenant JWT (centro_esperanza vs mentesana),
#                    RBAC gerencial y benchmark de extracto 20 años / dashboard 24m.
# ==============================================================================
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from django.db import close_old_connections
from django_tenants.utils import schema_context
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Usuario
from finanzas.services import FinanzasService
from finanzas.dashboard_service import DashboardFinancieroService
from finanzas.pdf_utils import generar_extracto_bancario_pdf, generar_extracto_bancario_excel


def test_hu56_estres_concurrente_30_peticiones():
    """HU-56 (a): 30+ peticiones simultáneas entre múltiples tenants con 0% errores y sin deadlocks."""
    errores = []
    latencias = []

    def _worker(idx: int):
        schema = 'centro_esperanza' if idx % 2 == 0 else 'mentesana'
        t0 = time.perf_counter()
        try:
            close_old_connections()
            with schema_context(schema):
                if idx % 3 == 0:
                    res = DashboardFinancieroService.obtener_dashboard(horizonte='24m')
                    assert res['rango']['meses_cubiertos'] == 24
                elif idx % 3 == 1:
                    ext = FinanzasService.obtener_extracto_bancario(
                        fecha_desde=date(2007, 1, 1),
                        fecha_hasta=date(2026, 12, 31),
                        page=1,
                        page_size=25,
                    )
                    assert ext['resumen']['total_registros'] >= 200
                else:
                    from clinica.ia_riesgo_service import RiesgoLongitudinalService
                    qs = list(RiesgoLongitudinalService.listar_consola_priorizada()[:10])
                    assert isinstance(qs, list)
            return time.perf_counter() - t0
        except Exception as exc:
            errores.append((idx, schema, repr(exc)))
            return None
        finally:
            close_old_connections()

    total_reqs = 32
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(_worker, i) for i in range(total_reqs)]
        for f in as_completed(futures):
            lat = f.result()
            if lat is not None:
                latencias.append(lat)

    assert len(errores) == 0, f"Errores bajo concurrencia: {errores[:3]}"
    assert len(latencias) == total_reqs
    avg_ms = (sum(latencias) / len(latencias)) * 1000
    print(f"    -> Concurrencia {total_reqs} tareas multi-tenant OK | 0% errores | latencia prom: {avg_ms:.1f} ms")


def test_hu56_aislamiento_multitenant_jwt_y_rbac():
    """
    HU-56 (b): Token JWT emitido para centro_esperanza es rechazado en mentesana.
    HU-53 (c): Rol Paciente es bloqueado con 403 Forbidden en Dashboard Financiero.
    """
    with schema_context('centro_esperanza'):
        admin_esp = Usuario.objects.filter(rol__nombre__icontains='Admin', activo=True).first()
        pac_esp = Usuario.objects.filter(rol__nombre__icontains='Paciente', activo=True).first()
        assert admin_esp is not None, "Falta usuario Admin en centro_esperanza"
        token_esp = str(RefreshToken.for_user(admin_esp).access_token)
        token_pac = str(RefreshToken.for_user(pac_esp).access_token) if pac_esp else None

    client = APIClient()

    # 1. Token válido de centro_esperanza SÍ accede a centro_esperanza
    resp_ok = client.get(
        '/api/finanzas/dashboard/?horizonte=24m',
        HTTP_AUTHORIZATION=f'Bearer {token_esp}',
        HTTP_X_TENANT_SLUG='centro_esperanza',
    )
    assert resp_ok.status_code == 200, f"Esperado 200 en propio tenant, recibido {resp_ok.status_code}"

    # 2. Mismo token de centro_esperanza intentando acceder a mentesana DEBE fallar (401/403)
    for endpoint in ('/api/finanzas/dashboard/', '/api/finanzas/extracto/', '/api/finanzas/cuentas/', '/api/clinica/alertas-riesgo/'):
        resp_cross = client.get(
            endpoint,
            HTTP_AUTHORIZATION=f'Bearer {token_esp}',
            HTTP_X_TENANT_SLUG='mentesana',
        )
        assert resp_cross.status_code in (401, 403), (
            f"FUGA MULTI-TENANT en {endpoint}: token de centro_esperanza obtuvo {resp_cross.status_code} en mentesana!"
        )

    # 3. Rol Paciente bloqueado con 403 en Dashboard Financiero gerencial
    if token_pac:
        resp_pac = client.get(
            '/api/finanzas/dashboard/',
            HTTP_AUTHORIZATION=f'Bearer {token_pac}',
            HTTP_X_TENANT_SLUG='centro_esperanza',
        )
        assert resp_pac.status_code == 403, f"Paciente debió recibir 403 en dashboard financiero, obtuvo {resp_pac.status_code}"


def test_hu56_benchmark_extracto_20_anios_y_dashboard_24_meses():
    """HU-56 (c): Rendimiento de extracto 20 años (JSON, PDF multipágina, Excel streaming) y dashboard 24 meses."""
    with schema_context('centro_esperanza'):
        t0 = time.perf_counter()
        dash = DashboardFinancieroService.obtener_dashboard(horizonte='24m')
        t_dash = time.perf_counter() - t0
        assert dash['rango']['meses_cubiertos'] == 24
        assert t_dash < 5.0, f"Dashboard 24m tardó demasiado: {t_dash:.2f}s"

        t1 = time.perf_counter()
        ext = FinanzasService.obtener_extracto_bancario(
            fecha_desde=date(2007, 1, 1),
            fecha_hasta=date(2026, 12, 31),
            page=1,
            page_size=50,
        )
        t_ext_json = time.perf_counter() - t1
        assert ext['resumen']['total_registros'] >= 400
        assert t_ext_json < 5.0

        t2 = time.perf_counter()
        meta_p, rows_p = FinanzasService.iterar_extracto_bancario(
            fecha_desde=date(2007, 1, 1),
            fecha_hasta=date(2026, 12, 31),
        )
        pdf_resp = generar_extracto_bancario_pdf(meta_p, rows_p, tenant_name='Centro Esperanza')
        t_pdf = time.perf_counter() - t2
        assert pdf_resp.content.startswith(b'%PDF')
        assert t_pdf < 10.0

        t3 = time.perf_counter()
        meta_x, rows_x = FinanzasService.iterar_extracto_bancario(
            fecha_desde=date(2007, 1, 1),
            fecha_hasta=date(2026, 12, 31),
        )
        xlsx_resp = generar_extracto_bancario_excel(meta_x, rows_x, tenant_name='Centro Esperanza')
        t_xlsx = time.perf_counter() - t3
        assert xlsx_resp.content.startswith(b'PK\x03\x04')
        assert t_xlsx < 5.0

        print(
            f"    -> Benchmark OK | Dashboard 24m: {t_dash*1000:.0f}ms | "
            f"Extracto 20a JSON ({ext['resumen']['total_registros']} movs): {t_ext_json*1000:.0f}ms | "
            f"PDF multipágina ({len(pdf_resp.content)//1024} KB): {t_pdf*1000:.0f}ms | "
            f"Excel streaming: {t_xlsx*1000:.0f}ms"
        )


if __name__ == '__main__':
    test_hu56_estres_concurrente_30_peticiones()
    print('[OK] HU-56 (a): Estrés concurrente 32 peticiones multi-tenant sin errores ni deadlocks')
    test_hu56_aislamiento_multitenant_jwt_y_rbac()
    print('[OK] HU-56 (b): Aislamiento JWT cross-tenant (centro_esperanza vs mentesana) + RBAC 403')
    test_hu56_benchmark_extracto_20_anios_y_dashboard_24_meses()
    print('[OK] HU-56 (c): Benchmark Extracto 20 años (JSON/PDF/Excel) y Dashboard 24 meses')
    print('ALL SPRINT 4 FASE 6 TESTS PASSED [OK]')
