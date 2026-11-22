// ==============================================================================
// MÓDULO: notificaciones_service.dart
// CASO DE USO: CU12 / HU-43 — Recepción de recordatorios automáticos de citas
//              y notificaciones push (FCM) en la app móvil del Paciente.
//
// Criterios de aceptación:
//  (a) Al iniciar sesión, el token del dispositivo se registra en
//      comunicacion_tokenfcm (POST /api/agenda/fcm-token/).
//  (b) Los recordatorios 'Recordatorio de Consulta' (24 h y 1 h antes) llegan al
//      teléfono como notificación del sistema (Android/iOS) y como banner emergente.
//  (c) Al presionar la notificación, la app abre la teleconsulta (VIRTUAL) o la
//      pantalla de detalle de la cita (PRESENCIAL).
//
// Modo SANDBOX: sin google-services.json no existe token FCM real; se genera un
// token de dispositivo persistente y la app recibe los avisos consultando el
// centro de notificaciones cada 30 s. Con Firebase configurado, el backend envía
// la push real a través de FCM sin cambios en el flujo.
// ==============================================================================
import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../core/constants/api_constants.dart';
import '../models/cita_model.dart';
import 'auth_service.dart';

/// Navegador global para abrir pantallas desde una notificación (criterio c).
final GlobalKey<NavigatorState> appNavigatorKey = GlobalKey<NavigatorState>();

class NotificacionModel {
  final String id;
  final String tipoEvento;
  final String titulo;
  final String cuerpo;
  final bool leida;
  final String citaId;
  final String modalidad;
  final String fechaCita;
  final String horaCita;
  final String psicologoNombre;
  final DateTime? fechaEnvio;

  NotificacionModel({
    required this.id,
    required this.tipoEvento,
    required this.titulo,
    required this.cuerpo,
    required this.leida,
    required this.citaId,
    required this.modalidad,
    required this.fechaCita,
    required this.horaCita,
    required this.psicologoNombre,
    this.fechaEnvio,
  });

  bool get esVirtual => modalidad == 'VIRTUAL';
  bool get esUnaHora => tipoEvento == 'RECORDATORIO_1H';

  NotificacionModel copyWith({bool? leida}) => NotificacionModel(
        id: id,
        tipoEvento: tipoEvento,
        titulo: titulo,
        cuerpo: cuerpo,
        leida: leida ?? this.leida,
        citaId: citaId,
        modalidad: modalidad,
        fechaCita: fechaCita,
        horaCita: horaCita,
        psicologoNombre: psicologoNombre,
        fechaEnvio: fechaEnvio,
      );

  factory NotificacionModel.fromJson(Map<String, dynamic> j) => NotificacionModel(
        id: j['id']?.toString() ?? '',
        tipoEvento: j['tipo_evento']?.toString() ?? '',
        titulo: j['titulo']?.toString() ?? 'Recordatorio de Consulta',
        cuerpo: j['cuerpo']?.toString() ?? '',
        leida: j['leida'] == true,
        citaId: j['cita_id']?.toString() ?? '',
        modalidad: j['modalidad']?.toString() ?? 'PRESENCIAL',
        fechaCita: j['fecha_cita']?.toString() ?? '',
        horaCita: j['hora_cita']?.toString() ?? '',
        psicologoNombre: j['psicologo_nombre']?.toString() ?? '',
        fechaEnvio: DateTime.tryParse(j['fecha_envio']?.toString() ?? '')?.toLocal(),
      );
}

class NotificacionesService extends ChangeNotifier {
  NotificacionesService._();
  static final NotificacionesService instance = NotificacionesService._();

  static const _tokenKey = 'sigepsi_fcm_device_token';
  static const _pollInterval = Duration(seconds: 30);

  final FlutterLocalNotificationsPlugin _local = FlutterLocalNotificationsPlugin();
  AuthService? _auth;
  Timer? _timer;
  Set<String>? _idsConocidos;
  bool _localInicializado = false;

