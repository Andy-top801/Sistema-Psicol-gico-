import '../../../core/config/api_config.dart';
import '../../../core/network/api_client.dart';

/// CU27 — Recuperar contraseña o credenciales de acceso (HU-10 / RF-31).
///
/// Caso de uso independiente de CU02 (Inicio de sesión) aunque viva en el
/// mismo paquete y comparta el mismo backend Django: se mantiene en su
/// propia clase (no mezclado con `AuthService`) para que cada una tenga
/// una sola responsabilidad. Encapsula `/api/users/auth/password-reset/`,
/// `/password-reset-verify/` y `/password-reset-confirm/`.
class PasswordResetService {
  PasswordResetService({ApiClient? apiClient})
    : _apiClient = apiClient ?? ApiClient();

  final ApiClient _apiClient;

  /// HU-10a: pide al backend que envíe un código de recuperación al correo.
  /// El backend responde con un mensaje genérico exista o no la cuenta,
  /// así que no hay nada que devolver más allá de "se completó la llamada".
  Future<void> requestPasswordReset({required String email}) async {
    await _apiClient.post(ApiConfig.passwordResetEndpoint, {'email': email});
  }

  /// HU-10b (paso intermedio): confirma que el código todavía es válido,
  /// sin cambiar la contraseña — permite avanzar automáticamente a la
  /// pantalla donde la persona escribe su nueva contraseña. Verificar no
  /// consume el código: se puede volver a usar en [confirmPasswordReset].
  /// Si es inválido o expiró, [ApiClient] lanza [ApiException].
  Future<void> verifyResetCode({required String code}) async {
    await _apiClient.post(ApiConfig.passwordResetVerifyEndpoint, {
      'code': code,
    });
  }

  /// HU-10c: con el código ya verificado, establece la nueva contraseña
  /// que la persona escribió. Si el código es inválido o expiró,
  /// [ApiClient] lanza [ApiException] con el mensaje del backend.
  Future<void> confirmPasswordReset({
    required String code,
    required String newPassword,
  }) async {
    await _apiClient.post(ApiConfig.passwordResetConfirmEndpoint, {
      'code': code,
      'new_password': newPassword,
    });
  }
}
