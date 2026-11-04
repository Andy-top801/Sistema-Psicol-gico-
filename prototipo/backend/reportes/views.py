# ==============================================================================
# MÓDULO: reportes/views.py
# DESCRIPCIÓN: Endpoints REST para el módulo de Reportes Personalizables.
#              Acceso restringido a SuperAdmin y Admin Centro.
#              Soporta filtrado y consolidación multi-tenant exclusivo para SuperAdmin.
# ==============================================================================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django_tenants.utils import schema_context

from accounts.models import Rol
from accounts.permissions import EsAdminCentro
from audit.permissions import AuditDeveloperPermission
from tenants.models import Tenant
from .services import ReportEngine, FUENTES_DISPONIBLES


class ReportesPermission:
    """Mixin: permite SuperAdmin O Admin Centro."""
    permission_classes = [EsAdminCentro]


def es_usuario_superadmin(user):
    """Determina si el usuario autenticado tiene rol o permisos globales de SuperAdministrador."""
    if not user or not user.is_authenticated:
        return False
    if getattr(user, 'is_superuser', False):
        return True
    if getattr(user, 'rol', None) and user.rol.nombre == Rol.SUPERADMIN:
        return True
    return False


def ejecutar_reporte_con_tenant(request, fuente, columnas=None, filtros=None, orden=None):
    """
    Ejecuta ReportEngine.generar(...) considerando el rol y permisos:
    - Si es SuperAdmin y especifica tenant/centro: conmuta dinámicamente al esquema de ese centro.
    - Si es SuperAdmin y no especifica (o pasa 'all'/'todos'): consolida los datos de todos los
      centros registrados activos y agrega la columna 'centro_nombre' (Centro Psicológico).
    - Si es Admin Centro: se respeta de manera estricta el aislamiento por esquema del tenant autenticado.
    Retorna: (resultado_dict, nombre_centro_para_encabezado)
    """
    filtros = dict(filtros or {})
    es_super = es_usuario_superadmin(request.user)

    # Identificar si se solicitó un centro específico
    tenant_param = (
        filtros.pop("tenant", None) or
        filtros.pop("centro", None) or
        filtros.pop("schema_name", None) or
        request.query_params.get("tenant") or
        request.query_params.get("centro") or
        ""
    )
    if isinstance(tenant_param, str):
        tenant_param = tenant_param.strip()
    else:
        tenant_param = ""

    if es_super:
        # Caso 1: SuperAdmin solicita un centro psicológico específico
        if tenant_param and tenant_param.lower() not in ("all", "todos", "global", "public", ""):
            target_tenant = Tenant.objects.exclude(schema_name='public').filter(
                Q(schema_name=tenant_param) | Q(slug=tenant_param) | Q(nombre__icontains=tenant_param)
            ).first()

            if not target_tenant:
                raise ValueError(f"Centro psicológico '{tenant_param}' no encontrado en el sistema.")

            with schema_context(target_tenant.schema_name):
                resultado = ReportEngine.generar(fuente, columnas, filtros, orden)
                resultado["centro_consultado"] = {
                    "nombre": target_tenant.nombre,
                    "slug": target_tenant.slug,
                    "schema_name": target_tenant.schema_name
                }
                return resultado, target_tenant.nombre

        # Caso 2: SuperAdmin no especificó centro o solicitó ver todos (Consolidado Multi-Tenant)
        tenants_activos = list(Tenant.objects.exclude(schema_name='public').filter(activo=True).order_by('nombre'))
        datos_consolidados = []
        columnas_base = None
        total_acumulado = 0

        for t in tenants_activos:
            try:
                with schema_context(t.schema_name):
                    sub_res = ReportEngine.generar(fuente, columnas, filtros, orden)
                    for fila in sub_res.get("datos", []):
                        fila_con_centro = dict(fila)
                        fila_con_centro["centro_nombre"] = t.nombre
                        datos_consolidados.append(fila_con_centro)
                    total_acumulado += sub_res.get("total", 0)
                    if columnas_base is None and sub_res.get("columnas"):
                        columnas_base = list(sub_res["columnas"])
            except Exception:
                continue

        col_centro = {"key": "centro_nombre", "label": "Centro Psicológico"}
        columnas_finales = [col_centro] + [c for c in (columnas_base or []) if c["key"] != "centro_nombre"]

        # Ordenar dataset consolidado si se especificó columna
        if orden and orden.get("columna"):
            col_ord = orden["columna"]
            reverse = orden.get("direccion", "ASC").upper() == "DESC"
            datos_consolidados.sort(key=lambda x: str(x.get(col_ord, "")), reverse=reverse)

        resultado = {
            "columnas": columnas_finales,
            "datos": datos_consolidados,
            "total": len(datos_consolidados),
            "resumen": {
                "total_registros": len(datos_consolidados),
                "centros_auditados": len(tenants_activos)
            },
            "es_consolidado_superadmin": True
        }
        return resultado, "Plataforma Global SIGEPSI (Consolidado Multi-Tenant)"

    # Admin Centro regular: aislamiento estricto dentro de su propio esquema
    resultado = ReportEngine.generar(fuente, columnas, filtros, orden)
    tenant_obj = getattr(request, 'tenant', None)
    nombre_centro = tenant_obj.nombre if tenant_obj else "Centro Psicológico"
    return resultado, nombre_centro


