"""
CU25 / HU-38: datos para Reportes por Comando de Voz, en cada tenant.

Rellena huecos (idempotente: correrlo 2 veces no duplica) para que cualquier
comando de voz del SpeechParserService devuelva filas:
  "citas de <mes> del psicólogo <nombre> <estado> <modalidad>"
  "ingresos de <mes>", "teleconsultas de <mes>", "alertas ..."

Coherencia temporal respecto a HOY:
  pasado  -> REALIZADA / CANCELADA / INASISTENCIA
  futuro  -> PROGRAMADA / CONFIRMADA / CANCELADA
  VIRTUAL + REALIZADA -> Teleconsulta con duración real.

Uso:
  python manage.py seed_reportes_voz --tenant all
  python manage.py seed_reportes_voz --tenant bienestar_pleno --anio 2026
"""
import calendar
import random
import uuid
from datetime import date, datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_tenants.utils import get_tenant_model, schema_context

from agenda.models import Alerta, Cita, Teleconsulta
from clinica.models import Paciente, Psicologo

ESTADOS_PASADO = ["REALIZADA", "CANCELADA", "INASISTENCIA"]
ESTADOS_FUTURO = ["PROGRAMADA", "CONFIRMADA", "CANCELADA"]
MODALIDADES = ["PRESENCIAL", "VIRTUAL"]
HORAS = list(range(8, 18))  # bloques de 1h, 08:00 a 18:00

MOTIVOS = [
    "Ansiedad generalizada y preocupación persistente",
    "Episodio depresivo leve, desánimo y apatía",
    "Dificultades de pareja y comunicación",
    "Estrés laboral y agotamiento (burnout)",
    "Duelo por pérdida de un familiar",
    "Problemas de sueño e insomnio de conciliación",
    "Seguimiento de terapia cognitivo-conductual",
    "Ataques de pánico recurrentes",
    "Baja autoestima e inseguridad social",
    "Conflictos familiares con hijos adolescentes",
    "Control de seguimiento post-crisis",
    "Orientación vocacional y manejo de estrés académico",
]
MOTIVOS_CANCELACION = [
    "Paciente reprogramó por motivos laborales",
    "Paciente con cuadro gripal, solicitó cancelar",
    "Psicólogo con capacitación externa ese día",
    "Viaje imprevisto del paciente",
    "Problemas de conectividad reportados con anticipación",
]
ALERTAS = {
    "INASISTENCIA_REITERADA": "Paciente acumula inasistencias consecutivas sin justificación.",
    "RIESGO_DESERCION": "Disminución de adherencia: tareas terapéuticas sin completar y citas canceladas.",
    "URGENCIA_CLINICA": "Reporte de ideación de riesgo en preconsulta; requiere contacto prioritario.",
    "CRISIS_RETROCESO": "Retroceso sintomático tras evento estresante reciente.",
}
SEVERIDADES = ["BAJA", "MEDIA", "ALTA", "CRITICA"]


