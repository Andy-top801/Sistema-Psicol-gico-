# ==============================================================================
# SERVICIO: agenda/services/concurrency.py
# CAPA BCE: CONTROL (Controller) — CTR_CitaService
# CASO DE USO: CU11 – Programación, Reserva y Gestión de Citas (HU-15, HU-16, HU-17, HU-22)
# DIAGRAMA DE COMUNICACIÓN CU11:
#   Actor → IU: 1: Seleccionar paciente, terapeuta, fecha y slot
#   IU → CTR:   2: POST /api/agenda/citas/ {fecha, hora, modalidad}
#   CTR → CE:   3: Iniciar tx y SELECT FOR UPDATE sobre slot
#   CE → CTR:   4: Bloqueo pesimista concedido (slot libre)
#   CTR → CE:   5: INSERT INTO agenda_cita y marcar slot ocupado
#   CE → CTR:   6: Cita registrada sin colisión horaria
#   CTR → IU:   7: 201 Created {cita_id, estado: 'PROGRAMADA'}
#   IU → Actor: 8: Desplegar comprobante de cita confirmada
#
# ESTE SERVICIO IMPLEMENTA LOS PASOS 3 A 6 DEL DIAGRAMA.
# ==============================================================================
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
        # ====================================================================
        # CU11 Paso 3 (Pre-validación): Validar hora coherente
        # Antes de iniciar la transacción, verificamos que hora_fin > hora_inicio.
        # ====================================================================
        if hora_fin <= hora_inicio:
            raise ValidationError({"hora_fin": "La hora de fin debe ser estrictamente posterior a la hora de inicio."})

        # ====================================================================
        # CU11 Paso 3a: Validar que el psicólogo tenga disponibilidad configurada
        # El AvailabilityValidator consulta clinica_disponibilidad para verificar
        # que el rango (hora_inicio, hora_fin) caiga dentro de una franja activa.
        # ====================================================================
        if not AvailabilityValidator.horario_esta_dentro_de_jornada(psicologo, fecha, hora_inicio, hora_fin):
            raise ValidationError({"horario": "El horario seleccionado no se encuentra dentro de la disponibilidad laboral del psicólogo."})

        # ====================================================================
        # CU11 Paso 3b: Transacción atómica con bloqueo pesimista
        # Se inicia una transacción PostgreSQL con SELECT FOR UPDATE para
        # bloquear las filas de citas existentes del psicólogo en la misma fecha.
        # Esto previene condiciones de carrera cuando dos usuarios intentan
        # reservar el mismo bloque simultáneamente (HU-15 Criterio b).
        # ====================================================================
        atomic_tx: Any = transaction.atomic()
        with atomic_tx:
            # CU11 Paso 3c: SELECT FOR UPDATE – Bloqueo pesimista sobre citas del psicólogo
            # Se obtienen TODAS las citas activas del psicólogo para esa fecha con
            # bloqueo exclusivo a nivel de fila en PostgreSQL.
            citas_psico_existentes = list(
                Cita.objects.select_for_update().filter(
                    psicologo=psicologo,
                    fecha=fecha,
                    estado__in=['PROGRAMADA', 'CONFIRMADA']
                )
            )

            # CU11 Paso 4: Verificar ausencia de solapamiento con citas del psicólogo
            # Se compara el rango (hora_inicio, hora_fin) solicitado contra cada cita
            # existente. Si hay colisión, el paso 4 retorna "slot ocupado" al CTR.
            for cita_existente in citas_psico_existentes:
                if hora_inicio < cita_existente.hora_fin and hora_fin > cita_existente.hora_inicio:
                    raise ValidationError({
                        "conflicto": "El psicólogo ya tiene una cita reservada o confirmada en ese intervalo de tiempo."
                    })

            # CU11 Paso 4 (cont.): Verificar que el paciente no tenga otra cita al mismo tiempo
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

            # ================================================================
            # CU11 Paso 5: INSERT INTO agenda_cita y marcar slot ocupado
            # Se crea el registro de la cita con estado='PROGRAMADA'.
            # CE retorna "Cita registrada sin colisión horaria" (Paso 6).
            # ================================================================
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

            # ================================================================
            # CU11 Paso 5 (extensión HU-15 Criterio c):
            # Si la modalidad es VIRTUAL, aprovisionar inmediatamente la sala
            # de Teleconsulta con un identificador único de sala Jitsi Meet.
            # Esto se vincula al Diagrama de Comunicación CU13 Paso 5.
            # ================================================================
            if modalidad == 'VIRTUAL':
                sala_id = f"sigepsi-{str(cita.id)[:8]}-{uuid.uuid4().hex[:6]}"
                Teleconsulta.objects.create(
                    cita=cita,
                    sala_id=sala_id
                )

            # CU11 Paso 6: Retornar la cita creada exitosamente al CTR
            return cita
