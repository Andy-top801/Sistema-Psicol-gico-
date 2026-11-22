# -*- coding: utf-8 -*-
# ==============================================================================
# MÓDULO: agenda/services/cita_mobile.py
# CAPA BCE: CONTROL — CTR_CitaMobileController
# CASO DE USO: CU11 Móvil — Gestión y Cancelación de Cita con Política >24h
# HISTORIAS: HU-41 (consulta de citas) · HU-42 (cancelación / reprogramación)
#
# Diagrama de Secuencia "Secuencia_Corregido_CU11_Citas_Movil":
#   1 : Paciente → IU_MisCitasMovil.presionar_cancelar_cita(cita_id, motivo)
#   2 : IU → CTR  POST /api/v1/citas/{id}/cancelar/ {motivo}
#   3 : CTR → CE_Cita.consultar_cita(cita_id)
#   4 : ← datos_cita(fecha, hora, estado)
#   5 : CTR → CTR.validar_anticipacion_mayor_24h(fecha, hora)
#   alt [anticipacion_horas > 24 (Cancelación Permitida)]
#     6 : → CE_Cita.cambiar_estado_cita('CANCELADA')        7 : ← cita_cancelada()
#     8 : → CE_Disponibilidad.liberar_bloque_horario()      9 : ← bloque_liberado()
#     10: → CE_Teleconsulta.cancelar_sala()                 11: ← sala_cancelada()
#     12: → CE_NotificacionCita.encolar_notificacion('CITA_CANCELADA')  13: ← notificacion_encolada()
#     14: → CE_AuditLog.registrar_acceso('CANCELACION_CITA_EXITOSA', ip) 15: ← acceso_auditado()
#     16: ← HTTP 200 OK {'Cita cancelada y bloque liberado'}
#     17: IU → Paciente.mostrar_confirmacion_cancelacion('Cita cancelada con éxito')
#   else [anticipacion_horas <= 24 (Fuera de Plazo)]
#     18: ← HTTP 400 Bad Request {'Plazo expirado: cancelaciones requieren > 24h'}
#     19: IU → Paciente.mostrar_aviso_politica_24h('Cancelación rechazada por política 24h')
#
# HU-42 (c): la regla temporal se evalúa SIEMPRE con el reloj del servidor
#            (timezone.localtime()); el cliente no envía ni influye en la hora.
# ==============================================================================
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from agenda.models import Cita, NotificacionCita
from audit.services import AuditLog
from clinica.models import Disponibilidad

POLITICA_HORAS = 24
VENTANA_TELECONSULTA_ANTES_MIN = 10
VENTANA_TELECONSULTA_DESPUES_MIN = 45

MSG_OK = "Cita cancelada y bloque liberado"
MSG_PLAZO = "Plazo expirado: cancelaciones requieren > 24h"


class CancelacionError(Exception):
    """Error de negocio con código HTTP y cuerpo de respuesta."""

    def __init__(self, status_code: int, body: dict):
        super().__init__(body.get("error"))
        self.status_code = status_code
        self.body = body


def _contacto_recepcion() -> dict:
    """Teléfono/WhatsApp de recepción del centro (HU-42 b)."""
    from core.models import Centro
    centro = Centro.objects.first()
    telefono = (centro.telefono if centro else "") or ""
    digitos = "".join(ch for ch in telefono if ch.isdigit())
    return {
        "telefono_recepcion": telefono,
        "whatsapp_recepcion": digitos,
        "centro_nombre": centro.nombre if centro else "",
        "centro_direccion": centro.direccion if centro else "",
    }


