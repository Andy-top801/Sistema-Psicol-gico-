from clinica.models import Paciente
from agenda.models import Cita, Alerta

class AlertService:
    """
    Servicio de detección proactiva de riesgos clínicos y alertas de priorización (HU-21).
    Detecta ausentismo reiterado (2 o más inasistencias consecutivas) y genera alertas automáticas.
    """

    @classmethod
    def evaluar_inasistencias_paciente(cls, paciente: Paciente) -> Alerta | None:
        # Obtener las últimas citas del paciente ordenadas por fecha descendente
        ultimas_citas = list(Cita.objects.filter(
            paciente=paciente,
            estado__in=['REALIZADA', 'INASISTENCIA']
        ).order_by('-fecha', '-hora_inicio')[:5])

        if len(ultimas_citas) < 2:
            return None

        # Verificar si las 2 más recientes son ambas INASISTENCIA
        consecutivas_inasistencia = (
            ultimas_citas[0].estado == 'INASISTENCIA' and
            ultimas_citas[1].estado == 'INASISTENCIA'
        )

        if consecutivas_inasistencia:
            # Comprobar si ya existe una alerta activa sin resolver para este paciente
            alerta_existente = Alerta.objects.filter(
                paciente=paciente,
                tipo='INASISTENCIA_REITERADA',
                resuelta=False
            ).first()

            if not alerta_existente:
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
