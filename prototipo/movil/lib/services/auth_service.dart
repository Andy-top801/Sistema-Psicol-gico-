// ==============================================================================
// MÓDULO: auth_service.dart
// CAPA BCE: CONTROL (Cliente Móvil / Service Adapter)
// CASOS DE USO: CU2: Iniciar Sesión (HU-01, HU-02)
//               CU2 (Logout): Cerrar Sesión Seguro (HU-09)
//               CU27: Recuperar Contraseña vía Token/Email (HU-27)
// DESCRIPCIÓN: Servicio cliente de autenticación, sesión y tokens JWT para la app móvil.
//              Conecta las pantallas Boundary (IU_Login, IU_RecuperarPassword, etc.)
//              con los Controladores Django REST API del backend.
// ==============================================================================
import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants/api_constants.dart';
import '../models/user_model.dart';
import '../models/tenant_model.dart';

class AuthService extends ChangeNotifier {
  UserModel? _currentUser;
  TenantModel? _currentTenant;
  String? _accessToken;
  String? _refreshToken;
  String? _customBaseUrl;
  String? lastErrorMessage;

  UserModel? get currentUser => _currentUser;
  TenantModel? get currentTenant => _currentTenant;
  bool get isAuthenticated => _accessToken != null;
  bool get isSuperAdmin => _currentUser?.isSuperAdmin ?? false;
  bool get isAdminCentro => _currentUser?.isAdminCentro ?? false;
  bool get isPsicologo => _currentUser?.isPsicologo ?? false;
  bool get isPaciente => _currentUser?.isPaciente ?? false;
  bool get isRecepcionista => _currentUser?.isRecepcionista ?? false;

  bool hasPermission(String codigo) => _currentUser?.hasPermission(codigo) ?? false;

  String get baseUrl => _customBaseUrl ?? (kIsWeb ? ApiConstants.webBaseUrl : ApiConstants.baseUrl);

