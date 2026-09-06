import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../paquetes/paquete1_admin_seguridad/providers/auth_provider.dart';

/// Pantalla inicial: intenta restaurar una sesión guardada y redirige a
/// Home o Login según corresponda. No pertenece a ningún paquete de
/// negocio (CU) — es infraestructura de navegación de la app.
class SplashScreen extends StatefulWidget {
  static const routeName = '/';

  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _restoreSession());
  }

  Future<void> _restoreSession() async {
    final authProvider = context.read<AuthProvider>();
    await authProvider.restoreSession();
    if (!mounted) return;

    final destination = authProvider.status == AuthStatus.authenticated
        ? '/home'
        : '/login';
    Navigator.of(context).pushReplacementNamed(destination);
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: CircularProgressIndicator()));
  }
}
