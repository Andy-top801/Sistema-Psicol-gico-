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

  // HU-10 / CU27 / RF-31
  static const String passwordResetEndpoint = '/users/auth/password-reset/request/';
  static const String passwordResetVerifyEndpoint =
      '/users/auth/password-reset-verify/';
  static const String passwordResetConfirmEndpoint =
      '/users/auth/password-reset-confirm/';
}
