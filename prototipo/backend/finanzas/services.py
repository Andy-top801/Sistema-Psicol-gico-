# ==============================================================================
# MÓDULO: finanzas/services.py
# CASOS DE USO: CU26 (HU-52 Cobros y Extracto Bancario 20 años,
#                     HU-54 Liquidación de Honorarios a Psicólogos)
# DESCRIPCIÓN: Lógica transaccional atómica (select_for_update + transaction.atomic)
#              para cobros, libro mayor cronológico con saldo acumulado SQL Window,
#              y liquidación de honorarios con prevención de doble pago.
# ==============================================================================
import secrets
from calendar import monthrange
from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db import connection, transaction
from django.db.models import F, Q, Sum, Count, Value, Window, DecimalField
from django.db.models.functions import Coalesce, TruncMonth, TruncYear
from django.utils import timezone

from agenda.models import Cita
from audit.services import log_event
from clinica.models import Paciente, Psicologo
from .models import (
    CuentaPaciente,
    PagoConsulta,
    MovimientoFinanciero,
    LiquidacionHonorario,
    DetalleLiquidacionCita,
    PlanPagoTerapeutico,
    CuotaAmortizacion,
)

TWOPLACES = Decimal('0.01')
FOURPLACES = Decimal('0.0001')
TASA_OFICIAL_USD_BOB = Decimal('6.9600')
MAX_EXTRACTO_DIAS = 366 * 20  # Hasta 20 años de historial tipo extracto bancario


