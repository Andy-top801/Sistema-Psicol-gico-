import 'package:flutter/material.dart';

import '../../../core/network/api_exception.dart';
import '../services/password_reset_service.dart';
import '../widgets/auth_header.dart';
import '../widgets/auth_text_field.dart';
import '../widgets/gradient_button.dart';
import 'reset_password_screen.dart';

/// CU27 — Recuperar contraseña o credenciales de acceso (HU-10b / RF-31):
/// paso intermedio, la persona ingresa el código que recibió por correo.
/// Al validarse, avanza automáticamente a [ResetPasswordScreen] — esa
/// pantalla es donde la persona escribe su propia contraseña nueva, este
/// paso solo confirma el código.
///
/// No tiene ruta con nombre registrada en `main.dart`: solo se llega aquí
/// empujada directamente desde [ForgotPasswordScreen] tras enviar el
/// código.
class VerifyResetCodeScreen extends StatefulWidget {
  const VerifyResetCodeScreen({
    super.key,
    required this.email,
    PasswordResetService? service,
  }) : _service = service;

  final String email;
  final PasswordResetService? _service;

  @override
  State<VerifyResetCodeScreen> createState() => _VerifyResetCodeScreenState();
}

class _VerifyResetCodeScreenState extends State<VerifyResetCodeScreen> {
  final _formKey = GlobalKey<FormState>();
  final _codeController = TextEditingController();
  late final PasswordResetService _service =
      widget._service ?? PasswordResetService();

  bool _isLoading = false;
  String? _errorMessage;

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  String? _validateCode(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Ingresa el código que recibiste por correo';
    }
    return null;
  }

  Future<void> _resend() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _service.requestPasswordReset(email: widget.email);
      if (!mounted) return;
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Código reenviado con éxito.')),
      );
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

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final code = _codeController.text.trim();
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _service.verifyResetCode(code: code);
      if (!mounted) return;
      setState(() => _isLoading = false);
      // Código válido: avanza automáticamente a la pantalla de nueva
      // contraseña — la persona sigue siendo quien la escribe, este paso
      // solo confirmó el código.
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => ResetPasswordScreen(code: code, service: _service),
        ),
      );
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
                    title: 'Ingresa el código',
                    subtitle:
                        'Te lo enviamos por correo. Es válido por 5 minutos.',
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
                          controller: _codeController,
                          label: 'Código de recuperación',
                          icon: Icons.vpn_key_outlined,
                          validator: _validateCode,
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
                          label: 'Verificar código',
                          isLoading: _isLoading,
                          onPressed: _submit,
                        ),
                        const SizedBox(height: 12),
                        TextButton(
                          onPressed: _isLoading ? null : _resend,
                          child: _isLoading
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF1E8A7E)),
                                  ),
                                )
                              : const Text(
                                  'Volver a enviar código',
                                  style: TextStyle(
                                    color: Color(0xFF1E8A7E),
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
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
