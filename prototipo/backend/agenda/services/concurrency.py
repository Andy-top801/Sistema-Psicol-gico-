import uuid
from typing import Any
from datetime import date, time
from django.db import transaction
from rest_framework.exceptions import ValidationError
from clinica.models import Paciente, Psicologo
from agenda.models import Cita, Teleconsulta
from agenda.services.availability import AvailabilityValidator

class ConflictResolutionService:
    """
    Servicio de resolución de concurrencia y reserva atómica de citas.
    Aplica bloqueo pesimista (SELECT FOR UPDATE) a nivel de fila y transacción en PostgreSQL
    para asegurar cero colisiones (doble reserva simultánea) bajo alta concurrencia.
    """

    @classmethod
    def reservar_cita(
        cls,
        paciente: Paciente,
        psicologo: Psicologo,
        fecha: date,
        hora_inicio: time,
        hora_fin: time,
        modalidad: str = 'PRESENCIAL',
        motivo_consulta: str = '',
        costo: float | None = None
    ) -> Cita:
        if hora_fin <= hora_inicio:
            raise ValidationError({"hora_fin": "La hora de fin debe ser estrictamente posterior a la hora de inicio."})

        # 1. Validar que el psicólogo tenga disponibilidad configurada en ese horario
        if not AvailabilityValidator.horario_esta_dentro_de_jornada(psicologo, fecha, hora_inicio, hora_fin):
            raise ValidationError({"horario": "El horario seleccionado no se encuentra dentro de la disponibilidad laboral del psicólogo."})

        # 2. Transacción atómica con bloqueo pesimista
        atomic_tx: Any = transaction.atomic()
        with atomic_tx:
            # Bloquear citas existentes del psicólogo en la misma fecha
            # Usando select_for_update() para evitar condiciones de carrera concurrentes
            citas_psico_existentes = list(
                Cita.objects.select_for_update().filter(
                    psicologo=psicologo,
                    fecha=fecha,
                    estado__in=['PROGRAMADA', 'CONFIRMADA']
                )
            )

            # Verificar solapamiento con el psicólogo
            for cita_existente in citas_psico_existentes:
                if hora_inicio < cita_existente.hora_fin and hora_fin > cita_existente.hora_inicio:
                    raise ValidationError({
                        "conflicto": "El psicólogo ya tiene una cita reservada o confirmada en ese intervalo de tiempo."
                    })

            # Verificar que el paciente no tenga otra cita al mismo tiempo
            cita_paciente_traslape = Cita.objects.filter(
                paciente=paciente,
                fecha=fecha,
                estado__in=['PROGRAMADA', 'CONFIRMADA'],
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio
            ).exists()

            if cita_paciente_traslape:
                raise ValidationError({
                    "paciente": "El paciente ya cuenta con otra cita programada en ese mismo horario."
                })

            costo_val = costo if costo is not None else getattr(psicologo, 'tarifa_base', 150.0)
            costo_final = float(str(costo_val))

            # 3. Crear el registro de la Cita
            cita = Cita.objects.create(
                paciente=paciente,
                psicologo=psicologo,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                modalidad=modalidad,
                estado='PROGRAMADA',
                motivo_consulta=motivo_consulta,
                costo=costo_final
            )

            # 4. Si la modalidad es VIRTUAL, aprovisionar de inmediato la sala de Teleconsulta
            if modalidad == 'VIRTUAL':
                sala_id = f"sigepsi-{str(cita.id)[:8]}-{uuid.uuid4().hex[:6]}"
                Teleconsulta.objects.create(
                    cita=cita,
                    sala_id=sala_id
                )

            return cita
