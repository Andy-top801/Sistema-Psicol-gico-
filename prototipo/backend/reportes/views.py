# ==============================================================================
# MÓDULO: reportes/views.py
# DESCRIPCIÓN: Endpoints REST para el módulo de Reportes Personalizables.
#              Acceso restringido a SuperAdmin y Admin Centro.
# ==============================================================================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import EsSuperAdmin, EsAdminCentro
from .services import ReportEngine, FUENTES_DISPONIBLES


class ReportesPermission:
    """Mixin: permite SuperAdmin O Admin Centro."""
    permission_classes = [EsAdminCentro]


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

        # Bitácora sólo para SuperAdmin
        if fuente == "bitacora":
            perm = EsSuperAdmin()
            if not perm.has_permission(request, self):
                return Response(
                    {"error": "La bitácora solo es accesible para SuperAdmin."},
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

        try:
            resultado = ReportEngine.generar(fuente, columnas, filtros, orden)
            return Response(resultado)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response(
                {"error": f"Error al generar reporte: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ─────────────────────────────────────────────────────────────
# Reporte personalizado (POST con body JSON)
# ─────────────────────────────────────────────────────────────
class ReportePersonalizadoView(ReportesPermission, APIView):
    """
    POST /api/reportes/personalizado/
    Body: { "fuente": "citas", "columnas": ["fecha", "estado"], "filtros": {...}, "orden": {...} }
    """

    def post(self, request):
        fuente = request.data.get("fuente")
        if not fuente or fuente not in FUENTES_DISPONIBLES:
            return Response(
                {"error": f"Fuente requerida. Opciones: {list(FUENTES_DISPONIBLES.keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if fuente == "bitacora":
            perm = EsSuperAdmin()
            if not perm.has_permission(request, self):
                return Response(
                    {"error": "La bitácora solo es accesible para SuperAdmin."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        columnas = request.data.get("columnas")
        filtros = request.data.get("filtros", {})
        orden = request.data.get("orden")

        try:
            resultado = ReportEngine.generar(fuente, columnas, filtros, orden)
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
class ReporteExportCSVView(ReportesPermission, APIView):
    """
    GET /api/reportes/<fuente>/export/csv/
    Descarga directa en formato CSV.
    """

    def get(self, request, fuente):
        if fuente not in FUENTES_DISPONIBLES:
            return Response({"error": "Fuente no reconocida."}, status=status.HTTP_400_BAD_REQUEST)

        if fuente == "bitacora":
            perm = EsSuperAdmin()
            if not perm.has_permission(request, self):
                return Response({"error": "Acceso denegado."}, status=status.HTTP_403_FORBIDDEN)

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
            perm = EsSuperAdmin()
            if not perm.has_permission(request, self):
                return Response({"error": "Acceso denegado."}, status=status.HTTP_403_FORBIDDEN)

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
            perm = EsSuperAdmin()
            if not perm.has_permission(request, self):
                return Response({"error": "Acceso denegado."}, status=status.HTTP_403_FORBIDDEN)

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
            perm = EsSuperAdmin()
            if not perm.has_permission(request, self):
                return Response({"error": "Acceso denegado a bitácora."}, status=status.HTTP_403_FORBIDDEN)

        asunto = request.data.get("asunto", f"Reporte SIGEPSI: {FUENTES_DISPONIBLES[fuente]['label']}")
        filtros = request.data.get("filtros", {})
        columnas = request.data.get("columnas")

        try:
            resultado = ReportEngine.generar(fuente, columnas, filtros, None)
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
