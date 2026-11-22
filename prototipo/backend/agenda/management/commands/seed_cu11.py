# -*- coding: utf-8 -*-
# Datos de demostración CU11 Móvil (HU-41 / HU-42), relativos a la hora actual:
#   - VIRTUAL CONFIRMADA que empieza en ~5 min  → tarjeta resaltada + 'Entrar a Teleconsulta' (HU-41 c)
#   - PRESENCIAL CONFIRMADA en ~10 h (< 24 h)  → cancelación bloqueada + WhatsApp (HU-42 b)
#   - VIRTUAL PROGRAMADA en ~3 días (> 24 h)   → etiqueta PENDIENTE, cancelación permitida (HU-42 a)
#     python manage.py seed_cu11
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_tenants.utils import schema_context

MARCA = "[DEMO CU11]"


def _slot(dt):
    dt = dt.replace(second=0, microsecond=0, minute=(dt.minute // 5) * 5)
    if dt.hour == 23 and dt.minute > 5:
        dt = dt.replace(minute=5)
    return dt


class Command(BaseCommand):
    help = "Crea citas de demostración para CU11 Móvil (consulta y cancelación con política > 24 h)."

    def add_arguments(self, parser):
        parser.add_argument('--tenant', default='centro_esperanza')
        parser.add_argument('--email', default='juan.perez@paciente.com')

    def handle(self, *args, **opts):
        with schema_context(opts['tenant']):
            from clinica.models import Paciente, Psicologo
            from agenda.models import Cita, Teleconsulta

            paciente = Paciente.objects.get(usuario__email=opts['email'])
            psicologos = list(Psicologo.objects.select_related('usuario').filter(activo=True)[:3])
            Cita.objects.filter(paciente=paciente, motivo_consulta__startswith=MARCA).delete()

            ahora = timezone.localtime()
            casos = [
                (timedelta(minutes=5), 'VIRTUAL', 'CONFIRMADA', 'Sesión de seguimiento semanal'),
                (timedelta(hours=10), 'PRESENCIAL', 'CONFIRMADA', 'Evaluación de avances'),
                (timedelta(days=3), 'VIRTUAL', 'PROGRAMADA', 'Terapia cognitivo-conductual'),
            ]
            for i, (delta, modalidad, estado, texto) in enumerate(casos):
                inicio = ahora + delta
                inicio = inicio.replace(second=0, microsecond=0) if i == 0 else _slot(inicio)
                fin = (datetime.combine(inicio.date(), inicio.time()) + timedelta(minutes=50)).time()
                psico = psicologos[i % len(psicologos)]
                cita = Cita.objects.create(
                    paciente=paciente, psicologo=psico, fecha=inicio.date(),
                    hora_inicio=inicio.time(), hora_fin=fin, modalidad=modalidad, estado=estado,
                    motivo_consulta=f"{MARCA} {texto}", costo=psico.tarifa_base,
                )
                if modalidad == 'VIRTUAL':
                    Teleconsulta.objects.create(cita=cita, sala_id=f"sigepsi-teleconsulta-{str(cita.id)[:8]}")
                self.stdout.write(self.style.SUCCESS(
                    f"  [OK] {modalidad} {estado} {inicio:%d/%m %H:%M} con {psico.usuario.nombre}"))
        self.stdout.write(self.style.NOTICE(
            f"Inicie sesión en la app móvil como {opts['email']} (Paciente123*) y abra Mis Citas."))
