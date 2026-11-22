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

  // Reportes (CU25)
  static const String reportesMetadata = '/reportes/metadata/';
  static const String reportesPersonalizado = '/reportes/personalizado/';

  // Sprint 2 - Clinica Endpoints (HU-24, HU-30, HU-32, HU-35)
  static const String formulariosPreconsulta = '/clinica/formularios-preconsulta/';
  static const String respuestasPreconsulta = '/clinica/respuestas-preconsulta/';
  static const String tareas = '/clinica/tareas/';
  static const String consentimientos = '/clinica/consentimientos/';
  static const String firmasConsentimiento = '/clinica/firmas-consentimiento/';
  static const String iaPreconsulta = '/clinica/ia/preconsulta/analizar/';

  // Sprint 3 - Móvil & IA Endpoints (HU-41, HU-43, HU-46, HU-47, HU-48)
  static const String misCitas = '/agenda/citas/mis-citas/';
  // CU11 Móvil (HU-41 / HU-42) — rutas del Diagrama de Secuencia: /api/v1/citas/...
  static const String citasV1 = '/v1/citas/';
  static const String misCitasV1 = '/v1/citas/mis-citas/';
  static const String fcmToken = '/agenda/fcm-token/';
  static const String notificaciones = '/agenda/notificaciones/';
  static const String registroAnimo = '/clinica/registro-animo/';
  static const String clasificacionIA = '/clinica/clasificacion-ia/';
  static const String triajeAlertas = '/clinica/triaje/alertas/';
  static const String triajeAsignar = '/clinica/triaje/asignar/';

  // Sprint 4 - Finanzas (Bs./USD), Amortización, Gastos Fijos, CRM, IA Longitudinal y SaaS
  static const String finanzasCuentas = '/finanzas/cuentas/';
  static const String finanzasPagos = '/finanzas/pagos/';
  static const String finanzasPagosRegistrar = '/v1/finanzas/pagos/registrar/';
  static const String finanzasPlanesAmortizacion = '/v1/finanzas/planes-amortizacion/';
  static const String finanzasExtractoPaciente = '/v1/finanzas/extracto-paciente/';
  static const String finanzasGastosFijos = '/v1/finanzas/gastos-fijos/';
  static const String finanzasEstadoResultados = '/v1/finanzas/estado-resultados/';
  static const String finanzasExtracto = '/finanzas/extracto/';
  static const String finanzasDashboard = '/finanzas/dashboard/';
  static const String finanzasLiquidaciones = '/finanzas/liquidaciones/';
  static const String finanzasLiquidacionesPreview = '/finanzas/liquidaciones/preview/';
  static const String crmCalificaciones = '/v1/crm/calificaciones/';
  static const String crmEstadisticas = '/v1/crm/estadisticas/';
  static const String alertasRiesgoIA = '/clinica/alertas-riesgo/';
  static const String alertasRiesgoEvaluar = '/v1/clinica/ml/evaluar-riesgo/';
  static const String mlAlertasBase = '/v1/clinica/ml/alertas/';
  static const String resumenesIA = '/clinica/resumenes-ia/';
  static const String iaResumenLongitudinal = '/v1/clinica/ia/resumen-longitudinal/';
  static const String saasAdminDashboard = '/subscriptions/admin/dashboard/';
  static const String saasAdminFacturas = '/subscriptions/admin/facturas/';
  static const String saasAdminTenants = '/subscriptions/admin/tenants/';
  static const String saasQuotas = '/subscriptions/quotas/';
}
