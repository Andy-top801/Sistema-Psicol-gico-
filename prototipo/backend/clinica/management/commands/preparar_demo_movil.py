"""
Prepara un paciente de demostración para la presentación móvil (CU11, CU12, CU13, CU17).

    python manage.py preparar_demo_movil                 # teleconsulta dentro de 5 min
    python manage.py preparar_demo_movil --tele-en 2     # teleconsulta dentro de 2 min

Es idempotente: cada ejecución borra y recrea los datos del paciente demo, con horas
relativas al momento actual (ejecutarlo justo antes de presentar).

Login móvil: paciente.demo@sigepsi.com / Demo1234*  (Centro Psicológico Esperanza)
"""
from datetime import datetime, timedelta, time

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django_tenants.utils import schema_context

TENANT = 'centro_esperanza'
EMAIL = 'paciente.demo@sigepsi.com'
PASSWORD = 'Demo1234*'


def _dia_habil(desde, dias_min):
    """Primer lunes-viernes a partir de hoy + dias_min."""
    d = desde + timedelta(days=dias_min)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


class Command(BaseCommand):
    help = 'Crea/reinicia el paciente demo con datos para CU11, CU12, CU13 y CU17 (app móvil).'

    def add_arguments(self, parser):
        parser.add_argument('--tele-en', type=int, default=5,
                            help='Minutos desde ahora para el inicio de la teleconsulta (default 5).')

    def handle(self, *args, **opts):
        with schema_context(TENANT), transaction.atomic():
            self._preparar(opts['tele_en'])

    def _preparar(self, tele_en):
        from accounts.models import Usuario, Rol
        from clinica.models import (Paciente, Psicologo, HistoriaClinica, TareaTerapeutica,
                                    EvidenciaTarea, RegistroAnimo)
        from agenda.models import Cita, NotificacionCita

        ahora = timezone.localtime()
        hoy = ahora.date()

        # ── Paciente demo ────────────────────────────────────────────────────
        usuario = Usuario.objects.filter(email=EMAIL).first()
        if not usuario:
            usuario = Usuario.objects.create_user(
                email=EMAIL, password=PASSWORD, nombre='Valeria', apellido='Rojas Demo',
                telefono='70000001', rol=Rol.objects.get(nombre=Rol.PACIENTE), activo=True)
        else:
            usuario.set_password(PASSWORD)
            usuario.activo = True
            usuario.save()
        psicologo = Psicologo.objects.select_related('usuario').get(usuario__email='carlos.mendoza@centroesperanza.com')
        paciente, _ = Paciente.objects.update_or_create(usuario=usuario, defaults={
            'codigo_expediente': 'EXP-DEMO-001', 'ci': '9990001-SC',
            'fecha_nacimiento': datetime(1998, 4, 12).date(), 'genero': 'F',
            'contacto_emergencia_nombre': 'Rosa Rojas (Madre)', 'contacto_emergencia_telf': '70000002',
            'psicologo_asignado': psicologo,
        })

        # Reinicio limpio (idempotente)
        Cita.objects.filter(paciente=paciente).delete()  # cascada: teleconsulta y notificaciones
        TareaTerapeutica.objects.filter(paciente=paciente).delete()
        RegistroAnimo.objects.filter(paciente=paciente).delete()
        historia, _ = HistoriaClinica.objects.get_or_create(paciente=paciente, defaults={
            'codigo_historia': 'HC-DEMO-001', 'psicologo_apertura': psicologo,
            'motivo_consulta_inicial': 'Ansiedad generalizada y dificultad para dormir.'})
        if historia.cerrada:
            historia.cerrada = False
            historia.save(update_fields=['cerrada'])

        def cita(fecha, hora, estado, modalidad='PRESENCIAL', motivo='Sesión de seguimiento', **extra):
            ini = datetime.combine(fecha, hora)
            fin = ini + timedelta(minutes=50)
            fin_t = fin.time() if fin.date() == fecha else time(23, 59)
            return Cita.objects.create(paciente=paciente, psicologo=psicologo, fecha=fecha,
                                       hora_inicio=hora, hora_fin=fin_t, modalidad=modalidad,
                                       estado=estado, motivo_consulta=motivo, costo=psicologo.tarifa_base, **extra)

        # ── CU13 / HU-44: teleconsulta dentro de la ventana (10 min antes … 45 min después)
        ini_tele = (ahora + timedelta(minutes=tele_en)).replace(second=0, microsecond=0)
        if ini_tele.date() != hoy:  # cerca de medianoche: dejarla en curso para no cruzar de día
            ini_tele = ahora.replace(second=0, microsecond=0)
        Cita.objects.filter(psicologo=psicologo, fecha=hoy, estado__in=['PROGRAMADA', 'CONFIRMADA'],
                            hora_inicio__lt=(datetime.combine(hoy, ini_tele.time()) + timedelta(minutes=50)).time(),
                            hora_fin__gt=ini_tele.time()).exclude(paciente=paciente).update(estado='CANCELADA',
                            motivo_cancelacion='Liberado para demo de teleconsulta')
        tele = cita(hoy, ini_tele.time(), 'CONFIRMADA', 'VIRTUAL', 'Teleconsulta: seguimiento de ansiedad')

        # ── CU11 / HU-41, HU-42: próximas (cancelables y no cancelables) + historial
        # mañana, una hora antes de la hora actual → siempre < 24 h → no cancelable desde la app
        no_cancelable = cita(hoy + timedelta(days=1), time(max(ahora.hour - 1, 0), 0),
                             'CONFIRMADA', 'PRESENCIAL', 'Control semanal')
        cancelable_1 = cita(_dia_habil(hoy, 4), time(10, 30), 'PROGRAMADA', 'PRESENCIAL', 'Terapia cognitivo-conductual')
        cancelable_2 = cita(_dia_habil(hoy, 8), time(15, 40), 'PROGRAMADA', 'VIRTUAL', 'Teleconsulta de seguimiento')
        realizada = cita(hoy - timedelta(days=7), time(10, 30), 'REALIZADA', 'PRESENCIAL', 'Primera sesión (evaluación)')
        cancelada = cita(hoy - timedelta(days=3), time(14, 50), 'CANCELADA', 'VIRTUAL', 'Sesión de seguimiento',
                         motivo_cancelacion='Viaje imprevisto por trabajo')
        cita(hoy - timedelta(days=14), time(8, 50), 'INASISTENCIA', 'PRESENCIAL', 'Sesión de seguimiento')

        # ── CU12 / HU-43: recordatorios push ya despachados (bandeja de notificaciones)
        def notif(c, tipo, titulo, cuerpo, hace_min, leida=False):
            env = ahora - timedelta(minutes=hace_min)
            NotificacionCita.objects.create(cita=c, tipo_evento=tipo, estado='ENVIADO', enviada=True,
                                            titulo=titulo, cuerpo=cuerpo, leida=leida,
                                            fecha_programada=env, fecha_envio=env)
        hhmm = lambda c: c.hora_inicio.strftime('%H:%M')
        notif(tele, 'RECORDATORIO_1H', 'Tu teleconsulta empieza pronto',
              f'Hoy a las {hhmm(tele)} con Lic. Carlos Mendoza. Entra a la sala desde Mis Citas.', 2)
        notif(no_cancelable, 'RECORDATORIO_24H', 'Recordatorio de cita',
              f'Tienes cita el {no_cancelable.fecha:%d/%m} a las {hhmm(no_cancelable)} (presencial).', 30)
        notif(cancelada, 'CANCELACION', 'Cita cancelada',
              f'Tu cita del {cancelada.fecha:%d/%m} fue cancelada. Motivo: viaje imprevisto.', 60 * 72, leida=True)
        notif(realizada, 'NUEVA_TAREA', 'Nueva tarea terapéutica',
              'Tu psicólogo te asignó "Registro de pensamientos automáticos".', 60 * 24 * 6, leida=True)

        # ── CU17 / HU-45: tareas en todos los estados
        def tarea(titulo, desc, cat, dias, estado='PENDIENTE'):
            return TareaTerapeutica.objects.create(historia_clinica=historia, psicologo=psicologo, paciente=paciente,
                                                   titulo=titulo, descripcion=desc, categoria=cat,
                                                   fecha_limite=hoy + timedelta(days=dias), estado=estado)
        tarea('Respiración diafragmática 4-7-8',
              'Practica 5 minutos antes de dormir: inhala 4 s, retén 7 s, exhala 8 s. Anota cómo te sentiste.',
              'MINDFULNESS', 3)
        tarea('Diario de gratitud', 'Escribe cada noche tres cosas por las que te sientes agradecida.', 'COGNITIVA', 0)
        hecha = tarea('Registro de pensamientos automáticos',
                      'Cuando sientas ansiedad, anota la situación, el pensamiento y la emoción (0-10).',
                      'AUTOREGISTRO', -4, 'COMPLETADA')
        EvidenciaTarea.objects.create(tarea=hecha, dificultad_percibida=3,
                                      texto_reflexion='Noté que la ansiedad aparece sobre todo antes de reuniones. '
                                                      'Escribirlo me ayudó a bajarla de 8 a 5.')
        tarea('Exposición gradual: llamada telefónica', 'Realiza una llamada corta que hayas estado evitando.',
              'CONDUCTUAL', -2)  # vencida → "Plazo vencido"

        # ── HU-46: historial de ánimo de la última semana (hoy queda libre para registrarlo en vivo)
        codigos = {1: 'MUY_BAJO', 2: 'BAJO', 3: 'NEUTRAL', 4: 'BUENO', 5: 'EXCELENTE'}
        for dias, valor in [(6, 2), (5, 3), (4, 3), (3, 2), (2, 4), (1, 4)]:
            RegistroAnimo.objects.create(paciente=paciente, fecha_registro=hoy - timedelta(days=dias),
                                         estado_animo=codigos[valor], escala_valor=valor)

        self.stdout.write(self.style.SUCCESS(
            f"Demo lista: {EMAIL} / {PASSWORD} ({TENANT})\n"
            f"  CU13 teleconsulta hoy {hhmm(tele)} (sala abierta hasta "
            f"{(datetime.combine(hoy, tele.hora_inicio) + timedelta(minutes=45)):%H:%M})\n"
            f"  CU11 cancelables: {cancelable_1.fecha:%d/%m} y {cancelable_2.fecha:%d/%m} | "
            f"no cancelable (<24 h): {no_cancelable.fecha:%d/%m}\n"
            f"  CU12 4 notificaciones (2 sin leer) | CU17 4 tareas + 6 días de ánimo"))
