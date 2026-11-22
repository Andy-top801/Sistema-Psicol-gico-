# ==============================================================================
# MÓDULO: clinica/ia_rules_engine.py
# CASO DE USO: HU-35 (Asistente Ético de Preconsulta) / Tarea SP2-54 (Motor Romero)
# DESCRIPCIÓN: Pasarela segura y motor heurístico de reglas clínicas para
#              preconsulta psicológica asistiva con estricta supervisión humana,
#              anonimización de PII, verificación de consentimiento y explicabilidad.
# ==============================================================================
import re
import hashlib
from typing import Dict, Any, List, Tuple
from django.utils import timezone

class PreconsultaRulesEngine:
    """
    Motor heurístico de reglas clínicas desarrollado bajo las directrices del Sprint 2.
    Evalúa respuestas de pre-consulta para generar un borrador neutral de preparación
    para el terapeuta sin escribir diagnósticos en la historia clínica.
    """

    @staticmethod
    def sanitizar_pii(texto: str) -> str:
        """Elimina correos, teléfonos y números de carnet para proteger datos personales."""
        if not texto:
            return ""
        # Teléfonos bolivianos (ej. 71234567, +591 71234567)
        texto = re.sub(r'(\+?591\s?)?[67]\d{7}', '[TELÉFONO ANONIMIZADO]', texto)
        # Cédulas de identidad (6 a 9 dígitos aislados)
        texto = re.sub(r'\b\d{6,9}\b', '[DOCUMENTO ANONIMIZADO]', texto)
        # Correos electrónicos
        texto = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL ANONIMIZADO]', texto)
        return texto

    @classmethod
    def evaluar_preconsulta(cls, respuesta) -> Dict[str, Any]:
        """
        Ejecuta el pipeline asistivo:
        1. Sanitización de PII
        2. Evaluación de reglas clínicas
        3. Formulación de resumen estructurado neutral
        4. Sellado con hash criptográfico SHA-256
        """
        motivo = cls.sanitizar_pii(respuesta.motivo_consulta or "")
        sintomas = cls.sanitizar_pii(respuesta.sintomas_principales or "")
        urgencia = int(respuesta.nivel_urgencia_percibido or 1)
        medicos = cls.sanitizar_pii(respuesta.antecedentes_medicos or "")
        psiquiatricos = cls.sanitizar_pii(respuesta.antecedentes_psiquiatricos or "")
        medicacion = cls.sanitizar_pii(respuesta.medicacion_actual or "")

        texto_combinado = f"{motivo} {sintomas} {medicos} {psiquiatricos} {medicacion}".lower()

        reglas: List[Dict[str, str]] = []
        prioridad = "BAJA"
        puntaje_severidad = urgencia  # Base 1-5

        # Regla 1: Nivel de malestar subjetivo reportado
        if urgencia >= 4:
            puntaje_severidad += 3
            reglas.append({
                "codigo": "REG-MALESTAR-ALTO",
                "criterio": f"Escala de malestar percibido igual a {urgencia}/5",
                "explicacion": "El paciente auto-reporta un nivel de perturbación emocional alto que amerita atención prioritaria en agenda."
            })
        elif urgencia == 3:
            reglas.append({
                "codigo": "REG-MALESTAR-MODERADO",
                "criterio": "Escala de malestar percibido en nivel 3/5",
                "explicacion": "Malestar emocional moderado en actividades cotidianas."
            })

        # Regla 2: Indicadores de riesgo autolítico o crisis severa
        palabras_riesgo = ["suicid", "morir", "acabar con todo", "hacerme daño", "quitarme la vida", "no quiero vivir", "sin sentido"]
        for p in palabras_riesgo:
            if p in texto_combinado:
                puntaje_severidad += 6
                reglas.append({
                    "codigo": "REG-ALERTA-CRISIS",
                    "criterio": f"Término de riesgo detectado: '{p}'",
                    "explicacion": "Presencia de ideación o lenguaje de desamparo agudo. Requiere evaluación directa presencial y protocolo de contención."
                })
                break

        # Regla 3: Crisis de pánico / sintomatología somática aguda
        palabras_panico = ["pánico", "panico", "taquicardia", "no puedo respirar", "ahogo", "asfixia", "miedo a morir"]
        for p in palabras_panico:
            if p in texto_combinado:
                puntaje_severidad += 2
                reglas.append({
                    "codigo": "REG-ANSIEDAD-SOMATICA",
                    "criterio": f"Signo autonómico reportado: '{p}'",
                    "explicacion": "Posible compromiso somático por reactividad fisiológica intensa tipo crisis de angustia."
                })
                break

        # Regla 4: Antecedente psicofarmacológico o psiquiátrico previo
        if medicacion or psiquiatricos:
            palabras_farmaco = ["clonazepam", "sertralina", "fluoxetina", "quetiapina", "alprazolam", "antidepresivo", "ansiolitico", "pastilla"]
            tiene_farmaco = any(f in texto_combinado for f in palabras_farmaco)
            if tiene_farmaco or psiquiatricos:
                puntaje_severidad += 2
                reglas.append({
                    "codigo": "REG-SOPORTE-FARMACO",
                    "criterio": "Mención de tratamiento psiquiátrico o psicofármacos activos",
                    "explicacion": "Sugiere seguimiento coordinado y verificación de adherencia terapéutica o interconsulta médica."
                })

        # Regla 5: Alteración del sueño / insomnio severo
        if any(s in texto_combinado for s in ["insomnio", "no duermo", "desvelo", "pesadillas"]):
            reglas.append({
                "codigo": "REG-ALTERACION-SUENO",
                "criterio": "Reporte de insomnio o trastorno del patrón de descanso",
                "explicacion": "Factor de vulnerabilidad neurobiológica que intensifica la labilidad afectiva."
            })

        # Determinación de nivel de prioridad sugerido
        if puntaje_severidad >= 9:
            prioridad = "CRITICA"
        elif puntaje_severidad >= 6:
            prioridad = "ALTA"
        elif puntaje_severidad >= 4:
            prioridad = "MEDIA"
        else:
            prioridad = "BAJA"

        # Construcción del resumen neutral
        sintesis_motivo = motivo.strip() or "No especificado detalladamente."
        resumen = (
            f"Paciente consulta principalmente por: {sintesis_motivo}.\n"
            f"Sintomatología descrita: {sintomas or 'Sin síntomas adicionales detallados'}.\n"
            f"Nivel de malestar emocional subjetivo: {urgencia}/5.\n"
            f"Antecedentes: Médicos ({medicos or 'Ninguno reportado'}), "
            f"Psiquiátricos ({psiquiatricos or 'Sin antecedentes psiquiátricos previos'}).\n"
            f"Medicación actual: {medicacion or 'No consume medicación psicotrópica'}.\n"
            f"Priorización sugerida por el motor: Nivel {prioridad}."
        )

        # Hash SHA-256 para integridad de la auditoría
        payload_raw = f"{respuesta.id}:{prioridad}:{texto_combinado}"
        hash_prompt = hashlib.sha256(payload_raw.encode("utf-8")).hexdigest()

        return {
            "prioridad_sugerida": prioridad,
            "resumen_generado": resumen,
            "reglas_aplicadas": reglas,
            "puntaje_severidad": puntaje_severidad,
            "hash_prompt": hash_prompt,
            "diagnostico_automatico_generado": False,  # DoD: NUNCA se guardan diagnósticos de forma automática
            "etiqueta_obligatoria": "Borrador IA — Requiere Revisión Profesional",
            "fecha_analisis": timezone.now().isoformat()
        }


