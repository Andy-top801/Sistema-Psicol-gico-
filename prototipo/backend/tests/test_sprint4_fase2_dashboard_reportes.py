# ==============================================================================
# TEST: tests/test_sprint4_fase2_dashboard_reportes.py
# FASE 2 (Sprint 4): HU-53 Dashboard Financiero Gerencial (>= 2 años / 24m),
#                    Motor de Reportes Unificado (15 fuentes) y PDFExporter.
# ==============================================================================
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from django_tenants.utils import schema_context
from finanzas.dashboard_service import DashboardFinancieroService
from reportes.services import ReportEngine, FUENTES_DISPONIBLES
from reportes.exporters import PDFExporter, ExcelExporter


def test_hu53_dashboard_gerencial_24_meses_y_yoy():
    with schema_context('centro_esperanza'):
        data = DashboardFinancieroService.obtener_dashboard(horizonte='24m')

        assert data['moneda'] == 'BOB'
        assert data['rango']['meses_cubiertos'] == 24
        assert len(data['serie_mensual']) == 24

        kpis = data['kpis']
        assert kpis['ingreso_bruto'] > 0
        assert kpis['honorarios_psicologos'] > 0
        assert round(kpis['ingreso_bruto'] - kpis['honorarios_psicologos'], 2) == kpis['margen_neto_centro']
        assert kpis['indice_morosidad_pct'] >= 0.0

        # Comparativa YoY (12m actual vs 12m anterior)
        yoy = data['comparativa_yoy']
        assert yoy['periodo_actual']['ingreso_bruto'] > 0
        assert yoy['periodo_anterior']['ingreso_bruto'] > 0
        assert 'ingreso_bruto' in yoy['variacion_pct']

        # Distribución por método de pago y psicólogos
        assert len(data['distribucion_metodo_pago']) >= 3
        assert len(data['rendimiento_psicologos']) >= 1

        # Catálogo unificado de reportes (incluye clínicas + financieras)
        fuentes_cat = {r['fuente'] for r in data['catalogo_reportes']}
        for expected in ('citas', 'pacientes', 'psicologos', 'pagos', 'cuentas_pacientes', 'extracto_pagos', 'liquidaciones', 'alertas_riesgo_ia'):
            assert expected in fuentes_cat, f"Falta fuente '{expected}' en catalogo_reportes"


def test_motor_reportes_unificado_paginacion_y_pdf_exporter():
    with schema_context('centro_esperanza'):
        for fuente in ('pagos', 'cuentas_pacientes', 'extracto_pagos', 'liquidaciones', 'alertas_riesgo_ia', 'resumenes_ia'):
            assert fuente in FUENTES_DISPONIBLES
            res = ReportEngine.generar(fuente, page=1, page_size=15)
            assert 'columnas' in res and 'datos' in res and 'paginacion' in res
            assert len(res['datos']) <= 15

        # Verificar PDFExporter y ExcelExporter sobre pagos y extracto_pagos
        res_pagos = ReportEngine.generar('pagos')
        assert res_pagos['total'] >= 100
        pdf_resp = PDFExporter.generar(res_pagos, 'pagos', tenant_name='Centro Esperanza')
        assert pdf_resp.status_code == 200
        assert pdf_resp['Content-Type'] == 'application/pdf'
        assert pdf_resp.content.startswith(b'%PDF')

        xlsx_resp = ExcelExporter.generar(res_pagos, 'pagos', tenant_name='Centro Esperanza')
        assert xlsx_resp.status_code == 200
        assert xlsx_resp.content.startswith(b'PK\x03\x04')

        # Verificar extracto_pagos con 20 años de historial
        res_ext = ReportEngine.generar('extracto_pagos')
        assert res_ext['total'] >= 400


def test_cu26b_estado_resultados_gastos_fijos_y_crm():
    from decimal import Decimal
    from django.db import transaction
    from django.utils import timezone
    from clinica.models import Paciente, Psicologo
    from agenda.models import Cita
    from datetime import time

    class _Rb(Exception):
        pass

    with schema_context('centro_esperanza'):
        try:
            with transaction.atomic():
                hoy = timezone.localdate()
                g = DashboardFinancieroService.registrar_gasto_fijo(
                    categoria='ALQUILER',
                    descripcion='Test P&L Alquiler CU26-B',
                    monto=Decimal('100.00'),
                    moneda='USD',  # 696.00 BOB
                    periodo_mes=hoy.replace(day=1),
                )
                assert g.monto_bob == Decimal('696.00')

                pl = DashboardFinancieroService.calcular_estado_resultados_y_crm()
                assert round(pl['ganancia_bruta_bob'] - pl['total_gastos_fijos_bob'], 2) == pl['utilidad_neta_bob']
                assert pl['total_gastos_fijos_bob'] >= 696.0

                # Verificar déficit contable cuando gasto excede ganancia bruta
                DashboardFinancieroService.registrar_gasto_fijo(
                    categoria='OTROS',
                    descripcion='Gasto extraordinario déficit test',
                    monto=Decimal('9999999.00'),
                    moneda='BOB',
                    periodo_mes=hoy.replace(day=1),
                )
                pl_def = DashboardFinancieroService.calcular_estado_resultados_y_crm()
                assert pl_def['es_deficit'] is True
                assert pl_def['utilidad_neta_bob'] < 0

                # CRM Post-Consulta: <= 2 estrellas activa seguimiento automático PENDIENTE
                pac = Paciente.objects.first()
                psi = Psicologo.objects.first()
                cita = Cita.objects.create(
                    paciente=pac, psicologo=psi, fecha=hoy,
                    hora_inicio=time(18, 0), hora_fin=time(19, 0),
                    modalidad='PRESENCIAL', estado='REALIZADA', costo=Decimal('150.00'),
                )
                calif = DashboardFinancieroService.registrar_calificacion_crm(
                    paciente=pac, cita=cita, psicologo=psi,
                    puntuacion_estrellas=2, comentario='Demora en sala',
                )
                assert calif.requiere_seguimiento is True
                assert calif.estado_seguimiento == 'PENDIENTE'
                crm = DashboardFinancieroService.obtener_estadisticas_crm()
                assert crm['total_calificaciones'] >= 1
                assert '2' in crm['histograma_1a5']
                raise _Rb()
        except _Rb:
            pass


if __name__ == '__main__':
    test_hu53_dashboard_gerencial_24_meses_y_yoy()
    print('[OK] HU-53: Dashboard Gerencial 24 meses, KPIs Margen Neto, YoY y Catálogo de Reportes')
    test_motor_reportes_unificado_paginacion_y_pdf_exporter()
    print('[OK] ReportEngine Unificado (paginación + 6 nuevas fuentes + PDFExporter + Excel)')
    test_cu26b_estado_resultados_gastos_fijos_y_crm()
    print('[OK] CU26-B & CRM: Ganancia Bruta vs Utilidad Neta (Gastos Fijos BOB/USD), Déficit y Alertas <=2*')
    print('ALL SPRINT 4 FASE 2 TESTS PASSED [OK]')
