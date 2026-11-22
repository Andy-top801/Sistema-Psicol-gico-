# -*- coding: utf-8 -*-
# ==============================================================================
# MÓDULO: agenda/services/fcm_gateway.py
# CAPA BCE: BOUNDARY (Interfaz externa) — IU_FirebaseCloudMessaging
# CASO DE USO: CU12 / HU-43 — CU12-paso 10 a CU12-paso 13 del Diagrama de Secuencia.
#
#   10: POST_messages_send(payload_recordatorio)   CTR → IU_FirebaseCloudMessaging
#   11: notificacion_push_emergente() [asíncrono]  IU  → Paciente (Smartphone)
#   12: recepcion_confirmada()                     Paciente → IU
#   13: HTTP 200 FCM {message_id}                  IU  → CTR
#
# Modo REAL   : si existe FIREBASE_CREDENTIALS_FILE (JSON de cuenta de servicio)
#               y la librería firebase_admin está instalada.
# Modo SANDBOX: sin credenciales, simula la respuesta HTTP 200 de FCM con un
#               message_id; el dispositivo recibe el aviso consultando
#               /api/agenda/notificaciones/ (centro de notificaciones).
# ==============================================================================
import logging
import os
import uuid

logger = logging.getLogger(__name__)


class TokenNoRegistradoError(Exception):
    """FCM respondió que el token ya no está registrado (app desinstalada / token rotado)."""


class FirebaseCloudMessaging:
    """IU_FirebaseCloudMessaging — atributos según el Diagrama de Clases de Análisis CU12."""

    endpointUrl = "https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

    def __init__(self):
        self.credentials_file = os.environ.get('FIREBASE_CREDENTIALS_FILE', '')
        self.projectId = os.environ.get('FIREBASE_PROJECT_ID', 'sigepsi-sandbox')
        self.serviceAccountToken = None
        self.statusDespacho = None
        self._messaging = None
        self.modo = 'SANDBOX'
        self.validarCredencialesOAuth()

    def validarCredencialesOAuth(self) -> bool:
        """Inicializa firebase_admin con la cuenta de servicio (OAuth2). False → modo sandbox."""
        if not self.credentials_file or not os.path.exists(self.credentials_file):
            return False
        try:
            import firebase_admin
            from firebase_admin import credentials, messaging
            if not firebase_admin._apps:
                firebase_admin.initialize_app(credentials.Certificate(self.credentials_file))
            self._messaging = messaging
            self.serviceAccountToken = 'oauth2-service-account'
            self.modo = 'REAL'
            return True
        except Exception as e:  # librería ausente o credencial inválida
            logger.warning(f"[FCM] Credenciales no válidas, se usa modo SANDBOX: {e}")
            return False

    def POST_messages_send(self, token: str, titulo: str, cuerpo: str, data: dict) -> dict:
        """
        CU12-paso 10: POST messages:send(payload_recordatorio) → CU12-paso 13: HTTP 200 FCM {message_id}. Retorna {'status': 200, 'message_id': ...}.
        Lanza TokenNoRegistradoError si FCM indica token inválido; otras excepciones = fallo.
        """
        data = {str(k): str(v) for k, v in (data or {}).items()}

        if self.modo == 'REAL':
            msg = self._messaging.Message(
                notification=self._messaging.Notification(title=titulo, body=cuerpo),
                data=data,
                token=token,
                android=self._messaging.AndroidConfig(priority='high'),
            )
            try:
                message_id = self._messaging.send(msg)
            except Exception as e:
                if 'not registered' in str(e).lower() or 'registration-token-not-registered' in str(e).lower():
                    raise TokenNoRegistradoError(str(e))
                raise
        else:
            message_id = f"projects/{self.projectId}/messages/sandbox-{uuid.uuid4().hex[:12]}"
            logger.info(f"[FCM-SANDBOX] {token[:18]}... | {titulo}")

        self.statusDespacho = 200
        return {"status": 200, "message_id": message_id}
