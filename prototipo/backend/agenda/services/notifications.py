# -*- coding: utf-8 -*-
# ==============================================================================
# MÓDULO: agenda/services/notifications.py
# CAPA BCE: CONTROL (Controller / Domain Service) — CTR_FCMNotificationService
# CASOS DE USO: CU12 (Gestionar Recordatorios y Notificaciones Push Automáticas)
# HISTORIAS DE USUARIO: HU-43
# DESCRIPCIÓN: Despacho transaccional de notificaciones push a terminales móviles
#              Flutter con tolerancia a fallos, soporte de modo simulación/test,
#              y procesamiento en segundo plano de recordatorios de citas (24h / 1h).
# ==============================================================================
import logging
from datetime import timedelta
from django.utils import timezone
from clinica.models import TokenFCM
from agenda.models import NotificacionCita, Cita

logger = logging.getLogger(__name__)

class FCMNotificationService:
    """Servicio de despacho y gestión de notificaciones push FCM (CU12 / HU-43)."""

    @classmethod
    def enviar_push_paciente(cls, paciente, titulo: str, cuerpo: str, payload_data: dict = None) -> bool:
        """
        Despacha una notificación push a todos los dispositivos registrados y activos del paciente.
        Si la biblioteca firebase_admin no está instalada o no hay credenciales activas,
        opera en modo tolerante a fallos simulando el despacho con log auditado.
        """
        tokens_qs = TokenFCM.objects.filter(paciente=paciente, activo=True)
        if not tokens_qs.exists():
            logger.info(f"[FCM] Paciente {paciente.id} no posee tokens FCM activos.")
            return False

        payload_dict = {str(k): str(v) for k, v in (payload_data or {}).items()}
        exito_global = False

        # Intentar despacho nativo con firebase_admin si estuviera configurado
        firebase_disponible = False
        messaging_mod = None
        try:
            from firebase_admin import messaging
            messaging_mod = messaging
            firebase_disponible = True
        except ImportError:
            firebase_disponible = False

        for token_record in tokens_qs:
            token_str = token_record.token
            try:
                if firebase_disponible and not token_str.startswith("fcm_test_"):
                    mensaje = messaging_mod.Message(
                        notification=messaging_mod.Notification(title=titulo, body=cuerpo),
                        data=payload_dict,
                        token=token_str
                    )
                    resp = messaging_mod.send(mensaje)
                    logger.info(f"[FCM] Push enviada con éxito: {resp}")
                else:
                    # Modo simulación / sandbox de pruebas de desarrollo
                    logger.info(f"[FCM-MOCK] Push simulada enviada a token={token_str[:15]}... | Título: {titulo}")

                exito_global = True
            except Exception as e:
                err_msg = str(e)
                logger.error(f"[FCM] Error despachando a token {token_str[:15]}...: {err_msg}")
                # Desactivar tokens revocados o no válidos
                if "registration-token-not-registered" in err_msg.lower() or "not registered" in err_msg.lower():
                    token_record.activo = False
                    token_record.save(update_fields=['activo'])

        return exito_global

    @classmethod
    def procesar_recordatorios_programados(cls) -> int:
        """
        Procesa la cola transaccional de notificaciones pendientes (NotificacionCita)
        cuya fecha_programada sea menor o igual al momento actual.
        Retorna la cantidad de notificaciones despachadas.
        """
        ahora = timezone.now()
        pendientes = NotificacionCita.objects.filter(
            enviada=False,
            fecha_programada__lte=ahora
        ).select_related('cita__paciente__usuario', 'cita__psicologo__usuario')

        despachadas_total = 0

        for notif in pendientes:
            cita = notif.cita
            paciente = cita.paciente
            u_psico = cita.psicologo.usuario
            psicologo_nombre = f"Lic. {u_psico.nombre} {u_psico.apellido}".strip()
            u_paciente = paciente.usuario
            paciente_nombre = getattr(u_paciente, 'nombre', '') or getattr(u_paciente, 'first_name', '')

            if notif.tipo_evento == 'RECORDATORIO_24H':
                titulo = "Recordatorio de Consulta Psicológica (24h)"
                cuerpo = f"Hola {paciente_nombre}, su sesión con {psicologo_nombre} está programada para mañana a las {cita.hora_inicio.strftime('%H:%M')} ({cita.modalidad})."
            elif notif.tipo_evento == 'RECORDATORIO_1H':
                titulo = "Su Consulta Comienza en 1 Hora"
                cuerpo = f"Por favor prepárese para su sesión con {psicologo_nombre} a las {cita.hora_inicio.strftime('%H:%M')}."
            elif notif.tipo_evento == 'CANCELACION':
                titulo = "Aviso de Cita Cancelada"
                cuerpo = f"Su consulta del {cita.fecha.strftime('%d/%m/%Y')} ha sido cancelada."
            else:
                titulo = "Notificación de SIGEPSI"
                cuerpo = f"Novedad en su consulta programada con {psicologo_nombre}."

            payload = {
                "tipo": notif.tipo_evento,
                "cita_id": str(cita.id),
                "modalidad": cita.modalidad,
                "fecha": cita.fecha.strftime("%Y-%m-%d"),
                "hora": cita.hora_inicio.strftime("%H:%M")
            }

            exito = cls.enviar_push_paciente(
                paciente=paciente,
                titulo=titulo,
                cuerpo=cuerpo,
                payload_data=payload
            )

            # Actualizar estado del registro en la cola
            notif.enviada = True
            notif.fecha_envio = timezone.now()
            notif.intentos_entrega += 1
            if not exito:
                notif.error_log = "Despacho finalizado sin dispositivos activos o entrega en fallback."
            notif.save(update_fields=['enviada', 'fecha_envio', 'intentos_entrega', 'error_log'])
            despachadas_total += 1

        return despachadas_total
