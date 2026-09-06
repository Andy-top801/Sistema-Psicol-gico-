import 'package:flutter/material.dart';

/// Paleta de marca de SIGEPSI, alineada visualmente con el login de
/// FRONTEND (Angular) — degradado teal oscuro a teal claro.
class AppColors {
  AppColors._();

  static const brandDark = Color(0xFF0B4F5C);
  static const brandLight = Color(0xFF1E8A7E);

  static const brandGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [brandDark, brandLight],
  );
}
