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
  bool get isSuperAdmin => _currentUser?.rolNombre == 'SuperAdmin';
  bool get isAdminCentro => _currentUser?.rolNombre == 'Admin Centro';

  String get baseUrl => _customBaseUrl ?? (kIsWeb ? ApiConstants.webBaseUrl : ApiConstants.baseUrl);

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
  /// ═════════════════════════════════════════════════════════════════════════
  Future<bool> login(String email, String password, {String? tenantSlug}) async {
    lastErrorMessage = null;
    try {
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
  /// ═════════════════════════════════════════════════════════════════════════
  Future<void> logout() async {
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

  /// CU27: Solicitar Token de Recuperación de Contraseña
  Future<Map<String, dynamic>> requestPasswordReset(String email, {String? tenantSlug}) async {
    try {
      final url = Uri.parse('$baseUrl${ApiConstants.passwordReset}');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          if (tenantSlug != null && tenantSlug.isNotEmpty) 'tenant': tenantSlug,
        }),
      ).timeout(const Duration(seconds: 8));

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

  /// CU27: Confirmar Nueva Contraseña con Token
  Future<Map<String, dynamic>> confirmPasswordReset({
    required String token,
    required String password,
    required String passwordConfirm,
  }) async {
    try {
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
