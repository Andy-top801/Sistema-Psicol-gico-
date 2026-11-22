import 'package:flutter/material.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'core/theme/app_theme.dart';
import 'services/auth_service.dart';
import 'screens/login_screen.dart';
import 'screens/dashboard_screen.dart';
import 'services/notificaciones_service.dart';
import 'screens/centro_notificaciones_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeDateFormatting('es', null);
  final authService = AuthService();
  await authService.init();

  // CU12 / HU-43: banner emergente y navegación al tocar una notificación
  NotificacionesService.instance
    ..onNuevaNotificacion = mostrarBannerPush
    ..abrirHandler = abrirDestinoNotificacion;

  runApp(SigepsiApp(authService: authService));
}

class SigepsiApp extends StatelessWidget {
  final AuthService authService;

  const SigepsiApp({super.key, required this.authService});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SIGEPSI Móvil',
      navigatorKey: appNavigatorKey,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: authService.isAuthenticated
          ? DashboardScreen(authService: authService)
          : LoginScreen(authService: authService),
    );
  }
}
