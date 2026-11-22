# ==============================================================================
# COMANDO: python manage.py seed_historico_sprint4
# DESCRIPCIÓN: Pobla datos históricos realistas de MÍNIMO 24 MESES (2 años)
#              para estadísticas gerenciales (HU-53), y además genera un
#              historial extendido de 20 AÑOS en el libro mayor para probar el
#              Extracto Histórico Tipo Bancario (HU-52).
# ==============================================================================
import random
from calendar import monthrange
from datetime import date, datetime, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_tenants.utils import get_public_schema_name, schema_context

from agenda.models import Cita
from clinica.models import Paciente, Psicologo
from finanzas.models import CuentaPaciente, PagoConsulta, MovimientoFinanciero, LiquidacionHonorario
from finanzas.services import FinanzasService
from tenants.models import Tenant


METODOS = ['EFECTIVO', 'QR_BANCARIO', 'TRANSFERENCIA', 'TARJETA_STRIPE']
COSTOS = [Decimal('150.00'), Decimal('180.00'), Decimal('200.00'), Decimal('250.00')]


def _subtract_months(ref: date, months: int) -> tuple[int, int]:
    y = ref.year
    m = ref.month - months
    while m <= 0:
        m += 12
        y -= 1
    return y, m


class Command(BaseCommand):
    help = 'Pobla historial financiero/clínico de >= 24 meses (2 años) + extracto de 20 años para Sprint 4.'

    def add_arguments(self, parser):
        parser.add_argument('--tenant', type=str, default=None, help='Schema name de un tenant específico (opcional).')
        parser.add_argument('--meses', type=int, default=24, help='Cantidad de meses de estadísticas a poblar (mínimo 24).')
        parser.add_argument('--anios-extracto', type=int, default=20, help='Años de historial para el extracto tipo banco (default 20).')

    def handle(self, *args, **options):
        meses = max(24, int(options['meses']))
        anios_extracto = max(2, min(20, int(options['anios_extracto'])))
        tenant_filter = options.get('tenant')

        tenants_qs = Tenant.objects.exclude(schema_name=get_public_schema_name()).filter(activo=True)
        if tenant_filter:
            tenants_qs = tenants_qs.filter(schema_name=tenant_filter)

        tenants = list(tenants_qs)
        if not tenants:
            self.stdout.write(self.style.WARNING('No se encontraron tenants activos para poblar.'))
            return

        hoy = timezone.localdate()

        for tenant in tenants:
            self.stdout.write(f"==> Poblando historial Sprint 4 ({meses} meses + extracto {anios_extracto} años) en: {tenant.schema_name}")
            with schema_context(tenant.schema_name):
                self._poblar_tenant(tenant.schema_name, hoy, meses, anios_extracto)

        self.stdout.write(self.style.SUCCESS('==> [OK] seed_historico_sprint4 finalizado exitosamente.'))

    def _poblar_tenant(self, schema_name: str, hoy: date, meses: int, anios_extracto: int):
        rng = random.Random(f"sprint4-{schema_name}")
        pacientes = list(Paciente.objects.select_related('usuario').all())
        psicologos = list(Psicologo.objects.filter(activo=True).select_related('usuario'))
        if not pacientes or not psicologos:
            self.stdout.write(self.style.WARNING(f"  [SKIP] {schema_name} sin pacientes o psicólogos."))
            return

        # Idempotencia: si ya hay >= 20 liquidaciones históricas, saltar
        if LiquidacionHonorario.objects.count() >= 20:
            self.stdout.write(f"  [SKIP] {schema_name} ya tiene historial financiero sembrado.")
            return

        total_citas = 0
        total_pagos = 0
        total_liqs = 0

        # 1. Poblar 24+ meses de citas, cobros y liquidaciones mensuales
        for offset in range(meses - 1, -1, -1):
            anio, mes = _subtract_months(hoy, offset)
            ultimo_dia = monthrange(anio, mes)[1]
            dia_tope = min(ultimo_dia, hoy.day) if (anio == hoy.year and mes == hoy.month) else ultimo_dia

            # Entre 8 y 14 sesiones por mes (tendencia creciente año a año para YoY realista)
            factor_crecimiento = 1.0 if offset >= 12 else 1.25
            n_sesiones = int(rng.randint(8, 12) * factor_crecimiento)

            for idx in range(n_sesiones):
                pac = rng.choice(pacientes)
                psico = rng.choice(psicologos)
                dia = rng.randint(1, max(1, dia_tope))
                hora_h = rng.randint(8, 17)
                estado_roll = rng.random()
                if estado_roll < 0.80:
                    estado = 'REALIZADA'
                elif estado_roll < 0.92:
                    estado = 'INASISTENCIA'
                else:
                    estado = 'CANCELADA'

                costo = rng.choice(COSTOS)
                modalidad = 'VIRTUAL' if rng.random() < 0.45 else 'PRESENCIAL'
                fecha_cita = date(anio, mes, dia)

                cita = Cita.objects.create(
                    paciente=pac,
                    psicologo=psico,
                    fecha=fecha_cita,
                    hora_inicio=time(hora_h, 0),
                    hora_fin=time(hora_h + 1, 0),
                    modalidad=modalidad,
                    estado=estado,
                    motivo_consulta=f"Seguimiento terapéutico histórico {anio}-{mes:02d}",
                    costo=costo,
                )
                total_citas += 1

                if estado == 'REALIZADA':
                    dt_cita = timezone.make_aware(datetime(anio, mes, dia, hora_h, 0))
                    FinanzasService.registrar_cargo_cita(cita, fecha_movimiento=dt_cita)
                    # 88% pagado (deja ~12% de cartera por cobrar realista)
                    if rng.random() < 0.88:
                        metodo = rng.choices(METODOS, weights=[35, 35, 20, 10])[0]
                        dt_pago = timezone.make_aware(datetime(anio, mes, dia, min(20, hora_h + 1), 15))
                        try:
                            FinanzasService.registrar_pago(
                                paciente=pac,
                                cita=cita,
                                monto=costo,
                                metodo_pago=metodo,
                                referencia_externa=f"REF-{anio}{mes:02d}-{idx:03d}",
                                fecha_pago=dt_pago,
                            )
                            total_pagos += 1
                        except ValueError:
                            pass

            # Liquidación mensual por cada psicólogo con sesiones realizadas en ese mes
            f_ini = date(anio, mes, 1)
            f_fin = date(anio, mes, ultimo_dia)
            for psico in psicologos:
                try:
                    liq = FinanzasService.generar_liquidacion(
                        psicologo=psico,
                        fecha_inicio=f_ini,
                        fecha_fin=f_fin,
                        porcentaje_comision_centro=Decimal('30.00'),
                        observaciones=f"Liquidación mensual automática {anio}-{mes:02d}",
                    )
                    if offset >= 1:  # Meses pasados ya pagados, mes actual queda GENERADA
                        FinanzasService.marcar_liquidacion_pagada(
                            liq.id,
                            referencia_bancaria=f"BNB-{anio}{mes:02d}-{str(psico.id)[:6].upper()}",
                        )
                    total_liqs += 1
                except ValueError:
                    pass

        # 2. Historial extendido de 20 años para el primer paciente (Extracto Tipo Banco)
        pac_demo = pacientes[0]
        cuenta_demo = FinanzasService.asegurar_cuenta(pac_demo)
        anio_inicio_ext = hoy.year - anios_extracto + 1
        movs_bulk = []
        total_cargo_ext = Decimal('0.00')
        total_abono_ext = Decimal('0.00')

        for anio_ext in range(anio_inicio_ext, hoy.year - 1):
            # 6 sesiones y 6 pagos por año (18 años previos * 12 = 216 movimientos + 2 años recientes)
            for mes_ext in (2, 4, 6, 8, 10, 12):
                monto = rng.choice(COSTOS)
                dt_c = timezone.make_aware(datetime(anio_ext, mes_ext, 10, 9, 0))
                dt_a = timezone.make_aware(datetime(anio_ext, mes_ext, 10, 10, 30))
                metodo = rng.choice(METODOS)
                movs_bulk.append(MovimientoFinanciero(
                    cuenta=cuenta_demo,
                    tipo='CARGO',
                    concepto=f"Consulta psicológica histórica ({anio_ext}-{mes_ext:02d})",
                    numero_documento=f"HIS-{anio_ext}{mes_ext:02d}",
                    debe=monto,
                    haber=Decimal('0.00'),
                    fecha_movimiento=dt_c,
                ))
                movs_bulk.append(MovimientoFinanciero(
                    cuenta=cuenta_demo,
                    tipo='ABONO',
                    concepto=f"Pago histórico verificado ({metodo}) — {anio_ext}-{mes_ext:02d}",
                    metodo_pago=metodo,
                    numero_documento=f"REC-{anio_ext}-{mes_ext:04d}01",
                    debe=Decimal('0.00'),
                    haber=monto,
                    fecha_movimiento=dt_a,
                ))
                total_cargo_ext += monto
                total_abono_ext += monto

        if movs_bulk:
            MovimientoFinanciero.objects.bulk_create(movs_bulk)
            cuenta_demo.refresh_from_db()
            cuenta_demo.total_cargado += total_cargo_ext
            cuenta_demo.total_pagado += total_abono_ext
            cuenta_demo.saldo_pendiente = cuenta_demo.total_cargado - cuenta_demo.total_pagado
            cuenta_demo.save(update_fields=['total_cargado', 'total_pagado', 'saldo_pendiente', 'ultima_actualizacion'])

        self.stdout.write(
            f"  [OK] {schema_name}: {total_citas} citas (24m), {total_pagos} pagos, "
            f"{total_liqs} liquidaciones, {len(movs_bulk)} movimientos históricos extra (20 años)."
        )
