from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import uuid
from django.conf import settings
from django.core.mail import send_mail

from .models import Usuario, Rol, Permiso, TokenRecuperacion, Especialidad, Psicologo, DisponibilidadPsicologo, Paciente, Cita, AlertaPriorizacion, Teleconsulta, ConfiguracionCentro
from .serializers import (
    UsuarioSerializer, RolSerializer, PermisoSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    MobilePasswordResetConfirmSerializer, PasswordResetVerifySerializer,
    RegisterSerializer, UserProfileSerializer, EspecialidadSerializer,
    ConfiguracionCentroSerializer,
    PsicologoSerializer, DisponibilidadPsicologoSerializer, PacienteSerializer,
    DashboardResumenSerializer, CitaSerializer,
    AlertaPriorizacionSerializer, TeleconsultaSerializer,
)
from .tokens import make_reset_code
from .permissions import HasAnyRole, IsSelfPacienteOrStaff, user_roles, STAFF_ROLES

# --- ViewSets for Web ---

class PermisoViewSet(viewsets.ReadOnlyModelViewSet):
    """CU4 – catálogo de permisos (solo lectura, staff)."""
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    read_roles = STAFF_ROLES

class RolViewSet(viewsets.ModelViewSet):
    """CU4 – gestión de roles y permisos del centro."""
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    read_roles = STAFF_ROLES
    write_roles = {'superadmin', 'admincentro'}

class UsuarioViewSet(viewsets.ModelViewSet):
    """CU3 – gestión de usuarios del centro (alta/edición/estado)."""
    queryset = Usuario.objects.all().prefetch_related('roles')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    read_roles = STAFF_ROLES
    write_roles = {'superadmin', 'admincentro'}


class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    read_roles = STAFF_ROLES | {'paciente'}
    write_roles = {'superadmin', 'admincentro', 'coordinador'}


class PsicologoViewSet(viewsets.ModelViewSet):
    queryset = Psicologo.objects.select_related('usuario').prefetch_related('especialidades')
    serializer_class = PsicologoSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    read_roles = STAFF_ROLES | {'paciente'}
    write_roles = {'superadmin', 'admincentro', 'coordinador'}


class DisponibilidadPsicologoViewSet(viewsets.ModelViewSet):
    queryset = DisponibilidadPsicologo.objects.select_related('psicologo', 'psicologo__usuario')
    serializer_class = DisponibilidadPsicologoSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    read_roles = STAFF_ROLES | {'paciente'}
    write_roles = {'superadmin', 'admincentro', 'coordinador', 'psicologo'}


class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.select_related('usuario')
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    read_roles = STAFF_ROLES | {'paciente'}
    write_roles = STAFF_ROLES | {'paciente'}

    def get_permissions(self):
        perms = super().get_permissions()
        if self.action in ('retrieve', 'update', 'partial_update'):
            perms.append(IsSelfPacienteOrStaff())
        return perms

    def get_queryset(self):
        qs = super().get_queryset()
        roles = user_roles(self.request.user)
        if roles == {'paciente'}:
            return qs.filter(usuario=self.request.user)
        return qs


