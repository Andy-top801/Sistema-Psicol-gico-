import 'package:sigepsi_mobile/core/storage/token_storage.dart';

/// Doble de prueba en memoria: evita depender del canal de plataforma real
/// de flutter_secure_storage en tests unitarios/de widget. Compartido por
/// los tests de todos los CU del Paquete 1 que necesitan un `TokenStorage`.
class FakeTokenStorage extends TokenStorage {
  final Map<String, String> _values = {};

  @override
  Future<void> saveTokens({
    required String access,
    required String refresh,
  }) async {
    _values['access'] = access;
    _values['refresh'] = refresh;
  }

  @override
  Future<void> saveAccessToken(String access) async {
    _values['access'] = access;
  }

  @override
  Future<String?> readAccessToken() async => _values['access'];

  @override
  Future<String?> readRefreshToken() async => _values['refresh'];

  @override
  Future<void> clear() async => _values.clear();
}
