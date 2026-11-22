# ==============================================================================
# MÓDULO: reportes/services.py
# DESCRIPCIÓN: Motor central de reportes. Construye queries dinámicas según la
#              fuente de datos, columnas, filtros y ordenamiento seleccionados.
# ==============================================================================
import uuid
from datetime import date, datetime
from decimal import Decimal

from django.db.models import Sum, Count, Q, F
from django.utils import timezone

from accounts.models import Usuario, Rol
from agenda.models import Cita, Teleconsulta, Alerta
from clinica.models import Psicologo, Paciente, Especialidad, AlertaRiesgoIA, ResumenClinicoIA
from finanzas.models import CuentaPaciente, PagoConsulta, MovimientoFinanciero, LiquidacionHonorario
from subscriptions.models import FacturaSaaS
from audit.services import read_events, parse_date


# ---------------------------------------------------------------------------
# Definición de fuentes de datos y sus columnas disponibles
# ---------------------------------------------------------------------------
FUENTES_DISPONIBLES = {
    "citas": {
        "label": "Citas Clínicas",
        "columnas": [
            {"key": "fecha", "label": "Fecha"},
            {"key": "hora_inicio", "label": "Hora Inicio"},
            {"key": "hora_fin", "label": "Hora Fin"},
            {"key": "paciente_nombre", "label": "Paciente"},
            {"key": "paciente_expediente", "label": "Expediente"},
            {"key": "psicologo_nombre", "label": "Psicólogo"},
            {"key": "modalidad", "label": "Modalidad"},
            {"key": "estado", "label": "Estado"},
            {"key": "costo", "label": "Costo (BOB)"},
            {"key": "motivo_consulta", "label": "Motivo"},
            {"key": "motivo_cancelacion", "label": "Motivo Cancelación"},
            {"key": "fecha_creacion", "label": "Fecha Creación"},
        ],
        "filtros": [
            {"key": "fecha_desde", "label": "Fecha Desde", "type": "date"},
            {"key": "fecha_hasta", "label": "Fecha Hasta", "type": "date"},
            {"key": "mes", "label": "Mes", "type": "select",
             "opciones": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]},
            {"key": "estado", "label": "Estado", "type": "select",
             "opciones": ["PROGRAMADA", "CONFIRMADA", "REALIZADA", "CANCELADA", "INASISTENCIA"]},
            {"key": "modalidad", "label": "Modalidad", "type": "select",
             "opciones": ["PRESENCIAL", "VIRTUAL"]},
            {"key": "psicologo_id", "label": "Psicólogo", "type": "text"},
            {"key": "paciente_id", "label": "Paciente", "type": "text"},
        ],
    },
    "psicologos": {
        "label": "Psicólogos",
        "columnas": [
            {"key": "nombre_completo", "label": "Nombre Completo"},
            {"key": "email", "label": "Email"},
            {"key": "numero_colegiado", "label": "N° Colegiado"},
            {"key": "especialidades", "label": "Especialidades"},
            {"key": "modalidad", "label": "Modalidad"},
            {"key": "tarifa_base", "label": "Tarifa Base (BOB)"},
            {"key": "activo", "label": "Activo"},
            {"key": "fecha_ingreso", "label": "Fecha Ingreso"},
            {"key": "total_citas", "label": "Total Citas"},
            {"key": "citas_realizadas", "label": "Citas Realizadas"},
        ],
        "filtros": [
            {"key": "modalidad", "label": "Modalidad", "type": "select",
             "opciones": ["PRESENCIAL", "VIRTUAL", "MIXTA"]},
            {"key": "activo", "label": "Activo", "type": "select",
             "opciones": ["true", "false"]},
            {"key": "especialidad", "label": "Especialidad", "type": "text"},
        ],
    },
    "pacientes": {
        "label": "Pacientes",
        "columnas": [
            {"key": "nombre_completo", "label": "Nombre Completo"},
            {"key": "email", "label": "Email"},
            {"key": "codigo_expediente", "label": "Expediente"},
            {"key": "ci", "label": "Cédula de Identidad"},
            {"key": "fecha_nacimiento", "label": "Fecha Nacimiento"},
            {"key": "edad", "label": "Edad"},
            {"key": "genero", "label": "Género"},
            {"key": "contacto_emergencia_nombre", "label": "Contacto Emergencia"},
            {"key": "contacto_emergencia_telf", "label": "Teléfono Emergencia"},
            {"key": "tutor_legal_nombre", "label": "Tutor Legal"},
            {"key": "tutor_legal_ci", "label": "CI Tutor"},
            {"key": "fecha_registro", "label": "Fecha Registro"},
        ],
        "filtros": [
            {"key": "genero", "label": "Género", "type": "select",
             "opciones": ["M", "F", "O"]},
            {"key": "fecha_registro_desde", "label": "Registrado Desde", "type": "date"},
            {"key": "fecha_registro_hasta", "label": "Registrado Hasta", "type": "date"},
            {"key": "es_menor", "label": "Es Menor de Edad", "type": "select",
             "opciones": ["true", "false"]},
        ],
    },
    "alertas": {
        "label": "Alertas Clínicas",
        "columnas": [
            {"key": "paciente_nombre", "label": "Paciente"},
            {"key": "codigo_expediente", "label": "Expediente"},
            {"key": "tipo", "label": "Tipo"},
            {"key": "severidad", "label": "Severidad"},
            {"key": "descripcion", "label": "Descripción"},
            {"key": "resuelta", "label": "Resuelta"},
            {"key": "fecha_creacion", "label": "Fecha Creación"},
            {"key": "fecha_resolucion", "label": "Fecha Resolución"},
            {"key": "nota_resolucion", "label": "Nota Resolución"},
        ],
        "filtros": [
            {"key": "tipo", "label": "Tipo", "type": "select",
             "opciones": ["INASISTENCIA_REITERADA", "RIESGO_DESERCION", "URGENCIA_CLINICA"]},
            {"key": "severidad", "label": "Severidad", "type": "select",
             "opciones": ["BAJA", "MEDIA", "ALTA", "CRITICA"]},
            {"key": "resuelta", "label": "Resuelta", "type": "select",
             "opciones": ["true", "false"]},
            {"key": "fecha_desde", "label": "Fecha Desde", "type": "date"},
            {"key": "fecha_hasta", "label": "Fecha Hasta", "type": "date"},
        ],
    },
    "ingresos": {
        "label": "Ingresos Financieros",
        "columnas": [
            {"key": "fecha", "label": "Fecha"},
            {"key": "paciente_nombre", "label": "Paciente"},
            {"key": "psicologo_nombre", "label": "Psicólogo"},
            {"key": "modalidad", "label": "Modalidad"},
            {"key": "estado", "label": "Estado"},
            {"key": "costo", "label": "Monto (BOB)"},
        ],
        "filtros": [
            {"key": "fecha_desde", "label": "Fecha Desde", "type": "date"},
            {"key": "fecha_hasta", "label": "Fecha Hasta", "type": "date"},
            {"key": "psicologo_id", "label": "Psicólogo", "type": "text"},
            {"key": "modalidad", "label": "Modalidad", "type": "select",
             "opciones": ["PRESENCIAL", "VIRTUAL"]},
        ],
    },
    "teleconsultas": {
        "label": "Teleconsultas",
        "columnas": [
            {"key": "fecha", "label": "Fecha"},
            {"key": "paciente_nombre", "label": "Paciente"},
            {"key": "psicologo_nombre", "label": "Psicólogo"},
            {"key": "sala_id", "label": "Sala Jitsi"},
            {"key": "hora_inicio_real", "label": "Hora Inicio Real"},
            {"key": "hora_fin_real", "label": "Hora Fin Real"},
            {"key": "duracion_minutos", "label": "Duración (min)"},
            {"key": "estado", "label": "Estado Cita"},
        ],
        "filtros": [
            {"key": "fecha_desde", "label": "Fecha Desde", "type": "date"},
            {"key": "fecha_hasta", "label": "Fecha Hasta", "type": "date"},
            {"key": "psicologo_id", "label": "Psicólogo", "type": "text"},
        ],
    },
    "bitacora": {
        "label": "Bitácora de Auditoría",
        "columnas": [
            {"key": "timestamp", "label": "Fecha / Hora"},
            {"key": "ip", "label": "IP"},
            {"key": "user", "label": "Usuario"},
            {"key": "tenant", "label": "Tenant / Centro"},
            {"key": "method", "label": "Método HTTP"},
            {"key": "path", "label": "Ruta"},
            {"key": "action", "label": "Acción"},
            {"key": "status_code", "label": "Código Estado"},
            {"key": "error", "label": "Error"},
        ],
        "filtros": [
            {"key": "date", "label": "Fecha", "type": "date"},
            {"key": "user", "label": "Usuario", "type": "text"},
            {"key": "method", "label": "Método", "type": "select",
             "opciones": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
            {"key": "status_code", "label": "Código Estado", "type": "text"},
            {"key": "ip", "label": "IP", "type": "text"},
            {"key": "tenant", "label": "Tenant", "type": "text"},
        ],
    },
    "usuarios": {
        "label": "Usuarios del Sistema",
        "columnas": [
            {"key": "nombre_completo", "label": "Nombre Completo"},
            {"key": "email", "label": "Email"},
            {"key": "telefono", "label": "Teléfono"},
            {"key": "rol", "label": "Rol"},
            {"key": "activo", "label": "Activo"},
            {"key": "fecha_creacion", "label": "Fecha Creación"},
        ],
        "filtros": [
            {"key": "rol", "label": "Rol", "type": "text"},
            {"key": "activo", "label": "Activo", "type": "select",
             "opciones": ["true", "false"]},
        ],
    },
    # ─── NUEVAS FUENTES SPRINT 4 (HU-52, HU-53, HU-54, HU-49, HU-50, HU-55) ───
    "pagos": {
        "label": "Cobros y Pagos en Caja (Bs.)",
        "columnas": [
            {"key": "fecha_pago", "label": "Fecha Pago"},
            {"key": "numero_recibo", "label": "N° Recibo"},
            {"key": "paciente_nombre", "label": "Paciente"},
            {"key": "expediente", "label": "Expediente"},
            {"key": "metodo_pago", "label": "Método"},
            {"key": "monto", "label": "Monto (Bs.)"},
            {"key": "referencia_externa", "label": "Referencia"},
            {"key": "registrado_por", "label": "Registrado Por"},
        ],
        "filtros": [
            {"key": "fecha_desde", "label": "Fecha Desde", "type": "date"},
            {"key": "fecha_hasta", "label": "Fecha Hasta", "type": "date"},
            {"key": "metodo_pago", "label": "Método de Pago", "type": "select",
             "opciones": ["EFECTIVO", "QR_BANCARIO", "TRANSFERENCIA", "TARJETA_STRIPE"]},
            {"key": "paciente_id", "label": "Paciente", "type": "text"},
        ],
    },
    "cuentas_pacientes": {
        "label": "Estado de Cuentas y Morosidad (Bs.)",
        "columnas": [
            {"key": "expediente", "label": "Expediente"},
            {"key": "paciente_nombre", "label": "Paciente"},
            {"key": "total_cargado", "label": "Total Cargado (Bs.)"},
            {"key": "total_pagado", "label": "Total Pagado (Bs.)"},
            {"key": "saldo_pendiente", "label": "Saldo Pendiente (Bs.)"},
            {"key": "ultima_actualizacion", "label": "Última Actualización"},
        ],
        "filtros": [
            {"key": "solo_deudores", "label": "Solo con Saldo Pendiente", "type": "select",
             "opciones": ["true", "false"]},
        ],
    },
    "extracto_pagos": {
        "label": "Extracto Histórico de Pagos (hasta 20 años)",
        "columnas": [
            {"key": "fecha", "label": "Fecha"},
            {"key": "expediente", "label": "Expediente"},
            {"key": "paciente_nombre", "label": "Paciente"},
            {"key": "tipo", "label": "Tipo"},
            {"key": "numero_documento", "label": "Documento"},
            {"key": "concepto", "label": "Concepto"},
            {"key": "metodo_pago", "label": "Método"},
            {"key": "debe", "label": "Debe (Bs.)"},
            {"key": "haber", "label": "Haber (Bs.)"},
        ],
        "filtros": [
            {"key": "fecha_desde", "label": "Fecha Desde", "type": "date"},
            {"key": "fecha_hasta", "label": "Fecha Hasta", "type": "date"},
            {"key": "tipo", "label": "Tipo", "type": "select", "opciones": ["CARGO", "ABONO", "AJUSTE"]},
            {"key": "metodo_pago", "label": "Método", "type": "select",
             "opciones": ["EFECTIVO", "QR_BANCARIO", "TRANSFERENCIA", "TARJETA_STRIPE"]},
            {"key": "paciente_id", "label": "Paciente", "type": "text"},
        ],
    },
    "liquidaciones": {
        "label": "Liquidaciones de Honorarios (Bs.)",
        "columnas": [
            {"key": "codigo_liquidacion", "label": "Código"},
            {"key": "psicologo_nombre", "label": "Psicólogo"},
            {"key": "fecha_inicio", "label": "Periodo Desde"},
            {"key": "fecha_fin", "label": "Periodo Hasta"},
            {"key": "total_sesiones", "label": "Sesiones"},
            {"key": "monto_bruto", "label": "Bruto (Bs.)"},
            {"key": "comision_centro", "label": "Comisión Centro (Bs.)"},
            {"key": "monto_neto_psicologo", "label": "Neto Psicólogo (Bs.)"},
            {"key": "estado", "label": "Estado"},
            {"key": "referencia_bancaria", "label": "Ref. Bancaria"},
        ],
        "filtros": [
            {"key": "fecha_desde", "label": "Fecha Desde", "type": "date"},
            {"key": "fecha_hasta", "label": "Fecha Hasta", "type": "date"},
            {"key": "estado", "label": "Estado", "type": "select", "opciones": ["GENERADA", "PAGADA", "ANULADA"]},
            {"key": "psicologo_id", "label": "Psicólogo", "type": "text"},
        ],
    },
    "alertas_riesgo_ia": {
        "label": "Alertas Longitudinales de Riesgo IA",
        "columnas": [
            {"key": "fecha_deteccion", "label": "Fecha Detección"},
            {"key": "expediente", "label": "Expediente"},
            {"key": "paciente_nombre", "label": "Paciente"},
            {"key": "tipo", "label": "Tipo Riesgo"},
            {"key": "severidad", "label": "Severidad"},
            {"key": "score_riesgo", "label": "Score (0-100)"},
            {"key": "estado", "label": "Estado"},
            {"key": "nota_intervencion", "label": "Intervención Clínica"},
        ],
        "filtros": [
            {"key": "severidad", "label": "Severidad", "type": "select", "opciones": ["CRITICO", "ALTO", "MEDIO", "BAJO"]},
            {"key": "estado", "label": "Estado", "type": "select", "opciones": ["ABIERTA", "EN_ATENCION", "RESUELTA", "DESCARTADA"]},
            {"key": "fecha_desde", "label": "Fecha Desde", "type": "date"},
            {"key": "fecha_hasta", "label": "Fecha Hasta", "type": "date"},
        ],
    },
    "resumenes_ia": {
        "label": "Auditoría de Resúmenes Clínicos IA (HITL)",
        "columnas": [
            {"key": "fecha_generacion", "label": "Fecha Generación"},
            {"key": "expediente", "label": "Expediente"},
            {"key": "paciente_nombre", "label": "Paciente"},
            {"key": "estado", "label": "Estado HITL"},
            {"key": "fuente_modelo", "label": "Modelo"},
            {"key": "total_notas_analizadas", "label": "Notas Analizadas"},
            {"key": "hash_sha256", "label": "Hash SHA-256"},
        ],
        "filtros": [
            {"key": "estado", "label": "Estado", "type": "select", "opciones": ["BORRADOR_IA", "APROBADO_HITL", "DESCARTADO"]},
            {"key": "fecha_desde", "label": "Fecha Desde", "type": "date"},
            {"key": "fecha_hasta", "label": "Fecha Hasta", "type": "date"},
        ],
    },
    "facturas_saas": {
        "label": "Facturación SaaS por Centro (USD)",
        "columnas": [
            {"key": "fecha_emision", "label": "Fecha Emisión"},
            {"key": "numero_factura", "label": "N° Factura"},
            {"key": "tenant_nombre", "label": "Centro Psicológico"},
            {"key": "plan", "label": "Plan"},
            {"key": "monto_usd", "label": "Monto (USD)"},
            {"key": "estado", "label": "Estado"},
            {"key": "stripe_session_id", "label": "Stripe Session"},
        ],
        "filtros": [
            {"key": "estado", "label": "Estado", "type": "select", "opciones": ["PAGADA", "PENDIENTE", "FALLIDA", "ANULADA"]},
            {"key": "plan", "label": "Plan", "type": "select", "opciones": ["basico", "profesional", "empresarial"]},
        ],
    },
}


