import 'package:flutter/material.dart';
import '../services/chatbot_service.dart';

class MensajeUI {
  final String remitente; // 'USUARIO' o 'BOT'
  final String texto;
  final bool alertaCrisis;
  final List<String> lineasAuxilio;
  final List<ChatbotBotonAccion> botonesAccion;
  final DateTime timestamp;

  MensajeUI({
    required this.remitente,
    required this.texto,
    this.alertaCrisis = false,
    this.lineasAuxilio = const [],
    this.botonesAccion = const [],
    required this.timestamp,
  });
}

class ChatbotScreen extends StatefulWidget {
  final String? initialPrompt;

  const ChatbotScreen({super.key, this.initialPrompt});

  @override
  State<ChatbotScreen> createState() => _ChatbotScreenState();
}

class _ChatbotScreenState extends State<ChatbotScreen> {
  final ChatbotService _chatbotService = ChatbotService();
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final String _sessionId = 'movil_${DateTime.now().millisecondsSinceEpoch}';

  final List<MensajeUI> _mensajes = [];
  bool _estaCargando = false;

  @override
  void initState() {
    super.initState();
    // Mensaje de bienvenida inicial
    _mensajes.add(
      MensajeUI(
        remitente: 'BOT',
        texto:
            '¡Hola! Te damos la bienvenida a SIGEPSI. Soy el asistente virtual con Inteligencia Artificial para orientación psicológica y consultas del centro. ¿En qué puedo orientarte hoy?',
        botonesAccion: [
          ChatbotBotonAccion(etiqueta: 'Agendar Cita', accion: 'AGENDAR_CITA'),
          ChatbotBotonAccion(etiqueta: 'Consultar Aranceles', accion: 'CONSULTAR_ARANCELES'),
          ChatbotBotonAccion(etiqueta: 'Formulario Previo', accion: 'IR_INTAKE'),
        ],
        timestamp: DateTime.now(),
      ),
    );

    if (widget.initialPrompt != null && widget.initialPrompt!.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _enviarTexto(widget.initialPrompt!);
      });
    }
  }

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollHaciaAbajo() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  List<Map<String, String>> _obtenerHistorial() {
    return _mensajes.take(10).map((m) {
      return {
        'role': m.remitente == 'USUARIO' ? 'user' : 'assistant',
        'content': m.texto,
      };
    }).toList();
  }

  Future<void> _enviarTexto(String texto) async {
    final limpio = texto.trim();
    if (limpio.isEmpty || _estaCargando) return;

    _textController.clear();

    // 1. Mensaje optimista del usuario
    setState(() {
      _mensajes.add(
        MensajeUI(
          remitente: 'USUARIO',
          texto: limpio,
          timestamp: DateTime.now(),
        ),
      );
      _estaCargando = true;
    });
    _scrollHaciaAbajo();

    final historial = _obtenerHistorial();

    // 2. Llamada a la API
    final resp = await _chatbotService.enviarMensaje(
      sessionId: _sessionId,
      mensaje: limpio,
      historial: historial,
    );

    if (!mounted) return;

    // 3. Registrar respuesta del Bot
    setState(() {
      _estaCargando = false;
      _mensajes.add(
        MensajeUI(
          remitente: 'BOT',
          texto: resp.respuesta,
          alertaCrisis: resp.alertaCrisis,
          lineasAuxilio: resp.lineasAuxilio,
          botonesAccion: resp.botonesAccion,
          timestamp: DateTime.now(),
        ),
      );
    });
    _scrollHaciaAbajo();
  }

  void _manejarBotonAccion(ChatbotBotonAccion boton) {
    if (_estaCargando) return;
    _enviarTexto(boton.etiqueta);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: const Color(0xFF0D9488).withValues(alpha: 0.2),
                shape: BoxShape.circle,
              ),
              child: const Text(
                'Ψ',
                style: TextStyle(
                  color: Color(0xFF2DD4BF),
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
            ),
            const SizedBox(width: 10),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Asistente SIGEPSI',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                ),
                Text(
                  'IA de Orientación y Crisis 24/7',
                  style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                ),
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          // Stream de Mensajes
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _mensajes.length,
              itemBuilder: (context, index) {
                final msg = _mensajes[index];
                final esUsuario = msg.remitente == 'USUARIO';

                return Padding(
                  padding: const EdgeInsets.only(bottom: 14),
                  child: Row(
                    mainAxisAlignment:
                        esUsuario ? MainAxisAlignment.end : MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (!esUsuario) ...[
                        CircleAvatar(
                          radius: 16,
                          backgroundColor: msg.alertaCrisis
                              ? const Color(0xFFEF4444)
                              : const Color(0xFF0F766E),
                          child: Text(
                            msg.alertaCrisis ? '⚠️' : 'Ψ',
                            style: const TextStyle(color: Colors.white, fontSize: 13),
                          ),
                        ),
                        const SizedBox(width: 8),
                      ],
                      Flexible(
                        child: Column(
                          crossAxisAlignment: esUsuario
                              ? CrossAxisAlignment.end
                              : CrossAxisAlignment.start,
                          children: [
                            // Burbuja principal
                            Container(
                              padding: const EdgeInsets.all(14),
                              decoration: BoxDecoration(
                                color: esUsuario
                                    ? const Color(0xFF0D9488)
                                    : (msg.alertaCrisis
                                        ? const Color(0xFF7F1D1D).withValues(alpha: 0.85)
                                        : const Color(0xFF1E293B)),
                                borderRadius: BorderRadius.circular(16).copyWith(
                                  bottomRight: esUsuario ? const Radius.circular(4) : null,
                                  bottomLeft: !esUsuario ? const Radius.circular(4) : null,
                                ),
                                border: msg.alertaCrisis
                                    ? Border.all(color: const Color(0xFFEF4444), width: 1.5)
                                    : Border.all(color: const Color(0xFF334155), width: 0.8),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  if (msg.alertaCrisis) ...[
                                    Row(
                                      children: const [
                                        Icon(Icons.warning_amber_rounded, color: Color(0xFFFCA5A5), size: 18),
                                        SizedBox(width: 6),
                                        Text(
                                          'PROTOCOLO DE CONTENCIÓN ACTIVO',
                                          style: TextStyle(
                                            color: Color(0xFFFCA5A5),
                                            fontWeight: FontWeight.bold,
                                            fontSize: 11,
                                            letterSpacing: 0.5,
                                          ),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 8),
                                  ],
                                  Text(
                                    msg.texto,
                                    style: TextStyle(
                                      color: Colors.white.withValues(alpha: 0.95),
                                      fontSize: 14,
                                      height: 1.4,
                                    ),
                                  ),
                                  // Líneas de Auxilio destacadas si hay crisis
                                  if (msg.lineasAuxilio.isNotEmpty) ...[
                                    const SizedBox(height: 12),
                                    Container(
                                      padding: const EdgeInsets.all(10),
                                      decoration: BoxDecoration(
                                        color: Colors.black.withValues(alpha: 0.3),
                                        borderRadius: BorderRadius.circular(8),
                                        border: Border.all(color: const Color(0xFFEF4444).withValues(alpha: 0.5)),
                                      ),
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          const Text(
                                            'Líneas Oficiales de Emergencia (24/7 Gratis):',
                                            style: TextStyle(
                                              color: Color(0xFFFCA5A5),
                                              fontWeight: FontWeight.bold,
                                              fontSize: 12,
                                            ),
                                          ),
                                          const SizedBox(height: 8),
                                          Wrap(
                                            spacing: 8,
                                            runSpacing: 6,
                                            children: msg.lineasAuxilio.map((tel) {
                                              return ElevatedButton.icon(
                                                onPressed: () {
                                                  ScaffoldMessenger.of(context).showSnackBar(
                                                    SnackBar(
                                                      content: Text('Llamando a línea de auxilio: $tel'),
                                                      backgroundColor: const Color(0xFFDC2626),
                                                    ),
                                                  );
                                                },
                                                icon: const Icon(Icons.phone, size: 14, color: Colors.white),
                                                label: Text(
                                                  'Llamar al $tel',
                                                  style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                                                ),
                                                style: ElevatedButton.styleFrom(
                                                  backgroundColor: const Color(0xFFDC2626),
                                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                                                ),
                                              );
                                            }).toList(),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),

                            // Botones de acción rápida clickeables
                            if (msg.botonesAccion.isNotEmpty) ...[
                              const SizedBox(height: 8),
                              Wrap(
                                spacing: 6,
                                runSpacing: 6,
                                children: msg.botonesAccion.map((btn) {
                                  return ActionChip(
                                    backgroundColor: const Color(0xFF0F766E).withValues(alpha: 0.25),
                                    side: const BorderSide(color: Color(0xFF0D9488), width: 0.8),
                                    label: Text(
                                      btn.etiqueta,
                                      style: const TextStyle(
                                        color: Color(0xFF2DD4BF),
                                        fontSize: 12,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                    onPressed: () => _manejarBotonAccion(btn),
                                  );
                                }).toList(),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),

          // Indicador de "Escribiendo..."
          if (_estaCargando)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              alignment: Alignment.centerLeft,
              child: Row(
                children: const [
                  SizedBox(
                    width: 14,
                    height: 14,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF2DD4BF)),
                    ),
                  ),
                  SizedBox(width: 10),
                  Text(
                    'Asistente procesando respuesta...',
                    style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12, fontStyle: FontStyle.italic),
                  ),
                ],
              ),
            ),

          // Input Barra inferior
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: const BoxDecoration(
              color: Color(0xFF1E293B),
              border: Border(top: BorderSide(color: Color(0xFF334155), width: 0.8)),
            ),
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _textController,
                      style: const TextStyle(color: Colors.white, fontSize: 14),
                      decoration: InputDecoration(
                        hintText: 'Escribe tu consulta o duda...',
                        hintStyle: TextStyle(color: const Color(0xFF94A3B8).withValues(alpha: 0.8)),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                        filled: true,
                        fillColor: const Color(0xFF0F172A),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                      ),
                      onSubmitted: _enviarTexto,
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    onPressed: () => _enviarTexto(_textController.text),
                    icon: const Icon(Icons.send_rounded, color: Color(0xFF2DD4BF)),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
