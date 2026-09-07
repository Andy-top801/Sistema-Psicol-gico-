import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'services/auth_service.dart';
import 'screens/login_screen.dart';
import 'screens/dashboard_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final authService = AuthService();
  await authService.init();

  runApp(SigepsiApp(authService: authService));
}

class SigepsiApp extends StatelessWidget {
  final AuthService authService;

  const SigepsiApp({super.key, required this.authService});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SIGEPSI Móvil',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: authService.isAuthenticated
          ? DashboardScreen(authService: authService)
          : LoginScreen(authService: authService),
    );
  }
}
