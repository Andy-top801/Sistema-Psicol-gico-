# ==============================================================================
# TEST: tests/test_sprint4_fase1_finanzas.py
# FASE 1 (Sprint 4): HU-52 (Caja, Cobros, Recibo PDF, Extracto Bancario 20 años)
#                    HU-54 (Liquidación de Honorarios, anti-doble pago, Boleta PDF)
# ==============================================================================
import os
import sys
from datetime import date, datetime, time
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from django.db import transaction
from django.utils import timezone
from django_tenants.utils import schema_context

from agenda.models import Cita
from clinica.models import Paciente, Psicologo
from finanzas.models import CuentaPaciente, MovimientoFinanciero
from finanzas.services import FinanzasService
from finanzas.pdf_utils import (
    generar_recibo_pago_pdf,
    generar_extracto_bancario_pdf,
    generar_extracto_bancario_excel,
    generar_extracto_bancario_csv,
    generar_boleta_liquidacion_pdf,
)


class _RollbackAfterTest(Exception):
    pass


def _run_rolled_back(schema_name, fn):
    with schema_context(schema_name):
        try:
            with transaction.atomic():
                fn()
                raise _RollbackAfterTest()
        except _RollbackAfterTest:
            pass


def test_hu52_cobro_atomico_validaciones_y_recibo_pdf():
    def _body():
        paciente = Paciente.objects.select_related('usuario').first()
        psicologo = Psicologo.objects.select_related('usuario').first()
        assert paciente is not None and psicologo is not None

        cita = Cita.objects.create(
            paciente=paciente,
            psicologo=psicologo,
            fecha=date(2026, 11, 10),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            modalidad='PRESENCIAL',
            estado='REALIZADA',
            costo=Decimal('150.00'),
        )
        FinanzasService.registrar_cargo_cita(cita)
        cuenta = CuentaPaciente.objects.get(paciente=paciente)
        saldo_antes = cuenta.saldo_pendiente
        assert saldo_antes >= Decimal('150.00')

        # HU-52 (b): Rechazar monto <= 0 y monto superior al saldo
        for bad_amount in (Decimal('0.00'), Decimal('-10.00'), saldo_antes + Decimal('1.00')):
            raised = False
            try:
                FinanzasService.registrar_pago(paciente=paciente, monto=bad_amount, metodo_pago='QR_BANCARIO')
            except ValueError:
                raised = True
            assert raised, f"Debió rechazar monto inválido: {bad_amount}"

        # HU-52 (a): Pago válido en QR_BANCARIO por 150.00 Bs.
        pago = FinanzasService.registrar_pago(
            paciente=paciente,
            cita=cita,
            monto=Decimal('150.00'),
            metodo_pago='QR_BANCARIO',
            referencia_externa='QR-TEST-001',
        )
        cuenta.refresh_from_db()
        assert cuenta.saldo_pendiente == saldo_antes - Decimal('150.00')
        assert pago.numero_recibo.startswith('REC-')
        assert len(pago.codigo_verificacion) == 16

        # HU-52 (c): Recibo PDF válido
        resp_pdf = generar_recibo_pago_pdf(pago, tenant_name='Centro Esperanza')
        assert resp_pdf.status_code == 200
        assert resp_pdf['Content-Type'] == 'application/pdf'
        assert resp_pdf.content.startswith(b'%PDF')

    _run_rolled_back('centro_esperanza', _body)


