# ==============================================================================
# MÓDULO: agenda/serializers.py
# CAPA BCE: CONTROL (Controller) — Subcomponente de validación y persistencia de
#           CTR_CitaService, CTR_AlertaService
# CASOS DE USO: CU11 (Gestión de Citas), CU10 (Alertas), HU-17 (Cancelación)
# DESCRIPCIÓN: Serializers DRF que implementan los pasos 2-7 de los Diagramas
#              de Comunicación BCE para la reserva/cancelación de citas y la
#              evaluación automática de alertas por inasistencia.
# ==============================================================================
from datetime import datetime, date, time, timedelta
from rest_framework import serializers
from django.utils import timezone
from clinica.models import Paciente, Psicologo
from clinica.serializers import PacienteSerializer, PsicologoSerializer
from agenda.models import Cita, Teleconsulta, Alerta
from agenda.services.concurrency import ConflictResolutionService
from agenda.services.alerts import AlertService

class TeleconsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teleconsulta
        fields = [
            'id', 'cita', 'sala_id', 'jwt_room_token',
            'hora_inicio_real', 'hora_fin_real', 'duracion_segundos'
        ]
        read_only_fields = ['id', 'sala_id', 'jwt_room_token']


# ──────────────────────────────────────────────────────────────────────────────
# SERIALIZER: CitaSerializer — Validación y Persistencia CU11 Pasos 2-7
# DIAGRAMA DE COMUNICACIÓN CU11:
#   Paso 2: Recibe los datos de la cita del IU_AgendaCitas
#   Pasos 3-6: Delega a ConflictResolutionService para bloqueo pesimista
#   Paso 7: Retorna la cita serializada al controlador
# ──────────────────────────────────────────────────────────────────────────────
class CitaSerializer(serializers.ModelSerializer):
    paciente_datos = serializers.SerializerMethodField(read_only=True)
    psicologo_datos = serializers.SerializerMethodField(read_only=True)
    teleconsulta = TeleconsultaSerializer(read_only=True)

    class Meta:
        model = Cita
        fields = [
            'id', 'paciente', 'paciente_datos',
            'psicologo', 'psicologo_datos',
            'fecha', 'hora_inicio', 'hora_fin',
            'modalidad', 'estado', 'motivo_consulta',
            'costo', 'motivo_cancelacion',
            'fecha_creacion', 'fecha_modificacion',
            'teleconsulta'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_modificacion']

    def get_paciente_datos(self, obj):
        u = obj.paciente.usuario
        return {
            "id": str(obj.paciente.id),
            "nombre": f"{u.nombre} {u.apellido}".strip(),
            "ci": obj.paciente.ci,
            "telefono": u.telefono,
            "codigo_expediente": obj.paciente.codigo_expediente
        }

    def get_psicologo_datos(self, obj):
        u = obj.psicologo.usuario
        return {
            "id": str(obj.psicologo.id),
            "nombre": f"{u.nombre} {u.apellido}".strip(),
            "numero_colegiado": obj.psicologo.numero_colegiado,
            "tarifa_base": float(obj.psicologo.tarifa_base),
            "modalidad": obj.psicologo.modalidad
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.paciente and instance.paciente.usuario:
            u = instance.paciente.usuario
            data['paciente_nombre'] = f"{u.nombre} {u.apellido}".strip()
            data['paciente_expediente'] = instance.paciente.codigo_expediente
        if instance.psicologo and instance.psicologo.usuario:
            u = instance.psicologo.usuario
            data['psicologo_nombre'] = f"{u.nombre} {u.apellido}".strip()
        return data


    def create(self, validated_data):
        """
        CU11 Pasos 3-6: Delegar la creación de la cita al servicio de concurrencia.
        ConflictResolutionService realiza SELECT FOR UPDATE (Paso 3), verifica
        ausencia de colisiones (Paso 4), e INSERT INTO agenda_cita (Paso 5).
        Retorna la cita creada (Paso 6).
        """
        return ConflictResolutionService.reservar_cita(
            paciente=validated_data['paciente'],
            psicologo=validated_data['psicologo'],
            fecha=validated_data['fecha'],
            hora_inicio=validated_data['hora_inicio'],
            hora_fin=validated_data['hora_fin'],
            modalidad=validated_data.get('modalidad', 'PRESENCIAL'),
            motivo_consulta=validated_data.get('motivo_consulta', ''),
            costo=validated_data.get('costo', None)
        )

    def update(self, instance, validated_data):
        """
        CU11 Paso 5 (actualización de estado):
        Si el estado cambia a 'INASISTENCIA', dispara CU10 Paso 3
        evaluando alertas de ausentismo automáticamente.
        """
        antiguo_estado = instance.estado
        nuevo_estado = validated_data.get('estado', antiguo_estado)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # CU10 Paso 3: Si cambió a INASISTENCIA, evaluar alertas automáticas
        # Esto dispara el flujo CU10 (Alertas de Priorización) automáticamente
        if nuevo_estado == 'INASISTENCIA' and antiguo_estado != 'INASISTENCIA':
            AlertService.evaluar_inasistencias_paciente(instance.paciente)

        return instance


# ──────────────────────────────────────────────────────────────────────────────
# SERIALIZER: CancelarCitaSerializer — HU-17 Cancelación de Citas
# DIAGRAMA DE COMUNICACIÓN CU11 (variante cancelación):
#   Paso 3: Validar motivo (mínimo 5 caracteres) y anticipación (2h mínimo)
#   Regla HU-17: Pacientes deben cancelar con al menos 2 horas de anticipación
# ──────────────────────────────────────────────────────────────────────────────
class CancelarCitaSerializer(serializers.Serializer):
    motivo = serializers.CharField(required=True, min_length=5, max_length=500)

    def validate(self, attrs):
        """HU-17 Paso 3: Validar estado de la cita y anticipación mínima."""
        cita = self.context.get('cita')
        request = self.context.get('request')

        if not cita:
            raise serializers.ValidationError("Cita no encontrada.")

        if cita.estado in ['CANCELADA', 'REALIZADA']:
            raise serializers.ValidationError(f"No es posible cancelar una cita con estado '{cita.estado}'.")

        # HU-17: Si es el paciente quien cancela, verificar anticipación mínima de 2 horas
        if request and request.user and hasattr(request.user, 'rol') and request.user.rol:
            if request.user.rol.nombre == "Paciente":
                ahora = timezone.localtime()
                cita_dt = timezone.make_aware(
                    datetime.combine(cita.fecha, cita.hora_inicio),
                    timezone.get_current_timezone()
                )
                limite_anticipacion = ahora + timedelta(hours=2)

                if cita_dt < limite_anticipacion:
                    raise serializers.ValidationError({
                        "anticipacion": "Las cancelaciones autónomas deben realizarse con al menos 2 horas de anticipación. Para cancelaciones de último momento, comuníquese con recepción."
                    })

        return attrs


class TeleconsultaFinishSerializer(serializers.Serializer):
    duracion_segundos = serializers.IntegerField(required=False, default=0, min_value=0)
    notas_sesion = serializers.CharField(required=False, allow_blank=True, default="")


class AlertaSerializer(serializers.ModelSerializer):
    paciente_datos = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Alerta
        fields = [
            'id', 'paciente', 'paciente_datos',
            'tipo', 'severidad', 'descripcion',
            'resuelta', 'fecha_creacion', 'fecha_resolucion',
            'nota_resolucion'
        ]
        read_only_fields = ['id', 'fecha_creacion']

    def get_paciente_datos(self, obj):
        u = obj.paciente.usuario
        return {
            "id": str(obj.paciente.id),
            "nombre": f"{u.nombre} {u.apellido}".strip(),
            "codigo_expediente": obj.paciente.codigo_expediente,
            "ci": obj.paciente.ci,
            "telefono": u.telefono
        }
