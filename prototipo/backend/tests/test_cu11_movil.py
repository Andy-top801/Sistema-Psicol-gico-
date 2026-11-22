# -*- coding: utf-8 -*-
# CU11 Móvil — HU-41 (consulta de citas) y HU-42 (cancelación con política > 24 h).
# Verifica el Diagrama de Secuencia "Secuencia_Corregido_CU11_Citas_Movil" vía API real.
#   python tests/test_cu11_movil.py
import sys, os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from django.utils import timezone
from django_tenants.utils import schema_context
from rest_framework.test import APIClient

TENANT = 'centro_esperanza'
MARCA = '[TEST CU11]'


def _cita(Cita, Teleconsulta, paciente, psicologo, horas, estado='CONFIRMADA', modalidad='VIRTUAL'):
    inicio = (timezone.localtime() + timedelta(hours=horas)).replace(second=0, microsecond=0)
    if inicio.hour == 23:
        inicio = inicio.replace(minute=0)
    fin = (datetime.combine(inicio.date(), inicio.time()) + timedelta(minutes=50)).time()
    c = Cita.objects.create(paciente=paciente, psicologo=psicologo, fecha=inicio.date(),
                            hora_inicio=inicio.time(), hora_fin=fin, modalidad=modalidad,
                            estado=estado, motivo_consulta=MARCA)
    if modalidad == 'VIRTUAL':
        Teleconsulta.objects.create(cita=c, sala_id=f"test-cu11-{str(c.id)[:8]}")
    return c


