# ==============================================================================
# MÓDULO: reportes/views.py
# DESCRIPCIÓN: Endpoints REST para el módulo de Reportes Personalizables.
#              Acceso restringido a SuperAdmin y Admin Centro.
# ==============================================================================
import re
import unicodedata
from contextlib import nullcontext

from django_tenants.utils import get_public_schema_name, schema_context
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import EsAdminCentro, EsSuperAdmin
from audit.permissions import AuditDeveloperPermission
from tenants.models import Tenant
from .services import ReportEngine, FUENTES_DISPONIBLES


class ReportesPermission:
    """Mixin: permite SuperAdmin O Admin Centro."""
    permission_classes = [EsAdminCentro]


# Palabras genéricas que se ignoran al comparar nombres: "Clínica Esperanza" == "esperanza".
_RELLENO_CLINICA = {"clinica", "centro", "y", "psicologico", "psicologica", "psicologia", "de", "del", "la", "el", "los", "las"}


def _normalizar_clinica(texto):
    texto = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()
    return " ".join(w for w in re.findall(r"[a-z0-9]+", texto) if w not in _RELLENO_CLINICA)


def resolver_clinica(request):
    """
    El SuperAdmin puede pedir el reporte de una clínica concreta enviando "clinica" (nombre o slug).
    Devuelve (tenant | None, Response de error | None). Un Admin de Centro nunca puede saltar a otro tenant.
    """
    nombre = str(request.data.get("clinica") or "").strip()
    if not nombre:
        return None, None
    if not EsSuperAdmin().has_permission(request, None):
        return None, Response(
            {"error": "Solo el SuperAdmin puede elegir la clínica del reporte."},
            status=status.HTTP_403_FORBIDDEN,
        )

    buscado = _normalizar_clinica(nombre)
    tenants = list(Tenant.objects.exclude(schema_name=get_public_schema_name()))
    if not buscado:
        candidatos = []
    else:
        exactos = [t for t in tenants if buscado in (_normalizar_clinica(t.nombre), _normalizar_clinica(t.slug))]
        candidatos = exactos or [
            t for t in tenants
            if buscado in _normalizar_clinica(t.nombre) or buscado in _normalizar_clinica(t.slug)
        ]

    if not candidatos:
        return None, Response(
            {"error": f"No se encontró la clínica '{nombre}'.", "clinicas_disponibles": sorted(t.nombre for t in tenants)},
            status=status.HTTP_404_NOT_FOUND,
        )
    if len(candidatos) > 1:
        return None, Response(
            {"error": f"'{nombre}' coincide con varias clínicas, sé más específico.", "clinicas_disponibles": sorted(t.nombre for t in candidatos)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    tenant = candidatos[0]
    if not tenant.activo:
        return None, Response(
            {"error": f"La clínica '{tenant.nombre}' está suspendida o inactiva."},
            status=status.HTTP_403_FORBIDDEN,
        )
    return tenant, None


def generar_en_clinica(tenant, *args):
    """Ejecuta el ReportEngine dentro del esquema de la clínica elegida (o el del request si no se eligió)."""
    with schema_context(tenant.schema_name) if tenant else nullcontext():
        resultado = ReportEngine.generar(*args)
    if tenant:
        resultado["clinica"] = tenant.nombre
    return resultado


# ─────────────────────────────────────────────────────────────
# Metadata: devuelve fuentes, columnas y filtros disponibles
# ─────────────────────────────────────────────────────────────
class ReporteMetadataView(ReportesPermission, APIView):
    """GET /api/reportes/metadata/ — Devuelve las fuentes de datos disponibles con sus columnas y filtros."""

    def get(self, request):
        return Response(ReportEngine.get_fuentes())


# ─────────────────────────────────────────────────────────────
# Reporte genérico por fuente (GET con query params)
# ─────────────────────────────────────────────────────────────
class ReporteGenericoView(ReportesPermission, APIView):
    """
    GET /api/reportes/<fuente>/
    Acepta filtros como query params. Columnas y orden opcionales.
    """

    def get(self, request, fuente):
        if fuente not in FUENTES_DISPONIBLES:
            return Response(
                {"error": f"Fuente '{fuente}' no reconocida. Opciones: {list(FUENTES_DISPONIBLES.keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Audit records require SuperAdmin and the dedicated key.
        if fuente == "bitacora":
            perm = AuditDeveloperPermission()
            if not perm.has_permission(request, self):
                return Response(
                    {"error": perm.message},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if fuente == "facturas_saas" and not EsSuperAdmin().has_permission(request, self):
            return Response(
                {"error": "Solo el SuperAdmin puede consultar la facturación SaaS global."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Extraer filtros de query params
        filtros = {}
        fuente_def = FUENTES_DISPONIBLES[fuente]
        for f_def in fuente_def["filtros"]:
            val = request.query_params.get(f_def["key"])
            if val:
                filtros[f_def["key"]] = val

        # Columnas opcionales (comma-separated)
        columnas_raw = request.query_params.get("columnas")
        columnas = columnas_raw.split(",") if columnas_raw else None

        # Orden opcional
        orden = None
        orden_col = request.query_params.get("orden_columna")
        if orden_col:
            orden = {
                "columna": orden_col,
                "direccion": request.query_params.get("orden_dir", "ASC"),
            }

        page = request.query_params.get("page")
        page_size = request.query_params.get("page_size")

        try:
            resultado = ReportEngine.generar(fuente, columnas, filtros, orden, page=page, page_size=page_size)
            return Response(resultado)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response(
                {"error": f"Error al generar reporte: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ==============================================================================
# MÓDULO: reportes/views.py — CU25: Constructor de Reportes Personalizados (QBE), Exportación y Voz (HU-38)
# CAPA BCE: CONTROL (Controller) — CTR_ReportEngineController
# DIAGRAMA DE SECUENCIA CU25 (sprint2.md):
#   alt Modo 1: Comandos de Voz (Web Speech API)
#     Actor → IU_ConstructorReportesQBE: 1a: presionar_boton_microfono()
#     Actor → CTR_SpeechParserService: 2a: dictar_instruccion(...)
#     CTR_SpeechParserService → CTR_SpeechParserService: 3a: web_speech_recognition_y_nlp_parse()
#     CTR_SpeechParserService --> IU_ConstructorReportesQBE: 4a: parametros_extraidos(fuente, filtros)
#     IU_ConstructorReportesQBE --> Actor: 5a: actualizar_formulario_qbe_reactivo(filtros_detectados)
#   else Modo 2: Configuración Manual QBE
#     Actor → IU_ConstructorReportesQBE: 1b: seleccionar_columnas_y_filtros(fuente, columnas[], filtros[], orden)
#   end
#   Actor → IU_ConstructorReportesQBE: 6: solicitar_ejecucion_y_exportacion(formato='EXCEL')
#   IU_ConstructorReportesQBE → CTR_ReportEngineController: 7: POST /api/v1/reportes/personalizado/ (payload_qbe, formato='EXCEL')
#   CTR_ReportEngineController → CTR_ReportEngineController: 8: construir_query_dinamico_con_aislamiento_tenant()
#   CTR_ReportEngineController → CE_CitaAgenda / CE_HistoriaClinica: 9-11: SELECT columnas FROM ... WHERE tenant_id=...
#   CE --> CTR_ReportEngineController: 12: dataset_relacional_proyectado()
#   alt Canal Excel (.xlsx con OpenPyXL)
#     CTR_ReportEngineController → CTR_OpenPyXLExporter: 13a: generar_libro_excel(dataset, encabezados)
#     CTR_OpenPyXLExporter --> CTR_ReportEngineController: 15a: archivo_binario_xlsx_bytes()
#     CTR_ReportEngineController --> IU_VisorReporteExportador: 16a: HTTP 200 OK (Content-Disposition: attachment; filename=reporte.xlsx)
#     IU_VisorReporteExportador --> Actor: 17a: disparar_descarga_automatica_en_navegador("reporte.xlsx")
#   else Canal Correo Electrónico (SMTP)
#     CTR_ReportEngineController → CTR_ReportEngineController: 13b: adjuntar_documento_y_enviar_smtp(email_destino, dataset)
#     CTR_ReportEngineController --> IU_VisorReporteExportador: 14b: HTTP 200 OK ("Reporte enviado exitosamente por eMail")
#   end
# ==============================================================================
class ReportePersonalizadoView(ReportesPermission, APIView):
    """
    CTR_ReportEngineController:
    Controlador para el procesamiento dinámico de consultas QBE y exportación multiformato.
    """

    def post(self, request):
        # CU25 Paso 7: POST /api/v1/reportes/personalizado/ (payload_qbe, formato)
        fuente = request.data.get("fuente")
        if not fuente or fuente not in FUENTES_DISPONIBLES:
            return Response(
                {"error": f"Fuente requerida. Opciones: {list(FUENTES_DISPONIBLES.keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if fuente == "bitacora":
            perm = AuditDeveloperPermission()
            if not perm.has_permission(request, self):
                return Response({"error": perm.message}, status=status.HTTP_403_FORBIDDEN)

        columnas = request.data.get("columnas")
        filtros = request.data.get("filtros", {})
        orden = request.data.get("orden")
        formato = (request.data.get("formato") or "").upper()

        clinica, error = resolver_clinica(request)
        if error:
            return error
        tenant_obj = clinica or getattr(request, 'tenant', None)

        try:
            # CU25 Pasos 8 a 12: construir_query_dinamico y proyectar dataset relacional
            resultado = generar_en_clinica(clinica, fuente, columnas, filtros, orden)

            # CU25 Pasos 13a a 17a: Canal Descarga Directa Excel (.xlsx con OpenPyXL)
            if formato in ["EXCEL", "XLSX"]:
                from .exporters import ExcelExporter
                nombre_centro = tenant_obj.nombre if tenant_obj else "Centro Psicológico"
                response = ExcelExporter.generar(resultado, fuente, tenant_name=nombre_centro)
                response['Content-Disposition'] = f'attachment; filename="reporte_{fuente}.xlsx"'
                return response

            # Canal Descarga Directa PDF oficial (ReportLab - HU-53)
            if formato == "PDF":
                from .exporters import PDFExporter
                nombre_centro = tenant_obj.nombre if tenant_obj else "Centro Psicológico"
                return PDFExporter.generar(resultado, fuente, tenant_name=nombre_centro)

            # Canal Descarga Directa CSV
            if formato == "CSV":
                from .exporters import CSVExporter
                return CSVExporter.generar(resultado, fuente)

            # Canal Descarga Directa HTML
            if formato == "HTML":
                from .exporters import HTMLExporter
                titulo = f"Reporte de {FUENTES_DISPONIBLES[fuente]['label']}"
                html_content = HTMLExporter.generar(resultado, titulo=titulo)
                from django.http import HttpResponse
                response = HttpResponse(html_content, content_type='text/html; charset=utf-8')
                response['Content-Disposition'] = f'attachment; filename="reporte_{fuente}.html"'
                return response

            # Canal Correo Electrónico (SMTP)
            if formato in ["EMAIL", "SMTP"]:
                destinatario = request.data.get("email")
                if not destinatario:
                    return Response(
                        {"error": "El correo de destino es obligatorio para envío por email."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                asunto = request.data.get("asunto", f"Reporte SIGEPSI: {FUENTES_DISPONIBLES[fuente]['label']}")
                from .exporters import HTMLExporter
                html_content = HTMLExporter.generar(resultado, titulo=asunto)

                from django.core.mail import EmailMultiAlternatives
                from django.conf import settings

                sender = getattr(settings, 'DEFAULT_FROM_EMAIL', 'notificaciones@sigepsi.com')
                text_content = f"Adjunto se encuentra el reporte solicitado de {FUENTES_DISPONIBLES[fuente]['label']} con {resultado['total']} registros."
                msg = EmailMultiAlternatives(asunto, text_content, sender, [destinatario])
                msg.attach_alternative(html_content, "text/html")

                try:
                    from .exporters import ExcelExporter
                    nombre_centro = tenant_obj.nombre if tenant_obj else "Centro Psicológico"
                    excel_resp = ExcelExporter.generar(resultado, fuente, tenant_name=nombre_centro)
                    msg.attach(f"reporte_{fuente}.xlsx", excel_resp.content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                except Exception:
                    pass

                msg.send(fail_silently=False)
                return Response({
                    "mensaje": f"Reporte enviado exitosamente por correo a {destinatario}",
                    "total_registros": resultado["total"],
                    "destinatario": destinatario
                }, status=status.HTTP_200_OK)

            # Por defecto: Retorno relacional proyectado (JSON) para visor interactivo
            return Response(resultado)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response(
                {"error": f"Error al generar reporte: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ─────────────────────────────────────────────────────────────
# Exportar a CSV (descarga directa)
# ─────────────────────────────────────────────────────────────
class ReporteExportPDFView(ReportesPermission, APIView):
    """
    GET /api/reportes/<fuente>/export/pdf/
    Descarga directa en formato PDF oficial multipágina (ReportLab - HU-53).
    """

    def get(self, request, fuente):
        if fuente not in FUENTES_DISPONIBLES:
            return Response({"error": "Fuente no reconocida."}, status=status.HTTP_400_BAD_REQUEST)

        if fuente == "bitacora":
            perm = AuditDeveloperPermission()
            if not perm.has_permission(request, self):
                return Response({"error": perm.message}, status=status.HTTP_403_FORBIDDEN)

        if fuente == "facturas_saas" and not EsSuperAdmin().has_permission(request, self):
            return Response(
                {"error": "Solo el SuperAdmin puede exportar facturación SaaS."},
                status=status.HTTP_403_FORBIDDEN,
            )

        filtros = {}
        for f_def in FUENTES_DISPONIBLES[fuente]["filtros"]:
            val = request.query_params.get(f_def["key"])
            if val:
                filtros[f_def["key"]] = val

        columnas_raw = request.query_params.get("columnas")
        columnas = columnas_raw.split(",") if columnas_raw else None

        orden = None
        orden_col = request.query_params.get("orden_columna")
        if orden_col:
            orden = {
                "columna": orden_col,
                "direccion": request.query_params.get("orden_dir", "ASC"),
            }

        try:
            resultado = ReportEngine.generar(fuente, columnas, filtros, orden)
            from .exporters import PDFExporter
            tenant_obj = getattr(request, 'tenant', None)
            nombre_centro = tenant_obj.nombre if tenant_obj else "Centro Psicológico"
            return PDFExporter.generar(resultado, fuente, tenant_name=nombre_centro)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response(
                {"error": f"Error al exportar PDF: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ReporteExportCSVView(ReportesPermission, APIView):
    """
    GET /api/reportes/<fuente>/export/csv/
    Descarga directa en formato CSV.
    """

    def get(self, request, fuente):
        if fuente not in FUENTES_DISPONIBLES:
            return Response({"error": "Fuente no reconocida."}, status=status.HTTP_400_BAD_REQUEST)

        if fuente == "bitacora":
            perm = AuditDeveloperPermission()
            if not perm.has_permission(request, self):
                return Response({"error": perm.message}, status=status.HTTP_403_FORBIDDEN)

        filtros = {}
        for f_def in FUENTES_DISPONIBLES[fuente]["filtros"]:
            val = request.query_params.get(f_def["key"])
            if val:
                filtros[f_def["key"]] = val

        try:
            resultado = ReportEngine.generar(fuente, None, filtros, None)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        from .exporters import CSVExporter
        response = CSVExporter.generar(resultado, fuente)
        return response


# ─────────────────────────────────────────────────────────────
# Exportar a Excel (.xlsx formal con openpyxl)
# ─────────────────────────────────────────────────────────────
class ReporteExportExcelView(ReportesPermission, APIView):
    """
    GET /api/reportes/<fuente>/export/excel/
    Descarga directa en formato Microsoft Excel (.xlsx) con membrete y estilos.
    """

    def get(self, request, fuente):
        if fuente not in FUENTES_DISPONIBLES:
            return Response({"error": "Fuente no reconocida."}, status=status.HTTP_400_BAD_REQUEST)

        if fuente == "bitacora":
            perm = AuditDeveloperPermission()
            if not perm.has_permission(request, self):
                return Response({"error": perm.message}, status=status.HTTP_403_FORBIDDEN)

        filtros = {}
        for f_def in FUENTES_DISPONIBLES[fuente]["filtros"]:
            val = request.query_params.get(f_def["key"])
            if val:
                filtros[f_def["key"]] = val

        columnas_raw = request.query_params.get("columnas")
        columnas = columnas_raw.split(",") if columnas_raw else None

        try:
            resultado = ReportEngine.generar(fuente, columnas, filtros, None)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        from .exporters import ExcelExporter
        tenant_obj = getattr(request, 'tenant', None)
        nombre_centro = tenant_obj.nombre if tenant_obj else "Centro Psicológico"
        return ExcelExporter.generar(resultado, fuente, tenant_name=nombre_centro)


# ─────────────────────────────────────────────────────────────
# Exportar a HTML (descarga o vista directa)
# ─────────────────────────────────────────────────────────────
class ReporteExportHTMLView(ReportesPermission, APIView):
    """
    GET /api/reportes/<fuente>/export/html/
    Descarga o visualización directa en formato HTML.
    """

    def get(self, request, fuente):
        if fuente not in FUENTES_DISPONIBLES:
            return Response({"error": "Fuente no reconocida."}, status=status.HTTP_400_BAD_REQUEST)

        if fuente == "bitacora":
            perm = AuditDeveloperPermission()
            if not perm.has_permission(request, self):
                return Response({"error": perm.message}, status=status.HTTP_403_FORBIDDEN)

        filtros = {}
        for f_def in FUENTES_DISPONIBLES[fuente]["filtros"]:
            val = request.query_params.get(f_def["key"])
            if val:
                filtros[f_def["key"]] = val

        columnas_raw = request.query_params.get("columnas")
        columnas = columnas_raw.split(",") if columnas_raw else None

        try:
            resultado = ReportEngine.generar(fuente, columnas, filtros, None)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        from .exporters import HTMLExporter
        titulo = f"Reporte de {FUENTES_DISPONIBLES[fuente]['label']}"
        html_content = HTMLExporter.generar(resultado, titulo=titulo)

        from django.http import HttpResponse
        response = HttpResponse(html_content, content_type='text/html; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="reporte_{fuente}.html"'
        return response


# ─────────────────────────────────────────────────────────────
# Envío de Reporte por Correo Electrónico
# ─────────────────────────────────────────────────────────────
class ReporteEmailView(ReportesPermission, APIView):
    """
    POST /api/reportes/email/
    Body: { "email": "admin@centro.com", "asunto": "...", "fuente": "...", "filtros": {...}, "columnas": [...] }
    Envía por correo el reporte en formato HTML adjunto o en el cuerpo.
    """

    def post(self, request):
        destinatario = request.data.get("email")
        if not destinatario:
            return Response({"error": "El correo de destino es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        fuente = request.data.get("fuente")
        if not fuente or fuente not in FUENTES_DISPONIBLES:
            return Response({"error": "Fuente requerida y válida."}, status=status.HTTP_400_BAD_REQUEST)

        if fuente == "bitacora":
            perm = AuditDeveloperPermission()
            if not perm.has_permission(request, self):
                return Response({"error": perm.message}, status=status.HTTP_403_FORBIDDEN)

        asunto = request.data.get("asunto", f"Reporte SIGEPSI: {FUENTES_DISPONIBLES[fuente]['label']}")
        filtros = request.data.get("filtros", {})
        columnas = request.data.get("columnas")

        clinica, error = resolver_clinica(request)
        if error:
            return error

        try:
            resultado = generar_en_clinica(clinica, fuente, columnas, filtros, None)
            from .exporters import HTMLExporter
            html_content = HTMLExporter.generar(resultado, titulo=asunto)

            from django.core.mail import EmailMultiAlternatives
            from django.conf import settings

            sender = getattr(settings, 'DEFAULT_FROM_EMAIL', 'notificaciones@sigepsi.com')
            text_content = f"Adjunto se encuentra el reporte solicitado de {FUENTES_DISPONIBLES[fuente]['label']} con {resultado['total']} registros."
            msg = EmailMultiAlternatives(asunto, text_content, sender, [destinatario])
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            return Response({
                "mensaje": f"Reporte enviado exitosamente a {destinatario}",
                "total_registros": resultado["total"],
                "destinatario": destinatario
            }, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(
                {"error": f"Error al procesar el envío de correo: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
