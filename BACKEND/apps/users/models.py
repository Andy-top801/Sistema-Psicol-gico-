from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

class Permiso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Rol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    permisos = models.ManyToManyField(Permiso, related_name='roles')

    def __str__(self):
        return self.name

class Usuario(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # email will be used to login instead of username
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    roles = models.ManyToManyField(Rol, related_name='usuarios')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

class ConfiguracionCentro(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    logo_url = models.CharField(max_length=255, blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#FFFFFF')

class TokenRecuperacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tokens_recuperacion')
    token = models.CharField(max_length=255, unique=True)
    fecha_expiracion = models.DateTimeField()
    usado = models.BooleanField(default=False)


class Especialidad(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Psicologo(models.Model):
    class ModalidadAtencion(models.TextChoices):
        PRESENCIAL = 'presencial', 'Presencial'
        VIRTUAL = 'virtual', 'Virtual'
        MIXTA = 'mixta', 'Mixta'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='psicologo',
    )
    especialidades = models.ManyToManyField(Especialidad, related_name='psicologos', blank=True)
    modalidad_atencion = models.CharField(
        max_length=20,
        choices=ModalidadAtencion.choices,
        default=ModalidadAtencion.PRESENCIAL,
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.usuario.email} ({self.get_modalidad_atencion_display()})'


class DisponibilidadPsicologo(models.Model):
    class DiaSemana(models.IntegerChoices):
        LUNES = 1, 'Lunes'
        MARTES = 2, 'Martes'
        MIERCOLES = 3, 'Miércoles'
        JUEVES = 4, 'Jueves'
        VIERNES = 5, 'Viernes'
        SABADO = 6, 'Sábado'
        DOMINGO = 7, 'Domingo'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE, related_name='disponibilidades')
    dia_semana = models.PositiveSmallIntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['psicologo', 'dia_semana', 'hora_inicio', 'hora_fin'],
                name='uniq_disponibilidad_psicologo_slot',
            )
        ]

    def __str__(self):
        return f'{self.psicologo.usuario.email} - {self.get_dia_semana_display()}'


class Paciente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='paciente',
    )
    fecha_nacimiento = models.DateField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    documento_identidad = models.CharField(max_length=50, blank=True, null=True)
    genero = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.usuario.email


class Cita(models.Model):
    class Estado(models.TextChoices):
        RESERVADA = 'reservada', 'Reservada'
        CONFIRMADA = 'confirmada', 'Confirmada'
        CANCELADA = 'cancelada', 'Cancelada'
        REPROGRAMADA = 'reprogramada', 'Reprogramada'
        INASISTENCIA = 'inasistencia', 'Inasistencia'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE, related_name='citas')
    fecha_hora = models.DateTimeField()
    duracion_minutos = models.PositiveIntegerField(default=60)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.RESERVADA)
    motivo = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['psicologo', 'fecha_hora']),
            models.Index(fields=['paciente', 'fecha_hora']),
        ]

    def __str__(self):
        return f'{self.paciente.usuario.email} - {self.psicologo.usuario.email} - {self.fecha_hora}'
