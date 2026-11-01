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
from clinica.models import Paciente, Psicologo, RegistroAnimo, TareaTerapeutica, HistoriaClinica
from agenda.models import Cita
from agenda.views import TeleconsultaAccessView, TeleconsultaFinishView
from clinica.views import RegistroAnimoViewSet, TareaTerapeuticaViewSet

def test_teleconsulta_window_mood_and_task_delivery():
    tenant = Tenant.objects.exclude(schema_name='public').first()
    assert tenant is not None

    with schema_context(tenant.schema_name):
        factory = APIRequestFactory()
        paciente = Paciente.objects.select_related('usuario', 'historia_clinica').first()
        if hasattr(paciente, 'historia_clinica') and paciente.historia_clinica:
            paciente.historia_clinica.cerrada = False
            paciente.historia_clinica.save(update_fields=['cerrada'])
        else:
            h, _ = HistoriaClinica.objects.get_or_create(paciente=paciente, defaults={'codigo_expediente': 'EXP-TEST-01', 'cerrada': False})
            paciente.historia_clinica = h
        psicologo = Psicologo.objects.select_related('usuario').first()
        usuario_paciente = paciente.usuario

        # ------------------------------------------------------------------
        # 1. Teleconsulta WebRTC: Validación de Ventana Horaria (CU13 / HU-44 / CP-M07)
        # ------------------------------------------------------------------
        ahora = timezone.localtime()

        # Cita C1: Activa AHORA (dentro de ventana T-10m a T+45m)
        hora_ini_activa = ahora.time()
        hora_fin_activa = (ahora + timedelta(minutes=45)).time()
        if hora_fin_activa <= hora_ini_activa:
            hora_ini_activa = time(11, 0)
            hora_fin_activa = time(11, 50)

        cita_activa = Cita.objects.create(
            paciente=paciente,
            psicologo=psicologo,
            fecha=ahora.date(),
            hora_inicio=hora_ini_activa,
            hora_fin=hora_fin_activa,
            modalidad='VIRTUAL',
            estado='PROGRAMADA',
            motivo_consulta="Teleconsulta activa en ventana"
        )

        view_access = TeleconsultaAccessView.as_view()
        req_access_ok = factory.get(f'/api/agenda/teleconsulta/{cita_activa.id}/access/')
        force_authenticate(req_access_ok, user=usuario_paciente)
        resp_access_ok = view_access(req_access_ok, cita_id=str(cita_activa.id))

        assert resp_access_ok.status_code == 200, f"Debe permitir acceso en ventana: {resp_access_ok.data}"
        assert 'room_name' in resp_access_ok.data or 'room' in resp_access_ok.data

        # Finalizar teleconsulta
        view_finish = TeleconsultaFinishView.as_view()
        req_finish = factory.post(
            f'/api/agenda/teleconsulta/{cita_activa.id}/finish/',
            {'duracion_segundos': 1800, 'notas_sesion': 'Sesión productiva.'},
            format='json'
        )
        force_authenticate(req_finish, user=psicologo.usuario)
        resp_finish = view_finish(req_finish, cita_id=str(cita_activa.id))
        assert resp_finish.status_code == 200
        cita_activa.refresh_from_db()
        assert cita_activa.estado == 'REALIZADA'

        # Cita C2: En 3 días (Fuera de ventana teleconsulta)
        cita_futura = Cita.objects.create(
            paciente=paciente,
            psicologo=psicologo,
            fecha=(ahora + timedelta(days=3)).date(),
            hora_inicio=time(15, 0),
            hora_fin=time(16, 0),
            modalidad='VIRTUAL',
            estado='CONFIRMADA',
            motivo_consulta="Teleconsulta lejana"
        )
        req_access_bad = factory.get(f'/api/agenda/teleconsulta/{cita_futura.id}/access/')
        force_authenticate(req_access_bad, user=usuario_paciente)
        resp_access_bad = view_access(req_access_bad, cita_id=str(cita_futura.id))

        assert resp_access_bad.status_code == 400, "Debe rechazar acceso fuera de ventana horaria"
        assert resp_access_bad.data.get('codigo') == 'OUTSIDE_TELECONSULTA_WINDOW'

        # ------------------------------------------------------------------
        # 2. Mood Tracker: Registro de Estado de Ánimo Diario (CU17 / HU-46 / CP-M09)
        # ------------------------------------------------------------------
        view_animo = RegistroAnimoViewSet.as_view({'post': 'create', 'get': 'list'})
        req_animo_1 = factory.post(
            '/api/clinica/registro-animo/',
            {
                'paciente': str(paciente.id),
                'fecha_registro': ahora.date().isoformat(),
                'estado_animo': 'FELIZ',
                'escala_valor': 4,
                'factores_contexto': ['Familia', 'Ejercicio', 'Descanso'],
                'nota_reflexiva': 'Me sentí más tranquilo hoy después de meditar.'
            },
            format='json'
        )
        force_authenticate(req_animo_1, user=usuario_paciente)
        resp_animo_1 = view_animo(req_animo_1)
        assert resp_animo_1.status_code in [200, 201]

        # Segundo registro en el mismo día debe actualizarse sin violar unicidad
        req_animo_2 = factory.post(
            '/api/clinica/registro-animo/',
            {
                'paciente': str(paciente.id),
                'fecha_registro': ahora.date().isoformat(),
                'estado_animo': 'MUY_FELIZ',
                'escala_valor': 5,
                'factores_contexto': ['Familia', 'Logro Laboral'],
                'nota_reflexiva': 'Gran cierre del día.'
            },
            format='json'
        )
        force_authenticate(req_animo_2, user=usuario_paciente)
        resp_animo_2 = view_animo(req_animo_2)
        assert resp_animo_2.status_code in [200, 201]

        # Verificar unicidad en DB
        registros_hoy = RegistroAnimo.objects.filter(paciente=paciente, fecha_registro=ahora.date())
        assert registros_hoy.count() == 1
        assert registros_hoy.first().estado_animo == 'MUY_FELIZ'

        # ------------------------------------------------------------------
        # 3. Tarea Terapéutica: Entrega de Evidencia y Reflexión (CU17 / HU-45 / CP-M08)
        # ------------------------------------------------------------------
        historia = paciente.historia_clinica
        tarea = TareaTerapeutica.objects.create(
            historia_clinica=historia,
            psicologo=psicologo,
            paciente=paciente,
            titulo="Registro de Pensamientos Automáticos",
            descripcion="Anotar en una libreta cada situación que disparó ansiedad.",
            categoria='AUTOREGISTRO',
            fecha_limite=ahora.date() + timedelta(days=2),
            estado='PENDIENTE'
        )

        view_tarea = TareaTerapeuticaViewSet.as_view({'post': 'entregar_tarea_alias'})
        req_tarea = factory.post(
            f'/api/clinica/tareas/{tarea.id}/entregar/',
            {
                'texto_reflexion': 'Pude identificar 3 distorsiones cognitivas de catastrofización.',
                'dificultad_percibida': 2
            },
            format='json'
        )
        force_authenticate(req_tarea, user=usuario_paciente)
        resp_tarea = view_tarea(req_tarea, pk=str(tarea.id))

        assert resp_tarea.status_code == 200, f"Error entrega tarea: {resp_tarea.data}"
        tarea.refresh_from_db()
        assert tarea.estado == 'COMPLETADA'

        # Limpiar
        cita_activa.delete()
        cita_futura.delete()
        tarea.delete()

if __name__ == "__main__":
    test_teleconsulta_window_mood_and_task_delivery()
    print("ALL TELECONSULTA, MOOD & TASK DELIVERY TESTS PASSED [OK]")
