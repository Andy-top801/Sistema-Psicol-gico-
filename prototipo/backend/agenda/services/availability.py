# ==============================================================================
# SERVICIO: agenda/services/availability.py
# CAPA BCE: CONTROL (Controller) — Subcomponente de CTR_Disponibilidad y CTR_CitaService
# CASOS DE USO: CU8 (Gestión de Disponibilidad), CU11 (Gestión de Citas)
# DIAGRAMA DE COMUNICACIÓN CU8 – Paso 5:
#   "Guardar franjas y particionar bloques en DB"
#   Este servicio genera los slots consultables a partir de las franjas.
# DIAGRAMA DE COMUNICACIÓN CU11 – Paso 3a:
#   Antes de iniciar SELECT FOR UPDATE, valida que el horario solicitado esté
#   dentro de la jornada laboral del psicólogo (clinica_disponibilidad).
# ==============================================================================
from datetime import datetime, date, time, timedelta
from clinica.models import Disponibilidad, Psicologo
from agenda.models import Cita


class AvailabilityValidator:
    @staticmethod
    def fecha_a_dia_semana_db(fecha: date) -> int:
        # Python: Monday=0, Sunday=6
        # BD: Domingo=0, Lunes=1, ..., Sábado=6
        return (fecha.weekday() + 1) % 7

    @classmethod
    def obtener_slots_disponibles(cls, psicologo: Psicologo, fecha: date):
        """
        CU8 Paso 5 / CU11 Paso 3: Genera la matriz de slots libres para un psicólogo
        en una fecha dada, cruzando las franjas de disponibilidad contra las citas existentes.
        """
        # CU8 Paso 5: Convertir fecha calendario a día de semana en formato BD
        dia_semana_db = cls.fecha_a_dia_semana_db(fecha)
        # CU8 Paso 5: Consultar franjas activas del psicólogo para ese día
        disponibilidades = Disponibilidad.objects.filter(
            psicologo=psicologo,
            dia_semana=dia_semana_db,
            activo=True
        ).order_by('hora_inicio')

        if not disponibilidades.exists():
            return []

        # CU11 Paso 3: Obtener citas ya ocupadas (PROGRAMADA o CONFIRMADA) para detectar colisiones
        citas_ocupadas = list(Cita.objects.filter(
            psicologo=psicologo,
            fecha=fecha,
            estado__in=['PROGRAMADA', 'CONFIRMADA']
        ).values_list('hora_inicio', 'hora_fin'))

        slots = []
        for disp in disponibilidades:
            # CU8 Paso 5: Particionar cada franja en bloques según duracion_bloque_min
            duracion_min = disp.duracion_bloque_min or 50
            bloque_delta = timedelta(minutes=duracion_min)

            # CU8 Paso 5: Generar intervalos desde hora_inicio hasta hora_fin
            cur_dt = datetime.combine(fecha, disp.hora_inicio)
            fin_dt = datetime.combine(fecha, disp.hora_fin)

            while cur_dt + bloque_delta <= fin_dt:
                slot_inicio = cur_dt.time()
                slot_fin = (cur_dt + bloque_delta).time()

                # CU11 Paso 3: Verificar si el slot solapa con alguna cita existente
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
        """
        CU11 Paso 3a: Valida que el rango horario solicitado para la cita
        coincida con una franja de disponibilidad activa del psicólogo.
        Si no existe una franja que cubra el rango, se rechaza la reserva.
        """
        dia_semana_db = cls.fecha_a_dia_semana_db(fecha)
        return Disponibilidad.objects.filter(
            psicologo=psicologo,
            dia_semana=dia_semana_db,
            hora_inicio__lte=hora_inicio,
            hora_fin__gte=hora_fin,
            activo=True
        ).exists()
