import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../paquetes/paquete1_admin_seguridad/providers/auth_provider.dart';

/// Destino tras iniciar sesión (CU02). La app móvil está orientada al
/// paciente; el personal puede entrar pero se le indica que la gestión
/// se hace desde la web. Las funciones reales del paciente llegan en
/// sprints posteriores.
class HomeScreen extends StatelessWidget {
  static const routeName = '/home';

  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final usuario = authProvider.currentUser;
    final esPaciente = usuario?.esPaciente ?? false;

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
                Navigator.of(context)
                    .pushNamedAndRemoveUntil('/login', (_) => false);
              }
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Hola, ${usuario?.firstName ?? ''}',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 4),
            Text(
              usuario?.email ?? '',
              style: TextStyle(color: Colors.grey.shade600),
            ),
            const SizedBox(height: 24),
            if (esPaciente) ...[
              _Card(
                icon: Icons.event_available,
                title: 'Portal del paciente',
                text:
                    'Aquí verás tus próximas citas, teleconsultas y tareas '
                    'terapéuticas. (Disponible en los próximos sprints.)',
              ),
            ] else ...[
              _Card(
                icon: Icons.desktop_windows,
                title: 'Cuenta de personal',
                text:
                    'La gestión de pacientes, agenda y expedientes se realiza '
                    'desde la versión web de SIGEPSI. Puedes cerrar sesión aquí.',
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _Card extends StatelessWidget {
  const _Card({required this.icon, required this.title, required this.text});

  final IconData icon;
  final String title;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: Theme.of(context).colorScheme.primary),
            const SizedBox(height: 12),
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 6),
            Text(text, style: TextStyle(color: Colors.grey.shade700)),
          ],
        ),
      ),
    );
  }
}
