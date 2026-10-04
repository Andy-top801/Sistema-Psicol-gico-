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

    # ══════════════════════════════════════════════════════════════════════════
    # CU28: GESTIONAR COPIAS DE SEGURIDAD Y RESTAURACIÓN (CRITERIO 6)
    # ══════════════════════════════════════════════════════════════════════════
    @action(detail=True, methods=['get', 'post'], permission_classes=[EsSuperAdmin])
    def backup(self, request, pk=None):
        """
        CU28: Generar respaldo bajo demanda para el esquema de este centro clínico o listar respaldos.
        """
        from .backup_service import crear_backup, listar_backups
        tenant = self.get_object()
        if request.method == 'POST':
            res = crear_backup(schema_name=tenant.schema_name)
            return Response(res, status=status.HTTP_201_CREATED)
        else:
            backups = listar_backups(schema_name=tenant.schema_name)
            return Response(backups)

    @action(detail=True, methods=['post'], permission_classes=[EsSuperAdmin])
    def restore(self, request, pk=None):
        """
        CU28: Restaurar base de datos del centro clínico desde un archivo de respaldo.
        """
        from .backup_service import restaurar_backup
        tenant = self.get_object()
        archivo = request.data.get('archivo')
        if not archivo:
            return Response({"error": "Debe especificar el nombre del archivo de respaldo a restaurar."}, status=400)
        from django.conf import settings
        from pathlib import Path
        filepath = Path(settings.BASE_DIR) / "backups" / archivo
        try:
            res = restaurar_backup(filepath, schema_name=tenant.schema_name)
            return Response(res)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=False, methods=['get', 'post'], permission_classes=[EsSuperAdmin], url_path='backups-globales')
    def backups_globales(self, request):
        """
        CU28: Generar o listar respaldos globales de toda la base de datos PostgreSQL.
        """
        from .backup_service import crear_backup, listar_backups
        if request.method == 'POST':
            res = crear_backup(schema_name=None)
            return Response(res, status=status.HTTP_201_CREATED)
        else:
            backups = listar_backups(schema_name=None)
            return Response(backups)
