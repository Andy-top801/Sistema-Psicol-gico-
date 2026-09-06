import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../widgets/auth_header.dart';
import '../widgets/auth_text_field.dart';
import '../widgets/gradient_button.dart';

/// CU02 — Gestionar inicio de sesión y autenticación (HU-02, registro de
/// pacientes).
class RegisterScreen extends StatefulWidget {
  static const routeName = '/register';

  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _passwordController.addListener(_onPasswordChanged);
  }

  void _onPasswordChanged() {
    if (mounted) {
      setState(() {});
    }
  }

  @override
  void dispose() {
    _passwordController.removeListener(_onPasswordChanged);
    _firstNameController.dispose();
    _lastNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  String? _required(String? value, String label) {
    if (value == null || value.trim().isEmpty) {
      return 'Ingresa $label';
    }
    return null;
  }

  String? _validateEmail(String? value) {
    final requiredError = _required(value, 'tu correo electrónico');
    if (requiredError != null) return requiredError;
    final emailRegex = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');
    if (!emailRegex.hasMatch(value!.trim())) {
      return 'Ingresa un correo electrónico válido';
    }
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Ingresa una contraseña';
    }
    if (value.length < 8) {
      return 'La contraseña debe tener al menos 8 caracteres';
    }
    if (!RegExp(r'[A-Z]').hasMatch(value)) {
      return 'La contraseña debe contener al menos una letra mayúscula';
    }
    if (!RegExp(r'[a-z]').hasMatch(value)) {
      return 'La contraseña debe contener al menos una letra minúscula';
    }
    if (!RegExp(r'\d').hasMatch(value)) {
      return 'La contraseña debe contener al menos un número';
    }
    if (!RegExp(r'[^a-zA-Z0-9]').hasMatch(value)) {
      return 'La contraseña debe contener al menos un carácter especial (ej. !, @, #, etc.)';
    }
    return null;
  }

  String? _validateConfirmPassword(String? value) {
    if (value != _passwordController.text) {
      return 'Las contraseñas no coinciden';
    }
    return null;
  }

  Widget _buildRequirementItem(String text, bool isMet) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3.0),
      child: Row(
        children: [
          Icon(
            isMet ? Icons.check_circle : Icons.radio_button_unchecked,
            color: isMet ? const Color(0xFF1E8A7E) : Colors.grey.shade400,
            size: 18,
          ),
          const SizedBox(width: 8),
          Text(
            text,
            style: TextStyle(
              color: isMet ? const Color(0xFF1E8A7E) : Colors.grey.shade600,
              fontSize: 13,
              fontWeight: isMet ? FontWeight.w500 : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _submit(AuthProvider authProvider) async {
    if (!_formKey.currentState!.validate()) return;

    final success = await authProvider.register(
      email: _emailController.text.trim(),
      password: _passwordController.text,
      firstName: _firstNameController.text.trim(),
      lastName: _lastNameController.text.trim(),
      phone: _phoneController.text.trim(),
    );

    if (success && mounted) {
      Navigator.of(context).pushReplacementNamed('/home');
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final isLoading = authProvider.status == AuthStatus.loading;
    final password = _passwordController.text;
    final hasMinLength = password.length >= 8;
    final hasUppercase = RegExp(r'[A-Z]').hasMatch(password);
    final hasLowercase = RegExp(r'[a-z]').hasMatch(password);
    final hasNumber = RegExp(r'\d').hasMatch(password);
    final hasSpecialChar = RegExp(r'[^a-zA-Z0-9]').hasMatch(password);

    return Scaffold(
      backgroundColor: const Color(0xFFF3F5F6),
      body: SingleChildScrollView(
        child: SafeArea(
          bottom: false,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Stack(
                children: [
                  const AuthHeader(
                    compact: true,
                    title: 'Crear cuenta',
                    subtitle:
                        'Regístrate para gestionar tus citas y tu tratamiento',
                  ),
                  Positioned(
                    top: 8,
                    left: 4,
                    child: IconButton(
                      icon: const Icon(Icons.arrow_back, color: Colors.white),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                  ),
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
                        AuthTextField(
                          controller: _firstNameController,
                          label: 'Nombres',
                          icon: Icons.person_outline,
                          validator: (v) => _required(v, 'tus nombres'),
                        ),
                        const SizedBox(height: 16),
                        AuthTextField(
                          controller: _lastNameController,
                          label: 'Apellidos',
                          icon: Icons.person_outline,
                          validator: (v) => _required(v, 'tus apellidos'),
                        ),
                        const SizedBox(height: 16),
                        AuthTextField(
                          controller: _emailController,
                          label: 'Correo electrónico',
                          icon: Icons.mail_outline,
                          keyboardType: TextInputType.emailAddress,
                          validator: _validateEmail,
                        ),
                        const SizedBox(height: 16),
                        AuthTextField(
                          controller: _phoneController,
                          label: 'Teléfono (opcional)',
                          icon: Icons.phone_outlined,
                          keyboardType: TextInputType.phone,
                        ),
                        const SizedBox(height: 16),
                        AuthTextField(
                          controller: _passwordController,
                          label: 'Contraseña',
                          icon: Icons.lock_outline,
                          obscureText: true,
                          validator: _validatePassword,
                        ),
                        const SizedBox(height: 12),
                        Padding(
                          padding: const EdgeInsets.only(left: 4.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Requisitos de seguridad:',
                                style: TextStyle(
                                  color: Colors.grey.shade700,
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 6),
                              _buildRequirementItem('Mínimo 8 caracteres', hasMinLength),
                              _buildRequirementItem('Letra mayúscula (A-Z)', hasUppercase),
                              _buildRequirementItem('Letra minúscula (a-z)', hasLowercase),
                              _buildRequirementItem('Al menos un número (0-9)', hasNumber),
                              _buildRequirementItem('Un carácter especial (ej. !, @, #, \$, etc.)', hasSpecialChar),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),
                        AuthTextField(
                          controller: _confirmPasswordController,
                          label: 'Confirmar contraseña',
                          icon: Icons.lock_outline,
                          obscureText: true,
                          validator: _validateConfirmPassword,
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
                          label: 'Registrarme',
                          isLoading: isLoading,
                          onPressed: () => _submit(authProvider),
                        ),
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
