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
    """CU1 / HU-04 — datos institucionales del centro (uno por schema)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150, blank=True, default='')
    nif_rif = models.CharField(max_length=50, blank=True, default='')
    registro_sanitario = models.CharField(max_length=100, blank=True, default='')
    direccion = models.CharField(max_length=255, blank=True, default='')
    telefono = models.CharField(max_length=30, blank=True, default='')
    email = models.EmailField(max_length=255, blank=True, default='')
    modalidad = models.CharField(max_length=60, blank=True, default='Presencial')
    linea_crisis = models.CharField(max_length=60, blank=True, default='')
    horarios_atencion = models.JSONField(default=dict, blank=True)
    especialidades = models.JSONField(default=list, blank=True)
    logo_url = models.CharField(max_length=255, blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#235d55')
    updated_at = models.DateTimeField(auto_now=True)

    # Campos legacy (se mantienen para no romper migraciones previas)
    address = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)

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

    class Modalidad(models.TextChoices):
        PRESENCIAL = 'presencial', 'Presencial'
        VIRTUAL = 'virtual', 'Virtual'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE, related_name='citas')
    fecha_hora = models.DateTimeField()
    duracion_minutos = models.PositiveIntegerField(default=60)
    modalidad = models.CharField(
        max_length=10, choices=Modalidad.choices, default=Modalidad.PRESENCIAL
    )
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


# ─────────────────────────────────────────────
# CU10 – Alertas de priorización y seguimiento
# ─────────────────────────────────────────────

class AlertaPriorizacion(models.Model):
    class Tipo(models.TextChoices):
        INASISTENCIA = 'inasistencia', 'Inasistencia consecutiva'
        RIESGO_ABANDONO = 'riesgo_abandono', 'Riesgo de abandono'
        SENAL_RIESGO = 'senal_riesgo', 'Señal de riesgo clínico'
        ESTANCAMIENTO = 'estancamiento', 'Estancamiento terapéutico'

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        EN_REVISION = 'en_revision', 'En revisión'
        RESUELTA = 'resuelta', 'Resuelta'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='alertas'
    )
    tipo = models.CharField(max_length=30, choices=Tipo.choices)
    descripcion = models.TextField()
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    accion_tomada = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_tipo_display()}] {self.paciente.usuario.email} - {self.get_estado_display()}'


# ─────────────────────────────────────────────
# CU13 – Teleconsultas y videoconferencias
# ─────────────────────────────────────────────

class Teleconsulta(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADA = 'programada', 'Programada'
        EN_CURSO = 'en_curso', 'En curso'
        FINALIZADA = 'finalizada', 'Finalizada'
        CANCELADA = 'cancelada', 'Cancelada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cita = models.OneToOneField(
        Cita, on_delete=models.CASCADE, related_name='teleconsulta'
    )
    # Sala generada automáticamente (p.ej. Jitsi: meet.jit.si/<room_name>)
    room_name = models.CharField(max_length=255, unique=True)
    enlace_psicologo = models.URLField(max_length=500)
    enlace_paciente = models.URLField(max_length=500)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PROGRAMADA
    )
    iniciada_at = models.DateTimeField(blank=True, null=True)
    finalizada_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Teleconsulta [{self.room_name}] - {self.get_estado_display()}'
