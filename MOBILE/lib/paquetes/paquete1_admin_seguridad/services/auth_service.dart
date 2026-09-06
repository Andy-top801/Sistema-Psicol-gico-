import '../../../core/config/api_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/storage/token_storage.dart';
import '../models/auth_tokens.dart';
import '../models/usuario.dart';

/// CU02 — Gestionar inicio de sesión y autenticación (HU-01, HU-02, HU-09;
/// en el móvil, backlog SP3-1..3). Encapsula la comunicación con
/// `/api/users/auth/login/`, `/auth/register/`, `/auth/refresh/` y
/// `/api/users/me/`.
///
/// La recuperación de contraseña (CU27) vive en
/// `services/password_reset_service.dart` — son casos de uso distintos
/// aunque comparten el mismo backend Django y el mismo paquete.
class AuthService {
  AuthService({ApiClient? apiClient, TokenStorage? tokenStorage})
    : _apiClient = apiClient ?? ApiClient(),
      _tokenStorage = tokenStorage ?? TokenStorage();

  final ApiClient _apiClient;
  final TokenStorage _tokenStorage;

  /// Registra un nuevo paciente y deja la sesión iniciada (el backend
  /// devuelve tokens listos para usar junto con el perfil creado).
  Future<Usuario> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String phone = '',
  }) async {
    final response = await _apiClient.post(ApiConfig.registerEndpoint, {
      'email': email,
      'password': password,
      'first_name': firstName,
      'last_name': lastName,
      'phone': phone,
    });

    final tokens = AuthTokens.fromJson(response);
    await _tokenStorage.saveTokens(
      access: tokens.access,
      refresh: tokens.refresh,
    );
    return Usuario.fromJson(response['user'] as Map<String, dynamic>);
  }

  /// Inicia sesión con credenciales existentes. El login solo devuelve
  /// tokens (contrato de SimpleJWT), así que se completa con [fetchMe]
  /// para obtener el perfil del usuario.
  Future<Usuario> login({
    required String email,
    required String password,
  }) async {
    final response = await _apiClient.post(ApiConfig.loginEndpoint, {
      'email': email,
      'password': password,
    });

    final tokens = AuthTokens.fromJson(response);
    await _tokenStorage.saveTokens(
      access: tokens.access,
      refresh: tokens.refresh,
    );
    return fetchMe();
  }

  Future<Usuario> fetchMe() async {
    final response = await _apiClient.get(
      ApiConfig.meEndpoint,
      authenticated: true,
    );
    return Usuario.fromJson(response);
  }

  Future<void> refreshToken() async {
    final refresh = await _tokenStorage.readRefreshToken();
    if (refresh == null) return;
    final response = await _apiClient.post(ApiConfig.refreshEndpoint, {
      'refresh': refresh,
    });
    await _tokenStorage.saveAccessToken(response['access'] as String);
  }

  /// Solo limpia la sesión local: no existe endpoint de blacklist de
  /// tokens en el backend (djangorestframework_simplejwt.token_blacklist
  /// no está instalado), así que el logout es puramente del lado cliente.
  Future<void> logout() async {
    await _tokenStorage.clear();
  }

  Future<bool> hasSession() async {
    final token = await _tokenStorage.readAccessToken();
    return token != null;
  }
}
