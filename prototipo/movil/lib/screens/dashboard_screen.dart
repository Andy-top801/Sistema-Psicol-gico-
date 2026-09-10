import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../core/theme/app_theme.dart';
import 'login_screen.dart';
import 'users_screen.dart';
import 'roles_screen.dart';
import 'centro_config_screen.dart';
import 'tenants_screen.dart';
import 'mis_citas_screen.dart';
import 'reservar_cita_screen.dart';
import 'paciente_perfil_screen.dart';
import 'teleconsulta_jitsi_screen.dart';
import '../models/cita_model.dart';

class DashboardScreen extends StatefulWidget {
  final AuthService authService;

  const DashboardScreen({super.key, required this.authService});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  bool _isRefreshing = false;

  @override
  void initState() {
    super.initState();
    _refreshProfileSilent();
  }

  Future<void> _refreshProfileSilent() async {
    await widget.authService.refreshProfile();
    if (mounted) setState(() {});
  }

  Future<void> _manualRefresh() async {
    setState(() => _isRefreshing = true);
    await widget.authService.refreshProfile();
    if (mounted) {
      setState(() => _isRefreshing = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Perfil y permisos actualizados: ${widget.authService.currentUser?.rolNombre ?? "Usuario"}'),
          backgroundColor: AppTheme.secondary,
          behavior: SnackBarBehavior.floating,
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }

  /// ═════════════════════════════════════════════════════════════════════════
  /// CU2 (Logout): Cierre de Sesión Seguro (HU-09)
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
    await widget.authService.logout();
    if (context.mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => LoginScreen(authService: widget.authService),
        ),
      );
    }
  }

  /// CU13: Iniciar o Unirse a Sala de Teleconsulta (Jitsi Meet WebRTC / HU-19)
  void _abrirTeleconsultaDirecta(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.cardBg,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(22.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: AppTheme.borderSubtle,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppTheme.primary.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(Icons.videocam_rounded, color: AppTheme.primaryLight, size: 26),
                  ),
                  const SizedBox(width: 14),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Teleconsulta / Videollamada',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17, color: AppTheme.textMain),
                        ),
                        Text(
                          'Videoconferencia WebRTC con Jitsi Meet (CU13 / HU-19)',
                          style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                icon: const Icon(Icons.video_call_rounded, size: 22),
                label: const Text('Iniciar / Probar Videollamada en Vivo', style: TextStyle(fontWeight: FontWeight.bold)),
                onPressed: () {
                  Navigator.pop(ctx);
                  final demoCita = CitaModel(
                    id: 'demo-teleconsulta',
                    pacienteId: widget.authService.currentUser?.id ?? '1',
                    pacienteNombre: widget.authService.currentUser?.nombre ?? 'Usuario',
                    psicologoId: '1',
                    psicologoNombre: 'Dra. Elena Ramos (Psicóloga)',
                    fecha: DateTime.now().toIso8601String().substring(0, 10),
                    horaInicio: '15:00:00',
                    horaFin: '15:50:00',
                    modalidad: 'VIRTUAL',
                    estado: 'CONFIRMADA',
                    motivoConsulta: 'Teleconsulta Psicológica - Sesión Virtual WebRTC (HU-19)',
                    costo: 180.0,
                    createdAt: DateTime.now(),
                  );
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => TeleconsultaJitsiScreen(
                        authService: widget.authService,
                        cita: demoCita,
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 10),
              OutlinedButton.icon(
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppTheme.textMain,
                  side: const BorderSide(color: AppTheme.borderSubtle),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                icon: const Icon(Icons.event_available_rounded, size: 20, color: AppTheme.primaryLight),
                label: const Text('Ver Citas Programadas con Teleconsulta'),
                onPressed: () {
                  Navigator.pop(ctx);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => MisCitasScreen(authService: widget.authService),
                    ),
                  );
                },
              ),
              const SizedBox(height: 12),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final user = widget.authService.currentUser;
    final tenant = widget.authService.currentTenant;

    // Clasificación de rol según intento.md (Sprint 0 & 1)
    final bool isSuperAdmin = widget.authService.isSuperAdmin;
    final bool isAdmin = widget.authService.isAdminCentro;
    final bool isPsico = widget.authService.isPsicologo;
    final bool isRecep = widget.authService.isRecepcionista;
    final bool isPaciente = widget.authService.isPaciente || (!isSuperAdmin && !isAdmin && !isPsico && !isRecep);

    // Conteo dinámico de módulos por rol (SuperAdmin accede a TODO: 8 módulos)
    int moduleCount = 0;
    if (isSuperAdmin) {
      moduleCount = 8;
    } else if (isAdmin) {
      moduleCount = 6;
    } else if (isPaciente) {
      moduleCount = 4;
    } else if (isPsico) {
      moduleCount = 3;
    } else if (isRecep) {
      moduleCount = 2;
    }

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
          // Botón para sincronizar rol y permisos en caliente
          IconButton(
            icon: _isRefreshing
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.primaryLight),
                  )
                : const Icon(Icons.sync_rounded, color: AppTheme.primaryLight, size: 20),
            tooltip: 'Sincronizar rol y permisos con el servidor',
            onPressed: _manualRefresh,
          ),
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
                  constraints: const BoxConstraints(maxWidth: 90),
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
            icon: const Icon(Icons.logout_rounded, color: AppTheme.danger, size: 20),
            tooltip: 'Cerrar sesión',
            onPressed: () => _confirmLogout(context),
          ),
          const SizedBox(width: 6),
        ],
      ),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _manualRefresh,
          color: AppTheme.primary,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
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
                                    color: _getRoleBadgeColor(user?.rolNombre).withOpacity(0.18),
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(color: _getRoleBadgeColor(user?.rolNombre).withOpacity(0.35)),
                                  ),
                                  child: Text(
                                    user?.rolNombre ?? (isSuperAdmin ? 'SuperAdministrador' : 'Paciente'),
                                    style: TextStyle(
                                      fontSize: 10,
                                      color: _getRoleBadgeColor(user?.rolNombre),
                                      fontWeight: FontWeight.w800,
                                      letterSpacing: 0.3,
                                    ),
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
                            isSuperAdmin ? 'SaaS Global' : (tenant?.slug ?? 'Tenant'),
                            Icons.cloud_done_outlined,
                            AppTheme.primaryLight,
                          ),
                          const SizedBox(width: 10),
                          _buildQuickKpi('SPRINT', 'Sprint 1', Icons.flag_outlined, AppTheme.accent),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // ═════════════════════════════════════════════════════════════
                // BANNER DE ACCESO DIRECTO: TELECONSULTA / VIDEOLLAMADA (CU13)
                // ═════════════════════════════════════════════════════════════
                Container(
                  margin: const EdgeInsets.only(bottom: 20),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        AppTheme.primary.withOpacity(0.35),
                        const Color(0xFF6366F1).withOpacity(0.18),
                      ],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(color: AppTheme.primaryLight.withOpacity(0.4)),
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.primary.withOpacity(0.15),
                        blurRadius: 14,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          gradient: AppTheme.primaryGradient,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.videocam_rounded, color: Colors.white, size: 24),
                      ),
                      const SizedBox(width: 14),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Teleconsulta / Videollamada en Vivo',
                              style: TextStyle(fontWeight: FontWeight.w800, fontSize: 13, color: AppTheme.textMain),
                            ),
                            SizedBox(height: 2),
                            Text(
                              'Videoconferencia WebRTC con Jitsi Meet (HU-19)',
                              style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                            ),
                          ],
                        ),
                      ),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.primaryLight,
                          foregroundColor: AppTheme.background,
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                          visualDensity: VisualDensity.compact,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        onPressed: () => _abrirTeleconsultaDirecta(context),
                        child: const Text('ENTRAR', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 11)),
                      ),
                    ],
                  ),
                ),

                // Encabezado de la lista de módulos adaptado por Rol
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isSuperAdmin
                              ? 'ADMINISTRACIÓN TOTAL SAAS'
                              : isPaciente
                                  ? 'MIS SERVICIOS DE SALUD MENTAL'
                                  : isPsico
                                      ? 'PORTAL CLÍNICO DEL TERAPEUTA'
                                      : isAdmin
                                          ? 'GESTIÓN INSTITUCIONAL (ADMIN)'
                                          : 'MÓDULOS DEL SISTEMA',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 0.5, color: AppTheme.textMuted),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          isSuperAdmin
                              ? 'Acceso irrestricto a todos los módulos y configuración'
                              : isPaciente
                                  ? 'Casos de uso para Pacientes (Sprint 1)'
                                  : isPsico
                                      ? 'Gestión de citas y teleconsulta Jitsi'
                                      : isAdmin
                                          ? 'Personal, roles y configuración del centro'
                                          : 'Operaciones activas según tu rol',
                          style: const TextStyle(fontSize: 11, color: AppTheme.textSubtle),
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
                        '$moduleCount ${moduleCount == 1 ? "Módulo" : "Módulos"}',
                        style: const TextStyle(fontSize: 10, color: AppTheme.primaryLight, fontWeight: FontWeight.w700),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),

                // ═════════════════════════════════════════════════════════════
                // ROL 1: SUPERADMINISTRADOR (Acceso Total a Todos los Módulos)
                // ═════════════════════════════════════════════════════════════
                if (isSuperAdmin) ...[
                  _buildMenuCard(
                    context,
                    title: 'Gestión de Centros Psicológicos',
                    subtitle: 'Alta, suspensión y suscripciones multi-tenant',
                    tag: 'SaaS Multi-Tenant • CU1',
                    icon: Icons.domain_add_rounded,
                    color: AppTheme.primary,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => TenantsScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Personal, Terapeutas y Accesos',
                    subtitle: 'Gestión global de psicólogos, recepcionistas y staff',
                    tag: 'Gestión de Usuarios • CU3',
                    icon: Icons.badge_outlined,
                    color: AppTheme.info,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => UsersScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Matriz de Roles y Permisos (RBAC)',
                    subtitle: 'Configuración granular de seguridad y privilegios',
                    tag: 'Seguridad Granular • CU4',
                    icon: Icons.shield_outlined,
                    color: const Color(0xFF6366F1),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => RolesScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Configuración Institucional',
                    subtitle: 'Datos de la clínica, sedes, dirección y contacto',
                    tag: 'Identidad del Centro • CU1',
                    icon: Icons.settings_suggest_outlined,
                    color: const Color(0xFFF59E0B),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => CentroConfigScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Agenda Central y Citas',
                    subtitle: 'Supervisión de sesiones, teleconsultas y estado de citas',
                    tag: 'Agenda Central • CU11',
                    icon: Icons.calendar_month_rounded,
                    color: AppTheme.primary,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => MisCitasScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Sala de Teleconsulta / Videollamada',
                    subtitle: 'Llamadas y videollamadas WebRTC Jitsi Meet en vivo',
                    tag: 'Videoconferencia • CU13',
                    icon: Icons.video_camera_front_rounded,
                    color: const Color(0xFF10B981),
                    onTap: () => _abrirTeleconsultaDirecta(context),
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Simulador / Reservar Cita',
                    subtitle: 'Probar flujo completo de reserva de citas para pacientes',
                    tag: 'Prueba de Citas • CU11',
                    icon: Icons.add_circle_outline_rounded,
                    color: AppTheme.secondary,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => ReservarCitaScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Expediente Clínico y Ficha del Paciente',
                    subtitle: 'Ficha clínica, contacto de emergencia y tutor legal',
                    tag: 'Salud Mental • CU7',
                    icon: Icons.contact_page_outlined,
                    color: AppTheme.accent,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => PacientePerfilScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                ],

                // ═════════════════════════════════════════════════════════════
                // ROL 2: PACIENTE (CU7, CU11, CU13 - Enfoque Principal Móvil)
                // ═════════════════════════════════════════════════════════════
                if (isPaciente) ...[
                  _buildMenuCard(
                    context,
                    title: 'Mis Citas y Agenda',
                    subtitle: 'Consulta de sesiones, historial y estado de turnos',
                    tag: 'Citas • CU11',
                    icon: Icons.calendar_month_rounded,
                    color: AppTheme.primary,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => MisCitasScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Sala de Teleconsulta / Videollamada',
                    subtitle: 'Acceso a videollamada Jitsi Meet WebRTC con tu terapeuta',
                    tag: 'Videollamada • CU13',
                    icon: Icons.video_camera_front_rounded,
                    color: const Color(0xFF10B981),
                    onTap: () => _abrirTeleconsultaDirecta(context),
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Reservar Cita Médica',
                    subtitle: 'Selección de terapeuta, modalidad y slots disponibles',
                    tag: 'Reserva en Vivo • CU11',
                    icon: Icons.add_circle_outline_rounded,
                    color: AppTheme.secondary,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => ReservarCitaScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Mi Expediente y Perfil',
                    subtitle: 'Ficha del paciente, contacto de emergencia y tutor',
                    tag: 'Expediente Paciente • CU7',
                    icon: Icons.contact_page_outlined,
                    color: AppTheme.accent,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => PacientePerfilScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                ],

                // ═════════════════════════════════════════════════════════════
                // ROL 3: PSICÓLOGO / TERAPEUTA (CU11, CU13, CU6)
                // ═════════════════════════════════════════════════════════════
                if (isPsico) ...[
                  _buildMenuCard(
                    context,
                    title: 'Mis Sesiones y Citas',
                    subtitle: 'Pacientes citados, horarios y estado de atención',
                    tag: 'Atención Clínica • CU11',
                    icon: Icons.calendar_month_rounded,
                    color: AppTheme.primary,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => MisCitasScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Sala de Teleconsulta / Videollamada',
                    subtitle: 'Videollamada Jitsi Meet WebRTC como anfitrión/moderador',
                    tag: 'Videoconsulta • CU13',
                    icon: Icons.video_camera_front_rounded,
                    color: const Color(0xFF10B981),
                    onTap: () => _abrirTeleconsultaDirecta(context),
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Directorio de Colegas y Personal',
                    subtitle: 'Consulta de psicólogos del centro y especialidades',
                    tag: 'Directorio • CU6',
                    icon: Icons.people_outline_rounded,
                    color: AppTheme.info,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => UsersScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                ],

                // ═════════════════════════════════════════════════════════════
                // ROL 4: RECEPCIONISTA (CU11, CU6)
                // ═════════════════════════════════════════════════════════════
                if (isRecep) ...[
                  _buildMenuCard(
                    context,
                    title: 'Agenda y Citas del Centro',
                    subtitle: 'Consulta y coordinación de citas de todos los psicólogos',
                    tag: 'Agenda General • CU11',
                    icon: Icons.calendar_today_rounded,
                    color: AppTheme.primary,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => MisCitasScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Directorio de Terapeutas',
                    subtitle: 'Lista de psicólogos y disponibilidad de consultorios',
                    tag: 'Personal • CU6',
                    icon: Icons.badge_outlined,
                    color: AppTheme.info,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => UsersScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                ],

                // ═════════════════════════════════════════════════════════════
                // ROL 5: ADMINISTRADOR DEL CENTRO (CU3, CU4, CU1, CU11, CU13)
                // ═════════════════════════════════════════════════════════════
                if (isAdmin) ...[
                  _buildMenuCard(
                    context,
                    title: 'Personal y Terapeutas',
                    subtitle: 'Gestión de psicólogos, recepcionistas y accesos',
                    tag: 'Gestión de Usuarios • CU3',
                    icon: Icons.badge_outlined,
                    color: AppTheme.info,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => UsersScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Matriz de Roles y Permisos (RBAC)',
                    subtitle: 'Configuración de seguridad y capacidades por perfil',
                    tag: 'Seguridad Granular • CU4',
                    icon: Icons.shield_outlined,
                    color: const Color(0xFF6366F1),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => RolesScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Configuración Institucional',
                    subtitle: 'Nombre, teléfono, dirección y datos del centro',
                    tag: 'Identidad del Centro • CU1',
                    icon: Icons.settings_suggest_outlined,
                    color: const Color(0xFFF59E0B),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => CentroConfigScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Agenda y Citas del Centro',
                    subtitle: 'Supervisión de sesiones, teleconsultas y estado',
                    tag: 'Agenda Central • CU11',
                    icon: Icons.calendar_month_rounded,
                    color: AppTheme.primary,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => MisCitasScreen(authService: widget.authService),
                        ),
                      );
                    },
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Sala de Teleconsulta / Videollamada',
                    subtitle: 'Supervisión y prueba de videollamadas Jitsi Meet WebRTC',
                    tag: 'Videoconferencia • CU13',
                    icon: Icons.video_camera_front_rounded,
                    color: const Color(0xFF10B981),
                    onTap: () => _abrirTeleconsultaDirecta(context),
                  ),
                  _buildMenuCard(
                    context,
                    title: 'Simulador / Reservar Cita',
                    subtitle: 'Probar flujo de reserva de citas para pacientes',
                    tag: 'Prueba de Citas • CU11',
                    icon: Icons.add_circle_outline_rounded,
                    color: AppTheme.secondary,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => ReservarCitaScreen(authService: widget.authService),
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
                  child: Row(
                    children: [
                      const Icon(Icons.verified_user_outlined, size: 18, color: AppTheme.success),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          isPaciente
                              ? 'Aplicación móvil de salud mental protegida con cifrado SSL y JWT.'
                              : 'Arquitectura PostgreSQL con Schemas independientes por centro psicológico.',
                          style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _getRoleBadgeColor(String? role) {
    if (role == null) return AppTheme.secondary;
    final r = role.toLowerCase();
    if (r.contains('paciente')) return AppTheme.accent;
    if (r.contains('psic')) return AppTheme.primaryLight;
    if (r.contains('admin')) return const Color(0xFF6366F1);
    if (r.contains('super')) return const Color(0xFFF59E0B);
    return AppTheme.secondary;
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
