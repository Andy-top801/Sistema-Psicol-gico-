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

  // Clinica Endpoints (Sprint 1 - HU-11, HU-12, HU-13, HU-14)
  static const String psicologos = '/clinica/psicologos/';
  static const String especialidades = '/clinica/especialidades/';
  static const String pacientes = '/clinica/pacientes/';
  static const String pacienteMe = '/clinica/pacientes/me/';
  static const String disponibilidad = '/clinica/disponibilidad/';

  // Agenda Endpoints (Sprint 1 - HU-15, HU-16, HU-18, HU-19, HU-20, HU-21)
  static const String citas = '/agenda/citas/';
  static const String citasSlotsDisponibles = '/agenda/citas/slots-disponibles/';
  static const String teleconsultaAccess = '/agenda/teleconsulta/';
  static const String agendaDashboard = '/agenda/dashboard/kpis/';
  static const String alertas = '/agenda/alertas/';
}
