# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_clasificador_motivo_consulta_nlp_y_crisis():
    from clinica.ia_rules_engine import ClasificadorMotivoConsulta

    # 1. Test PII sanitization
    texto_raw = "Mi nombre es Ana, mi CI es 8374829 y mi correo es ana.paciente@gmail.com. Celular: 71234567."
    limpio = ClasificadorMotivoConsulta.sanitizar_pii(texto_raw)
    assert "8374829" not in limpio
    assert "ana.paciente@gmail.com" not in limpio
    assert "71234567" not in limpio

    # 2. Test Anxiety classification
    res_ansiedad = ClasificadorMotivoConsulta.clasificar(
        motivo="Siento mucha angustia, taquicardia y miedo constante a fallar en mi trabajo.",
        sintomas="Palpitaciones y ahogo al salir de casa",
        urgencia_percibida=3
    )
    assert res_ansiedad['categoria_principal'] == 'ANSIEDAD_FOBIAS'
    assert res_ansiedad['alerta_crisis'] is False
    assert res_ansiedad['confianza_score'] >= 0.70
    assert len(res_ansiedad['hash_trazabilidad_sha256']) == 64

    # 3. Test Depression classification
    res_depresion = ClasificadorMotivoConsulta.clasificar(
        motivo="Tengo un desánimo profundo, lloro todos los días y siento un gran vacío.",
        sintomas="Tristeza persistente y culpa",
        urgencia_percibida=4
    )
    assert res_depresion['categoria_principal'] == 'DEPRESION_ANIMO'
    assert res_depresion['nivel_severidad'] in ['MODERADO', 'SEVERO']

    # 4. Test Crisis vital alert trigger (CP-M11 / Sequence CU21)
    res_crisis = ClasificadorMotivoConsulta.clasificar(
        motivo="Ya no aguanto más el sufrimiento, siento que quiero morir y acabar con todo.",
        sintomas="Pensamientos de hacerme daño",
        urgencia_percibida=5
    )
    assert res_crisis['alerta_crisis'] is True
    assert res_crisis['nivel_severidad'] == 'CRITICA'
    assert 'morir' in [w.lower() for w in res_crisis['palabras_clave_detectadas']] or any('morir' in p for p in res_crisis['palabras_clave_detectadas'])


if __name__ == "__main__":
    test_clasificador_motivo_consulta_nlp_y_crisis()
    print("ALL CLASIFICACION IA TESTS PASSED [OK]")