  List<NotificacionModel> items = [];
  bool cargando = false;
  String? error;

  /// Callback para mostrar el banner emergente dentro de la app.
  void Function(NotificacionModel n)? onNuevaNotificacion;

  int get noLeidas => items.where((n) => !n.leida).length;
  AuthService? get auth => _auth;

  bool get _soportaNotifSistema =>
      !kIsWeb && (defaultTargetPlatform == TargetPlatform.android || defaultTargetPlatform == TargetPlatform.iOS);

  String get _plataforma {
    if (kIsWeb) return 'WEB';
    return defaultTargetPlatform == TargetPlatform.iOS ? 'IOS' : 'ANDROID';
  }

  // ───────────────────────────── Ciclo de vida ─────────────────────────────

  /// Se llama al entrar al panel del paciente (inmediatamente después del login).
  Future<void> iniciar(AuthService auth) async {
    if (_auth == auth && _timer != null) return;
    _auth = auth;
    _idsConocidos = null;
    await _inicializarNotifSistema();
    await registrarDispositivo();
    await cargar();
    _timer?.cancel();
    _timer = Timer.periodic(_pollInterval, (_) => cargar());
  }

  /// Al cerrar sesión: el dispositivo deja de recibir pushes de este paciente.
  Future<void> detener() async {
    _timer?.cancel();
    _timer = null;
    final auth = _auth;
    if (auth != null) {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString(_tokenKey);
      if (token != null) {
        try {
          await http.delete(
            Uri.parse('${auth.baseUrl}${ApiConstants.fcmToken}'),
            headers: auth.getHeaders(),
            body: jsonEncode({'token': token}),
          );
        } catch (_) {}
      }
    }
    _auth = null;
    items = [];
    _idsConocidos = null;
    notifyListeners();
  }

  // ─────────────────────────── Criterio (a) ───────────────────────────

  Future<bool> registrarDispositivo() async {
    final auth = _auth;
    if (auth == null) return false;
    final prefs = await SharedPreferences.getInstance();
    var token = prefs.getString(_tokenKey);
    if (token == null) {
      final r = Random.secure();
      final hex = List.generate(16, (_) => r.nextInt(256).toRadixString(16).padLeft(2, '0')).join();
      token = '${_plataforma.toLowerCase()}-sandbox-$hex';
      await prefs.setString(_tokenKey, token);
    }
    try {
      final resp = await http.post(
        Uri.parse('${auth.baseUrl}${ApiConstants.fcmToken}'),
        headers: auth.getHeaders(),
        body: jsonEncode({'token': token, 'plataforma': _plataforma}),
      );
      return resp.statusCode == 200 || resp.statusCode == 201;
    } catch (_) {
      return false;
    }
  }

  // ─────────────────────────── Criterio (b) ───────────────────────────

  Future<void> cargar() async {
    final auth = _auth;
    if (auth == null) return;
    cargando = true;
    notifyListeners();
    try {
      final resp = await http
          .get(Uri.parse('${auth.baseUrl}${ApiConstants.notificaciones}'), headers: auth.getHeaders())
          .timeout(const Duration(seconds: 8));
      if (resp.statusCode == 200) {
        final data = jsonDecode(utf8.decode(resp.bodyBytes));
        final lista = (data['resultados'] as List? ?? [])
            .map((e) => NotificacionModel.fromJson(Map<String, dynamic>.from(e)))
            .toList();
        _detectarNuevas(lista);
        items = lista;
        error = null;
      } else {
        error = 'No se pudieron cargar las notificaciones (${resp.statusCode}).';
      }
    } catch (_) {
      error = 'Sin conexión con el servidor.';
    }
    cargando = false;
    notifyListeners();
  }