class Command(BaseCommand):
    help = "Siembra datos para Reportes por Comando de Voz (CU25/HU-38) en cada tenant, sin duplicar."

    def add_arguments(self, parser):
        parser.add_argument("--tenant", default="all", help='schema_name, slug o "all"')
        parser.add_argument("--anio", type=int, default=timezone.localdate().year)

    def handle(self, *args, **opts):
        qs = get_tenant_model().objects.exclude(schema_name="public").filter(activo=True)
        if opts["tenant"] != "all":
            qs = qs.filter(Q(schema_name=opts["tenant"]) | Q(slug=opts["tenant"]))
        tenants = list(qs.order_by("schema_name"))
        if not tenants:
            self.stderr.write(f"Tenant '{opts['tenant']}' no encontrado o inactivo.")
            return
        for t in tenants:
            with schema_context(t.schema_name), transaction.atomic():
                c, tc, a = self.sembrar(t.schema_name, opts["anio"])
            self.stdout.write(self.style.SUCCESS(
                f"{t.schema_name}: +{c} citas, +{tc} teleconsultas, +{a} alertas"))

    # ------------------------------------------------------------------
    def sembrar(self, schema, anio):
        rng = random.Random(f"{schema}-{anio}")  # distinto por tenant, reproducible
        hoy = timezone.localdate()
        psicologos = list(Psicologo.objects.select_related("usuario").filter(activo=True))
        pacientes = list(Paciente.objects.all())
        if not psicologos or not pacientes:
            self.stderr.write(f"  {schema}: sin psicólogos/pacientes, corre seed_sprint1 primero.")
            return 0, 0, 0

        # Ocupación existente para no solapar horarios (psicólogo y paciente)
        ocupado = set()
        existentes = set()
        for fecha, h, ps, pa, est, mod in Cita.objects.filter(fecha__year=anio).values_list(
                "fecha", "hora_inicio", "psicologo_id", "paciente_id", "estado", "modalidad"):
            ocupado.add((ps, fecha, h.hour))
            ocupado.add((pa, fecha, h.hour))
            existentes.add((ps, fecha.month, est, mod, fecha < hoy))

        nuevas_citas = nuevas_tele = 0
        for mes in range(1, 13):
            ultimo = calendar.monthrange(anio, mes)[1]
            habiles = [date(anio, mes, d) for d in range(1, ultimo + 1)
                       if date(anio, mes, d).weekday() < 6]  # lunes a sábado
            pasado = [d for d in habiles if d < hoy]
            futuro = [d for d in habiles if d > hoy]
            for psico in psicologos:
                for dias, estados, es_pasado in ((pasado, ESTADOS_PASADO, True),
                                                 (futuro, ESTADOS_FUTURO, False)):
                    if not dias:
                        continue
                    for estado in estados:
                        for mod in MODALIDADES:
                            if (psico.id, mes, estado, mod, es_pasado) in existentes:
                                continue
                            cita = self.crear_cita(rng, psico, pacientes, dias, estado, mod, ocupado)
                            if not cita:
                                continue
                            existentes.add((psico.id, mes, estado, mod, es_pasado))
                            nuevas_citas += 1
                            if mod == "VIRTUAL" and estado == "REALIZADA":
                                self.crear_teleconsulta(rng, schema, cita)
                                nuevas_tele += 1
        return nuevas_citas, nuevas_tele, self.sembrar_alertas(rng, anio, hoy, pacientes)

    def crear_cita(self, rng, psico, pacientes, dias, estado, mod, ocupado):
        for _ in range(40):  # intentos para hallar un hueco libre
            fecha, hora, pac = rng.choice(dias), rng.choice(HORAS), rng.choice(pacientes)
            if (psico.id, fecha, hora) in ocupado or (pac.id, fecha, hora) in ocupado:
                continue
            ocupado.add((psico.id, fecha, hora))
            ocupado.add((pac.id, fecha, hora))
            return Cita.objects.create(
                paciente=pac, psicologo=psico, fecha=fecha,
                hora_inicio=time(hora, 0), hora_fin=time(hora, 50),
                modalidad=mod, estado=estado, costo=psico.tarifa_base,
                motivo_consulta=rng.choice(MOTIVOS),
                motivo_cancelacion=rng.choice(MOTIVOS_CANCELACION) if estado == "CANCELADA" else "",
            )
        return None

    def crear_teleconsulta(self, rng, schema, cita):
        inicio = timezone.make_aware(datetime.combine(cita.fecha, cita.hora_inicio)) \
            + timedelta(minutes=rng.randint(0, 6))
        dur = rng.randint(38, 55) * 60
        Teleconsulta.objects.create(
            cita=cita, sala_id=f"sigepsi-{schema}-{uuid.uuid4().hex[:12]}",
            hora_inicio_real=inicio, hora_fin_real=inicio + timedelta(seconds=dur),
            duracion_segundos=dur, estado_sala="CANCELADA",  # sala cerrada al finalizar
        )

    def sembrar_alertas(self, rng, anio, hoy, pacientes):
        """Cubre tipo x severidad (16 combinaciones) en meses ya transcurridos."""
        ya = set(Alerta.objects.values_list("tipo", "severidad"))
        meses = [m for m in range(1, 13) if date(anio, m, 1) <= hoy] or [1]
        n = 0
        for tipo, desc in ALERTAS.items():
            for sev in SEVERIDADES:
                if (tipo, sev) in ya:
                    continue
                mes = rng.choice(meses)
                tope = hoy.day if (anio, mes) == (hoy.year, hoy.month) else 28
                creada = timezone.make_aware(datetime(
                    anio, mes, rng.randint(1, tope), rng.randint(8, 17), rng.randint(0, 59)))
                # BAJA/MEDIA resueltas; ALTA/CRITICA mayormente abiertas
                resuelta = sev in ("BAJA", "MEDIA") or rng.random() < 0.4
                a = Alerta.objects.create(paciente=rng.choice(pacientes), tipo=tipo, severidad=sev,
                                          descripcion=desc, resuelta=resuelta)
                campos = {"fecha_creacion": creada}
                if resuelta:
                    campos["fecha_resolucion"] = min(creada + timedelta(days=rng.randint(1, 6)), timezone.now())
                    campos["nota_resolucion"] = "Contacto realizado y plan de seguimiento acordado con el paciente."
                Alerta.objects.filter(pk=a.pk).update(**campos)  # auto_now_add ignora el valor en create
                n += 1
        return n
