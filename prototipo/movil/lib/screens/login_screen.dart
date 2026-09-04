import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../models/tenant_model.dart';
import '../core/theme/app_theme.dart';
import 'dashboard_screen.dart';
import 'password_reset_screen.dart';

class LoginScreen extends StatefulWidget {
  final AuthService authService;

  const LoginScreen({super.key, required this.authService});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isSuperAdminMode = false;
  bool _obscurePassword = true;
  bool _isLoading = false;
  String? _errorMessage;

  List<TenantModel> _tenants = [];
  TenantModel? _selectedTenant;

  @override
  void initState() {
    super.initState();
    _loadTenants();
  }

  Future<void> _loadTenants() async {
    final list = await widget.authService.getPublicTenants();
    if (mounted) {
      setState(() {
        _tenants = list;
        if (list.isNotEmpty) {
          if (_selectedTenant == null || !_tenants.any((t) => t.slug == _selectedTenant!.slug)) {
            _selectedTenant = list.first;
          }
        }
      });
    }
  }

  void _fillDemo(String email, String password, bool isSuperAdmin, String tenantSlug) {
    setState(() {
      _emailController.text = email;
      _passwordController.text = password;
      _isSuperAdminMode = isSuperAdmin;
      if (!isSuperAdmin && _tenants.isNotEmpty) {
        _selectedTenant = _tenants.firstWhere(
          (t) => t.slug == tenantSlug,
          orElse: () => _tenants.first,
        );
      }
    });
  }

