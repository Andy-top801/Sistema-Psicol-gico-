# -*- coding: utf-8 -*-
# ==============================================================================
# MÓDULO: clinica/ia_nlp.py
# CASO DE USO: CU21 / HU-47 — Inferencia de IA para el motivo de consulta.
#
# Secuencia_Corregido_CU21_Clasificacion_IA:
#   CU21-paso 7: consultar_inferencia_nlp(texto_anonimizado)   → modelo Hugging Face
#   CU21-paso 8: evaluar_patrones_riesgo_crisis(score, categoria) → red de seguridad + severidad
#   (el diagrama nombra el modelo 'HF-ClinicalBert'; el que se usa es mDeBERTa-v3 zero-shot multilingüe)
#
# Modelo: clasificación zero-shot por inferencia de lenguaje natural (NLI) con un
# modelo multilingüe pre-entrenado (por defecto MoritzLaurer/mDeBERTa-v3-base-mnli-xnli).
# No se entrena: cada categoría es una hipótesis en español ("Este texto trata sobre X.")
# y el modelo devuelve la probabilidad de que el texto la implique.
#
# Calibración (manage.py evaluar_modelo_ia, 50 casos en español, 2026-11-04):
#   categoría 38/50 (0.76) con UMBRAL_OTRO=0.25; ~1.3 s por intake en CPU (i7-1165G7).
#   El riesgo inferido por zero-shot NO separa bien crisis de casos normales (redacciones que
#   detectan 10/10 crisis marcan además 17-39/40 normales), por eso se usa la hipótesis
#   conservadora (3/10 crisis, 4/40 falsos positivos) y la red de reglas garantiza recall 1.0.
#
# Si el modelo no puede cargarse (sin librerías, sin red en la primera descarga, sin RAM)
# o IA_HABILITADA=0, se usa el motor de reglas y se registra modelo_ia='REGLAS-FALLBACK'.
# Las reglas de crisis SIEMPRE se evalúan: solo pueden subir el riesgo, nunca bajarlo.
# ==============================================================================
import functools
import logging
import re
import threading
import unicodedata

from django.conf import settings

logger = logging.getLogger(__name__)

MODELO_FALLBACK = 'REGLAS-FALLBACK'
MODELO_SIN_TEXTO = 'SIN-TEXTO'

HYPOTHESIS_TEMPLATE = 'Este texto trata sobre {}.'

# Etiqueta en lenguaje natural (hipótesis) → código de categoría (CE_ClasificacionIA)
ETIQUETAS_CATEGORIA = {
    'ansiedad, miedo o pánico': 'ANSIEDAD_FOBIAS',
    'tristeza o depresión': 'DEPRESION_ANIMO',
    'problemas de pareja o familia': 'PAREJA_FAMILIA',
    'problemas de un niño o adolescente': 'INFANTO_JUVENIL',
    'duelo o pérdida de un ser querido': 'DUELO_ADAPTACION',
}
ETIQUETAS_RIESGO = ['ideación suicida o autolesión', 'violencia o abuso']

UMBRAL_OTRO = 0.25      # confianza mínima (azar = 0.20 con 5 categorías); calibrado con evaluar_modelo_ia
UMBRAL_CRISIS = 0.70    # alt [score_severidad >= 0.70 o alerta_crisis == true]
PESO_MALESTAR = 0.69    # el malestar autopercibido solo, nunca alcanza el umbral de crisis
SCORE_REGLA_CRISIS = 0.95


def normalizar(texto: str) -> str:
    """minúsculas y sin tildes, para comparar patrones de forma robusta."""
    sin_tildes = unicodedata.normalize('NFKD', texto or '').encode('ascii', 'ignore').decode('ascii')
    return sin_tildes.lower()


def modelo_configurado() -> str:
    return getattr(settings, 'IA_MODELO_HF', 'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli')


_lock = threading.Lock()


class ClasificadorZeroShotNLI:
    """
    Clasificación zero-shot por NLI (misma técnica que transformers' zero-shot-classification),
    pero evaluando todas las hipótesis en UN solo lote: ~0.4 s por llamada en CPU, frente a
    ~20 s del pipeline estándar, que procesa cada hipótesis por separado.
    Interfaz compatible con el pipeline: (texto, candidate_labels, hypothesis_template, multi_label)
    → {'labels': [...], 'scores': [...]} ordenado de mayor a menor.
    """

    def __init__(self, nombre_modelo: str):
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(nombre_modelo)
        self.model = AutoModelForSequenceClassification.from_pretrained(nombre_modelo).eval()
        etiquetas = {k.lower(): v for k, v in self.model.config.label2id.items()}
        self.id_entailment = etiquetas['entailment']
        self.id_contradiction = etiquetas['contradiction']
        # ponytail: inferencia serializada por proceso (el tokenizer HF "fast" no es seguro entre hilos:
        # "Already borrowed"). ~1.3 s por intake; si hay mucha concurrencia, usar más workers, no hilos.
        self._lock = threading.Lock()

    def __call__(self, texto, candidate_labels, hypothesis_template='{}', multi_label=False):
        labels = list(candidate_labels)
        hipotesis = [hypothesis_template.format(l) for l in labels]
        with self._lock:
            enc = self.tokenizer([texto] * len(labels), hipotesis, return_tensors='pt',
                                 padding=True, truncation='only_first', max_length=512)
            with self.torch.inference_mode():
                logits = self.model(**enc).logits
        if multi_label:   # probabilidad independiente de cada hipótesis: entailment vs contradiction
            pares = logits[:, [self.id_contradiction, self.id_entailment]]
            scores = pares.softmax(dim=1)[:, 1]
        else:             # una sola categoría: softmax de los logits de entailment entre hipótesis
            scores = logits[:, self.id_entailment].softmax(dim=0)
        orden = sorted(zip(labels, scores.tolist()), key=lambda x: x[1], reverse=True)
        return {'labels': [l for l, _ in orden], 'scores': [s for _, s in orden]}