def test_hu52_extracto_bancario_20_anios_pdf_excel_csv():
    def _body():
        paciente = Paciente.objects.select_related('usuario').last()
        cuenta = FinanzasService.asegurar_cuenta(paciente)

        # Insertar movimientos a lo largo de 20 años (2007 a 2026)
        for anio in range(2007, 2027):
            dt_cargo = timezone.make_aware(datetime(anio, 3, 15, 9, 0))
            dt_abono = timezone.make_aware(datetime(anio, 3, 15, 10, 0))
            MovimientoFinanciero.objects.create(
                cuenta=cuenta,
                tipo='CARGO',
                concepto=f'Sesión histórica {anio}',
                numero_documento=f'CITA-{anio}',
                debe=Decimal('200.00'),
                haber=Decimal('0.00'),
                fecha_movimiento=dt_cargo,
            )
            MovimientoFinanciero.objects.create(
                cuenta=cuenta,
                tipo='ABONO',
                concepto=f'Pago histórico {anio}',
                metodo_pago='TRANSFERENCIA',
                numero_documento=f'REC-{anio}-000001',
                debe=Decimal('0.00'),
                haber=Decimal('150.00'),
                fecha_movimiento=dt_abono,
            )

        ext = FinanzasService.obtener_extracto_bancario(
            paciente_id=paciente.id,
            fecha_desde=date(2007, 1, 1),
            fecha_hasta=date(2026, 12, 31),
            page=1,
            page_size=10,
        )
        assert ext['resumen']['total_registros'] >= 40
        assert len(ext['movimientos']) == 10
        assert len(ext['resumen_anual']) >= 20
        assert ext['movimientos'][0]['debe'] == 200.0
        assert ext['movimientos'][1]['haber'] == 150.0

        # Validar exportación PDF multipágina
        meta_pdf, rows_pdf = FinanzasService.iterar_extracto_bancario(
            paciente_id=paciente.id,
            fecha_desde=date(2007, 1, 1),
            fecha_hasta=date(2026, 12, 31),
        )
        pdf_resp = generar_extracto_bancario_pdf(meta_pdf, rows_pdf, tenant_name='Centro Esperanza')
        assert pdf_resp.status_code == 200 and pdf_resp.content.startswith(b'%PDF')

        # Validar exportación Excel streaming (write_only)
        meta_xlsx, rows_xlsx = FinanzasService.iterar_extracto_bancario(
            paciente_id=paciente.id,
            fecha_desde=date(2007, 1, 1),
            fecha_hasta=date(2026, 12, 31),
        )
        xlsx_resp = generar_extracto_bancario_excel(meta_xlsx, rows_xlsx, tenant_name='Centro Esperanza')
        assert xlsx_resp.status_code == 200 and xlsx_resp.content.startswith(b'PK\x03\x04')

        # Validar exportación CSV streaming
        meta_csv, rows_csv = FinanzasService.iterar_extracto_bancario(
            paciente_id=paciente.id,
            fecha_desde=date(2007, 1, 1),
            fecha_hasta=date(2026, 12, 31),
        )
        csv_resp = generar_extracto_bancario_csv(meta_csv, rows_csv)
        csv_content = b''.join(csv_resp.streaming_content).decode('utf-8')
        assert 'Saldo Acumulado' in csv_content and 'Sesión histórica 2007' in csv_content

    _run_rolled_back('centro_esperanza', _body)


def test_hu54_liquidacion_honorarios_antidoble_pago_y_boleta_pdf():
    def _body():
        paciente = Paciente.objects.first()
        psicologo = Psicologo.objects.first()

        for dia in range(1, 6):
            Cita.objects.create(
                paciente=paciente,
                psicologo=psicologo,
                fecha=date(2025, 2, dia),
                hora_inicio=time(14, 0),
                hora_fin=time(15, 0),
                modalidad='VIRTUAL',
                estado='REALIZADA',
                costo=Decimal('180.00'),
            )

        # HU-54 (a): 5 x 180 = 900.00 bruto, 30% = 270.00, neto = 630.00
        liq = FinanzasService.generar_liquidacion(
            psicologo=psicologo,
            fecha_inicio=date(2025, 2, 1),
            fecha_fin=date(2025, 2, 28),
            porcentaje_comision_centro=Decimal('30.00'),
        )
        assert liq.total_sesiones == 5
        assert liq.monto_bruto == Decimal('900.00')
        assert liq.comision_centro == Decimal('270.00')
        assert liq.monto_neto_psicologo == Decimal('630.00')
        assert liq.estado == 'GENERADA'

        # HU-54 (b): Evitar doble pago en fechas solapadas
        raised = False
        try:
            FinanzasService.generar_liquidacion(
                psicologo=psicologo,
                fecha_inicio=date(2025, 2, 1),
                fecha_fin=date(2025, 2, 28),
            )
        except ValueError:
            raised = True
        assert raised, "Debió evitar doble liquidación en fechas solapadas"

        # HU-54 (c): Marcar como PAGADA y generar Boleta PDF
        liq_pagada = FinanzasService.marcar_liquidacion_pagada(liq.id, 'TRANS-BNB-998877')
        assert liq_pagada.estado == 'PAGADA'
        boleta_resp = generar_boleta_liquidacion_pdf(liq_pagada, tenant_name='Centro Esperanza')
        assert boleta_resp.status_code == 200 and boleta_resp.content.startswith(b'%PDF')

    _run_rolled_back('centro_esperanza', _body)


if __name__ == '__main__':
    test_hu52_cobro_atomico_validaciones_y_recibo_pdf()
    print('[OK] HU-52: Cobro atómico, validaciones de saldo y Recibo PDF')
    test_hu52_extracto_bancario_20_anios_pdf_excel_csv()
    print('[OK] HU-52: Extracto Bancario 20 años (running balance, subtotales, PDF, Excel streaming, CSV)')
    test_hu54_liquidacion_honorarios_antidoble_pago_y_boleta_pdf()
    print('[OK] HU-54: Liquidación de honorarios (70/30), anti-doble pago y Boleta PDF')
    print('ALL SPRINT 4 FASE 1 TESTS PASSED [OK]')
