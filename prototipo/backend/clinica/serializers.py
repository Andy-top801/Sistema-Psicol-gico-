# ==============================================================================
# MÓDULO: clinica/serializers.py
# CAPA BCE: CONTROL (Controller) — Subcomponente de validación de CTR_Psicologo,
#           CTR_Paciente, CTR_Disponibilidad
# CASOS DE USO: CU6 (Psicólogos), CU7 (Pacientes), CU8 (Disponibilidad)
# DESCRIPCIÓN: Serializers DRF que implementan los pasos 3-4 (validación) y
#              5-6 (persistencia) de los Diagramas de Comunicación BCE.
# ==============================================================================
from datetime import date
from rest_framework import serializers
from django.db import transaction
from accounts.models import Usuario, Rol
from accounts.serializers import UsuarioSerializer
from clinica.models import Especialidad, Psicologo, PsicologoEspecialidad, Disponibilidad, Paciente

class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = ['id', 'nombre', 'descripcion']


# ──────────────────────────────────────────────────────────────────────────────
# SERIALIZER: DisponibilidadSerializer — Validación CU8 Pasos 3-4
# DIAGRAMA DE COMUNICACIÓN CU8:
#   Paso 3: "Validar coherencia de horarios (inicio < fin) y no traslape"
#   Paso 4: CE retorna "Franjas válidas y terapeuta activo"
# ──────────────────────────────────────────────────────────────────────────────
class DisponibilidadSerializer(serializers.ModelSerializer):
    dia_semana_texto = serializers.CharField(source='get_dia_semana_display', read_only=True)

    class Meta:
        model = Disponibilidad
        fields = [
            'id', 'psicologo', 'dia_semana', 'dia_semana_texto',
            'hora_inicio', 'hora_fin', 'duracion_bloque_min', 'activo'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        """CU8 Paso 3: Validar coherencia de horarios y no solapamiento."""
        hora_inicio = attrs.get('hora_inicio', getattr(self.instance, 'hora_inicio', None))
        hora_fin = attrs.get('hora_fin', getattr(self.instance, 'hora_fin', None))
        psicologo = attrs.get('psicologo', getattr(self.instance, 'psicologo', None))
        dia_semana = attrs.get('dia_semana', getattr(self.instance, 'dia_semana', None))

        # CU8 Paso 3: Validar que hora_fin > hora_inicio
        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            raise serializers.ValidationError({"hora_fin": "La hora de finalización debe ser posterior a la hora de inicio."})

        # CU8 Paso 3: Validar no traslape con otras franjas del mismo psicólogo y día
        if psicologo and dia_semana is not None and hora_inicio and hora_fin:
            qs = Disponibilidad.objects.filter(
                psicologo=psicologo,
                dia_semana=dia_semana,
                activo=True
            )
            if self.instance:
                qs = qs.exclude(id=self.instance.id)

            traslape = qs.filter(
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio
            ).exists()
            if traslape:
                raise serializers.ValidationError({"non_field_errors": "Existe un traslape con otro bloque horario configurado para este día."})

        # CU8 Paso 4: Retorna "Franjas válidas" al controlador
        return attrs


def crear_disponibilidad_default(psicologo):
    """
    CU6 / CU8: Configura disponibilidad estándar inicial (Lunes a Viernes de 08:00 a 12:00
    y de 14:00 a 18:00, duración de bloque 50 min) para que el terapeuta esté habilitado
    inmediatamente en la agenda de citas al momento de su alta.
    """
    from clinica.models import Disponibilidad
    from datetime import time
    if not Disponibilidad.objects.filter(psicologo=psicologo).exists():
        for dia in range(1, 6):  # 1=Lunes, 2=Martes, 3=Miércoles, 4=Jueves, 5=Viernes
            # Franja Mañana
            Disponibilidad.objects.create(
                psicologo=psicologo,
                dia_semana=dia,
                hora_inicio=time(8, 0),
                hora_fin=time(12, 0),
                duracion_bloque_min=50,
                activo=True
            )
            # Franja Tarde
            Disponibilidad.objects.create(
                psicologo=psicologo,
                dia_semana=dia,
                hora_inicio=time(14, 0),
                hora_fin=time(18, 0),
                duracion_bloque_min=50,
                activo=True
            )


class PsicologoSerializer(serializers.ModelSerializer):
    usuario_id = serializers.UUIDField(write_only=True, required=False)
    usuario = UsuarioSerializer(read_only=True)
    usuario_datos = UsuarioSerializer(source='usuario', read_only=True)
    # Datos opcionales para crear usuario al vuelo
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    nombre = serializers.CharField(write_only=True, required=False)
    apellido = serializers.CharField(write_only=True, required=False, allow_blank=True)
    telefono = serializers.CharField(write_only=True, required=False, allow_blank=True)
    numero_colegiado = serializers.CharField(required=False, allow_blank=True)

    especialidades_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Especialidad.objects.all(),
        source='especialidades',
        required=False
    )
    especialidad_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    especialidades_detalle = EspecialidadSerializer(source='especialidades', many=True, read_only=True)
    disponibilidades = DisponibilidadSerializer(many=True, read_only=True)

    class Meta:
        model = Psicologo
        fields = [
            'id', 'usuario', 'usuario_id', 'usuario_datos',
            'email', 'password', 'nombre', 'apellido', 'telefono',
            'numero_colegiado', 'biografia', 'modalidad',
            'tarifa_base', 'activo', 'fecha_ingreso',
            'especialidades_ids', 'especialidad_ids',
            'especialidades_detalle', 'disponibilidades'
        ]
        read_only_fields = ['id', 'fecha_ingreso']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        u_data = data.get('usuario') or data.get('usuario_datos')
        if u_data:
            data['usuario'] = u_data
            data['usuario_datos'] = u_data
        return data

    def validate_tarifa_base(self, value):
        """CU6 Paso 3: Validar que la tarifa base no sea negativa."""
        if value < 0:
            raise serializers.ValidationError("La tarifa base no puede ser negativa.")
        return value

    def validate(self, attrs):
        """
        CU6 Paso 3: Validar datos del psicólogo (email y colegiatura únicos).
        Implementa la validación BCE donde CTR_Psicologo consulta CE para
        verificar unicidad antes de crear el registro.
        """
        import random
        usuario_id = attrs.get('usuario_id')
        email = attrs.get('email')
        if email:
            email = email.strip().lower()
            attrs['email'] = email

        esp_ids = attrs.pop('especialidad_ids', None)
        if esp_ids and 'especialidades' not in attrs:
            attrs['especialidades'] = list(Especialidad.objects.filter(id__in=esp_ids))

        if not self.instance and not usuario_id and not email:
            raise serializers.ValidationError({
                "usuario": "Debe especificar 'usuario_id' existente o 'email' y 'nombre' para crear el usuario."
            })
        if email and not usuario_id and Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Ya existe una cuenta de usuario con este correo electrónico."})

        num_col = attrs.get('numero_colegiado')
        if not num_col and not getattr(self.instance, 'numero_colegiado', None):
            attrs['numero_colegiado'] = f"COL-PSI-{random.randint(1000, 9999)}"
        elif num_col:
            qs = Psicologo.objects.filter(numero_colegiado__iexact=num_col)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"numero_colegiado": "Ya existe un psicólogo con este número de colegiado."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        CU6 Pasos 5-6: Crear Usuario y Psicólogo en esquema tenant.
        Se crea atómicamente: 1) cuenta de usuario con rol 'Psicólogo',
        2) perfil profesional con número de colegiado, y 3) disponibilidad por defecto.
        CE retorna "Registros creados exitosamente" (Paso 6).
        """
        especialidades = validated_data.pop('especialidades', [])
        usuario_id = validated_data.pop('usuario_id', None)
        email = validated_data.pop('email', None)
        password = validated_data.pop('password', None)
        if not password or not password.strip():
            password = 'PsicologoSeguro2026*'
        nombre = validated_data.pop('nombre', '')
        apellido = validated_data.pop('apellido', '')
        telefono = validated_data.pop('telefono', '')

        if usuario_id:
            # CU6 Paso 5a: Vincular a usuario existente
            usuario = Usuario.objects.get(id=usuario_id)
        else:
            # CU6 Paso 5b: Crear usuario nuevo con rol Psicólogo
            rol_psico = Rol.objects.filter(nombre__icontains="Psicólogo").first()
            if not rol_psico:
                rol_psico = Rol.objects.filter(nombre__icontains="Psicologo").first()
            usuario = Usuario.objects.create_user(
                email=email,
                password=password,
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                rol=rol_psico
            )

        # CU6 Paso 5c: Crear perfil profesional del psicólogo
        psicologo = Psicologo.objects.create(usuario=usuario, **validated_data)
        # CU6 Paso 5d: Vincular especialidades seleccionadas (relación M:N)
        if especialidades:
            psicologo.especialidades.set(especialidades)
        # CU6/CU8 Paso 5e: Crear disponibilidad por defecto (L-V, 08-12, 14-18)
        crear_disponibilidad_default(psicologo)
        # CU6 Paso 6: Retornar psicólogo creado exitosamente
        return psicologo

    @transaction.atomic
    def update(self, instance, validated_data):
        especialidades = validated_data.pop('especialidades', None)
        # Actualizar datos de usuario si se suministraron
        nombre = validated_data.pop('nombre', None)
        apellido = validated_data.pop('apellido', None)
        telefono = validated_data.pop('telefono', None)
        email = validated_data.pop('email', None)
        if any([nombre, apellido, telefono, email]):
            if nombre is not None:
                instance.usuario.nombre = nombre
            if apellido is not None:
                instance.usuario.apellido = apellido
            if telefono is not None:
                instance.usuario.telefono = telefono
            if email is not None:
                instance.usuario.email = email.strip().lower()
            instance.usuario.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if especialidades is not None:
            instance.especialidades.set(especialidades)
        return instance


class PacienteSerializer(serializers.ModelSerializer):
    usuario_id = serializers.UUIDField(write_only=True, required=False)
    usuario = UsuarioSerializer(read_only=True)
    usuario_datos = UsuarioSerializer(source='usuario', read_only=True)
    # Campos para creación directa de usuario
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    nombre = serializers.CharField(write_only=True, required=False)
    apellido = serializers.CharField(write_only=True, required=False, allow_blank=True)
    telefono = serializers.CharField(write_only=True, required=False, allow_blank=True)

    codigo_expediente = serializers.CharField(required=False, allow_blank=True)
    edad = serializers.SerializerMethodField(read_only=True)
    es_menor_de_edad = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Paciente
        fields = [
            'id', 'usuario', 'usuario_id', 'usuario_datos',
            'email', 'password', 'nombre', 'apellido', 'telefono',
            'codigo_expediente', 'ci', 'fecha_nacimiento', 'genero',
            'contacto_emergencia_nombre', 'contacto_emergencia_telf',
            'tutor_legal_nombre', 'tutor_legal_ci', 'fecha_registro',
            'edad', 'es_menor_de_edad'
        ]
        read_only_fields = ['id', 'fecha_registro']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        u_data = data.get('usuario') or data.get('usuario_datos')
        if u_data:
            data['usuario'] = u_data
            data['usuario_datos'] = u_data
        return data

    def get_edad(self, obj):
        return obj.calcular_edad()

    def get_es_menor_de_edad(self, obj):
        return obj.es_menor_de_edad

    def validate(self, attrs):
        """
        CU7 Paso 3: Validar unicidad de CI en tenant activo.
        Implementa la validación BCE donde CTR_Paciente consulta CE para
        verificar no duplicación de CI y código de expediente, y para validar
        obligatoriedad de tutor legal en menores de 18 años.
        CE retorna "Documento no duplicado y tutor válido" (Paso 4).
        """
        # CU7 Paso 3a: Validar edad y obligatoriedad de tutor legal
        fecha_nac = attrs.get('fecha_nacimiento', getattr(self.instance, 'fecha_nacimiento', None))
        tutor_nombre = attrs.get('tutor_legal_nombre', getattr(self.instance, 'tutor_legal_nombre', ''))
        tutor_ci = attrs.get('tutor_legal_ci', getattr(self.instance, 'tutor_legal_ci', ''))

        if fecha_nac:
            hoy = date.today()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            if edad < 0:
                raise serializers.ValidationError({"fecha_nacimiento": "La fecha de nacimiento no puede ser futura."})
            # CU7 Paso 3b: Si es menor de 18, tutor_legal es obligatorio (HU-13 Criterio c)
            if edad < 18:
                if not tutor_nombre or not tutor_nombre.strip():
                    raise serializers.ValidationError({
                        "tutor_legal_nombre": "El tutor legal es obligatorio para pacientes menores de edad (< 18 años)."
                    })
                if not tutor_ci or not tutor_ci.strip():
                    raise serializers.ValidationError({
                        "tutor_legal_ci": "El CI del tutor legal es obligatorio para pacientes menores de edad."
                    })

        # CU7 Paso 3c: Validar email y usuario
        usuario_id = attrs.get('usuario_id')
        email = attrs.get('email')
        if email:
            email = email.strip().lower()
            attrs['email'] = email

        if not self.instance and not usuario_id and not email:
            raise serializers.ValidationError({
                "usuario": "Debe proporcionar 'usuario_id' o bien 'email' y 'nombre' del paciente."
            })
        if email and not usuario_id and Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Ya existe una cuenta de usuario con este correo electrónico."})

        # CU7 Paso 3d: Validar unicidad de CI en el tenant
        ci = attrs.get('ci')
        if ci:
            qs = Paciente.objects.filter(ci__iexact=ci)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"ci": "Ya existe un paciente con este CI."})

        # CU7 Paso 3e: Validar unicidad de código de expediente
        codigo_exp = attrs.get('codigo_expediente')
        if codigo_exp:
            qs = Paciente.objects.filter(codigo_expediente__iexact=codigo_exp)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"codigo_expediente": "Ya existe un paciente con este código de expediente."})

        # CU7 Paso 4: Retorna "Documento no duplicado y tutor válido"
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        CU7 Pasos 5-6: INSERT INTO clinica_paciente con código único.
        Se crea atómicamente: 1) cuenta de usuario con rol 'Paciente',
        2) expediente clínico con código autogenerado (EXP-YYYYMM-XXXX).
        CE retorna "Paciente registrado en esquema tenant" (Paso 6).
        """
        import random
        from django.utils import timezone

        usuario_id = validated_data.pop('usuario_id', None)
        email = validated_data.pop('email', None)
        password = validated_data.pop('password', None)
        if not password or not password.strip():
            password = 'PacienteSeguro2026*'
        nombre = validated_data.pop('nombre', '')
        apellido = validated_data.pop('apellido', '')
        telefono = validated_data.pop('telefono', '')

        # CU7 Paso 5a: Generar código de expediente automáticamente si no fue proporcionado
        if not validated_data.get('codigo_expediente'):
            prefix = f"EXP-{timezone.localdate().strftime('%Y%m')}"
            rnd = random.randint(1000, 9999)
            while Paciente.objects.filter(codigo_expediente=f"{prefix}-{rnd}").exists():
                rnd = random.randint(1000, 9999)
            validated_data['codigo_expediente'] = f"{prefix}-{rnd}"

        if usuario_id:
            # CU7 Paso 5b: Vincular a usuario existente
            usuario = Usuario.objects.get(id=usuario_id)
        else:
            # CU7 Paso 5c: Crear usuario nuevo con rol Paciente
            rol_paciente = Rol.objects.filter(nombre__icontains="Paciente").first()
            usuario = Usuario.objects.create_user(
                email=email,
                password=password,
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                rol=rol_paciente
            )

        # CU7 Paso 5d: Crear expediente clínico del paciente
        paciente = Paciente.objects.create(usuario=usuario, **validated_data)
        # CU7 Paso 6: Retornar paciente creado exitosamente
        return paciente

    @transaction.atomic
    def update(self, instance, validated_data):
        nombre = validated_data.pop('nombre', None)
        apellido = validated_data.pop('apellido', None)
        telefono = validated_data.pop('telefono', None)
        email = validated_data.pop('email', None)
        if any([nombre, apellido, telefono, email]):
            if nombre is not None:
                instance.usuario.nombre = nombre
            if apellido is not None:
                instance.usuario.apellido = apellido
            if telefono is not None:
                instance.usuario.telefono = telefono
            if email is not None:
                instance.usuario.email = email.strip().lower()
            instance.usuario.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

