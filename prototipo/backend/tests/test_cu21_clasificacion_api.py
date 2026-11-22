# -*- coding: utf-8 -*-
# CU21 / HU-47 — Secuencia_Corregido_CU21_Clasificacion_IA vía API real.
# Usa IA_HABILITADA=False (respaldo por reglas) para que sea determinista y no descargue el modelo.
#   python tests/test_cu21_clasificacion_api.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from django.test import override_settings
from django_tenants.utils import schema_context
from rest_framework.test import APIClient

TENANT = 'centro_esperanza'
MARCA = '[TEST CU21]'


def _intake(paciente, formulario, motivo, malestar=3, sintomas=''):
    from clinica.models import RespuestaPreConsulta
    return RespuestaPreConsulta.objects.create(
        formulario=formulario, paciente=paciente, motivo_consulta=motivo,
        sintomas_principales=sintomas, nivel_urgencia_percibido=malestar, antecedentes_medicos=MARCA)


@override_settings(IA_HABILITADA=False)
def test_cu21_clasificar_triaje():
    with schema_context(TENANT):
        from accounts.models import Usuario
        from clinica.models import (Paciente, FormularioPreConsulta, RespuestaPreConsulta,
                                    ClasificacionIA, AuditoriaIA)
        coord = Usuario.objects.get(email='coordinador@centroesperanza.com')
        paciente = Paciente.objects.select_related('usuario').first()
        form = FormularioPreConsulta.objects.first()
        RespuestaPreConsulta.objects.filter(antecedentes_medicos=MARCA).delete()

        crisis = _intake(paciente, form, 'Ya no aguanto, quiero quitarme la vida.', 4)
        ordinario = _intake(paciente, form, 'Discuto mucho con mi pareja, ya no nos comunicamos.', 2)
        pii = _intake(paciente, form, f'Llamar al 71234567, soy {paciente.usuario.nombre}, tengo angustia y pánico.', 3)

    api = APIClient(HTTP_X_TENANT_ID=TENANT)
    api.force_authenticate(user=coord)
    try:
        # ── alt [alerta_crisis == true] Protocolo Crisis (Msg 9-17) ──────────────
        r = api.post('/api/v1/ia/clasificar-triaje/', {'respuesta_id': str(crisis.id)}, format='json')
        assert r.status_code == 200, r.content
        d = r.json()
        assert d['alerta_crisis'] is True
        assert d['nivel'] == 'ALTO'
        assert d['sugerencia_inmediata']
        with schema_context(TENANT):
            c = ClasificacionIA.objects.get(respuestapreconsulta=crisis)
            assert c.nivel_atencion == 'CRITICO' and c.nivel_severidad == 'CRITICA' and c.puntaje_severidad == 5
            aud = AuditoriaIA.objects.get(clasificacion=c)
            assert aud.alerta_crisis is True and len(aud.hash_prompt) == 64
            assert aud.modelo_ia == 'REGLAS-FALLBACK'

        # ── else Atención ordinaria (Msg 19-25) ──────────────────────────────────
        r = api.post('/api/v1/ia/clasificar-triaje/', {'respuesta_id': str(ordinario.id)}, format='json')
        assert r.status_code == 200, r.content
        d = r.json()
        assert d['alerta_crisis'] is False and d['nivel'] == 'REGULAR'
        assert d['clasificacion']['categoria_principal'] == 'PAREJA_FAMILIA'
        assert d['clasificacion']['nivel_severidad'] in ('BAJA', 'MODERADA')
        with schema_context(TENANT):
            c = ClasificacionIA.objects.get(respuestapreconsulta=ordinario)
            assert c.nivel_atencion == 'REGULAR'
            assert AuditoriaIA.objects.get(clasificacion=c).alerta_crisis is False

        # Reclasificar no duplica la clasificación vigente
        r = api.post('/api/v1/ia/clasificar-triaje/', {'respuesta_id': str(ordinario.id)}, format='json')
        assert r.status_code == 200
        with schema_context(TENANT):
            assert ClasificacionIA.objects.filter(respuestapreconsulta=ordinario).count() == 1

        # PII nunca se persiste en la explicación ni en palabras clave
        r = api.post('/api/v1/ia/clasificar-triaje/', {'respuesta_id': str(pii.id)}, format='json')
        assert r.status_code == 200
        cl = r.json()['clasificacion']
        assert '71234567' not in cl['explicacion_heuristica'] + str(cl['palabras_clave_detectadas'])
        assert cl['categoria_principal'] == 'ANSIEDAD_FOBIAS'

        # Validaciones
        r = api.post('/api/v1/ia/clasificar-triaje/', {'respuesta_id': '00000000-0000-0000-0000-000000000000'}, format='json')
        assert r.status_code == 404
        r = api.post('/api/v1/ia/clasificar-triaje/', {'respuesta_id': str(pii.id), 'escala_malestar': 9}, format='json')
        assert r.status_code == 400
        r = api.post('/api/v1/ia/clasificar-triaje/', {}, format='json')
        assert r.status_code == 400

        # Ruta anterior (bug 1: escala_malestar inexistente) sigue funcionando
        r = api.post(f'/api/v1/intake/{ordinario.id}/clasificar/', {}, format='json')
        assert r.status_code == 200, r.content

        # Alertas para la consola del coordinador
        r = api.get('/api/v1/triaje/alertas/')
        assert r.status_code == 200
        assert any(a['respuestapreconsulta'] == str(crisis.id) for a in r.json())

        # Bug 6: crear el intake por la API lo clasifica automáticamente
        api.force_authenticate(user=paciente.usuario)
        r = api.post('/api/v1/respuestas-preconsulta/', {
            'formulario': str(form.id), 'paciente': str(paciente.id),
            'motivo_consulta': 'Mi madre falleció y estoy de duelo.', 'nivel_urgencia_percibido': 3,
            'antecedentes_medicos': MARCA}, format='json')
        assert r.status_code == 201, r.content
        with schema_context(TENANT):
            auto = ClasificacionIA.objects.get(respuestapreconsulta_id=r.json()['id'])
            assert auto.categoria_principal == 'DUELO_ADAPTACION'
    finally:
        with schema_context(TENANT):
            RespuestaPreConsulta.objects.filter(antecedentes_medicos=MARCA).delete()
            AuditoriaIA.objects.filter(clasificacion__isnull=True, hash_prompt__isnull=False,
                                       modelo_ia='REGLAS-FALLBACK').delete()


if __name__ == "__main__":
    test_cu21_clasificar_triaje()
    print("ALL CU21 CLASIFICACION API TESTS PASSED [OK]")
