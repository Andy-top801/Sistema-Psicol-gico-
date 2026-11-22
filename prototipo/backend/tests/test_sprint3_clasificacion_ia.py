# -*- coding: utf-8 -*-
# CU21 / HU-47 — Motor de inferencia (Hugging Face zero-shot) + red de seguridad por reglas.
# No descarga el modelo: el pipeline HF se sustituye por stubs deterministas.
#   python tests/test_sprint3_clasificacion_ia.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from clinica import ia_nlp


def _pipeline_que_falla():
    raise RuntimeError("modelo no disponible")


def _stub_pipeline(categoria_label, p_cat, p_riesgo):
    """Simula transformers.pipeline('zero-shot-classification')."""
    def clasificador(texto, candidate_labels, hypothesis_template=None, multi_label=False):
        if multi_label:
            return {'labels': list(candidate_labels), 'scores': [p_riesgo] + [0.01] * (len(candidate_labels) - 1)}
        otros = [l for l in candidate_labels if l != categoria_label]
        resto = (1 - p_cat) / len(otros)
        return {'labels': [categoria_label] + otros, 'scores': [p_cat] + [resto] * len(otros)}
    return lambda: clasificador


def _con_pipeline(fn):
    original = ia_nlp._pipeline
    ia_nlp._pipeline = fn
    return original


class _Fake:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_sanitizar_pii_incluye_nombre():
    from clinica.models import RespuestaPreConsulta
    fake = _Fake(paciente=_Fake(usuario=_Fake(nombre='Ana', apellido='Quispe')))
    texto = "Soy Ana Quispe, CI 8374829, correo ana@x.com, celular 71234567. ANA necesita ayuda."
    limpio = RespuestaPreConsulta.sanitizar_pii(fake, texto)
    for dato in ('Ana', 'ANA', 'Quispe', '8374829', 'ana@x.com', '71234567'):
        assert dato not in limpio, (dato, limpio)
    assert '[NOMBRE ANONIMIZADO]' in limpio


def test_fallback_sin_modelo():
    orig = _con_pipeline(_pipeline_que_falla)
    try:
        r = ia_nlp.consultar_inferencia_nlp("siento angustia, taquicardia y ataques de pánico")
        assert r['modelo_ia'] == 'REGLAS-FALLBACK'
        assert r['categoria'] == 'ANSIEDAD_FOBIAS'
        r2 = ia_nlp.consultar_inferencia_nlp("ya no quiero vivir")
        assert r2['p_riesgo'] == 0.95
    finally:
        ia_nlp._pipeline = orig


def test_texto_vacio_no_llama_al_modelo():
    orig = _con_pipeline(lambda: (_ for _ in ()).throw(AssertionError("no debe llamarse")))
    try:
        r = ia_nlp.consultar_inferencia_nlp('[TELÉFONO ANONIMIZADO]  ')
        assert r == {'categoria': 'OTRO', 'confianza': 0.0, 'p_riesgo': 0.0, 'modelo_ia': 'SIN-TEXTO'}
    finally:
        ia_nlp._pipeline = orig


def test_stub_hf():
    orig = _con_pipeline(_stub_pipeline('ansiedad, miedo o pánico', 0.9, 0.8))
    try:
        r = ia_nlp.consultar_inferencia_nlp("me tiemblan las manos")
        assert r['categoria'] == 'ANSIEDAD_FOBIAS'
        assert r['confianza'] == 0.9
        assert r['modelo_ia'] == ia_nlp.modelo_configurado()
        ev = ia_nlp.evaluar_patrones_riesgo_crisis(r['p_riesgo'], r['categoria'], "me tiemblan las manos", 2)
        assert ev['alerta_crisis'] is True and ev['nivel_severidad'] == 'CRITICA'
    finally:
        ia_nlp._pipeline = orig


def test_confianza_baja_es_otro():
    orig = _con_pipeline(_stub_pipeline('duelo o pérdida de un ser querido', 0.22, 0.0))
    try:
        assert ia_nlp.consultar_inferencia_nlp("tengo dudas varias")['categoria'] == 'OTRO'
    finally:
        ia_nlp._pipeline = orig


def test_crisis_por_reglas_aunque_ml_diga_cero():
    ev = ia_nlp.evaluar_patrones_riesgo_crisis(0.0, 'DEPRESION_ANIMO', 'a veces quiero morir', 2)
    assert ev['alerta_crisis'] is True
    assert ev['nivel_severidad'] == 'CRITICA'
    assert ev['puntaje_severidad'] == 5
    assert any('morir' in p for p in ev['palabras_clave'])


def test_malestar_5_sin_texto_riesgo():
    ev = ia_nlp.evaluar_patrones_riesgo_crisis(0.0, 'ANSIEDAD_FOBIAS', 'muchos nervios', 5)
    assert ev['alerta_crisis'] is False
    assert ev['nivel_severidad'] == 'ALTA'
    assert ev['puntaje_severidad'] == 4


def test_escala_de_severidades():
    assert ia_nlp.evaluar_patrones_riesgo_crisis(0.0, 'OTRO', 'x', 1)['nivel_severidad'] == 'BAJA'
    assert ia_nlp.evaluar_patrones_riesgo_crisis(0.0, 'OTRO', 'x', 1)['puntaje_severidad'] == 1
    assert ia_nlp.evaluar_patrones_riesgo_crisis(0.40, 'OTRO', 'x', 1)['nivel_severidad'] == 'MODERADA'
    assert ia_nlp.evaluar_patrones_riesgo_crisis(0.60, 'OTRO', 'x', 1)['nivel_severidad'] == 'ALTA'
    assert ia_nlp.evaluar_patrones_riesgo_crisis(0.70, 'OTRO', 'x', 1)['alerta_crisis'] is True


def test_violencia():
    ev = ia_nlp.evaluar_patrones_riesgo_crisis(0.0, 'PAREJA_FAMILIA', 'mi pareja me golpea', 3)
    assert ev['alerta_crisis'] is True


def test_trampas_no_son_crisis_por_reglas():
    for t in ('me muero de risa con mis amigos', 'quiero matar el tiempo leyendo'):
        assert ia_nlp.evaluar_patrones_riesgo_crisis(0.0, 'OTRO', t, 2)['alerta_crisis'] is False, t


if __name__ == "__main__":
    for nombre, fn in list(globals().items()):
        if nombre.startswith('test_'):
            fn()
            print(f"  ok  {nombre}")
    print("ALL CLASIFICACION IA TESTS PASSED [OK]")
