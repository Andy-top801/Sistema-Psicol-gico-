# -*- coding: utf-8 -*-
import sys, os
from datetime import datetime, date, time, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from django.utils import timezone
from django_tenants.utils import schema_context
from rest_framework.test import APIRequestFactory, force_authenticate
from tenants.models import Tenant
from clinica.models import Paciente, Psicologo
from agenda.models import Cita
from agenda.views import CitaViewSet

def test_mis_citas_and_cancellation_policy_24h():
    tenant = Tenant.objects.exclude(schema_name='public').first()
    assert tenant is not None

    with schema_context(tenant.schema_name):
        factory = APIRequestFactory()
        paciente = Paciente.objects.select_related('usuario', 'historia_clinica').first()
        if hasattr(paciente, 'historia_clinica') and paciente.historia_clinica:
            paciente.historia_clinica.cerrada = False
            paciente.historia_clinica.save(update_fields=['cerrada'])
        psicologo = Psicologo.objects.select_related('usuario').first()
        usuario_paciente = paciente.usuario

        # 1. Crear 2 citas de prueba:
        # Cita A: En 48 horas (Cancelable oportunamente > 24h)
        fecha_a = (timezone.now() + timedelta(days=2)).date()
        cita_a = Cita.objects.create(
            paciente=paciente,
            psicologo=psicologo,
            fecha=fecha_a,
            hora_inicio=time(14, 0),
            hora_fin=time(15, 0),
            modalidad='PRESENCIAL',
            estado='PROGRAMADA',
            motivo_consulta="Evaluación inicial"
        )

        # Cita B: En 4 horas (Bloqueada para cancelación <= 24h)
        fecha_b = (timezone.now() + timedelta(hours=4)).date()
        hora_b_ini = (timezone.now() + timedelta(hours=4)).time()
        hora_b_fin = (timezone.now() + timedelta(hours=5)).time()
        # Asegurar hora_fin > hora_inicio para evitar restricción chk_cita_rango_horario
        if hora_b_fin <= hora_b_ini:
            hora_b_ini = time(10, 0)
            hora_b_fin = time(11, 0)
            fecha_b = timezone.now().date()

        cita_b = Cita.objects.create(
            paciente=paciente,
            psicologo=psicologo,
            fecha=fecha_b,
            hora_inicio=hora_b_ini,
            hora_fin=hora_b_fin,
            modalidad='VIRTUAL',
            estado='CONFIRMADA',
            motivo_consulta="Sesión urgente"
        )

        # Probar endpoint mis-citas (HU-41 / CP-M03)
        view_mis_citas = CitaViewSet.as_view({'get': 'mis_citas'})
        req_mis_citas = factory.get(f'/api/agenda/citas/mis-citas/?paciente_id={paciente.id}')
        force_authenticate(req_mis_citas, user=usuario_paciente)
        resp_mis_citas = view_mis_citas(req_mis_citas)

        assert resp_mis_citas.status_code == 200
        data_citas = resp_mis_citas.data
        assert 'proximas' in data_citas
        assert 'historial' in data_citas
        assert len(data_citas['proximas']) >= 2

        # Probar cancelación oportuna con > 24h (HU-42 / CP-M04)
        view_cancelar = CitaViewSet.as_view({'post': 'cancelar'})
        req_cancel_ok = factory.post(
            f'/api/agenda/citas/{cita_a.id}/cancelar/',
            {'motivo': 'Tengo un compromiso laboral imprevisto pero aviso con 48h de anticipación.'},
            format='json'
        )
        force_authenticate(req_cancel_ok, user=usuario_paciente)
        resp_cancel_ok = view_cancelar(req_cancel_ok, pk=str(cita_a.id))

        assert resp_cancel_ok.status_code == 200, f"Error en cancel_ok: {resp_cancel_ok.data}"
        cita_a.refresh_from_db()
        assert cita_a.estado == 'CANCELADA'
        assert "compromiso laboral" in cita_a.motivo_cancelacion

        # Probar bloqueo de cancelación tardía <= 24h (HU-42 / CP-M05)
        req_cancel_bloq = factory.post(
            f'/api/agenda/citas/{cita_b.id}/cancelar/',
            {'motivo': 'Quiero cancelar faltando pocas horas.'},
            format='json'
        )
        force_authenticate(req_cancel_bloq, user=usuario_paciente)
        resp_cancel_bloq = view_cancelar(req_cancel_bloq, pk=str(cita_b.id))

        assert resp_cancel_bloq.status_code == 400, "Debe rechazar cancelación con menos de 24h"
        # Verificar que el error señale la política de 24 horas
        err_str = str(resp_cancel_bloq.data).lower()
        assert "24 horas" in err_str or "cancellation_window_expired" in err_str

        # Limpiar
        cita_a.delete()
        cita_b.delete()

if __name__ == "__main__":
    test_mis_citas_and_cancellation_policy_24h()
    print("ALL CANCELLATION POLICY TESTS PASSED [OK]")
