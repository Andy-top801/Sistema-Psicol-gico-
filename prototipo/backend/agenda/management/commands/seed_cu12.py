# -*- coding: utf-8 -*-
# Datos de demostración CU12/HU-43: citas CONFIRMADAS dentro de las ventanas de 24h y 1h,
# relativas a la hora actual, para el paciente juan.perez@paciente.com (centro_esperanza).
#     python manage.py seed_cu12
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_tenants.utils import schema_context

MARCA = "[DEMO CU12]"


def _slot(dt):
    """Redondea a múltiplo de 5 min y evita que la sesión de 50 min cruce la medianoche."""
    dt = dt.replace(second=0, microsecond=0, minute=(dt.minute // 5) * 5)
    if dt.hour == 23 and dt.minute > 5:
        dt = dt.replace(minute=5)
    return dt


class Command(BaseCommand):
    help = "Crea citas confirmadas de demostración para ver CU12 (recordatorios 24h y 1h)."

    def add_arguments(self, parser):
        parser.add_argument('--tenant', default='centro_esperanza')
        parser.add_argument('--email', default='juan.perez@paciente.com')

    def handle(self, *args, **opts):
        with schema_context(opts['tenant']):
            from clinica.models import Paciente, Psicologo
            from agenda.models import Cita, Teleconsulta

            paciente = Paciente.objects.select_related('usuario').get(usuario__email=opts['email'])
            psicologo = (Psicologo.objects.filter(usuario__email__startswith='psicologo@').first()
                         or Psicologo.objects.first())

            Cita.objects.filter(paciente=paciente, motivo_consulta__startswith=MARCA).delete()

            ahora = timezone.localtime()
            for horas, modalidad, texto in [
                (20, 'PRESENCIAL', 'Seguimiento de técnicas de afrontamiento'),
                (0.75, 'VIRTUAL', 'Teleconsulta de control semanal'),
            ]:
                inicio = _slot(ahora + timedelta(hours=horas))
                fin = (datetime.combine(inicio.date(), inicio.time()) + timedelta(minutes=50)).time()
                cita = Cita.objects.create(
                    paciente=paciente, psicologo=psicologo,
                    fecha=inicio.date(), hora_inicio=inicio.time(), hora_fin=fin,
                    modalidad=modalidad, estado='CONFIRMADA',
                    motivo_consulta=f"{MARCA} {texto}", costo=psicologo.tarifa_base,
                )
                if modalidad == 'VIRTUAL':
                    Teleconsulta.objects.get_or_create(
                        cita=cita, defaults={'sala_id': f"sigepsi-teleconsulta-{str(cita.id)[:8]}"}
                    )
                self.stdout.write(self.style.SUCCESS(
                    f"  [OK] Cita {modalidad} CONFIRMADA {inicio:%d/%m/%Y %H:%M} con {psicologo}"
                ))

        self.stdout.write(self.style.NOTICE(
            f"Inicie sesión como {opts['email']} (Paciente123*) en web o móvil para registrar el dispositivo; "
            "el Cron despachará los recordatorios en el siguiente ciclo."
        ))
