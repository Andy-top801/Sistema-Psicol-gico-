class ApiConstants {
  // Con adb reverse tcp:8000 tcp:8000 o en Web, se usa localhost:8000
  // Si se usa emulador sin adb reverse, cambiar a 10.0.2.2:8000
  static const String baseUrl = 'http://localhost:8000/api';
  static const String webBaseUrl = 'http://localhost:8000/api';

  // Auth Endpoints
  static const String login = '/auth/login/';
  static const String register = '/auth/register/';
  static const String logout = '/auth/logout/';
  static const String passwordReset = '/auth/password-reset/';
  static const String passwordResetConfirm = '/auth/password-reset-confirm/';
  static const String me = '/auth/me/';

  // Tenant Endpoints
  static const String tenants = '/tenants/';
  static const String publicTenants = '/tenants/public/';

  // User & Roles Endpoints
  static const String users = '/users/';
  static const String roles = '/roles/';
  static const String permisos = '/permisos/';

  // Clinic Config
  static const String centroConfig = '/centro/config/';
}
