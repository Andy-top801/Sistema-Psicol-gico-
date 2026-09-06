import re
from rest_framework import serializers
from datetime import timedelta
from django.utils import timezone

from .models import Usuario, Rol, Permiso, Especialidad, Psicologo, DisponibilidadPsicologo, Paciente, Cita
from django.contrib.auth.hashers import make_password

def validate_secure_password(value):
    if len(value) < 8:
        raise serializers.ValidationError('La contraseña debe tener al menos 8 caracteres.')
    if not re.search(r'[A-Z]', value):
        raise serializers.ValidationError('La contraseña debe contener al menos una letra mayúscula.')
    if not re.search(r'[a-z]', value):
        raise serializers.ValidationError('La contraseña debe contener al menos una letra minúscula.')
    if not re.search(r'\d', value):
        raise serializers.ValidationError('La contraseña debe contener al menos un número.')
    if not re.search(r'[^a-zA-Z0-9]', value):
        raise serializers.ValidationError('La contraseña debe contener al menos un carácter especial (ej. !, @, #, $, etc.).')
    return value

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ['id', 'name', 'codename']

class RolSerializer(serializers.ModelSerializer):
    permisos_details = PermisoSerializer(source='permisos', many=True, read_only=True)
    permisos = serializers.PrimaryKeyRelatedField(
        queryset=Permiso.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Rol
        fields = ['id', 'name', 'description', 'permisos', 'permisos_details']

class UsuarioSerializer(serializers.ModelSerializer):
    roles_details = RolSerializer(source='roles', many=True, read_only=True)
    roles = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        many=True,
        required=False
    )
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, validators=[validate_secure_password])

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'phone', 'password', 'is_active', 'roles', 'roles_details'
        ]

    def create(self, validated_data):
        roles_data = validated_data.pop('roles', [])
        validated_data['password'] = make_password(validated_data.get('password'))
        
        # When creating a user in django-tenants, they are created in the current tenant's schema
        user = Usuario.objects.create(**validated_data)
        
        if roles_data:
            user.roles.set(roles_data)
        return user

    def update(self, instance, validated_data):
        roles_data = validated_data.pop('roles', None)
        
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data.get('password'))

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if roles_data is not None:
            instance.roles.set(roles_data)
            
        return instance

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_secure_password])

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .tokens import resolve_reset_code

PACIENTE_ROLE_NAME = 'Paciente'

class RegisterSerializer(serializers.ModelSerializer):
    """CU27: registro de pacientes desde la aplicación móvil."""
    email = serializers.EmailField(validators=[])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_secure_password])
    phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Usuario
        fields = ['email', 'password', 'first_name', 'last_name', 'phone']

    def validate_email(self, value):
        value = value.strip().lower()
        if Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                'Ya existe una cuenta registrada con este correo electrónico.'
            )
        return value

    def validate_password(self, value):
        validate_secure_password(value)
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data['email']
        user = Usuario.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
        )
        rol_paciente, _ = Rol.objects.get_or_create(
            name=PACIENTE_ROLE_NAME,
            defaults={'description': 'Paciente registrado desde la aplicación móvil'},
        )
        user.roles.add(rol_paciente)
        Paciente.objects.create(usuario=user)
        return user

class PasswordResetVerifySerializer(serializers.Serializer):
    """HU-10b (paso intermedio): confirma que el código todavía es válido."""
    code = serializers.CharField()

    def validate_code(self, value):
        if resolve_reset_code(value) is None:
            raise serializers.ValidationError(
                'El código no es válido o ya expiró. Solicita uno nuevo.'
            )
        return value

class MobilePasswordResetConfirmSerializer(serializers.Serializer):
    """HU-10b/c: confirmación con el código enviado por correo para móvil."""
    code = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_secure_password])

    def validate_new_password(self, value):
        validate_secure_password(value)
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def validate(self, attrs):
        user = resolve_reset_code(attrs['code'])
        if user is None:
            raise serializers.ValidationError(
                {'code': 'El código no es válido o ya expiró. Solicita uno nuevo.'}
            )
        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    roles = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'roles']
        read_only_fields = fields


class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = ['id', 'name', 'description']


class DisponibilidadPsicologoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisponibilidadPsicologo
        fields = ['id', 'psicologo', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo']


PSICOLOGO_ROLE_NAME = 'Psicólogo'


class PsicologoSerializer(serializers.ModelSerializer):
    usuario = UserProfileSerializer(read_only=True)
    especialidades_details = EspecialidadSerializer(source='especialidades', many=True, read_only=True)
    email = serializers.EmailField(write_only=True)
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=False, validators=[validate_secure_password])
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    especialidades = serializers.PrimaryKeyRelatedField(queryset=Especialidad.objects.all(), many=True, required=False)

    class Meta:
        model = Psicologo
        fields = [
            'id', 'usuario', 'email', 'username', 'password',
            'first_name', 'last_name', 'phone', 'modalidad_atencion',
            'activo', 'especialidades', 'especialidades_details',
        ]

    def validate_email(self, value):
        value = value.strip().lower()
        if Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Ya existe una cuenta con este correo electrónico.')
        return value

    def create(self, validated_data):
        especialidades = validated_data.pop('especialidades', [])
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        username = validated_data.pop('username', '') or email
        user = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=validated_data.pop('first_name', ''),
            last_name=validated_data.pop('last_name', ''),
            phone=validated_data.pop('phone', ''),
        )
        rol_psicologo, _ = Rol.objects.get_or_create(
            name=PSICOLOGO_ROLE_NAME,
            defaults={'description': 'Psicólogo registrado desde el panel administrativo'},
        )
        user.roles.add(rol_psicologo)
        psicologo = Psicologo.objects.create(usuario=user, **validated_data)
        if especialidades:
            psicologo.especialidades.set(especialidades)
        return psicologo

    def update(self, instance, validated_data):
        especialidades = validated_data.pop('especialidades', None)
        user = instance.usuario

        for attr in ['email', 'username', 'first_name', 'last_name', 'phone']:
            if attr in validated_data:
                value = validated_data.pop(attr)
                if attr == 'email':
                    user.email = value.strip().lower()
                elif attr == 'username':
                    if value:
                        user.username = value
                else:
                    setattr(user, attr, value)

        if 'password' in validated_data:
            user.set_password(validated_data.pop('password'))

        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if especialidades is not None:
            instance.especialidades.set(especialidades)

        rol_psicologo, _ = Rol.objects.get_or_create(
            name=PSICOLOGO_ROLE_NAME,
            defaults={'description': 'Psicólogo registrado desde el panel administrativo'},
        )
        if not user.roles.filter(pk=rol_psicologo.pk).exists():
            user.roles.add(rol_psicologo)

        return instance


class PacienteSerializer(serializers.ModelSerializer):
    usuario = UserProfileSerializer(read_only=True)
    email = serializers.EmailField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=False, validators=[validate_secure_password])
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Paciente
        fields = [
            'id', 'usuario', 'email', 'username', 'password', 'first_name',
            'last_name', 'phone', 'fecha_nacimiento', 'direccion',
            'documento_identidad', 'genero', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password', None)
        username = validated_data.pop('username', '') or email
        user = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password or Usuario.objects.make_random_password(),
            first_name=validated_data.pop('first_name', ''),
            last_name=validated_data.pop('last_name', ''),
            phone=validated_data.pop('phone', ''),
        )
        rol_paciente, _ = Rol.objects.get_or_create(
            name=PACIENTE_ROLE_NAME,
            defaults={'description': 'Paciente registrado desde la aplicación móvil'},
        )
        user.roles.add(rol_paciente)
        return Paciente.objects.create(usuario=user, **validated_data)

    def update(self, instance, validated_data):
        user = instance.usuario

        for attr in ['email', 'username', 'first_name', 'last_name', 'phone']:
            if attr in validated_data:
                value = validated_data.pop(attr)
                if attr == 'email':
                    user.email = value.strip().lower()
                elif attr == 'username':
                    if value:
                        user.username = value
                else:
                    setattr(user, attr, value)

        if 'password' in validated_data:
            user.set_password(validated_data.pop('password'))

        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DashboardResumenSerializer(serializers.Serializer):
    citas_totales = serializers.IntegerField()
    pacientes_totales = serializers.IntegerField()
    inasistencias = serializers.IntegerField()
    carga_profesional = serializers.IntegerField()


class CitaSerializer(serializers.ModelSerializer):
    paciente_details = UserProfileSerializer(source='paciente.usuario', read_only=True)
    psicologo_details = UserProfileSerializer(source='psicologo.usuario', read_only=True)

    class Meta:
        model = Cita
        fields = [
            'id', 'paciente', 'paciente_details', 'psicologo', 'psicologo_details',
            'fecha_hora', 'duracion_minutos', 'estado', 'motivo', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        paciente = attrs.get('paciente', getattr(instance, 'paciente', None))
        psicologo = attrs.get('psicologo', getattr(instance, 'psicologo', None))
        fecha_hora = attrs.get('fecha_hora', getattr(instance, 'fecha_hora', None))
        duracion = attrs.get('duracion_minutos', getattr(instance, 'duracion_minutos', 60))

        if not paciente or not psicologo or not fecha_hora:
            return attrs

        if not psicologo.activo:
            raise serializers.ValidationError({'psicologo': 'El psicólogo está inactivo.'})

        fecha_fin = fecha_hora + timedelta(minutes=duracion)
        if fecha_hora.date() != fecha_fin.date():
            raise serializers.ValidationError({'fecha_hora': 'La cita no puede cruzar de día.'})

        dia_semana = fecha_hora.isoweekday()
        hora_inicio = fecha_hora.time()
        hora_fin = fecha_fin.time()
        disponible = psicologo.disponibilidades.filter(
            activo=True,
            dia_semana=dia_semana,
            hora_inicio__lte=hora_inicio,
            hora_fin__gte=hora_fin,
        ).exists()
        if not disponible:
            raise serializers.ValidationError({'fecha_hora': 'La cita no cae dentro de la disponibilidad del psicólogo.'})

        active_states = [Cita.Estado.RESERVADA, Cita.Estado.CONFIRMADA, Cita.Estado.REPROGRAMADA]
        overlap = Cita.objects.filter(
            psicologo=psicologo,
            estado__in=active_states,
            fecha_hora__lt=fecha_fin,
        )
        if instance is not None:
            overlap = overlap.exclude(pk=instance.pk)
        for cita in overlap:
            cita_fin = cita.fecha_hora + timedelta(minutes=cita.duracion_minutos)
            if cita_fin > fecha_hora:
                raise serializers.ValidationError({'fecha_hora': 'El psicólogo ya tiene una cita en ese horario.'})

        return attrs
