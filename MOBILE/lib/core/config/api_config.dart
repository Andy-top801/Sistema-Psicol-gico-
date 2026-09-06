/// Configuración de red de la app. Django resuelve el tenant (centro
/// psicológico) según el header Host de la petición (django-tenants), así
/// que este valor debe apuntar al dominio del centro correcto.
///
/// Por defecto apunta a la clínica de prueba creada por
/// `python manage.py init_system` (sanamente.localhost).
///
/// Para cambiarlo sin tocar código: `flutter run --dart-define=API_BASE_URL=...`
class ApiConfig {
  ApiConfig._();

  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://sanamente.localhost:8000/api',
  );

  static const String registerEndpoint = '/users/auth/register/';
  static const String loginEndpoint = '/users/auth/login/';
  static const String refreshEndpoint = '/users/auth/refresh/';
  static const String meEndpoint = '/users/me/';

  // HU-10 / CU27 / RF-31 — flujo de CÓDIGO de 6 dígitos (móvil).
  // OJO: NO usar `/password-reset/request/` (esa acción manda un enlace con
  // token, para la web). `PasswordResetRequestView` manda el código.
  static const String passwordResetEndpoint = '/users/auth/password-reset/';
  static const String passwordResetVerifyEndpoint =
      '/users/auth/password-reset-verify/';
  static const String passwordResetConfirmEndpoint =
      '/users/auth/password-reset-confirm/';
}
