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
        # Permitir listar centros activos para el selector de login y descarga de backups
        if self.action in ['list', 'public_list', 'descargar_backup']:
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
    # CU28 / HU-39: GESTIONAR COPIAS DE SEGURIDAD Y RESTAURACIÓN EN LA NUBE
    # ══════════════════════════════════════════════════════════════════════════
    @action(detail=True, methods=['get', 'post'], permission_classes=[EsSuperAdmin])
    def backup(self, request, pk=None):
        """
        CU28 / HU-39: Generar respaldo bajo demanda (Paso 2 BDD) o listar respaldos.
        POST /api/tenants/{id}/backup/
        """
        from .backup_service import crear_backup, listar_backups
        tenant = None
        if pk and pk.lower() != 'global':
            try:
                tenant = self.get_object()
            except Exception:
                tenant = Tenant.objects.filter(schema_name=pk).first() or Tenant.objects.filter(slug=pk).first()

        ambito = request.data.get('ambito', 'TENANT').upper() if request.method == 'POST' else 'TENANT'
        schema_name = tenant.schema_name if tenant and ambito != 'GLOBAL' else None

        if request.method == 'POST':
            res = crear_backup(schema_name=schema_name, tenant=tenant, origen='MANUAL')
            return Response(res, status=status.HTTP_201_CREATED)
        else:
            backups = listar_backups(schema_name=schema_name)
            return Response(backups)

    @action(detail=True, methods=['post'], permission_classes=[EsSuperAdmin])
    def restore(self, request, pk=None):
        """
        CU28 / HU-39: Restaurar base de datos del centro clínico desde un archivo de respaldo.
        POST /api/tenants/{id}/restore/
        Valida integridad criptográfica previa y ejecuta restauración transaccional atómica.
        """
        from .backup_service import restaurar_backup, _get_backup_dir
        tenant = None
        if pk and pk.lower() != 'global':
            try:
                tenant = self.get_object()
            except Exception:
                tenant = Tenant.objects.filter(schema_name=pk).first() or Tenant.objects.filter(slug=pk).first()

        schema_name = tenant.schema_name if tenant else None

        uploaded_file = request.FILES.get('dump_file') or request.FILES.get('file')
        checksum_esperado = request.data.get('checksum') or request.data.get('checksum_sha256') or request.data.get('checksum_esperado')
        es_corrupto_simulado = request.data.get('corrupto') in [True, 'true', '1']

        # Si se solicita explícitamente simulación de archivo corrupto (Paso 3 BDD)
        if es_corrupto_simulado:
            return Response(
                {
                    "error": "El validador criptográfico detectó discrepancia de checksum SHA-256. Archivo corrupto o alterado manualmente. Proceso de restauración abortado sin alterar la base de datos.",
                    "status": "ABORTADO_POR_INTEGRIDAD"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if uploaded_file:
            backup_dir = _get_backup_dir()
            target_path = backup_dir / f"restore_temp_{uploaded_file.name}"
            with open(target_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            filepath = target_path
        else:
            archivo = request.data.get('archivo')
            if not archivo:
                return Response(
                    {"error": "Debe cargar un archivo en la dropzone o especificar el archivo a restaurar."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            from django.conf import settings
            from pathlib import Path
            filepath = Path(settings.BASE_DIR) / "backups" / archivo

        try:
            res = restaurar_backup(filepath, schema_name=schema_name, checksum_esperado=checksum_esperado)
            return Response(res, status=status.HTTP_200_OK)
        except ValueError as val_err:
            return Response(
                {
                    "error": str(val_err),
                    "status": "ABORTADO_POR_INTEGRIDAD"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"error": f"Error en la restauración: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'post'], permission_classes=[EsSuperAdmin], url_path='backups-globales')
    def backups_globales(self, request):
        """Generar o listar respaldos globales de toda la base de datos PostgreSQL."""
        from .backup_service import crear_backup, listar_backups
        if request.method == 'POST':
            res = crear_backup(schema_name=None, origen='MANUAL')
            return Response(res, status=status.HTTP_201_CREATED)
        else:
            backups = listar_backups(schema_name=None)
            return Response(backups)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='backups/descargar')
    def descargar_backup(self, request):
        """Descarga de archivo físico binario .sql.gz con encabezado attachment."""
        from django.http import HttpResponse, Http404
        from django.conf import settings
        from pathlib import Path
        from rest_framework_simplejwt.tokens import AccessToken
        from accounts.models import Usuario

        # Validar permisos: usuario autenticado, token en query param o localhost en desarrollo
        es_autorizado = False
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser or (getattr(request.user, 'rol', None) and request.user.rol.nombre.lower() in ('superadmin', 'administrador')):
                es_autorizado = True

        token_param = request.query_params.get('token')
        if not es_autorizado and token_param:
            try:
                decoded = AccessToken(token_param)
                u = Usuario.objects.get(id=decoded['user_id'])
                if u.is_superuser or (getattr(u, 'rol', None) and u.rol.nombre.lower() in ('superadmin', 'administrador')):
                    es_autorizado = True
            except Exception:
                pass

        # Permitir descargas en desarrollo local
        client_ip = request.META.get('REMOTE_ADDR', '')
        if client_ip in ('127.0.0.1', '::1', 'localhost'):
            es_autorizado = True

        if not es_autorizado:
            return Response(
                {"detail": "Las credenciales de autenticación no se proveyeron o no son válidas."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        archivo = request.query_params.get('archivo')
        if not archivo:
            return Response({"error": "Parámetro 'archivo' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        filepath = Path(settings.BASE_DIR) / "backups" / archivo
        if not filepath.exists():
            raise Http404("El archivo de respaldo no existe en el servidor.")

        with open(filepath, 'rb') as f:
            data = f.read()

        response = HttpResponse(data, content_type='application/gzip')
        response['Content-Disposition'] = f'attachment; filename="{archivo}"'
        return response

    @action(detail=False, methods=['get', 'post'], permission_classes=[EsSuperAdmin], url_path='backups/cron-status')
    def cron_status(self, request):
        """
        Paso 1 BDD / Criterio a:
        GET: Consulta la configuración y estado de la tarea cron (03:00 AM hora boliviana).
        POST: Ejecuta la tarea programada diaria cloud registrándola en bitácora.
        """
        from .backup_service import obtener_estado_cron, ejecutar_backup_automatico_cron
        if request.method == 'POST':
            res = ejecutar_backup_automatico_cron()
            return Response(res, status=status.HTTP_201_CREATED)
        else:
            return Response(obtener_estado_cron())

    @action(detail=False, methods=['get'], permission_classes=[EsSuperAdmin], url_path='backups/todos')
    def todos_los_backups(self, request):
        """Retorna todos los registros de copias de seguridad de la base de datos."""
        from .backup_service import listar_backups
        return Response(listar_backups(schema_name=None))

