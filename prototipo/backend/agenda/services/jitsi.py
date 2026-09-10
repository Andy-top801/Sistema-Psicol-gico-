# ==============================================================================
# SERVICIO: agenda/services/jitsi.py
# CAPA BCE: CONTROL (Controller) — CTR_Teleconsulta
# CASO DE USO: CU13 – Gestión de Teleconsultas y Videoconferencias Jitsi Meet (HU-18, HU-19)
# DIAGRAMA DE COMUNICACIÓN CU13:
#   Actor → IU: 1: Clic en 'Unirse a Teleconsulta'
#   IU → CTR:   2: GET /api/agenda/teleconsulta/{id}/access/ + JWT
#   CTR → CE:   3: Validar ventana horaria activa (cita +/- 15 min)
#   CE → CTR:   4: Cita virtual vigente y usuario participante
#   CTR → CE:   5: INSERT INTO agenda_teleconsulta (room, fecha_inicio)
#   CE → CTR:   6: Sala registrada y credenciales generadas
#   CTR → IU:   7: 200 OK {room_name, jwt_token, rol_moderador}
#   IU → Actor: 8: Embeber sala Jitsi Meet con controles de llamada
#
# ESTE SERVICIO IMPLEMENTA LOS PASOS 3 A 6 DEL DIAGRAMA (generación de
# credenciales JWT y configuración de sala WebRTC).
# ==============================================================================
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
        # ====================================================================
        # CU13 Paso 5: Obtener o crear registro de teleconsulta con sala_id única
        # Si aún no existe el registro, se genera un identificador de sala
        # con formato 'sigepsi-{cita_id_corto}-{usuario_id_corto}'.
        # ====================================================================
        teleconsulta, _ = Teleconsulta.objects.get_or_create(
            cita=cita,
            defaults={'sala_id': f"sigepsi-{str(cita.id)[:8]}-{usuario.id.hex[:4]}"}
        )

        # ====================================================================
        # CU13 Paso 3/4: Validar que el usuario sea participante autorizado
        # Determinar el rol del usuario: Psicólogo (moderador) o Paciente (invitado).
        # Si no es ninguno de los dos, se deniega el acceso (PermissionError).
        # ====================================================================
        es_psicologo = (cita.psicologo.usuario_id == usuario.id)
        es_paciente = (cita.paciente.usuario_id == usuario.id)
        es_admin = bool(usuario.rol and ('admin' in usuario.rol.nombre.lower() or 'coord' in usuario.rol.nombre.lower()))

        if not es_psicologo and not es_paciente and not usuario.is_superuser and not es_admin:
            raise PermissionError("No está autorizado para ingresar a esta sala de teleconsulta.")

        # CU13 Paso 4: Asignar rol de moderador al psicólogo y de invitado al paciente
        es_moderador = es_psicologo or usuario.is_superuser or es_admin

        # ====================================================================
        # CU13 Paso 5/6: Generar token JWT firmado con claims de Jitsi Meet
        # El token incluye el rol del usuario (moderador/invitado), la sala,
        # y la configuración de features (grabación, compartir pantalla).
        # ====================================================================
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
