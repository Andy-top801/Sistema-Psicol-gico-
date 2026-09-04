from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from tenants.models import Tenant
from tenants.serializers import TenantSerializer
from accounts.permissions import EsSuperAdmin

class TenantViewSet(viewsets.ModelViewSet):
    """
    ═══════════════════════════════════════════════════════════════════════════
    CU1: Gestionar Centros Psicológicos y Configuración Multi-Tenant
         (HU-03, HU-04, HU-07, HU-08)
    Diagrama de Comunicación – CTR_TenantService (Django)
    Participantes:
      Actor  → SuperAdministrador
      IU     → IU_FormularioCentro (Angular)
      CTR    → CTR_TenantService (Django)  ← ESTE ARCHIVO
      CE     → CE_Tenant_y_Dominio (PostgreSQL)

    Flujo del diagrama de comunicación (POST /api/tenants/):
      Paso 2: POST /api/tenants/ (petición recibida con datos del centro)
      Paso 3: Valida disponibilidad Dominio
      Paso 4: Dominio disponible
      Paso 5: insert(Tenant, Dominio)
      Paso 6: Registros creados
      Paso 7: CREATE SCHEMA y Migraciones
      Paso 8: Esquema creado
      Paso 9: 201 Created (respuesta al frontend)
    ═══════════════════════════════════════════════════════════════════════════
    CRUD de Centros Psicológicos (Tenants).
    Permite al SuperAdministrador registrar, listar, editar y suspender centros.
    """
    queryset = Tenant.objects.all().order_by('-fecha_creacion')
    serializer_class = TenantSerializer

    def get_permissions(self):
        # Permitir listar centros activos para el selector de login
        if self.action in ['list', 'public_list']:
            return [AllowAny()]
        return [EsSuperAdmin()]

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='public')
    def public_list(self, request):
        """Retorna la lista de centros activos para el selector en pantallas de login."""
        tenants = Tenant.objects.filter(activo=True).values('id', 'nombre', 'slug', 'schema_name')
        return Response(list(tenants))

    @action(detail=True, methods=['post'], permission_classes=[EsSuperAdmin])
    def suspender(self, request, pk=None):
        tenant = self.get_object()
        tenant.suspender()
        return Response({"mensaje": f"Centro '{tenant.nombre}' suspendido exitosamente.", "activo": False})

    @action(detail=True, methods=['post'], permission_classes=[EsSuperAdmin])
    def activar(self, request, pk=None):
        tenant = self.get_object()
        tenant.activar()
        return Response({"mensaje": f"Centro '{tenant.nombre}' reactivado exitosamente.", "activo": True})
