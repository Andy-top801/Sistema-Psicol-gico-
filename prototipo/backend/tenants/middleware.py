from django.db import connection
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import get_public_schema_name, schema_context
from tenants.models import Tenant, Dominio

class SigepsiTenantMiddleware(MiddlewareMixin):
    """
    Middleware Multi-Tenant personalizado para SIGEPSI.
    Identifica el tenant activo mediante:
    1. Header HTTP 'X-Tenant-ID' (UUID o Slug)
    2. Subdominio en la cabecera 'Host'
    3. Si no se especifica o es público, activa el esquema 'public'.
    """

    def process_request(self, request):
        """
        Interviene en los diagramas de comunicación:
          CU2 (Login): Paso 3-4 (Validar tenant y conmutar schema -> Esquema PostgreSQL activo)
          CU3 (Usuarios): Paso 3-4 (Validar TenantMiddleware -> Contexto tenant verificado)
          CU4 (Roles): Paso 3-4 (Validar esquema tenant -> Permisos administrativos verificados)
        """
        # Conexión por defecto a esquema public
        connection.set_schema_to_public()
        request.tenant = None

        # 1. Verificar Header X-Tenant-ID / X-Tenant-Slug / META / GET
        # --- Paso 3: Validar tenant y conmutar schema ---
        tenant_header = (
            request.headers.get('X-Tenant-ID') or
            request.headers.get('X-Tenant-Slug') or
            request.headers.get('x-tenant-id') or
            request.headers.get('x-tenant-slug') or
            request.META.get('HTTP_X_TENANT_ID') or
            request.META.get('HTTP_X_TENANT_SLUG') or
            request.GET.get('tenant')
        )

        if tenant_header:
            tenant = None
            if tenant_header.lower() == 'public':
                connection.set_schema_to_public()
                return None

            try:
                # Intentar por UUID o por slug o schema_name
                try:
                    tenant = Tenant.objects.get(id=tenant_header)
                except Exception:
                    tenant = Tenant.objects.get(slug=tenant_header)
            except Tenant.DoesNotExist:
                try:
                    tenant = Tenant.objects.get(schema_name=tenant_header)
                except Tenant.DoesNotExist:
                    return JsonResponse(
                        {"error": "Centro psicológico (Tenant) no encontrado", "codigo": "TENANT_NOT_FOUND"},
                        status=404
                    )

            if not tenant.activo:
                return JsonResponse(
                    {"error": "El centro psicológico se encuentra suspendido o inactivo", "codigo": "TENANT_INACTIVE"},
                    status=403
                )

            # --- Paso 4: Esquema PostgreSQL activo / Contexto tenant verificado ---
            request.tenant = tenant
            connection.set_tenant(tenant)
            return None

        # 2. Verificar por Dominio / Subdominio
        hostname = request.get_host().split(':')[0].lower()
        if hostname and hostname not in ['localhost', '127.0.0.1', 'testserver']:
            try:
                domain_obj = Dominio.objects.select_related('tenant').get(domain=hostname)
                if not domain_obj.tenant.activo:
                    return JsonResponse(
                        {"error": "El centro psicológico se encuentra suspendido", "codigo": "TENANT_INACTIVE"},
                        status=403
                    )
                request.tenant = domain_obj.tenant
                connection.set_tenant(domain_obj.tenant)
                return None
            except Dominio.DoesNotExist:
                pass

        # Si no hay tenant específico, operar en esquema public
        connection.set_schema_to_public()
        return None