# ==============================================================================
# SPRINT 3: MOTOR DE CLASIFICACIÓN ASISTIDA POR IA Y DETECCIÓN DE CRISIS (CU21)
# ==============================================================================
class ClasificadorMotivoConsulta:
    """
    Catálogos de patrones para CU21 / HU-47 (respaldo por reglas y red de seguridad de crisis).
    La inferencia principal la hace el modelo Hugging Face en clinica/ia_nlp.py.
    Los patrones se comparan en minúsculas y sin tildes (ia_nlp.normalizar).
    """

    PATRONES_ESPECIALIDAD = {
        'ANSIEDAD_FOBIAS': [
            'ansiedad', 'panico', 'angustia', 'fobia', 'miedo', 'taquicardia', 'ahogo',
            'obsesi', 'palpitaciones', 'temblor', 'nervios', 'preocupacion constante'
        ],
        'DEPRESION_ANIMO': [
            'depresion', 'tristeza', 'desanimo', 'llanto', 'lloro', 'vacio', 'culpa',
            'desesperanza', 'sin ganas', 'desmotiv', 'insomnio', 'cansancio'
        ],
        'PAREJA_FAMILIA': [
            'pareja', 'esposo', 'esposa', 'novio', 'novia', 'matrimonio', 'infidelidad',
            'divorcio', 'discusion', 'discuto', 'familia', 'familiar', 'convivencia'
        ],
        'INFANTO_JUVENIL': [
            'hijo', 'hija', 'nino', 'nina', 'colegio', 'berrinche', 'adolescente',
            'escuela', 'escolar', 'crianza', 'hiperactiv'
        ],
        'DUELO_ADAPTACION': [
            'duelo', 'fallecimiento', 'fallecio', 'murio', 'perdida', 'perdi a', 'separacion',
            'luto', 'mudanza', 'adaptacion'
        ],
    }

    # Ideación autolítica o violencia (HU-47). Frases, no palabras sueltas, para no marcar
    # "me muero de risa" o "matar el tiempo". Solo pueden SUBIR el riesgo inferido por el modelo.
    PATRONES_CRISIS = [
        'suicid', 'quiero morir', 'quisiera morir', 'deseo morir', 'ganas de morir', 'morirme',
        'acabar con todo', 'acabar con mi vida', 'quitarme la vida', 'matarme', 'hacerme dano',
        'no quiero vivir', 'no vale la pena vivir', 'autolesi', 'cortarme', 'no despertar',
        'desaparecer para siempre', 'sentido a seguir viviendo', 'sentido a vivir', 'lastimarme',
        # autolesión en curso
        'cortandome', 'me he cortado', 'he estado cortando', 'me estado cortando', 'me corto los', 'me corto las',
        'cortes en los brazos', 'cortes en las munecas',
        # ideación pasiva / sentirse una carga
        'mejor sin mi', 'mejor si yo no estuviera', 'ser una carga para', 'no quiero despertar',
        'me golpea', 'me pega', 'me pegan', 'me golpean', 'abuso', 'violencia', 'violacion',
        'amenaza de muerte', 'me amenaza',
    ]


