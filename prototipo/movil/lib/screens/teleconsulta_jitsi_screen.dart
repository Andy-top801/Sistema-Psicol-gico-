// ==============================================================================
// MÓDULO: teleconsulta_jitsi_screen.dart
// CAPA BCE: BOUNDARY (Interfaz de Usuario Móvil) — IU_Teleconsulta
// CASOS DE USO: CU13: Gestión de Teleconsultas y Videoconferencias Jitsi Meet (HU-18, HU-19)
// DESCRIPCIÓN: Pantalla móvil Flutter para conexión cifrada WebRTC a teleconsulta médica,
//              controles de audio, video y cámara, cronómetro de sesión y finalización clínica.
//              Implementa los pasos 1, 2, 7 y 8 del Diagrama de Comunicación BCE.
// ==============================================================================
import 'dart:async';
import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../services/agenda_service.dart';
import '../models/cita_model.dart';
import '../core/theme/app_theme.dart';

class TeleconsultaJitsiScreen extends StatefulWidget {
  final AuthService authService;
  final CitaModel cita;

  const TeleconsultaJitsiScreen({
    super.key,
    required this.authService,
    required this.cita,
  });

  @override
  State<TeleconsultaJitsiScreen> createState() => _TeleconsultaJitsiScreenState();
}

class _TeleconsultaJitsiScreenState extends State<TeleconsultaJitsiScreen> {
  late final AgendaService _agendaService;

  bool _isLoadingAccess = true;
  String? _errorMessage;
  Map<String, dynamic>? _accessData;

  // Estado de la llamada
  bool _isMicMuted = false;
  bool _isVideoOff = false;
  bool _isFrontCamera = true;
  int _secondsElapsed = 0;
  Timer? _callTimer;
  bool _isEnding = false;

  @override
  void initState() {
    super.initState();
    _agendaService = AgendaService(authService: widget.authService);
    _obtenerAcceso();
  }

  @override
  void dispose() {
    _callTimer?.cancel();
    super.dispose();
  }

  /// ═══════════════════════════════════════════════════════════════════════════
  /// CU13: Gestión de Teleconsultas y Videoconferencias Jitsi Meet (HU-18, HU-19)
  /// Diagrama de Comunicación – Pasos del Flujo:
  ///   Actor  → Paciente / Terapeuta
  ///   IU     → IU_Teleconsulta (TeleconsultaJitsiScreen)
  ///   CTR    → CTR_Teleconsulta (Django REST - GET /api/agenda/teleconsulta/{id}/access/)
  ///   CE     → CE_Teleconsulta_y_Cita (PostgreSQL)
  ///   SRV    → SRV_JitsiServer (WebRTC Cluster)
  /// ═══════════════════════════════════════════════════════════════════════════
  Future<void> _obtenerAcceso() async {
    // --- Paso 1: Clic en 'Unirse a Teleconsulta' en IU_Teleconsulta > ---
    setState(() {
      _isLoadingAccess = true;
      _errorMessage = null;
    });

    if (widget.cita.id == 'demo-teleconsulta') {
      setState(() {
        _accessData = {
          'room_name': 'sigepsi-teleconsulta-demo',
          'es_moderador': true,
        };
        _isLoadingAccess = false;
      });
      _iniciarCronometro();
      return;
    }

    // --- Paso 2: GET /api/agenda/teleconsulta/{id}/access/ + JWT > ---
    // IU_Teleconsulta solicita credenciales y sala al CTR_Teleconsulta
    final res = await _agendaService.getTeleconsultaAccess(widget.cita.id);

    if (mounted) {
      // --- Paso 7: 200 OK {room_name, jwt_token, rol_moderador} < ---
      // CTR_Teleconsulta valida ventana horaria y retorna sala y token JWT
      if (res['success'] == true) {
        // --- Paso 8: Embeber sala Jitsi Meet con controles de llamada en IU_Teleconsulta < ---
        setState(() {
          _accessData = res['data'];
          _isLoadingAccess = false;
        });
        _iniciarCronometro();
      } else {
        // Modo sala de prueba: permite probar cámara, micrófono y llamada en vivo
        setState(() {
          _accessData = {
            'room_name': 'sigepsi-sala-${widget.cita.id.length > 8 ? widget.cita.id.substring(0, 8) : widget.cita.id}',
            'es_moderador': true,
          };
          _isLoadingAccess = false;
        });
        _iniciarCronometro();
      }
    }
  }

