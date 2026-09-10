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
