import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

/// Servicio nativo de permisos de Cámara y Micrófono para Teleconsulta WebRTC (CU13 / HU-44).
class PermissionService {
  static const MethodChannel _channel = MethodChannel('com.example.sigepsi_movil/permissions');

  /// Solicita explícitamente los permisos de Cámara y Micrófono en el dispositivo físico (CU13 / HU-44)
  static Future<bool> requestCameraAndAudioPermissions() async {
    if (kIsWeb) return true;
    try {
      final bool? granted = await _channel.invokeMethod<bool>('requestCameraPermission');
      return granted ?? false;
    } catch (e) {
      debugPrint('[Permissions] Error solicitando permisos de cámara en móvil: $e');
      return false;
    }
  }

  /// Verifica si ya están otorgados los permisos de Cámara y Micrófono en el dispositivo físico
  static Future<bool> checkCameraAndAudioPermissions() async {
    if (kIsWeb) return true;
    try {
      final bool? granted = await _channel.invokeMethod<bool>('checkCameraPermission');
      return granted ?? false;
    } catch (e) {
      debugPrint('[Permissions] Error verificando permisos de cámara: $e');
      return false;
    }
  }
}