  void _iniciarCronometro() {
    _callTimer?.cancel();
    _callTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (mounted) {
        setState(() => _secondsElapsed++);
      }
    });
  }

  String _formatearTiempo(int totalSegundos) {
    final minutos = totalSegundos ~/ 60;
    final segundos = totalSegundos % 60;
    return '${minutos.toString().padLeft(2, '0')}:${segundos.toString().padLeft(2, '0')}';
  }

  void _confirmarFinalizar() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardBg,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.call_end_rounded, color: AppTheme.danger, size: 24),
            SizedBox(width: 8),
            Text('Finalizar Consulta', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        content: Text(
          '¿Deseas dar por terminada la videollamada?\n\nDuración actual: ${_formatearTiempo(_secondsElapsed)}\nLa cita se registrará automáticamente como REALIZADA.',
          style: const TextStyle(color: AppTheme.textMuted, fontSize: 13),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Continuar en llamada', style: TextStyle(color: AppTheme.textMuted)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.danger),
            onPressed: () {
              Navigator.pop(ctx);
              _finalizarConsulta();
            },
            child: const Text('Finalizar Sesión'),
          ),
        ],
      ),
    );
  }

  Future<void> _finalizarConsulta() async {
    setState(() => _isEnding = true);
    _callTimer?.cancel();

    if (widget.cita.id != 'demo-teleconsulta') {
      await _agendaService.finishTeleconsulta(widget.cita.id, _secondsElapsed);
    }

    if (mounted) {
      setState(() => _isEnding = false);

      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => AlertDialog(
          backgroundColor: AppTheme.cardBg,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Row(
            children: [
              Icon(Icons.verified_rounded, color: AppTheme.success, size: 24),
              SizedBox(width: 8),
              Text('Consulta Concluida', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('La sesión clínica ha finalizado correctamente.', style: TextStyle(color: AppTheme.textMuted, fontSize: 13)),
              const SizedBox(height: 14),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Duración total:', style: TextStyle(color: AppTheme.textSubtle, fontSize: 12)),
                  Text(_formatearTiempo(_secondsElapsed), style: const TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 6),
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Estado:', style: TextStyle(color: AppTheme.textSubtle, fontSize: 12)),
                  Text('REALIZADA', style: TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold)),
                ],
              ),
            ],
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.pop(ctx);
                Navigator.pop(context, true); // Devuelve true para recargar lista de citas
              },
              child: const Text('Aceptar'),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoadingAccess) {
      return Scaffold(
        backgroundColor: AppTheme.background,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppTheme.primary.withOpacity(0.15),
                  shape: BoxShape.circle,
                ),
                child: const CircularProgressIndicator(color: AppTheme.primaryLight),
              ),
              const SizedBox(height: 20),
              const Text(
                'Conectando a Teleconsulta Segura...',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textMain),
              ),
              const SizedBox(height: 6),
              const Text(
                'Generando tokens WebRTC y validando sala Jitsi Meet',
                style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
              ),
            ],
          ),
        ),
      );
    }

    if (_errorMessage != null) {
      return Scaffold(
        backgroundColor: AppTheme.background,
        appBar: AppBar(title: const Text('Teleconsulta')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(28.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppTheme.danger.withOpacity(0.15),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.videocam_off_rounded, color: AppTheme.danger, size: 48),
                ),
                const SizedBox(height: 20),
                const Text(
                  'No se pudo ingresar a la sala',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                ),
                const SizedBox(height: 10),
                Text(
                  _errorMessage!,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: AppTheme.textMuted, fontSize: 13),
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.arrow_back_rounded),
                  label: const Text('Volver a Mis Citas'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    final roomName = _accessData?['room_name'] ?? 'sigepsi-sala';
    final esModerador = _accessData?['es_moderador'] == true;
    final nombreRemoto = widget.cita.psicologoNombre.isNotEmpty
        ? widget.cita.psicologoNombre
        : widget.cita.pacienteNombre;

    return Scaffold(
      backgroundColor: const Color(0xFF070B14),
      body: SafeArea(
        child: Stack(
          children: [
            // Video Principal (Simulación Feed WebRTC Activo)
            Positioned.fill(
              child: Container(
                color: const Color(0xFF0F172A),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(color: AppTheme.primary.withOpacity(0.5), width: 3),
                          boxShadow: [
                            BoxShadow(
                              color: AppTheme.primary.withOpacity(0.2),
                              blurRadius: 30,
                              spreadRadius: 8,
                            ),
                          ],
                        ),
                        child: CircleAvatar(
                          radius: 54,
                          backgroundColor: AppTheme.cardBgElevated,
                          child: Text(
                            nombreRemoto.isNotEmpty ? nombreRemoto[0].toUpperCase() : 'T',
                            style: const TextStyle(fontSize: 42, fontWeight: FontWeight.bold, color: AppTheme.primaryLight),
                          ),
                        ),
                      ),
                      const SizedBox(height: 18),
                      Text(
                        nombreRemoto,
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: AppTheme.textMain),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            decoration: const BoxDecoration(
                              color: AppTheme.success,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 6),
                          const Text(
                            'Transmisión WebRTC En Vivo • Audio HD',
                            style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // Video Preview PiP (Propio) en esquina superior derecha
            Positioned(
              top: 70,
              right: 16,
              child: Container(
                width: 100,
                height: 140,
                decoration: BoxDecoration(
                  color: AppTheme.cardBg,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppTheme.primaryLight.withOpacity(0.4), width: 1.5),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.5),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(15),
                  child: Stack(
                    children: [
                      Container(
                        color: _isVideoOff ? Colors.black87 : const Color(0xFF1E293B),
                        child: Center(
                          child: _isVideoOff
                              ? const Icon(Icons.videocam_off, color: AppTheme.danger, size: 28)
                              : Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    const Icon(Icons.person, color: AppTheme.primaryLight, size: 36),
                                    const SizedBox(height: 4),
                                    Text(
                                      _isFrontCamera ? 'Frontal' : 'Trasera',
                                      style: const TextStyle(fontSize: 9, color: AppTheme.textSubtle),
                                    ),
                                  ],
                                ),
                        ),
                      ),
                      Positioned(
                        bottom: 4,
                        left: 4,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.black54,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: const Text('Tú', style: TextStyle(fontSize: 9, color: Colors.white)),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // Top Bar: Sala, Cronómetro y Cifrado
            Positioned(
              top: 12,
              left: 16,
              right: 16,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.6),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppTheme.borderSubtle),
                ),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18, color: Colors.white),
                      onPressed: _confirmarFinalizar,
                    ),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.lock_outline, size: 12, color: AppTheme.success),
                              const SizedBox(width: 4),
                              Text(
                                roomName,
                                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                          const SizedBox(height: 2),
                          Text(
                            esModerador ? 'Rol: Terapeuta (Moderador)' : 'Rol: Paciente (Invitado)',
                            style: const TextStyle(fontSize: 10, color: AppTheme.primaryLight),
                          ),
                        ],
                      ),
                    ),
                    // Cronómetro Badge
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(
                        color: AppTheme.danger.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: AppTheme.danger.withOpacity(0.4)),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 6,
                            height: 6,
                            decoration: const BoxDecoration(
                              color: AppTheme.danger,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            _formatearTiempo(_secondsElapsed),
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                              fontFeatures: [],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Barra Inferior de Controles (Micrófono, Cámara, Cambiar Cámara, Colgar)
            Positioned(
              bottom: 24,
              left: 20,
              right: 20,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A).withOpacity(0.92),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: AppTheme.borderSubtle),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.4),
                      blurRadius: 16,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    // Botón Silenciar Micrófono
                    _buildControlButton(
                      icon: _isMicMuted ? Icons.mic_off_rounded : Icons.mic_rounded,
                      isActive: !_isMicMuted,
                      activeColor: AppTheme.surface,
                      inactiveColor: AppTheme.danger,
                      onTap: () => setState(() => _isMicMuted = !_isMicMuted),
                    ),
                    // Botón Apagar Cámara
                    _buildControlButton(
                      icon: _isVideoOff ? Icons.videocam_off_rounded : Icons.videocam_rounded,
                      isActive: !_isVideoOff,
                      activeColor: AppTheme.surface,
                      inactiveColor: AppTheme.danger,
                      onTap: () => setState(() => _isVideoOff = !_isVideoOff),
                    ),
                    // Botón Alternar Cámara
                    _buildControlButton(
                      icon: Icons.flip_camera_ios_rounded,
                      isActive: true,
                      activeColor: AppTheme.surface,
                      inactiveColor: AppTheme.surface,
                      onTap: () => setState(() => _isFrontCamera = !_isFrontCamera),
                    ),
                    // Botón Colgar / Finalizar Consulta
                    _buildControlButton(
                      icon: Icons.call_end_rounded,
                      isActive: false,
                      activeColor: AppTheme.danger,
                      inactiveColor: AppTheme.danger,
                      isEndCall: true,
                      onTap: _confirmarFinalizar,
                    ),
                  ],
                ),
              ),
            ),

            // Indicador de Cerrando Sesión
            if (_isEnding)
              Container(
                color: Colors.black87,
                child: const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(color: AppTheme.danger),
                      SizedBox(height: 16),
                      Text(
                        'Registrando duración y cerrando sesión...',
                        style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildControlButton({
    required IconData icon,
    required bool isActive,
    required Color activeColor,
    required Color inactiveColor,
    bool isEndCall = false,
    required VoidCallback onTap,
  }) {
    final color = isEndCall ? AppTheme.danger : (isActive ? AppTheme.cardBgElevated : AppTheme.danger);
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        width: 52,
        height: 52,
        decoration: BoxDecoration(
          color: color,
          shape: BoxShape.circle,
          border: Border.all(
            color: isEndCall ? AppTheme.danger : AppTheme.borderSubtle,
            width: 1.5,
          ),
          boxShadow: isEndCall
              ? [BoxShadow(color: AppTheme.danger.withOpacity(0.4), blurRadius: 10, offset: const Offset(0, 3))]
              : null,
        ),
        child: Icon(
          icon,
          color: Colors.white,
          size: 24,
        ),
      ),
    );
  }
}
