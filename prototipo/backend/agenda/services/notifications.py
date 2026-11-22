# -*- coding: utf-8 -*-
# ==============================================================================
# MÓDULO: agenda/services/notifications.py
# CAPA BCE: CONTROL — CTR_FCMNotificationController
# CASO DE USO: CU12 (Recordatorios Automáticos y Notificaciones Push FCM) / HU-43
#
# Implementa el Diagrama de Secuencia "Secuencia_Corregida_CU12_Notificaciones_Push_FCM":
#
#   1 : Cron Celery Beat → ejecutar_despacho_recordatorios()
#   2 : → CE_NotificacionCita.seleccionar_citas_proximas(ventana_24h, ventana_1h)
#   3 : ← citas_pendientes_notificar
#   loop [por cada cita próxima]
#     4 : → CE_Cita.obtener_detalle_cita(cita_id)
#     5 : ← detalle_cita(fecha, hora, psicologo)
#     6 : → CE_Paciente.obtener_paciente_asociado(paciente_id)
#     7 : ← datos_paciente(nombre, expediente)
#     8 : → CE_TokenFCM.obtener_tokens_activos_paciente(paciente_id)
#     9 : ← tokens_fcm_activos
#     10: → IU_FirebaseCloudMessaging.POST_messages_send(payload_recordatorio)
#     11/12: push emergente al smartphone y recepción confirmada
#     13: ← HTTP 200 FCM {message_id}
#     14: → CE_NotificacionCita.marcar_enviado(cita_id, estado='ENVIADO')
#     15: ← estado_actualizado()
#   16: ← resumen_despacho(total_enviadas: N) al Cron
# ==============================================================================
import logging

from clinica.models import Paciente, TokenFCM
from agenda.models import Cita, NotificacionCita
from agenda.services.fcm_gateway import FirebaseCloudMessaging, TokenNoRegistradoError

logger = logging.getLogger(__name__)

TITULO_RECORDATORIO = "Recordatorio de Consulta"
TITULO_CANCELACION = "Cita Cancelada"


