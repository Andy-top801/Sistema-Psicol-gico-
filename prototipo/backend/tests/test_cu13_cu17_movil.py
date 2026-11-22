# -*- coding: utf-8 -*-
# CU13 Móvil (HU-44) — Sala de teleconsulta Jitsi: ventana 10 min antes / 45 min después.
# CU17 Móvil (HU-45, HU-46) — Entrega de tarea + registro de ánimo.
# Verifica los Diagramas de Secuencia vía API real.
#   python tests/test_cu13_cu17_movil.py
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
MARCA = '[TEST CU13-CU17]'


def _cita(Cita, paciente, psicologo, minutos, estado='CONFIRMADA'):
    inicio = (timezone.localtime() + timedelta(minutes=minutos)).replace(second=0, microsecond=0)
    fin_dt = datetime.combine(inicio.date(), inicio.time()) + timedelta(minutes=50)
    fin = fin_dt.time() if fin_dt.date() == inicio.date() else datetime.max.time().replace(microsecond=0)
    return Cita.objects.create(paciente=paciente, psicologo=psicologo, fecha=inicio.date(),
                               hora_inicio=inicio.time(), hora_fin=fin, modalidad='VIRTUAL',
                               estado=estado, motivo_consulta=MARCA)


def test_cu13_cu17_movil():
    with schema_context(TENANT):
        from clinica.models import Paciente, Psicologo, TareaTerapeutica, RegistroAnimo, HistoriaClinica
        from agenda.models import Cita

        paciente = Paciente.objects.select_related('usuario').get(usuario__email='juan.perez@paciente.com')
        psicologo = Psicologo.objects.first()
        historia, _ = HistoriaClinica.objects.get_or_create(paciente=paciente, defaults={
            'codigo_historia': 'HC-TEST-CU17', 'psicologo_apertura': psicologo, 'motivo_consulta_inicial': MARCA})
        if historia.cerrada:
            historia.cerrada = False
            historia.save(update_fields=['cerrada'])
        Cita.objects.filter(motivo_consulta=MARCA).delete()
        TareaTerapeutica.objects.filter(titulo__startswith=MARCA).delete()

        api = APIClient(HTTP_X_TENANT_ID=TENANT)
        api.force_authenticate(paciente.usuario)
        try:
            # ── CU13: ventana de acceso (HU-44 a) ──────────────────────────────
            casos = [(5, 200), (-40, 200), (30, 403), (-50, 403)]  # minutos desde ahora → esperado
            for minutos, esperado in casos:
                c = _cita(Cita, paciente, psicologo, minutos)
                if c.fecha != timezone.localdate():  # cerca de medianoche: no aplica
                    continue
                r = api.post(f'/api/agenda/teleconsulta/{c.id}/unirse/')
                assert r.status_code == esperado, f"cita a {minutos} min → {r.status_code} {r.data}"
                if esperado == 200:
                    for k in ('jitsi_jwt', 'room_name', 'server_url'):
                        assert r.data.get(k), f"falta {k} en respuesta 200"
                    assert r.data['es_moderador'] is False, "el paciente entra como invitado"
                else:
                    assert r.data['codigo'] == 'OUTSIDE_TELECONSULTA_WINDOW'

            cancelada = _cita(Cita, paciente, psicologo, 0, estado='CANCELADA')
            r = api.post(f'/api/agenda/teleconsulta/{cancelada.id}/unirse/')
            assert r.status_code == 400 and r.data['codigo'] == 'SESSION_CLOSED'

            # ── CU17: entrega de tarea (HU-45) + ánimo (HU-46) ─────────────────
            def tarea(dias):
                return TareaTerapeutica.objects.create(
                    historia_clinica=historia, psicologo=psicologo, paciente=paciente,
                    titulo=f"{MARCA} Respiración diafragmática", descripcion="5 min diarios.",
                    categoria='MINDFULNESS', fecha_limite=timezone.localdate() + timedelta(days=dias))

            t = tarea(2)
            r = api.get('/api/clinica/tareas/')
            fila = next(x for x in (r.data if isinstance(r.data, list) else r.data['results']) if x['id'] == str(t.id))
            assert fila['estado'] == 'PENDIENTE' and fila['fecha_limite']  # HU-45 a

            r = api.post(f'/api/clinica/tareas/{t.id}/entregar/', {'texto_reflexion': '', 'dificultad_percibida': 2},
                         format='json')
            assert r.status_code == 400, "la reflexión es obligatoria"
            r = api.post(f'/api/clinica/tareas/{t.id}/entregar/', {'texto_reflexion': 'x', 'dificultad_percibida': 9},
                         format='json')
            assert r.status_code == 400, "dificultad fuera de 1-5"

            r = api.post(f'/api/clinica/tareas/{t.id}/entregar/',
                         {'texto_reflexion': 'Me ayudó a dormir mejor.', 'dificultad_percibida': 2, 'escala_animo': 4},
                         format='json')
            assert r.status_code == 200, r.data
            assert r.data['mensaje'] == 'Tarea entregada y ánimo registrado'
            t.refresh_from_db()
            assert t.estado == 'COMPLETADA' and t.evidencia.dificultad_percibida == 2
            assert RegistroAnimo.objects.get(paciente=paciente, fecha_registro=timezone.localdate()).escala_valor == 4

            r = api.post(f'/api/clinica/tareas/{t.id}/entregar/', {'texto_reflexion': 'otra', 'dificultad_percibida': 1},
                         format='json')
            assert r.status_code == 400, "HU-45 c: edición bloqueada tras entregar"

            vencida = tarea(-1)
            r = api.post(f'/api/clinica/tareas/{vencida.id}/entregar/', {'texto_reflexion': 'tarde', 'dificultad_percibida': 3},
                         format='json')
            assert r.status_code == 400 and r.data['codigo'] == 'PLAZO_EXPIRADO'
            vencida.refresh_from_db()
            assert vencida.estado == 'PENDIENTE', "una entrega rechazada no cambia el estado"
            print("OK CU13 + CU17 móvil")
        finally:
            Cita.objects.filter(motivo_consulta=MARCA).delete()
            TareaTerapeutica.objects.filter(titulo__startswith=MARCA).delete()


if __name__ == '__main__':
    test_cu13_cu17_movil()
