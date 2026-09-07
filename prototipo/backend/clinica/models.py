import uuid
from datetime import date
from django.db import models
from django.utils import timezone
from accounts.models import Usuario

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Especialidad")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        db_table = "clinica_especialidad"
        verbose_name = "Especialidad Clínica"
        verbose_name_plural = "Especialidades Clínicas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Psicologo(models.Model):
    MODALIDAD_CHOICES = [
        ('PRESENCIAL', 'Presencial'),
        ('VIRTUAL', 'Virtual'),
        ('MIXTA', 'Mixta (Presencial y Virtual)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_psicologo")
    numero_colegiado = models.CharField(max_length=50, unique=True, verbose_name="Número de Colegiado")
    biografia = models.TextField(blank=True, default="", verbose_name="Biografía / Perfil Profesional")
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default='MIXTA', verbose_name="Modalidad")
    tarifa_base = models.DecimalField(max_digits=10, decimal_places=2, default=150.00, verbose_name="Tarifa Base (BOB)")
    activo = models.BooleanField(default=True, verbose_name="Activo en el Centro")
    fecha_ingreso = models.DateField(default=timezone.localdate, verbose_name="Fecha de Incorporación")
    especialidades = models.ManyToManyField(
        Especialidad,
        through='PsicologoEspecialidad',
        related_name="psicologos",
        blank=True
    )

    class Meta:
        db_table = "clinica_psicologo"
        verbose_name = "Psicólogo / Terapeuta"
        verbose_name_plural = "Psicólogos"
        ordering = ['usuario__nombre', 'usuario__apellido']
        indexes = [
            models.Index(fields=['numero_colegiado'], name='idx_psicologo_colegiado'),
        ]

    def __str__(self):
        return f"Lic. {self.usuario.nombre} {self.usuario.apellido} (Col. {self.numero_colegiado})"


class PsicologoEspecialidad(models.Model):
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)

    class Meta:
        db_table = "clinica_psicologo_especialidad"
        verbose_name = "Especialidad de Psicólogo"
        verbose_name_plural = "Especialidades de Psicólogos"
        unique_together = ('psicologo', 'especialidad')

    def __str__(self):
        return f"{self.psicologo} - {self.especialidad.nombre}"


class Disponibilidad(models.Model):
    DIAS_SEMANA = [
        (0, 'Domingo'),
        (1, 'Lunes'),
        (2, 'Martes'),
        (3, 'Miércoles'),
        (4, 'Jueves'),
        (5, 'Viernes'),
        (6, 'Sábado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE, related_name="disponibilidades")
    dia_semana = models.SmallIntegerField(choices=DIAS_SEMANA, verbose_name="Día de la Semana (0-6)")
    hora_inicio = models.TimeField(verbose_name="Hora Inicio")
    hora_fin = models.TimeField(verbose_name="Hora Fin")
    duracion_bloque_min = models.SmallIntegerField(default=50, verbose_name="Duración Bloque (min)")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        db_table = "clinica_disponibilidad"
        verbose_name = "Disponibilidad Horaria"
        verbose_name_plural = "Disponibilidades Horarias"
        ordering = ['dia_semana', 'hora_inicio']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(hora_fin__gt=models.F('hora_inicio')),
                name='chk_disponibilidad_rango_horario'
            ),
            models.CheckConstraint(
                condition=models.Q(duracion_bloque_min__gt=0),
                name='chk_disponibilidad_bloque_pos'
            ),
        ]
        indexes = [
            models.Index(fields=['psicologo', 'dia_semana'], name='idx_disp_psico_dia'),
        ]

    def __str__(self):
        return f"{self.psicologo.usuario.nombre} - Día {self.get_dia_semana_display()} ({self.hora_inicio} - {self.hora_fin})"


class Paciente(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_paciente")
    codigo_expediente = models.CharField(max_length=30, unique=True, verbose_name="Código de Expediente")
    ci = models.CharField(max_length=20, unique=True, verbose_name="Cédula de Identidad (CI)")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, verbose_name="Género")
    contacto_emergencia_nombre = models.CharField(max_length=120, blank=True, default="", verbose_name="Contacto Emergencia (Nombre)")
    contacto_emergencia_telf = models.CharField(max_length=25, blank=True, default="", verbose_name="Contacto Emergencia (Teléfono)")
    tutor_legal_nombre = models.CharField(max_length=120, blank=True, default="", verbose_name="Tutor Legal (Nombre)")
    tutor_legal_ci = models.CharField(max_length=20, blank=True, default="", verbose_name="Tutor Legal (CI)")
    fecha_registro = models.DateField(default=timezone.localdate, verbose_name="Fecha de Registro Clínico")

    class Meta:
        db_table = "clinica_paciente"
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-fecha_registro', 'usuario__nombre']
        indexes = [
            models.Index(fields=['ci'], name='idx_paciente_ci'),
            models.Index(fields=['codigo_expediente'], name='idx_paciente_expediente'),
        ]

    def __str__(self):
        return f"{self.usuario.nombre} {self.usuario.apellido} [Exp: {self.codigo_expediente}]"

    def calcular_edad(self):
        hoy = date.today()
        nac = self.fecha_nacimiento
        return hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))

    @property
    def es_menor_de_edad(self):
        return self.calcular_edad() < 18