# ─────────────────────────────────────────────────────────────
# Metadata: devuelve fuentes, columnas y filtros disponibles
# ─────────────────────────────────────────────────────────────
class ReporteMetadataView(ReportesPermission, APIView):
    """GET /api/reportes/metadata/ — Devuelve las fuentes de datos disponibles con sus columnas y filtros."""

    def get(self, request):
        data = ReportEngine.get_fuentes()
        # Si el usuario es SuperAdmin, inyectar el filtro de Centro Psicológico en todas las fuentes
        if es_usuario_superadmin(request.user):
            centros_opciones = list(
                Tenant.objects.exclude(schema_name='public').filter(activo=True).order_by('nombre').values_list('nombre', flat=True)
            )
            filtro_superadmin = {
                "key": "tenant",
                "label": "Centro Psicológico (Exclusivo SuperAdmin)",
                "type": "select",
                "opciones": ["Todos los Centros"] + centros_opciones
            }
            for fuente_key in data:
                data[fuente_key]["filtros"] = [filtro_superadmin] + data[fuente_key]["filtros"]

        return Response(data)


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

        if fuente == "bitacora":
            perm = AuditDeveloperPermission()
            if not perm.has_permission(request, self):
                return Response(
                    {"error": perm.message},
                    status=status.HTTP_403_FORBIDDEN,
                )

        filtros = {}
        fuente_def = FUENTES_DISPONIBLES[fuente]
        for f_def in fuente_def["filtros"]:
            val = request.query_params.get(f_def["key"])
            if val:
                filtros[f_def["key"]] = val

        if request.query_params.get("tenant"):
            filtros["tenant"] = request.query_params.get("tenant")

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
            resultado, _ = ejecutar_reporte_con_tenant(request, fuente, columnas, filtros, orden)
            return Response(resultado)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response(
                {"error": f"Error al generar reporte: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ==============================================================================
# CU25: Constructor de Reportes Personalizados (QBE), Exportación y Voz (HU-38)
# CAPA BCE: CONTROL (Controller) — CTR_ReportEngineController
# ==============================================================================
class ReportePersonalizadoView(ReportesPermission, APIView):
    """
    CTR_ReportEngineController:
    Controlador para el procesamiento dinámico de consultas QBE y exportación multiformato.
    Soporta filtrado y consolidación multi-tenant para SuperAdmin.
    """

    def post(self, request):
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

        try:
            # Ejecutar consulta considerando permisos y selector de tenant para SuperAdmin
            resultado, nombre_centro = ejecutar_reporte_con_tenant(request, fuente, columnas, filtros, orden)

            # Canal Descarga Directa Excel (.xlsx con OpenPyXL)
            if formato in ["EXCEL", "XLSX"]:
                from .exporters import ExcelExporter
                response = ExcelExporter.generar(resultado, fuente, tenant_name=nombre_centro)
                response['Content-Disposition'] = f'attachment; filename="reporte_{fuente}.xlsx"'
                return response

            # Canal Descarga Directa CSV
            if formato == "CSV":
                from .exporters import CSVExporter
                return CSVExporter.generar(resultado, fuente)

            # Canal Descarga Directa HTML
            if formato == "HTML":
                from .exporters import HTMLExporter
                titulo = f"Reporte de {FUENTES_DISPONIBLES[fuente]['label']} - {nombre_centro}"
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
                asunto = request.data.get("asunto", f"Reporte SIGEPSI: {FUENTES_DISPONIBLES[fuente]['label']} ({nombre_centro})")
                from .exporters import HTMLExporter
                html_content = HTMLExporter.generar(resultado, titulo=asunto)

                from django.core.mail import EmailMultiAlternatives
                from django.conf import settings

                sender = getattr(settings, 'DEFAULT_FROM_EMAIL', 'notificaciones@sigepsi.com')
                text_content = f"Adjunto se encuentra el reporte solicitado de {FUENTES_DISPONIBLES[fuente]['label']} de {nombre_centro} con {resultado['total']} registros."
                msg = EmailMultiAlternatives(asunto, text_content, sender, [destinatario])
                msg.attach_alternative(html_content, "text/html")

                try:
                    from .exporters import ExcelExporter
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

            # Por defecto: Retorno JSON para el visor interactivo
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
    """GET /api/reportes/<fuente>/export/csv/ — Descarga directa en formato CSV."""

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
            resultado, _ = ejecutar_reporte_con_tenant(request, fuente, None, filtros, None)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        from .exporters import CSVExporter
        return CSVExporter.generar(resultado, fuente)


# ─────────────────────────────────────────────────────────────
# Exportar a Excel (.xlsx formal con openpyxl)
# ─────────────────────────────────────────────────────────────
class ReporteExportExcelView(ReportesPermission, APIView):
    """GET /api/reportes/<fuente>/export/excel/ — Descarga directa en Microsoft Excel (.xlsx)."""

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
            resultado, nombre_centro = ejecutar_reporte_con_tenant(request, fuente, columnas, filtros, None)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        from .exporters import ExcelExporter
        return ExcelExporter.generar(resultado, fuente, tenant_name=nombre_centro)


# ─────────────────────────────────────────────────────────────
# Exportar a HTML (descarga o vista directa)
# ─────────────────────────────────────────────────────────────
class ReporteExportHTMLView(ReportesPermission, APIView):
    """GET /api/reportes/<fuente>/export/html/ — Descarga o visualización directa en HTML."""

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
            resultado, nombre_centro = ejecutar_reporte_con_tenant(request, fuente, columnas, filtros, None)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        from .exporters import HTMLExporter
        titulo = f"Reporte de {FUENTES_DISPONIBLES[fuente]['label']} - {nombre_centro}"
        html_content = HTMLExporter.generar(resultado, titulo=titulo)

        from django.http import HttpResponse
        response = HttpResponse(html_content, content_type='text/html; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="reporte_{fuente}.html"'
        return response


# ─────────────────────────────────────────────────────────────
# Envío de Reporte por Correo Electrónico
# ─────────────────────────────────────────────────────────────
class ReporteEmailView(ReportesPermission, APIView):
    """POST /api/reportes/email/ — Envía por correo el reporte en formato HTML/Excel adjunto."""

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

        filtros = request.data.get("filtros", {})
        columnas = request.data.get("columnas")

        try:
            resultado, nombre_centro = ejecutar_reporte_con_tenant(request, fuente, columnas, filtros, None)
            asunto = request.data.get("asunto", f"Reporte SIGEPSI: {FUENTES_DISPONIBLES[fuente]['label']} ({nombre_centro})")
            from .exporters import HTMLExporter
            html_content = HTMLExporter.generar(resultado, titulo=asunto)

            from django.core.mail import EmailMultiAlternatives
            from django.conf import settings

            sender = getattr(settings, 'DEFAULT_FROM_EMAIL', 'notificaciones@sigepsi.com')
            text_content = f"Adjunto se encuentra el reporte solicitado de {FUENTES_DISPONIBLES[fuente]['label']} de {nombre_centro} con {resultado['total']} registros."
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