def _q2(val: Decimal | float | int | str) -> Decimal:
    return Decimal(str(val)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def _add_months(ref: date, months: int) -> date:
    total_m = (ref.month - 1) + months
    anio = ref.year + total_m // 12
    mes = (total_m % 12) + 1
    dia = min(ref.day, monthrange(anio, mes)[1])
    return date(anio, mes, dia)


def _to_aware_start(d: date | datetime) -> datetime:
    if isinstance(d, datetime):
        return timezone.make_aware(d) if timezone.is_naive(d) else d
    return timezone.make_aware(datetime.combine(d, time.min))


def _to_aware_end(d: date | datetime) -> datetime:
    if isinstance(d, datetime):
        return timezone.make_aware(d) if timezone.is_naive(d) else d
    return timezone.make_aware(datetime.combine(d, time.max))


class FinanzasService:
    """Servicio transaccional central para Caja Clínica, Extractos y Honorarios."""

    @classmethod
    def asegurar_cuenta(cls, paciente: Paciente) -> CuentaPaciente:
        cuenta, _ = CuentaPaciente.objects.get_or_create(
            paciente=paciente,
            defaults={'moneda': 'BOB'},
        )
        return cuenta

    @classmethod
    @transaction.atomic
    def registrar_cargo_cita(
        cls,
        cita: Cita,
        concepto: str | None = None,
        fecha_movimiento: datetime | None = None,
    ) -> MovimientoFinanciero | None:
        """
        Registra de forma idempotente el cargo (Debe) de una cita con costo > 0
        en la cuenta del paciente.
        """
        costo = _q2(cita.costo or Decimal('0.00'))
        if costo <= Decimal('0.00'):
            return None

        existente = MovimientoFinanciero.objects.filter(cita=cita, tipo='CARGO').first()
        if existente:
            return existente

        cuenta = cls.asegurar_cuenta(cita.paciente)
        cuenta = CuentaPaciente.objects.select_for_update().get(pk=cuenta.pk)

        psico_nom = f"Lic. {cita.psicologo.usuario.nombre} {cita.psicologo.usuario.apellido}".strip()
        glosa = concepto or f"Consulta psicológica ({cita.modalidad}) — {psico_nom} [{cita.fecha.isoformat()}]"
        fecha_mov = fecha_movimiento or _to_aware_start(datetime.combine(cita.fecha, cita.hora_inicio))

        mov = MovimientoFinanciero.objects.create(
            cuenta=cuenta,
            cita=cita,
            tipo='CARGO',
            concepto=glosa[:255],
            numero_documento=f"CITA-{cita.fecha.strftime('%Y%m%d')}-{str(cita.id)[:6].upper()}",
            debe=costo,
            haber=Decimal('0.00'),
            fecha_movimiento=fecha_mov,
        )

        cuenta.total_cargado = _q2(cuenta.total_cargado + costo)
        cuenta.saldo_pendiente = _q2(cuenta.total_cargado - cuenta.total_pagado)
        cuenta.save(update_fields=['total_cargado', 'saldo_pendiente', 'ultima_actualizacion'])
        return mov

    @classmethod
    def sincronizar_cargos_paciente(cls, paciente: Paciente) -> CuentaPaciente:
        """Asegura que todas las citas facturables del paciente estén cargadas en su cuenta."""
        citas_sin_cargo = (
            Cita.objects.filter(paciente=paciente, costo__gt=0)
            .exclude(estado='CANCELADA')
            .exclude(movimientos_financieros__tipo='CARGO')
            .select_related('psicologo__usuario', 'paciente')
        )
        for cita in citas_sin_cargo:
            cls.registrar_cargo_cita(cita)
        return cls.asegurar_cuenta(paciente)

    @classmethod
    def _siguiente_numero_recibo(cls, anio: int) -> str:
        prefix = f"REC-{anio}-"
        ultimo = (
            PagoConsulta.objects.select_for_update()
            .filter(numero_recibo__startswith=prefix)
            .order_by('-numero_recibo')
            .values_list('numero_recibo', flat=True)
            .first()
        )
        correlativo = 1
        if ultimo:
            try:
                correlativo = int(ultimo.split('-')[-1]) + 1
            except (ValueError, IndexError):
                correlativo = PagoConsulta.objects.filter(numero_recibo__startswith=prefix).count() + 1
        return f"{prefix}{correlativo:06d}"

    @classmethod
    def convertir_a_bob(
        cls,
        monto_origen,
        moneda: str = 'BOB',
        tasa: Decimal = TASA_OFICIAL_USD_BOB,
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        CU26A-paso 5: convertir_a_bob(monto, moneda, tasa_oficial=6.96)
        Retorna (monto_bob_equivalente, ajuste_redondeo, tasa_aplicada) con ROUND_HALF_UP.
        """
        mon = (moneda or 'BOB').upper().strip()
        monto_orig_dec = _q2(monto_origen)
        if monto_orig_dec <= Decimal('0.00'):
            raise ValueError('El monto del cobro debe ser mayor a 0.00.')
        if mon == 'BOB':
            return monto_orig_dec, Decimal('0.0000'), Decimal('1.0000')
        if mon == 'USD':
            tasa_dec = Decimal(str(tasa or TASA_OFICIAL_USD_BOB)).quantize(FOURPLACES, rounding=ROUND_HALF_UP)
            exacto = monto_orig_dec * tasa_dec
            redondeado = exacto.quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            ajuste = (redondeado - exacto).quantize(FOURPLACES, rounding=ROUND_HALF_UP)
            return redondeado, ajuste, tasa_dec
        raise ValueError(f"Moneda '{moneda}' no soportada. Use BOB o USD.")

    @classmethod
    def generar_tabla_amortizacion(
        cls,
        monto_total,
        numero_cuotas: int,
        tasa_interes_anual=Decimal('12.00'),
        porcentaje_seguro=Decimal('1.50'),
        fecha_inicio: date | None = None,
    ) -> list[dict]:
        """
        Genera el cronograma cuota por cuota (capital amortizado, interés/comisión,
        seguro asistencial y saldo insoluto), absorbiendo cualquier centavo residual en la
        última cuota para cerrar exactamente en 0.00.
        """
        capital_total = _q2(monto_total)
        cuotas_n = max(1, int(numero_cuotas))
        saldo = capital_total
        capital_base = (capital_total / Decimal(cuotas_n)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        tasa_mensual = (Decimal(str(tasa_interes_anual)) / Decimal('100')) / Decimal('12')
        seguro_tasa = Decimal(str(porcentaje_seguro)) / Decimal('100')
        f_ini = fecha_inicio or timezone.localdate()
        cronograma = []

        for idx in range(1, cuotas_n + 1):
            capital = saldo if idx == cuotas_n else capital_base
            interes = (saldo * tasa_mensual).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            seguro = (saldo * seguro_tasa).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            saldo_nuevo = max(Decimal('0.00'), _q2(saldo - capital))
            total_cuota = _q2(capital + interes + seguro)
            cronograma.append({
                'numero_cuota': idx,
                'fecha_vencimiento': _add_months(f_ini, idx - 1),
                'capital_amortizado': capital,
                'interes_o_comision': interes,
                'seguro_asistencial': seguro,
                'monto_total_cuota': total_cuota,
                'saldo_insoluto': saldo_nuevo,
            })
            saldo = saldo_nuevo
        return cronograma

    @classmethod
    @transaction.atomic
    def crear_plan_amortizacion(
        cls,
        paciente: Paciente,
        nombre_plan: str,
        monto_total,
        numero_cuotas: int = 6,
        tasa_interes_anual=Decimal('12.00'),
        porcentaje_seguro=Decimal('1.50'),
        moneda: str = 'BOB',
        sesiones_incluidas: int = 6,
        fecha_inicio: date | None = None,
    ) -> PlanPagoTerapeutico:
        """Crea un PlanPagoTerapeutico, sus CuotaAmortizacion y el cargo contable."""
        mon = (moneda or 'BOB').upper().strip()
        monto_dec = _q2(monto_total)
        if monto_dec <= Decimal('0.00'):
            raise ValueError('El monto total del plan debe ser mayor a 0.00.')
        monto_bob, _, _ = cls.convertir_a_bob(monto_dec, mon)
        f_ini = fecha_inicio or timezone.localdate()

        cronograma = cls.generar_tabla_amortizacion(
            monto_total=monto_bob,
            numero_cuotas=numero_cuotas,
            tasa_interes_anual=tasa_interes_anual,
            porcentaje_seguro=porcentaje_seguro,
            fecha_inicio=f_ini,
        )

        plan = PlanPagoTerapeutico.objects.create(
            paciente=paciente,
            nombre_plan=nombre_plan.strip()[:160],
            sesiones_incluidas=max(1, int(sesiones_incluidas)),
            monto_total=monto_bob,
            moneda='BOB',
            tasa_interes_anual=_q2(tasa_interes_anual),
            porcentaje_seguro=_q2(porcentaje_seguro),
            numero_cuotas=max(1, int(numero_cuotas)),
            saldo_insoluto=monto_bob,
            estado='ACTIVO',
            fecha_inicio=f_ini,
        )
        cuotas_objs = [
            CuotaAmortizacion(
                plan=plan,
                numero_cuota=row['numero_cuota'],
                fecha_vencimiento=row['fecha_vencimiento'],
                capital_amortizado=row['capital_amortizado'],
                interes_o_comision=row['interes_o_comision'],
                seguro_asistencial=row['seguro_asistencial'],
                monto_total_cuota=row['monto_total_cuota'],
                saldo_insoluto=row['saldo_insoluto'],
                estado='PENDIENTE',
            )
            for row in cronograma
        ]
        CuotaAmortizacion.objects.bulk_create(cuotas_objs)

        total_plan_con_cargos = _q2(sum((row['monto_total_cuota'] for row in cronograma), Decimal('0.00')))
        cuenta = cls.asegurar_cuenta(paciente)
        cuenta = CuentaPaciente.objects.select_for_update().get(pk=cuenta.pk)
        MovimientoFinanciero.objects.create(
            cuenta=cuenta,
            tipo='CARGO',
            concepto=f"Plan Terapéutico ({plan.numero_cuotas} cuotas): {plan.nombre_plan}"[:255],
            numero_documento=f"PLAN-{str(plan.id)[:8].upper()}",
            debe=total_plan_con_cargos,
            haber=Decimal('0.00'),
            fecha_movimiento=_to_aware_start(f_ini),
        )
        cuenta.total_cargado = _q2(cuenta.total_cargado + total_plan_con_cargos)
        cuenta.saldo_pendiente = _q2(cuenta.total_cargado - cuenta.total_pagado)
        cuenta.save(update_fields=['total_cargado', 'saldo_pendiente', 'ultima_actualizacion'])
        return plan

    @classmethod
    @transaction.atomic
    def registrar_pago_cuota(
        cls,
        cuota_id,
        monto=None,
        moneda: str = 'BOB',
        metodo_pago: str = 'QR_BANCARIO',
        usuario=None,
        referencia_externa: str = '',
        tasa_cambio: Decimal = TASA_OFICIAL_USD_BOB,
    ) -> dict:
        """
        Flujo exacto del Diagrama de Secuencia CU26-A (CTR_PagosAmortizacion — Pasos 3 a 15).
        """
        # CU26A-paso 3: CTR -> CUOTA : bloquear_cuota_para_pago(cuota_id) [SELECT FOR UPDATE]
        cuota = CuotaAmortizacion.objects.select_for_update().select_related('plan__paciente__usuario').get(pk=cuota_id)
        # CU26A-paso 4: CUOTA --> CTR : cuota_info(estado, monto_total_cuota, plan_id) [retorno]
        plan = PlanPagoTerapeutico.objects.select_for_update().get(pk=cuota.plan_id)

        mon = (moneda or 'BOB').upper().strip()
        if monto is None:
            if mon == 'USD':
                tasa_dec = Decimal(str(tasa_cambio or TASA_OFICIAL_USD_BOB)).quantize(FOURPLACES, rounding=ROUND_HALF_UP)
                monto_eval = (cuota.monto_total_cuota / tasa_dec).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            else:
                monto_eval = cuota.monto_total_cuota
        else:
            monto_eval = _q2(monto)
        # CU26A-paso 14: else cuota_ya_pagada o monto_invalido -> HTTP 400 Bad Request
        if cuota.estado not in ('PENDIENTE', 'MORA') or monto_eval <= Decimal('0.00'):
            raise ValueError('Cuota no elegible o monto inválido.')

        # CU26A-paso 5: CTR -> CTR : convertir_a_bob(monto, moneda, tasa_oficial=6.96)
        monto_bob, _, _ = cls.convertir_a_bob(monto_eval, moneda, tasa=tasa_cambio)
        if monto_bob + Decimal('0.50') < cuota.monto_total_cuota:
            raise ValueError(
                f'El equivalente en Bs. ({monto_bob}) es inferior al valor exigible de la cuota (Bs. {cuota.monto_total_cuota}).'
            )

        # CU26A-paso 6-7: CTR -> PAGO : registrar_transaccion(monto_origen, monto_bob, ajuste_redondeo)
        pago = cls.registrar_pago(
            paciente=plan.paciente,
            monto=monto_eval,
            moneda_origen=moneda,
            tipo_cambio=tasa_cambio,
            cuota=cuota,
            metodo_pago=metodo_pago,
            usuario=usuario,
            referencia_externa=referencia_externa,
            observaciones=f"Amortización cuota {cuota.numero_cuota}/{plan.numero_cuotas} — {plan.nombre_plan}",
            permitir_abono_adelantado=True,
        )

        # CU26A-paso 8-9: CTR -> CUOTA : marcar_pagada(cuota_id) -> estado='PAGADA'
        cuota.estado = 'PAGADA'
        cuota.fecha_pago = timezone.now()
        cuota.save(update_fields=['estado', 'fecha_pago'])

        # CU26A-paso 10-11: CTR -> PLAN : calcular_saldo_restante(plan_id) -> saldo_insoluto, lista_cuotas[]
        saldo_restante = plan.calcular_saldo_restante()
        plan.saldo_insoluto = saldo_restante
        if saldo_restante <= Decimal('0.00'):
            plan.estado = 'PAGADO'
        plan.save(update_fields=['saldo_insoluto', 'estado'])

        return {
            'pago': pago,
            'cuota': cuota,
            'plan': plan,
            'extracto_amortizacion': cls.obtener_extracto_paciente_completo(plan.paciente_id),
        }

    @classmethod
    def obtener_extracto_paciente_completo(cls, paciente_id) -> dict:
        """Retorna todos los planes y cuotas de amortización del paciente."""
        planes = list(
            PlanPagoTerapeutico.objects.filter(paciente_id=paciente_id)
            .prefetch_related('cuotas')
            .order_by('-fecha_creacion')
        )
        planes_data = []
        saldo_total = Decimal('0.00')
        cuotas_pend = 0
        cuotas_pag = 0
        for pl in planes:
            cuotas_list = list(pl.cuotas.all().order_by('numero_cuota'))
            if pl.estado != 'ANULADO':
                saldo_total += pl.saldo_insoluto
            cuotas_pend += sum(1 for c in cuotas_list if c.estado != 'PAGADA')
            cuotas_pag += sum(1 for c in cuotas_list if c.estado == 'PAGADA')
            planes_data.append({
                'id': str(pl.id),
                'nombre_plan': pl.nombre_plan,
                'sesiones_incluidas': pl.sesiones_incluidas,
                'monto_total': float(pl.monto_total),
                'moneda': pl.moneda,
                'tasa_interes_anual': float(pl.tasa_interes_anual),
                'porcentaje_seguro': float(pl.porcentaje_seguro),
                'numero_cuotas': pl.numero_cuotas,
                'saldo_insoluto': float(pl.saldo_insoluto),
                'estado': pl.estado,
                'fecha_inicio': pl.fecha_inicio.isoformat(),
                'cuotas': [
                    {
                        'id': str(c.id),
                        'numero_cuota': c.numero_cuota,
                        'fecha_vencimiento': c.fecha_vencimiento.isoformat(),
                        'capital_amortizado': float(c.capital_amortizado),
                        'interes_o_comision': float(c.interes_o_comision),
                        'seguro_asistencial': float(c.seguro_asistencial),
                        'monto_total_cuota': float(c.monto_total_cuota),
                        'saldo_insoluto': float(c.saldo_insoluto),
                        'estado': c.estado,
                        'fecha_pago': timezone.localtime(c.fecha_pago).isoformat() if c.fecha_pago else None,
                    }
                    for c in cuotas_list
                ],
            })
        return {
            'paciente_id': str(paciente_id),
            'moneda': 'BOB',
            'tasa_oficial_usd_bob': float(TASA_OFICIAL_USD_BOB),
            'resumen_amortizacion': {
                'total_planes': len(planes_data),
                'saldo_insoluto_total': float(_q2(saldo_total)),
                'cuotas_pendientes': cuotas_pend,
                'cuotas_pagadas': cuotas_pag,
            },
            'planes': planes_data,
        }

    @classmethod
    @transaction.atomic
    def registrar_pago(
        cls,
        paciente: Paciente,
        monto,
        metodo_pago: str,
        usuario=None,
        cita: Cita | None = None,
        referencia_externa: str = '',
        observaciones: str = '',
        permitir_abono_adelantado: bool = False,
        fecha_pago: datetime | None = None,
        moneda_origen: str = 'BOB',
        tipo_cambio: Decimal = TASA_OFICIAL_USD_BOB,
        cuota: CuotaAmortizacion | None = None,
    ) -> PagoConsulta:
        """
        HU-52 / CU26A-paso 5..7: Registra un cobro en BOB o USD convertido exacto a Bs.
        de forma atómica (select_for_update + transaction.atomic), valida monto > 0,
        genera recibo correlativo y actualiza libro mayor + CE_AuditLog.
        """
        mon_norm = (moneda_origen or 'BOB').upper().strip()
        monto_orig_dec = _q2(monto)
        monto_dec, ajuste_redondeo, tasa_aplicada = cls.convertir_a_bob(
            monto_orig_dec, mon_norm, tasa=tipo_cambio
        )

        metodos_validos = {m[0] for m in PagoConsulta.METODO_PAGO_CHOICES}
        metodo_norm = (metodo_pago or '').upper().strip()
        if metodo_norm not in metodos_validos:
            raise ValueError(f"Método de pago inválido. Permitidos: {', '.join(sorted(metodos_validos))}.")

        if cita is not None:
            if cita.paciente_id != paciente.id:
                raise ValueError('La cita seleccionada no pertenece al paciente indicado.')
            cls.registrar_cargo_cita(cita)

        cuenta = cls.asegurar_cuenta(paciente)
        cuenta = CuentaPaciente.objects.select_for_update().get(pk=cuenta.pk)

        if not permitir_abono_adelantado:
            if cuenta.saldo_pendiente <= Decimal('0.00'):
                raise ValueError('El paciente no tiene saldo pendiente exigible (saldo = 0.00 Bs.).')
            if monto_dec > cuenta.saldo_pendiente:
                raise ValueError(
                    f'El monto (Bs. {monto_dec}) supera el saldo pendiente exigible (Bs. {cuenta.saldo_pendiente}).'
                )

        fecha_efectiva = fecha_pago or timezone.now()
        if timezone.is_naive(fecha_efectiva):
            fecha_efectiva = timezone.make_aware(fecha_efectiva)

        numero_recibo = cls._siguiente_numero_recibo(fecha_efectiva.year)
        codigo_verif = secrets.token_hex(8).upper()

        pago = PagoConsulta.objects.create(
            cuenta=cuenta,
            cita=cita,
            cuota=cuota,
            monto=monto_dec,
            moneda_origen=mon_norm,
            monto_origen=monto_orig_dec,
            tipo_cambio_aplicado=tasa_aplicada,
            ajuste_redondeo=ajuste_redondeo,
            metodo_pago=metodo_norm,
            numero_recibo=numero_recibo,
            codigo_verificacion=codigo_verif,
            referencia_externa=(referencia_externa or '')[:120],
            observaciones=observaciones or '',
            registrado_por=usuario,
            fecha_pago=fecha_efectiva,
        )

        concepto_abono = f"Pago recibido ({pago.get_metodo_pago_display()}, {mon_norm}) — Recibo {numero_recibo}"
        if cita is not None:
            concepto_abono += f" [Cita {cita.fecha.isoformat()}]"

        MovimientoFinanciero.objects.create(
            cuenta=cuenta,
            cita=cita,
            pago=pago,
            tipo='ABONO',
            concepto=concepto_abono[:255],
            metodo_pago=metodo_norm,
            numero_documento=numero_recibo,
            debe=Decimal('0.00'),
            haber=monto_dec,
            fecha_movimiento=fecha_efectiva,
        )

        cuenta.total_pagado = _q2(cuenta.total_pagado + monto_dec)
        cuenta.saldo_pendiente = max(Decimal('0.00'), _q2(cuenta.total_cargado - cuenta.total_pagado))
        cuenta.save(update_fields=['total_pagado', 'saldo_pendiente', 'ultima_actualizacion'])

        log_event(
            action='PAGO_CONSULTA_REGISTRADO',
            modulo='CU26_FINANZAS',
            tenant=getattr(connection, 'schema_name', None),
            user=getattr(usuario, 'email', None),
            user_id=str(usuario.id) if usuario else None,
            pago_id=str(pago.id),
            numero_recibo=numero_recibo,
            paciente_id=str(paciente.id),
            cita_id=str(cita.id) if cita else None,
            moneda_origen=mon_norm,
            monto_origen=float(monto_orig_dec),
            monto_bob=float(monto_dec),
            ajuste_redondeo=float(ajuste_redondeo),
            metodo_pago=metodo_norm,
            saldo_resultante_bob=float(cuenta.saldo_pendiente),
        )
        return pago

    # ==========================================================================
    # EXTRACTO HISTÓRICO TIPO BANCARIO (HASTA 20 AÑOS) — HU-52
    # ==========================================================================
    @classmethod
    def _build_extracto_queryset(
        cls,
        paciente_id=None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        metodo_pago: str | None = None,
        tipo: str | None = None,
    ):
        hoy = timezone.localdate()
        hasta = fecha_hasta or hoy
        desde = fecha_desde or (hasta - timedelta(days=365 * 20))

        if desde > hasta:
            raise ValueError('fecha_desde no puede ser mayor que fecha_hasta.')
        if (hasta - desde).days > MAX_EXTRACTO_DIAS:
            raise ValueError('El rango máximo permitido para el extracto histórico es de 20 años.')

        dt_desde = _to_aware_start(desde)
        dt_hasta = _to_aware_end(hasta)

        base_qs = MovimientoFinanciero.objects.select_related(
            'cuenta__paciente__usuario',
            'cita__psicologo__usuario',
            'pago',
        )
        if paciente_id:
            base_qs = base_qs.filter(cuenta__paciente_id=paciente_id)

        # Saldo inicial previo al rango solicitado
        prev_agg = base_qs.filter(fecha_movimiento__lt=dt_desde).aggregate(
            debe_prev=Coalesce(Sum('debe'), Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2)),
            haber_prev=Coalesce(Sum('haber'), Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2)),
        )
        saldo_inicial = _q2(prev_agg['debe_prev'] - prev_agg['haber_prev'])

        rango_qs = base_qs.filter(fecha_movimiento__gte=dt_desde, fecha_movimiento__lte=dt_hasta)
        if metodo_pago:
            rango_qs = rango_qs.filter(metodo_pago=metodo_pago.upper().strip())
        if tipo:
            rango_qs = rango_qs.filter(tipo=tipo.upper().strip())

        # Saldo acumulado (running balance) calculado en PostgreSQL con Window Function
        rango_annotated = rango_qs.annotate(
            variacion_acumulada=Window(
                expression=Sum(F('debe') - F('haber')),
                order_by=[F('fecha_movimiento').asc(), F('fecha_creacion').asc(), F('id').asc()],
            )
        ).order_by('fecha_movimiento', 'fecha_creacion', 'id')

        return {
            'desde': desde,
            'hasta': hasta,
            'saldo_inicial': saldo_inicial,
            'rango_qs': rango_qs,
            'rango_annotated': rango_annotated,
        }

    @classmethod
    def obtener_extracto_bancario(
        cls,
        paciente_id=None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        metodo_pago: str | None = None,
        tipo: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        """
        Retorna el extracto histórico tipo banco paginado + subtotales anuales y mensuales.
        """
        page = max(1, int(page or 1))
        page_size = max(1, min(500, int(page_size or 50)))

        ctx = cls._build_extracto_queryset(
            paciente_id=paciente_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            metodo_pago=metodo_pago,
            tipo=tipo,
        )
        rango_qs = ctx['rango_qs']
        rango_annotated = ctx['rango_annotated']
        saldo_inicial = ctx['saldo_inicial']

        totales = rango_qs.aggregate(
            total_debe=Coalesce(Sum('debe'), Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2)),
            total_haber=Coalesce(Sum('haber'), Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2)),
            total_registros=Count('id'),
        )
        total_registros = totales['total_registros']
        total_debe = _q2(totales['total_debe'])
        total_haber = _q2(totales['total_haber'])
        saldo_final = _q2(saldo_inicial + total_debe - total_haber)

        # Subtotales anuales (esencial para extractos de hasta 20 años)
        resumen_anual_qs = (
            rango_qs.annotate(anio=TruncYear('fecha_movimiento'))
            .values('anio')
            .annotate(
                movimientos=Count('id'),
                total_debe=Coalesce(Sum('debe'), Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2)),
                total_haber=Coalesce(Sum('haber'), Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2)),
            )
            .order_by('anio')
        )
        resumen_anual = [
            {
                'anio': row['anio'].year if row['anio'] else None,
                'movimientos': row['movimientos'],
                'total_debe': float(_q2(row['total_debe'])),
                'total_haber': float(_q2(row['total_haber'])),
                'variacion_neta': float(_q2(row['total_debe'] - row['total_haber'])),
            }
            for row in resumen_anual_qs
        ]

        # Subtotales mensuales
        resumen_mensual_qs = (
            rango_qs.annotate(periodo=TruncMonth('fecha_movimiento'))
            .values('periodo')
            .annotate(
                movimientos=Count('id'),
                total_debe=Coalesce(Sum('debe'), Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2)),
                total_haber=Coalesce(Sum('haber'), Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2)),
            )
            .order_by('periodo')
        )
        resumen_mensual = [
            {
                'periodo': row['periodo'].strftime('%Y-%m') if row['periodo'] else '',
                'movimientos': row['movimientos'],
                'total_debe': float(_q2(row['total_debe'])),
                'total_haber': float(_q2(row['total_haber'])),
            }
            for row in resumen_mensual_qs
        ]

        offset = (page - 1) * page_size
        slice_qs = rango_annotated[offset: offset + page_size]

        movimientos = []
        for m in slice_qs:
            pac = m.cuenta.paciente
            saldo_linea = _q2(saldo_inicial + (m.variacion_acumulada or Decimal('0.00')))
            movimientos.append({
                'id': str(m.id),
                'fecha': timezone.localtime(m.fecha_movimiento).strftime('%Y-%m-%d %H:%M'),
                'paciente_id': str(pac.id),
                'paciente_nombre': f"{pac.usuario.nombre} {pac.usuario.apellido}".strip(),
                'expediente': pac.codigo_expediente,
                'tipo': m.tipo,
                'numero_documento': m.numero_documento,
                'concepto': m.concepto,
                'metodo_pago': m.metodo_pago or '-',
                'debe': float(_q2(m.debe)),
                'haber': float(_q2(m.haber)),
                'saldo_acumulado': float(saldo_linea),
            })

        total_paginas = max(1, (total_registros + page_size - 1) // page_size)

        return {
            'moneda': 'BOB',
            'rango': {
                'fecha_desde': ctx['desde'].isoformat(),
                'fecha_hasta': ctx['hasta'].isoformat(),
                'anios_cubiertos': round((ctx['hasta'] - ctx['desde']).days / 365.25, 2),
            },
            'resumen': {
                'saldo_inicial': float(saldo_inicial),
                'total_debe': float(total_debe),
                'total_haber': float(total_haber),
                'saldo_final': float(saldo_final),
                'total_registros': total_registros,
            },
            'paginacion': {
                'page': page,
                'page_size': page_size,
                'total_registros': total_registros,
                'total_paginas': total_paginas,
            },
            'resumen_anual': resumen_anual,
            'resumen_mensual': resumen_mensual,
            'movimientos': movimientos,
        }

    @classmethod
    def iterar_extracto_bancario(
        cls,
        paciente_id=None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        metodo_pago: str | None = None,
        tipo: str | None = None,
    ):
        """
        Generador eficiente en memoria (chunk_size=1000) para exportar extractos
        de miles de filas a PDF multipágina, Excel write_only o CSV.
        Retorna (metadata_dict, generator_of_rows).
        """
        ctx = cls._build_extracto_queryset(
            paciente_id=paciente_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            metodo_pago=metodo_pago,
            tipo=tipo,
        )
        rango_qs = ctx['rango_qs']
        saldo_inicial = ctx['saldo_inicial']

        totales = rango_qs.aggregate(
            total_debe=Coalesce(Sum('debe'), Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2)),
            total_haber=Coalesce(Sum('haber'), Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2)),
            total_registros=Count('id'),
        )
        total_debe = _q2(totales['total_debe'])
        total_haber = _q2(totales['total_haber'])
        saldo_final = _q2(saldo_inicial + total_debe - total_haber)

        resumen_anual_qs = (
            rango_qs.annotate(anio=TruncYear('fecha_movimiento'))
            .values('anio')
            .annotate(
                movimientos=Count('id'),
                total_debe=Coalesce(Sum('debe'), Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2)),
                total_haber=Coalesce(Sum('haber'), Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2)),
            )
            .order_by('anio')
        )
        resumen_anual = [
            {
                'anio': row['anio'].year if row['anio'] else None,
                'movimientos': row['movimientos'],
                'total_debe': float(_q2(row['total_debe'])),
                'total_haber': float(_q2(row['total_haber'])),
                'variacion_neta': float(_q2(row['total_debe'] - row['total_haber'])),
            }
            for row in resumen_anual_qs
        ]

        paciente_label = 'Consolidado del Centro'
        if paciente_id:
            pac = Paciente.objects.select_related('usuario').filter(pk=paciente_id).first()
            if pac:
                paciente_label = f"{pac.usuario.nombre} {pac.usuario.apellido} ({pac.codigo_expediente})".strip()

        meta = {
            'paciente_label': paciente_label,
            'fecha_desde': ctx['desde'].isoformat(),
            'fecha_hasta': ctx['hasta'].isoformat(),
            'saldo_inicial': float(saldo_inicial),
            'total_debe': float(total_debe),
            'total_haber': float(total_haber),
            'saldo_final': float(saldo_final),
            'total_registros': totales['total_registros'],
            'resumen_anual': resumen_anual,
        }

        def _row_generator():
            saldo = saldo_inicial
            ordered_qs = rango_qs.order_by('fecha_movimiento', 'fecha_creacion', 'id')
            for m in ordered_qs.iterator(chunk_size=1000):
                saldo = _q2(saldo + m.debe - m.haber)
                pac = m.cuenta.paciente
                yield {
                    'fecha': timezone.localtime(m.fecha_movimiento).strftime('%Y-%m-%d %H:%M'),
                    'paciente': f"{pac.usuario.nombre} {pac.usuario.apellido}".strip(),
                    'expediente': pac.codigo_expediente,
                    'tipo': m.tipo,
                    'documento': m.numero_documento or '-',
                    'concepto': m.concepto,
                    'metodo_pago': m.metodo_pago or '-',
                    'debe': float(_q2(m.debe)),
                    'haber': float(_q2(m.haber)),
                    'saldo_acumulado': float(saldo),
                }

        return meta, _row_generator()

    # ==========================================================================
    # LIQUIDACIÓN PERIÓDICA DE HONORARIOS A PSICÓLOGOS (Bs.) — HU-54
    # ==========================================================================
    @classmethod
    def _siguiente_codigo_liquidacion(cls, anio: int) -> str:
        prefix = f"LIQ-{anio}-"
        ultimo = (
            LiquidacionHonorario.objects.select_for_update()
            .filter(codigo_liquidacion__startswith=prefix)
            .order_by('-codigo_liquidacion')
            .values_list('codigo_liquidacion', flat=True)
            .first()
        )
        correlativo = 1
        if ultimo:
            try:
                correlativo = int(ultimo.split('-')[-1]) + 1
            except (ValueError, IndexError):
                correlativo = LiquidacionHonorario.objects.filter(codigo_liquidacion__startswith=prefix).count() + 1
        return f"{prefix}{correlativo:05d}"

    @classmethod
    def citas_pendientes_liquidacion(cls, psicologo: Psicologo, fecha_inicio: date, fecha_fin: date):
        """
        Retorna las citas REALIZADAS en el periodo con costo > 0 que aún no
        fueron incluidas en una liquidación activa (no anulada).
        """
        citas_ya_liquidadas = DetalleLiquidacionCita.objects.filter(activo=True).values_list('cita_id', flat=True)
        return (
            Cita.objects.filter(
                psicologo=psicologo,
                estado='REALIZADA',
                costo__gt=0,
                fecha__gte=fecha_inicio,
                fecha__lte=fecha_fin,
            )
            .exclude(id__in=citas_ya_liquidadas)
            .select_related('paciente__usuario', 'psicologo__usuario')
            .order_by('fecha', 'hora_inicio')
        )

    @classmethod
    @transaction.atomic
    def generar_liquidacion(
        cls,
        psicologo: Psicologo,
        fecha_inicio: date,
        fecha_fin: date,
        usuario=None,
        porcentaje_comision_centro=Decimal('30.00'),
        observaciones: str = '',
    ) -> LiquidacionHonorario:
        """
        HU-54: Calcula y genera una liquidación en estado GENERADA evitando
        doble pago de sesiones ya liquidadas en fechas solapadas.
        """
        if fecha_fin < fecha_inicio:
            raise ValueError('La fecha de fin del periodo no puede ser anterior a la fecha de inicio.')

        pct = _q2(porcentaje_comision_centro)
        if pct < Decimal('0.00') or pct > Decimal('100.00'):
            raise ValueError('El porcentaje de comisión del centro debe estar entre 0 y 100.')

        citas = list(cls.citas_pendientes_liquidacion(psicologo, fecha_inicio, fecha_fin).select_for_update())
        if not citas:
            raise ValueError(
                'No existen sesiones REALIZADAS pendientes de liquidación para este psicólogo en el periodo seleccionado.'
            )

        monto_bruto = _q2(sum((_q2(c.costo) for c in citas), Decimal('0.00')))
        comision_centro = _q2((monto_bruto * pct) / Decimal('100.00'))
        monto_neto = _q2(monto_bruto - comision_centro)

        codigo = cls._siguiente_codigo_liquidacion(fecha_fin.year)
        liq = LiquidacionHonorario.objects.create(
            psicologo=psicologo,
            codigo_liquidacion=codigo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            total_sesiones=len(citas),
            monto_bruto=monto_bruto,
            porcentaje_comision_centro=pct,
            comision_centro=comision_centro,
            monto_neto_psicologo=monto_neto,
            estado='GENERADA',
            observaciones=observaciones or '',
            emitida_por=usuario,
        )

        detalles = []
        for c in citas:
            m_ses = _q2(c.costo)
            c_ses = _q2((m_ses * pct) / Decimal('100.00'))
            n_ses = _q2(m_ses - c_ses)
            detalles.append(
                DetalleLiquidacionCita(
                    liquidacion=liq,
                    cita=c,
                    monto_sesion=m_ses,
                    comision_sesion=c_ses,
                    neto_sesion=n_ses,
                    activo=True,
                )
            )
        DetalleLiquidacionCita.objects.bulk_create(detalles)

        log_event(
            action='LIQUIDACION_HONORARIO_GENERADA',
            modulo='CU26_FINANZAS',
            tenant=getattr(connection, 'schema_name', None),
            user=getattr(usuario, 'email', None),
            user_id=str(usuario.id) if usuario else None,
            liquidacion_id=str(liq.id),
            codigo_liquidacion=codigo,
            psicologo_id=str(psicologo.id),
            total_sesiones=len(citas),
            monto_bruto_bob=float(monto_bruto),
            comision_centro_bob=float(comision_centro),
            monto_neto_psicologo_bob=float(monto_neto),
        )
        return liq

    @classmethod
    @transaction.atomic
    def marcar_liquidacion_pagada(
        cls,
        liquidacion_id,
        referencia_bancaria: str,
        usuario=None,
    ) -> LiquidacionHonorario:
        liq = LiquidacionHonorario.objects.select_for_update().get(pk=liquidacion_id)
        if liq.estado == 'PAGADA':
            raise ValueError('Esta liquidación ya fue marcada como PAGADA.')
        if liq.estado == 'ANULADA':
            raise ValueError('No se puede pagar una liquidación ANULADA.')
        if not (referencia_bancaria or '').strip():
            raise ValueError('Debe proporcionar la referencia bancaria o comprobante de pago.')

        liq.estado = 'PAGADA'
        liq.referencia_bancaria = referencia_bancaria.strip()[:120]
        liq.pagada_por = usuario
        liq.fecha_pago = timezone.now()
        liq.save(update_fields=['estado', 'referencia_bancaria', 'pagada_por', 'fecha_pago'])

        log_event(
            action='LIQUIDACION_HONORARIO_PAGADA',
            modulo='CU26_FINANZAS',
            tenant=getattr(connection, 'schema_name', None),
            user=getattr(usuario, 'email', None),
            user_id=str(usuario.id) if usuario else None,
            liquidacion_id=str(liq.id),
            codigo_liquidacion=liq.codigo_liquidacion,
            referencia_bancaria=liq.referencia_bancaria,
            monto_neto_psicologo_bob=float(liq.monto_neto_psicologo),
        )
        return liq

    @classmethod
    @transaction.atomic
    def anular_liquidacion(cls, liquidacion_id, motivo: str = '', usuario=None) -> LiquidacionHonorario:
        liq = LiquidacionHonorario.objects.select_for_update().get(pk=liquidacion_id)
        if liq.estado == 'PAGADA':
            raise ValueError('No se puede anular una liquidación que ya fue PAGADA.')
        if liq.estado == 'ANULADA':
            return liq

        liq.estado = 'ANULADA'
        if motivo:
            liq.observaciones = f"{liq.observaciones}\n[ANULADA] {motivo}".strip()
        liq.save(update_fields=['estado', 'observaciones'])
        liq.detalles.update(activo=False)

        log_event(
            action='LIQUIDACION_HONORARIO_ANULADA',
            modulo='CU26_FINANZAS',
            tenant=getattr(connection, 'schema_name', None),
            user=getattr(usuario, 'email', None),
            user_id=str(usuario.id) if usuario else None,
            liquidacion_id=str(liq.id),
            codigo_liquidacion=liq.codigo_liquidacion,
            motivo=motivo,
        )
        return liq