class FCMNotificationController:
    """CTR_FCMNotificationController (Diagrama de Clases de Análisis CU12)."""

    # CU12-paso 1: ejecutar_despacho_recordatorios() — lo dispara el Cron Celery Beat
    #              (comando despachar_recordatorios_push o el ciclo embebido de agenda/apps.py)
    @classmethod
    def ejecutar_despacho_recordatorios(cls, ventana_24h=24, ventana_1h=1) -> dict:
        fcm = FirebaseCloudMessaging()

        # CU12-paso 2: seleccionar_citas_proximas(ventana_24h, ventana_1h) → CE_NotificacionCita
        # CU12-paso 3: citas_pendientes_notificar [retorno]
        citas_pendientes_notificar = cls.seleccionar_citas_proximas(ventana_24h, ventana_1h)

        enviadas, fallidas, detalle = 0, 0, []
        # loop [Por cada cita próxima a notificar] → CU12-paso 4 a CU12-paso 15 en despachar_push_fcm()
        for notif in citas_pendientes_notificar:
            ok = cls.despachar_push_fcm(fcm, notif)
            enviadas += 1 if ok else 0
            fallidas += 0 if ok else 1
            detalle.append({
                "notificacion_id": str(notif.id),
                "cita_id": str(notif.cita_id),
                "tipo_evento": notif.tipo_evento,
                "estado": notif.estado,
            })

        # CU12-paso 16: resumen_despacho(total_enviados=N) [retorno al Cron]
        return {
            "modo_fcm": fcm.modo,
            "total_evaluadas": len(citas_pendientes_notificar),
            "total_enviadas": enviadas,
            "total_fallidas": fallidas,
            "detalle": detalle,
        }

    # Alias con el nombre del Diagrama de Clases
    ejecutar_procesar_recordatorios_programados = ejecutar_despacho_recordatorios

    @staticmethod
    def seleccionar_citas_proximas(ventana_24h=24, ventana_1h=1) -> list:
        """CU12-paso 2 → CE_NotificacionCita; CU12-paso 3 ← citas_pendientes_notificar [retorno]."""
        return NotificacionCita.seleccionar_citas_proximas(ventana_24h, ventana_1h)

    @classmethod
    def despachar_push_fcm(cls, fcm: FirebaseCloudMessaging, notif: NotificacionCita) -> bool:
        """Cuerpo del loop: CU12-paso 4 a CU12-paso 15 para una cita."""
        # CU12-paso 4: obtener_detalle_cita(cita_id) → CE_Cita
        # CU12-paso 5: detalle_cita(fecha, hora, psicologo) [retorno]
        detalle_cita = Cita.obtener_detalle_cita(notif.cita_id)
        # CU12-paso 6: obtener_paciente_asociado(paciente_id) → CE_Paciente
        # CU12-paso 7: datos_paciente(nombre, expediente) [retorno]
        datos_paciente = Paciente.obtener_paciente_asociado(detalle_cita["paciente_id"])
        # CU12-paso 8: obtener_tokens_activos_paciente(paciente_id) → CE_TokenFCM
        # CU12-paso 9: tokens_fcm_activos [retorno]
        tokens_fcm_activos = TokenFCM.obtener_tokens_activos_paciente(datos_paciente["paciente_id"])

        titulo, cuerpo = cls.construir_mensaje(notif.tipo_evento, detalle_cita, datos_paciente)
        notif.titulo, notif.cuerpo = titulo, cuerpo
        notif.save(update_fields=['titulo', 'cuerpo'])

        if not tokens_fcm_activos:
            notif.registrar_fallo("Paciente sin dispositivos con token FCM activo.")
            return False

        payload_recordatorio = {
            "tipo": notif.tipo_evento,
            "notificacion_id": str(notif.id),
            "cita_id": detalle_cita["cita_id"],
            "modalidad": detalle_cita["modalidad"],
            "fecha": detalle_cita["fecha"].strftime("%Y-%m-%d"),
            "hora": detalle_cita["hora"].strftime("%H:%M"),
            # Criterio (c): pantalla destino al presionar la notificación
            "ruta": ("teleconsulta" if detalle_cita["modalidad"] == 'VIRTUAL' and notif.tipo_evento != 'CANCELACION'
                     else "detalle_cita"),
        }

        message_id, errores = None, []
        for token in tokens_fcm_activos:
            try:
                # CU12-paso 10: POST messages:send(payload_recordatorio) → IU_FirebaseCloudMessaging
                # CU12-paso 11: notificacion_push_emergente() — FCM la muestra en el smartphone del Paciente
                # CU12-paso 12: recepcion_confirmada [retorno del dispositivo a FCM]
                # CU12-paso 13: HTTP 200 FCM {message_id} [retorno]
                resp = fcm.POST_messages_send(token.token, titulo, cuerpo, payload_recordatorio)
                message_id = message_id or resp["message_id"]
            except TokenNoRegistradoError as e:
                token.desactivar()
                errores.append(f"token revocado: {e}")
            except Exception as e:
                errores.append(str(e))
                logger.error(f"[FCM] Error despachando cita {notif.cita_id}: {e}")

        if message_id:
            # CU12-paso 14: marcar_enviado(cita_id, estado='ENVIADO') → CE_NotificacionCita
            # CU12-paso 15: estado_actualizado [retorno]
            cls.registrar_alerta_enviada(notif, message_id)
            return True

        notif.registrar_fallo("; ".join(errores) or "FCM no confirmó la entrega.")
        return False

    @staticmethod
    def registrar_alerta_enviada(notif: NotificacionCita, message_id: str):
        """CU12-paso 14: marcar_enviado(cita_id, estado='ENVIADO') → CU12-paso 15: estado_actualizado() [retorno]."""
        return notif.marcar_enviado(estado='ENVIADO', message_id=message_id)

    @staticmethod
    def construir_mensaje(tipo_evento: str, detalle_cita: dict, datos_paciente: dict):
        """Criterio (b): título 'Recordatorio de Consulta' indicando psicólogo, hora y modalidad."""
        modalidad = "Teleconsulta (virtual)" if detalle_cita["modalidad"] == 'VIRTUAL' else "Presencial"
        hora = detalle_cita["hora"].strftime('%H:%M')
        fecha = detalle_cita["fecha"].strftime('%d/%m/%Y')
        nombre = datos_paciente["nombre"]
        psico = detalle_cita["psicologo"]
        if tipo_evento == 'CANCELACION':
            # CU11 Móvil / HU-42 (a): aviso FCM de cancelación confirmada
            return TITULO_CANCELACION, (
                f"{nombre}, tu cita con {psico} del {fecha} a las {hora} fue cancelada. "
                "El horario quedó liberado; puedes reprogramar desde Mis Citas."
            )
        if tipo_evento == 'RECORDATORIO_1H':
            cuerpo = f"{nombre}, tu sesión con {psico} comienza en menos de 1 hora, a las {hora}. Modalidad: {modalidad}."
        else:
            cuerpo = f"{nombre}, tienes sesión con {psico} el {fecha} a las {hora}. Modalidad: {modalidad}."
        return TITULO_RECORDATORIO, cuerpo


# Compatibilidad con código/tests previos del Sprint 3
class FCMNotificationService(FCMNotificationController):

    @classmethod
    def procesar_recordatorios_programados(cls) -> int:
        return cls.ejecutar_despacho_recordatorios()["total_evaluadas"]

    @classmethod
    def enviar_push_paciente(cls, paciente, titulo: str, cuerpo: str, payload_data: dict = None) -> bool:
        fcm = FirebaseCloudMessaging()
        exito = False
        for token in TokenFCM.obtener_tokens_activos_paciente(paciente.id):
            try:
                fcm.POST_messages_send(token.token, titulo, cuerpo, payload_data or {})
                exito = True
            except TokenNoRegistradoError:
                token.desactivar()
            except Exception as e:
                logger.error(f"[FCM] {e}")
        return exito