class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.select_related('paciente__usuario', 'psicologo__usuario').all()
    serializer_class = CitaSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    read_roles = STAFF_ROLES | {'paciente'}
    write_roles = STAFF_ROLES | {'paciente'}

    def get_queryset(self):
        qs = super().get_queryset()
        roles = user_roles(self.request.user)
        if roles == {'paciente'}:
            qs = qs.filter(paciente__usuario=self.request.user)
        elif roles == {'psicologo'}:
            qs = qs.filter(psicologo__usuario=self.request.user)

        params = self.request.query_params
        estado = params.get('estado')
        fecha = params.get('fecha')
        if estado:
            qs = qs.filter(estado=estado)
        if fecha:
            qs = qs.filter(fecha_hora__date=fecha)
        if params.get('sin_teleconsulta') in ('1', 'true'):
            qs = qs.filter(teleconsulta__isnull=True)
        return qs

    def perform_create(self, serializer):
        roles = user_roles(self.request.user)
        if roles == {'paciente'}:
            serializer.save(estado=Cita.Estado.RESERVADA)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        cita = self.get_object()
        cita.estado = Cita.Estado.CONFIRMADA
        cita.save(update_fields=['estado', 'updated_at'])
        return Response(self.get_serializer(cita).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        cita = self.get_object()
        cita.estado = Cita.Estado.CANCELADA
        cita.save(update_fields=['estado', 'updated_at'])
        return Response(self.get_serializer(cita).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reprogramar(self, request, pk=None):
        cita = self.get_object()
        nueva = request.data.get('nueva_fecha_hora') or request.data.get('fecha_hora')
        if not nueva:
            return Response(
                {'nueva_fecha_hora': 'Este campo es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(cita, data={'fecha_hora': nueva}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(estado=Cita.Estado.REPROGRAMADA)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {
            'citas_totales': Cita.objects.count(),
            'pacientes_totales': Paciente.objects.count(),
            'inasistencias': Cita.objects.filter(estado=Cita.Estado.INASISTENCIA).count(),
            'carga_profesional': Psicologo.objects.filter(activo=True).count(),
        }
        serializer = DashboardResumenSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
# CU10 – Alertas de priorización
# ─────────────────────────────────────────────

class AlertaPriorizacionViewSet(viewsets.ModelViewSet):
    """CU10 – CRUD de alertas + acciones para cambiar su estado."""
    queryset = AlertaPriorizacion.objects.select_related('paciente__usuario').all()
    serializer_class = AlertaPriorizacionSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    read_roles = {'superadmin', 'admincentro', 'coordinador', 'psicologo'}
    write_roles = {'superadmin', 'admincentro', 'coordinador', 'psicologo'}

    def get_queryset(self):
        qs = super().get_queryset()
        # Filtros opcionales por query param
        estado = self.request.query_params.get('estado')
        tipo = self.request.query_params.get('tipo')
        paciente = self.request.query_params.get('paciente')
        if estado:
            qs = qs.filter(estado=estado)
        if tipo:
            qs = qs.filter(tipo=tipo)
        if paciente:
            qs = qs.filter(paciente=paciente)
        return qs

    @action(detail=True, methods=['post'], url_path='revisar')
    def revisar(self, request, pk=None):
        """Pasa la alerta a estado EN_REVISION."""
        alerta = self.get_object()
        alerta.estado = AlertaPriorizacion.Estado.EN_REVISION
        alerta.save(update_fields=['estado', 'updated_at'])
        return Response(self.get_serializer(alerta).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='resolver')
    def resolver(self, request, pk=None):
        """Marca la alerta como RESUELTA y registra la acción tomada."""
        alerta = self.get_object()
        accion = request.data.get('accion_tomada', '')
        alerta.estado = AlertaPriorizacion.Estado.RESUELTA
        alerta.accion_tomada = accion
        alerta.save(update_fields=['estado', 'accion_tomada', 'updated_at'])
        return Response(self.get_serializer(alerta).data, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
# CU13 – Teleconsultas / Videoconferencias
# ─────────────────────────────────────────────

class TeleconsultaViewSet(viewsets.ModelViewSet):
    """CU13 – Crear sala Jitsi vinculada a una cita y gestionar su ciclo de vida."""
    queryset = Teleconsulta.objects.select_related('cita__paciente__usuario', 'cita__psicologo__usuario').all()
    serializer_class = TeleconsultaSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    read_roles = STAFF_ROLES | {'paciente'}
    write_roles = STAFF_ROLES

    def get_queryset(self):
        qs = super().get_queryset()
        roles = user_roles(self.request.user)
        if roles == {'paciente'}:
            return qs.filter(cita__paciente__usuario=self.request.user)
        if roles == {'psicologo'}:
            return qs.filter(cita__psicologo__usuario=self.request.user)
        return qs

    @action(detail=True, methods=['post'], url_path='iniciar')
    def iniciar(self, request, pk=None):
        """Cambia el estado a EN_CURSO y registra la hora de inicio."""
        tc = self.get_object()
        tc.estado = Teleconsulta.Estado.EN_CURSO
        tc.iniciada_at = timezone.now()
        tc.save(update_fields=['estado', 'iniciada_at', 'updated_at'])
        return Response(self.get_serializer(tc).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='finalizar')
    def finalizar(self, request, pk=None):
        """Cambia el estado a FINALIZADA y registra la hora de fin."""
        tc = self.get_object()
        tc.estado = Teleconsulta.Estado.FINALIZADA
        tc.finalizada_at = timezone.now()
        tc.save(update_fields=['estado', 'finalizada_at', 'updated_at'])
        return Response(self.get_serializer(tc).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        """Cancela la teleconsulta."""
        tc = self.get_object()
        tc.estado = Teleconsulta.Estado.CANCELADA
        tc.save(update_fields=['estado', 'updated_at'])
        return Response(self.get_serializer(tc).data, status=status.HTTP_200_OK)


class PasswordResetViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='request')
    def request_reset(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = Usuario.objects.filter(email=email).first()
            if user:
                # Generate token
                token_obj = TokenRecuperacion.objects.create(
                    usuario=user,
                    token=str(uuid.uuid4()),
                    fecha_expiracion=timezone.now() + timedelta(minutes=5)
                )
                
                # Enlace al frontend: mismo host que la petición pero puerto 4200
                # (dev). En producción se resuelve al dominio real del centro.
                host = request.get_host().split(':')[0]
                frontend = getattr(settings, 'FRONTEND_URL', None) or f"http://{host}:4200"
                reset_url = f"{frontend}/password-reset/confirm?token={token_obj.token}"

                send_mail(
                    subject='Restablecer Contraseña (SIGEPSI)',
                    message=f'Hola,\n\nHaz clic en el siguiente enlace para crear tu nueva contraseña:\n{reset_url}\n\nSi no fuiste tú, ignora este mensaje.',
                    from_email=settings.EMAIL_HOST_USER if getattr(settings, 'EMAIL_HOST_USER', None) else 'no-reply@sigepsi.com',
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                
            return Response({"message": "Si el correo existe, se ha enviado un enlace de recuperación."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_reset(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            token_obj = TokenRecuperacion.objects.filter(
                token=token, 
                usado=False, 
                fecha_expiracion__gt=timezone.now()
            ).first()
            
            if not token_obj:
                return Response({"error": "Token inválido o expirado."}, status=status.HTTP_400_BAD_REQUEST)
                
            user = token_obj.usuario
            user.set_password(new_password)
            user.save()
            
            token_obj.usado = True
            token_obj.save()
            
            return Response({"message": "Contraseña actualizada exitosamente."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- APIViews for Mobile ---

class RegisterView(APIView):
    """Registro de pacientes desde la aplicación móvil (HU-02 / backlog
    SP3-1..3). Devuelve tokens listos para usar, igual que /auth/login/,
    para permitir el ingreso inmediato tras registrarse."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'user': UserProfileSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )

class PasswordResetRequestView(APIView):
    """HU-10a / CU27 / RF-31: solicitud de recuperación de contraseña.

    Responde 200 con un mensaje genérico exista o no el correo, para no
    revelar qué cuentas están registradas (mismo criterio que el login,
    RF-01). El código es válido 5 minutos (PASSWORD_RESET_TIMEOUT) y de
    un solo uso (se invalida solo al cambiar la contraseña).
    """

    permission_classes = [permissions.AllowAny]

    GENERIC_MESSAGE = (
        'Si el correo está registrado, recibirás un mensaje con instrucciones '
        'para restablecer tu contraseña.'
    )

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user = Usuario.objects.filter(email__iexact=email).first()
        if user is not None:
            code = make_reset_code(user)
            send_mail(
                subject='SIGEPSI - Recuperación de contraseña',
                message=(
                    f'Hola {user.first_name or user.email},\n\n'
                    'Recibimos una solicitud para restablecer tu contraseña.\n'
                    f'Tu código de verificación (válido por 5 minutos): {code}\n\n'
                    'Ingresa este código en la app para crear una nueva contraseña. '
                    'Si no solicitaste esto, ignora este correo.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else (settings.EMAIL_HOST_USER if getattr(settings, 'EMAIL_HOST_USER', None) else 'no-reply@sigepsi.com'),
                recipient_list=[user.email],
            )

        return Response({'detail': self.GENERIC_MESSAGE}, status=status.HTTP_200_OK)

class PasswordResetVerifyView(APIView):
    """HU-10b (paso intermedio): solo confirma que el código todavía es
    válido, sin tocar la contraseña."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'detail': 'Código válido.'}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    """HU-10c: con el código ya verificado, establece la nueva contraseña
    que la persona escribió."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = MobilePasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Contraseña actualizada correctamente.'},
            status=status.HTTP_200_OK,
        )

class MeView(generics.RetrieveAPIView):
    """Perfil del usuario autenticado (nombre, rol) para que el cliente
    móvil sepa quién inició sesión tras el login/registro."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class ConfiguracionCentroView(generics.RetrieveUpdateAPIView):
    """CU1 / HU-04 — datos institucionales del centro (singleton por schema).

    Lectura: cualquier personal del centro. Escritura: superadmin / admincentro.
    """

    serializer_class = ConfiguracionCentroSerializer
    permission_classes = [permissions.IsAuthenticated, HasAnyRole]
    read_roles = STAFF_ROLES
    write_roles = {'superadmin', 'admincentro'}

    def get_object(self):
        obj = ConfiguracionCentro.objects.first()
        if obj is None:
            obj = ConfiguracionCentro.objects.create()
        return obj