# ==============================================================================
# SPRINT 3: ALGORITMO MULTIVARIABLE DE EMPAREJAMIENTO DE PSICÓLOGOS (CU22)
# ==============================================================================
class MatchingPsicologoService:
    """
    CU22 / HU-48 — Algoritmo multivariable de emparejamiento (fórmula transparente, sin ML):
        Score = 0.4×Afinidad + 0.3×Disponibilidad + 0.2×BalanceCarga + 0.1×Modalidad
    Cada factor está en [0, 1]; el score se expresa en [0, 100] con un decimal.
    """

    PESOS = {'afinidad': 0.4, 'disponibilidad': 0.3, 'balance_carga': 0.2, 'modalidad': 0.1}
    BLOQUES_PLENA_DISPONIBILIDAD = 40  # bloques de atención semanales ≈ jornada completa (8 × 5 días)

    # Categoría del triaje IA → términos que deben aparecer en nombre/descripción de la especialidad
    AREAS_POR_CATEGORIA = {
        'ANSIEDAD_FOBIAS': ['ansiedad', 'cognitivo'],
        'DEPRESION_ANIMO': ['animo', 'depres'],
        'PAREJA_FAMILIA': ['pareja', 'familiar'],
        'INFANTO_JUVENIL': ['infan', 'adolesc'],
        'DUELO_ADAPTACION': ['duelo', 'paliativ'],
        'OTRO': [],
    }

    @classmethod
    def afinidad(cls, categoria: str, especialidades) -> float:
        """1.0 si alguna especialidad del psicólogo cubre el área del triaje; si no, 0.0."""
        from clinica.ia_nlp import normalizar
        terminos = cls.AREAS_POR_CATEGORIA.get(categoria, [])
        for esp in especialidades:
            texto = normalizar(f"{esp.obtener_nombre()} {getattr(esp, 'descripcion', '') or ''}")
            if any(t in texto for t in terminos):
                return 1.0
        return 0.0

    @classmethod
    def calcular_score(cls, afinidad: float, carga: tuple, disponibilidad: int,
                       modalidad_psico: str, modalidad_pac: str) -> dict:
        """CU22-paso 15: calcular_score(afinidad, carga, disponibilidad) — fórmula ponderada de HU-48 (no es ML)."""
        carga_actual, cupo = carga
        cupo_completo = cupo <= 0 or carga_actual >= cupo
        factores = {
            'afinidad': float(afinidad),
            'disponibilidad': round(min(1.0, max(0, disponibilidad) / cls.BLOQUES_PLENA_DISPONIBILIDAD), 3),
            'balance_carga': 0.0 if cupo_completo else round(1 - carga_actual / cupo, 3),
            'modalidad': 1.0 if ('MIXTA' in (modalidad_psico, modalidad_pac) or modalidad_psico == modalidad_pac) else 0.0,
        }
        score = round(100 * sum(cls.PESOS[k] * v for k, v in factores.items()), 1)
        return {'score': score, 'factores': factores, 'cupo_completo': cupo_completo}

    @staticmethod
    def ordenar_top3(candidatos: list) -> list:
        """HU-48 (b): los profesionales con cupo completo quedan detrás de cualquiera con cupo."""
        return sorted(candidatos, key=lambda c: (c['cupo_completo'], -c['score']))[:3]
