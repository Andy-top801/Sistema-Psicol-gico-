# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')
import django
django.setup()
import uuid
from django.utils import timezone

def test_sprint3_models_exist():
    from clinica.models import TokenFCM, RegistroAnimo, ClasificacionIA, SugerenciaMatching
    from agenda.models import NotificacionCita

    assert TokenFCM._meta.db_table == 'comunicacion_tokenfcm'
    assert NotificacionCita._meta.db_table == 'agenda_notificacioncita'
    assert RegistroAnimo._meta.db_table == 'clinica_registroanimo'
    assert ClasificacionIA._meta.db_table == 'clinica_clasificacionia'
    assert SugerenciaMatching._meta.db_table == 'clinica_sugerenciamatching'

    # Check key fields in TokenFCM
    fcm_fields = [f.name for f in TokenFCM._meta.get_fields()]
    for req in ['paciente', 'token', 'plataforma', 'activo', 'creado_en']:
        assert req in fcm_fields

    # Check key fields in NotificacionCita
    notif_fields = [f.name for f in NotificacionCita._meta.get_fields()]
    for req in ['cita', 'tipo_evento', 'canal', 'enviada', 'fecha_programada']:
        assert req in notif_fields

    # Check key fields in RegistroAnimo
    animo_fields = [f.name for f in RegistroAnimo._meta.get_fields()]
    for req in ['paciente', 'fecha_registro', 'estado_animo', 'escala_valor', 'factores_contexto']:
        assert req in animo_fields

    # Check key fields in ClasificacionIA
    clasif_fields = [f.name for f in ClasificacionIA._meta.get_fields()]
    for req in ['respuestapreconsulta', 'categoria_principal', 'confianza_score', 'nivel_severidad', 'alerta_crisis', 'hash_trazabilidad_sha256']:
        assert req in clasif_fields

    # Check key fields in SugerenciaMatching
    match_fields = [f.name for f in SugerenciaMatching._meta.get_fields()]
    for req in ['paciente', 'clasificacion', 'psicologo_sugerido', 'ranking_posicion', 'score_afinidad', 'factores_ponderacion', 'estado_decision']:
        assert req in match_fields


if __name__ == "__main__":
    test_sprint3_models_exist()
    print("ALL SPRINT 3 MODELS TESTS PASSED [OK]")