class CitaMobileController:
    """CTR_CitaMobileController (Diagrama de Clases de Análisis CU11 Móvil)."""

    # CU11-paso 5: validar_anticipacion_mayor_24h(fecha, hora) — autollamada del CTR_CitaMovilController
    @staticmethod
    def validar_anticipacion_mayor_24h(fecha, hora, ahora=None):
        """Retorna (permitido, horas_restantes) con la hora del SERVIDOR (HU-42 c)."""
        ahora = ahora or timezone.localtime()
        inicio = timezone.make_aware(datetime.combine(fecha, hora), timezone.get_current_timezone())
        horas = (inicio - ahora).total_seconds() / 3600.0
        return horas > POLITICA_HORAS, horas

    # CU11-paso 2: POST /api/v1/citas/{id}/cancelar/ (motivo) — llega desde IU_MisCitasMovil (vía CitaViewSet.cancelar)
    #              y termina en CU11-paso 16 (200 OK) o CU11-paso 18 (400 Bad Request).
    @classmethod
    @transaction.atomic
    def cancelar_cita(cls, cita_id, motivo: str, usuario, ip: str, aplicar_politica: bool = True) -> dict:
        motivo = (motivo or "").strip()
        if len(motivo) < 5:
            raise CancelacionError(400, {"error": "Indica un motivo de al menos 5 caracteres.", "codigo": "MOTIVO_INVALIDO"})

        # CU11-paso 3: consultar_cita(cita_id) → CE_Cita (bloquea la fila con SELECT FOR UPDATE)
        # CU11-paso 4: datos_cita(fecha, hora, estado) [retorno]
        try:
            cita = Cita.consultar_cita(cita_id)
        except Cita.DoesNotExist:
            raise CancelacionError(404, {"error": "Cita no encontrada."})
        datos_cita = {"fecha": cita.fecha, "hora": cita.hora_inicio, "estado": cita.estado}

        if datos_cita["estado"] not in ('PROGRAMADA', 'CONFIRMADA'):
            raise CancelacionError(400, {
                "error": f"No es posible cancelar una cita en estado {datos_cita['estado']}.",
                "codigo": "ESTADO_NO_CANCELABLE",
            })

        # CU11-paso 5: validar_anticipacion_mayor_24h(fecha, hora) → anticipacion_horas con el reloj del servidor
        permitido, horas = cls.validar_anticipacion_mayor_24h(datos_cita["fecha"], datos_cita["hora"])

        if aplicar_politica and not permitido:
            # else [anticipacion_horas <= 24 (Fuera de Plazo)]
            # CU11-paso 18: HTTP 400 Bad Request {'Plazo expirado: cancelaciones requieren > 24h'} [retorno]
            raise CancelacionError(400, {
                "error": MSG_PLAZO,
                "codigo": "CANCELLATION_WINDOW_EXPIRED",
                "politica_horas": POLITICA_HORAS,
                "horas_restantes": round(max(horas, 0), 1),
                **_contacto_recepcion(),
            })

        # alt [anticipacion_horas > 24 (Cancelación Permitida)] — el personal del centro cancela sin la política
        # CU11-paso 6: cambiar_estado_cita('CANCELADA') → CE_Cita
        # CU11-paso 7: cita_cancelada() [retorno]
        estado = cita.cambiar_estado_cita('CANCELADA', motivo)
        # CU11-paso 8: liberar_bloque_horario() → CE_Disponibilidad
        # CU11-paso 9: bloque_liberado() [retorno]
        bloque = Disponibilidad.liberar_bloque_horario(
            cita.psicologo, cita.fecha, cita.hora_inicio, cita.hora_fin)
        sala = None
        tele = getattr(cita, 'teleconsulta', None) if cita.modalidad == 'VIRTUAL' else None
        if tele:
            # CU11-paso 10: cancelar_sala() → CE_Teleconsulta (solo si la cita es VIRTUAL)
            # CU11-paso 11: sala_cancelada() [retorno]
            sala = tele.cancelar_sala()
        # CU11-paso 12: encolar_notificacion('CITA_CANCELADA') → CE_NotificacionCita (la envía el Cron de CU12)
        # CU11-paso 13: notificacion_encolada() [retorno]
        notif = NotificacionCita.encolar_notificacion(cita, 'CITA_CANCELADA')
        # CU11-paso 14: registrar_acceso(evento='CANCELACION_CITA_EXITOSA', ip) → CE_AuditLog
        # CU11-paso 15: acceso_auditado() [retorno]
        AuditLog.registrar_acceso(
            'CANCELACION_CITA_EXITOSA', ip,
            user=getattr(usuario, 'email', None), user_id=str(getattr(usuario, 'id', '')),
            cita_id=str(cita.id), anticipacion_horas=round(horas, 1), motivo=motivo,
        )

        # CU11-paso 16: HTTP 200 OK {'Cita cancelada y bloque liberado'} [retorno]
        return {
            "mensaje": MSG_OK,
            "cita_id": str(cita.id),
            "estado": estado,
            "cita_liberada": bloque["liberado"],
            "bloque": bloque,
            "sala": sala,
            "notificacion_id": str(notif.id),
            "anticipacion_horas": round(horas, 1),
            "psicologo_id": str(cita.psicologo_id),
        }

    # ── HU-41: listar_citas_paciente ─────────────────────────────────────────
    @classmethod
    def listar_citas_paciente(cls, paciente) -> dict:
        ahora = timezone.localtime()
        hoy = ahora.date()
        contacto = _contacto_recepcion()

        qs = Cita.objects.filter(paciente=paciente).select_related(
            'psicologo__usuario', 'teleconsulta'
        ).prefetch_related('psicologo__especialidades')

        proximas_qs = qs.filter(
            Q(fecha__gt=hoy) | Q(fecha=hoy, hora_fin__gte=ahora.time()),
            estado__in=['PROGRAMADA', 'CONFIRMADA'],
        ).order_by('fecha', 'hora_inicio')
        historial_qs = qs.exclude(id__in=proximas_qs.values_list('id', flat=True)).order_by('-fecha', '-hora_inicio')

        def formato(c):
            u = c.psicologo.usuario
            esps = [e.nombre for e in c.psicologo.especialidades.all()]
            inicio = timezone.make_aware(datetime.combine(c.fecha, c.hora_inicio), timezone.get_current_timezone())
            minutos = (inicio - ahora).total_seconds() / 60.0
            activa = c.estado in ('PROGRAMADA', 'CONFIRMADA')
            tele = getattr(c, 'teleconsulta', None) if c.modalidad == 'VIRTUAL' else None
            puede_entrar = (
                c.modalidad == 'VIRTUAL' and activa
                and -VENTANA_TELECONSULTA_DESPUES_MIN <= minutos <= VENTANA_TELECONSULTA_ANTES_MIN
            )
            permitido, _ = cls.validar_anticipacion_mayor_24h(c.fecha, c.hora_inicio, ahora)
            nombre = f"{u.nombre} {u.apellido}".strip()
            return {
                "id": str(c.id),
                "fecha": c.fecha.strftime("%Y-%m-%d"),
                "hora_inicio": c.hora_inicio.strftime("%H:%M"),
                "hora_fin": c.hora_fin.strftime("%H:%M"),
                "modalidad": c.modalidad,
                "estado": c.estado,
                # Etiqueta HU-41: PROGRAMADA se presenta como PENDIENTE (de confirmar)
                "estado_etiqueta": "PENDIENTE" if c.estado == 'PROGRAMADA' else c.estado,
                "psicologo_id": str(c.psicologo_id),
                "psicologo_nombre": f"Lic. {nombre}",
                "psicologo_iniciales": "".join(p[0] for p in nombre.split()[:2]).upper(),
                "psicologo_foto": None,
                "especialidad": esps[0] if esps else "Psicología General",
                "consultorio": contacto["centro_direccion"] if c.modalidad == 'PRESENCIAL' else "",
                "enlace_virtual": (tele.sala_id if tele else "") if c.modalidad == 'VIRTUAL' else "",
                "motivo_consulta": c.motivo_consulta,
                "motivo_cancelacion": c.motivo_cancelacion,
                "costo": float(c.costo),
                "minutos_para_inicio": round(minutos),
                "puede_entrar_teleconsulta": puede_entrar,
                "puede_cancelar": activa and permitido,
            }

        return {
            "paciente_id": str(paciente.id),
            "hora_servidor": ahora.isoformat(),
            "politica_cancelacion_horas": POLITICA_HORAS,
            **contacto,
            "proximas": [formato(c) for c in proximas_qs],
            "historial": [formato(c) for c in historial_qs],
        }
