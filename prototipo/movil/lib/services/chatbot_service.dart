// ==============================================================================
// MÓDULO: chatbot_service.dart (Móvil)
// CAPA BCE: CONTROL (Cliente Móvil / Service Adapter) — CTR_ChatbotService
// CASO DE USO: CU20 – Interacción con el Chatbot de Orientación Clínica y Derivación a Operador (HU-36)
//
// DIAGRAMA DE SECUENCIA UML (CU20 - Chatbot de Orientación Clínica y Derivación):
// ------------------------------------------------------------------------------
// 1. Paciente / Usuario -> IU_ChatbotWidget: 1: enviar_mensaje_o_consulta(texto, session_token)
// 2. IU_ChatbotWidget -> CTR_ChatbotController: 2: POST /api/v1/chatbot/mensaje/
// 3. CTR_ChatbotController -> CTR_ChatbotController: 3: sanitizar_y_clasificar_intencion(texto)
// 4. CTR_ChatbotController -> CE_ConversacionChatbot: 4: INSERT INTO clinica_mensajechatbot (emisor='PACIENTE', texto)
// 5. CE_ConversacionChatbot --> CTR_ChatbotController: 5: mensaje_registrado()
// 6. CTR_ChatbotController -> CTR_ChatbotController: 6: evaluar_umbral_de_confianza_o_riesgo_de_crisis()
// [Alt 1: Detección de Crisis Emocional Aguda]
// 7. CTR_ChatbotController --> IU_ChatbotWidget: 7: HTTP 200 (alerta_crisis=true, lineas_auxilio_800_11_3040)
// 8. IU_ChatbotWidget --> Paciente: 8: desplegar_modal_urgencias_con_telefonos()
// [Alt 2: Intención FAQ Clara (Confianza >= 80%)]
// 9. CTR_ChatbotController -> CE_ConversacionChatbot: 9: INSERT INTO clinica_mensajechatbot (emisor='BOT', respuesta_faq)
// 10. CE_ConversacionChatbot --> CTR_ChatbotController: 10: respuesta_faq_almacenada()
// 11. CTR_ChatbotController --> IU_ChatbotWidget: 11: HTTP 200 OK (tipo='BOT_FAQ', respuesta, botones_accion)
// 12. IU_ChatbotWidget --> Paciente: 12: renderizar_mensaje_de_orientacion(botones_accion)
// [Alt 3: Solicitud Asesor o Intención No Resuelta (Escalamiento)]
// 13. CTR_ChatbotController -> CE_ConversacionChatbot: 13: UPDATE clinica_conversacionchatbot (estado='ESCALADA_HUMANO')
// 14. CE_ConversacionChatbot --> CTR_ChatbotController: 14: estado_actualizado()
// 15. CTR_ChatbotController -> Recepcionista: 15: emitir_notificacion_websocket_de_transferencia(conversacion_id)
// 16. CTR_ChatbotController --> IU_ChatbotWidget: 16: HTTP 200 (tipo='TRANSFERENCIA_HUMANA', status='EN_ESPERA_ASESOR')
// 17. IU_ChatbotWidget --> Paciente: 17: mostrar_estado_espera('Conectando con un asesor en vivo...')
// 18. Recepcionista -> IU_ChatbotWidget: 18: tomar_control_del_chat_y_responder(mensaje_operador)
// 19. IU_ChatbotWidget --> Paciente: 19: conexion_en_vivo_con_soporte_del_centro(mensaje_operador)
// ==============================================================================
import 'dart:convert';
import 'package:http/http.dart' as http;

class ChatbotBotonAccion {
  final String etiqueta;
  final String accion;

  ChatbotBotonAccion({required this.etiqueta, required this.accion});

  factory ChatbotBotonAccion.fromJson(Map<String, dynamic> json) {
    return ChatbotBotonAccion(
      etiqueta: json['etiqueta'] ?? '',
      accion: json['accion'] ?? '',
    );
  }
}

class ChatbotRespuesta {
  final String sessionId;
  final String remitente;
  final String respuesta;
  final String intencionDetectada;
  final bool contieneRiesgo;
  final String nivelRiesgo;
  final bool alertaCrisis;
  final bool escalarHumano;
  final List<String> lineasAuxilio;
  final List<ChatbotBotonAccion> botonesAccion;
  final String timestamp;

  ChatbotRespuesta({
    required this.sessionId,
    required this.remitente,
    required this.respuesta,
    required this.intencionDetectada,
    required this.contieneRiesgo,
    required this.nivelRiesgo,
    required this.alertaCrisis,
    required this.escalarHumano,
    required this.lineasAuxilio,
    required this.botonesAccion,
    required this.timestamp,
  });

