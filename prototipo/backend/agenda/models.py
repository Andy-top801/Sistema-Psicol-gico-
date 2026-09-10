# ==============================================================================
# MÓDULO: agenda/models.py
# CAPA BCE: ENTIDAD (Entity) — CE_Cita_y_Disponibilidad, CE_Sala_y_Cita,
#           CE_Metricas_y_Citas, CE_Alerta_y_Asistencia
# CASOS DE USO: CU11 (Gestión de Citas), CU13 (Teleconsulta Jitsi Meet),
#               CU9 (Dashboard KPIs), CU10 (Alertas de Priorización)
# DESCRIPCIÓN: Entidades persistentes del módulo de agenda que son
#              referenciadas en los pasos 3→6 de los Diagramas de Comunicación
#              BCE del Sprint 1.
# ==============================================================================
import uuid
from django.db import models
from django.utils import timezone
from clinica.models import Paciente, Psicologo

# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: Cita — CE_Cita_y_Disponibilidad (Diagrama de Comunicación CU11)
# DIAGRAMA DE COMUNICACIÓN CU11 – Programación, Reserva y Gestión de Citas:
#   Paso 3: CTR_CitaService inicia tx y SELECT FOR UPDATE sobre slot → CE
#           → Se bloquean las filas de citas del psicólogo para evitar colisiones.
#   Paso 4: CE retorna "Bloqueo pesimista concedido (slot libre)".
#   Paso 5: CTR_CitaService ejecuta "INSERT INTO agenda_cita y marcar slot ocupado"
#           → Se crea el registro con estado='PROGRAMADA'.
#   Paso 6: CE retorna "Cita registrada sin colisión horaria".
#
# DIAGRAMA DE COMUNICACIÓN CU9 – Paso 5:
#   El MetricsAggregator ejecuta SELECT COUNT, AVG sobre esta tabla
#   para calcular KPIs de citas del día/mes, ausentismo y ocupación.
#
# DIAGRAMA DE COMUNICACIÓN CU10 – Paso 3:
#   El AlertService evalúa el historial de estado='INASISTENCIA' en esta tabla.
# ──────────────────────────────────────────────────────────────────────────────
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
    # CU11 Paso 3: hora_inicio y hora_fin se usan en SELECT FOR UPDATE para detectar colisiones
    hora_inicio = models.TimeField(verbose_name="Hora de Inicio")
    hora_fin = models.TimeField(verbose_name="Hora de Finalización")
    # CU11 Paso 5: Si modalidad='VIRTUAL', se genera sala Teleconsulta automáticamente
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default='PRESENCIAL', verbose_name="Modalidad")
    # CU11 Paso 5: estado se establece como 'PROGRAMADA' al crear la cita
    # CU10 Paso 3: estado='INASISTENCIA' dispara evaluación de alertas automáticas
    estado = models.CharField(max_length=25, choices=ESTADO_CHOICES, default='PROGRAMADA', verbose_name="Estado de la Cita")
    motivo_consulta = models.TextField(blank=True, default="", verbose_name="Motivo de Consulta")
    # CU9 Paso 5: costo se agrega con SUM para calcular ingresos_mes en el Dashboard
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=150.00, verbose_name="Costo de la Sesión (BOB)")
    # HU-17: Motivo registrado al cancelar la cita (validado por CancelarCitaSerializer)
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
            # CU11 Paso 3: Índice compuesto optimiza el SELECT FOR UPDATE por psicólogo y fecha
            models.Index(fields=['psicologo', 'fecha', 'hora_inicio'], name='idx_cita_psico_fecha_hora'),
            models.Index(fields=['paciente', 'fecha'], name='idx_cita_paciente_fecha'),
            # CU9 Paso 5: Índice por estado optimiza las agregaciones COUNT del Dashboard
            models.Index(fields=['estado'], name='idx_cita_estado'),
        ]

    def __str__(self):
        return f"Cita {self.fecha} {self.hora_inicio} - Paciente: {self.paciente.usuario.nombre} / Psico: {self.psicologo.usuario.nombre} ({self.estado})"


# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: Teleconsulta — CE_Sala_y_Cita (Diagrama de Comunicación CU13)
# DIAGRAMA DE COMUNICACIÓN CU13 – Teleconsultas y Videoconferencias Jitsi Meet:
#   Paso 3: CTR_Teleconsulta valida ventana horaria activa (cita +/- 15 min) → CE
#   Paso 4: CE retorna "Cita virtual vigente y usuario participante".
#   Paso 5: CTR_Teleconsulta ejecuta "INSERT INTO agenda_teleconsulta (room, fecha_inicio)"
#           → Se genera sala_id única y jwt_room_token con credenciales WebRTC.
#   Paso 6: CE retorna "Sala registrada y credenciales generadas".
#
# DIAGRAMA DE COMUNICACIÓN CU11 – Paso 5 (modalidad VIRTUAL):
#   Al crear la cita virtual, ConflictResolutionService también crea
#   el registro de Teleconsulta con sala_id generado automáticamente.
# ──────────────────────────────────────────────────────────────────────────────
class Teleconsulta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE, related_name="teleconsulta")
    # CU13 Paso 5: Identificador único de sala Jitsi Meet generado al crear la cita virtual
    sala_id = models.CharField(max_length=150, unique=True, verbose_name="Identificador Único de Sala Jitsi")
    # CU13 Paso 6: Token JWT firmado por JitsiTokenGenerator con roles de moderador/invitado
    jwt_room_token = models.TextField(blank=True, null=True, verbose_name="Token JWT de Acceso WebRTC")
    # CU13 Paso 5: Hora inicio se registra al primer acceso a la sala
    hora_inicio_real = models.DateTimeField(blank=True, null=True, verbose_name="Hora Inicio Efectiva")
    # HU-18 Paso 3: hora_fin_real y duracion_segundos se registran al finalizar la consulta
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


# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: Alerta — CE_Alerta_y_Asistencia (Diagrama de Comunicación CU10)
# DIAGRAMA DE COMUNICACIÓN CU10 – Gestión de Alertas Tempranas y Priorización:
#   Paso 3: CTR_AlertaService evalúa historial de inasistencias consecutivas (2+) → CE
#   Paso 4: CE retorna "Pacientes con ausentismo crítico identificados".
#   Paso 5: CTR_AlertaService ejecuta "INSERT / UPDATE agenda_alerta (prioridad='ALTA')"
#           → Se crea una alerta con tipo='INASISTENCIA_REITERADA' y severidad='ALTA'.
#   Paso 6: CE retorna "Alertas clínicas registradas en esquema".
#
# HU-21 Criterio c):
#   Al resolver la alerta, se actualizan: resuelta=True, fecha_resolucion, nota_resolucion.
# ──────────────────────────────────────────────────────────────────────────────
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
    # CU10 Paso 5: tipo se establece como 'INASISTENCIA_REITERADA' al detectar 2+ faltas
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name="Tipo de Alerta")
    # CU10 Paso 5: severidad se establece como 'ALTA' para inasistencias reiteradas
    severidad = models.CharField(max_length=20, choices=SEVERIDAD_CHOICES, default='MEDIA', verbose_name="Severidad")
    descripcion = models.TextField(verbose_name="Descripción de la Alerta")
    # HU-21 Paso 3: resuelta se actualiza a True cuando el psicólogo la resuelve
    resuelta = models.BooleanField(default=False, verbose_name="¿Resuelta?")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    # HU-21 Paso 3: fecha_resolucion se registra cuando se marca como resuelta
    fecha_resolucion = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de Resolución")
    # HU-21 Paso 3: nota_resolucion es obligatoria para cerrar la alerta
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
