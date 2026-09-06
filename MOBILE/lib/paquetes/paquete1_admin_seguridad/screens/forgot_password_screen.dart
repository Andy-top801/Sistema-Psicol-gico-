import 'package:flutter/material.dart';

import '../../../core/network/api_exception.dart';
import '../services/password_reset_service.dart';
import '../widgets/auth_header.dart';
import '../widgets/auth_text_field.dart';
import '../widgets/gradient_button.dart';
import 'verify_reset_code_screen.dart';

/// CU27 — Recuperar contraseña o credenciales de acceso (HU-10a / RF-31):
/// solicitud del código por correo.
class ForgotPasswordScreen extends StatefulWidget {
  static const routeName = '/forgot-password';

  const ForgotPasswordScreen({super.key, PasswordResetService? service})
    // ignore: prefer_initializing_formals
    : _service = service;

  final PasswordResetService? _service;

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  late final PasswordResetService _service =
      widget._service ?? PasswordResetService();

  bool _isLoading = false;
  String? _errorMessage;
  bool _sent = false;

  @override
  void dispose() {
    _emailController.dispose();
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

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _service.requestPasswordReset(email: _emailController.text.trim());
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _sent = true;
      });
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

  Future<void> _resend() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _service.requestPasswordReset(email: _emailController.text.trim());
      if (!mounted) return;
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Enlace reenviado con éxito.')),
      );
    } on ApiException catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.message;
        _sent = false;
      });
    } catch (_) {
      setState(() {
        _isLoading = false;
        _errorMessage =
            'No se pudo conectar con el servidor. Verifica tu conexión.';
        _sent = false;
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
                    title: 'Recuperar contraseña',
                    subtitle:
                        'Te enviaremos un enlace a tu correo para restablecerla',
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
                  child: _sent ? _buildSentState(context) : _buildForm(),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildForm() {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AuthTextField(
            controller: _emailController,
            label: 'Correo electrónico',
            icon: Icons.mail_outline,
            keyboardType: TextInputType.emailAddress,
            validator: _validateEmail,
          ),
          if (_errorMessage != null) ...[
            const SizedBox(height: 12),
            Text(
              _errorMessage!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ],
          const SizedBox(height: 24),
          GradientButton(
            label: 'Enviar enlace',
            isLoading: _isLoading,
            onPressed: _submit,
          ),
        ],
      ),
    );
  }

  Widget _buildSentState(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Icon(
          Icons.mark_email_read_outlined,
          size: 48,
          color: Color(0xFF1E8A7E),
        ),
        const SizedBox(height: 16),
        const Text(
          'Revisa tu correo',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Text(
          'Si el correo está registrado, recibirás un enlace de recuperación válido por 5 minutos.',
          textAlign: TextAlign.center,
          style: TextStyle(color: Colors.grey.shade600),
        ),
        const SizedBox(height: 24),
        GradientButton(
          label: 'Volver al inicio de sesión',
          onPressed: () {
            Navigator.of(context).pop();
          },
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
                  'Volver a enviar enlace',
                  style: TextStyle(
                    color: Color(0xFF1E8A7E),
                    fontWeight: FontWeight.bold,
                  ),
                ),
        ),
      ],
    );
  }
}
