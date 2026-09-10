# ==============================================================================
# SERVICIO: agenda/services/dashboard.py
# CAPA BCE: CONTROL (Controller) — CTR_Dashboard
# CASO DE USO: CU9 – Consultar Dashboard e Indicadores Clínicos (HU-20)
# DIAGRAMA DE COMUNICACIÓN CU9:
#   Actor → IU: 1: Acceder al Dashboard y seleccionar período
#   IU → CTR:   2: GET /api/agenda/dashboard/kpis/?periodo=mes
#   CTR → CE:   3: Validar permisos y esquema tenant
#   CE → CTR:   4: Contexto administrativo autorizado
#   CTR → CE:   5: SELECT COUNT, AVG(tasa_ausentismo) GROUP BY terapeuta
#   CE → CTR:   6: Agregaciones estadísticas calculadas
#   CTR → IU:   7: 200 OK {total_citas, ausentismo, ocupacion}
#   IU → Actor: 8: Renderizar KPIs, gráficos de tasa y métricas
#
# ESTE SERVICIO IMPLEMENTA LOS PASOS 5 Y 6 DEL DIAGRAMA (consultas agregadas
# sobre citas, pacientes, ausentismo y ocupación por terapeuta).
# ==============================================================================
from datetime import date
from django.db import connection
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django_tenants.utils import schema_context
from clinica.models import Psicologo, Paciente
from agenda.models import Cita, Alerta

