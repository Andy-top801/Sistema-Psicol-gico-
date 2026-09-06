import 'package:flutter/material.dart';

import '../../../core/network/api_exception.dart';
import '../services/password_reset_service.dart';
import '../widgets/auth_header.dart';
import '../widgets/auth_text_field.dart';
import '../widgets/gradient_button.dart';
import 'login_screen.dart';

/// CU27 — Recuperar contraseña o credenciales de acceso (HU-10c / RF-31):
/// paso final, la persona escribe su propia contraseña nueva. El código
/// ya se validó en [VerifyResetCodeScreen] (paso anterior); esta pantalla
/// no vuelve a pedirlo, solo lo reenvía junto con la contraseña.
///
/// No tiene ruta con nombre registrada en `main.dart`: solo se llega aquí
/// empujada directamente desde el paso de verificación, que es quien
/// tiene el [code] ya comprobado.
class ResetPasswordScreen extends StatefulWidget {
  const ResetPasswordScreen({
    super.key,
    required this.code,
    PasswordResetService? service,
    // ignore: prefer_initializing_formals
  }) : _service = service;

  final String code;
  final PasswordResetService? _service;

  @override
  State<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends State<ResetPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  late final PasswordResetService _service =
      widget._service ?? PasswordResetService();

  bool _isLoading = false;
  String? _errorMessage;

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
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
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

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _service.confirmPasswordReset(
        code: widget.code,
        newPassword: _passwordController.text,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Contraseña actualizada. Ya puedes iniciar sesión.'),
        ),
      );
      Navigator.of(
        context,
      ).pushNamedAndRemoveUntil(LoginScreen.routeName, (_) => false);
    } on ApiException catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.message;
      });
    } catch (_) {
      setState(() {
        _isLoading = false;
        _errorMessage =
            'No se pudo conectar con el servidor. Verifica tu conexión.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
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
              const AuthHeader(
                compact: true,
                title: 'Nueva contraseña',
                subtitle:
                    'Elige la contraseña que vas a usar de ahora en adelante',
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
                          controller: _passwordController,
                          label: 'Nueva contraseña',
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
                        if (_errorMessage != null) ...[
                          const SizedBox(height: 12),
                          Text(
                            _errorMessage!,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                        ],
                        const SizedBox(height: 24),
                        GradientButton(
                          label: 'Guardar nueva contraseña',
                          isLoading: _isLoading,
                          onPressed: _submit,
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
