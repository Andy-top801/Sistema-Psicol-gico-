# -*- coding: utf-8 -*-
# CU21 / HU-47 — Task 2b: evaluación del modelo de IA con casos escritos a mano en español.
#   python manage.py evaluar_modelo_ia [--detalle]
# Criterio de aceptación: recall de crisis = 1.0 (no se pierde ninguna crisis) y
# exactitud de categoría >= 0.70. Los falsos positivos de crisis se toleran (los revisa un humano).
import json
import time
from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from clinica import ia_nlp

CASOS = Path(__file__).resolve().parents[2] / 'ia_eval' / 'casos_evaluacion.json'
EXACTITUD_MINIMA = 0.70


class Command(BaseCommand):
    help = "Evalúa la clasificación IA (categoría y crisis) contra el set de casos en español."

    def add_arguments(self, parser):
        parser.add_argument('--detalle', action='store_true', help="Imprime cada caso fallido.")

    def handle(self, *args, **opts):
        casos = json.loads(CASOS.read_text(encoding='utf-8'))
        aciertos, conf, modelos = 0, Counter(), Counter()
        crisis_tp = crisis_fn = crisis_fp = crisis_ml_tp = 0
        t0 = time.perf_counter()

        for c in casos:
            inf = ia_nlp.consultar_inferencia_nlp(c['texto'])
            ev = ia_nlp.evaluar_patrones_riesgo_crisis(inf['p_riesgo'], inf['categoria'], c['texto'], 3)
            modelos[inf['modelo_ia']] += 1
            ok_cat = inf['categoria'] == c['categoria']
            aciertos += ok_cat
            conf[(c['categoria'], inf['categoria'])] += 1
            if c['crisis']:
                crisis_tp += ev['alerta_crisis']
                crisis_fn += not ev['alerta_crisis']
                crisis_ml_tp += inf['p_riesgo'] >= ia_nlp.UMBRAL_CRISIS
            else:
                crisis_fp += ev['alerta_crisis']
            if opts['detalle'] and (not ok_cat or ev['alerta_crisis'] != c['crisis']):
                self.stdout.write(f"  ✗ esperado={c['categoria']}/crisis={c['crisis']} "
                                  f"obtenido={inf['categoria']}({inf['confianza']})/crisis={ev['alerta_crisis']} "
                                  f"p_riesgo={inf['p_riesgo']} reglas={ev['palabras_clave']} :: {c['texto'][:70]}")

        n, n_crisis = len(casos), crisis_tp + crisis_fn
        exactitud = aciertos / n
        recall = crisis_tp / n_crisis if n_crisis else 1.0
        dt = time.perf_counter() - t0

        self.stdout.write(f"\nModelo(s): {dict(modelos)}   casos: {n}   tiempo: {dt:.1f}s ({dt / n:.2f}s/caso)")
        self.stdout.write(f"Exactitud de categoría: {aciertos}/{n} = {exactitud:.2f}")
        categorias = sorted({c['categoria'] for c in casos})
        for esperado in categorias:
            fila = {k[1]: v for k, v in conf.items() if k[0] == esperado}
            self.stdout.write(f"  {esperado:<18} → {fila}")
        self.stdout.write(f"Crisis: recall={recall:.2f} ({crisis_tp}/{n_crisis})  falsos positivos={crisis_fp}  "
                          f"detectadas solo por el modelo={crisis_ml_tp}/{n_crisis}")

        if recall < 1.0 or exactitud < EXACTITUD_MINIMA:
            raise CommandError(f"Evaluación NO superada (recall crisis {recall:.2f} < 1.0 "
                               f"o exactitud {exactitud:.2f} < {EXACTITUD_MINIMA}).")
        self.stdout.write(self.style.SUCCESS("Evaluación superada."))
