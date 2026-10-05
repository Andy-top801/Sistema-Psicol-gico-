# ==============================================================================
# MÓDULO: audit/views.py — CU5: Bitácora Confidencial y Llave Única del Desarrollador (HU-37)
# CAPA BCE: CONTROL (Controller) — CTR_AuditLogController
# DIAGRAMA DE SECUENCIA CU5 (sprint2.md):
#   Actor (SuperAdmin / Developer) → IU_ModalLlaveDesarrollador: 1: ingresar_llave_maestra(developer_key, fecha_consulta, tenant_filtro)
#   IU_ModalLlaveDesarrollador → CTR_AuditLogController: 2: GET /api/v1/audit/log/?date=... (Header: X-Developer-Key)
#   CTR_AuditLogController → CTR_FernetDecryptor: 3: validar_firma_hmac_sha256(developer_key)
#   CTR_FernetDecryptor --> CTR_AuditLogController: 4: resultado_validacion_clave(es_valida)
#   alt Llave de Desarrollador Inválida o No Proporcionada
#     CTR_AuditLogController --> IU_ModalLlaveDesarrollador: 5a: HTTP 403 Forbidden ("Llave de Desarrollador Inválida - Acceso Denegado")
#     IU_ModalLlaveDesarrollador --> Developer: 6a: mostrar_alerta_seguridad_bloqueo("Intento de acceso auditado y bloqueado")
#   else Llave de Desarrollador Válida
#     CTR_AuditLogController → CE_EncryptedLogFile: 5b: abrir_archivo_cifrado(audit-YYYY-MM-DD.log.enc, modo=0600)
#     CE_EncryptedLogFile --> CTR_AuditLogController: 6b: stream_lineas_cifradas_bytes()
#     loop Por cada línea registrada en la bitácora
#       CTR_AuditLogController → CTR_FernetDecryptor: 7b: decrypt_payload_fernet(linea_cifrada, derived_aes_key)
#       CTR_FernetDecryptor --> CTR_AuditLogController: 8b: json_payload_en_claro(ip, user_id, action, timestamp_bolivia)
#       opt Usuario Autenticado
#         CTR_AuditLogController → CE_Usuario: 9b: resolver_email_y_rol(user_id)
#         CE_Usuario --> CTR_AuditLogController: 10b: datos_usuario(email, rol_tenant)
#       end
#     end
#     CTR_AuditLogController --> IU_VisorBitacoraForense: 11b: HTTP 200 OK [eventos_descifrados_auditados]
#     IU_VisorBitacoraForense --> Developer: 12b: renderizar_tabla_forense(ip, usuario, accion, hora_gmt4_bolivia)
#   end
# ==============================================================================
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import AuditDeveloperPermission
from .serializers import AuditEventSerializer
from .services import parse_date, read_events


class AuditLogView(APIView):
    """
    CTR_AuditLogController:
    Controlador para la consulta y descifrado forense de la bitácora confidencial en disco.
    Exige la llave única de desarrollador (X-Developer-Key) y privilegios de SuperAdmin.
    """
    # CU5 Pasos 3 y 4: validar_firma_hmac_sha256 (si inválida -> Pasos 5a-6a: 403 Forbidden)
    permission_classes = [AuditDeveloperPermission]

    def get(self, request):
        # CU5 Paso 2: GET /api/v1/audit/log/?date=...
        try:
            # CU5 Pasos 5b a 10b: abrir_archivo_cifrado, decrypt_payload_fernet y resolver_email_y_rol
            events = read_events(parse_date(request.query_params.get("date")))
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        except Exception:
            return Response(
                {"error": "La bitacora no esta disponible o la llave es invalida."},
                status=503,
            )

        tenant = request.query_params.get("tenant")
        if tenant:
            events = [event for event in events if event.get("tenant") == tenant]

        # CU5 Paso 11b: HTTP 200 OK [eventos_descifrados_auditados]
        return Response(AuditEventSerializer(events, many=True).data)
