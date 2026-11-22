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
from decimal import Decimal
from django.db.models import Sum, Count, Q, DecimalField
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone

from agenda.models import Cita
from clinica.models import Psicologo
from reportes.services import ReportEngine
from .models import CuentaPaciente, PagoConsulta, LiquidacionHonorario

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
                'cartera_por_cobrar': round(float(cartera_por_cobrar), 2),
                'indice_morosidad_pct': indice_morosidad_pct,
                'pacientes_morosos': cuentas_agg['pacientes_morosos'],
            },
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
