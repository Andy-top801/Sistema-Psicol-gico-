# ==============================================================================
# MÓDULO: finanzas/dashboard_service.py
# CASO DE USO: CU26 (HU-53) Dashboard Financiero y Gerencial Integral
# DESCRIPCIÓN: Calcula KPIs exactos en Bs. (Ingreso Bruto vs. Honorarios =
#              Margen Neto Real, Cartera por Cobrar y Morosidad %), series
#              mensuales de mínimo 2 años (24+ meses), comparativa interanual
#              (YoY), distribución por método/especialidad/psicólogo y catálogo
#              unificado de todos los reportes y consultas del sistema.
# ==============================================================================
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.db import connection
from django.db.models import Sum, Count, Q, DecimalField
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone

from agenda.models import Cita
from audit.services import log_event
from clinica.models import Paciente, Psicologo
from reportes.services import ReportEngine
from .models import (
    CuentaPaciente,
    PagoConsulta,
    LiquidacionHonorario,
    GastoFijoMensual,
    CalificacionCRM,
)
from .services import FinanzasService, TASA_OFICIAL_USD_BOB, _q2

DEC_FIELD = DecimalField(max_digits=14, decimal_places=2)


def _subtract_months(ref: date, months: int) -> date:
    y = ref.year
    m = ref.month - months
    while m <= 0:
        m += 12
        y -= 1
    return date(y, m, 1)


def _iter_months(start: date, end: date) -> list[str]:
    result = []
    cur = date(start.year, start.month, 1)
    lim = date(end.year, end.month, 1)
    while cur <= lim:
        result.append(cur.strftime('%Y-%m'))
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)
    return result