class MetricsAggregator:
    """
    Servicio de agregación de métricas y KPIs para el Dashboard Clínico (HU-20).
    Calcula en tiempo real citas del día, ausentismo, distribución por estados,
    ocupación de terapeutas e ingresos estimados.
    Soporta ejecución en esquemas tenant individuales y agregación global en esquema public.
    """

    @classmethod
    def _obtener_kpis_esquema(cls, anio: int, mes: int, hoy: date) -> dict:
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
                "horas_atendidas": realizadas_p,
                "inasistencias": inasistencias_p,
                "ingresos_generados": float(ingresos_p)
            })

        # 4. Alertas Clínicas Activas
        alertas_raw = list(Alerta.objects.filter(resuelta=False).values(
            'id', 'paciente__usuario__nombre', 'paciente__usuario__apellido',
            'paciente__codigo_expediente', 'tipo', 'severidad', 'descripcion', 'fecha_creacion'
        )[:20])

        alertas_formateadas = []
        for a in alertas_raw:
            p_nom = f"{a.get('paciente__usuario__nombre') or ''} {a.get('paciente__usuario__apellido') or ''}".strip()
            alertas_formateadas.append({
                "id": str(a["id"]),
                "paciente_nombre": p_nom if p_nom else "Paciente",
                "codigo_expediente": a.get('paciente__codigo_expediente') or 'S/E',
                "tipo": a.get('tipo', ''),
                "severidad": a.get('severidad', ''),
                "descripcion": a.get('descripcion', ''),
                "fecha_creacion": a.get('fecha_creacion').isoformat() if hasattr(a.get('fecha_creacion'), 'isoformat') else str(a.get('fecha_creacion') or '')
            })

        return {
            "periodo": {
                "anio": anio,
                "mes": mes,
                "fecha_actual": hoy.strftime("%Y-%m-%d")
            },
            # Estructura requerida por verify_sprint1.py
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
                "lista": alertas_raw
            },
            # Propiedades desnormalizadas / enriquecidas para el frontend Angular:
            "total_citas_hoy": total_hoy,
            "total_citas_mes": total_mes,
            "tasa_ausentismo_pct": tasa_ausentismo,
            "tasa_asistencia_pct": tasa_asistencia,
            "ingresos_mes": float(ingresos_estimados),
            "distribucion_estados": {
                "PROGRAMADA": programadas_mes,
                "CONFIRMADA": confirmadas_mes,
                "REALIZADA": realizadas_mes,
                "CANCELADA": canceladas_mes,
                "INASISTENCIA": inasistencias_mes
            },
            "ocupacion_por_psicologo": [
                {
                    "psicologo_id": p["psicologo_id"],
                    "nombre": p["nombre"],
                    "colegiado": p["colegiado"],
                    "total_citas": p["citas_totales"],
                    "horas_atendidas": p["horas_atendidas"],
                    "realizadas": p["realizadas"],
                    "inasistencias": p["inasistencias"],
                    "ingresos_generados": p["ingresos_generados"]
                }
                for p in psicologos_metricas
            ],
            "alertas_activas": alertas_formateadas
        }

    @classmethod
    def obtener_kpis(cls, anio: int | None = None, mes: int | None = None) -> dict:
        hoy = date.today()
        if not anio:
            anio = hoy.year
        if not mes:
            mes = hoy.month

        # Si estamos en un tenant específico, calcular directamente en su esquema
        if connection.schema_name != 'public':
            return cls._obtener_kpis_esquema(anio, mes, hoy)

        # Si estamos en esquema 'public', agregar métricas de todos los tenants activos
        from tenants.models import Tenant
        tenants_activos = list(Tenant.objects.exclude(schema_name='public').filter(activo=True))
        if not tenants_activos:
            return cls._obtener_kpis_esquema(anio, mes, hoy)

        # Agregación multi-tenant consolidada
        total_hoy = 0
        hoy_prog = hoy_conf = hoy_real = hoy_canc = hoy_inas = 0
        total_mes = 0
        mes_prog = mes_conf = mes_real = mes_canc = mes_inas = 0
        ingresos_total = 0.0
        todos_psicologos = []
        todas_alertas = []
        alertas_raw_global = []

        for t in tenants_activos:
            try:
                with schema_context(t.schema_name):
                    res_t = cls._obtener_kpis_esquema(anio, mes, hoy)
                    c_hoy = res_t["citas_hoy"]
                    total_hoy += c_hoy["total"]
                    hoy_prog += c_hoy["programadas"]
                    hoy_conf += c_hoy["confirmadas"]
                    hoy_real += c_hoy["realizadas"]
                    hoy_canc += c_hoy["canceladas"]
                    hoy_inas += c_hoy["inasistencias"]

                    c_mes = res_t["citas_mes"]
                    total_mes += c_mes["total"]
                    mes_prog += c_mes["programadas"]
                    mes_conf += c_mes["confirmadas"]
                    mes_real += c_mes["realizadas"]
                    mes_canc += c_mes["canceladas"]
                    mes_inas += c_mes["inasistencias"]
                    ingresos_total += c_mes["ingresos_mes"]

                    for psi in res_t["ocupacion_por_psicologo"]:
                        todos_psicologos.append({
                            **psi,
                            "nombre": f"{psi['nombre']} ({t.nombre})"
                        })

                    for al in res_t["alertas_activas"]:
                        todas_alertas.append({
                            **al,
                            "centro_nombre": t.nombre
                        })
                    alertas_raw_global.extend(res_t["alertas_pendientes"]["lista"])
            except Exception:
                continue

        sesiones_cerradas = mes_real + mes_inas
        tasa_ausentismo = round((mes_inas / sesiones_cerradas) * 100, 2) if sesiones_cerradas > 0 else 0.0
        tasa_asistencia = round((mes_real / sesiones_cerradas) * 100, 2) if sesiones_cerradas > 0 else 0.0

        return {
            "periodo": {
                "anio": anio,
                "mes": mes,
                "fecha_actual": hoy.strftime("%Y-%m-%d"),
                "modo": "GLOBAL_SAAS"
            },
            "citas_hoy": {
                "total": total_hoy,
                "programadas": hoy_prog,
                "confirmadas": hoy_conf,
                "realizadas": hoy_real,
                "canceladas": hoy_canc,
                "inasistencias": hoy_inas
            },
            "citas_mes": {
                "total": total_mes,
                "programadas": mes_prog,
                "confirmadas": mes_conf,
                "realizadas": mes_real,
                "canceladas": mes_canc,
                "inasistencias": mes_inas,
                "tasa_ausentismo_pct": tasa_ausentismo,
                "tasa_asistencia_pct": tasa_asistencia,
                "ingresos_mes": round(ingresos_total, 2)
            },
            "ocupacion_psicologos": todos_psicologos,
            "alertas_pendientes": {
                "total": len(todas_alertas),
                "lista": alertas_raw_global
            },
            "total_citas_hoy": total_hoy,
            "total_citas_mes": total_mes,
            "tasa_ausentismo_pct": tasa_ausentismo,
            "tasa_asistencia_pct": tasa_asistencia,
            "ingresos_mes": round(ingresos_total, 2),
            "distribucion_estados": {
                "PROGRAMADA": mes_prog,
                "CONFIRMADA": mes_conf,
                "REALIZADA": mes_real,
                "CANCELADA": mes_canc,
                "INASISTENCIA": mes_inas
            },
            "ocupacion_por_psicologo": todos_psicologos,
            "alertas_activas": todas_alertas
        }