  void _detectarNuevas(List<NotificacionModel> lista) {
    final conocidos = _idsConocidos;
    _idsConocidos = lista.map((n) => n.id).toSet();
    if (conocidos == null) return; // primera carga: no se re-anuncian avisos antiguos
    for (final n in lista.where((n) => !n.leida && !conocidos.contains(n.id))) {
      // CU12-paso 11: notificacion_push_emergente() — notificación del sistema y banner en el smartphone
      _mostrarNotifSistema(n);
      // CU12-paso 12: recepcion_confirmada [retorno] — con Firebase real la confirma el SDK de FCM;
      //               en modo SANDBOX la app recibe el aviso al consultar el centro de notificaciones.
      onNuevaNotificacion?.call(n);
    }
  }

  Future<void> _inicializarNotifSistema() async {
    if (!_soportaNotifSistema || _localInicializado) return;
    try {
      await _local.initialize(
        settings: const InitializationSettings(
          android: AndroidInitializationSettings('@mipmap/ic_launcher'),
          iOS: DarwinInitializationSettings(),
        ),
        onDidReceiveNotificationResponse: (resp) {
          final citaId = resp.payload;
          final n = items.where((x) => x.citaId == citaId).firstOrNull;
          if (n != null) abrir(n);
        },
      );
      await _local
          .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
          ?.requestNotificationsPermission();
      _localInicializado = true;
    } catch (e) {
      debugPrint('[CU12] Notificaciones del sistema no disponibles: $e');
    }
  }

  Future<void> _mostrarNotifSistema(NotificacionModel n) async {
    if (!_localInicializado) return;
    try {
      await _local.show(
        id: n.id.hashCode & 0x7fffffff,
        title: n.titulo,
        body: n.cuerpo,
        payload: n.citaId,
        notificationDetails: NotificationDetails(
          android: AndroidNotificationDetails(
            'sigepsi_recordatorios',
            'Recordatorios de citas',
            channelDescription: 'Avisos 24 h y 1 h antes de tus sesiones (CU12)',
            importance: Importance.max,
            priority: Priority.high,
            color: const Color(0xFF19734E),
            styleInformation: BigTextStyleInformation(n.cuerpo),
          ),
          iOS: const DarwinNotificationDetails(presentAlert: true, presentSound: true),
        ),
      );
    } catch (e) {
      debugPrint('[CU12] No se pudo mostrar la notificación: $e');
    }
  }

  // ─────────────────────────── Criterio (c) ───────────────────────────

  Future<void> marcarLeida(NotificacionModel n) async {
    final auth = _auth;
    if (auth == null || n.leida) return;
    items = items.map((x) => x.id == n.id ? x.copyWith(leida: true) : x).toList();
    notifyListeners();
    try {
      await http.post(
        Uri.parse('${auth.baseUrl}${ApiConstants.notificaciones}${n.id}/leer/'),
        headers: auth.getHeaders(),
      );
    } catch (_) {}
  }

  Future<void> marcarTodasLeidas() async {
    final auth = _auth;
    if (auth == null) return;
    items = items.map((x) => x.copyWith(leida: true)).toList();
    notifyListeners();
    try {
      await http.post(
        Uri.parse('${auth.baseUrl}${ApiConstants.notificaciones}leer-todas/'),
        headers: auth.getHeaders(),
      );
    } catch (_) {}
  }

  Future<CitaModel?> obtenerCita(String citaId) async {
    final auth = _auth;
    if (auth == null) return null;
    try {
      final resp = await http.get(
        Uri.parse('${auth.baseUrl}${ApiConstants.citas}$citaId/'),
        headers: auth.getHeaders(),
      );
      if (resp.statusCode == 200) {
        return CitaModel.fromJson(Map<String, dynamic>.from(jsonDecode(utf8.decode(resp.bodyBytes))));
      }
    } catch (_) {}
    return null;
  }

  /// Registrado por la pantalla del centro de notificaciones para resolver la navegación.
  Future<void> Function(NotificacionModel n)? abrirHandler;

  Future<void> abrir(NotificacionModel n) async {
    await marcarLeida(n);
    await abrirHandler?.call(n);
  }
}
