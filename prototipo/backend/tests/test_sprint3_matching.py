# -*- coding: utf-8 -*-
# CU22 / HU-48 — fórmula transparente: Score = 0.4×Afinidad + 0.3×Disponibilidad + 0.2×BalanceCarga + 0.1×Modalidad
#   python tests/test_sprint3_matching.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from clinica.ia_rules_engine import MatchingPsicologoService as M


class _Esp:
    def __init__(self, nombre, descripcion=''):
        self.nombre, self.descripcion = nombre, descripcion

    def obtener_nombre(self):
        return self.nombre


def test_formula_hu48():
    r = M.calcular_score(1.0, (5, 20), 32, 'MIXTA', 'VIRTUAL')
    assert r['factores'] == {'afinidad': 1.0, 'disponibilidad': 0.8, 'balance_carga': 0.75, 'modalidad': 1.0}
    assert r['score'] == 89.0
    assert r['cupo_completo'] is False


def test_limites_de_factores():
    r = M.calcular_score(0.0, (20, 20), 40, 'PRESENCIAL', 'VIRTUAL')
    assert r['factores'] == {'afinidad': 0.0, 'disponibilidad': 1.0, 'balance_carga': 0.0, 'modalidad': 0.0}
    assert r['score'] == 30.0 and r['cupo_completo'] is True
    # cupo 0 se trata como lleno (no división por cero)
    assert M.calcular_score(1.0, (0, 0), 0, 'VIRTUAL', 'VIRTUAL')['cupo_completo'] is True
    assert M.calcular_score(1.0, (25, 20), 0, 'VIRTUAL', 'MIXTA')['factores']['balance_carga'] == 0.0


def test_afinidad_por_categoria():
    tcc = _Esp("Terapia Cognitivo-Conductual (TCC)", "Reestructuración cognitiva y abordaje de esquemas desadaptativos y ansiedad.")
    fam = _Esp("Terapia Familiar y Sistémica", "Intervención sistémica orientada a conflictos vinculares y de pareja.")
    inf = _Esp("Psicología Infantil y del Desarrollo", "Trastornos del neurodesarrollo en infancia y adolescencia.")
    pal = _Esp("Psicooncología y Cuidados Paliativos", "Acompañamiento en enfermedades crónicas, duelo y trauma.")
    clin = _Esp("Psicología Clínica y de la Salud", "Tratamiento de trastornos emocionales y del estado de ánimo.")
    assert M.afinidad('ANSIEDAD_FOBIAS', [fam, tcc]) == 1.0
    assert M.afinidad('ANSIEDAD_FOBIAS', [fam]) == 0.0
    assert M.afinidad('PAREJA_FAMILIA', [fam]) == 1.0
    assert M.afinidad('INFANTO_JUVENIL', [inf]) == 1.0
    assert M.afinidad('DUELO_ADAPTACION', [pal]) == 1.0
    assert M.afinidad('DEPRESION_ANIMO', [clin]) == 1.0
    assert M.afinidad('OTRO', [clin, tcc]) == 0.0
    assert M.afinidad('ANSIEDAD_FOBIAS', []) == 0.0


def test_top3_saturados_al_final():
    candidatos = [
        {'id': 'A', **M.calcular_score(1.0, (20, 20), 10, 'MIXTA', 'MIXTA')},   # 80, saturado
        {'id': 'B', **M.calcular_score(1.0, (19, 20), 10, 'MIXTA', 'MIXTA')},   # 81, saturado no
        {'id': 'C', **M.calcular_score(0.0, (2, 20), 2, 'MIXTA', 'MIXTA')},     # bajo pero con cupo
        {'id': 'D', **M.calcular_score(1.0, (30, 20), 10, 'MIXTA', 'MIXTA')},   # saturado
    ]
    top = M.ordenar_top3(candidatos)
    assert [c['id'] for c in top] == ['B', 'C', 'A']
    assert all(c['factores']['balance_carga'] == 0.0 for c in candidatos if c['cupo_completo'])


def test_todos_saturados_igual_devuelve_top3():
    cands = [{'id': i, **M.calcular_score(1.0, (20, 20), i, 'MIXTA', 'MIXTA')} for i in range(5)]
    top = M.ordenar_top3(cands)
    assert len(top) == 3 and all(c['cupo_completo'] for c in top)
    assert [c['id'] for c in top] == [4, 3, 2]


if __name__ == "__main__":
    for nombre, fn in list(globals().items()):
        if nombre.startswith('test_'):
            fn()
            print(f"  ok  {nombre}")
    print("ALL MATCHING TESTS PASSED [OK]")
