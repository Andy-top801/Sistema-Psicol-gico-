# ==============================================================================
# MÓDULO: clinica/models.py
# CAPA BCE: ENTIDAD (Entity) — CE_Usuario_y_Psicologo, CE_Paciente_y_Expediente,
#           CE_Disponibilidad_y_Horario
# CASOS DE USO: CU6 (Gestión de Psicólogos), CU7 (Gestión de Pacientes),
#               CU8 (Gestión de Disponibilidad Horaria)
# DESCRIPCIÓN: Define las entidades persistentes del módulo clínico que son
#              referenciadas en los pasos 3→6 de los Diagramas de Comunicación
#              BCE del Sprint 1 (interacción CTR ↔ CE).
# ==============================================================================
import uuid
from datetime import date
from django.db import models
from django.utils import timezone
from accounts.models import Usuario

# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: Especialidad — Catálogo de especialidades clínicas de psicología.
# DIAGRAMA DE COMUNICACIÓN CU6 – Paso 5:
#   CTR_Psicologo → CE_Usuario_y_Psicologo:
#   "Crear Usuario y Psicólogo en esquema tenant"
#   Al crear un psicólogo (paso 5), se vinculan las especialidades seleccionadas
#   mediante la relación M:N clinica_psicologo_especialidad.
# ──────────────────────────────────────────────────────────────────────────────
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


# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: Psicologo — CE_Usuario_y_Psicologo (Diagrama de Comunicación CU6)
# DIAGRAMA DE COMUNICACIÓN CU6 – Gestión de Psicólogos y Perfiles Profesionales:
#   Paso 3: CTR_Psicologo valida datos (email y colegiatura únicos) → CE
#           → numero_colegiado (UNIQUE) garantiza la unicidad en el tenant.
#   Paso 4: CE retorna "Datos válidos" al controlador.
#   Paso 5: CTR_Psicologo ejecuta "Crear Usuario y Psicólogo en esquema tenant"
#           → Se crea un registro en esta tabla vinculado 1:1 a accounts_usuario.
#   Paso 6: CE retorna "Registros creados exitosamente".
#
# DIAGRAMA DE COMUNICACIÓN CU8 – Paso 4:
#   CE_Disponibilidad valida que el terapeuta esté activo (campo `activo`).
# ──────────────────────────────────────────────────────────────────────────────
class Psicologo(models.Model):
    MODALIDAD_CHOICES = [
        ('PRESENCIAL', 'Presencial'),
        ('VIRTUAL', 'Virtual'),
        ('MIXTA', 'Mixta (Presencial y Virtual)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_psicologo")
    # CU6 Paso 3: numero_colegiado es validado como UNIQUE por el serializer y la BD
    numero_colegiado = models.CharField(max_length=50, unique=True, verbose_name="Número de Colegiado")
    biografia = models.TextField(blank=True, default="", verbose_name="Biografía / Perfil Profesional")
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default='MIXTA', verbose_name="Modalidad")
    # CU6 Paso 5: tarifa_base se persiste con el perfil profesional al crear el psicólogo
    tarifa_base = models.DecimalField(max_digits=10, decimal_places=2, default=150.00, verbose_name="Tarifa Base (BOB)")
    # CU8 Paso 4: El controlador verifica que el terapeuta esté activo
    activo = models.BooleanField(default=True, verbose_name="Activo en el Centro")
    fecha_ingreso = models.DateField(default=timezone.localdate, verbose_name="Fecha de Incorporación")
    # CU6 Paso 5: Relación M:N con especialidades se establece al crear el perfil
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


# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: Disponibilidad — CE_Disponibilidad_y_Horario (Diagrama de Comunicación CU8)
# DIAGRAMA DE COMUNICACIÓN CU8 – Gestión de Disponibilidad y Horarios:
#   Paso 3: CTR_Disponibilidad valida coherencia (inicio < fin) sin traslapes → CE
#           → Las constraints CHECK de la BD refuerzan hora_fin > hora_inicio.
#   Paso 4: CE retorna "Franjas válidas y terapeuta activo".
#   Paso 5: CTR_Disponibilidad ejecuta "Guardar franjas y particionar bloques en DB"
#           → Se insertan registros en clinica_disponibilidad con los bloques configurados.
#   Paso 6: CE retorna "Disponibilidad persistida en esquema".
#
# DIAGRAMA DE COMUNICACIÓN CU11 – Paso 3:
#   El servicio AvailabilityValidator consulta estas franjas para verificar
#   que el horario de la cita esté dentro de la jornada laboral del psicólogo.
# ──────────────────────────────────────────────────────────────────────────────
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
    # CU8 Paso 3: hora_inicio y hora_fin son validados por el serializer (inicio < fin)
    hora_inicio = models.TimeField(verbose_name="Hora Inicio")
    hora_fin = models.TimeField(verbose_name="Hora Fin")
    # CU8 Paso 5: duracion_bloque_min se usa para particionar las franjas en slots consultables
    duracion_bloque_min = models.SmallIntegerField(default=50, verbose_name="Duración Bloque (min)")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        db_table = "clinica_disponibilidad"
        verbose_name = "Disponibilidad Horaria"
        verbose_name_plural = "Disponibilidades Horarias"
        ordering = ['dia_semana', 'hora_inicio']
        constraints = [
            # CU8 Paso 3: Constraint CHECK a nivel de BD refuerza la validación del controlador
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


# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: Paciente — CE_Paciente_y_Expediente (Diagrama de Comunicación CU7)
# DIAGRAMA DE COMUNICACIÓN CU7 – Gestión de Pacientes Web y Móvil:
#   Paso 3: CTR_Paciente valida unicidad de CI en tenant activo → CE
#           → ci (UNIQUE) y codigo_expediente (UNIQUE) garantizan no-duplicación.
#   Paso 4: CE retorna "Documento no duplicado y tutor válido".
#   Paso 5: CTR_Paciente ejecuta "INSERT INTO clinica_paciente con código único"
#           → Se genera codigo_expediente automáticamente (formato EXP-YYYYMM-XXXX).
#   Paso 6: CE retorna "Paciente registrado en esquema tenant".
#
# REGLA DE NEGOCIO HU-13 Criterio c):
#   Si el paciente es menor de 18 años, tutor_legal_nombre y tutor_legal_ci
#   son obligatorios (validado por el serializer en paso 3).
# ──────────────────────────────────────────────────────────────────────────────
class Paciente(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_paciente")
    # CU7 Paso 5: Código de expediente generado automáticamente al crear el paciente
    codigo_expediente = models.CharField(max_length=30, unique=True, verbose_name="Código de Expediente")
    # CU7 Paso 3: CI validado como UNIQUE en el tenant para evitar duplicados
    ci = models.CharField(max_length=20, unique=True, verbose_name="Cédula de Identidad (CI)")
    # CU7 Paso 3: fecha_nacimiento se usa para calcular la edad y exigir tutor si < 18
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, verbose_name="Género")
    contacto_emergencia_nombre = models.CharField(max_length=120, blank=True, default="", verbose_name="Contacto Emergencia (Nombre)")
    contacto_emergencia_telf = models.CharField(max_length=25, blank=True, default="", verbose_name="Contacto Emergencia (Teléfono)")
    # CU7 Paso 3/4: Campos obligatorios si el paciente es menor de edad (< 18 años)
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
        """CU7 Paso 3: Calcula la edad para determinar si es menor y requiere tutor legal."""
        hoy = date.today()
        nac = self.fecha_nacimiento
        return hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))

    @property
    def es_menor_de_edad(self):
        """CU7 Paso 3: Propiedad usada por el serializer para validar obligatoriedad de tutor."""
        return self.calcular_edad() < 18


# ==============================================================================
# INCREMENTO SPRINT 2: HISTORIA CLÍNICA, INTAKE, NOTAS SOAP, CONSENTIMIENTOS,
#                      DERIVACIONES Y AUDITORÍA DE IA ASISTIVA
# ==============================================================================

# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: FormularioPreConsulta & RespuestaPreConsulta (CU14 / HU-23, HU-24)
# ──────────────────────────────────────────────────────────────────────────────
class FormularioPreConsulta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=150, verbose_name="Título del Formulario")
    version = models.CharField(max_length=20, default='v1.0', verbose_name="Versión")
    descripcion = models.TextField(blank=True, default="", verbose_name="Descripción")
    preguntas_schema = models.JSONField(default=list, blank=True, verbose_name="Esquema JSON de Preguntas")
    activo = models.BooleanField(default=True, verbose_name="Activo en el Centro")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        db_table = "clinica_formulariopreconsulta"
        verbose_name = "Formulario Pre-Consulta"
        verbose_name_plural = "Formularios Pre-Consulta"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} ({self.version}) - {'Activo' if self.activo else 'Inactivo'}"


class RespuestaPreConsulta(models.Model):
    ESTADO_CHOICES = [
        ('ENVIADO', 'Enviado'),
        ('REVISADO', 'Revisado por Terapeuta'),
        ('ARCHIVADO', 'Archivado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formulario = models.ForeignKey(FormularioPreConsulta, on_delete=models.RESTRICT, related_name="respuestas", verbose_name="Formulario Base")
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="respuestas_preconsulta", verbose_name="Paciente")
    cita = models.ForeignKey('agenda.Cita', on_delete=models.SET_NULL, null=True, blank=True, related_name="respuestas_preconsulta", verbose_name="Cita Asociada")
    motivo_consulta = models.TextField(verbose_name="Motivo Principal de Consulta")
    sintomas_principales = models.TextField(blank=True, default="", verbose_name="Síntomas Frecuentes Reportados")
    nivel_urgencia_percibido = models.SmallIntegerField(default=1, verbose_name="Escala de Malestar / Urgencia (1-5)")
    antecedentes_medicos = models.TextField(blank=True, default="", verbose_name="Antecedentes Médicos Relevantes")
    antecedentes_psiquiatricos = models.TextField(blank=True, default="", verbose_name="Antecedentes Psiquiátricos")
    medicacion_actual = models.TextField(blank=True, default="", verbose_name="Medicación Actual")
    respuestas_detalle = models.JSONField(default=dict, blank=True, verbose_name="Detalle de Respuestas JSON")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ENVIADO', verbose_name="Estado de Revisión")
    fecha_envio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Envío")

    class Meta:
        db_table = "clinica_respuestapreconsulta"
        verbose_name = "Respuesta Pre-Consulta (Intake)"
        verbose_name_plural = "Respuestas Pre-Consulta (Intake)"
        ordering = ['-fecha_envio']
        indexes = [
            models.Index(fields=['paciente'], name='idx_respuestapre_paciente'),
            models.Index(fields=['estado'], name='idx_respuestapre_estado'),
        ]

    def __str__(self):
        return f"Intake {self.paciente.usuario.nombre} - Malestar {self.nivel_urgencia_percibido}/5 ({self.estado})"

    @property
    def tiene_urgencia_alta(self):
        return self.nivel_urgencia_percibido >= 4


# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: HistoriaClinica & DiagnosticoCIE (CU15 / HU-25, HU-26)
# ──────────────────────────────────────────────────────────────────────────────
class HistoriaClinica(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name="historia_clinica", verbose_name="Paciente")
    psicologo_apertura = models.ForeignKey(Psicologo, on_delete=models.RESTRICT, related_name="historias_abiertas", verbose_name="Psicólogo de Apertura")
    codigo_historia = models.CharField(max_length=50, unique=True, verbose_name="Código Correlativo de Historia")
    motivo_consulta_inicial = models.TextField(verbose_name="Motivo de Consulta Inicial")
    antecedentes_personales = models.TextField(blank=True, default="", verbose_name="Antecedentes Personales Patológicos y No Patológicos")
    antecedentes_familiares = models.TextField(blank=True, default="", verbose_name="Antecedentes Familiares")
    historia_evolutiva = models.TextField(blank=True, default="", verbose_name="Historia del Problema / Anamnesis")
    examen_mental_inicial = models.TextField(blank=True, default="", verbose_name="Examen del Estado Mental (EEM)")
    plan_tratamiento = models.TextField(blank=True, default="", verbose_name="Plan de Tratamiento y Objetivos Terapéuticos")
    cerrada = models.BooleanField(default=False, verbose_name="Expediente Cerrado")
    fecha_apertura = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Apertura")
    fecha_cierre = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Cierre")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        db_table = "clinica_historiaclinica"
        verbose_name = "Historia Clínica Psicológica"
        verbose_name_plural = "Historias Clínicas Psicológicas"
        ordering = ['-fecha_apertura']
        indexes = [
            models.Index(fields=['paciente'], name='idx_historia_paciente'),
            models.Index(fields=['codigo_historia'], name='idx_historia_codigo'),
        ]

    def __str__(self):
        return f"HC {self.codigo_historia} - {self.paciente.usuario.nombre} {self.paciente.usuario.apellido}"


class DiagnosticoCIE(models.Model):
    TIPO_CHOICES = [
        ('PRESUNTIVO', 'Presuntivo'),
        ('CONFIRMADO', 'Confirmado'),
        ('DIFERENCIAL', 'Diferencial'),
    ]

    id = models.AutoField(primary_key=True)
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name="diagnosticos", verbose_name="Historia Clínica")
    codigo_cie = models.CharField(max_length=20, verbose_name="Código CIE (ej. F41.1)")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción Diagnóstica")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='PRESUNTIVO', verbose_name="Tipo de Diagnóstico")
    observaciones = models.TextField(blank=True, default="", verbose_name="Observaciones Clínicas")
    fecha_diagnostico = models.DateField(default=timezone.localdate, verbose_name="Fecha de Diagnóstico")

    class Meta:
        db_table = "clinica_diagnosticocie"
        verbose_name = "Diagnóstico CIE"
        verbose_name_plural = "Diagnósticos CIE"
        ordering = ['-fecha_diagnostico', 'codigo_cie']
        indexes = [
            models.Index(fields=['historia_clinica', 'codigo_cie'], name='idx_cie_historia_codigo'),
        ]

    def __str__(self):
        return f"[{self.codigo_cie}] {self.descripcion} ({self.tipo})"


# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: NotaSesion (CU16 / HU-27 - Modelo SOAP)
# ──────────────────────────────────────────────────────────────────────────────
class NotaSesion(models.Model):
    ESTADO_GUARDADO_CHOICES = [
        ('BORRADOR', 'Borrador Temporal'),
        ('FIRMADA', 'Firmada / Inmutable'),
        ('EDITADA', 'Editada con Registro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name="notas_sesion", verbose_name="Historia Clínica")
    cita = models.OneToOneField('agenda.Cita', on_delete=models.SET_NULL, null=True, blank=True, related_name="nota_soap", verbose_name="Cita Documentada")
    psicologo = models.ForeignKey(Psicologo, on_delete=models.RESTRICT, related_name="notas_sesion", verbose_name="Psicólogo Tratante")
    numero_sesion = models.IntegerField(default=1, verbose_name="Número Correlativo de Sesión")
    fecha_sesion = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora de la Sesión")
    # Cuadrantes SOAP
    subjetivo = models.TextField(verbose_name="S - Subjetivo (Relato del paciente)")
    objetivo = models.TextField(verbose_name="O - Objetivo (Observación y examen conductual)")
    analisis = models.TextField(verbose_name="A - Análisis / Evaluación clínica")
    plan = models.TextField(verbose_name="P - Plan terapéutico e intervenciones")
    tecnicas_aplicadas = models.CharField(max_length=255, blank=True, default="", verbose_name="Técnicas Clínicas Aplicadas")
    conducta_observada = models.TextField(blank=True, default="", verbose_name="Conducta Observada / Afecto")
    estado_guardado = models.CharField(max_length=20, choices=ESTADO_GUARDADO_CHOICES, default='FIRMADA', verbose_name="Estado de la Nota")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_firma = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Firma Legal")

    class Meta:
        db_table = "clinica_notasesion"
        verbose_name = "Nota de Sesión (SOAP)"
        verbose_name_plural = "Notas de Sesión (SOAP)"
        ordering = ['numero_sesion']
        indexes = [
            models.Index(fields=['historia_clinica', 'numero_sesion'], name='idx_notasesion_historia'),
            models.Index(fields=['psicologo', 'fecha_sesion'], name='idx_notasesion_psico'),
        ]

    def __str__(self):
        return f"Nota SOAP #{self.numero_sesion} ({self.fecha_sesion.strftime('%d/%m/%Y')}) - {self.estado_guardado}"


# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: EvolucionClinica & TareaTerapeutica & EvidenciaTarea (CU17 / HU-28, HU-29, HU-30)
# ──────────────────────────────────────────────────────────────────────────────
class EvolucionClinica(models.Model):
    ESTADO_AVANCE_CHOICES = [
        ('PROGRESO_NOTABLE', 'Progreso Notable'),
        ('EN_PROCESO', 'En Proceso / Estable'),
        ('ESTANCAMIENTO', 'Estancamiento'),
        ('RETROCESO_CRISIS', 'Retroceso / Crisis'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name="evoluciones", verbose_name="Historia Clínica")
    nota_sesion = models.ForeignKey(NotaSesion, on_delete=models.SET_NULL, null=True, blank=True, related_name="evoluciones", verbose_name="Nota Asociada")
    estado_avance = models.CharField(max_length=30, choices=ESTADO_AVANCE_CHOICES, verbose_name="Estado de Avance")
    justificacion = models.TextField(verbose_name="Justificación Clínica Cualitativa")
    acuerdos_pactados = models.TextField(blank=True, default="", verbose_name="Acuerdos y Compromisos Terapéuticos")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        db_table = "clinica_evolucionclinica"
        verbose_name = "Evolución Clínica Longitudinal"
        verbose_name_plural = "Evoluciones Clínicas Longitudinales"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"Evolución: {self.estado_avance} ({self.fecha_registro.strftime('%d/%m/%Y')})"


class TareaTerapeutica(models.Model):
    CATEGORIA_CHOICES = [
        ('COGNITIVA', 'Cognitiva / Reestructuración'),
        ('CONDUCTUAL', 'Conductual / Exposición'),
        ('MINDFULNESS', 'Mindfulness / Respiración'),
        ('AUTOREGISTRO', 'Autorregistro de Pensamientos'),
        ('OTRA', 'Otra Técnica Inter-Sesión'),
    ]

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_REVISION', 'En Revisión'),
        ('COMPLETADA', 'Completada'),
        ('VENCIDA', 'Vencida'),
        ('NO_REALIZADA', 'No Realizada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name="tareas", verbose_name="Historia Clínica")
    psicologo = models.ForeignKey(Psicologo, on_delete=models.RESTRICT, related_name="tareas_asignadas", verbose_name="Psicólogo Asignador")
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="tareas_terapeuticas", verbose_name="Paciente")
    titulo = models.CharField(max_length=150, verbose_name="Título del Ejercicio")
    descripcion = models.TextField(verbose_name="Instrucciones Detalladas")
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, default='COGNITIVA', verbose_name="Categoría")
    fecha_limite = models.DateField(verbose_name="Fecha Límite de Entrega")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado de la Tarea")
    archivo_adjunto_url = models.CharField(max_length=255, blank=True, default="", verbose_name="Guía o Plantilla Adjunta (URL)")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Asignación")

    class Meta:
        db_table = "clinica_tareaterapeutica"
        verbose_name = "Tarea Terapéutica"
        verbose_name_plural = "Tareas Terapéuticas"
        ordering = ['fecha_limite']
        indexes = [
            models.Index(fields=['paciente', 'estado'], name='idx_tareaterap_paciente'),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.paciente.usuario.nombre} ({self.estado})"


class EvidenciaTarea(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tarea = models.OneToOneField(TareaTerapeutica, on_delete=models.CASCADE, related_name="evidencia", verbose_name="Tarea Correspondiente")
    texto_reflexion = models.TextField(verbose_name="Autorreflexión y Aprendizajes del Paciente")
    dificultad_percibida = models.SmallIntegerField(default=3, verbose_name="Dificultad Percibida (1-Fácil a 5-Muy Difícil)")
    archivo_evidencia_url = models.CharField(max_length=255, blank=True, default="", verbose_name="Archivo de Evidencia (Foto/Audio/PDF)")
    fecha_cumplimiento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Envío")

    class Meta:
        db_table = "clinica_evidenciatarea"
        verbose_name = "Evidencia de Cumplimiento de Tarea"
        verbose_name_plural = "Evidencias de Cumplimiento de Tareas"
        ordering = ['-fecha_cumplimiento']

    def __str__(self):
        return f"Evidencia para '{self.tarea.titulo}' - Dificultad {self.dificultad_percibida}/5"


# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: ConsentimientoInformado & FirmaConsentimiento (CU18 / HU-31, HU-32)
# ──────────────────────────────────────────────────────────────────────────────
class ConsentimientoInformado(models.Model):
    TIPO_CHOICES = [
        ('ATENCION_GENERAL', 'Consentimiento de Atención Psicológica General'),
        ('TELEPSICOLOGIA', 'Consentimiento para Servicios de Telepsicología'),
        ('MENORES_EDAD', 'Autorización de Tratamiento para Menores de Edad'),
        ('DATOS_SENSIBLES', 'Tratamiento de Datos Sensibles de Salud Mental'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=150, verbose_name="Título del Documento Legal")
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name="Tipo de Consentimiento")
    contenido_legal = models.TextField(verbose_name="Texto y Cláusulas Legales")
    version = models.CharField(max_length=20, default='v1.0', verbose_name="Versión Legal")
    activo = models.BooleanField(default=True, verbose_name="Plantilla Vigente")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        db_table = "clinica_consentimientoinformado"
        verbose_name = "Plantilla de Consentimiento Informado"
        verbose_name_plural = "Plantillas de Consentimiento Informado"
        ordering = ['titulo']

    def __str__(self):
        return f"{self.titulo} ({self.version})"


class FirmaConsentimiento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consentimiento = models.ForeignKey(ConsentimientoInformado, on_delete=models.RESTRICT, related_name="firmas", verbose_name="Plantilla Legal")
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="firmas_consentimiento", verbose_name="Paciente")
    firmado_por = models.CharField(max_length=150, verbose_name="Nombre Completo del Firmante")
    es_menor_edad = models.BooleanField(default=False, verbose_name="Paciente Menor de Edad")
    tutor_nombre = models.CharField(max_length=150, blank=True, default="", verbose_name="Nombre del Tutor Legal")
    tutor_ci = models.CharField(max_length=30, blank=True, default="", verbose_name="CI del Tutor Legal")
    hash_sha256 = models.CharField(max_length=64, verbose_name="Huella Criptográfica SHA-256")
    ip_origen = models.CharField(max_length=45, default="127.0.0.1", verbose_name="Dirección IP del Firmante")
    user_agent = models.TextField(blank=True, default="", verbose_name="Navegador / Dispositivo")
    firma_canvas_url = models.TextField(blank=True, default="", verbose_name="Firma Táctil (Base64 o URL)")
    fecha_firma = models.DateTimeField(auto_now_add=True, verbose_name="Marca de Tiempo de Firma")

    class Meta:
        db_table = "clinica_firmaconsentimiento"
        verbose_name = "Firma de Consentimiento Informado"
        verbose_name_plural = "Firmas de Consentimiento Informado"
        ordering = ['-fecha_firma']
        indexes = [
            models.Index(fields=['paciente'], name='idx_firmaconsent_paciente'),
            models.Index(fields=['hash_sha256'], name='idx_firmaconsent_hash'),
        ]

    def __str__(self):
        return f"Consentimiento {self.consentimiento.tipo} - {self.firmado_por} [{self.hash_sha256[:8]}]"


# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: DerivacionCaso (CU19 / HU-33, HU-34)
# ──────────────────────────────────────────────────────────────────────────────
class DerivacionCaso(models.Model):
    TIPO_CHOICES = [
        ('INTERNA_COLEGA', 'Derivación Interna a Colega'),
        ('EXTERNA_PSIQUIATRIA', 'Referencia Médica Externa a Psiquiatría'),
        ('EXTERNA_NEUROLOGIA', 'Referencia Externa a Neurología'),
        ('CIERRE_ALTA', 'Alta Terapéutica por Cumplimiento de Metas'),
        ('DESERCION', 'Cierre por Abandono / Deserción'),
    ]

    NIVEL_RIESGO_CHOICES = [
        ('BAJO', 'Bajo'),
        ('MEDIO', 'Medio'),
        ('ALTO', 'Alto'),
        ('CRITICO', 'Crítico'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name="derivaciones", verbose_name="Historia Clínica")
    psicologo_emisor = models.ForeignKey(Psicologo, on_delete=models.RESTRICT, related_name="derivaciones_emitidas", verbose_name="Psicólogo Emisor")
    tipo_derivacion = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo de Derivación / Cierre")
    motivo_clinico = models.TextField(verbose_name="Motivo Clínico de Egreso o Interconsulta")
    sintomatologia_relevante = models.TextField(blank=True, default="", verbose_name="Sintomatología Predominante")
    profesional_destino = models.CharField(max_length=150, blank=True, default="", verbose_name="Profesional Destinatario")
    institucion_destino = models.CharField(max_length=150, blank=True, default="", verbose_name="Institución / Centro Destino")
    nivel_riesgo = models.CharField(max_length=20, choices=NIVEL_RIESGO_CHOICES, default='MEDIO', verbose_name="Nivel de Riesgo Psicopatológico")
    fecha_derivacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    aceptada = models.BooleanField(default=False, verbose_name="Derivación Aceptada / Confirmada")
    documento_pdf_url = models.CharField(max_length=255, blank=True, default="", verbose_name="Documento Oficial Firmado (PDF)")

    class Meta:
        db_table = "clinica_derivacioncaso"
        verbose_name = "Derivación o Cierre de Caso"
        verbose_name_plural = "Derivaciones y Cierres de Caso"
        ordering = ['-fecha_derivacion']
        indexes = [
            models.Index(fields=['historia_clinica'], name='idx_deriv_historia'),
        ]

    def __str__(self):
        return f"{self.tipo_derivacion} - {self.historia_clinica.codigo_historia} ({self.nivel_riesgo})"


# ──────────────────────────────────────────────────────────────────────────────
# ENTIDAD: AuditoriaIA (HU-35 / Salvaguarda Ética y Supervisión Humana)
# ──────────────────────────────────────────────────────────────────────────────
class AuditoriaIA(models.Model):
    EVALUACION_CHOICES = [
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('ACEPTADO', 'Aceptado por Terapeuta'),
        ('EDITADO', 'Editado y Aceptado'),
        ('DESCARTADO', 'Descartado por Terapeuta'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formulario_respuesta_id = models.UUIDField(null=True, blank=True, verbose_name="UUID de Respuesta Evaluada")
    psicologo = models.ForeignKey(Psicologo, on_delete=models.SET_NULL, null=True, blank=True, related_name="auditorias_ia", verbose_name="Psicólogo Revisor")
    hash_prompt = models.CharField(max_length=64, verbose_name="Hash SHA-256 del Prompt")
    resumen_generado = models.TextField(verbose_name="Borrador Asistivo Generado")
    prioridad_sugerida = models.CharField(max_length=30, verbose_name="Prioridad Sugerida por Motor")
    reglas_aplicadas = models.JSONField(default=list, blank=True, verbose_name="Reglas Clínicas Transparentes")
    evaluacion_humana = models.CharField(max_length=20, choices=EVALUACION_CHOICES, default='PENDIENTE', verbose_name="Decisión Profesional Humana")
    observaciones_profesional = models.TextField(blank=True, default="", verbose_name="Observaciones del Terapeuta")
    fecha_analisis = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Análisis")
    fecha_decision = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Decisión")
    ip_origen = models.CharField(max_length=45, default="127.0.0.1", verbose_name="IP del Solicitante")

    class Meta:
        db_table = "clinica_auditoriaia"
        verbose_name = "Auditoría de IA Asistiva"
        verbose_name_plural = "Auditorías de IA Asistiva"
        ordering = ['-fecha_analisis']

    def __str__(self):
        return f"Auditoría IA [{self.prioridad_sugerida}] - Decisión: {self.evaluacion_humana}"

