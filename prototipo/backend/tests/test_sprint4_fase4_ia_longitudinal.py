# ==============================================================================
# TEST: tests/test_sprint4_fase4_ia_longitudinal.py
# FASE 4 (Sprint 4): HU-49 (Resumen Clínico IA + PII + Fallback + HITL + PDF),
#                    HU-50 (Motor Longitudinal de Riesgo 4 señales + anti-duplicado),
#                    HU-51 (Consola de Alertas Prioritarias + nota obligatoria)
# ==============================================================================
import os
import sys
from datetime import date, time, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from django.db import transaction
from django.utils import timezone
from django_tenants.utils import schema_context

from accounts.models import Usuario
from agenda.models import Cita
from clinica.models import (
    Paciente, Psicologo, HistoriaClinica, NotaSesion, DiagnosticoCIE,
    RegistroAnimo, TareaTerapeutica, AlertaRiesgoIA,
)
from clinica.ia_resumen_service import ResumenIAService, generar_resumen_ia_pdf, ETIQUETA_OBLIGATORIA
from clinica.ia_riesgo_service import RiesgoLongitudinalService


class _RollbackAfterTest(Exception):
    pass


def _run_rolled_back(schema_name, fn):
    with schema_context(schema_name):
        try:
            with transaction.atomic():
                fn()
                raise _RollbackAfterTest()
        except _RollbackAfterTest:
            pass


def test_hu49_resumen_longitudinal_pii_hitl_y_pdf():
    def _body():
        paciente = Paciente.objects.select_related('usuario').first()
        psicologo = Psicologo.objects.select_related('usuario').first()
        hc = HistoriaClinica.objects.filter(paciente=paciente).first()
        assert paciente and psicologo and hc

        # Insertar 2 notas SOAP con PII incrustado (CI, teléfono, email y nombre)
        NotaSesion.objects.create(
            historia_clinica=hc,
            psicologo=psicologo,
            numero_sesion=901,
            subjetivo=f"El paciente {paciente.usuario.nombre} con CI {paciente.ci} y correo {paciente.usuario.email} refiere ansiedad.",
            objetivo="Postura tensa, contacto 77123456.",
            analisis="Sintomatología ansiosa moderada en remisión parcial.",
            plan="Continuar reestructuración cognitiva.",
        )
        NotaSesion.objects.create(
            historia_clinica=hc,
            psicologo=psicologo,
            numero_sesion=902,
            subjetivo="Mejoría en calidad de sueño durante la semana.",
            objetivo="Afecto congruente y tranquilo.",
            analisis="Evolución favorable en manejo de estrés.",
            plan="Reforzar higiene del sueño.",
        )

        diag_antes = DiagnosticoCIE.objects.filter(historia_clinica=hc).count()
        resumen = ResumenIAService.generar_resumen(paciente=paciente, usuario=psicologo.usuario, usar_hf=False)

        assert resumen.estado == 'BORRADOR_IA'
        assert resumen.etiqueta_cumplimiento == ETIQUETA_OBLIGATORIA
        assert len(resumen.hash_sha256) == 64
        # PII sanitizado: no debe aparecer email ni CI en el texto
        if paciente.usuario.email:
            assert paciente.usuario.email not in resumen.texto_resumen
        if paciente.ci:
            assert paciente.ci not in resumen.texto_resumen
        # Nunca debe crear diagnósticos CIE automáticos
        assert DiagnosticoCIE.objects.filter(historia_clinica=hc).count() == diag_antes

        # Aprobación HITL
        aprobado = ResumenIAService.aprobar_hitl(
            resumen=resumen,
            usuario=psicologo.usuario,
            texto_editado=resumen.texto_resumen + '\nValidado por terapeuta tratante.',
        )
        assert aprobado.estado == 'APROBADO_HITL'
        assert aprobado.aprobado_por == psicologo.usuario
        assert aprobado.fecha_aprobacion is not None

        # Exportación PDF
        pdf_resp = generar_resumen_ia_pdf(aprobado, tenant_name='Centro Esperanza')
        assert pdf_resp.status_code == 200 and pdf_resp.content.startswith(b'%PDF')

    _run_rolled_back('centro_esperanza', _body)


