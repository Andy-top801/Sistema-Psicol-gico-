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
    Pipeline de IA asistiva para la clasificación de motivos de consulta (CU21 / HU-47).
    Aplica sanitización estricta de PII, categorización temática en 5 áreas y detección inmediata de crisis vital.
    """

    PATRONES_ESPECIALIDAD = {
        'ANSIEDAD_FOBIAS': [
            'ansiedad', 'pánico', 'panico', 'angustia', 'fobia', 'miedo',
            'taquicardia', 'ahogo', 'obsesi', 'crisis de panico', 'ataque', 'palpitaciones', 'temblor', 'nervios'
        ],
        'DEPRESION_ANIMO': [
            'depresion', 'depresión', 'tristeza', 'desánimo', 'desanimo', 'llanto',
            'vacío', 'vacio', 'culpa', 'desesperanza', 'sin ganas', 'desmotiv', 'insomnio', 'cansancio'
        ],
        'PAREJA_FAMILIA': [
            'pareja', 'esposo', 'esposa', 'novio', 'novia', 'matrimonio',
            'infidelidad', 'divorcio', 'comunicación', 'comunicacion', 'discusion', 'familia', 'familiar', 'convivencia'
        ],
        'INFANTO_JUVENIL': [
            'hijo', 'hija', 'niño', 'niña', 'colegio', 'berrinche',
            'adolescente', 'conducta', 'escuela', 'escolar', 'crianza', 'hiperactiv'
        ],
        'DUELO_ADAPTACION': [
            'duelo', 'fallecimiento', 'muerte', 'pérdida', 'perdida',
            'separación', 'separacion', 'luto', 'fallecio', 'perdi', 'mudanza', 'adaptacion'
        ],
    }

    PATRONES_CRISIS = [
        'suicid', 'morir', 'acabar con todo', 'quitarme la vida',
        'hacerme daño', 'hacerme dano', 'no quiero vivir', 'autolesion', 'cortarme',
        'no despertar', 'matar', 'sin sentido', 'desaparecer para siempre'
    ]

    @classmethod
    def sanitizar_pii(cls, texto: str) -> str:
        """Elimina números de teléfono, correos y carnets para anonimizar los datos."""
        if not texto:
            return ""
        texto = re.sub(r'(\+?591\s?)?[67]\d{7}', '[TELÉFONO ANONIMIZADO]', texto)
        texto = re.sub(r'\b\d{6,9}\b', '[DOCUMENTO ANONIMIZADO]', texto)
        texto = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL ANONIMIZADO]', texto)
        return texto

    @classmethod
    def clasificar(cls, motivo: str, sintomas: str, urgencia_percibida: int = 3) -> Dict[str, Any]:
        motivo_limpio = cls.sanitizar_pii(motivo or "")
        sintomas_limpio = cls.sanitizar_pii(sintomas or "")
        texto_analisis = f"{motivo_limpio} {sintomas_limpio}".lower()

        # Detección inmediata de banderas de crisis
        palabras_crisis = [p for p in cls.PATRONES_CRISIS if p in texto_analisis]
        es_crisis = len(palabras_crisis) > 0

        # Ponderación de categorías temáticas
        scores = {}
        palabras_detectadas = []
        for esp, palabras in cls.PATRONES_ESPECIALIDAD.items():
            coincidencias = [p for p in palabras if p in texto_analisis]
            if coincidencias:
                scores[esp] = len(coincidencias)
                palabras_detectadas.extend(coincidencias)

        if palabras_crisis:
            palabras_detectadas.extend(palabras_crisis)

        categoria_principal = max(scores, key=scores.get) if scores else 'ANSIEDAD_FOBIAS'
        total_coincidencias = sum(scores.values()) or 1
        confianza = min(0.98, round((scores.get(categoria_principal, 1) / total_coincidencias) * 0.7 + 0.25, 3))

        # Nivel de severidad y bandera de crisis
        if es_crisis or urgencia_percibida == 5:
            severidad = 'CRITICA'
            alerta_crisis = True
        elif urgencia_percibida >= 4 or len(palabras_detectadas) >= 3:
            severidad = 'SEVERO'
            alerta_crisis = False
        elif urgencia_percibida == 3:
            severidad = 'MODERADO'
            alerta_crisis = False
        else:
            severidad = 'LEVE'
            alerta_crisis = False

        explicacion = (
            f"Clasificación automática asistiva: {categoria_principal} (Confianza: {confianza*100:.1f}%). "
            f"Nivel de severidad asignado: {severidad}. "
        )
        if alerta_crisis:
            explicacion += f"ALERTA DE SEGURIDAD VITAL: Se detectaron patrones de crisis o riesgo autolítico ({', '.join(palabras_crisis)}). Protocolo de contención activado."
        else:
            explicacion += "Caso estándar derivado a triaje asistido para emparejamiento con psicólogo."

        # Hash inmutable SHA-256
        hash_payload = f"{texto_analisis}:{categoria_principal}:{severidad}:{alerta_crisis}"
        hash_sha256 = hashlib.sha256(hash_payload.encode('utf-8')).hexdigest()

        return {
            'categoria_principal': categoria_principal,
            'confianza_score': confianza,
            'nivel_severidad': severidad,
            'alerta_crisis': alerta_crisis,
            'palabras_clave_detectadas': list(set(palabras_detectadas)),
            'explicacion_heuristica': explicacion,
            'hash_trazabilidad_sha256': hash_sha256
        }


# ==============================================================================
# SPRINT 3: ALGORITMO MULTIVARIABLE DE EMPAREJAMIENTO DE PSICÓLOGOS (CU22)
# ==============================================================================
class MatchingPsicologoService:
    """
    Algoritmo de recomendación multivariable de psicólogos (CU22 / Tarea SP3-77).
    Calcula un score de compatibilidad normalizado [0, 100] aplicando:
    - Especialidad requerida (40%)
    - Disponibilidad horaria (30%)
    - Balanceo de carga de pacientes (20%)
    - Compatibilidad de modalidad (10%)
    """

    @classmethod
    def sugerir_psicologos(cls, especialidad_req: str, modalidad_req: str, psicologos_queryset) -> List[Dict[str, Any]]:
        candidatos = []

        for p in psicologos_queryset:
            usuario = getattr(p, 'usuario', None)
            if usuario and not getattr(usuario, 'is_active', True):
                continue

            # 1. Afinidad de Especialidad (Peso: 40%)
            score_esp = 10.0  # Base
            tokens_req = [t for t in especialidad_req.lower().replace('_', ' ').split() if len(t) > 3]
            if hasattr(p, 'especialidades'):
                esps = p.especialidades.all() if hasattr(p.especialidades, 'all') else []
                for esp in esps:
                    nom = getattr(esp, 'nombre', '').lower()
                    if any(t in nom for t in tokens_req) or especialidad_req.lower() in nom:
                        score_esp = 40.0
                        break

            # 2. Disponibilidad de Horarios (Peso: 30%)
            bloques_disponibles = 0
            if hasattr(p, 'horarios_disponibilidad'):
                if hasattr(p.horarios_disponibilidad, 'filter'):
                    bloques_disponibles = p.horarios_disponibilidad.filter(activo=True).count()
                elif hasattr(p.horarios_disponibilidad, 'count'):
                    bloques_disponibles = p.horarios_disponibilidad.count()
            elif hasattr(p, 'disponibilidades'):
                count = p.disponibilidades.filter(activo=True).count()
                bloques_disponibles = count if count > 0 else 6
            else:
                bloques_disponibles = 6

            score_disp = min(30.0, max(0, bloques_disponibles) * 3.0)

            # 3. Balanceo de Carga de Pacientes (Peso: 20%)
            pacientes_activos = 0
            if hasattr(p, 'pacientes_asignados'):
                if hasattr(p.pacientes_asignados, 'filter'):
                    pacientes_activos = p.pacientes_asignados.filter(activo=True).count()
                elif hasattr(p.pacientes_asignados, 'count'):
                    pacientes_activos = p.pacientes_asignados.count()
            max_capacidad = getattr(p, 'carga_maxima_pacientes', 20) or 20
            ratio_ocupacion = pacientes_activos / max_capacidad if max_capacidad > 0 else 1.0

            if ratio_ocupacion >= 1.0:
                score_carga = 0.0  # Saturado al 100%
            else:
                score_carga = max(0.0, (1.0 - ratio_ocupacion) * 20.0)

            # 4. Compatibilidad de Modalidad (Peso: 10%)
            mod_psico = getattr(p, 'modalidad', 'MIXTA')
            if mod_psico in ['MIXTA', modalidad_req] or not modalidad_req:
                score_mod = 10.0
            else:
                score_mod = 0.0

            score_total = round(score_esp + score_disp + score_carga + score_mod, 1)

            nombre_completo = ""
            if usuario:
                nombre_completo = getattr(usuario, 'get_full_name', lambda: "")() or f"{getattr(usuario, 'first_name', '')} {getattr(usuario, 'last_name', '')}".strip() or getattr(usuario, 'email', '')

            candidatos.append({
                'psicologo_id': str(p.id),
                'nombre_completo': nombre_completo,
                'psicologo_nombre': nombre_completo,
                'numero_colegiado': getattr(p, 'numero_colegiado', ''),
                'score_compatibilidad': score_total,
                'factores': {
                    'afinidad_especialidad': score_esp,
                    'disponibilidad_horaria': score_disp,
                    'balance_carga': score_carga,
                    'modalidad': score_mod,
                },
                'pacientes_activos': pacientes_activos,
                'capacidad_maxima': max_capacidad
            })

        candidatos.sort(key=lambda x: x['score_compatibilidad'], reverse=True)
        return candidatos[:3]
