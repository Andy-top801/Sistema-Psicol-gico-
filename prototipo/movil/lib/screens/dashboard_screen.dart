import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../core/theme/app_theme.dart';
import 'login_screen.dart';
import 'users_screen.dart';
import 'roles_screen.dart';
import 'centro_config_screen.dart';
import 'tenants_screen.dart';

class DashboardScreen extends StatelessWidget {
  final AuthService authService;

  const DashboardScreen({super.key, required this.authService});

  /// ═════════════════════════════════════════════════════════════════════════
  /// CU2 (Logout): Cierre de Sesión Seguro (HU-09)
  /// Diagrama de Comunicación – Cierre de Sesión (Móvil Flutter)
  /// Participantes:
  ///   Actor  → Usuario Autenticado (Todos los roles)
  ///   IU     → IU_Navbar (Móvil)  ← ESTE ARCHIVO
  ///   CTR    → CTR_AuthLogout (Django REST)
  ///   CE     → CE_TokenBlacklist (PostgreSQL)
  /// ═════════════════════════════════════════════════════════════════════════
  void _confirmLogout(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardBg,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.logout_rounded, color: AppTheme.danger, size: 22),
            SizedBox(width: 8),
            Text('Cerrar Sesión', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        content: const Text(
          '¿Estás seguro de que deseas salir de tu cuenta en SIGEPSI?',
          style: TextStyle(color: AppTheme.textMuted, fontSize: 14),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancelar', style: TextStyle(color: AppTheme.textMuted)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.danger,
              foregroundColor: Colors.white,
            ),
            onPressed: () {
              Navigator.pop(ctx);
              _logout(context);
            },
            child: const Text('Cerrar Sesión'),
          ),
        ],
      ),
    );
  }

  void _logout(BuildContext context) async {
    // --- Paso 1: Click en 'Cerrar Sesión' ---
    // El Actor pulsa el botón de logout en la barra superior
    // --- Paso 2: POST /api/auth/logout/ {refresh} + Bearer JWT ---
    // Se invoca el servicio de logout para revocar token
    await authService.logout();
    // --- Paso 7: 200 OK {"mensaje": "Sesión cerrada"} ---
    if (context.mounted) {
      // --- Paso 8: Redirigir a pantalla de Login ---
      // IU redirige al Actor a LoginScreen
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => LoginScreen(authService: authService),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = authService.currentUser;
    final tenant = authService.currentTenant;

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: AppTheme.primaryGradient,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.psychology_outlined, size: 20, color: Colors.white),
            ),
            const SizedBox(width: 10),
            const Text('SIGEPSI', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
          ],
        ),
        actions: [
          // Chip indicador de sede / tenant
          Container(
            margin: const EdgeInsets.symmetric(vertical: 10),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: AppTheme.cardBgElevated,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.borderSubtle),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 7,
                  height: 7,
                  decoration: const BoxDecoration(
                    color: AppTheme.success,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 100),
                  child: Text(
                    tenant?.nombre ?? 'Global',
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.textMuted),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.logout_rounded, color: AppTheme.danger, size: 22),
            tooltip: 'Cerrar sesión',
            onPressed: () => _confirmLogout(context),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Hero Card: Usuario y Estado Clínico
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: AppTheme.heroGradient,
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: AppTheme.borderSubtle),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.primary.withOpacity(0.08),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(3),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: AppTheme.primaryGradient,
                          ),
                          child: CircleAvatar(
                            radius: 28,
                            backgroundColor: AppTheme.background,
                            child: Text(
                              user?.nombre.isNotEmpty == true ? user!.nombre[0].toUpperCase() : 'U',
                              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.primaryLight),
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '¡Hola, ${user?.nombre ?? "Usuario"}!',
                                style: const TextStyle(fontSize: 19, fontWeight: FontWeight.w800, color: AppTheme.textMain),
                              ),
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  const Icon(Icons.apartment_rounded, size: 14, color: AppTheme.primaryLight),
                                  const SizedBox(width: 4),
                                  Expanded(
                                    child: Text(
                                      tenant?.nombre ?? 'Plataforma SaaS Global',
                                      style: const TextStyle(
                                        color: AppTheme.primaryLight,
                                        fontSize: 12,
                                        fontWeight: FontWeight.w600,
                                      ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 6),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                decoration: BoxDecoration(
                                  color: AppTheme.secondary.withOpacity(0.18),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: AppTheme.secondary.withOpacity(0.3)),
                                ),
                                child: Text(
                                  user?.rolNombre ?? (authService.isSuperAdmin ? 'SuperAdministrador' : 'Usuario'),
                                  style: const TextStyle(fontSize: 10, color: Color(0xFFA5B4FC), fontWeight: FontWeight.w800, letterSpacing: 0.3),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 18),
                    const Divider(height: 1, color: AppTheme.borderSubtle),
                    const SizedBox(height: 14),
                    // Quick KPI Badges
                    Row(
                      children: [
                        _buildQuickKpi('ESTADO', 'Activo', Icons.check_circle_outline_rounded, AppTheme.success),
                        const SizedBox(width: 10),
                        _buildQuickKpi(
                          'MODO',
                          authService.isSuperAdmin ? 'SaaS Global' : 'Tenant Aislado',
                          Icons.cloud_done_outlined,
                          AppTheme.primaryLight,
                        ),
                        const SizedBox(width: 10),
                        _buildQuickKpi('SPRINT', 'Fase 0', Icons.flag_outlined, AppTheme.warning),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Modules List Title
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'MÓDULOS DE GESTIÓN CLÍNICA',
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 0.5, color: AppTheme.textMuted),
                      ),
                      SizedBox(height: 2),
                      Text(
                        'Accesos y operaciones disponibles',
                        style: TextStyle(fontSize: 11, color: AppTheme.textSubtle),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: AppTheme.primary.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      authService.isSuperAdmin ? '1 Módulo' : '3 Módulos',
                      style: const TextStyle(fontSize: 10, color: AppTheme.primaryLight, fontWeight: FontWeight.w700),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),

              // SuperAdmin Module: Tenants
              if (authService.isSuperAdmin) ...[
                _buildMenuCard(
                  context,
                  title: 'Gestión de Centros Psicológicos',
                  subtitle: 'Alta, suspensión y suscripciones multi-tenant',
                  tag: 'SaaS Multi-Tenant',
                  icon: Icons.domain_add_rounded,
                  color: AppTheme.primary,
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => TenantsScreen(authService: authService),
                      ),
                    );
                  },
                ),
              ],

              // Admin Centro Modules
              if (!authService.isSuperAdmin) ...[
                _buildMenuCard(
                  context,
                  title: 'Personal y Terapeutas',
                  subtitle: 'Gestión de psicólogos, recepcionistas y accesos',
                  tag: 'Gestión de Usuarios',
                  icon: Icons.badge_outlined,
                  color: AppTheme.primary,
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => UsersScreen(authService: authService),
                      ),
                    );
                  },
                ),
                _buildMenuCard(
                  context,
                  title: 'Matriz de Roles y Permisos (RBAC)',
                  subtitle: 'Seguridad granular por perfiles clínicos',
                  tag: 'Seguridad & Acceso',
                  icon: Icons.shield_outlined,
                  color: AppTheme.secondary,
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => RolesScreen(authService: authService),
                      ),
                    );
                  },
                ),
                _buildMenuCard(
                  context,
                  title: 'Configuración Institucional',
                  subtitle: 'Nombre, teléfono, dirección y datos del centro',
                  tag: 'Identidad del Centro',
                  icon: Icons.settings_suggest_outlined,
                  color: AppTheme.accent,
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => CentroConfigScreen(authService: authService),
                      ),
                    );
                  },
                ),
              ],

              const SizedBox(height: 20),

              // Pie de página de seguridad
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppTheme.inputBg,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppTheme.borderSubtle),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.verified_user_outlined, size: 18, color: AppTheme.success),
                    SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Arquitectura PostgreSQL con Schemas independientes por centro psicológico.',
                        style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickKpi(String title, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 8),
        decoration: BoxDecoration(
          color: AppTheme.background.withOpacity(0.5),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: AppTheme.borderSubtle),
        ),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, size: 12, color: color),
                const SizedBox(width: 4),
                Text(
                  title,
                  style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w700, color: AppTheme.textSubtle),
                ),
              ],
            ),
            const SizedBox(height: 3),
            Text(
              value,
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: color),
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required String tag,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppTheme.borderSubtle),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(18),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [color.withOpacity(0.25), color.withOpacity(0.08)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: color.withOpacity(0.3)),
                  ),
                  child: Icon(icon, color: color, size: 26),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              title,
                              style: const TextStyle(
                                fontWeight: FontWeight.w800,
                                fontSize: 14,
                                color: AppTheme.textMain,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 3),
                      Text(
                        subtitle,
                        style: const TextStyle(color: AppTheme.textMuted, fontSize: 12),
                      ),
                      const SizedBox(height: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: color.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          tag,
                          style: TextStyle(
                            fontSize: 9,
                            fontWeight: FontWeight.w700,
                            color: color,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 10),
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: AppTheme.inputBg,
                    shape: BoxShape.circle,
                    border: Border.all(color: AppTheme.borderSubtle),
                  ),
                  child: const Icon(Icons.arrow_forward_ios_rounded, size: 12, color: AppTheme.textMuted),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
