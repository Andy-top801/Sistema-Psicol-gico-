import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../core/theme/app_theme.dart';

class PasswordResetScreen extends StatefulWidget {
  final AuthService authService;

  const PasswordResetScreen({super.key, required this.authService});

  @override
  State<PasswordResetScreen> createState() => _PasswordResetScreenState();
}

class _PasswordResetScreenState extends State<PasswordResetScreen> {
  final _emailController = TextEditingController();
  final _tokenController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  int _step = 1;
  bool _isLoading = false;
  bool _obscurePwd = true;
  bool _obscureConfirm = true;
  String? _message;
  String? _errorMessage;
  String? _generatedToken;

  /// ═════════════════════════════════════════════════════════════════════════
  /// CU27: Recuperar Contraseña y Credenciales (HU-10)
  /// Diagrama de Comunicación – Solicitud de Token (Móvil Flutter)
  /// Participantes:
  ///   Actor  → Usuario (Todos los roles)
  ///   IU     → IU_RecuperarPassword (Móvil)  ← ESTE ARCHIVO
  ///   CTR    → CTR_PasswordReset (Django REST)
  ///   CE     → CE_Usuario_y_Token (PostgreSQL)
  ///   SRV    → SRV_ServicioCorreo (SMTP / SendGrid)
  /// ═════════════════════════════════════════════════════════════════════════
  Future<void> _requestToken() async {
    final email = _emailController.text.trim();
    if (email.isEmpty) {
      setState(() => _errorMessage = 'Ingresa tu correo electrónico registrado.');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _message = null;
    });

    final res = await widget.authService.requestPasswordReset(email);

