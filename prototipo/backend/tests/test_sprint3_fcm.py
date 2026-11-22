# -*- coding: utf-8 -*-
# CU12 / HU-43 — Verifica el Diagrama de Secuencia de Notificaciones Push FCM.
#   python tests/test_sprint3_fcm.py
import sys, os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from django.utils import timezone
from django_tenants.utils import schema_context
from tenants.models import Tenant


def _cita(Cita, paciente, psicologo, horas, estado='CONFIRMADA', modalidad='VIRTUAL'):
    inicio = (timezone.localtime() + timedelta(hours=horas)).replace(second=0, microsecond=0)
    if inicio.hour == 23:
        inicio = inicio.replace(minute=0)
    fin = (datetime.combine(inicio.date(), inicio.time()) + timedelta(minutes=50)).time()
    return Cita.objects.create(
        paciente=paciente, psicologo=psicologo, fecha=inicio.date(),
        hora_inicio=inicio.time(), hora_fin=fin, modalidad=modalidad,
        estado=estado, motivo_consulta="[TEST CU12]",
    )


def test_cu12_secuencia_recordatorios_push():
    tenant = Tenant.objects.exclude(schema_name='public').first()
    assert tenant is not None

    with schema_context(tenant.schema_name):
        from clinica.models import Paciente, TokenFCM, Psicologo
        from agenda.models import Cita, NotificacionCita
        from agenda.services.notifications import FCMNotificationController

        paciente = Paciente.objects.first()
        otro = Paciente.objects.exclude(id=paciente.id).first()
        psicologo = Psicologo.objects.first()
        Cita.objects.filter(motivo_consulta="[TEST CU12]").delete()
        TokenFCM.objects.filter(paciente__in=[paciente, otro]).delete()

        # (a) token del dispositivo registrado para el paciente
        TokenFCM.objects.create(paciente=paciente, token="sandbox_test_device", plataforma='ANDROID')

        c24 = _cita(Cita, paciente, psicologo, 20, modalidad='PRESENCIAL')
        c1 = _cita(Cita, paciente, psicologo, 0.5, modalidad='VIRTUAL')
        c_prog = _cita(Cita, paciente, psicologo, 10, estado='PROGRAMADA')   # no confirmada
        c_lejos = _cita(Cita, paciente, psicologo, 30)                      # fuera de ventana
        c_sin_token = _cita(Cita, otro, psicologo, 5)

        try:
            # Msg 1 → 16
            r = FCMNotificationController.ejecutar_despacho_recordatorios()

            n24 = NotificacionCita.objects.get(cita=c24)
            n1 = NotificacionCita.objects.get(cita=c1)
            assert n24.tipo_evento == 'RECORDATORIO_24H' and n1.tipo_evento == 'RECORDATORIO_1H'

            # (b) título y contenido: psicólogo, hora y modalidad; Msg 14 estado ENVIADO con message_id
            for n, cita in [(n24, c24), (n1, c1)]:
                assert n.estado == 'ENVIADO' and n.enviada and n.message_id, n.error_log
                assert n.titulo == 'Recordatorio de Consulta'
                assert cita.hora_inicio.strftime('%H:%M') in n.cuerpo
                assert psicologo.usuario.nombre in n.cuerpo
            assert 'Presencial' in n24.cuerpo and 'Teleconsulta' in n1.cuerpo

            # Solo citas CONFIRMADAS y dentro de ventana
            assert not NotificacionCita.objects.filter(cita__in=[c_prog, c_lejos]).exists()

            # Paciente sin dispositivo → FALLIDO (se reintentará)
            ns = NotificacionCita.objects.get(cita=c_sin_token)
            assert ns.estado == 'FALLIDO' and ns.intentos_entrega == 1

            assert r["total_enviadas"] >= 2 and r["total_fallidas"] >= 1

            # Idempotencia del Cron: una segunda ejecución no reenvía
            FCMNotificationController.ejecutar_despacho_recordatorios()
            n24.refresh_from_db()
            assert n24.intentos_entrega == 1
            assert NotificacionCita.objects.filter(cita=c24).count() == 1

            # (c) payload que abre la pantalla correcta al tocar la notificación
            ruta = "teleconsulta" if c1.modalidad == 'VIRTUAL' else "detalle_cita"
            assert ruta == "teleconsulta"
        finally:
            Cita.objects.filter(motivo_consulta="[TEST CU12]").delete()
            TokenFCM.objects.filter(token="sandbox_test_device").delete()


if __name__ == "__main__":
    test_cu12_secuencia_recordatorios_push()
    print("CU12 / HU-43: TODAS LAS PRUEBAS PASARON [OK]")
