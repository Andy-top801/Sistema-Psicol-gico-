# ==============================================================================
# SERVICIO: agenda/services/alerts.py
# CAPA BCE: CONTROL (Controller) — CTR_AlertaService
# CASO DE USO: CU10 – Gestión de Alertas Tempranas y Priorización (HU-21)
# DIAGRAMA DE COMUNICACIÓN CU10:
#   Actor → IU: 1: Consultar bandeja de alertas prioritarias
#   IU → CTR:   2: GET /api/agenda/alertas/?resuelta=false
#   CTR → CE:   3: Evaluar historial de inasistencias consecutivas (2+)
#   CE → CTR:   4: Pacientes con ausentismo crítico identificados
#   CTR → CE:   5: INSERT / UPDATE agenda_alerta (prioridad='ALTA')
#   CE → CTR:   6: Alertas clínicas registradas en esquema
#   CTR → IU:   7: 200 OK {alertas_activas, nivel_riesgo: ALTO}
#   IU → Actor: 8: Desplegar lista de pacientes en riesgo de abandono
#
# ESTE SERVICIO IMPLEMENTA LOS PASOS 3 A 6 DEL DIAGRAMA.
# Se invoca automáticamente cuando una cita cambia a estado='INASISTENCIA'
# (disparado desde CitaSerializer.update(), paso 3 del flujo CU10).
# ==============================================================================
from clinica.models import Paciente
from agenda.models import Cita, Alerta

class AlertService:
    """
    Servicio de detección proactiva de riesgos clínicos y alertas de priorización (HU-21).
    Detecta ausentismo reiterado (2 o más inasistencias consecutivas) y genera alertas automáticas.
    """

    @classmethod
    def evaluar_inasistencias_paciente(cls, paciente: Paciente) -> Alerta | None:
        # ====================================================================
        # CU10 Paso 3: Evaluar historial de inasistencias consecutivas
        # Se obtienen las últimas 5 citas cerradas (REALIZADA o INASISTENCIA)
        # ordenadas cronológicamente descendente para analizar el patrón.
        # ====================================================================
        ultimas_citas = list(Cita.objects.filter(
            paciente=paciente,
            estado__in=['REALIZADA', 'INASISTENCIA']
        ).order_by('-fecha', '-hora_inicio')[:5])

        if len(ultimas_citas) < 2:
            return None

        # CU10 Paso 3 (cont.): Verificar si las 2 citas más recientes son INASISTENCIA
        consecutivas_inasistencia = (
            ultimas_citas[0].estado == 'INASISTENCIA' and
            ultimas_citas[1].estado == 'INASISTENCIA'
        )

        if consecutivas_inasistencia:
            # CU10 Paso 4: Paciente con ausentismo crítico identificado
            # Verificar si ya existe una alerta activa para evitar duplicados.
            alerta_existente = Alerta.objects.filter(
                paciente=paciente,
                tipo='INASISTENCIA_REITERADA',
                resuelta=False
            ).first()

            if not alerta_existente:
                # ============================================================
                # CU10 Paso 5: INSERT INTO agenda_alerta (prioridad='ALTA')
                # Se genera una nueva alerta con tipo='INASISTENCIA_REITERADA'
                # y severidad='ALTA' para que aparezca en la bandeja del
                # equipo terapéutico (IU_AlertasClinicas en Angular).
                # CU10 Paso 6: CE retorna "Alertas clínicas registradas en esquema"
                # ============================================================
                nueva_alerta = Alerta.objects.create(
                    paciente=paciente,
                    tipo='INASISTENCIA_REITERADA',
                    severidad='ALTA',
                    descripcion=(
                        f"Alerta preventiva: El paciente {paciente.usuario.nombre} {paciente.usuario.apellido} "
                        f"(Expediente: {paciente.codigo_expediente}) acumula 2 inasistencias consecutivas a sus sesiones. "
                        f"Se sugiere contactar de inmediato para prevenir deserción del proceso terapéutico."
                    ),
                    resuelta=False
                )
                return nueva_alerta
            return alerta_existente

        return None
