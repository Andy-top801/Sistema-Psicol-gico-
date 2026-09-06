import 'package:flutter/foundation.dart';

import '../../../core/network/api_exception.dart';
import '../models/usuario.dart';
import '../services/auth_service.dart';

enum AuthStatus { idle, loading, authenticated, unauthenticated, error }

/// CU02 — Estado de sesión expuesto a la UI. Traduce las operaciones de
/// [AuthService] en un estado observable por las pantallas de
/// login/registro/splash/home vía `provider`.
class AuthProvider extends ChangeNotifier {
  AuthProvider({AuthService? authService})
    : _authService = authService ?? AuthService();

  final AuthService _authService;

  AuthStatus status = AuthStatus.idle;
  Usuario? currentUser;
  String? errorMessage;

  Future<void> restoreSession() async {
    status = AuthStatus.loading;
    notifyListeners();

    final hasSession = await _authService.hasSession();
    if (!hasSession) {
      status = AuthStatus.unauthenticated;
      notifyListeners();
      return;
    }

    try {
      currentUser = await _authService.fetchMe();
      status = AuthStatus.authenticated;
    } catch (_) {
      // Token guardado ya no es válido (expiró, se revocó, etc.).
      await _authService.logout();
      status = AuthStatus.unauthenticated;
    }
    notifyListeners();
  }

  Future<bool> login({required String email, required String password}) {
    return _runAuthAction(
      () => _authService.login(email: email, password: password),
    );
  }

  Future<bool> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String phone = '',
  }) {
    return _runAuthAction(
      () => _authService.register(
        email: email,
        password: password,
        firstName: firstName,
        lastName: lastName,
        phone: phone,
      ),
    );
  }

  Future<bool> _runAuthAction(Future<Usuario> Function() action) async {
    status = AuthStatus.loading;
    errorMessage = null;
    notifyListeners();

    try {
      currentUser = await action();
      status = AuthStatus.authenticated;
      notifyListeners();
      return true;
    } on ApiException catch (e) {
      errorMessage = e.message;
      status = AuthStatus.error;
      notifyListeners();
      return false;
    } catch (_) {
      errorMessage =
          'No se pudo conectar con el servidor. Verifica tu conexión.';
      status = AuthStatus.error;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    currentUser = null;
    status = AuthStatus.unauthenticated;
    notifyListeners();
  }
}