def test_hu50_y_hu51_motor_riesgo_antiduplicado_y_consola_intervencion():
    def _body():
        paciente = Paciente.objects.select_related('usuario').last()
        psicologo = Psicologo.objects.select_related('usuario').first()
        hc = HistoriaClinica.objects.filter(paciente=paciente).first()
        admin_user = Usuario.objects.filter(activo=True).first()
        hoy = timezone.localdate()

        # Señal 1 + 2: 3 días consecutivos de ánimo <= 2 + léxico de riesgo vital
        RegistroAnimo.objects.filter(paciente=paciente).delete()
        for d in range(3):
            RegistroAnimo.objects.create(
                paciente=paciente,
                fecha_registro=hoy - timedelta(days=d),
                estado_animo='MUY_BAJO',
                escala_valor=1,
                nota_reflexiva='Me siento desesperado y no quiero vivir así.' if d == 0 else 'Día muy difícil.',
            )

        # Señal 3 + 4: 2 inasistencias consecutivas + 2 tareas vencidas
        for d in (1, 2):
            Cita.objects.create(
                paciente=paciente,
                psicologo=psicologo,
                fecha=hoy + timedelta(days=10 + d),
                hora_inicio=time(16, 0),
                hora_fin=time(17, 0),
                modalidad='PRESENCIAL',
                estado='INASISTENCIA',
            )
        if hc:
            for i in range(2):
                TareaTerapeutica.objects.create(
                    historia_clinica=hc,
                    psicologo=psicologo,
                    paciente=paciente,
                    titulo=f'Tarea vencida test {i}',
                    descripcion='Registro de pensamientos',
                    categoria='AUTOREGISTRO',
                    fecha_limite=hoy - timedelta(days=5),
                    estado='VENCIDA',
                )

        alertas_1 = RiesgoLongitudinalService.evaluar_paciente(paciente)
        tipos_1 = {a.tipo for a in alertas_1}
        assert 'RIESGO_VITAL' in tipos_1
        assert 'RIESGO_ABANDONO' in tipos_1

        alerta_vital = next(a for a in alertas_1 if a.tipo == 'RIESGO_VITAL')
        assert alerta_vital.severidad == 'CRITICO'
        assert alerta_vital.score_riesgo >= 80

        # HU-50 (c): Re-evaluar no debe duplicar alertas abiertas
        count_antes = AlertaRiesgoIA.objects.filter(paciente=paciente, estado='ABIERTA').count()
        RiesgoLongitudinalService.evaluar_paciente(paciente)
        count_despues = AlertaRiesgoIA.objects.filter(paciente=paciente, estado='ABIERTA').count()
        assert count_antes == count_despues

        # HU-51 (a): Consola priorizada pone CRITICO primero
        consola = list(RiesgoLongitudinalService.listar_consola_priorizada(estado='ABIERTA'))
        assert consola[0].severidad == 'CRITICO'

        # HU-51 (b): Bloquear resolución sin nota de intervención
        bloqueado = False
        try:
            RiesgoLongitudinalService.transicionar_alerta(alerta_vital, 'RESUELTA', '', admin_user)
        except ValueError:
            bloqueado = True
        assert bloqueado, 'Debió exigir nota de intervención para resolver la alerta'

        # HU-51 (c): Resolver con nota clínica audita y registra responsable
        resuelta = RiesgoLongitudinalService.transicionar_alerta(
            alerta_vital,
            'RESUELTA',
            'Se realizó llamada de contención inmediata y se coordinó sesión de urgencia con familia.',
            admin_user,
        )
        assert resuelta.estado == 'RESUELTA'
        assert resuelta.atendido_por == admin_user
        assert resuelta.fecha_resolucion is not None

    _run_rolled_back('centro_esperanza', _body)


