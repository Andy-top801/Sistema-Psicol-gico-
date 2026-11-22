# -*- coding: utf-8 -*-
# CU22 / HU-48 — Secuencia_Corregido_CU22_Matching_Asignacion_IA vía API real.
#   python tests/test_cu22_matching_api.py
import sys, os
from datetime import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from django_tenants.utils import schema_context
from rest_framework.test import APIClient

TENANT = 'centro_esperanza'
MARCA = 'test-cu22'


def _usuario(Usuario, Rol, email, rol_contiene, nombre):
    rol = Rol.objects.filter(nombre__icontains=rol_contiene).first()
    return Usuario.objects.create_user(email=email, password='x', nombre=nombre, apellido='CU22', rol=rol)


def _limpiar():
    from accounts.models import Usuario
    from clinica.models import Psicologo
    Psicologo.objects.filter(usuario__email__startswith=MARCA).delete()
    Usuario.objects.filter(email__startswith=MARCA).delete()  # cascada: paciente, intake, clasificación, sugerencias


def _preparar():
    from datetime import date
    from accounts.models import Usuario, Rol
    from clinica.models import (Psicologo, Paciente, Especialidad, PsicologoEspecialidad, Disponibilidad,
                                FormularioPreConsulta, RespuestaPreConsulta, ClasificacionIA)
    _limpiar()
    tcc = Especialidad.objects.filter(nombre__icontains='Cognitivo').first() or \
        Especialidad.objects.create(nombre='Terapia Cognitivo-Conductual (TCC)', descripcion='ansiedad')
    fam = Especialidad.objects.filter(nombre__icontains='Familiar').first() or \
        Especialidad.objects.create(nombre='Terapia Familiar y Sistémica', descripcion='pareja')

    def psico(n, esp, carga, cupo, modalidad, franjas):
        u = _usuario(Usuario, Rol, f'{MARCA}-psi{n}@x.bo', 'psic', f'Psico{n}')
        p = Psicologo.objects.create(usuario=u, numero_colegiado=f'{MARCA}-{n}', modalidad=modalidad,
                                     carga_actual=carga, cupo_maximo=cupo)
        PsicologoEspecialidad.objects.create(psicologo=p, especialidad=esp)
        for d in range(1, franjas + 1):   # 08:00-16:20 = 10 bloques de 50 min por día
            Disponibilidad.objects.create(psicologo=p, dia_semana=d, hora_inicio=time(8), hora_fin=time(16, 20))
        return p

    p_ideal = psico(1, tcc, 0, 20, 'MIXTA', 4)          # 40 bloques → 100 pts
    p_lleno = psico(2, tcc, 20, 20, 'MIXTA', 4)         # cupo completo
    p_otro = psico(3, fam, 2, 20, 'PRESENCIAL', 1)      # sin afinidad
    p_manual = psico(4, fam, 0, 20, 'MIXTA', 1)         # elegido manualmente

    up = _usuario(Usuario, Rol, f'{MARCA}-pac@x.bo', 'pacien', 'PacienteCU22')
    pac = Paciente.objects.create(usuario=up, codigo_expediente=f'{MARCA}-EXP', ci=f'{MARCA}-CI',
                                  fecha_nacimiento=date(1990, 1, 1), genero='F', modalidad_preferencia='VIRTUAL')
    up2 = _usuario(Usuario, Rol, f'{MARCA}-pac2@x.bo', 'pacien', 'Paciente2CU22')
    pac2 = Paciente.objects.create(usuario=up2, codigo_expediente=f'{MARCA}-EXP2', ci=f'{MARCA}-CI2',
                                   fecha_nacimiento=date(1990, 1, 1), genero='M')
    sin_triaje_u = _usuario(Usuario, Rol, f'{MARCA}-pac3@x.bo', 'pacien', 'SinTriaje')
    sin_triaje = Paciente.objects.create(usuario=sin_triaje_u, codigo_expediente=f'{MARCA}-EXP3', ci=f'{MARCA}-CI3',
                                         fecha_nacimiento=date(1990, 1, 1), genero='M')
    form = FormularioPreConsulta.objects.first()
    for p in (pac, pac2):
        r = RespuestaPreConsulta.objects.create(formulario=form, paciente=p, motivo_consulta='ansiedad y pánico',
                                                nivel_urgencia_percibido=3)
        ClasificacionIA.objects.create(respuestapreconsulta=r, categoria_principal='ANSIEDAD_FOBIAS',
                                       confianza_score=0.9, nivel_severidad='MODERADA', alerta_crisis=False,
                                       explicacion_heuristica='x', hash_trazabilidad_sha256='0' * 64)
    coord = Usuario.objects.get(email='coordinador@centroesperanza.com')
    return dict(p_ideal=p_ideal, p_lleno=p_lleno, p_otro=p_otro, p_manual=p_manual, pac=pac, pac2=pac2,
                sin_triaje=sin_triaje, coord=coord, paciente_user=up)


