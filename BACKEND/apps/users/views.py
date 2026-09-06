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

from .models import Usuario, Rol, Permiso, TokenRecuperacion, Especialidad, Psicologo, DisponibilidadPsicologo
from .serializers import (
    UsuarioSerializer, RolSerializer, PermisoSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    MobilePasswordResetConfirmSerializer, PasswordResetVerifySerializer,
    RegisterSerializer, UserProfileSerializer, EspecialidadSerializer,
    PsicologoSerializer, DisponibilidadPsicologoSerializer
)
from .tokens import make_reset_code

# --- ViewSets for Web ---

class PermisoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer
    permission_classes = [IsAuthenticated]

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]


class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    permission_classes = [IsAuthenticated, permissions.IsAdminUser]


class PsicologoViewSet(viewsets.ModelViewSet):
    queryset = Psicologo.objects.select_related('usuario').prefetch_related('especialidades')
    serializer_class = PsicologoSerializer
    permission_classes = [IsAuthenticated, permissions.IsAdminUser]


class DisponibilidadPsicologoViewSet(viewsets.ModelViewSet):
    queryset = DisponibilidadPsicologo.objects.select_related('psicologo', 'psicologo__usuario')
    serializer_class = DisponibilidadPsicologoSerializer
    permission_classes = [IsAuthenticated, permissions.IsAdminUser]

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
                
                reset_url = f"http://localhost:4200/password-reset/confirm?token={token_obj.token}"
                
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
