from datetime import datetime, date, time, timedelta
from clinica.models import Disponibilidad, Psicologo
from agenda.models import Cita

class AvailabilityValidator:
    """
    Servicio de cálculo y validación de franjas horarias libres y ocupadas.
    Convierte el día calendario al formato de base de datos (0=Domingo, 1=Lunes, ..., 6=Sábado)
    y desglosa los bloques según la duración configurada (por defecto 50 min).
    """

    @staticmethod
    def fecha_a_dia_semana_db(fecha: date) -> int:
        # Python: Monday=0, Sunday=6
        # BD: Domingo=0, Lunes=1, ..., Sábado=6
        return (fecha.weekday() + 1) % 7

    @classmethod
    def obtener_slots_disponibles(cls, psicologo: Psicologo, fecha: date):
        dia_semana_db = cls.fecha_a_dia_semana_db(fecha)
        disponibilidades = Disponibilidad.objects.filter(
            psicologo=psicologo,
            dia_semana=dia_semana_db,
            activo=True
        ).order_by('hora_inicio')

        if not disponibilidades.exists():
            return []

        # Citas ya ocupadas en esa fecha (solo activas: PROGRAMADA o CONFIRMADA)
        citas_ocupadas = list(Cita.objects.filter(
            psicologo=psicologo,
            fecha=fecha,
            estado__in=['PROGRAMADA', 'CONFIRMADA']
        ).values_list('hora_inicio', 'hora_fin'))

        slots = []
        for disp in disponibilidades:
            duracion_min = disp.duracion_bloque_min or 50
            bloque_delta = timedelta(minutes=duracion_min)

            # Generar intervalos desde hora_inicio hasta hora_fin
            cur_dt = datetime.combine(fecha, disp.hora_inicio)
            fin_dt = datetime.combine(fecha, disp.hora_fin)

            while cur_dt + bloque_delta <= fin_dt:
                slot_inicio = cur_dt.time()
                slot_fin = (cur_dt + bloque_delta).time()

                # Verificar si solapa con alguna cita ocupada
                colision = False
                for c_ini, c_fin in citas_ocupadas:
                    if slot_inicio < c_fin and slot_fin > c_ini:
                        colision = True
                        break

                slots.append({
                    "hora_inicio": slot_inicio.strftime("%H:%M:%S"),
                    "hora_fin": slot_fin.strftime("%H:%M:%S"),
                    "duracion_min": duracion_min,
                    "disponible": not colision
                })

                cur_dt += bloque_delta

        return slots

    @classmethod
    def horario_esta_dentro_de_jornada(cls, psicologo: Psicologo, fecha: date, hora_inicio: time, hora_fin: time) -> bool:
        """Valida que el rango solicitado coincida con una franja de disponibilidad activa del psicólogo."""
        dia_semana_db = cls.fecha_a_dia_semana_db(fecha)
        return Disponibilidad.objects.filter(
            psicologo=psicologo,
            dia_semana=dia_semana_db,
            hora_inicio__lte=hora_inicio,
            hora_fin__gte=hora_fin,
            activo=True
        ).exists()