  factory ChatbotRespuesta.fromJson(Map<String, dynamic> json) {
    var rawBotones = json['botones_accion'] as List? ?? [];
    List<ChatbotBotonAccion> botones = rawBotones
        .map((b) => b is Map<String, dynamic>
            ? ChatbotBotonAccion.fromJson(b)
            : ChatbotBotonAccion(etiqueta: b.toString(), accion: 'ACCION'))
        .toList();

    var rawLineas = json['lineas_auxilio'] as List? ?? [];
    List<String> lineas = rawLineas.map((l) => l.toString()).toList();

    return ChatbotRespuesta(
      sessionId: json['session_id'] ?? '',
      remitente: json['remitente'] ?? 'BOT',
      respuesta: json['respuesta'] ?? '',
      intencionDetectada: json['intencion_detectada'] ?? 'CONVERSACION_CASUAL',
      contieneRiesgo: json['contiene_riesgo'] == true,
      nivelRiesgo: json['nivel_riesgo'] ?? 'BAJO',
      alertaCrisis: json['alerta_crisis'] == true,
      escalarHumano: json['escalar_humano'] == true,
      lineasAuxilio: lineas,
      botonesAccion: botones,
      timestamp: json['timestamp'] ?? DateTime.now().toIso8601String(),
    );
  }
}

class ChatbotService {
  static const String apiUrl = 'https://antidino-iacupficct.hf.space/api/v1/chatbot/mensaje/';
  static const Duration timeoutDuration = Duration(seconds: 30);

  /// Envía un mensaje a la API de IA en Hugging Face con memoria de historial
  Future<ChatbotRespuesta> enviarMensaje({
    required String sessionId,
    required String mensaje,
    required List<Map<String, String>> historial,
  }) async {
    final payload = {
      'session_id': sessionId,
      'mensaje': mensaje,
      'historial': historial,
    };

    try {
      final response = await http
          .post(
            Uri.parse(apiUrl),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(payload),
          )
          .timeout(timeoutDuration);

      if (response.statusCode == 200) {
        final decoded = jsonDecode(utf8.decode(response.bodyBytes));
        return ChatbotRespuesta.fromJson(decoded);
      } else {
        throw Exception('Error en respuesta de IA: ${response.statusCode}');
      }
    } catch (e) {
      // Fallback local seguro ante problemas de red o latencia
      final bool esCrisis = RegExp(
        r'suicid|morir|matarme|quitarme la vida|no aguanto m[aá]s|hacerme da[ñn]o',
        caseSensitive: false,
      ).hasMatch(mensaje);

      if (esCrisis) {
        return ChatbotRespuesta(
          sessionId: sessionId,
          remitente: 'BOT',
          respuesta:
              '🚨 ATENCIÓN PRIORITARIA: Tu vida y tu salud emocional son lo más importante. '
              'Por favor comunícate de inmediato con las líneas gratuitas de auxilio en Bolivia:\n'
              '• Línea de la Vida: 800-11-3040 (24/7 Gratis)\n'
              '• Emergencias Nacionales: 911 / 110',
          intencionDetectada: 'CRISIS_SUICIDA',
          contieneRiesgo: true,
          nivelRiesgo: 'CRITICO',
          alertaCrisis: true,
          escalarHumano: true,
          lineasAuxilio: ['800-11-3040', '911'],
          botonesAccion: [
            ChatbotBotonAccion(etiqueta: 'Llamar al 800-11-3040', accion: 'LLAMAR_CRISIS'),
            ChatbotBotonAccion(etiqueta: 'Emergencias 911', accion: 'LLAMAR_911'),
          ],
          timestamp: DateTime.now().toIso8601String(),
        );
      }

      return ChatbotRespuesta(
        sessionId: sessionId,
        remitente: 'BOT',
        respuesta:
            'Hola. En este momento el asistente está procesando varias consultas. '
            'Puedes agendar tu cita psicológica en el menú principal o consultar aranceles institucionales.',
        intencionDetectada: 'FALLBACK',
        contieneRiesgo: false,
        nivelRiesgo: 'BAJO',
        alertaCrisis: false,
        escalarHumano: false,
        lineasAuxilio: [],
        botonesAccion: [
          ChatbotBotonAccion(etiqueta: 'Agendar Cita', accion: 'AGENDAR_CITA'),
          ChatbotBotonAccion(etiqueta: 'Consultar Aranceles', accion: 'CONSULTAR_ARANCELES'),
        ],
        timestamp: DateTime.now().toIso8601String(),
      );
    }
  }
}
