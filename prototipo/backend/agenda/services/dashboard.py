from datetime import date
from django.db.models import Count, Sum, Q
from django.utils import timezone
from clinica.models import Psicologo, Paciente
from agenda.models import Cita, Alerta

class MetricsAggregator:
    """
    Servicio de agregación de métricas y KPIs para el Dashboard Clínico (HU-20).
    Calcula en tiempo real citas del día, ausentismo, distribución por estados,
    ocupación de terapeutas e ingresos estimados.
    """

    @classmethod
    def obtener_kpis(cls, anio: int | None = None, mes: int | None = None) -> dict:
        hoy = date.today()
        if not anio:
            anio = hoy.year
        if not mes:
            mes = hoy.month

        # 1. Citas del Día
        citas_hoy_qs = Cita.objects.filter(fecha=hoy)
        total_hoy = citas_hoy_qs.count()
        hoy_programadas = citas_hoy_qs.filter(estado='PROGRAMADA').count()
        hoy_confirmadas = citas_hoy_qs.filter(estado='CONFIRMADA').count()
        hoy_realizadas = citas_hoy_qs.filter(estado='REALIZADA').count()
        hoy_canceladas = citas_hoy_qs.filter(estado='CANCELADA').count()
        hoy_inasistencias = citas_hoy_qs.filter(estado='INASISTENCIA').count()

        # 2. Citas del Período (Mes)
        citas_mes_qs = Cita.objects.filter(fecha__year=anio, fecha__month=mes)
        total_mes = citas_mes_qs.count()
        realizadas_mes = citas_mes_qs.filter(estado='REALIZADA').count()
        inasistencias_mes = citas_mes_qs.filter(estado='INASISTENCIA').count()
        canceladas_mes = citas_mes_qs.filter(estado='CANCELADA').count()
        programadas_mes = citas_mes_qs.filter(estado='PROGRAMADA').count()
        confirmadas_mes = citas_mes_qs.filter(estado='CONFIRMADA').count()

        # Cálculo de Ausentismo (%)
        sesiones_cerradas = realizadas_mes + inasistencias_mes
        if sesiones_cerradas > 0:
            tasa_ausentismo = round((inasistencias_mes / sesiones_cerradas) * 100, 2)
            tasa_asistencia = round((realizadas_mes / sesiones_cerradas) * 100, 2)
        else:
            tasa_ausentismo = 0.0
            tasa_asistencia = 0.0

        # Ingresos del Mes (Citas Realizadas)
        ingresos_estimados = citas_mes_qs.filter(estado='REALIZADA').aggregate(total=Sum('costo'))['total'] or 0.0

        # 3. Métricas por Psicólogo (Ocupación)
        psicologos_metricas = []
        for psico in Psicologo.objects.filter(activo=True).select_related('usuario'):
            citas_psico = citas_mes_qs.filter(psicologo=psico)
            total_p = citas_psico.count()
            realizadas_p = citas_psico.filter(estado='REALIZADA').count()
            inasistencias_p = citas_psico.filter(estado='INASISTENCIA').count()
            ingresos_p = citas_psico.filter(estado='REALIZADA').aggregate(total=Sum('costo'))['total'] or 0.0

            psicologos_metricas.append({
                "psicologo_id": str(psico.id),
                "nombre": f"{psico.usuario.nombre} {psico.usuario.apellido}".strip(),
                "colegiado": psico.numero_colegiado,
                "citas_totales": total_p,
                "realizadas": realizadas_p,
                "inasistencias": inasistencias_p,
                "ingresos_generados": float(ingresos_p)
            })

        # 4. Alertas Clínicas Activas
        alertas_activas = list(Alerta.objects.filter(resuelta=False).values(
            'id', 'paciente__usuario__nombre', 'paciente__usuario__apellido',
            'paciente__codigo_expediente', 'tipo', 'severidad', 'descripcion', 'fecha_creacion'
        )[:10])

        return {
            "periodo": {
                "anio": anio,
                "mes": mes,
                "fecha_actual": hoy.strftime("%Y-%m-%d")
            },
            "citas_hoy": {
                "total": total_hoy,
                "programadas": hoy_programadas,
                "confirmadas": hoy_confirmadas,
                "realizadas": hoy_realizadas,
                "canceladas": hoy_canceladas,
                "inasistencias": hoy_inasistencias
            },
            "citas_mes": {
                "total": total_mes,
                "programadas": programadas_mes,
                "confirmadas": confirmadas_mes,
                "realizadas": realizadas_mes,
                "canceladas": canceladas_mes,
                "inasistencias": inasistencias_mes,
                "tasa_ausentismo_pct": tasa_ausentismo,
                "tasa_asistencia_pct": tasa_asistencia,
                "ingresos_mes": float(ingresos_estimados)
            },
            "ocupacion_psicologos": psicologos_metricas,
            "alertas_pendientes": {
                "total": Alerta.objects.filter(resuelta=False).count(),
                "lista": alertas_activas
            }
        }