@functools.lru_cache(maxsize=1)
def _cargar_pipeline():
    logger.info("Cargando modelo de IA %s ...", modelo_configurado())
    return ClasificadorZeroShotNLI(modelo_configurado())


def _pipeline():
    """Devuelve el clasificador HF (una sola carga por proceso, protegida contra carga concurrente)."""
    if not getattr(settings, 'IA_HABILITADA', True):
        raise RuntimeError("IA deshabilitada por configuración (IA_HABILITADA=0)")
    with _lock:
        return _cargar_pipeline()


def _inferencia_reglas(texto: str) -> dict:
    from clinica.ia_rules_engine import ClasificadorMotivoConsulta
    t = normalizar(texto)
    scores = {
        cat: sum(1 for p in palabras if normalizar(p) in t)
        for cat, palabras in ClasificadorMotivoConsulta.PATRONES_ESPECIALIDAD.items()
    }
    scores = {c: n for c, n in scores.items() if n}
    if scores:
        categoria = max(scores, key=scores.get)
        confianza = round(scores[categoria] / sum(scores.values()), 3)
    else:
        categoria, confianza = 'OTRO', 0.0
    p_riesgo = SCORE_REGLA_CRISIS if detectar_patrones_crisis(texto) else 0.0
    return {'categoria': categoria, 'confianza': confianza, 'p_riesgo': p_riesgo, 'modelo_ia': MODELO_FALLBACK}


def consultar_inferencia_nlp(texto_anonimizado: str) -> dict:
    """CU21-paso 7: consultar_inferencia_nlp(texto_anonimizado). Devuelve {categoria, confianza, p_riesgo, modelo_ia}."""
    contenido = re.sub(r'\[[^\]]*\]', ' ', texto_anonimizado or '').strip()
    if not re.search(r'\w', contenido):
        return {'categoria': 'OTRO', 'confianza': 0.0, 'p_riesgo': 0.0, 'modelo_ia': MODELO_SIN_TEXTO}

    try:
        # CU21-paso 7: el modelo HF evalúa 5 hipótesis de categoría (una sola etiqueta) y 2 de riesgo (multi-etiqueta)
        clasificador = _pipeline()
        res_cat = clasificador(texto_anonimizado, list(ETIQUETAS_CATEGORIA),
                               hypothesis_template=HYPOTHESIS_TEMPLATE)
        res_riesgo = clasificador(texto_anonimizado, ETIQUETAS_RIESGO,
                                  hypothesis_template=HYPOTHESIS_TEMPLATE, multi_label=True)
    except Exception as exc:  # sin librería / sin red / sin memoria → respaldo por reglas
        logger.warning("Inferencia HF no disponible, se usa respaldo por reglas: %s", exc)
        return _inferencia_reglas(texto_anonimizado)

    confianza = round(float(res_cat['scores'][0]), 3)
    categoria = ETIQUETAS_CATEGORIA[res_cat['labels'][0]] if confianza >= UMBRAL_OTRO else 'OTRO'
    return {
        'categoria': categoria,
        'confianza': confianza,
        'p_riesgo': round(float(max(res_riesgo['scores'])), 3),
        'modelo_ia': modelo_configurado(),
    }


def detectar_patrones_crisis(texto: str) -> list:
    from clinica.ia_rules_engine import ClasificadorMotivoConsulta
    t = normalizar(texto)
    return [p for p in ClasificadorMotivoConsulta.PATRONES_CRISIS if normalizar(p) in t]


def _nivel_y_puntaje(score: float):
    if score >= UMBRAL_CRISIS:
        return 'CRITICA', 5
    if score >= 0.55:
        return 'ALTA', 4
    if score >= 0.35:
        return 'MODERADA', 3
    return 'BAJA', (2 if score >= 0.20 else 1)


def evaluar_patrones_riesgo_crisis(score: float, categoria: str, texto: str, escala_malestar: int) -> dict:
    """
    CU21-paso 8: evaluar_patrones_riesgo_crisis(score, categoria).
    Combina el riesgo del modelo, el malestar autopercibido (1-5) y la red de seguridad por reglas.
    """
    escala = min(5, max(1, int(escala_malestar or 1)))
    reglas = detectar_patrones_crisis(texto)
    score_sev = max(float(score or 0.0), (escala - 1) / 4 * PESO_MALESTAR)
    if reglas:
        score_sev = max(score_sev, SCORE_REGLA_CRISIS)
    score_sev = round(min(1.0, score_sev), 3)
    nivel, puntaje = _nivel_y_puntaje(score_sev)
    return {
        'score_severidad': score_sev,
        'puntaje_severidad': puntaje,
        'nivel_severidad': nivel,
        'alerta_crisis': bool(reglas) or score_sev >= UMBRAL_CRISIS,
        'palabras_clave': reglas,
    }


def precargar_en_segundo_plano():
    """Carga el modelo al iniciar el worker para que el primer intake no espere la carga."""
    try:
        _pipeline()
        logger.info("Modelo de IA %s precargado.", modelo_configurado())
    except Exception as exc:
        logger.warning("No se pudo precargar el modelo de IA (se usará respaldo por reglas): %s", exc)
