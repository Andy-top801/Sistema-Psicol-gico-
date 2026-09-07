import uuid
from django.db import models
from django.utils import timezone
from clinica.models import Paciente, Psicologo

class Cita(models.Model):
    MODALIDAD_CHOICES = [
        ('PRESENCIAL', 'Presencial'),
        ('VIRTUAL', 'Virtual (Teleconsulta)'),
    ]

    ESTADO_CHOICES = [
        ('PROGRAMADA', 'Programada'),
        ('CONFIRMADA', 'Confirmada'),
        ('REALIZADA', 'Realizada'),
        ('CANCELADA', 'Cancelada'),
        ('INASISTENCIA', 'Inasistencia / Ausente'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.RESTRICT, related_name="citas")
    psicologo = models.ForeignKey(Psicologo, on_delete=models.RESTRICT, related_name="citas")
    fecha = models.DateField(verbose_name="Fecha de la Cita")
    hora_inicio = models.TimeField(verbose_name="Hora de Inicio")
    hora_fin = models.TimeField(verbose_name="Hora de Finalización")
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default='PRESENCIAL', verbose_name="Modalidad")
    estado = models.CharField(max_length=25, choices=ESTADO_CHOICES, default='PROGRAMADA', verbose_name="Estado de la Cita")
    motivo_consulta = models.TextField(blank=True, default="", verbose_name="Motivo de Consulta")
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=150.00, verbose_name="Costo de la Sesión (BOB)")
    motivo_cancelacion = models.TextField(blank=True, default="", verbose_name="Motivo de Cancelación")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última Modificación")

    class Meta:
        db_table = "agenda_cita"
        verbose_name = "Cita Clínica"
        verbose_name_plural = "Citas Clínicas"
        ordering = ['fecha', 'hora_inicio']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(hora_fin__gt=models.F('hora_inicio')),
                name='chk_cita_rango_horario'
            ),
            models.CheckConstraint(
                condition=models.Q(costo__gte=0),
                name='chk_cita_costo_no_negativo'
            ),
        ]
        indexes = [
            models.Index(fields=['psicologo', 'fecha', 'hora_inicio'], name='idx_cita_psico_fecha_hora'),
            models.Index(fields=['paciente', 'fecha'], name='idx_cita_paciente_fecha'),
            models.Index(fields=['estado'], name='idx_cita_estado'),
        ]

    def __str__(self):
        return f"Cita {self.fecha} {self.hora_inicio} - Paciente: {self.paciente.usuario.nombre} / Psico: {self.psicologo.usuario.nombre} ({self.estado})"


class Teleconsulta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE, related_name="teleconsulta")
    sala_id = models.CharField(max_length=150, unique=True, verbose_name="Identificador Único de Sala Jitsi")
    jwt_room_token = models.TextField(blank=True, null=True, verbose_name="Token JWT de Acceso WebRTC")
    hora_inicio_real = models.DateTimeField(blank=True, null=True, verbose_name="Hora Inicio Efectiva")
    hora_fin_real = models.DateTimeField(blank=True, null=True, verbose_name="Hora Fin Efectiva")
    duracion_segundos = models.IntegerField(default=0, verbose_name="Duración Total (segundos)")

    class Meta:
        db_table = "agenda_teleconsulta"
        verbose_name = "Teleconsulta WebRTC"
        verbose_name_plural = "Teleconsultas WebRTC"
        indexes = [
            models.Index(fields=['sala_id'], name='idx_teleconsulta_sala'),
        ]

    def __str__(self):
        return f"Teleconsulta Sala: {self.sala_id} (Cita: {self.cita.id})"


class Alerta(models.Model):
    TIPO_CHOICES = [
        ('INASISTENCIA_REITERADA', 'Inasistencia Reiterada'),
        ('RIESGO_DESERCION', 'Riesgo de Deserción Terapéutica'),
        ('URGENCIA_CLINICA', 'Urgencia Clínica'),
    ]

    SEVERIDAD_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="alertas")
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name="Tipo de Alerta")
    severidad = models.CharField(max_length=20, choices=SEVERIDAD_CHOICES, default='MEDIA', verbose_name="Severidad")
    descripcion = models.TextField(verbose_name="Descripción de la Alerta")
    resuelta = models.BooleanField(default=False, verbose_name="¿Resuelta?")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_resolucion = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de Resolución")
    nota_resolucion = models.TextField(blank=True, default="", verbose_name="Nota de Resolución Clínica")

    class Meta:
        db_table = "agenda_alerta"
        verbose_name = "Alerta Clínica"
        verbose_name_plural = "Alertas Clínicas"
        ordering = ['resuelta', '-fecha_creacion']
        indexes = [
            models.Index(fields=['paciente', 'resuelta'], name='idx_alerta_paciente_resuelta'),
            models.Index(fields=['tipo'], name='idx_alerta_tipo'),
        ]

    def __str__(self):
        estado_txt = "Resuelta" if self.resuelta else "Pendiente"
        return f"[{self.severidad}] {self.tipo} - Paciente: {self.paciente.usuario.nombre} ({estado_txt})"
