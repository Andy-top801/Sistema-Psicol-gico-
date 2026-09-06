import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

/// Encabezado de marca compartido por las pantallas del Paquete 1
/// (CU02 Inicio de sesión, CU27 Recuperar contraseña): degradado teal,
/// ícono, título y (opcionalmente) una lista corta de bullets — mismo
/// lenguaje visual que el panel izquierdo del login web.
class AuthHeader extends StatelessWidget {
  const AuthHeader({
    super.key,
    required this.title,
    required this.subtitle,
    this.features = const [],
    this.compact = false,
  });

  final String title;
  final String subtitle;
  final List<String> features;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.fromLTRB(24, compact ? 48 : 64, 24, 40),
      decoration: const BoxDecoration(gradient: AppColors.brandGradient),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(
              Icons.monitor_heart_outlined,
              color: Colors.white,
              size: 30,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.5,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            subtitle,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.85),
              fontSize: 14,
              height: 1.4,
            ),
          ),
          if (features.isNotEmpty) ...[
            const SizedBox(height: 20),
            for (final feature in features)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    const Icon(
                      Icons.check_circle,
                      color: Colors.white,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        feature,
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.9),
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ],
      ),
    );
  }
}
