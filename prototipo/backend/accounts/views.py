from rest_framework import status, viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from accounts.models import Usuario, Rol, Permiso, TokenRecuperacion
from accounts.serializers import (
    UsuarioSerializer, RegistroSerializer, LoginSerializer,
    LogoutSerializer, RolSerializer, PermisoSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from accounts.permissions import EsAdminCentro, EsSuperAdmin, RequierePermiso

class RegistroView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Permite registrar un nuevo usuario con credenciales seguras.
    """
    queryset = Usuario.objects.all()
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "mensaje": "Usuario registrado exitosamente.",
                "usuario": UsuarioSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """
    ═══════════════════════════════════════════════════════════════════════════
    CU2: Gestionar Inicio de Sesión y Autenticación (HU-01, HU-02)
    Diagrama de Comunicación – CTR_AuthService (Django REST)
    Participantes:
      Actor  → Usuario (Todos los roles)
      IU     → IU_Login (Angular / Móvil)
      CTR    → CTR_AuthService (Django REST)  ← ESTE ARCHIVO
      CE     → CE_Usuario_y_Tenant (PostgreSQL)
    ═══════════════════════════════════════════════════════════════════════════
    POST /api/auth/login/
    Inicia sesión validando credenciales y tenant. Retorna tokens JWT y datos de rol.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # --- Paso 2: POST /api/auth/login/ ---
        # Se recibe la petición con credenciales (email, password, tenant)
        serializer = LoginSerializer(data=request.data)
        # Los pasos 3-8 ocurren dentro del LoginSerializer.validate():
        #   Paso 3: Validar tenant y conmutar schema
        #   Paso 4: Esquema PostgreSQL activo
        #   Paso 5: SELECT usuario WHERE email = ? AND activo = true
        #   Paso 6: Retornar usuario y hash password
        #   Paso 7: Verificar password (PBKDF2) y generar JWT
        #   Paso 8: Tokens JWT generados (con claims)
        serializer.is_valid(raise_exception=True)
        # --- Paso 9: 200 OK (access_token, refresh_token, usuario, rol) ---
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    ═══════════════════════════════════════════════════════════════════════════
    CU2 (Logout): Cierre de Sesión Seguro (HU-09)
    Diagrama de Comunicación – CTR_AuthLogout (Django REST)
    Participantes:
      Actor  → Usuario Autenticado (Todos los roles)
      IU     → IU_Navbar (Angular / Móvil)
      CTR    → CTR_AuthLogout (Django REST)  ← ESTE ARCHIVO
      CE     → CE_TokenBlacklist (PostgreSQL)
    ═══════════════════════════════════════════════════════════════════════════
    POST /api/auth/logout/
    Invalida el refresh token del usuario y cierra la sesión.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # --- Paso 2: POST /api/auth/logout/ {refresh} + Bearer JWT ---
        # Se recibe la petición con el refresh token a invalidar
        serializer = LogoutSerializer(data=request.data)
        # --- Paso 3: Validar token y autenticación de usuario ---
        serializer.is_valid(raise_exception=True)
        # --- Paso 4: Refresh token válido ---
        # --- Paso 5: INSERT INTO token_blacklist (token, fecha) ---
        serializer.save()
        # --- Paso 6: Token revocado en lista negra ---
        # --- Paso 7: 200 OK {"mensaje": "Sesión cerrada"} ---
        return Response({"mensaje": "Sesión cerrada exitosamente."}, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    ═══════════════════════════════════════════════════════════════════════════
    CU27: Recuperar Contraseña y Credenciales (HU-10)
    Diagrama de Comunicación – CTR_PasswordReset (Django REST) – Solicitud
    Participantes:
      Actor  → Usuario (Todos los roles)
      IU     → IU_RecuperarPassword (Angular)
      CTR    → CTR_PasswordReset (Django REST)  ← ESTE ARCHIVO
      CE     → CE_Usuario_y_Token (PostgreSQL)
      SRV    → SRV_ServicioCorreo (SMTP / SendGrid)
    ═══════════════════════════════════════════════════════════════════════════
    POST /api/auth/password-reset/
    Genera un token de recuperación temporal de 24 horas y envía el correo.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # --- Paso 2: POST /api/auth/password-reset/ {email} ---
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        from django.db import connection
        from django_tenants.utils import schema_context
        from tenants.models import Tenant

        target_user = None
        target_tenant = None

        # 1. Si se envió tenant explícito
        tenant_param = request.data.get('tenant')
        if tenant_param and tenant_param.lower() != 'public':
            try:
                try:
                    target_tenant = Tenant.objects.get(id=tenant_param)
                except Exception:
                    target_tenant = Tenant.objects.get(slug=tenant_param)
                connection.set_tenant(target_tenant)
                target_user = Usuario.objects.get(email=email, activo=True)
            except (Tenant.DoesNotExist, Usuario.DoesNotExist):
                target_user = None

        # 2. Si no se especificó o no se halló, buscar en esquema actual
        if not target_user:
            try:
                target_user = Usuario.objects.get(email=email, activo=True)
            except Usuario.DoesNotExist:
                # 3. Buscar en todos los esquemas de tenants activos
                for t in Tenant.objects.exclude(slug='public').filter(activo=True):
                    with schema_context(t.schema_name):
                        if Usuario.objects.filter(email=email, activo=True).exists():
                            target_tenant = t
                            break

                if target_tenant:
                    connection.set_tenant(target_tenant)
                    target_user = Usuario.objects.get(email=email, activo=True)

        if not target_user:
            return Response({
                "mensaje": "Si el correo está registrado, recibirá un enlace de recuperación."
            }, status=status.HTTP_200_OK)

        # --- Paso 5: INSERT INTO accounts_tokenrecuperacion (token, exp=24h) ---
        token_obj = TokenRecuperacion.generar_para_usuario(target_user)
        # --- Paso 6: Token generado ---

        # Construir enlace de recuperación
        from django.conf import settings
        from django.core.mail import send_mail
        import socket
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:4200').rstrip('/')
        reset_link = f"{frontend_url}/reset-password?token={token_obj.token}"

        # Imprimir en consola/logs de Render para auditoría inmediata y pruebas
        print("=" * 80)
        print(f"🔑 [RECUPERACIÓN DE CONTRASEÑA] Solicitado para: {email}")
        print(f"👉 TOKEN: {token_obj.token}")
        print(f"👉 ENLACE DIRECTO: {reset_link}")
        print("=" * 80)

        # --- Paso 5.1: send_mail(email, reset_link) ---
        default_sock_timeout = socket.getdefaulttimeout()
        try:
            # Máximo 3 segundos para el intento SMTP (evita bloqueo por firewall en Render Free)
            socket.setdefaulttimeout(3)
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
            send_mail(
                subject='SIGEPSI - Recuperación de Contraseña',
                message=(
                    f'Hola {target_user.nombre},\n\n'
                    f'Recibimos una solicitud para restablecer tu contraseña.\n'
                    f'Haz clic en el siguiente enlace para crear una nueva contraseña:\n\n'
                    f'{reset_link}\n\n'
                    f'Este enlace expira en 24 horas.\n'
                    f'Si no solicitaste este cambio, ignora este mensaje.\n\n'
                    f'— Equipo SIGEPSI'
                ),
                from_email=from_email,
                recipient_list=[email],
                fail_silently=False,
            )
            print(f"✅ Correo enviado exitosamente a {email} vía SMTP.")
        except Exception as smtp_err:
            print(f"ℹ️ [AVISO] Envío SMTP omitido o bloqueado por firewall en nube ({smtp_err}). Enlace listo en respuesta y log.")
        finally:
            socket.setdefaulttimeout(default_sock_timeout)

        # --- Paso 7: 200 OK (Enlace y token retornados para evaluación) ---
        response_data = {
            "mensaje": f"Se ha generado el enlace de recuperación para {email}.",
            "tenant": target_tenant.slug if target_tenant else "public",
            "token": token_obj.token,
            "reset_link": reset_link,
            "expira": token_obj.fecha_expiracion,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    CU27: Recuperar Contraseña y Credenciales (HU-10)
    Diagrama de Comunicación – Confirmación de Nueva Contraseña
    POST /api/auth/password-reset-confirm/
    Verifica el token temporal y actualiza la contraseña del usuario.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # --- Paso 10: POST /api/auth/password-reset-confirm/ {token, password} ---
        serializer = PasswordResetConfirmSerializer(data=request.data)
        # --- Paso 11: Validar token (vigente y usado = false) ---
        serializer.is_valid(raise_exception=True)
        # --- Paso 12: Token verificado ---
        
        token_obj = serializer.validated_data['token_obj']
        tenant_obj = serializer.validated_data.get('tenant_obj')
        if tenant_obj:
            from django.db import connection
            connection.set_tenant(tenant_obj)

        user = token_obj.usuario
        # --- Paso 13: UPDATE usuario SET password = ? ; token.usado = true ---
        user.set_password(serializer.validated_data['password'])
        user.save()

        # Marcar token como consumido
        token_obj.usado = True
        token_obj.save()
        # --- Paso 14: Credenciales actualizadas ---

        # --- Paso 15: 200 OK (Contraseña actualizada) ---
        return Response({"mensaje": "Contraseña actualizada exitosamente. Ya puede iniciar sesión."}, status=status.HTTP_200_OK)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ═══════════════════════════════════════════════════════════════════════════
    CU3: Gestionar Usuarios (HU-05)
    Diagrama de Comunicación – CTR_UsuarioService (Django REST)
    Participantes:
      Actor  → Administrador del Centro
      IU     → IU_GestionUsuarios (Angular)
      CTR    → CTR_UsuarioService (Django REST)  ← ESTE ARCHIVO
      CE     → CE_Usuario_y_Rol (PostgreSQL)

    Flujo del diagrama de comunicación:
      Paso 2: POST /api/users/ + JWT Header (petición recibida)
      Paso 3: Validar JWT, TenantMiddleware y rol Admin Centro
      Paso 4: Contexto tenant y permisos verificados
      Paso 5: Validar datos y unicidad de email
      Paso 6: Email disponible
      Paso 7: SELECT rol WHERE id = ?
      Paso 8: Rol encontrado
      Paso 9: INSERT INTO accounts_usuario (email, password_hash, rol_id)
      Paso 10: Usuario guardado en esquema tenant
      Paso 11: 201 Created {usuario_creado}
    ═══════════════════════════════════════════════════════════════════════════
    CRUD de Usuarios dentro del tenant actual.
    Permite al Administrador del Centro crear, listar, editar y activar/desactivar usuarios.
    """
    queryset = Usuario.objects.all().select_related('rol')
    serializer_class = UsuarioSerializer
    # --- Paso 3: Validar JWT y rol Admin Centro ---
    permission_classes = [IsAuthenticated, EsAdminCentro]

    def get_queryset(self):
        # --- Paso 4: Contexto tenant verificado (TenantMiddleware ya conmutó el schema) ---
        # En el esquema del tenant retorna los usuarios de este centro
        return Usuario.objects.all().select_related('rol').order_by('-fecha_creacion')

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def alternar_estado(self, request, pk=None):
        usuario = self.get_object()
        usuario.activo = not usuario.activo
        usuario.save()
        estado_str = "activado" if usuario.activo else "desactivado"
        return Response({"mensaje": f"Usuario {estado_str} exitosamente.", "activo": usuario.activo})


class RolViewSet(viewsets.ModelViewSet):
    """
    ═══════════════════════════════════════════════════════════════════════════
    CU4: Gestionar Roles y Permisos (HU-06)
    Diagrama de Comunicación – CTR_RolService (Django REST)
    Participantes:
      Actor  → Administrador del Centro
      IU     → IU_GestionRoles (Angular)
      CTR    → CTR_RolService (Django REST)  ← ESTE ARCHIVO
      CE     → CE_Rol_y_Permiso (PostgreSQL)

    Flujo del diagrama de comunicación (PUT /api/roles/{id}/):
      Paso 2: PUT /api/roles/{id}/ {permisos: [ids]} + JWT
      Paso 3: Validar JWT, permisos RBAC y esquema tenant
      Paso 4: Permisos administrativos verificados
      Paso 5: SELECT * FROM accounts_permiso WHERE id IN (?)
      Paso 6: Permisos validados
      Paso 7: DELETE FROM accounts_rol_permiso WHERE rol_id = ?
      Paso 8: Permisos anteriores desvinculados
      Paso 9: INSERT INTO accounts_rol_permiso (rol_id, permiso_id)
      Paso 10: Nuevos permisos registrados en esquema
      Paso 11: 200 OK {rol_actualizado}
    ═══════════════════════════════════════════════════════════════════════════
    CRUD de Roles y asignación de Permisos (RBAC) en el tenant.
    """
    queryset = Rol.objects.all().prefetch_related('permisos_asignados__permiso')
    serializer_class = RolSerializer
    # --- Paso 3: Validar JWT y permisos RBAC ---
    permission_classes = [IsAuthenticated, EsAdminCentro]


class PermisoListView(generics.ListAPIView):
    """
    GET /api/permisos/
    Lista todos los permisos disponibles en el sistema.
    """
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer
    permission_classes = [IsAuthenticated]


class MeView(APIView):
    """
    GET /api/auth/me/
    Retorna el perfil del usuario autenticado en la sesión actual.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        permisos = []
        if request.user.rol:
            permisos = list(request.user.rol.permisos_asignados.values_list('permiso__codigo', flat=True))
        elif request.user.is_superuser:
            permisos = list(Permiso.objects.values_list('codigo', flat=True))

        return Response({
            "usuario": serializer.data,
            "permisos": permisos,
            "tenant": request.tenant.nombre if request.tenant else "Public / Plataforma Global"
        })
