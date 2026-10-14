import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Paleta Principal (Forest & Mint Luxury Theme — Alineada con Web)
  static const Color primary = Color(0xFF19734E);
  static const Color primaryLight = Color(0xFF2EC486);
  static const Color primaryDark = Color(0xFF135D3E);
  static const Color secondary = Color(0xFF0F2922);
  static const Color accent = Color(0xFF38BDF8);

  // Fondos y Superficies Cristalinas (Dark Glassmorphism)
  static const Color background = Color(0xFF0B1E19);
  static const Color cardBg = Color(0xFF112B23);
  static const Color cardBgElevated = Color(0xFF16382E);
  static const Color surface = Color(0xFF193F34);
  static const Color inputBg = Color(0xFF0D221C);

  // Tipografía y Textos
  static const Color textMain = Color(0xFFF8FAFC);
  static const Color textMuted = Color(0xFF9CBAB0);
  static const Color textSubtle = Color(0xFF658B7C);

  // Estados Semánticos
  static const Color success = Color(0xFF10B981);
  static const Color warning = Color(0xFFF59E0B);
  static const Color danger = Color(0xFFF43F5E);
  static const Color info = Color(0xFF38BDF8);

  // Bordes Cristalinos y Resplandores
  static const Color borderSubtle = Color(0x2E2EC486);
  static const Color borderFocus = Color(0x992EC486);
  static const Color glowMint = Color(0x402EC486);
  static const Color glowCold = Color(0x4038BDF8);

  // Curvas de Animación Motion.dev Spring
  static const Curve springCurve = Curves.easeOutBack;
  static const Curve smoothCurve = Curves.easeInOutCubic;

  // Gradientes Reutilizables (Aceternity & Aurora)
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF19734E), Color(0xFF2EC486)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient coldGradient = LinearGradient(
    colors: [Color(0xFF2EC486), Color(0xFF38BDF8)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient accentGradient = LinearGradient(
    colors: [Color(0xFF2EC486), Color(0xFF0EA5E9)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient heroGradient = LinearGradient(
    colors: [Color(0xFF0B1E19), Color(0xFF14382E), Color(0xFF0F2922)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient cardGradient = LinearGradient(
    colors: [Color(0xCC112B23), Color(0xCC0D221C)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // Helper de Decoración Glassmorphism (Efecto Cristal Esmerilado)
  static BoxDecoration glassDecoration({
    double radius = 18,
    Color? borderColor,
    Color? bgColor,
  }) {
    return BoxDecoration(
      color: bgColor ?? const Color(0xCC112B23),
      borderRadius: BorderRadius.circular(radius),
      border: Border.all(
        color: borderColor ?? const Color(0x332EC486),
        width: 1.2,
      ),
      boxShadow: [
        BoxShadow(
          color: Colors.black.withOpacity(0.35),
          blurRadius: 18,
          offset: const Offset(0, 8),
        ),
        BoxShadow(
          color: const Color(0xFF2EC486).withOpacity(0.12),
          blurRadius: 12,
          offset: const Offset(0, 0),
        ),
      ],
    );
  }

  static ThemeData get darkTheme {
    final baseTextTheme = ThemeData.dark().textTheme;
    final textTheme = GoogleFonts.plusJakartaSansTextTheme(baseTextTheme).apply(
      bodyColor: textMain,
      displayColor: textMain,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: background,
      primaryColor: primary,
      textTheme: textTheme,
      colorScheme: const ColorScheme.dark(
        primary: primary,
        secondary: secondary,
        surface: cardBg,
        error: danger,
        onPrimary: Colors.white,
        onSurface: textMain,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: background.withOpacity(0.85),
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: GoogleFonts.plusJakartaSans(
          fontSize: 18,
          fontWeight: FontWeight.w700,
          color: textMain,
        ),
        iconTheme: const IconThemeData(color: textMain),
      ),
      cardTheme: CardThemeData(
        color: cardBg,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: borderSubtle, width: 1),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: inputBg,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: borderSubtle, width: 1),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: borderSubtle, width: 1),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: primary, width: 1.8),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: danger, width: 1.2),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: danger, width: 1.8),
        ),
        labelStyle: GoogleFonts.plusJakartaSans(color: textMuted, fontSize: 13),
        hintStyle: GoogleFonts.plusJakartaSans(color: textSubtle, fontSize: 13),
        prefixIconColor: textMuted,
        suffixIconColor: textMuted,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          elevation: 2,
          shadowColor: primary.withOpacity(0.4),
          textStyle: GoogleFonts.plusJakartaSans(
            fontWeight: FontWeight.w700,
            fontSize: 14,
            letterSpacing: 0.3,
          ),
        ),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: cardBgElevated,
        selectedColor: primary.withOpacity(0.2),
        labelStyle: GoogleFonts.plusJakartaSans(fontSize: 12, color: textMain),
        side: const BorderSide(color: borderSubtle, width: 1),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: cardBg,
        elevation: 16,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: borderSubtle, width: 1),
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: borderSubtle,
        thickness: 1,
        space: 24,
      ),
    );
  }
}