    setState(() {
      _isLoading = false;
      if (res['success'] == true) {
        final data = res['data'];
        _message = data['mensaje'] ?? 'Solicitud procesada.';
        _generatedToken = data['token_debug'];
      } else {
        _errorMessage = res['error'] ?? 'Error al solicitar recuperación.';
      }
    });
  }

  Future<void> _confirmReset() async {
    final token = _tokenController.text.trim();
    final pwd = _newPasswordController.text.trim();
    final confirm = _confirmPasswordController.text.trim();

    if (token.isEmpty) {
      setState(() => _errorMessage = 'El token de recuperación es obligatorio.');
      return;
    }
    if (pwd.length < 8) {
      setState(() => _errorMessage = 'La nueva contraseña debe tener al menos 8 caracteres.');
      return;
    }
    if (pwd != confirm) {
      setState(() => _errorMessage = 'Las contraseñas no coinciden.');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _message = null;
    });

    final res = await widget.authService.confirmPasswordReset(
      token: token,
      password: pwd,
      passwordConfirm: confirm,
    );

    setState(() {
      _isLoading = false;
      if (res['success'] == true) {
        _message = res['message'] ?? '¡Contraseña restablecida exitosamente!';
      } else {
        _errorMessage = res['error'] ?? 'Error al restablecer contraseña.';
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Recuperar Acceso'),
        elevation: 0,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Stepper Visual Superior
              Row(
                children: [
                  _buildStepIndicator(step: 1, label: 'Solicitud', isActive: _step == 1, isCompleted: _step > 1),
                  Expanded(
                    child: Container(
                      height: 2,
                      color: _step > 1 ? AppTheme.primary : AppTheme.borderSubtle,
                    ),
                  ),
                  _buildStepIndicator(step: 2, label: 'Nueva Clave', isActive: _step == 2, isCompleted: false),
                ],
              ),
              const SizedBox(height: 28),

              // Mensajes de Alerta
              if (_message != null)
                Container(
                  margin: const EdgeInsets.only(bottom: 18),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: AppTheme.success.withOpacity(0.15),
                    border: Border.all(color: AppTheme.success.withOpacity(0.35)),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.check_circle_rounded, color: AppTheme.success, size: 20),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(_message!, style: const TextStyle(color: Color(0xFFA7F3D0), fontSize: 12, fontWeight: FontWeight.w600)),
                      ),
                    ],
                  ),
                ),

              if (_errorMessage != null)
                Container(
                  margin: const EdgeInsets.only(bottom: 18),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: AppTheme.danger.withOpacity(0.12),
                    border: Border.all(color: AppTheme.danger.withOpacity(0.35)),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline_rounded, color: AppTheme.danger, size: 20),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(_errorMessage!, style: const TextStyle(color: Color(0xFFFECDD3), fontSize: 12)),
                      ),
                    ],
                  ),
                ),

              // PASO 1: Solicitar Token
              if (_step == 1) ...[
                Container(
                  padding: const EdgeInsets.all(22),
                  decoration: BoxDecoration(
                    color: AppTheme.cardBg,
                    borderRadius: BorderRadius.circular(22),
                    border: Border.all(color: AppTheme.borderSubtle),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Center(
                        child: Container(
                          width: 60,
                          height: 60,
                          decoration: BoxDecoration(
                            color: AppTheme.primary.withOpacity(0.15),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.mark_email_read_rounded, size: 30, color: AppTheme.primaryLight),
                        ),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'Restablecimiento de Credenciales',
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        'Ingresa tu correo institucional registrado para recibir el token seguro de recuperación:',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: AppTheme.textMuted, fontSize: 12),
                      ),
                      const SizedBox(height: 20),
                      TextField(
                        controller: _emailController,
                        keyboardType: TextInputType.emailAddress,
                        decoration: const InputDecoration(
                          labelText: 'Correo Electrónico',
                          hintText: 'tu-correo@centro.com',
                          prefixIcon: Icon(Icons.alternate_email_rounded),
                        ),
                      ),
                      const SizedBox(height: 12),
                      const Text(
                        'Cuentas para demostración rápida:',
                        style: TextStyle(fontSize: 11, color: AppTheme.textMuted, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 6),
                      Wrap(
                        spacing: 8,
                        runSpacing: 6,
                        children: [
                          _buildDemoChip('admin@sigepsi.com', 'SuperAdmin'),
                          _buildDemoChip('admin@centroesperanza.com', 'Admin Centro'),
                          _buildDemoChip('psicologo@centroesperanza.com', 'Psicólogo'),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Container(
                        height: 50,
                        decoration: BoxDecoration(
                          gradient: AppTheme.primaryGradient,
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Material(
                          color: Colors.transparent,
                          child: InkWell(
                            borderRadius: BorderRadius.circular(14),
                            onTap: _isLoading ? null : _requestToken,
                            child: Center(
                              child: _isLoading
                                  ? const SizedBox(
                                      height: 20,
                                      width: 20,
                                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                    )
                                  : const Text(
                                      'ENVIAR TOKEN DE RECUPERACIÓN',
                                      style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 13, letterSpacing: 0.5),
                                    ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                if (_generatedToken != null) ...[
                  const SizedBox(height: 20),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppTheme.cardBgElevated,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppTheme.primary.withOpacity(0.4)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.vpn_key_rounded, size: 16, color: AppTheme.primaryLight),
                            SizedBox(width: 8),
                            Text(
                              'Token generado (Modo Demostración):',
                              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.primaryLight),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: AppTheme.inputBg,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: AppTheme.borderSubtle),
                          ),
                          child: SelectableText(
                            _generatedToken!,
                            style: const TextStyle(color: AppTheme.primaryLight, fontFamily: 'monospace', fontSize: 13, fontWeight: FontWeight.bold),
                          ),
                        ),
                        const SizedBox(height: 12),
                        ElevatedButton.icon(
                          onPressed: () {
                            setState(() {
                              _tokenController.text = _generatedToken!;
                              _step = 2;
                            });
                          },
                          icon: const Icon(Icons.arrow_forward_rounded, size: 18),
                          label: const Text('Continuar a Paso 2 (Restablecer)'),
                        ),
                      ],
                    ),
                  ),
                ],
              ] else ...[
                // PASO 2: Restablecer Contraseña
                Container(
                  padding: const EdgeInsets.all(22),
                  decoration: BoxDecoration(
                    color: AppTheme.cardBg,
                    borderRadius: BorderRadius.circular(22),
                    border: Border.all(color: AppTheme.borderSubtle),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text(
                        'Ingresa tu Nueva Contraseña',
                        style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 4),
                      const Text(
                        'Verifica el token de autorización y define una clave segura.',
                        style: TextStyle(color: AppTheme.textMuted, fontSize: 12),
                      ),
                      const SizedBox(height: 20),
                      TextField(
                        controller: _tokenController,
                        decoration: const InputDecoration(
                          labelText: 'Token de Recuperación',
                          prefixIcon: Icon(Icons.vpn_key_rounded),
                        ),
                      ),
                      const SizedBox(height: 14),
                      TextField(
                        controller: _newPasswordController,
                        obscureText: _obscurePwd,
                        decoration: InputDecoration(
                          labelText: 'Nueva Contraseña',
                          prefixIcon: const Icon(Icons.lock_rounded),
                          suffixIcon: IconButton(
                            icon: Icon(_obscurePwd ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                            onPressed: () => setState(() => _obscurePwd = !_obscurePwd),
                          ),
                        ),
                      ),
                      const SizedBox(height: 14),
                      TextField(
                        controller: _confirmPasswordController,
                        obscureText: _obscureConfirm,
                        decoration: InputDecoration(
                          labelText: 'Confirmar Contraseña',
                          prefixIcon: const Icon(Icons.lock_reset_rounded),
                          suffixIcon: IconButton(
                            icon: Icon(_obscureConfirm ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                            onPressed: () => setState(() => _obscureConfirm = !_obscureConfirm),
                          ),
                        ),
                      ),
                      const SizedBox(height: 22),
                      Container(
                        height: 50,
                        decoration: BoxDecoration(
                          gradient: AppTheme.primaryGradient,
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Material(
                          color: Colors.transparent,
                          child: InkWell(
                            borderRadius: BorderRadius.circular(14),
                            onTap: _isLoading ? null : _confirmReset,
                            child: Center(
                              child: _isLoading
                                  ? const SizedBox(
                                      height: 20,
                                      width: 20,
                                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                    )
                                  : const Text(
                                      'ACTUALIZAR CONTRASEÑA',
                                      style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 13, letterSpacing: 0.5),
                                    ),
                            ),
                          ),
                        ),
                      ),
                      if (_message != null && _message!.contains('exitosa')) ...[
                        const SizedBox(height: 14),
                        Container(
                          height: 46,
                          decoration: BoxDecoration(
                            color: AppTheme.success.withOpacity(0.18),
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: AppTheme.success),
                          ),
                          child: TextButton.icon(
                            onPressed: () => Navigator.pop(context),
                            icon: const Icon(Icons.login_rounded, color: AppTheme.success),
                            label: const Text(
                              'VOLVER AL INICIO DE SESIÓN',
                              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                            ),
                          ),
                        ),
                      ],
                      const SizedBox(height: 12),
                      TextButton(
                        onPressed: () => setState(() => _step = 1),
                        child: const Text('← Volver al Paso 1', style: TextStyle(color: AppTheme.textMuted)),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDemoChip(String email, String role) {
    return InkWell(
      onTap: () {
        setState(() {
          _emailController.text = email;
          _errorMessage = null;
        });
      },
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: AppTheme.primary.withOpacity(0.12),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: AppTheme.primary.withOpacity(0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.touch_app_outlined, size: 13, color: AppTheme.primaryLight),
            const SizedBox(width: 4),
            Text(
              role,
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.primaryLight),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStepIndicator({
    required int step,
    required String label,
    required bool isActive,
    required bool isCompleted,
  }) {
    final color = isCompleted
        ? AppTheme.success
        : isActive
            ? AppTheme.primary
            : AppTheme.textSubtle;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: isCompleted ? AppTheme.success : (isActive ? AppTheme.primary : AppTheme.inputBg),
            shape: BoxShape.circle,
            border: Border.all(color: color, width: 2),
          ),
          child: Center(
            child: isCompleted
                ? const Icon(Icons.check_rounded, color: Colors.white, size: 16)
                : Text(
                    step.toString(),
                    style: TextStyle(
                      color: isActive ? Colors.white : AppTheme.textMuted,
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                    ),
                  ),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: isActive || isCompleted ? FontWeight.bold : FontWeight.normal,
            color: isActive || isCompleted ? AppTheme.textMain : AppTheme.textMuted,
          ),
        ),
      ],
    );
  }
}