class DashboardFinancieroService:
    """Motor analítico multi-año (>= 24 meses) para el Dashboard Gerencial (HU-53)."""

    @classmethod
    def resolver_rango(cls, horizonte: str | None = '24m', fecha_desde: date | None = None, fecha_hasta: date | None = None):
        hoy = timezone.localdate()
        hasta = fecha_hasta or hoy
        if fecha_desde:
            desde = fecha_desde
        else:
            h = (horizonte or '24m').lower().strip()
            if h == '6m':
                desde = _subtract_months(hasta, 5)
            elif h == '12m':
                desde = _subtract_months(hasta, 11)
            elif h in ('36m', '3y'):
                desde = _subtract_months(hasta, 35)
            elif h == 'all':
                desde = date(hasta.year - 19, 1, 1)
            else:
                # Por defecto: mínimo 2 años completos (24 meses)
                desde = _subtract_months(hasta, 23)
        if desde > hasta:
            raise ValueError('fecha_desde no puede ser mayor que fecha_hasta.')
        return desde, hasta

    @classmethod
    def obtener_dashboard(
        cls,
        horizonte: str | None = '24m',
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        psicologo_id: str | None = None,
        especialidad_id: str | None = None,
        incluir_superadmin_reportes: bool = False,
    ) -> dict:
        desde, hasta = cls.resolver_rango(horizonte, fecha_desde, fecha_hasta)

        pagos_qs = PagoConsulta.objects.filter(
            anulado=False,
            fecha_pago__date__gte=desde,
            fecha_pago__date__lte=hasta,
        )
        liq_qs = LiquidacionHonorario.objects.exclude(estado='ANULADA').filter(
            fecha_fin__gte=desde,
            fecha_inicio__lte=hasta,
        )
        citas_qs = Cita.objects.filter(fecha__gte=desde, fecha__lte=hasta)

        if psicologo_id:
            pagos_qs = pagos_qs.filter(cita__psicologo_id=psicologo_id)
            liq_qs = liq_qs.filter(psicologo_id=psicologo_id)
            citas_qs = citas_qs.filter(psicologo_id=psicologo_id)

        if especialidad_id:
            pagos_qs = pagos_qs.filter(cita__psicologo__especialidades__id=especialidad_id)
            liq_qs = liq_qs.filter(psicologo__especialidades__id=especialidad_id)
            citas_qs = citas_qs.filter(psicologo__especialidades__id=especialidad_id)

        # 1. KPIs Principales en Bs.
        ingreso_bruto = pagos_qs.aggregate(
            total=Coalesce(Sum('monto'), Decimal('0.00'), output_field=DEC_FIELD)
        )['total']

        liq_agg = liq_qs.aggregate(
            honorarios=Coalesce(Sum('monto_neto_psicologo'), Decimal('0.00'), output_field=DEC_FIELD),
            comision=Coalesce(Sum('comision_centro'), Decimal('0.00'), output_field=DEC_FIELD),
            bruto_liq=Coalesce(Sum('monto_bruto'), Decimal('0.00'), output_field=DEC_FIELD),
        )
        honorarios_psicologos = liq_agg['honorarios']
        comision_retenida = liq_agg['comision']
        margen_neto_centro = ingreso_bruto - honorarios_psicologos

        cuentas_agg = CuentaPaciente.objects.aggregate(
            total_cargado=Coalesce(Sum('total_cargado'), Decimal('0.00'), output_field=DEC_FIELD),
            cartera=Coalesce(Sum('saldo_pendiente', filter=Q(saldo_pendiente__gt=0)), Decimal('0.00'), output_field=DEC_FIELD),
            pacientes_morosos=Count('id', filter=Q(saldo_pendiente__gt=0)),
            total_cuentas=Count('id'),
        )
        total_cargado_hist = cuentas_agg['total_cargado']
        cartera_por_cobrar = cuentas_agg['cartera']
        indice_morosidad_pct = (
            round((float(cartera_por_cobrar) / float(total_cargado_hist)) * 100.0, 2)
            if total_cargado_hist > 0 else 0.0
        )

        # 2. Serie Mensual Longitudinal (>= 24 meses)
        meses_keys = _iter_months(desde, hasta)
        pagos_mes = {
            row['mes'].strftime('%Y-%m'): float(row['total'])
            for row in pagos_qs.annotate(mes=TruncMonth('fecha_pago'))
            .values('mes')
            .annotate(total=Coalesce(Sum('monto'), Decimal('0.00'), output_field=DEC_FIELD))
            if row['mes']
        }
        liq_mes = {
            row['mes'].strftime('%Y-%m'): float(row['honorarios'])
            for row in liq_qs.annotate(mes=TruncMonth('fecha_inicio'))
            .values('mes')
            .annotate(honorarios=Coalesce(Sum('monto_neto_psicologo'), Decimal('0.00'), output_field=DEC_FIELD))
            if row['mes']
        }
        citas_mes = {
            row['mes'].strftime('%Y-%m'): row
            for row in citas_qs.annotate(mes=TruncMonth('fecha'))
            .values('mes')
            .annotate(
                totales=Count('id'),
                realizadas=Count('id', filter=Q(estado='REALIZADA')),
                inasistencias=Count('id', filter=Q(estado='INASISTENCIA')),
                canceladas=Count('id', filter=Q(estado='CANCELADA')),
            )
            if row['mes']
        }

        serie_mensual = []
        for mk in meses_keys:
            ing = round(pagos_mes.get(mk, 0.0), 2)
            hon = round(liq_mes.get(mk, 0.0), 2)
            cm = citas_mes.get(mk, {})
            realizadas = cm.get('realizadas', 0)
            inasist = cm.get('inasistencias', 0)
            cerradas = realizadas + inasist
            tasa_aus = round((inasist / cerradas) * 100.0, 2) if cerradas > 0 else 0.0
            serie_mensual.append({
                'periodo': mk,
                'ingreso_bruto': ing,
                'honorarios': hon,
                'margen_neto': round(ing - hon, 2),
                'citas_totales': cm.get('totales', 0),
                'citas_realizadas': realizadas,
                'inasistencias': inasist,
                'tasa_ausentismo_pct': tasa_aus,
            })

        # 3. Comparativa Interanual (YoY): últimos 12 meses vs. 12 meses previos
        fin_actual = hasta
        ini_actual = _subtract_months(fin_actual, 11)
        fin_anterior = ini_actual - timedelta(days=1)
        ini_anterior = _subtract_months(fin_anterior, 11)

        def _sum_ventana(d1: date, d2: date):
            ing = float(
                PagoConsulta.objects.filter(anulado=False, fecha_pago__date__gte=d1, fecha_pago__date__lte=d2)
                .aggregate(t=Coalesce(Sum('monto'), Decimal('0.00'), output_field=DEC_FIELD))['t']
            )
            hon = float(
                LiquidacionHonorario.objects.exclude(estado='ANULADA')
                .filter(fecha_fin__gte=d1, fecha_inicio__lte=d2)
                .aggregate(t=Coalesce(Sum('monto_neto_psicologo'), Decimal('0.00'), output_field=DEC_FIELD))['t']
            )
            cit = Cita.objects.filter(fecha__gte=d1, fecha__lte=d2, estado='REALIZADA').count()
            return {'ingreso_bruto': round(ing, 2), 'honorarios': round(hon, 2), 'margen_neto': round(ing - hon, 2), 'citas_realizadas': cit}

        v_act = _sum_ventana(ini_actual, fin_actual)
        v_ant = _sum_ventana(ini_anterior, fin_anterior)

        def _pct_delta(cur_v: float, prev_v: float) -> float:
            if prev_v == 0:
                return 100.0 if cur_v > 0 else 0.0
            return round(((cur_v - prev_v) / prev_v) * 100.0, 2)

        comparativa_yoy = {
            'periodo_actual': {'desde': ini_actual.isoformat(), 'hasta': fin_actual.isoformat(), **v_act},
            'periodo_anterior': {'desde': ini_anterior.isoformat(), 'hasta': fin_anterior.isoformat(), **v_ant},
            'variacion_pct': {
                'ingreso_bruto': _pct_delta(v_act['ingreso_bruto'], v_ant['ingreso_bruto']),
                'margen_neto': _pct_delta(v_act['margen_neto'], v_ant['margen_neto']),
                'citas_realizadas': _pct_delta(v_act['citas_realizadas'], v_ant['citas_realizadas']),
            },
        }

        # 4. Distribución por Método de Pago
        por_metodo = [
            {
                'metodo_pago': row['metodo_pago'],
                'cantidad': row['cantidad'],
                'total_bob': round(float(row['total']), 2),
            }
            for row in pagos_qs.values('metodo_pago')
            .annotate(cantidad=Count('id'), total=Coalesce(Sum('monto'), Decimal('0.00'), output_field=DEC_FIELD))
            .order_by('-total')
        ]

        # 5. Rendimiento por Psicólogo
        por_psicologo = []
        for p in Psicologo.objects.filter(activo=True).select_related('usuario'):
            c_real = citas_qs.filter(psicologo=p, estado='REALIZADA')
            bruto_p = float(c_real.aggregate(t=Coalesce(Sum('costo'), Decimal('0.00'), output_field=DEC_FIELD))['t'])
            hon_p = float(
                liq_qs.filter(psicologo=p)
                .aggregate(t=Coalesce(Sum('monto_neto_psicologo'), Decimal('0.00'), output_field=DEC_FIELD))['t']
            )
            por_psicologo.append({
                'psicologo_id': str(p.id),
                'nombre': f"Lic. {p.usuario.nombre} {p.usuario.apellido}".strip(),
                'sesiones_realizadas': c_real.count(),
                'ingreso_generado_bob': round(bruto_p, 2),
                'honorarios_liquidados_bob': round(hon_p, 2),
                'margen_centro_bob': round(bruto_p - hon_p, 2),
            })
        por_psicologo.sort(key=lambda x: x['ingreso_generado_bob'], reverse=True)

        # 6. Catálogo unificado de todos los reportes y consultas disponibles
        fuentes = ReportEngine.get_fuentes()
        if not incluir_superadmin_reportes:
            fuentes = {k: v for k, v in fuentes.items() if k not in ('bitacora', 'facturas_saas')}

        # Integración CU26-B & CRM: Estado de Resultados Contable (Utilidad Neta) + CRM 1-5★
        estado_resultados_pl = cls.calcular_estado_resultados_y_crm(fecha_desde=desde, fecha_hasta=hasta)

        return {
            'moneda': 'BOB',
            'rango': {
                'fecha_desde': desde.isoformat(),
                'fecha_hasta': hasta.isoformat(),
                'meses_cubiertos': len(serie_mensual),
            },
            'kpis': {
                'ingreso_bruto': round(float(ingreso_bruto), 2),
                'honorarios_psicologos': round(float(honorarios_psicologos), 2),
                'comision_retenida_centro': round(float(comision_retenida), 2),
                'margen_neto_centro': round(float(margen_neto_centro), 2),
                'ganancia_bruta_bob': estado_resultados_pl['ganancia_bruta_bob'],
                'total_gastos_fijos_bob': estado_resultados_pl['total_gastos_fijos_bob'],
                'utilidad_neta_bob': estado_resultados_pl['utilidad_neta_bob'],
                'cartera_por_cobrar': round(float(cartera_por_cobrar), 2),
                'indice_morosidad_pct': indice_morosidad_pct,
                'pacientes_morosos': cuentas_agg['pacientes_morosos'],
            },
            'estado_resultados_pl': estado_resultados_pl,
            'crm_stats': estado_resultados_pl['crm_stats'],
            'serie_mensual': serie_mensual,
            'comparativa_yoy': comparativa_yoy,
            'distribucion_metodo_pago': por_metodo,
            'rendimiento_psicologos': por_psicologo,
            'catalogo_reportes': [
                {
                    'fuente': k,
                    'label': v['label'],
                    'export_pdf': f'/api/reportes/{k}/export/pdf/',
                    'export_excel': f'/api/reportes/{k}/export/excel/',
                    'export_csv': f'/api/reportes/{k}/export/csv/',
                }
                for k, v in fuentes.items()
            ],
            'extracto_bancario_endpoint': '/api/finanzas/extracto/',
        }

    # ==========================================================================
    # INCREMENTO CU26-B & CRM: CTR_ContabilidadYCRM (Pasos 1 a 15)
    # ==========================================================================
    @classmethod
    def registrar_gasto_fijo(
        cls,
        categoria: str,
        descripcion: str,
        monto,
        moneda: str = 'BOB',
        fecha_gasto: date | None = None,
        periodo_mes: str | None = None,
        comprobante_ref: str = '',
        usuario=None,
    ) -> GastoFijoMensual:
        """Registra un gasto operativo fijo mensual convertido exactamente a Bs."""
        cat = (categoria or 'OTROS').upper().strip()
        cats_validas = {c[0] for c in GastoFijoMensual.CATEGORIA_CHOICES}
        if cat not in cats_validas:
            raise ValueError(f"Categoría inválida '{categoria}'.")
        monto_bob, _, _ = FinanzasService.convertir_a_bob(monto, moneda, tasa=TASA_OFICIAL_USD_BOB)
        f_g = fecha_gasto or timezone.localdate()
        per = str(periodo_mes or f"{f_g.year:04d}-{f_g.month:02d}")[:7]
        gasto = GastoFijoMensual.objects.create(
            periodo_mes=per,
            fecha_gasto=f_g,
            categoria=cat,
            descripcion=(descripcion or '').strip()[:220] or cat,
            moneda=(moneda or 'BOB').upper().strip(),
            monto_bob=monto_bob,
            comprobante_ref=(comprobante_ref or '').strip()[:120],
            registrado_por=usuario,
        )
        log_event(
            action='GASTO_FIJO_REGISTRADO',
            modulo='CU26_CONTABILIDAD',
            tenant=getattr(connection, 'schema_name', None),
            user=getattr(usuario, 'email', None),
            gasto_id=str(gasto.id),
            categoria=cat,
            monto_bob=float(monto_bob),
        )
        return gasto

    @classmethod
    def registrar_calificacion_crm(
        cls,
        paciente: Paciente,
        puntuacion_estrellas: int,
        cita: Cita | None = None,
        psicologo: Psicologo | None = None,
        puntualidad: int = 5,
        empatia_profesional: int = 5,
        calidad_plataforma: int = 5,
        comentario: str = '',
    ) -> CalificacionCRM:
        """
        Registra calificación post-consulta 1–5 estrellas (única por cita) y genera
        automáticamente alerta de seguimiento si puntuacion_estrellas <= 2.
        """
        estrellas = int(puntuacion_estrellas)
        if estrellas < 1 or estrellas > 5:
            raise ValueError('La puntuación de estrellas debe estar entre 1 y 5.')
        if cita is not None and CalificacionCRM.objects.filter(cita=cita).exists():
            raise ValueError('Esta cita ya cuenta con una calificación CRM registrada.')
        if cita is not None and psicologo is None:
            psicologo = cita.psicologo

        req_seg = estrellas <= 2
        calif = CalificacionCRM.objects.create(
            cita=cita,
            paciente=paciente,
            psicologo=psicologo,
            puntuacion_estrellas=estrellas,
            puntualidad=max(1, min(5, int(puntualidad))),
            empatia_profesional=max(1, min(5, int(empatia_profesional))),
            calidad_plataforma=max(1, min(5, int(calidad_plataforma))),
            comentario=(comentario or '').strip(),
            requiere_seguimiento=req_seg,
            estado_seguimiento='PENDIENTE' if req_seg else 'NO_REQUIERE',
        )
        log_event(
            action='CALIFICACION_CRM_REGISTRADA',
            modulo='CU26_CRM',
            tenant=getattr(connection, 'schema_name', None),
            paciente_id=str(paciente.id),
            cita_id=str(cita.id) if cita else None,
            estrellas=estrellas,
            requiere_seguimiento=req_seg,
        )
        return calif

    @classmethod
    def obtener_estadisticas_crm(cls, fecha_desde: date | None = None, fecha_hasta: date | None = None) -> dict:
        """CU26B-paso 12-13: CTR -> CRM : obtener_distribucion_estrellas -> csat_pct, promedio, histograma."""
        qs = CalificacionCRM.objects.select_related('paciente__usuario', 'psicologo__usuario')
        if fecha_desde:
            qs = qs.filter(fecha_calificacion__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha_calificacion__date__lte=fecha_hasta)
        items = list(qs)
        total = len(items)
        histograma = {str(i): 0 for i in range(1, 6)}
        for it in items:
            histograma[str(it.puntuacion_estrellas)] = histograma.get(str(it.puntuacion_estrellas), 0) + 1

        if total > 0:
            promedio = round(sum(it.puntuacion_estrellas for it in items) / total, 2)
            satisfechos = sum(1 for it in items if it.puntuacion_estrellas >= 4)
            csat_pct = round((satisfechos / total) * 100.0, 2)
            promotores = sum(1 for it in items if it.puntuacion_estrellas == 5)
            detractores = sum(1 for it in items if it.puntuacion_estrellas <= 3)
            nps_score = round(((promotores - detractores) / total) * 100.0, 1)
        else:
            promedio = 0.0
            csat_pct = 0.0
            nps_score = 0.0

        alertas_baja = [
            {
                'id': str(it.id),
                'paciente_nombre': f"{it.paciente.usuario.nombre} {it.paciente.usuario.apellido}".strip(),
                'psicologo_nombre': f"Lic. {it.psicologo.usuario.nombre} {it.psicologo.usuario.apellido}".strip() if it.psicologo else '-',
                'puntuacion_estrellas': it.puntuacion_estrellas,
                'comentario': it.comentario,
                'estado_seguimiento': it.estado_seguimiento,
                'nota_seguimiento': it.nota_seguimiento,
                'fecha': timezone.localtime(it.fecha_calificacion).strftime('%Y-%m-%d %H:%M'),
            }
            for it in items
            if it.requiere_seguimiento
        ]
        recientes = [
            {
                'id': str(it.id),
                'paciente_nombre': f"{it.paciente.usuario.nombre} {it.paciente.usuario.apellido}".strip(),
                'psicologo_nombre': f"Lic. {it.psicologo.usuario.nombre} {it.psicologo.usuario.apellido}".strip() if it.psicologo else '-',
                'puntuacion_estrellas': it.puntuacion_estrellas,
                'comentario': it.comentario,
                'requiere_seguimiento': it.requiere_seguimiento,
                'estado_seguimiento': it.estado_seguimiento,
                'fecha': timezone.localtime(it.fecha_calificacion).strftime('%Y-%m-%d %H:%M'),
            }
            for it in items[:25]
        ]
        return {
            'total_calificaciones': total,
            'promedio_estrellas': promedio,
            'csat_pct': csat_pct,
            'nps_score': nps_score,
            'histograma_1a5': histograma,
            'alertas_baja_calif': alertas_baja,
            'total_alertas_pendientes': sum(1 for a in alertas_baja if a['estado_seguimiento'] == 'PENDIENTE'),
            'calificaciones_recientes': recientes,
        }

    @classmethod
    def calcular_estado_resultados_y_crm(cls, fecha_desde: date | None = None, fecha_hasta: date | None = None) -> dict:
        """
        Flujo exacto del Diagrama de Secuencia CU26-B & CRM (Pasos 3 a 15):
          Ganancia Bruta = Ingresos Brutos - Costos Honorarios
          Utilidad Neta  = Ganancia Bruta - SUM(Gastos Fijos Mensuales)
        """
        hoy = timezone.localdate()
        hasta = fecha_hasta or hoy
        desde = fecha_desde or _subtract_months(hasta, 11)

        # CU26B-paso 3-4: CTR -> PAGO : sumar_ingresos_bob(fecha_ini, fecha_fin)
        pagos_agg = PagoConsulta.objects.filter(
            anulado=False,
            fecha_pago__date__gte=desde,
            fecha_pago__date__lte=hasta,
        ).aggregate(
            ingresos=Coalesce(Sum('monto'), Decimal('0.00'), output_field=DEC_FIELD),
            ajuste_neto=Coalesce(Sum('ajuste_redondeo'), Decimal('0.0000'), output_field=DecimalField(max_digits=14, decimal_places=4)),
        )
        ingresos_brutos_bob = _q2(pagos_agg['ingresos'])
        ajuste_cambiario_neto = Decimal(str(pagos_agg['ajuste_neto'] or Decimal('0.0000')))

        # CU26B-paso 5-6: CTR -> LIQ : sumar_honorarios_periodo(fecha_ini, fecha_fin)
        costos_honorarios_bob = _q2(
            LiquidacionHonorario.objects.exclude(estado='ANULADA')
            .filter(fecha_fin__gte=desde, fecha_inicio__lte=hasta)
            .aggregate(t=Coalesce(Sum('monto_neto_psicologo'), Decimal('0.00'), output_field=DEC_FIELD))['t']
        )

        # CU26B-paso 7: CTR -> CTR : ganancia_bruta = ingresos_brutos_bob - costos_honorarios_bob
        ganancia_bruta_bob = _q2(ingresos_brutos_bob - costos_honorarios_bob)

        # CU26B-paso 8-9: CTR -> GASTO : desglosar_por_categoria(fecha_ini, fecha_fin)
        gastos_qs = GastoFijoMensual.objects.filter(fecha_gasto__gte=desde, fecha_gasto__lte=hasta)
        gastos_cat_rows = (
            gastos_qs.values('categoria')
            .annotate(total=Coalesce(Sum('monto_bob'), Decimal('0.00'), output_field=DEC_FIELD), items=Count('id'))
            .order_by('-total')
        )
        labels_cat = dict(GastoFijoMensual.CATEGORIA_CHOICES)
        gastos_por_rubro = [
            {
                'categoria': r['categoria'],
                'label': labels_cat.get(r['categoria'], r['categoria']),
                'monto_bob': float(_q2(r['total'])),
                'registros': r['items'],
            }
            for r in gastos_cat_rows
        ]

        # CU26B-paso 10: loop por cada rubro -> acumular_total_gastos_fijos
        total_gastos_fijos_bob = Decimal('0.00')
        for rubro in gastos_por_rubro:
            total_gastos_fijos_bob = _q2(total_gastos_fijos_bob + Decimal(str(rubro['monto_bob'])))

        # CU26B-paso 11: utilidad_neta = ganancia_bruta - total_gastos_fijos
        utilidad_neta_bob = _q2(ganancia_bruta_bob - total_gastos_fijos_bob)
        margen_neto_pct = (
            round(float((utilidad_neta_bob / ingresos_brutos_bob) * Decimal('100.00')), 2)
            if ingresos_brutos_bob > Decimal('0.00') else 0.0
        )

        # CU26B-paso 12-13: CTR -> CRM : obtener_distribucion_estrellas
        crm_stats = cls.obtener_estadisticas_crm(fecha_desde=desde, fecha_hasta=hasta)

        # CU26B-paso 14: HTTP 200 OK {ganancia_bruta, gastos_fijos, utilidad_neta, crm_stats}
        return {
            'moneda': 'BOB',
            'fecha_inicio': desde.isoformat(),
            'fecha_fin': hasta.isoformat(),
            'ingresos_brutos_bob': float(ingresos_brutos_bob),
            'ajuste_cambiario_neto': float(ajuste_cambiario_neto),
            'costos_honorarios_bob': float(costos_honorarios_bob),
            'ganancia_bruta_bob': float(ganancia_bruta_bob),
            'gastos_fijos_desglose': gastos_por_rubro,
            'total_gastos_fijos_bob': float(total_gastos_fijos_bob),
            'utilidad_neta_bob': float(utilidad_neta_bob),
            'margen_neto_pct': margen_neto_pct,
            'es_deficit': utilidad_neta_bob < Decimal('0.00'),
            'waterfall': [
                {'concepto': 'Ingresos Brutos Cobrados', 'monto': float(ingresos_brutos_bob), 'tipo': 'ingreso'},
                {'concepto': '(-) Honorarios Psicólogos', 'monto': float(-costos_honorarios_bob), 'tipo': 'costo'},
                {'concepto': '(=) Ganancia Bruta', 'monto': float(ganancia_bruta_bob), 'tipo': 'subtotal'},
                {'concepto': '(-) Gastos Fijos Operativos', 'monto': float(-total_gastos_fijos_bob), 'tipo': 'gasto'},
                {'concepto': '(=) Utilidad Neta Real', 'monto': float(utilidad_neta_bob), 'tipo': 'neto'},
            ],
            'crm_stats': crm_stats,
        }
