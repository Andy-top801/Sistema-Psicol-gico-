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
from datetime import datetime, date, timedelta
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

    def calcular_horas_restantes(self, ahora=None) -> float:
        """Calcula el tiempo en horas que resta para el inicio de la cita."""
        if not ahora:
            ahora = timezone.localtime()
        cita_dt = timezone.make_aware(
            datetime.combine(self.fecha, self.hora_inicio),
            timezone.get_current_timezone()
        )
        return (cita_dt - ahora).total_seconds() / 3600.0

    @classmethod
    def obtener_detalle_cita(cls, cita_id) -> dict:
        """CU12-paso 4: obtener_detalle_cita(cita_id) → CU12-paso 5: detalle_cita(fecha, hora, psicologo) [retorno]."""
        cita = cls.objects.select_related('psicologo__usuario').get(id=cita_id)
        u = cita.psicologo.usuario
        return {
            "cita_id": str(cita.id),
            "paciente_id": str(cita.paciente_id),
            "fecha": cita.fecha,
            "hora": cita.hora_inicio,
            "psicologo": f"Lic. {u.nombre} {u.apellido}".strip(),
            "modalidad": cita.modalidad,
        }

    def permite_cancelacion(self, ahora=None) -> bool:
        """Verifica la politica de cancelacion anticipada (> 24 horas)."""
        if self.estado in ['CANCELADA', 'REALIZADA']:
            return False
        return self.calcular_horas_restantes(ahora) > 24.0

    def marcar_cancelada(self, motivo: str):
        """Aplica la transicion formal de estado a CANCELADA registrando el motivo."""
        self.estado = 'CANCELADA'
        self.motivo_cancelacion = motivo
        self.save(update_fields=['estado', 'motivo_cancelacion', 'fecha_modificacion'])

    # ── CU11 Móvil · Secuencia mensajes 3-4 ─────────────────────────────────
    @classmethod
    def consultar_cita(cls, cita_id):
        """CU11-paso 3: consultar_cita(cita_id) → CU11-paso 4: datos_cita(fecha, hora, estado) [retorno].
        Bloquea la fila (SELECT FOR UPDATE) para que dos cancelaciones simultáneas no se crucen."""
        return cls.objects.select_for_update().select_related(
            'paciente__usuario', 'psicologo__usuario'
        ).get(id=cita_id)

    # ── CU11 Móvil · Secuencia mensajes 6-7 ─────────────────────────────────
    def cambiar_estado_cita(self, nuevo_estado: str, motivo: str = ""):
        """CU11-paso 6: cambiar_estado_cita('CANCELADA') → CU11-paso 7: cita_cancelada() [retorno]."""
        if nuevo_estado == 'CANCELADA':
            self.marcar_cancelada(motivo)
        else:
            self.estado = nuevo_estado
            self.save(update_fields=['estado', 'fecha_modificacion'])
        return self.estado


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
    # CU11-paso 10: la sala se invalida cuando la cita virtual se cancela
    ESTADO_SALA_CHOICES = [('ACTIVA', 'Activa'), ('CANCELADA', 'Cancelada')]
    estado_sala = models.CharField(max_length=12, choices=ESTADO_SALA_CHOICES, default='ACTIVA', verbose_name="Estado de la Sala")

    class Meta:
        db_table = "agenda_teleconsulta"
        verbose_name = "Teleconsulta WebRTC"
        verbose_name_plural = "Teleconsultas WebRTC"
        indexes = [
            models.Index(fields=['sala_id'], name='idx_teleconsulta_sala'),
        ]

    def __str__(self):
        return f"Teleconsulta Sala: {self.sala_id} (Cita: {self.cita.id})"

    def cancelar_sala(self):
        """CU11-paso 10: cancelar_sala() → CU11-paso 11: sala_cancelada() [retorno]. Revoca el token de acceso."""
        self.estado_sala = 'CANCELADA'
        self.jwt_room_token = None
        self.save(update_fields=['estado_sala', 'jwt_room_token'])
        return self.estado_sala


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
        ('CRISIS_RETROCESO', 'Retroceso / Factor de Crisis'),
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