  void _showServerConfigDialog() {
    final urlController = TextEditingController(text: widget.authService.baseUrl);
    bool testing = false;
    bool? testResult;

    showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return AlertDialog(
              backgroundColor: AppTheme.cardBg,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              title: const Row(
                children: [
                  Icon(Icons.settings_ethernet_rounded, color: AppTheme.primaryLight),
                  SizedBox(width: 8),
                  Text('Configuración del Servidor', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                ],
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Dirección Base del API Backend:',
                    style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: urlController,
                    decoration: InputDecoration(
                      hintText: 'http://localhost:8000/api',
                      prefixIcon: const Icon(Icons.link_rounded),
                      suffixIcon: IconButton(
                        icon: const Icon(Icons.clear_rounded, size: 18),
                        onPressed: () => urlController.clear(),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Preajustes rápidos:',
                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
                  ),
                  const SizedBox(height: 6),
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: [
                      ActionChip(
                        label: const Text('USB (adb reverse)', style: TextStyle(fontSize: 11)),
                        onPressed: () => urlController.text = 'http://localhost:8000/api',
                      ),
                      ActionChip(
                        label: const Text('Emulador (10.0.2.2)', style: TextStyle(fontSize: 11)),
                        onPressed: () => urlController.text = 'http://10.0.2.2:8000/api',
                      ),
                      ActionChip(
                        label: const Text('Wi-Fi PC (10.134.123.170)', style: TextStyle(fontSize: 11)),
                        onPressed: () => urlController.text = 'http://10.134.123.170:8000/api',
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  if (testResult != null)
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: testResult! ? AppTheme.success.withOpacity(0.15) : AppTheme.danger.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: testResult! ? AppTheme.success : AppTheme.danger),
                      ),
                      child: Row(
                        children: [
                          Icon(testResult! ? Icons.check_circle_rounded : Icons.error_rounded,
                              size: 16, color: testResult! ? AppTheme.success : AppTheme.danger),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              testResult! ? '¡Conexión exitosa con el backend!' : 'No se pudo conectar al servidor.',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: testResult! ? const Color(0xFFA7F3D0) : const Color(0xFFFECDD3),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: testing
                      ? null
                      : () async {
                          setModalState(() {
                            testing = true;
                            testResult = null;
                          });
                          final ok = await widget.authService.testConnection(testUrl: urlController.text.trim());
                          setModalState(() {
                            testing = false;
                            testResult = ok;
                          });
                        },
                  child: testing
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('Probar Conexión'),
                ),
                ElevatedButton(
                  onPressed: () async {
                    await widget.authService.setCustomBaseUrl(urlController.text.trim());
                    if (ctx.mounted) Navigator.pop(ctx);
                    _loadTenants();
                  },
                  child: const Text('Guardar'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _submitLogin() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final tenantSlug = _isSuperAdminMode ? 'public' : _selectedTenant?.slug;
    if (!_isSuperAdminMode) {
      widget.authService.setTenant(_selectedTenant);
    } else {
      widget.authService.setTenant(null);
    }

    final success = await widget.authService.login(
      _emailController.text.trim(),
      _passwordController.text.trim(),
      tenantSlug: tenantSlug,
    );

    setState(() {
      _isLoading = false;
    });

    if (success && mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => DashboardScreen(authService: widget.authService),
        ),
      );
    } else {
      setState(() {
        _errorMessage = widget.authService.lastErrorMessage ?? 'Credenciales inválidas o centro suspendido.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: Stack(
        children: [
          // Luces ambientales decorativas de fondo
          Positioned(
            top: -60,
            right: -60,
            child: Container(
              width: 240,
              height: 240,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    AppTheme.primary.withOpacity(0.18),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            bottom: -80,
            left: -80,
            child: Container(
              width: 260,
              height: 260,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    AppTheme.secondary.withOpacity(0.15),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),

          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Brand Header
                    Center(
                      child: Container(
                        width: 80,
                        height: 80,
                        padding: const EdgeInsets.all(3),
                        decoration: BoxDecoration(
                          gradient: AppTheme.primaryGradient,
                          borderRadius: BorderRadius.circular(24),
                          boxShadow: [
                            BoxShadow(
                              color: AppTheme.primary.withOpacity(0.35),
                              blurRadius: 24,
                              offset: const Offset(0, 8),
                            ),
                          ],
                        ),
                        child: Container(
                          decoration: BoxDecoration(
                            color: AppTheme.background,
                            borderRadius: BorderRadius.circular(21),
                          ),
                          child: const Icon(
                            Icons.psychology_outlined,
                            size: 46,
                            color: AppTheme.primaryLight,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'SIGEPSI',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 30,
                        fontWeight: FontWeight.w900,
                        letterSpacing: -0.5,
                        color: AppTheme.textMain,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Center(
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppTheme.primary.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: AppTheme.primary.withOpacity(0.25)),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Container(
                              width: 6,
                              height: 6,
                              decoration: const BoxDecoration(
                                color: AppTheme.success,
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 6),
                            const Text(
                              'SALUD MENTAL DIGITAL • MULTI-TENANT',
                              style: TextStyle(
                                color: AppTheme.primaryLight,
                                fontSize: 10,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.5,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Center(
                      child: InkWell(
                        onTap: _showServerConfigDialog,
                        borderRadius: BorderRadius.circular(16),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                          decoration: BoxDecoration(
                            color: AppTheme.surface,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: AppTheme.borderSubtle),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.dns_rounded, size: 12, color: AppTheme.primaryLight),
                              const SizedBox(width: 6),
                              Text(
                                'Servidor: ${widget.authService.baseUrl}',
                                style: const TextStyle(fontSize: 10, color: AppTheme.textMuted, fontWeight: FontWeight.w500),
                              ),
                              const SizedBox(width: 4),
                              const Icon(Icons.tune_rounded, size: 12, color: AppTheme.textMuted),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Tarjeta Principal del Formulario
                    Container(
                      padding: const EdgeInsets.all(22),
                      decoration: BoxDecoration(
                        color: AppTheme.cardBg,
                        borderRadius: BorderRadius.circular(22),
                        border: Border.all(color: AppTheme.borderSubtle),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.4),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // Selector Segmentado de Modo
                          Container(
                            padding: const EdgeInsets.all(4),
                            decoration: BoxDecoration(
                              color: AppTheme.inputBg,
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(color: AppTheme.borderSubtle),
                            ),
                            child: Row(
                              children: [
                                Expanded(
                                  child: GestureDetector(
                                    onTap: () => setState(() => _isSuperAdminMode = false),
                                    child: AnimatedContainer(
                                      duration: const Duration(milliseconds: 200),
                                      padding: const EdgeInsets.symmetric(vertical: 10),
                                      decoration: BoxDecoration(
                                        gradient: !_isSuperAdminMode ? AppTheme.primaryGradient : null,
                                        color: !_isSuperAdminMode ? null : Colors.transparent,
                                        borderRadius: BorderRadius.circular(10),
                                        boxShadow: !_isSuperAdminMode
                                            ? [
                                                BoxShadow(
                                                  color: AppTheme.primary.withOpacity(0.3),
                                                  blurRadius: 8,
                                                  offset: const Offset(0, 2),
                                                ),
                                              ]
                                            : null,
                                      ),
                                      child: Row(
                                        mainAxisAlignment: MainAxisAlignment.center,
                                        children: [
                                          Icon(
                                            Icons.local_hospital_rounded,
                                            size: 16,
                                            color: !_isSuperAdminMode ? Colors.white : AppTheme.textMuted,
                                          ),
                                          const SizedBox(width: 6),
                                          Text(
                                            'Centro Clínico',
                                            style: TextStyle(
                                              fontWeight: FontWeight.w700,
                                              fontSize: 12,
                                              color: !_isSuperAdminMode ? Colors.white : AppTheme.textMuted,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                                ),
                                Expanded(
                                  child: GestureDetector(
                                    onTap: () => setState(() => _isSuperAdminMode = true),
                                    child: AnimatedContainer(
                                      duration: const Duration(milliseconds: 200),
                                      padding: const EdgeInsets.symmetric(vertical: 10),
                                      decoration: BoxDecoration(
                                        gradient: _isSuperAdminMode ? AppTheme.accentGradient : null,
                                        color: _isSuperAdminMode ? null : Colors.transparent,
                                        borderRadius: BorderRadius.circular(10),
                                        boxShadow: _isSuperAdminMode
                                            ? [
                                                BoxShadow(
                                                  color: AppTheme.secondary.withOpacity(0.3),
                                                  blurRadius: 8,
                                                  offset: const Offset(0, 2),
                                                ),
                                              ]
                                            : null,
                                      ),
                                      child: Row(
                                        mainAxisAlignment: MainAxisAlignment.center,
                                        children: [
                                          Icon(
                                            Icons.admin_panel_settings_rounded,
                                            size: 16,
                                            color: _isSuperAdminMode ? Colors.white : AppTheme.textMuted,
                                          ),
                                          const SizedBox(width: 6),
                                          Text(
                                            'SuperAdmin',
                                            style: TextStyle(
                                              fontWeight: FontWeight.w700,
                                              fontSize: 12,
                                              color: _isSuperAdminMode ? Colors.white : AppTheme.textMuted,
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
                          const SizedBox(height: 18),

                          // Mensaje de Error
                          if (_errorMessage != null)
                            Container(
                              margin: const EdgeInsets.only(bottom: 16),
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: AppTheme.danger.withOpacity(0.12),
                                border: Border.all(color: AppTheme.danger.withOpacity(0.35)),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.error_outline_rounded, color: AppTheme.danger, size: 20),
                                  const SizedBox(width: 10),
                                  Expanded(
                                    child: Text(
                                      _errorMessage!,
                                      style: const TextStyle(color: Color(0xFFFECDD3), fontSize: 12, fontWeight: FontWeight.w500),
                                    ),
                                  ),
                                ],
                              ),
                            ),

                          // Selector de Centro (Modo Centro)
                          if (!_isSuperAdminMode) ...[
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Row(
                                  children: [
                                    Icon(Icons.apartment_rounded, size: 14, color: AppTheme.primaryLight),
                                    SizedBox(width: 6),
                                    Text(
                                      'SELECCIONAR CENTRO PSICOLÓGICO',
                                      style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.w800,
                                        letterSpacing: 0.4,
                                        color: AppTheme.textMuted,
                                      ),
                                    ),
                                  ],
                                ),
                                IconButton(
                                  icon: const Icon(Icons.refresh_rounded, size: 16, color: AppTheme.primaryLight),
                                  onPressed: _loadTenants,
                                  tooltip: 'Recargar Centros',
                                  padding: EdgeInsets.zero,
                                  constraints: const BoxConstraints(),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            if (_tenants.isEmpty)
                              Container(
                                margin: const EdgeInsets.only(bottom: 16),
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: AppTheme.warning.withOpacity(0.12),
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(color: AppTheme.warning.withOpacity(0.4)),
                                ),
                                child: Row(
                                  children: [
                                    const Icon(Icons.info_outline_rounded, size: 18, color: AppTheme.warning),
                                    const SizedBox(width: 8),
                                    const Expanded(
                                      child: Text(
                                        'Conectando con el servidor para obtener los centros...',
                                        style: TextStyle(fontSize: 11, color: Color(0xFFFDE68A)),
                                      ),
                                    ),
                                    TextButton(
                                      onPressed: _loadTenants,
                                      style: TextButton.styleFrom(padding: EdgeInsets.zero, visualDensity: VisualDensity.compact),
                                      child: const Text('Reintentar', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.primaryLight)),
                                    ),
                                  ],
                                ),
                              )
                            else ...[
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 3),
                                decoration: BoxDecoration(
                                  color: AppTheme.inputBg,
                                  borderRadius: BorderRadius.circular(14),
                                  border: Border.all(color: AppTheme.borderSubtle),
                                ),
                                child: DropdownButtonHideUnderline(
                                  child: DropdownButton<TenantModel>(
                                    value: _selectedTenant,
                                    isExpanded: true,
                                    dropdownColor: AppTheme.cardBgElevated,
                                    icon: const Icon(Icons.keyboard_arrow_down_rounded, color: AppTheme.primaryLight),
                                    items: _tenants.map((t) {
                                      return DropdownMenuItem(
                                        value: t,
                                        child: Row(
                                          children: [
                                            Container(
                                              padding: const EdgeInsets.all(6),
                                              decoration: BoxDecoration(
                                                color: AppTheme.primary.withOpacity(0.15),
                                                borderRadius: BorderRadius.circular(8),
                                              ),
                                              child: const Icon(Icons.domain_rounded, size: 16, color: AppTheme.primaryLight),
                                            ),
                                            const SizedBox(width: 10),
                                            Expanded(
                                              child: Text(
                                                t.nombre,
                                                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                                                overflow: TextOverflow.ellipsis,
                                              ),
                                            ),
                                          ],
                                        ),
                                      );
                                    }).toList(),
                                    onChanged: (val) => setState(() => _selectedTenant = val),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 16),
                            ],
                          ],

                          // Email
                          const Row(
                            children: [
                              Icon(Icons.mail_outline_rounded, size: 14, color: AppTheme.primaryLight),
                              SizedBox(width: 6),
                              Text(
                                'CORREO ELECTRÓNICO',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 0.4,
                                  color: AppTheme.textMuted,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _emailController,
                            keyboardType: TextInputType.emailAddress,
                            decoration: const InputDecoration(
                              hintText: 'admin@centro.com',
                              prefixIcon: Icon(Icons.alternate_email_rounded, size: 20),
                            ),
                          ),
                          const SizedBox(height: 16),

                          // Password
                          const Row(
                            children: [
                              Icon(Icons.lock_outline_rounded, size: 14, color: AppTheme.primaryLight),
                              SizedBox(width: 6),
                              Text(
                                'CONTRASEÑA',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 0.4,
                                  color: AppTheme.textMuted,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _passwordController,
                            obscureText: _obscurePassword,
                            decoration: InputDecoration(
                              hintText: '••••••••',
                              prefixIcon: const Icon(Icons.key_rounded, size: 20),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                                  size: 20,
                                ),
                                onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                              ),
                            ),
                          ),
                          const SizedBox(height: 6),

                          // Enlace Recuperar Contraseña
                          Align(
                            alignment: Alignment.centerRight,
                            child: TextButton(
                              onPressed: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => PasswordResetScreen(authService: widget.authService),
                                  ),
                                );
                              },
                              style: TextButton.styleFrom(
                                visualDensity: VisualDensity.compact,
                                padding: EdgeInsets.zero,
                              ),
                              child: const Text(
                                '¿Olvidaste tu contraseña?',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: AppTheme.primaryLight,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 12),

                          // Botón de Iniciar Sesión con Gradiente
                          Container(
                            height: 52,
                            decoration: BoxDecoration(
                              gradient: AppTheme.primaryGradient,
                              borderRadius: BorderRadius.circular(14),
                              boxShadow: [
                                BoxShadow(
                                  color: AppTheme.primary.withOpacity(0.4),
                                  blurRadius: 16,
                                  offset: const Offset(0, 4),
                                ),
                              ],
                            ),
                            child: Material(
                              color: Colors.transparent,
                              child: InkWell(
                                borderRadius: BorderRadius.circular(14),
                                onTap: _isLoading ? null : _submitLogin,
                                child: Center(
                                  child: _isLoading
                                      ? const SizedBox(
                                          height: 22,
                                          width: 22,
                                          child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white),
                                        )
                                      : const Row(
                                          mainAxisAlignment: MainAxisAlignment.center,
                                          children: [
                                            Text(
                                              'INICIAR SESIÓN',
                                              style: TextStyle(
                                                color: Colors.white,
                                                fontWeight: FontWeight.w800,
                                                fontSize: 14,
                                                letterSpacing: 0.8,
                                              ),
                                            ),
                                            SizedBox(width: 8),
                                            Icon(Icons.arrow_forward_rounded, color: Colors.white, size: 18),
                                          ],
                                        ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Cuentas de Acceso Rápido Demo
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppTheme.cardBg.withOpacity(0.6),
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(color: AppTheme.borderSubtle),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Row(
                            children: [
                              Icon(Icons.flash_on_rounded, size: 16, color: AppTheme.warning),
                              SizedBox(width: 6),
                              Text(
                                'Acceso Rápido para Demostración:',
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w700,
                                  color: AppTheme.textMuted,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: [
                              _buildDemoChip(
                                label: 'SuperAdmin',
                                role: 'Global SaaS',
                                icon: Icons.shield_rounded,
                                color: AppTheme.accent,
                                onTap: () => _fillDemo('admin@sigepsi.com', 'Admin1234*', true, ''),
                              ),
                              _buildDemoChip(
                                label: 'Admin Centro',
                                role: 'Esperanza',
                                icon: Icons.local_hospital_rounded,
                                color: AppTheme.primaryLight,
                                onTap: () => _fillDemo('admin@centroesperanza.com', 'Admin1234*', false, 'centro_esperanza'),
                              ),
                              _buildDemoChip(
                                label: 'Psicólogo',
                                role: 'Terapeuta',
                                icon: Icons.psychology_rounded,
                                color: AppTheme.success,
                                onTap: () => _fillDemo('psicologo@centroesperanza.com', 'Psico1234*', false, 'centro_esperanza'),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),
                    const Text(
                      'SIGEPSI • Plataforma Clínica Segura JWT',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: AppTheme.textSubtle, fontSize: 11),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDemoChip({
    required String label,
    required String role,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: color.withOpacity(0.12),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: color),
            const SizedBox(width: 6),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: color,
                  ),
                ),
                Text(
                  role,
                  style: const TextStyle(
                    fontSize: 9,
                    color: AppTheme.textMuted,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
