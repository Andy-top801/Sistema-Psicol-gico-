import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'paquetes/paquete1_admin_seguridad/providers/auth_provider.dart';
import 'paquetes/paquete1_admin_seguridad/screens/forgot_password_screen.dart';
import 'paquetes/paquete1_admin_seguridad/screens/login_screen.dart';
import 'paquetes/paquete1_admin_seguridad/screens/register_screen.dart';
import 'shell/home/screens/home_screen.dart';
import 'shell/splash/screens/splash_screen.dart';

void main() {
  runApp(const SigepsiApp());
}

class SigepsiApp extends StatelessWidget {
  const SigepsiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AuthProvider(),
      child: MaterialApp(
        title: 'SIGEPSI',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: Colors.teal, useMaterial3: true),
        initialRoute: SplashScreen.routeName,
        routes: {
          SplashScreen.routeName: (_) => const SplashScreen(),
          LoginScreen.routeName: (_) => const LoginScreen(),
          RegisterScreen.routeName: (_) => const RegisterScreen(),
          ForgotPasswordScreen.routeName: (_) => const ForgotPasswordScreen(),
          HomeScreen.routeName: (_) => const HomeScreen(),
        },
      ),
    );
  }
}
