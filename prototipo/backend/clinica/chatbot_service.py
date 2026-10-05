# ==============================================================================
# MÓDULO: clinica/chatbot_service.py
# CASO DE USO: CU20 (HU-36) Chatbot de Orientación Clínica con Detección de Riesgo y Crisis
# INTEGRACIÓN: API Externa Hugging Face (https://antidino-iacupficct.hf.space)
#              + Motor de Salvaguarda Ética y Reglas Institucionales (Fallback)
# ==============================================================================
import os
import re
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from django.utils import timezone

logger = logging.getLogger(__name__)

class ChatbotEngine:
    """
    Motor conversacional Full-Stack para orientación psicológica.
    Integra la API de Inteligencia Artificial desplegada en Hugging Face Space
    con detección de riesgo vital, protocolo de contención de crisis (800-11-3040 / 911),
    memoria conversacional y fallback resiliente de alta disponibilidad.
    """

    HF_API_URL = os.environ.get("CHATBOT_API_URL", "https://antidino-iacupficct.hf.space/api/v1/chatbot/mensaje/")
    TIMEOUT_SECONDS = 15

    PALABRAS_CRISIS = [
        r'\bsuicid',
        r'\bmatar(me)?\b',
        r'\bmorir(me)?\b',
        r'\bquitarme la vida\b',
        r'\bhacerme da[ñn]o\b',
        r'\bcortar(me)?\b',
        r'\bno quiero vivir\b',
        r'\bdesesperad[oa]\b',
        r'\bno aguanto m[aá]s\b',
        r'\bcrisis de p[aá]nico\b',
        r'\bataque de p[aá]nico\b',
        r'\bahogo\b',
        r'\basfixia\b',
        r'\bterminar con todo\b',
    ]

    INTENCIONES = [
        {
            "nombre": "HUMANO",
            "regex": [r'\bhumano\b', r'\boperador\b', r'\basesor\b', r'\bpersona\b', r'\brecepcion(ista)?\b', r'\bsecretaria\b', r'\bhablar con alguien\b'],
            "respuesta": "Entendido. He transferido tu conversación a la recepción en turno del centro. Un operador humano te asistirá en este mismo canal para atender tu consulta personalizada.",
            "botones": [
                {"etiqueta": "Esperar Operador", "accion": "ESPERAR_OPERADOR"},
                {"etiqueta": "Consultar Aranceles", "accion": "CONSULTAR_ARANCELES"},
                {"etiqueta": "Agendar Cita", "accion": "AGENDAR_CITA"}
            ],
            "escalar": True
        },
        {
            "nombre": "AGENDAR_CITA",
            "regex": [r'\bcita\b', r'\bagendar\b', r'\breservar\b', r'\bhora\b', r'\bturno\b', r'\bdisponib', r'\bcalendario\b'],
            "respuesta": "Para agendar tu consulta psicológica en SIGEPSI:\n1. Ingresa al módulo 'Agenda y Citas'.\n2. Elige el profesional de tu preferencia y modalidad (Presencial o Teleconsulta virtual cifrada WebRTC).\n3. Selecciona tu día y franja horaria preferida.\n4. Si es tu primera sesión, recuerda completar el Cuestionario Pre-Consulta (Intake) antes de la cita.",
            "botones": [
                {"etiqueta": "Agendar Cita", "accion": "AGENDAR_CITA"},
                {"etiqueta": "Formulario Previo (Intake)", "accion": "IR_INTAKE"},
                {"etiqueta": "Aranceles y Modalidades", "accion": "CONSULTAR_ARANCELES"},
                {"etiqueta": "Hablar con Recepción", "accion": "SOLICITAR_HUMANO"}
            ],
            "escalar": False
        },
        {
            "nombre": "ARANCELES",
            "regex": [r'\bprecio\b', r'\bcosto\b', r'\barancel\b', r'\btarifa\b', r'\bcuanto cuesta\b', r'\bpagar\b', r'\bpago\b', r'\bdescuento\b'],
            "respuesta": "Los aranceles de atención clínica institucional en el centro son:\n• Psicoterapia Individual Presencial: 150 - 180 BOB por sesión.\n• Teleconsulta Online (WebRTC): 140 - 160 BOB por sesión.\n• Evaluación Diagnóstica y Psicométrica: 200 - 220 BOB.\nDispones de pago por QR electrónico, tarjeta o en caja física.",
            "botones": [
                {"etiqueta": "Agendar Cita", "accion": "AGENDAR_CITA"},
                {"etiqueta": "Llenar Formulario Previo", "accion": "IR_INTAKE"},
                {"etiqueta": "Hablar con Asesor Humano", "accion": "SOLICITAR_HUMANO"}
            ],
            "escalar": False
        },
        {
            "nombre": "INTAKE",
            "regex": [r'\bformulario\b', r'\bintake\b', r'\bpreconsulta\b', r'\bpreguntas\b', r'\bcuestionario\b', r'\bantes de la sesion\b'],
            "respuesta": "El Formulario Pre-Consulta (Intake Digital) permite a tu terapeuta conocer el motivo de tu consulta, malestar percibido (1 a 5) y antecedentes antes de tu primera sesión:\n• Puedes completarlo en 3 a 5 minutos en el menú 'Pre-Consulta (Intake)'.\n• Todas tus respuestas son confidenciales y resguardadas bajo secreto profesional médico.\n• Si tu cita es en menos de 24 horas, te recomendamos completarlo hoy mismo.",
            "botones": [
                {"etiqueta": "Ir a Formulario Previo", "accion": "IR_INTAKE"},
                {"etiqueta": "Agendar Cita", "accion": "AGENDAR_CITA"},
                {"etiqueta": "Hablar con Asesor Humano", "accion": "SOLICITAR_HUMANO"}
            ],
            "escalar": False
        },
        {
            "nombre": "CONVERSACION_CASUAL",
            "regex": [r'\bhola\b', r'\bbuen[oa]s d[ií]as\b', r'\btardes\b', r'\bnoches\b', r'\bsaludos\b', r'\binicio\b'],
            "respuesta": "¡Hola! Bienvenido(a) al Asistente de Orientación Clínica de SIGEPSI. Estoy aquí para acompañarte y resolver tus dudas sobre citas, aranceles y formularios clínicos. ¿En qué te puedo orientar hoy?",
            "botones": [
                {"etiqueta": "Agendar Cita", "accion": "AGENDAR_CITA"},
                {"etiqueta": "Aranceles y Modalidades", "accion": "CONSULTAR_ARANCELES"},
                {"etiqueta": "Formulario Previo (Intake)", "accion": "IR_INTAKE"},
                {"etiqueta": "Hablar con Asesor Humano", "accion": "SOLICITAR_HUMANO"}
            ],
            "escalar": False
        }
    ]

    @classmethod
    def detectar_crisis(cls, texto: str) -> bool:
        texto_lower = texto.lower()
        return any(re.search(patron, texto_lower) for patron in cls.PALABRAS_CRISIS)

    @classmethod
    def consultar_huggingface(
        cls, 
        session_id: str, 
        texto: str, 
        historial: Optional[List[Dict[str, str]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Envía la petición a la API del Chatbot en Hugging Face Space.
        Maneja errores y timeout de conexión.
        """
        payload = {
            "session_id": session_id or "sigepsi-session",
            "mensaje": texto,
            "historial": historial or []
        }
        
        try:
            req_data = json.dumps(payload).encode('utf-8')
            request = urllib.request.Request(
                cls.HF_API_URL,
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "SIGEPSI-Backend-Client/2.0"
                }
            )
            with urllib.request.urlopen(request, timeout=cls.TIMEOUT_SECONDS) as response:
                if response.status == 200:
                    raw_body = response.read().decode('utf-8')
                    parsed = json.loads(raw_body)
                    if isinstance(parsed, dict) and "respuesta" in parsed:
                        return parsed
        except urllib.error.URLError as e:
            logger.warning(f"Error conectando con API Chatbot Hugging Face: {e}")
        except Exception as ex:
            logger.warning(f"Excepción en cliente Hugging Face Chatbot: {ex}")
        
        return None

    @classmethod
    def procesar_mensaje_local(cls, texto_usuario: str, session_id: str = "") -> Dict[str, Any]:
        """
        Motor de fallback local basado en reglas de salvaguarda ética y FAQ institucional.
        Garantiza respuesta instantánea (<100ms) si la API externa no está disponible.
        """
        texto_limpio = texto_usuario.strip()
        ts_actual = timezone.now().isoformat()

        # 1. PROTOCOLO DE PELIGRO / CRISIS (Crítico)
        if cls.detectar_crisis(texto_limpio):
            return {
                "session_id": session_id,
                "remitente": "BOT",
                "respuesta": (
                    "🚨 ATENCIÓN PRIORITARIA DE CONTENCIÓN EMOCIONAL (HU-36):\n\n"
                    "Tu bienestar y tu vida son lo más importante. No estás solo(a) en este momento.\n\n"
                    "Te recomendamos contactar de inmediato con los servicios oficiales y gratuitos de contención psicológica en Bolivia:\n"
                    "• Línea de la Vida (Salud Mental Bolivia): 800-11-3040 (Llamada Gratuita 24/7)\n"
                    "• Emergencias Médicas y Policía Nacional: 911 / 110\n"
                    "• Defensoría del Pueblo / Atención en Crisis: 160\n\n"
                    "Hemos activado una alerta prioritaria en nuestra recepción para que un profesional humano te asista de inmediato."
                ),
                "intencion_detectada": "CRISIS_SUICIDA",
                "contiene_riesgo": True,
                "nivel_riesgo": "CRITICO",
                "alerta_crisis": True,
                "escalar_humano": True,
                "lineas_auxilio": ["800-11-3040", "911"],
                "botones_accion": [
                    {"etiqueta": "Llamar 800-11-3040", "accion": "LLAMAR_CRISIS"},
                    {"etiqueta": "Hablar con Recepcionista", "accion": "SOLICITAR_HUMANO"},
                    {"etiqueta": "Emergencias 911", "accion": "LLAMAR_EMERGENCIA"}
                ],
                "timestamp": ts_actual,
                # Compatibilidad
                "es_crisis": True,
                "texto": "🚨 ATENCIÓN PRIORITARIA DE CONTENCIÓN EMOCIONAL...",
                "opciones": ["Llamar al 800-11-3040", "Hablar con Recepcionista", "Emergencias 911"]
            }

        # 2. Búsqueda de intención por patrones
        texto_lower = texto_limpio.lower()
        for intent in cls.INTENCIONES:
            if any(re.search(patron, texto_lower) for patron in intent["regex"]):
                return {
                    "session_id": session_id,
                    "remitente": "BOT",
                    "respuesta": intent["respuesta"],
                    "intencion_detectada": intent["nombre"],
                    "contiene_riesgo": False,
                    "nivel_riesgo": "BAJO",
                    "alerta_crisis": False,
                    "escalar_humano": intent.get("escalar", False),
                    "lineas_auxilio": [],
                    "botones_accion": intent.get("botones", []),
                    "timestamp": ts_actual,
                    # Compatibilidad
                    "es_crisis": False,
                    "texto": intent["respuesta"],
                    "opciones": [b["etiqueta"] for b in intent.get("botones", [])]
                }

        # 3. Fallback General
        botones_default = [
            {"etiqueta": "Agendar Cita", "accion": "AGENDAR_CITA"},
            {"etiqueta": "Aranceles y Modalidades", "accion": "CONSULTAR_ARANCELES"},
            {"etiqueta": "Formulario Previo (Intake)", "accion": "IR_INTAKE"},
            {"etiqueta": "Hablar con Asesor Humano", "accion": "SOLICITAR_HUMANO"}
        ]
        return {
            "session_id": session_id,
            "remitente": "BOT",
            "respuesta": (
                "Comprendo tu consulta. Como asistente clínico automatizado de SIGEPSI, puedo orientarte sobre las siguientes "
                "áreas frecuentes del centro o transferirte directamente con un operador humano:"
            ),
            "intencion_detectada": "CONVERSACION_CASUAL",
            "contiene_riesgo": False,
            "nivel_riesgo": "BAJO",
            "alerta_crisis": False,
            "escalar_humano": False,
            "lineas_auxilio": [],
            "botones_accion": botones_default,
            "timestamp": ts_actual,
            # Compatibilidad
            "es_crisis": False,
            "texto": "Comprendo tu consulta...",
            "opciones": [b["etiqueta"] for b in botones_default]
        }

    @classmethod
    def procesar_mensaje(
        cls, 
        texto_usuario: str, 
        session_id: str = "", 
        historial: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Punto de entrada principal:
        1. Consulta la API externa en Hugging Face Space.
        2. Si responde correctamente dentro del timeout, normaliza y entrega la respuesta de la IA.
        3. Si la API externa no está disponible o tarda, ejecuta el motor local de contingencia.
        """
        # Intentar con la IA en Hugging Face
        respuesta_hf = cls.consultar_huggingface(session_id, texto_usuario, historial)
        if respuesta_hf and isinstance(respuesta_hf, dict) and "respuesta" in respuesta_hf:
            # Normalizar campos de compatibilidad hacia el backend
            respuesta_hf["texto"] = respuesta_hf.get("respuesta", "")
            respuesta_hf["es_crisis"] = respuesta_hf.get("alerta_crisis", False)
            respuesta_hf["opciones"] = [
                b.get("etiqueta", "") for b in respuesta_hf.get("botones_accion", []) if isinstance(b, dict)
            ]
            return respuesta_hf

        # Si no respondió la IA externa, recurrir al motor local de respaldo
        return cls.procesar_mensaje_local(texto_usuario, session_id=session_id)
