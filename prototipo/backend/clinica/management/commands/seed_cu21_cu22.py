# -*- coding: utf-8 -*-
# CU21 / CU22 (HU-47, HU-48) — datos de demostración para la Consola de Triaje IA.
#   python manage.py seed_cu21_cu22 [--tenant centro_esperanza]
# Idempotente: los intakes de demo llevan la marca [SEED CU21-22] y se recrean en cada ejecución.
# 1) Crea 3 intakes de demo (crisis, pareja, duelo) en pacientes sin psicólogo asignado.
# 2) Clasifica con IA todos los intakes del tenant que aún no tienen clasificación.
# 3) Ajusta cupos para que el ranking muestre un psicólogo con cupo completo.
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

MARCA = '[SEED CU21-22]'
CASOS = [
    ('Ya no aguanto más. Siento que mi familia estaría mejor sin mí y he pensado en quitarme la vida.', 5, 'VIRTUAL'),
    ('Con mi pareja discutimos todos los días, ya no nos comunicamos y estamos pensando en separarnos.', 3, 'PRESENCIAL'),
    ('Mi madre falleció hace dos meses y no logro aceptar su muerte, lloro todas las noches.', 4, 'MIXTA'),
]


class Command(BaseCommand):
    help = "Datos de demostración CU21/CU22: intakes clasificados con IA y cupos de psicólogos."

    def add_arguments(self, parser):
        parser.add_argument('--tenant', default='centro_esperanza')

    def handle(self, *args, **opts):
        from clinica.models import (Paciente, Psicologo, FormularioPreConsulta, RespuestaPreConsulta,
                                    ClasificacionIA)
        from clinica.views import CTR_ClasificacionIAController

        with schema_context(opts['tenant']):
            form = FormularioPreConsulta.objects.filter(activo=True).first() or FormularioPreConsulta.objects.first()
            if not form:
                raise CommandError("No hay formularios de preconsulta; ejecute seed_sprint2 primero.")

            RespuestaPreConsulta.objects.filter(antecedentes_medicos=MARCA).delete()
            pacientes = list(Paciente.objects.filter(psicologo_asignado__isnull=True)
                             .select_related('usuario').order_by('codigo_expediente')[:len(CASOS)])
            if len(pacientes) < len(CASOS):
                self.stdout.write(self.style.WARNING("Hay menos pacientes sin asignar que casos de demo."))
            for pac, (motivo, malestar, modalidad) in zip(pacientes, CASOS):
                pac.modalidad_preferencia = modalidad
                pac.save(update_fields=['modalidad_preferencia'])
                RespuestaPreConsulta.objects.create(
                    formulario=form, paciente=pac, motivo_consulta=motivo,
                    nivel_urgencia_percibido=malestar, antecedentes_medicos=MARCA)

            # Cupos: el primer psicólogo activo queda con cupo completo para demostrar HU-48 (b)
            psicologos = list(Psicologo.objects.filter(activo=True).order_by('numero_colegiado'))
            for i, p in enumerate(psicologos):
                p.cupo_maximo = 20
                asignados = p.pacientes_asignados.count()
                p.carga_actual = 20 if i == 0 else max(asignados, (i * 4) % 15)
                p.save(update_fields=['cupo_maximo', 'carga_actual'])

            pendientes = (RespuestaPreConsulta.objects.filter(clasificaciones_ia__isnull=True)
                          .select_related('paciente__usuario'))
            total = crisis = 0
            for resp in pendientes:
                payload, _ = CTR_ClasificacionIAController.clasificar(resp, ip='127.0.0.1')
                total += 1
                crisis += payload['alerta_crisis']
                c = payload['clasificacion']
                self.stdout.write(f"  {resp.paciente.codigo_expediente}: {c['categoria_principal']} "
                                  f"{c['nivel_severidad']} crisis={payload['alerta_crisis']} ({c['modelo_ia']})")

            self.stdout.write(self.style.SUCCESS(
                f"Clasificados {total} intake(s), {crisis} con ALERTA_CRISIS. "
                f"Psicólogos con cupo ajustado: {len(psicologos)}."))
