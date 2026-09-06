import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../widgets/auth_header.dart';
import '../widgets/auth_text_field.dart';
import '../widgets/gradient_button.dart';
import 'forgot_password_screen.dart';
import 'register_screen.dart';

/// CU02 — Gestionar inicio de sesión y autenticación (HU-02).
class LoginScreen extends StatefulWidget {
  static const routeName = '/login';

  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  String? _validateEmail(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Ingresa tu correo electrónico';
    }
    final emailRegex = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');
    if (!emailRegex.hasMatch(value.trim())) {
      return 'Ingresa un correo electrónico válido';
    }
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Ingresa tu contraseña';
    }
    return null;
  }

  Future<void> _submit(AuthProvider authProvider) async {
    if (!_formKey.currentState!.validate()) return;

    final success = await authProvider.login(
      email: _emailController.text.trim(),
      password: _passwordController.text,
    );

    if (success && mounted) {
      Navigator.of(context).pushReplacementNamed('/home');
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final isLoading = authProvider.status == AuthStatus.loading;

    return Scaffold(
      backgroundColor: const Color(0xFFF3F5F6),
      body: SingleChildScrollView(
        child: SafeArea(
          bottom: false,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const AuthHeader(
                title: 'SIGEPSI',
                subtitle:
                    'Gestión de citas, expedientes y seguimiento terapéutico',
                features: [
                  'Acceso seguro a tus citas y tratamiento',
                  'Privacidad y confidencialidad garantizada',
                  'Seguimiento de tu proceso terapéutico',
                ],
              ),
              Transform.translate(
                offset: const Offset(0, -24),
                child: Container(
                  padding: const EdgeInsets.fromLTRB(24, 32, 24, 24),
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(28),
                      topRight: Radius.circular(28),
                    ),
                  ),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const Text(
                          'Iniciar Sesión',
                          style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          'Inicia sesión para continuar',
                          style: TextStyle(
                            color: Colors.grey.shade600,
                            fontSize: 14,
                          ),
                        ),
                        const SizedBox(height: 24),
                        AuthTextField(
                          controller: _emailController,
                          label: 'Correo electrónico',
                          icon: Icons.mail_outline,
                          keyboardType: TextInputType.emailAddress,
                          validator: _validateEmail,
                        ),
                        const SizedBox(height: 16),
                        AuthTextField(
                          controller: _passwordController,
                          label: 'Contraseña',
                          icon: Icons.lock_outline,
                          obscureText: true,
                          validator: _validatePassword,
                        ),
                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            onPressed: isLoading
                                ? null
                                : () => Navigator.of(
                                    context,
                                  ).pushNamed(ForgotPasswordScreen.routeName),
                            child: const Text('¿Olvidaste tu contraseña?'),
                          ),
                        ),
                        if (authProvider.status == AuthStatus.error &&
                            authProvider.errorMessage != null) ...[
                          const SizedBox(height: 12),
                          Text(
                            authProvider.errorMessage!,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                        ],
                        const SizedBox(height: 24),
                        GradientButton(
                          label: 'Ingresar',
                          isLoading: isLoading,
                          onPressed: () => _submit(authProvider),
                        ),
                        // El botón de registro se ocultó para el Sprint 0 (corresponde a sprints posteriores)
                        // const SizedBox(height: 16),
                        // Center(
                        //   child: TextButton(
                        //     onPressed: isLoading
                        //         ? null
                        //         : () => Navigator.of(
                        //             context,
                        //           ).pushNamed(RegisterScreen.routeName),
                        //     child: const Text('¿No tienes cuenta? Regístrate'),
                        //   ),
                        // ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
