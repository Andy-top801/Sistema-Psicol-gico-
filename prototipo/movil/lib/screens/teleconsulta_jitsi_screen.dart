// ==============================================================================
// MÓDULO: teleconsulta_jitsi_screen.dart
// CAPA BCE: BOUNDARY — IU_SalaTeleconsultaMovil
// CASO DE USO: CU13 Móvil – Sesión de Teleconsulta Nativa WebRTC Jitsi Meet (HU-44)
//
// DIAGRAMA DE SECUENCIA "Secuencia_Corregido_CU13_Teleconsulta_Movil_WebRTC":
//   1 : Paciente → IU.presionar_ingresar_teleconsulta(teleconsulta_id)
//   2 : IU → CTR  POST /api/agenda/teleconsulta/{id}/unirse/
//   3-18: CTR valida ventana, consulta cita/paciente/psicólogo, inicia sala,
//         registra entrada, genera JWT y audita INGRESO_SALA_TELECONSULTA
//   alt [en_ventana_acceso == true]
//     19: 200 OK {jitsi_jwt, room_name, server_url}
//     20: IU → Paciente.conectar_webrtc(jitsi_jwt, room_name)   ← SDK nativo Jitsi Meet
//   else
//     21: 403 Forbidden {'Sala disponible solo 10 min antes…'}
//     22: IU → Paciente.mostrar_alerta_horario_invalido()
//
// HU-44 (a) ventana 10 min antes / 45 min después (validada en el servidor)
//       (b) el SDK pide permisos de cámara/micrófono y muestra silenciar, cámara
//           frontal/trasera y colgar
//       (c) al colgar vuelve al detalle de la cita con agradecimiento + invitación
//           a registrar el estado de ánimo (Mood Tracker, HU-46)
// ==============================================================================
import 'package:flutter/material.dart';
import 'package:jitsi_meet_flutter_sdk/jitsi_meet_flutter_sdk.dart';
import '../services/auth_service.dart';
import '../services/agenda_service.dart';
import '../models/cita_model.dart';
import '../core/theme/app_theme.dart';
import 'mood_tracker_sheet.dart';

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
  final JitsiMeet _jitsi = JitsiMeet();

  bool _conectando = true;
  bool _enLlamada = false;
  bool _terminada = false;
  String? _error;
  Map<String, dynamic> _acceso = const {};
  DateTime? _inicioLlamada;

  bool get _esDemo => widget.cita.id == 'demo-teleconsulta';

  String get _nombreRemoto => widget.cita.psicologoNombre.isNotEmpty
      ? widget.cita.psicologoNombre
      : widget.cita.pacienteNombre;

  @override
  void initState() {
    super.initState();
    _agendaService = AgendaService(authService: widget.authService);
    _ingresar();
  }

  /// CU13-paso 1: presionar_ingresar_teleconsulta(teleconsulta_id) — el Paciente entra a IU_SalaTeleconsultaMovil.
  Future<void> _ingresar() async {
    setState(() {
      _conectando = true;
      _error = null;
    });

    Map<String, dynamic> acceso;
    if (_esDemo) {
      acceso = {'room_name': 'sigepsi-teleconsulta-demo', 'server_url': 'https://meet.jit.si', 'es_moderador': true};
    } else {
      // CU13-paso 2: POST teleconsulta/{id}/unirse/ (dispositivo) → CTR_TeleconsultaController
      final res = await _agendaService.getTeleconsultaAccess(widget.cita.id);
      if (!mounted) return;
      if (res['success'] != true) {
        // CU13-paso 21: HTTP 403 Forbidden {'Sala disponible solo ... antes de cita'} [retorno]
        // CU13-paso 22: mostrar_alerta_horario_invalido('Sala no habilitada') — se muestra con _error
        setState(() {
          _conectando = false;
          _error = (res['error'] ?? 'No fue posible acceder a la sala de teleconsulta.').toString();
        });
        return;
      }
      // CU13-paso 19: HTTP 200 OK {jitsi_jwt, room_name, server_url} [retorno]
      acceso = Map<String, dynamic>.from(res['data'] as Map);
    }
    _acceso = acceso;
    await _conectarWebRTC();
  }

  /// CU13-paso 20: conectar_webrtc_jitsi(room_name, token) con el SDK nativo de Jitsi Meet.
  Future<void> _conectarWebRTC() async {
    final serverUrl = (_acceso['server_url'] ?? 'https://meet.jit.si').toString();
    final usuario = widget.authService.currentUser;
    // ponytail: meet.jit.si público rechaza JWT propios; el token solo se envía a
    // un servidor Jitsi propio configurado con JITSI_DOMAIN/JITSI_APP_SECRET.
    final usarToken = !serverUrl.contains('meet.jit.si');

    final opciones = JitsiMeetConferenceOptions(
      serverURL: serverUrl,
      room: (_acceso['room_name'] ?? 'sigepsi-sala').toString(),
      token: usarToken ? _acceso['jitsi_jwt']?.toString() : null,
      configOverrides: {
        'startWithAudioMuted': false,
        'startWithVideoMuted': false,
        'subject': _nombreRemoto.isNotEmpty ? 'Sesión con $_nombreRemoto' : 'Teleconsulta SIGEPSI',
      },
      featureFlags: {
        'welcomepage.enabled': false,
        'prejoinpage.enabled': false,
        'unsaferoomwarning.enabled': false,
        'invite.enabled': false,
        'add-people.enabled': false,
        'calendar.enabled': false,
        'recording.enabled': false,
        'live-streaming.enabled': false,
      },
      userInfo: JitsiMeetUserInfo(
        displayName: usuario == null ? 'Paciente' : '${usuario.nombre} ${usuario.apellido}'.trim(),
        email: usuario?.email,
      ),
    );

    final listener = JitsiMeetEventListener(
      conferenceJoined: (url) {
        if (!mounted) return;
        setState(() {
          _conectando = false;
          _enLlamada = true;
          _inicioLlamada = DateTime.now();
        });
      },
      conferenceTerminated: (url, error) => _alColgar(),
      readyToClose: _alColgar,
    );

    try {
      await _jitsi.join(opciones, listener);
      if (mounted) setState(() => _conectando = false);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _conectando = false;
        _error = 'No se pudo abrir la sala de video en este dispositivo. '
            'La teleconsulta nativa requiere la app en Android o iOS.\n($e)';
      });
    }
  }

  /// HU-44 (c): al colgar, volver al detalle de la cita con agradecimiento
  /// e invitación a registrar el estado de ánimo.
  Future<void> _alColgar() async {
    if (_terminada || !mounted) return;
    _terminada = true;

    final duracion = _inicioLlamada == null ? 0 : DateTime.now().difference(_inicioLlamada!).inSeconds;
    // Solo el psicólogo (moderador) cierra la cita como REALIZADA; si el paciente
    // se desconecta puede volver a entrar mientras la ventana siga abierta.
    if (!_esDemo && _acceso['es_moderador'] == true) {
      await _agendaService.finishTeleconsulta(widget.cita.id, duracion);
    }
    if (!mounted) return;

    final nav = Navigator.of(context);
    final auth = widget.authService;
    nav.pop(true);
    showDialog(
      context: nav.context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardBg,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(children: [
          Icon(Icons.favorite_rounded, color: kMoodColor, size: 24),
          SizedBox(width: 8),
          Expanded(child: Text('¡Gracias por tu sesión!', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18))),
        ]),
        content: const Text(
          'Tu teleconsulta ha finalizado. Registrar cómo te sientes hoy ayuda a tu psicólogo/a a acompañar tu proceso.',
          style: TextStyle(color: AppTheme.textMuted, fontSize: 13),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Ahora no', style: TextStyle(color: AppTheme.textMuted)),
          ),
          ElevatedButton.icon(
            style: ElevatedButton.styleFrom(backgroundColor: kMoodColor, foregroundColor: Colors.white),
            onPressed: () {
              Navigator.pop(ctx);
              mostrarMoodTrackerSheet(nav.context, auth);
            },
            icon: const Icon(Icons.mood_rounded, size: 18),
            label: const Text('Registrar mi ánimo'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    if (_enLlamada && !_terminada) _jitsi.hangUp();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(title: const Text('Sala de Teleconsulta')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: _error != null ? _buildError() : _buildEstado(),
        ),
      ),
    );
  }

  Widget _buildEstado() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(color: AppTheme.primary.withOpacity(0.15), shape: BoxShape.circle),
          child: _conectando
              ? const CircularProgressIndicator(color: AppTheme.primaryLight)
              : const Icon(Icons.videocam_rounded, color: AppTheme.primaryLight, size: 40),
        ),
        const SizedBox(height: 20),
        Text(
          _conectando ? 'Conectando a la sala segura...' : 'Sesión en curso',
          style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: AppTheme.textMain),
        ),
        const SizedBox(height: 8),
        Text(
          _conectando
              ? 'Validando tu cita y preparando la videollamada cifrada WebRTC.'
              : 'La videollamada${_nombreRemoto.isNotEmpty ? ' con $_nombreRemoto' : ''} está abierta. '
                  'Usa los controles de la sala para silenciar, cambiar de cámara o colgar.',
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 13, color: AppTheme.textMuted),
        ),
        const SizedBox(height: 16),
        const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.lock_outline, size: 14, color: AppTheme.success),
            SizedBox(width: 6),
            Text('Conexión cifrada', style: TextStyle(fontSize: 12, color: AppTheme.success)),
          ],
        ),
      ],
    );
  }

  Widget _buildError() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(color: AppTheme.warning.withOpacity(0.15), shape: BoxShape.circle),
          child: const Icon(Icons.schedule_rounded, color: AppTheme.warning, size: 48),
        ),
        const SizedBox(height: 20),
        const Text(
          'Sala no habilitada',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.textMain),
        ),
        const SizedBox(height: 10),
        Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: AppTheme.textMuted, fontSize: 13)),
        const SizedBox(height: 24),
        ElevatedButton.icon(
          onPressed: () => Navigator.pop(context),
          icon: const Icon(Icons.arrow_back_rounded),
          label: const Text('Volver a mis citas'),
        ),
      ],
    );
  }
}