# ==============================================================================
# SPRINT 3: COLA TRANSACCIONAL DE NOTIFICACIONES Y RECORDATORIOS (CU12 / HU-43)
# ==============================================================================
class NotificacionCita(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('RECORDATORIO_24H', 'Recordatorio 24 horas antes'),
        ('RECORDATORIO_1H', 'Recordatorio 1 hora antes'),
        ('CANCELACION', 'Aviso de Cancelación'),
        ('REPROGRAMACION', 'Aviso de Reprogramación'),
        ('NUEVA_TAREA', 'Aviso de Nueva Tarea Asignada'),
    ]

    CANAL_CHOICES = [
        ('PUSH_FCM', 'Push Notification (Firebase Cloud Messaging)'),
        ('EMAIL', 'Correo Electrónico'),
        ('SMS', 'Mensaje SMS'),
    ]

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de despacho'),
        ('ENVIADO', 'Enviado al dispositivo'),
        ('FALLIDO', 'Fallido'),
    ]

    # CU12: máximo de reintentos antes de abandonar un recordatorio fallido
    MAX_INTENTOS = 3

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name="notificaciones", verbose_name="Cita Asociada")
    tipo_evento = models.CharField(max_length=30, choices=TIPO_EVENTO_CHOICES, verbose_name="Tipo de Evento")
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES, default='PUSH_FCM', verbose_name="Canal de Despacho")
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado del Despacho")
    enviada = models.BooleanField(default=False, verbose_name="¿Notificación Enviada?")
    titulo = models.CharField(max_length=120, blank=True, default="", verbose_name="Título de la Push")
    cuerpo = models.TextField(blank=True, default="", verbose_name="Cuerpo de la Push")
    message_id = models.CharField(max_length=200, blank=True, default="", verbose_name="ID de Mensaje FCM")
    leida = models.BooleanField(default=False, verbose_name="¿Leída por el Paciente?")
    fecha_programada = models.DateTimeField(verbose_name="Fecha Programada de Envío")
    fecha_envio = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Real de Envío")
    error_log = models.TextField(null=True, blank=True, verbose_name="Registro de Error")
    intentos_entrega = models.IntegerField(default=0, verbose_name="Intentos de Entrega")

    class Meta:
        db_table = "agenda_notificacioncita"
        verbose_name = "Notificación y Recordatorio de Cita"
        verbose_name_plural = "Notificaciones y Recordatorios de Citas"
        ordering = ['fecha_programada']
        indexes = [
            models.Index(fields=['fecha_programada', 'enviada'], name='idx_notif_prog_env'),
        ]
        constraints = [
            # Idempotencia del Cron: un solo recordatorio de cada tipo por cita
            models.UniqueConstraint(fields=['cita', 'tipo_evento'], name='uq_notif_cita_tipo'),
        ]

    def __str__(self):
        return f"[{self.tipo_evento}] Cita {self.cita_id} ({self.estado} - {self.fecha_programada})"

    # ── CU12 · Secuencia mensajes 2-3 ────────────────────────────────────────
    @classmethod
    def seleccionar_citas_proximas(cls, ventana_24h=24, ventana_1h=1, ahora=None):
        """
        CU12-paso 2: seleccionar_citas_proximas(ventana_24h, ventana_1h)
        CU12-paso 3: retorna citas_pendientes_notificar (lista de NotificacionCita PENDIENTE).

        Encola un recordatorio por cada cita CONFIRMADA cuyo inicio cae dentro de una ventana:
          - RECORDATORIO_24H: faltan entre ventana_1h y ventana_24h horas.
          - RECORDATORIO_1H : faltan entre 0 y ventana_1h horas.
        La UniqueConstraint (cita, tipo_evento) garantiza que el Cron no duplique avisos.
        """
        ahora = ahora or timezone.localtime()
        hoy = timezone.localdate()
        candidatas = Cita.objects.filter(
            estado='CONFIRMADA',
            fecha__gte=hoy,
            fecha__lte=hoy + timedelta(days=2),
        )
        for cita in candidatas:
            horas = cita.calcular_horas_restantes(ahora)
            if 0 < horas <= ventana_1h:
                tipo = 'RECORDATORIO_1H'
            elif ventana_1h < horas <= ventana_24h:
                tipo = 'RECORDATORIO_24H'
            else:
                continue
            cls.objects.get_or_create(
                cita=cita, tipo_evento=tipo,
                defaults={'fecha_programada': ahora, 'canal': 'PUSH_FCM'}
            )

        return list(
            cls.objects.filter(
                estado__in=['PENDIENTE', 'FALLIDO'],
                intentos_entrega__lt=cls.MAX_INTENTOS,
                fecha_programada__lte=ahora,
            ).filter(
                models.Q(cita__estado='CONFIRMADA', tipo_evento__in=['RECORDATORIO_24H', 'RECORDATORIO_1H'])
                | models.Q(cita__estado='CANCELADA', tipo_evento='CANCELACION')
            ).select_related('cita')
        )

    # ── CU11 Móvil · Secuencia mensajes 12-13 ────────────────────────────────
    EVENTOS_A_TIPO = {'CITA_CANCELADA': 'CANCELACION'}

    @classmethod
    def encolar_notificacion(cls, cita, evento='CITA_CANCELADA'):
        """CU11-paso 12: encolar_notificacion('CITA_CANCELADA') → CU11-paso 13: notificacion_encolada() [retorno].
        Queda PENDIENTE; el Cron de CU12 la despacha por FCM en su siguiente ciclo."""
        notif, _ = cls.objects.get_or_create(
            cita=cita, tipo_evento=cls.EVENTOS_A_TIPO[evento],
            defaults={'fecha_programada': timezone.now(), 'canal': 'PUSH_FCM'}
        )
        return notif

    # ── CU12 · Secuencia mensajes 14-15 ──────────────────────────────────────
    def marcar_enviado(self, estado='ENVIADO', message_id=''):
        """CU12-paso 14: marcar_enviado(cita_id, estado='ENVIADO') → CU12-paso 15: estado_actualizado() [retorno]."""
        self.estado = estado
        self.enviada = True
        self.message_id = message_id or ''
        self.fecha_envio = timezone.now()
        self.intentos_entrega += 1
        self.error_log = None
        self.save(update_fields=['estado', 'enviada', 'message_id', 'fecha_envio', 'intentos_entrega', 'error_log'])
        return self.estado

    def registrar_fallo(self, error: str):
        """Registra un intento fallido; el Cron reintentará hasta MAX_INTENTOS."""
        self.estado = 'FALLIDO'
        self.intentos_entrega += 1
        self.error_log = error
        self.save(update_fields=['estado', 'intentos_entrega', 'error_log'])
        return self.estado

