import time
import jwt
from django.conf import settings
from agenda.models import Cita, Teleconsulta
from accounts.models import Usuario

class JitsiTokenGenerator:
    """
    Generador de salas y credenciales de acceso para Teleconsultas WebRTC con Jitsi Meet.
    Emite tokens JWT firmados con roles diferenciados:
    - Psicólogo: Rol Moderador con privilegios de control y finalización.
    - Paciente: Rol Asistente / Invitado para streaming multimedia.
    """

    @classmethod
    def generar_acceso(cls, cita: Cita, usuario: Usuario) -> dict:
        # 1. Obtener o crear registro de teleconsulta
        teleconsulta, _ = Teleconsulta.objects.get_or_create(
            cita=cita,
            defaults={'sala_id': f"sigepsi-{str(cita.id)[:8]}-{usuario.id.hex[:4]}"}
        )

        es_psicologo = (cita.psicologo.usuario_id == usuario.id)
        es_paciente = (cita.paciente.usuario_id == usuario.id)

        if not es_psicologo and not es_paciente and not usuario.is_superuser:
            raise PermissionError("No está autorizado para ingresar a esta sala de teleconsulta.")

        es_moderador = es_psicologo or usuario.is_superuser

        # 2. Configuración de Jitsi
        jitsi_domain = getattr(settings, 'JITSI_DOMAIN', 'meet.jit.si')
        app_id = getattr(settings, 'JITSI_APP_ID', 'sigepsi_app')
        app_secret = getattr(settings, 'JITSI_APP_SECRET', 'sigepsi_secret_key_2026')

        now = int(time.time())
        exp = now + 7200  # 2 horas de validez

        payload = {
            "aud": "jitsi",
            "iss": app_id,
            "sub": jitsi_domain,
            "room": teleconsulta.sala_id,
            "iat": now,
            "nbf": now - 10,
            "exp": exp,
            "context": {
                "user": {
                    "id": str(usuario.id),
                    "name": f"{usuario.nombre} {usuario.apellido}".strip(),
                    "email": usuario.email,
                    "moderator": es_moderador,
                    "avatar": ""
                },
                "features": {
                    "recording": es_moderador,
                    "livestreaming": False,
                    "screen-sharing": True
                }
            }
        }

        token = jwt.encode(payload, app_secret, algorithm="HS256")
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        teleconsulta.jwt_room_token = token
        teleconsulta.save(update_fields=['jwt_room_token'])

        return {
            "sala_id": teleconsulta.sala_id,
            "domain": jitsi_domain,
            "jwt_token": token,
            "es_moderador": es_moderador,
            "usuario": {
                "id": str(usuario.id),
                "nombre": f"{usuario.nombre} {usuario.apellido}".strip(),
                "email": usuario.email,
            },
            "cita_id": str(cita.id),
            "modalidad": cita.modalidad,
            "estado": cita.estado
        }