def test_cu22_matching_hitl():
    from clinica.models import Psicologo, Paciente, SugerenciaMatching
    from audit.services import read_events
    with schema_context(TENANT):
        d = _preparar()
        # Para que el ranking sea determinista, el resto de psicólogos queda temporalmente sin cupo
        otros = list(Psicologo.objects.exclude(usuario__email__startswith=MARCA).values('id', 'carga_actual', 'cupo_maximo'))
        for o in otros:
            Psicologo.objects.filter(id=o['id']).update(carga_actual=o['cupo_maximo'])

    api = APIClient(HTTP_X_TENANT_ID=TENANT)
    api.force_authenticate(user=d['coord'])
    url = '/api/v1/matching/sugerencias/'
    try:
        # ── Msg 2-18: Top 3 con desglose de factores ───────────────────────────
        r = api.get(url, {'paciente_id': str(d['pac'].id)})
        assert r.status_code == 200, r.content
        body = r.json()
        assert body['triaje']['categoria'] == 'ANSIEDAD_FOBIAS'
        assert body['paciente']['modalidad_preferencia'] == 'VIRTUAL'
        top = body['top3_candidatos']
        assert len(top) == 3
        assert top[0]['psicologo_id'] == str(d['p_ideal'].id)
        assert top[0]['score'] == 100.0
        assert top[0]['factores'] == {'afinidad': 1.0, 'disponibilidad': 1.0, 'balance_carga': 1.0, 'modalidad': 1.0}
        assert top[0]['pesos'] == {'afinidad': 0.4, 'disponibilidad': 0.3, 'balance_carga': 0.2, 'modalidad': 0.1}
        assert top[0]['nombre_psicologo'] and top[0]['especialidades']
        lleno = [c for c in top if c['psicologo_id'] == str(d['p_lleno'].id)]
        con_cupo = [c for c in top if not c['cupo_completo']]
        assert all(top.index(c) < top.index(x) for c in con_cupo for x in top if x['cupo_completo'])
        if lleno:
            assert lleno[0]['factores']['balance_carga'] == 0.0 and lleno[0]['cupo_completo'] is True
        # HU-48 (a): ruta oficial /ia/sugerir-psicologo/{paciente_id}/ devuelve lo mismo
        r = api.get(f"/api/v1/ia/sugerir-psicologo/{d['pac'].id}/")
        assert r.status_code == 200 and r.json()['top3_candidatos'][0]['psicologo_id'] == str(d['p_ideal'].id)
        with schema_context(TENANT):
            pend = SugerenciaMatching.objects.filter(paciente=d['pac'], estado_decision='PENDIENTE_VALIDACION')
            assert pend.count() == 3, "Solo las sugerencias de la última llamada"
            # El GET nunca asigna
            assert Paciente.objects.get(id=d['pac'].id).psicologo_asignado_id is None
            assert Psicologo.objects.get(id=d['p_ideal'].id).carga_actual == 0
        sug_top1 = r.json()['top3_candidatos'][0]['sugerencia_id']

        # Validaciones del GET
        assert api.get(url, {'paciente_id': str(d['sin_triaje'].id)}).status_code == 409
        assert api.get(url, {'paciente_id': '00000000-0000-0000-0000-000000000000'}).status_code == 404
        assert api.get(url).status_code == 400

        # ── Msg 21-29: aprobar sugerencia (alt: coordinador acepta) ──────────────
        r = api.post(f'/api/v1/matching/{sug_top1}/aprobar/', {'psicologo_id': str(d['p_otro'].id)}, format='json')
        assert r.status_code == 400, "psicologo_id debe coincidir con el sugerido"
        r = api.post(f'/api/v1/matching/{sug_top1}/aprobar/', {'psicologo_id': str(d['p_ideal'].id)}, format='json')
        assert r.status_code == 200, r.content
        assert r.json()['mensaje'] == 'Psicólogo asignado exitosamente'
        with schema_context(TENANT):
            assert Paciente.objects.get(id=d['pac'].id).psicologo_asignado_id == d['p_ideal'].id
            assert Psicologo.objects.get(id=d['p_ideal'].id).carga_actual == 1
            s = SugerenciaMatching.objects.get(id=sug_top1)
            assert s.estado_decision == 'APROBADO' and s.aprobado_hitl is True
            assert s.psicologo_asignado_final_id == d['p_ideal'].id
            assert s.validado_por_coordinador_id == d['coord'].id
            assert not SugerenciaMatching.objects.filter(paciente=d['pac'], estado_decision='PENDIENTE_VALIDACION').exists()
        # Doble clic → 409 y la carga no cambia
        r = api.post(f'/api/v1/matching/{sug_top1}/aprobar/', {'psicologo_id': str(d['p_ideal'].id)}, format='json')
        assert r.status_code == 409
        with schema_context(TENANT):
            assert Psicologo.objects.get(id=d['p_ideal'].id).carga_actual == 1
        # Paciente ya asignado → el GET también responde 409
        assert api.get(url, {'paciente_id': str(d['pac'].id)}).status_code == 409

        # ── Msg 30-39: rechazar y reasignar manualmente (else) ──────────────────
        r = api.get(url, {'paciente_id': str(d['pac2'].id)})
        assert r.status_code == 200
        sug2 = r.json()['top3_candidatos'][0]['sugerencia_id']
        base = f'/api/v1/matching/{sug2}/rechazar_y_reasignar/'
        assert api.post(base, {'psicologo_manual_id': str(d['p_manual'].id)}, format='json').status_code == 400
        assert api.post(base, {'psicologo_manual_id': str(d['p_manual'].id), 'motivo': 'corto'},
                        format='json').status_code == 400
        motivo = 'El paciente pidió explícitamente atención con este profesional por continuidad.'
        r = api.post(base, {'psicologo_manual_id': str(d['p_manual'].id), 'motivo': motivo}, format='json')
        assert r.status_code == 200, r.content
        assert r.json()['mensaje'] == 'Asignación manual registrada'
        with schema_context(TENANT):
            s = SugerenciaMatching.objects.get(id=sug2)
            assert s.estado_decision == 'RECHAZADO_MANUAL' and s.aprobado_hitl is False
            assert s.psicologo_asignado_final_id == d['p_manual'].id
            assert s.justificacion_clinica == motivo
            assert Paciente.objects.get(id=d['pac2'].id).psicologo_asignado_id == d['p_manual'].id
            assert Psicologo.objects.get(id=d['p_manual'].id).carga_actual == 1
            assert Psicologo.objects.get(id=d['p_ideal'].id).carga_actual == 1  # el sugerido no cambia

        # HU-48 (c): decisiones en la bitácora del sistema
        acciones = [e.get('action') for e in read_events()]
        assert 'MATCHING_HITL_APROBADO' in acciones and 'MATCHING_REASIGNACION_MANUAL' in acciones

        # Solo el coordinador opera la consola
        api.force_authenticate(user=d['paciente_user'])
        assert api.get(url, {'paciente_id': str(d['pac'].id)}).status_code == 403
        assert api.post(f'/api/v1/matching/{sug2}/aprobar/', {}, format='json').status_code == 403
    finally:
        with schema_context(TENANT):
            for o in otros:
                Psicologo.objects.filter(id=o['id']).update(carga_actual=o['carga_actual'])
            _limpiar()


if __name__ == "__main__":
    test_cu22_matching_hitl()
    print("ALL CU22 MATCHING API TESTS PASSED [OK]")