def test_cu23_y_cu24_rutas_secuencia_api():
    from rest_framework.test import APIClient

    def _body():
        paciente = Paciente.objects.select_related('usuario').first()
        psicologo = Psicologo.objects.select_related('usuario').first()
        hc = HistoriaClinica.objects.filter(paciente=paciente).first()
        admin_user = psicologo.usuario
        assert paciente and hc and admin_user

        for num_ses in (905, 906):
            NotaSesion.objects.create(
                historia_clinica=hc,
                psicologo=psicologo,
                numero_sesion=num_ses,
                subjetivo='Seguimiento longitudinal CU23 de prueba clínica.',
                objetivo='Estabilidad psicomotriz observada en entrevista.',
                analisis='Progreso terapéutico favorable con adherencia parcial.',
                plan='Continuar sesiones quincenales y autorregistro.',
            )

        client = APIClient()
        client.force_authenticate(user=admin_user)

        # CU23: POST /api/v1/clinica/ia/resumen-longitudinal/
        r_cu23 = client.post(
            '/api/v1/clinica/ia/resumen-longitudinal/',
            {
                'paciente_id': str(paciente.id),
                'fecha_ini': '2024-01-01',
                'fecha_fin': date.today().isoformat(),
                'usar_hf': False,
            },
            format='json',
            HTTP_X_TENANT_SLUG='centro_esperanza',
        )
        assert r_cu23.status_code == 201, f"CU23 HTTP inesperado: {r_cu23.status_code} -> {r_cu23.content}"
        body23 = r_cu23.json()
        assert body23.get('resumen_id') and body23.get('hash_sha256') and body23.get('exportable_pdf') is False
        r_aprob = client.patch(
            f"/api/v1/clinica/resumenes-ia/{body23['resumen_id']}/aprobar/",
            {'texto_resumen': body23['borrador_ia'] + '\nAprobado HITL.'},
            format='json',
            HTTP_X_TENANT_SLUG='centro_esperanza',
        )
        assert r_aprob.status_code == 200 and r_aprob.json().get('exportable_pdf') is True

        # CU24: POST /api/v1/clinica/ml/evaluar-riesgo/
        r_cu24 = client.post(
            '/api/v1/clinica/ml/evaluar-riesgo/',
            {'paciente_id': str(paciente.id), 'ventana_meses': 3},
            format='json',
            HTTP_X_TENANT_SLUG='centro_esperanza',
        )
        assert r_cu24.status_code == 200, f"CU24 HTTP inesperado: {r_cu24.status_code} -> {r_cu24.content}"
        body24 = r_cu24.json()
        assert 'pacientes_evaluados' in body24 and 'resumen_cohorte' in body24

        if body24.get('alertas'):
            alerta_id = body24['alertas'][0]['id']
            assert 'indice_riesgo' in body24['alertas'][0]
            # CU24: PATCH intervenir requiere nota para RESUELTA
            r_bad = client.patch(
                f'/api/v1/clinica/ml/alertas/{alerta_id}/intervenir/',
                {'estado': 'RESUELTA', 'nota_intervencion': ''},
                format='json',
                HTTP_X_TENANT_SLUG='centro_esperanza',
            )
            assert r_bad.status_code == 400
            r_ok = client.patch(
                f'/api/v1/clinica/ml/alertas/{alerta_id}/intervenir/',
                {'estado': 'INTERVENIDA', 'nota_intervencion': 'Contención telefónica verificada CU24.'},
                format='json',
                HTTP_X_TENANT_SLUG='centro_esperanza',
            )
            assert r_ok.status_code == 200 and r_ok.json().get('estado') == 'RESUELTA'

    _run_rolled_back('centro_esperanza', _body)


if __name__ == '__main__':
    test_hu49_resumen_longitudinal_pii_hitl_y_pdf()
    print('[OK] HU-49: Resumen Clínico IA (PII sanitizado, Fallback, SHA-256, HITL y PDF)')
    test_hu50_y_hu51_motor_riesgo_antiduplicado_y_consola_intervencion()
    print('[OK] HU-50 & HU-51: Motor 4 señales, anti-duplicado, consola CRITICO primero y nota obligatoria')
    test_cu23_y_cu24_rutas_secuencia_api()
    print('[OK] CU23 & CU24 Endpoints de Secuencia (/ia/resumen-longitudinal/, /ml/evaluar-riesgo/, /intervenir/)')
    print('ALL SPRINT 4 FASE 4 TESTS PASSED [OK]')