def test_cu11_movil():
    with schema_context(TENANT):
        from accounts.models import Usuario
        from clinica.models import Paciente, Psicologo
        from agenda.models import Cita, Teleconsulta, NotificacionCita
        from agenda.services.notifications import FCMNotificationController

        paciente = Paciente.objects.select_related('usuario').get(usuario__email='juan.perez@paciente.com')
        otro = Paciente.objects.exclude(id=paciente.id).first()
        psicologo = Psicologo.objects.first()
        staff = Usuario.objects.get(email='admin@centroesperanza.com')
        Cita.objects.filter(motivo_consulta=MARCA).delete()

        c_ok = _cita(Cita, Teleconsulta, paciente, psicologo, 30)                     # > 24 h, virtual
        c_tarde = _cita(Cita, Teleconsulta, paciente, psicologo, 10, modalidad='PRESENCIAL')  # < 24 h
        c_ahora = _cita(Cita, Teleconsulta, paciente, psicologo, 5 / 60)               # virtual en 5 min
        c_pend = _cita(Cita, Teleconsulta, paciente, psicologo, 48, estado='PROGRAMADA', modalidad='PRESENCIAL')
        c_ajena = _cita(Cita, Teleconsulta, otro, psicologo, 40)

    api = APIClient(HTTP_X_TENANT_ID=TENANT)
    try:
        api.force_authenticate(user=paciente.usuario)

        # ── HU-41 ────────────────────────────────────────────────────────────
        r = api.get('/api/v1/citas/mis-citas/')
        assert r.status_code == 200, r.content
        d = r.json()
        prox = [c for c in d['proximas'] if c['motivo_consulta'] == MARCA]
        ids = [c['id'] for c in prox]
        assert str(c_ajena.id) not in ids, "Solo debe listar citas propias"
        # (a) orden cronológico ascendente
        claves = [(c['fecha'], c['hora_inicio']) for c in d['proximas']]
        assert claves == sorted(claves)
        por_id = {c['id']: c for c in prox}
        assert por_id[str(c_pend.id)]['estado_etiqueta'] == 'PENDIENTE'
        assert por_id[str(c_tarde.id)]['consultorio'], "Presencial debe mostrar consultorio"
        assert por_id[str(c_ok.id)]['enlace_virtual'], "Virtual debe mostrar enlace"
        # (c) teleconsulta habilitada solo si es virtual y faltan <= 10 min
        assert por_id[str(c_ahora.id)]['puede_entrar_teleconsulta'] is True
        assert por_id[str(c_ok.id)]['puede_entrar_teleconsulta'] is False
        assert por_id[str(c_tarde.id)]['puede_entrar_teleconsulta'] is False
        # HU-42 (b): el servidor indica qué citas ya no se pueden cancelar
        assert por_id[str(c_ok.id)]['puede_cancelar'] is True
        assert por_id[str(c_tarde.id)]['puede_cancelar'] is False
        assert d['whatsapp_recepcion'], "Debe exponer el WhatsApp de recepción"

        # ── HU-42 rama else: < 24 h → Msg 18 (400) y la cita NO cambia ──────
        r = api.post(f'/api/v1/citas/{c_tarde.id}/cancelar/',
                     {'motivo': 'Imprevisto laboral', 'fecha_cliente': '2020-01-01T00:00:00'}, format='json')
        assert r.status_code == 400, r.content
        assert r.json()['error'] == 'Plazo expirado: cancelaciones requieren > 24h'
        assert r.json()['codigo'] == 'CANCELLATION_WINDOW_EXPIRED'
        with schema_context(TENANT):
            c_tarde.refresh_from_db()
            assert c_tarde.estado == 'CONFIRMADA', "(c) la hora del cliente no debe influir"
            assert not NotificacionCita.objects.filter(cita=c_tarde, tipo_evento='CANCELACION').exists()

        # Motivo obligatorio
        r = api.post(f'/api/v1/citas/{c_ok.id}/cancelar/', {'motivo': 'x'}, format='json')
        assert r.status_code == 400 and r.json()['codigo'] == 'MOTIVO_INVALIDO'

        # No puede cancelar citas ajenas
        r = api.post(f'/api/v1/citas/{c_ajena.id}/cancelar/', {'motivo': 'Intento ajeno'}, format='json')
        assert r.status_code == 404

        # ── HU-42 rama alt: > 24 h → Msg 6..16 ───────────────────────────────
        r = api.post(f'/api/v1/citas/{c_ok.id}/cancelar/', {'motivo': 'Viaje imprevisto'}, format='json')
        assert r.status_code == 200, r.content
        body = r.json()
        assert body['mensaje'] == 'Cita cancelada y bloque liberado'
        assert body['cita_liberada'] is True and body['sala'] == 'CANCELADA'
        with schema_context(TENANT):
            c_ok.refresh_from_db()
            assert c_ok.estado == 'CANCELADA' and c_ok.motivo_cancelacion == 'Viaje imprevisto'   # Msg 6-7
            assert c_ok.teleconsulta.estado_sala == 'CANCELADA'                                 # Msg 10-11
            n = NotificacionCita.objects.get(cita=c_ok, tipo_evento='CANCELACION')               # Msg 12-13
            assert n.estado == 'PENDIENTE'
            # (a) "notifica por FCM": el Cron de CU12 la despacha
            from clinica.models import TokenFCM
            TokenFCM.objects.get_or_create(paciente=paciente, token='sandbox-test-cu11',
                                           defaults={'plataforma': 'ANDROID'})
            FCMNotificationController.ejecutar_despacho_recordatorios()
            n.refresh_from_db()
            assert n.estado == 'ENVIADO' and n.titulo == 'Cita Cancelada', (n.estado, n.error_log)

        # Ya cancelada → no se puede volver a cancelar
        r = api.post(f'/api/v1/citas/{c_ok.id}/cancelar/', {'motivo': 'Otra vez'}, format='json')
        assert r.status_code == 400 and r.json()['codigo'] == 'ESTADO_NO_CANCELABLE'

        # Personal del centro: puede cancelar aun con < 24 h (la política es del paciente)
        api.force_authenticate(user=staff)
        r = api.post(f'/api/v1/citas/{c_tarde.id}/cancelar/', {'motivo': 'Psicólogo enfermo'}, format='json')
        assert r.status_code == 200, r.content

        # Un usuario no paciente no tiene "mis citas"
        assert api.get('/api/v1/citas/mis-citas/').status_code == 403
    finally:
        with schema_context(TENANT):
            from agenda.models import Cita
            from clinica.models import TokenFCM
            Cita.objects.filter(motivo_consulta=MARCA).delete()
            TokenFCM.objects.filter(token='sandbox-test-cu11').delete()


if __name__ == "__main__":
    test_cu11_movil()
    print("CU11 Móvil (HU-41 / HU-42): TODAS LAS PRUEBAS PASARON [OK]")