  Future<void> refreshProfile() async {
    if (!isAuthenticated) return;
    try {
      final url = Uri.parse('$baseUrl${ApiConstants.me}');
      final response = await http.get(url, headers: getHeaders()).timeout(const Duration(seconds: 4));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['usuario'] != null) {
          final uMap = Map<String, dynamic>.from(data['usuario']);
          if (data['permisos'] != null && data['permisos'] is List) {
            uMap['permisos'] = data['permisos'];
          }
          _currentUser = UserModel.fromJson(uMap);
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('user_data', jsonEncode(uMap));
          notifyListeners();
        }
      }
    } catch (_) {}
  }

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _accessToken = prefs.getString('access_token');
    _refreshToken = prefs.getString('refresh_token');
    _customBaseUrl = prefs.getString('custom_base_url');

    final userJson = prefs.getString('user_data');
    if (userJson != null) {
      _currentUser = UserModel.fromJson(jsonDecode(userJson));
    }
    final tenantJson = prefs.getString('tenant_data');
    if (tenantJson != null) {
      _currentTenant = TenantModel.fromJson(jsonDecode(tenantJson));
    }
    notifyListeners();
  }

  Future<void> setCustomBaseUrl(String? url) async {
    final prefs = await SharedPreferences.getInstance();
    if (url != null && url.trim().isNotEmpty) {
      var clean = url.trim();
      if (clean.endsWith('/')) {
        clean = clean.substring(0, clean.length - 1);
      }
      if (!clean.endsWith('/api')) {
        clean = '$clean/api';
      }
      _customBaseUrl = clean;
      await prefs.setString('custom_base_url', clean);
    } else {
      _customBaseUrl = null;
      await prefs.remove('custom_base_url');
    }
    notifyListeners();
  }

  Future<bool> testConnection({String? testUrl}) async {
    final target = testUrl ?? baseUrl;
    try {
      final url = Uri.parse('$target${ApiConstants.publicTenants}');
      final response = await http.get(url).timeout(const Duration(seconds: 4));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  void setTenant(TenantModel? tenant) async {
    _currentTenant = tenant;
    final prefs = await SharedPreferences.getInstance();
    if (tenant != null) {
      prefs.setString('tenant_data', jsonEncode({
        'id': tenant.id,
        'nombre': tenant.nombre,
        'slug': tenant.slug,
        'schema_name': tenant.schemaName,
      }));
    } else {
      prefs.remove('tenant_data');
    }
    notifyListeners();
  }

  Map<String, String> getHeaders() {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (_accessToken != null) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }
    if (_currentTenant != null) {
      headers['X-Tenant-ID'] = _currentTenant!.slug;
    }
    return headers;
  }

  /// ═════════════════════════════════════════════════════════════════════════
  /// CU2: Gestionar Inicio de Sesión y Autenticación (HU-01, HU-02)
  /// Diagrama de Comunicación – Autenticación JWT y Carga de Perfil
  /// Participantes:
  ///   Actor  → Usuario del Sistema (Admin, Psicólogo, Recepcionista, Paciente)
  ///   IU     → IU_Login (Móvil)
  ///   CTR    → AuthService (Cliente) ➔ CTR_Autenticacion (Django REST: CustomTokenObtainPairView)
  ///   CE     → CE_Usuario (PostgreSQL: accounts_usuario)
  /// ═════════════════════════════════════════════════════════════════════════
  Future<bool> login(String email, String password, {String? tenantSlug}) async {
    lastErrorMessage = null;
    try {
      // ---------------------------------------------------------------------
      // CU2 Paso 2: Envío de credenciales POST a CTR_Autenticacion (/api/auth/login/)
      // ---------------------------------------------------------------------
      final url = Uri.parse('$baseUrl${ApiConstants.login}');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
          if (tenantSlug != null && tenantSlug.isNotEmpty) 'tenant': tenantSlug,
        }),
      ).timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        // -------------------------------------------------------------------
        // CU2 Paso 9: CTR_Autenticacion retorna 200 OK con tokens JWT y datos de sesión
        // CU2 Paso 10: Se almacenan tokens y se notifica autenticación exitosa a IU_Login
        // -------------------------------------------------------------------
        final data = jsonDecode(response.body);
        _accessToken = data['access'];
        _refreshToken = data['refresh'];
        _currentUser = UserModel.fromJson(data['usuario']);

        final prefs = await SharedPreferences.getInstance();
        prefs.setString('access_token', _accessToken!);
        prefs.setString('refresh_token', _refreshToken!);
        prefs.setString('user_data', jsonEncode(data['usuario']));

        notifyListeners();
        return true;
      } else {
        try {
          final data = jsonDecode(response.body);
          lastErrorMessage = data['non_field_errors']?[0] ??
              data['detail'] ??
              data['error'] ??
              data['email']?[0] ??
              'Credenciales inválidas o centro suspendido.';
        } catch (_) {
          lastErrorMessage = 'Error del servidor (Código ${response.statusCode}).';
        }
        return false;
      }
    } on TimeoutException {
      lastErrorMessage = 'Tiempo de espera agotado al conectar a $baseUrl. Verifica la IP del servidor.';
      return false;
    } catch (e) {
      lastErrorMessage = 'No se pudo conectar con el servidor ($baseUrl).\n'
          'Si estás en un celular físico por USB, ejecuta en tu PC:\n'
          'adb reverse tcp:8000 tcp:8000';
      return false;
    }
  }

  /// ═════════════════════════════════════════════════════════════════════════
  /// CU2 (Logout): Cierre de Sesión Seguro (HU-09)
  /// Diagrama de Comunicación – Cierre de Sesión y Revocación de Refresh Token
  /// Participantes:
  ///   Actor  → Usuario Activo
  ///   IU     → IU_BarraNavegacion / IU_MenuPrincipal (Móvil)
  ///   CTR    → AuthService (Cliente) ➔ CTR_Autenticacion (Django REST: LogoutView)
  ///   CE     → CE_BlacklistedToken (PostgreSQL / Redis)
  /// ═════════════════════════════════════════════════════════════════════════
  Future<void> logout() async {
    // -----------------------------------------------------------------------
    // CU2 Logout Paso 2: Notificar revocación a CTR_Autenticacion (/api/auth/logout/)
    // -----------------------------------------------------------------------
    if (_refreshToken != null) {
      try {
        final url = Uri.parse('$baseUrl${ApiConstants.logout}');
        await http.post(
          url,
          headers: getHeaders(),
          body: jsonEncode({'refresh': _refreshToken}),
        ).timeout(const Duration(seconds: 3));
      } catch (_) {}
    }

    // -----------------------------------------------------------------------
    // CU2 Logout Paso 7: Limpiar tokens y sesión local en el cliente móvil
    // -----------------------------------------------------------------------
    _accessToken = null;
    _refreshToken = null;
    _currentUser = null;

    final prefs = await SharedPreferences.getInstance();
    prefs.remove('access_token');
    prefs.remove('refresh_token');
    prefs.remove('user_data');
    notifyListeners();
  }

  Future<List<TenantModel>> getPublicTenants() async {
    try {
      final url = Uri.parse('$baseUrl${ApiConstants.publicTenants}');
      final response = await http.get(url).timeout(const Duration(seconds: 5));
      if (response.statusCode == 200) {
        final List list = jsonDecode(response.body);
        return list.map((e) => TenantModel.fromJson(e)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// ═════════════════════════════════════════════════════════════════════════
  /// CU27: Recuperar Contraseña vía Token/Email (HU-27)
  /// Diagrama de Comunicación – Fase 1: Solicitud de Token
  /// Participantes:
  ///   Actor  → Usuario Olvidadizo
  ///   IU     → IU_SolicitarReset (Móvil: PasswordResetScreen)
  ///   CTR    → AuthService (Cliente) ➔ CTR_RecuperarPassword (Django REST: PasswordResetRequestView)
  ///   CE     → CE_PasswordResetToken (PostgreSQL)
  /// ═════════════════════════════════════════════════════════════════════════
  Future<Map<String, dynamic>> requestPasswordReset(String email, {String? tenantSlug}) async {
    try {
      // ---------------------------------------------------------------------
      // CU27 Paso 2: Envío de solicitud POST a CTR_RecuperarPassword (/api/auth/password-reset/)
      // ---------------------------------------------------------------------
      final url = Uri.parse('$baseUrl${ApiConstants.passwordReset}');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          if (tenantSlug != null && tenantSlug.isNotEmpty) 'tenant': tenantSlug,
        }),
      ).timeout(const Duration(seconds: 8));

      // ---------------------------------------------------------------------
      // CU27 Paso 7: CTR_RecuperarPassword retorna confirmación de token emitido
      // ---------------------------------------------------------------------
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'data': data};
      } else {
        final err = data['email']?[0] ?? data['non_field_errors']?[0] ?? 'Error al solicitar recuperación.';
        return {'success': false, 'error': err};
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Error de conexión con el servidor ($baseUrl). Verifica la conectividad.',
      };
    }
  }

  /// ═════════════════════════════════════════════════════════════════════════
  /// CU27: Recuperar Contraseña vía Token/Email (HU-27)
  /// Diagrama de Comunicación – Fase 2: Confirmación con Token
  /// Participantes:
  ///   Actor  → Usuario Olvidadizo
  ///   IU     → IU_ConfirmarReset (Móvil: PasswordResetScreen)
  ///   CTR    → AuthService (Cliente) ➔ CTR_RecuperarPassword (Django REST: PasswordResetConfirmView)
  ///   CE     → CE_PasswordResetToken & CE_Usuario (PostgreSQL)
  /// ═════════════════════════════════════════════════════════════════════════
  Future<Map<String, dynamic>> confirmPasswordReset({
    required String token,
    required String password,
    required String passwordConfirm,
  }) async {
    try {
      // ---------------------------------------------------------------------
      // CU27 Paso 10: Envío de token y nueva contraseña POST a CTR_RecuperarPassword
      // ---------------------------------------------------------------------
      final url = Uri.parse('$baseUrl${ApiConstants.passwordResetConfirm}');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'token': token,
          'password': password,
          'password_confirm': passwordConfirm,
        }),
      ).timeout(const Duration(seconds: 8));

      // ---------------------------------------------------------------------
      // CU27 Paso 15: CTR_RecuperarPassword retorna 200 OK con mensaje de éxito
      // ---------------------------------------------------------------------
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'message': data['mensaje'] ?? 'Contraseña restablecida exitosamente.'};
      } else {
        final err = data['non_field_errors']?[0] ?? data['token']?[0] ?? data['password']?[0] ?? 'Error al restablecer contraseña.';
        return {'success': false, 'error': err};
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Error de conexión al confirmar restablecimiento.',
      };
    }
  }
}
