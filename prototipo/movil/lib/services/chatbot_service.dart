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
