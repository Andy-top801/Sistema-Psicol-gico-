import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../paquetes/paquete1_admin_seguridad/providers/auth_provider.dart';

/// Destino placeholder tras iniciar sesión o registrarse (CU02). No
/// implementa funcionalidad real de paciente (eso corresponde a los
/// paquetes de sprints posteriores) — solo confirma que el flujo de
/// login/registro llega a buen término.
class HomeScreen extends StatelessWidget {
  static const routeName = '/home';

  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final usuario = authProvider.currentUser;

    return Scaffold(
      appBar: AppBar(
        title: const Text('SIGEPSI'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Cerrar sesión',
            onPressed: () async {
              await authProvider.logout();
              if (context.mounted) {
                Navigator.of(
                  context,
                ).pushNamedAndRemoveUntil('/login', (_) => false);
              }
            },
          ),
        ],
      ),
      body: Center(
        child: Text(
          'Bienvenido, ${usuario?.firstName ?? ''}',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
      ),
    );
  }
}
