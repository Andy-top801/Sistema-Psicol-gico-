# ==============================================================================
# MÓDULO: clinica/chatbot_service.py
# CASO DE USO: CU20 (HU-36) Chatbot de Orientación Clínica y Derivación Humana
# DESCRIPCIÓN: Motor de intenciones NLP, FAQ clínica institucional (<1s),
#              protocolo de contención de crisis 24/7 (800-11-3040 / 911)
#              y escalamiento contextual a recepcionista en servicio.
# ==============================================================================
import re
from typing import Dict, Any, List

class ChatbotEngine:
    """
    Motor conversacional de orientación al paciente con salvaguarda ética de crisis
    y derivación a operador humano.
    """

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
            "respuesta": "Entendido. He transferido tu conversación a la bandeja de recepción humana en turno. Un operador del centro continuará la atención en este mismo canal para asistirte personalmente.",
            "opciones": ["Esperar Operador", "Consultar Aranceles", "Ver Agenda"],
            "escalar": True
        },
        {
            "nombre": "AGENDAMIENTO",
            "regex": [r'\bcita\b', r'\bagendar\b', r'\breservar\b', r'\bhora\b', r'\bturno\b', r'\bdisponib', r'\bcalendario\b'],
            "respuesta": "Para agendar tu consulta psicológica en SIGEPSI:\n1. Ingresa a la sección 'Agenda y Citas'.\n2. Elige al psicólogo de tu preferencia y la modalidad (Presencial o Teleconsulta virtual por WebRTC).\n3. Selecciona la fecha y el horario disponible que prefieras.\n4. Si es tu primera sesión, recuerda completar el Cuestionario Pre-Consulta (Intake) antes de la cita.",
            "opciones": ["Directorio de Psicólogos", "Llenar Formulario Previo", "Consultar Aranceles", "Hablar con un Asesor Humano"],
            "escalar": False
        },
        {
            "nombre": "ARANCELES",
            "regex": [r'\bprecio\b', r'\bcosto\b', r'\barancel\b', r'\btarifa\b', r'\bcuanto cuesta\b', r'\bpagar\b', r'\bpago\b', r'\bdescuento\b'],
            "respuesta": "Los aranceles de atención clínica institucional en el centro son:\n• Psicoterapia Individual Presencial: 150 - 180 BOB por sesión.\n• Teleconsulta Online (WebRTC): 140 - 160 BOB por sesión.\n• Evaluación Diagnóstica y Psicométrica: 200 - 220 BOB.\nDispones de pago por QR electrónico, tarjeta de débito/crédito o en caja física.",
            "opciones": ["Agendar una Cita", "¿Cómo llenar Formulario Previo?", "Hablar con un Asesor Humano"],
            "escalar": False
        },
        {
            "nombre": "INTAKE",
            "regex": [r'\bformulario\b', r'\bintake\b', r'\bpreconsulta\b', r'\bpreguntas\b', r'\bcuestionario\b', r'\bantes de la sesion\b'],
            "respuesta": "El Formulario Pre-Consulta (Intake Digital) permite a tu terapeuta conocer el motivo de tu consulta, malestar percibido (1 a 5) y antecedentes antes de tu primera sesión:\n• Puedes completarlo en 3 a 5 minutos en el menú 'Pre-Consulta (Intake)'.\n• Todas tus respuestas son confidenciales y están resguardadas bajo secreto profesional médico.\n• Si tu cita es en menos de 24 horas, te recomendamos completarlo hoy mismo.",
            "opciones": ["Ir a Formulario Previo", "¿Cómo agendar mi cita?", "Hablar con un Asesor Humano"],
            "escalar": False
        },
        {
            "nombre": "HISTORIA_CLINICA",
            "regex": [r'\bhistoria\b', r'\bexpediente\b', r'\bconfidencial\b', r'\bprivacidad\b', r'\bsecreto profesional\b', r'\bm[eé]dico-legal\b'],
            "respuesta": "En SIGEPSI, tu expediente clínico electrónico (EHR) cuenta con estricta protección de acceso RBAC:\n• Solo tu psicólogo tratante asignado y la Dirección Clínica tienen autorización de lectura.\n• Todas las notas SOAP y diagnósticos CIE-10 están sellados con trazabilidad inmutable y firma digital.",
            "opciones": ["Agendar Cita", "Formulario Previo", "Hablar con un Asesor Humano"],
            "escalar": False
        },
        {
            "nombre": "SALUDO",
            "regex": [r'\bhola\b', r'\bbuen[oa]s d[ií]as\b', r'\btardes\b', r'\bnoches\b', r'\bsaludos\b', r'\binicio\b'],
            "respuesta": "¡Hola! Bienvenido(a) al Asistente de Orientación Clínica de SIGEPSI. Estoy aquí para resolver tus dudas sobre citas, aranceles y llenado de formularios previos. ¿En qué te puedo orientar hoy?",
            "opciones": ["¿Cómo agendar mi cita?", "Aranceles y Modalidades", "Ayuda con Formulario Previo", "Hablar con un Asesor Humano"],
            "escalar": False
        }
    ]

    @classmethod
    def detectar_crisis(cls, texto: str) -> bool:
        texto_lower = texto.lower()
        for patron in cls.PALABRAS_CRISIS:
            if re.search(patron, texto_lower):
                return True
        return False

    @classmethod
    def procesar_mensaje(cls, texto_usuario: str) -> Dict[str, Any]:
        """
        Procesa el mensaje del usuario, evalúa banderas de crisis y devuelve la respuesta.
        """
        texto_limpio = texto_usuario.strip()

        # 1. SALVAGUARDA ÉTICA OBLIGATORIA: Detección de Crisis / Riesgo Vital
        if cls.detectar_crisis(texto_limpio):
            return {
                "es_crisis": True,
                "nivel_riesgo": "CRISIS",
                "escalar_humano": True,
                "texto": (
                    "🚨 ATENCIÓN PRIORITARIA DE CONTENCIÓN EMOCIONAL (HU-36):\n\n"
                    "Tu bienestar y tu vida son lo más importante. No estás solo(a) en este momento.\n\n"
                    "Te recomendamos contactar de inmediato con los servicios oficiales y gratuitos de contención psicológica en Bolivia:\n"
                    "• Línea de la Vida (Salud Mental Bolivia): 800-11-3040 (Llamada Gratuita 24/7)\n"
                    "• Emergencias Médicas y Policía Nacional: 911 / 110\n"
                    "• Defensoría del Pueblo / Atención en Crisis: 160\n\n"
                    "Hemos activado una alerta prioritaria en nuestra recepción para que un profesional humano te asista de inmediato."
                ),
                "opciones": [
                    "Llamar al 800-11-3040",
                    "Hablar con Recepcionista Humano",
                    "Emergencias 911"
                ]
            }

        # 2. Clasificación de Intenciones por Palabras Clave / Expresiones Regulares
        texto_lower = texto_limpio.lower()
        for intent in cls.INTENCIONES:
            for regex in intent["regex"]:
                if re.search(regex, texto_lower):
                    return {
                        "es_crisis": False,
                        "nivel_riesgo": "NORMAL",
                        "escalar_humano": intent.get("escalar", False),
                        "texto": intent["respuesta"],
                        "opciones": intent["opciones"]
                    }

        # 3. Fallback General
        return {
            "es_crisis": False,
            "nivel_riesgo": "NORMAL",
            "escalar_humano": False,
            "texto": (
                "Comprendo tu consulta. Como asistente clínico automatizado, puedo orientarte sobre las siguientes áreas frecuentes del centro, "
                "o bien derivarte directamente con un recepcionista humano:"
            ),
            "opciones": [
                "¿Cómo agendar mi cita?",
                "Aranceles y Modalidades",
                "Ayuda con Formulario Previo",
                "Hablar con un Asesor Humano"
            ]
        }