def _safe_str(val):
    if val is None:
        return ""
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    return str(val)


class ReportEngine:
    """Motor genérico de reportes que construye consultas y devuelve datos tabulares."""

    @classmethod
    def get_fuentes(cls):
        return {k: {"label": v["label"], "columnas": v["columnas"], "filtros": v["filtros"]}
                for k, v in FUENTES_DISPONIBLES.items()}

    @classmethod
    def generar(cls, fuente, columnas=None, filtros=None, orden=None, page=None, page_size=None):
        """
        Genera un reporte según la fuente, columnas, filtros y orden.
        Soporta paginación opcional (page, page_size) para consultas web grandes.
        Retorna: { "columnas": [...], "datos": [...], "total": int, "resumen": {} }
        """
        filtros = filtros or {}
        handler = {
            "citas": cls._reporte_citas,
            "psicologos": cls._reporte_psicologos,
            "pacientes": cls._reporte_pacientes,
            "alertas": cls._reporte_alertas,
            "ingresos": cls._reporte_ingresos,
            "teleconsultas": cls._reporte_teleconsultas,
            "bitacora": cls._reporte_bitacora,
            "usuarios": cls._reporte_usuarios,
            "pagos": cls._reporte_pagos,
            "cuentas_pacientes": cls._reporte_cuentas_pacientes,
            "extracto_pagos": cls._reporte_extracto_pagos,
            "liquidaciones": cls._reporte_liquidaciones,
            "alertas_riesgo_ia": cls._reporte_alertas_riesgo_ia,
            "resumenes_ia": cls._reporte_resumenes_ia,
            "facturas_saas": cls._reporte_facturas_saas,
        }.get(fuente)
        if not handler:
            raise ValueError(f"Fuente de datos '{fuente}' no reconocida.")

        filas, resumen = handler(filtros)

        # Filtrar columnas
        todas_cols = FUENTES_DISPONIBLES[fuente]["columnas"]
        if columnas:
            cols_keys = [c for c in columnas if any(tc["key"] == c for tc in todas_cols)]
            if not cols_keys:
                cols_keys = [c["key"] for c in todas_cols]
        else:
            cols_keys = [c["key"] for c in todas_cols]

        col_defs = [c for c in todas_cols if c["key"] in cols_keys]

        # Filtrar datos por columnas seleccionadas
        datos_filtrados = []
        for fila in filas:
            datos_filtrados.append({k: fila.get(k, "") for k in cols_keys})

        # Ordenar
        if orden and orden.get("columna") in cols_keys:
            col_ord = orden["columna"]
            reverse = orden.get("direccion", "ASC").upper() == "DESC"
            datos_filtrados.sort(key=lambda x: _safe_str(x.get(col_ord, "")), reverse=reverse)

        total = len(datos_filtrados)
        paginacion = None
        if page is not None and page_size is not None:
            p = max(1, int(page))
            ps = max(1, min(500, int(page_size)))
            offset = (p - 1) * ps
            datos_filtrados = datos_filtrados[offset: offset + ps]
            paginacion = {
                "page": p,
                "page_size": ps,
                "total_registros": total,
                "total_paginas": max(1, (total + ps - 1) // ps),
            }

        resp = {
            "columnas": col_defs,
            "datos": datos_filtrados,
            "total": total,
            "resumen": resumen,
        }
        if paginacion:
            resp["paginacion"] = paginacion
        return resp

    # ─────────────────────── CITAS ───────────────────────
    @classmethod
    def _reporte_citas(cls, filtros):
        qs = Cita.objects.select_related(
            'paciente__usuario', 'psicologo__usuario'
        ).all()

        if filtros.get("fecha_desde"):
            qs = qs.filter(fecha__gte=filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            qs = qs.filter(fecha__lte=filtros["fecha_hasta"])
        if filtros.get("mes"):
            mes_raw = str(filtros["mes"]).lower().strip()
            meses_map = {
                "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
                "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
                "noviembre": 11, "diciembre": 12
            }
            mes_num = meses_map.get(mes_raw)
            if not mes_num and mes_raw.isdigit():
                mes_num = int(mes_raw)
            if mes_num:
                qs = qs.filter(fecha__month=mes_num)
        if filtros.get("estado"):
            qs = qs.filter(estado=filtros["estado"].upper())
        if filtros.get("modalidad"):
            qs = qs.filter(modalidad=filtros["modalidad"].upper())
        if filtros.get("psicologo_id") or filtros.get("psicologo"):
            psic_val = str(filtros.get("psicologo_id") or filtros.get("psicologo")).strip()
            q_psico = (
                Q(psicologo__usuario__nombre__icontains=psic_val) |
                Q(psicologo__usuario__apellido__icontains=psic_val)
            )
            try:
                q_psico |= Q(psicologo_id=uuid.UUID(psic_val))
            except (ValueError, TypeError, AttributeError):
                pass
            qs = qs.filter(q_psico)
        if filtros.get("paciente_id") or filtros.get("paciente"):
            pac_val = str(filtros.get("paciente_id") or filtros.get("paciente")).strip()
            q_pac = (
                Q(paciente__usuario__nombre__icontains=pac_val) |
                Q(paciente__usuario__apellido__icontains=pac_val) |
                Q(paciente__codigo_expediente__icontains=pac_val)
            )
            try:
                q_pac |= Q(paciente_id=uuid.UUID(pac_val))
            except (ValueError, TypeError, AttributeError):
                pass
            qs = qs.filter(q_pac)

        qs = qs.order_by('-fecha', 'hora_inicio')
        filas = []
        total_costo = Decimal("0.00")
        for c in qs:
            total_costo += c.costo or Decimal("0.00")
            filas.append({
                "fecha": c.fecha.isoformat(),
                "hora_inicio": c.hora_inicio.strftime("%H:%M"),
                "hora_fin": c.hora_fin.strftime("%H:%M"),
                "paciente_nombre": f"{c.paciente.usuario.nombre} {c.paciente.usuario.apellido}".strip(),
                "paciente_expediente": c.paciente.codigo_expediente,
                "psicologo_nombre": f"{c.psicologo.usuario.nombre} {c.psicologo.usuario.apellido}".strip(),
                "modalidad": c.modalidad,
                "estado": c.estado,
                "costo": float(c.costo),
                "motivo_consulta": c.motivo_consulta or "",
                "motivo_cancelacion": c.motivo_cancelacion or "",
                "fecha_creacion": c.fecha_creacion.isoformat() if c.fecha_creacion else "",
            })

        resumen = {
            "total_registros": len(filas),
            "total_ingresos": float(total_costo),
            "por_estado": {},
        }
        for fila in filas:
            est = fila["estado"]
            resumen["por_estado"][est] = resumen["por_estado"].get(est, 0) + 1

        return filas, resumen

    # ─────────────────────── PSICÓLOGOS ───────────────────────
    @classmethod
    def _reporte_psicologos(cls, filtros):
        qs = Psicologo.objects.select_related('usuario').prefetch_related('especialidades').all()

        if filtros.get("modalidad"):
            qs = qs.filter(modalidad=filtros["modalidad"].upper())
        if filtros.get("activo"):
            qs = qs.filter(activo=filtros["activo"].lower() in ("true", "1"))
        if filtros.get("especialidad"):
            qs = qs.filter(especialidades__nombre__icontains=filtros["especialidad"])

        filas = []
        for p in qs.distinct():
            total_citas = Cita.objects.filter(psicologo=p).count()
            citas_realizadas = Cita.objects.filter(psicologo=p, estado='REALIZADA').count()
            esp_list = ", ".join(e.nombre for e in p.especialidades.all())
            filas.append({
                "nombre_completo": f"{p.usuario.nombre} {p.usuario.apellido}".strip(),
                "email": p.usuario.email,
                "numero_colegiado": p.numero_colegiado,
                "especialidades": esp_list,
                "modalidad": p.modalidad,
                "tarifa_base": float(p.tarifa_base),
                "activo": "Sí" if p.activo else "No",
                "fecha_ingreso": p.fecha_ingreso.isoformat() if p.fecha_ingreso else "",
                "total_citas": total_citas,
                "citas_realizadas": citas_realizadas,
            })

        return filas, {"total_registros": len(filas)}


    # ─────────────────────── PACIENTES ───────────────────────
    @classmethod
    def _reporte_pacientes(cls, filtros):
        qs = Paciente.objects.select_related('usuario').all()

        if filtros.get("genero"):
            qs = qs.filter(genero=filtros["genero"].upper())
        if filtros.get("fecha_registro_desde"):
            qs = qs.filter(fecha_registro__gte=filtros["fecha_registro_desde"])
        if filtros.get("fecha_registro_hasta"):
            qs = qs.filter(fecha_registro__lte=filtros["fecha_registro_hasta"])

        filas = []
        for p in qs.order_by('-fecha_registro'):
            edad = p.calcular_edad()
            if filtros.get("es_menor"):
                es_menor_flag = filtros["es_menor"].lower() in ("true", "1")
                if es_menor_flag and edad >= 18:
                    continue
                if not es_menor_flag and edad < 18:
                    continue
            filas.append({
                "nombre_completo": f"{p.usuario.nombre} {p.usuario.apellido}".strip(),
                "email": p.usuario.email,
                "codigo_expediente": p.codigo_expediente,
                "ci": p.ci,
                "fecha_nacimiento": p.fecha_nacimiento.isoformat(),
                "edad": edad,
                "genero": p.get_genero_display(),
                "contacto_emergencia_nombre": p.contacto_emergencia_nombre or "",
                "contacto_emergencia_telf": p.contacto_emergencia_telf or "",
                "tutor_legal_nombre": p.tutor_legal_nombre or "",
                "tutor_legal_ci": p.tutor_legal_ci or "",
                "fecha_registro": p.fecha_registro.isoformat(),
            })

        return filas, {"total_registros": len(filas)}


    # ─────────────────────── ALERTAS ───────────────────────
    @classmethod
    def _reporte_alertas(cls, filtros):
        qs = Alerta.objects.select_related('paciente__usuario').all()

        if filtros.get("tipo"):
            qs = qs.filter(tipo=filtros["tipo"].upper())
        if filtros.get("severidad"):
            qs = qs.filter(severidad=filtros["severidad"].upper())
        if filtros.get("resuelta"):
            qs = qs.filter(resuelta=filtros["resuelta"].lower() in ("true", "1"))
        if filtros.get("fecha_desde"):
            qs = qs.filter(fecha_creacion__date__gte=filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            qs = qs.filter(fecha_creacion__date__lte=filtros["fecha_hasta"])

        filas = []
        for a in qs.order_by('-fecha_creacion'):
            filas.append({
                "paciente_nombre": f"{a.paciente.usuario.nombre} {a.paciente.usuario.apellido}".strip(),
                "codigo_expediente": a.paciente.codigo_expediente,
                "tipo": a.tipo,
                "severidad": a.severidad,
                "descripcion": a.descripcion,
                "resuelta": "Sí" if a.resuelta else "No",
                "fecha_creacion": a.fecha_creacion.isoformat() if a.fecha_creacion else "",
                "fecha_resolucion": a.fecha_resolucion.isoformat() if a.fecha_resolucion else "",
                "nota_resolucion": a.nota_resolucion or "",
            })

        resumen = {"total_registros": len(filas), "por_severidad": {}}
        for f in filas:
            sev = f["severidad"]
            resumen["por_severidad"][sev] = resumen["por_severidad"].get(sev, 0) + 1

        return filas, resumen

    # ─────────────────────── INGRESOS ───────────────────────
    @classmethod
    def _reporte_ingresos(cls, filtros):
        qs = Cita.objects.select_related(
            'paciente__usuario', 'psicologo__usuario'
        ).filter(estado='REALIZADA')

        if filtros.get("fecha_desde"):
            qs = qs.filter(fecha__gte=filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            qs = qs.filter(fecha__lte=filtros["fecha_hasta"])
        if filtros.get("psicologo_id") or filtros.get("psicologo"):
            p_val = str(filtros.get("psicologo_id") or filtros.get("psicologo")).strip()
            q_p = (
                Q(psicologo__usuario__nombre__icontains=p_val) |
                Q(psicologo__usuario__apellido__icontains=p_val)
            )
            try:
                q_p |= Q(psicologo_id=uuid.UUID(p_val))
            except (ValueError, TypeError, AttributeError):
                pass
            qs = qs.filter(q_p)
        if filtros.get("modalidad"):
            qs = qs.filter(modalidad=filtros["modalidad"].upper())

        filas = []
        total_ingresos = Decimal("0.00")
        for c in qs.order_by('-fecha'):
            total_ingresos += c.costo or Decimal("0.00")
            filas.append({
                "fecha": c.fecha.isoformat(),
                "paciente_nombre": f"{c.paciente.usuario.nombre} {c.paciente.usuario.apellido}".strip(),
                "psicologo_nombre": f"{c.psicologo.usuario.nombre} {c.psicologo.usuario.apellido}".strip(),
                "modalidad": c.modalidad,
                "estado": c.estado,
                "costo": float(c.costo),
            })

        return filas, {"total_registros": len(filas), "total_ingresos": float(total_ingresos)}

    # ─────────────────────── TELECONSULTAS ───────────────────────
    @classmethod
    def _reporte_teleconsultas(cls, filtros):
        qs = Teleconsulta.objects.select_related(
            'cita__paciente__usuario', 'cita__psicologo__usuario'
        ).all()

        if filtros.get("fecha_desde"):
            qs = qs.filter(cita__fecha__gte=filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            qs = qs.filter(cita__fecha__lte=filtros["fecha_hasta"])
        if filtros.get("psicologo_id") or filtros.get("psicologo"):
            p_val = str(filtros.get("psicologo_id") or filtros.get("psicologo")).strip()
            q_p = (
                Q(cita__psicologo__usuario__nombre__icontains=p_val) |
                Q(cita__psicologo__usuario__apellido__icontains=p_val)
            )
            try:
                q_p |= Q(cita__psicologo_id=uuid.UUID(p_val))
            except (ValueError, TypeError, AttributeError):
                pass
            qs = qs.filter(q_p)

        filas = []
        for t in qs.order_by('-cita__fecha'):
            dur_min = round(t.duracion_segundos / 60, 1) if t.duracion_segundos else 0
            filas.append({
                "fecha": t.cita.fecha.isoformat(),
                "paciente_nombre": f"{t.cita.paciente.usuario.nombre} {t.cita.paciente.usuario.apellido}".strip(),
                "psicologo_nombre": f"{t.cita.psicologo.usuario.nombre} {t.cita.psicologo.usuario.apellido}".strip(),
                "sala_id": t.sala_id,
                "hora_inicio_real": t.hora_inicio_real.isoformat() if t.hora_inicio_real else "",
                "hora_fin_real": t.hora_fin_real.isoformat() if t.hora_fin_real else "",
                "duracion_minutos": dur_min,
                "estado": t.cita.estado,
            })

        return filas, {"total_registros": len(filas)}


    # ─────────────────────── BITÁCORA ───────────────────────
    @classmethod
    def _reporte_bitacora(cls, filtros):
        log_date = None
        if filtros.get("date"):
            log_date = parse_date(filtros["date"])

        try:
            events = read_events(log_date)
        except Exception:
            events = []

        # Filtros en memoria
        if filtros.get("user"):
            events = [e for e in events if filtros["user"].lower() in (e.get("user") or "").lower()]
        if filtros.get("method"):
            events = [e for e in events if e.get("method") == filtros["method"].upper()]
        if filtros.get("status_code"):
            try:
                sc = int(filtros["status_code"])
                events = [e for e in events if e.get("status_code") == sc]
            except ValueError:
                pass
        if filtros.get("ip"):
            events = [e for e in events if filtros["ip"] in (e.get("ip") or "")]
        if filtros.get("tenant"):
            events = [e for e in events if filtros["tenant"].lower() in (e.get("tenant") or "").lower()]

        filas = []
        for ev in events:
            filas.append({
                "timestamp": ev.get("timestamp", ""),
                "ip": ev.get("ip", ""),
                "user": ev.get("user", ""),
                "tenant": ev.get("tenant", ""),
                "method": ev.get("method", ""),
                "path": ev.get("path", ""),
                "action": ev.get("action", ""),
                "status_code": ev.get("status_code", ""),
                "error": ev.get("error", ""),
            })

        return filas, {"total_registros": len(filas)}


    # ─────────────────────── USUARIOS ───────────────────────
    @classmethod
    def _reporte_usuarios(cls, filtros):
        qs = Usuario.objects.select_related('rol').all()

        if filtros.get("rol"):
            qs = qs.filter(rol__nombre__icontains=filtros["rol"])
        if filtros.get("activo"):
            qs = qs.filter(activo=filtros["activo"].lower() in ("true", "1"))

        filas = []
        for u in qs.order_by('-fecha_creacion'):
            filas.append({
                "nombre_completo": f"{u.nombre} {u.apellido}".strip(),
                "email": u.email,
                "telefono": u.telefono or "",
                "rol": u.rol.nombre if u.rol else "Sin Rol",
                "activo": "Sí" if u.activo else "No",
                "fecha_creacion": u.fecha_creacion.isoformat() if u.fecha_creacion else "",
            })

        return filas, {"total_registros": len(filas)}


    # ─────────────────────── PAGOS CAJA (Bs.) ───────────────────────
    @classmethod
    def _reporte_pagos(cls, filtros):
        qs = PagoConsulta.objects.filter(anulado=False).select_related(
            "cuenta__paciente__usuario", "registrado_por"
        )
        if filtros.get("fecha_desde"):
            qs = qs.filter(fecha_pago__date__gte=filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            qs = qs.filter(fecha_pago__date__lte=filtros["fecha_hasta"])
        if filtros.get("metodo_pago"):
            qs = qs.filter(metodo_pago=filtros["metodo_pago"].upper())
        if filtros.get("paciente_id"):
            val = str(filtros["paciente_id"]).strip()
            q = Q(cuenta__paciente__usuario__nombre__icontains=val) | Q(cuenta__paciente__usuario__apellido__icontains=val)
            try:
                q |= Q(cuenta__paciente_id=uuid.UUID(val))
            except (ValueError, TypeError):
                pass
            qs = qs.filter(q)

        filas = []
        total_bob = Decimal("0.00")
        for p in qs.order_by("-fecha_pago"):
            pac = p.cuenta.paciente
            total_bob += p.monto
            filas.append({
                "fecha_pago": timezone.localtime(p.fecha_pago).strftime("%Y-%m-%d %H:%M"),
                "numero_recibo": p.numero_recibo,
                "paciente_nombre": f"{pac.usuario.nombre} {pac.usuario.apellido}".strip(),
                "expediente": pac.codigo_expediente,
                "metodo_pago": p.metodo_pago,
                "monto": float(p.monto),
                "referencia_externa": p.referencia_externa or "-",
                "registrado_por": f"{p.registrado_por.nombre} {p.registrado_por.apellido}".strip() if p.registrado_por else "Sistema",
            })
        return filas, {"total_pagos": len(filas), "total_recaudado_bob": round(float(total_bob), 2)}

    # ─────────────────────── CUENTAS PACIENTES ───────────────────────
    @classmethod
    def _reporte_cuentas_pacientes(cls, filtros):
        qs = CuentaPaciente.objects.select_related("paciente__usuario").all()
        if str(filtros.get("solo_deudores", "")).lower() in ("true", "1"):
            qs = qs.filter(saldo_pendiente__gt=0)

        filas = []
        total_por_cobrar = Decimal("0.00")
        for c in qs.order_by("-saldo_pendiente"):
            total_por_cobrar += c.saldo_pendiente
            filas.append({
                "expediente": c.paciente.codigo_expediente,
                "paciente_nombre": f"{c.paciente.usuario.nombre} {c.paciente.usuario.apellido}".strip(),
                "total_cargado": float(c.total_cargado),
                "total_pagado": float(c.total_pagado),
                "saldo_pendiente": float(c.saldo_pendiente),
                "ultima_actualizacion": timezone.localtime(c.ultima_actualizacion).strftime("%Y-%m-%d %H:%M"),
            })
        return filas, {"total_cuentas": len(filas), "cartera_por_cobrar_bob": round(float(total_por_cobrar), 2)}

    # ─────────────────────── EXTRACTO HISTÓRICO PAGOS ───────────────────────
    @classmethod
    def _reporte_extracto_pagos(cls, filtros):
        qs = MovimientoFinanciero.objects.select_related("cuenta__paciente__usuario").all()
        if filtros.get("fecha_desde"):
            qs = qs.filter(fecha_movimiento__date__gte=filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            qs = qs.filter(fecha_movimiento__date__lte=filtros["fecha_hasta"])
        if filtros.get("tipo"):
            qs = qs.filter(tipo=filtros["tipo"].upper())
        if filtros.get("metodo_pago"):
            qs = qs.filter(metodo_pago=filtros["metodo_pago"].upper())
        if filtros.get("paciente_id"):
            val = str(filtros["paciente_id"]).strip()
            q = Q(cuenta__paciente__usuario__nombre__icontains=val) | Q(cuenta__paciente__usuario__apellido__icontains=val)
            try:
                q |= Q(cuenta__paciente_id=uuid.UUID(val))
            except (ValueError, TypeError):
                pass
            qs = qs.filter(q)

        filas = []
        total_debe = Decimal("0.00")
        total_haber = Decimal("0.00")
        for m in qs.order_by("fecha_movimiento", "fecha_creacion").iterator(chunk_size=1000):
            pac = m.cuenta.paciente
            total_debe += m.debe
            total_haber += m.haber
            filas.append({
                "fecha": timezone.localtime(m.fecha_movimiento).strftime("%Y-%m-%d %H:%M"),
                "expediente": pac.codigo_expediente,
                "paciente_nombre": f"{pac.usuario.nombre} {pac.usuario.apellido}".strip(),
                "tipo": m.tipo,
                "numero_documento": m.numero_documento or "-",
                "concepto": m.concepto,
                "metodo_pago": m.metodo_pago or "-",
                "debe": float(m.debe),
                "haber": float(m.haber),
            })
        return filas, {
            "total_movimientos": len(filas),
            "total_debe_bob": round(float(total_debe), 2),
            "total_haber_bob": round(float(total_haber), 2),
            "saldo_neto_bob": round(float(total_debe - total_haber), 2),
        }

    # ─────────────────────── LIQUIDACIONES HONORARIOS ───────────────────────
    @classmethod
    def _reporte_liquidaciones(cls, filtros):
        qs = LiquidacionHonorario.objects.select_related("psicologo__usuario").all()
        if filtros.get("fecha_desde"):
            qs = qs.filter(fecha_inicio__gte=filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            qs = qs.filter(fecha_fin__lte=filtros["fecha_hasta"])
        if filtros.get("estado"):
            qs = qs.filter(estado=filtros["estado"].upper())
        if filtros.get("psicologo_id"):
            val = str(filtros["psicologo_id"]).strip()
            q = Q(psicologo__usuario__nombre__icontains=val) | Q(psicologo__usuario__apellido__icontains=val)
            try:
                q |= Q(psicologo_id=uuid.UUID(val))
            except (ValueError, TypeError):
                pass
            qs = qs.filter(q)

        filas = []
        tot_bruto = Decimal("0.00")
        tot_neto = Decimal("0.00")
        for l in qs.order_by("-fecha_emision"):
            if l.estado != "ANULADA":
                tot_bruto += l.monto_bruto
                tot_neto += l.monto_neto_psicologo
            filas.append({
                "codigo_liquidacion": l.codigo_liquidacion,
                "psicologo_nombre": f"Lic. {l.psicologo.usuario.nombre} {l.psicologo.usuario.apellido}".strip(),
                "fecha_inicio": l.fecha_inicio.isoformat(),
                "fecha_fin": l.fecha_fin.isoformat(),
                "total_sesiones": l.total_sesiones,
                "monto_bruto": float(l.monto_bruto),
                "comision_centro": float(l.comision_centro),
                "monto_neto_psicologo": float(l.monto_neto_psicologo),
                "estado": l.estado,
                "referencia_bancaria": l.referencia_bancaria or "-",
            })
        return filas, {
            "total_liquidaciones": len(filas),
            "monto_bruto_bob": round(float(tot_bruto), 2),
            "total_honorarios_psicologos_bob": round(float(tot_neto), 2),
        }

    # ─────────────────────── ALERTAS RIESGO IA ───────────────────────
    @classmethod
    def _reporte_alertas_riesgo_ia(cls, filtros):
        qs = AlertaRiesgoIA.objects.select_related("paciente__usuario").all()
        if filtros.get("severidad"):
            qs = qs.filter(severidad=filtros["severidad"].upper())
        if filtros.get("estado"):
            qs = qs.filter(estado=filtros["estado"].upper())
        if filtros.get("fecha_desde"):
            qs = qs.filter(fecha_deteccion__date__gte=filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            qs = qs.filter(fecha_deteccion__date__lte=filtros["fecha_hasta"])

        filas = []
        for a in qs.order_by("-score_riesgo", "-fecha_deteccion"):
            filas.append({
                "fecha_deteccion": timezone.localtime(a.fecha_deteccion).strftime("%Y-%m-%d %H:%M"),
                "expediente": a.paciente.codigo_expediente,
                "paciente_nombre": f"{a.paciente.usuario.nombre} {a.paciente.usuario.apellido}".strip(),
                "tipo": a.tipo,
                "severidad": a.severidad,
                "score_riesgo": a.score_riesgo,
                "estado": a.estado,
                "nota_intervencion": a.nota_intervencion or "-",
            })
        return filas, {"total_alertas_riesgo": len(filas)}

    # ─────────────────────── RESÚMENES CLÍNICOS IA ───────────────────────
    @classmethod
    def _reporte_resumenes_ia(cls, filtros):
        qs = ResumenClinicoIA.objects.select_related("paciente__usuario").all()
        if filtros.get("estado"):
            qs = qs.filter(estado=filtros["estado"].upper())
        if filtros.get("fecha_desde"):
            qs = qs.filter(fecha_generacion__date__gte=filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            qs = qs.filter(fecha_generacion__date__lte=filtros["fecha_hasta"])

        filas = []
        for r in qs.order_by("-fecha_generacion"):
            filas.append({
                "fecha_generacion": timezone.localtime(r.fecha_generacion).strftime("%Y-%m-%d %H:%M"),
                "expediente": r.paciente.codigo_expediente,
                "paciente_nombre": f"{r.paciente.usuario.nombre} {r.paciente.usuario.apellido}".strip(),
                "estado": r.estado,
                "fuente_modelo": r.fuente_modelo,
                "total_notas_analizadas": r.total_notas_analizadas,
                "hash_sha256": r.hash_sha256[:16] + "...",
            })
        return filas, {"total_resumenes_ia": len(filas)}

    # ─────────────────────── FACTURAS SAAS (USD - PUBLIC) ───────────────────────
    @classmethod
    def _reporte_facturas_saas(cls, filtros):
        qs = FacturaSaaS.objects.select_related("tenant", "suscripcion").all()
        if filtros.get("estado"):
            qs = qs.filter(estado=filtros["estado"].upper())
        if filtros.get("plan"):
            qs = qs.filter(plan=filtros["plan"].lower())

        filas = []
        total_usd = Decimal("0.00")
        for f in qs.order_by("-fecha_emision"):
            if f.estado == "PAGADA":
                total_usd += f.monto_usd
            filas.append({
                "fecha_emision": timezone.localtime(f.fecha_emision).strftime("%Y-%m-%d %H:%M"),
                "numero_factura": f.numero_factura,
                "tenant_nombre": f.tenant.nombre if f.tenant else f.suscripcion.nombre_centro,
                "plan": f.plan,
                "monto_usd": float(f.monto_usd),
                "estado": f.estado,
                "stripe_session_id": f.stripe_session_id,
            })
        return filas, {"total_facturas": len(filas), "total_facturado_usd": round(float(total_usd), 2)}
