// ==============================================================================
// MÓDULO: centro_notificaciones_screen.dart
// CAPA BCE: BOUNDARY — IU_CentroNotificacionesMovil (Prototipo Figma HU-43)
// CASO DE USO: CU12 / HU-43 — Recordatorios automáticos y notificaciones push.
//   • Centro de Notificaciones: lista de recordatorios recibidos (24 h / 1 h).
//   • Banner emergente tipo push cuando llega un recordatorio con la app abierta.
//   • Criterio (c): al tocar, abre la Teleconsulta (VIRTUAL) o el Detalle de la Cita.
// ==============================================================================
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../core/theme/app_theme.dart';
import '../models/cita_model.dart';
import '../services/notificaciones_service.dart';
import 'teleconsulta_jitsi_screen.dart';

// ─────────────────────────────── Navegación (c) ───────────────────────────────

Future<void> abrirDestinoNotificacion(NotificacionModel n) async {
  final svc = NotificacionesService.instance;
  final nav = appNavigatorKey.currentState;
  final auth = svc.auth;
  if (nav == null || auth == null) return;
  final messenger = ScaffoldMessenger.maybeOf(nav.context);

  final cita = await svc.obtenerCita(n.citaId);
  if (cita == null) {
    messenger?.showSnackBar(
      const SnackBar(content: Text('No se pudo abrir la cita. Intenta de nuevo.'), behavior: SnackBarBehavior.floating),
    );
    return;
  }
  // Regla CU13: la sala Jitsi se habilita 10 min antes; antes de eso se muestra el detalle.
  final inicio = DateTime.tryParse('${cita.fecha} ${cita.horaInicioCorta}:00');
  final salaAbierta = inicio != null && DateTime.now().isAfter(inicio.subtract(const Duration(minutes: 10)));
  if (cita.isVirtual && salaAbierta) {
    nav.push(MaterialPageRoute(builder: (_) => TeleconsultaJitsiScreen(authService: auth, cita: cita)));
  } else {
    nav.push(MaterialPageRoute(builder: (_) => DetalleCitaScreen(cita: cita)));
  }
}

// ─────────────────────────────── Estilo por tipo ──────────────────────────────

IconData _icono(NotificacionModel n) {
  if (n.esVirtual) return Icons.videocam_rounded;
  return n.esUnaHora ? Icons.hourglass_top_rounded : Icons.event_available_rounded;
}

Color _color(NotificacionModel n) {
  if (n.esVirtual) return AppTheme.info;
  return n.esUnaHora ? AppTheme.warning : AppTheme.primaryLight;
}

String _haceCuanto(DateTime? f) {
  if (f == null) return '';
  final d = DateTime.now().difference(f);
  if (d.inMinutes < 1) return 'ahora';
  if (d.inMinutes < 60) return 'hace ${d.inMinutes} min';
  if (d.inHours < 24) return 'hace ${d.inHours} h';
  return DateFormat('dd/MM HH:mm').format(f);
}

String _fechaLarga(String yyyyMmDd) {
  final f = DateTime.tryParse(yyyyMmDd);
  if (f == null) return yyyyMmDd;
  final s = DateFormat("EEEE d 'de' MMMM", 'es').format(f);
  return s[0].toUpperCase() + s.substring(1);
}

// ─────────────────────────── Banner emergente (b) ─────────────────────────────

OverlayEntry? _bannerActual;

void mostrarBannerPush(NotificacionModel n) {
  final overlay = appNavigatorKey.currentState?.overlay;
  if (overlay == null) return;
  _bannerActual?.remove();
  late OverlayEntry entry;
  entry = OverlayEntry(
    builder: (_) => _PushBanner(
      n: n,
      onTap: () {
        entry.remove();
        if (_bannerActual == entry) _bannerActual = null;
        NotificacionesService.instance.abrir(n);
      },
      onClose: () {
        if (entry.mounted) entry.remove();
        if (_bannerActual == entry) _bannerActual = null;
      },
    ),
  );
  _bannerActual = entry;
  overlay.insert(entry);
}

class _PushBanner extends StatefulWidget {
  final NotificacionModel n;
  final VoidCallback onTap;
  final VoidCallback onClose;
  const _PushBanner({required this.n, required this.onTap, required this.onClose});

  @override
  State<_PushBanner> createState() => _PushBannerState();
}

class _PushBannerState extends State<_PushBanner> with SingleTickerProviderStateMixin {
  late final AnimationController _c =
      AnimationController(vsync: this, duration: const Duration(milliseconds: 380))..forward();

  @override
  void initState() {
    super.initState();
    Future.delayed(const Duration(seconds: 8), () async {
      if (!mounted) return;
      await _c.reverse();
      widget.onClose();
    });
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final n = widget.n;
    return Positioned(
      top: MediaQuery.of(context).padding.top + 10,
      left: 12,
      right: 12,
      child: SlideTransition(
        position: Tween(begin: const Offset(0, -1.4), end: Offset.zero)
            .animate(CurvedAnimation(parent: _c, curve: Curves.easeOutBack)),
        child: Material(
          color: Colors.transparent,
          child: Dismissible(
            key: ValueKey('banner-${n.id}'),
            direction: DismissDirection.up,
            onDismissed: (_) => widget.onClose(),
            child: GestureDetector(
              onTap: widget.onTap,
              child: Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xF2163A2F),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: AppTheme.borderFocus),
                  boxShadow: const [BoxShadow(color: Color(0x80000000), blurRadius: 24, offset: Offset(0, 10))],
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(gradient: AppTheme.primaryGradient, borderRadius: BorderRadius.circular(12)),
                      child: const Icon(Icons.psychology_outlined, color: Colors.white, size: 22),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('SIGEPSI • ahora',
                              style: TextStyle(fontSize: 11, color: AppTheme.textMuted, fontWeight: FontWeight.w600)),
                          const SizedBox(height: 2),
                          Text(n.titulo,
                              style: const TextStyle(fontSize: 14.5, fontWeight: FontWeight.w800, color: AppTheme.textMain)),
                          const SizedBox(height: 3),
                          Text(n.cuerpo,
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(fontSize: 12.5, height: 1.35, color: AppTheme.textMain)),
                        ],
                      ),
                    ),
                    Icon(_icono(n), color: _color(n), size: 20),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────── Centro de Notificaciones ─────────────────────────

class CentroNotificacionesScreen extends StatefulWidget {
  const CentroNotificacionesScreen({super.key});

  @override
  State<CentroNotificacionesScreen> createState() => _CentroNotificacionesScreenState();
}

class _CentroNotificacionesScreenState extends State<CentroNotificacionesScreen> {
  final svc = NotificacionesService.instance;

  @override
  void initState() {
    super.initState();
    svc.cargar();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Centro de Notificaciones', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
        actions: [
          ListenableBuilder(
            listenable: svc,
            builder: (_, __) => svc.noLeidas > 0
                ? TextButton.icon(
                    onPressed: svc.marcarTodasLeidas,
                    icon: const Icon(Icons.done_all_rounded, size: 18, color: AppTheme.primaryLight),
                    label: const Text('Leídas', style: TextStyle(color: AppTheme.primaryLight, fontWeight: FontWeight.w700)),
                  )
                : const SizedBox.shrink(),
          ),
          const SizedBox(width: 6),
        ],
      ),
      body: ListenableBuilder(
        listenable: svc,
        builder: (context, _) {
          return RefreshIndicator(
            color: AppTheme.primary,
            onRefresh: svc.cargar,
            child: ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 28),
              children: [
                _cabecera(),
                const SizedBox(height: 18),
                if (svc.cargando && svc.items.isEmpty)
                  const Padding(
                    padding: EdgeInsets.only(top: 60),
                    child: Center(child: CircularProgressIndicator(color: AppTheme.primaryLight)),
                  )
                else if (svc.items.isEmpty)
                  _vacio()
                else ...[
                  if (svc.items.any((n) => !n.leida)) _seccion('Nuevas'),
                  ...svc.items.where((n) => !n.leida).map(_tarjeta),
                  if (svc.items.any((n) => n.leida)) _seccion('Anteriores'),
                  ...svc.items.where((n) => n.leida).map(_tarjeta),
                ],
                if (svc.error != null) ...[
                  const SizedBox(height: 12),
                  Text(svc.error!, textAlign: TextAlign.center, style: const TextStyle(color: AppTheme.danger, fontSize: 12)),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _cabecera() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF19734E), Color(0xFF0F3D2F)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(22),
        boxShadow: const [BoxShadow(color: AppTheme.glowMint, blurRadius: 24, offset: Offset(0, 8))],
      ),
      child: Row(
        children: [
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(color: Colors.white.withOpacity(0.14), borderRadius: BorderRadius.circular(16)),
            child: Stack(
              alignment: Alignment.center,
              children: [
                const Icon(Icons.notifications_active_rounded, color: Colors.white, size: 26),
                if (svc.noLeidas > 0)
                  Positioned(
                    top: 8,
                    right: 8,
                    child: Container(
                      width: 10,
                      height: 10,
                      decoration: BoxDecoration(
                        color: AppTheme.danger,
                        shape: BoxShape.circle,
                        border: Border.all(color: const Color(0xFF19734E), width: 2),
                      ),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  svc.noLeidas == 0
                      ? 'Estás al día'
                      : '${svc.noLeidas} recordatorio${svc.noLeidas == 1 ? '' : 's'} sin leer',
                  style: const TextStyle(color: Colors.white, fontSize: 17, fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Te avisamos 24 h y 1 h antes de cada cita confirmada.',
                  style: TextStyle(color: Color(0xFFCDEBDD), fontSize: 12.5, height: 1.3),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _seccion(String t) => Padding(
        padding: const EdgeInsets.only(left: 4, bottom: 10, top: 6),
        child: Text(t.toUpperCase(),
            style: const TextStyle(
                color: AppTheme.textSubtle, fontSize: 11.5, fontWeight: FontWeight.w800, letterSpacing: 1.1)),
      );

  Widget _tarjeta(NotificacionModel n) {
    final color = _color(n);
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Material(
        color: n.leida ? AppTheme.cardBg : AppTheme.cardBgElevated,
        borderRadius: BorderRadius.circular(18),
        child: InkWell(
          borderRadius: BorderRadius.circular(18),
          onTap: () => svc.abrir(n),
          child: Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: n.leida ? AppTheme.borderSubtle : color.withOpacity(0.45)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(color: color.withOpacity(0.16), borderRadius: BorderRadius.circular(14)),
                  child: Icon(_icono(n), color: color, size: 22),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(n.titulo,
                                style: const TextStyle(
                                    fontWeight: FontWeight.w800, fontSize: 14.5, color: AppTheme.textMain)),
                          ),
                          Text(_haceCuanto(n.fechaEnvio),
                              style: const TextStyle(fontSize: 11, color: AppTheme.textSubtle)),
                          if (!n.leida) ...[
                            const SizedBox(width: 6),
                            Container(
                              width: 8,
                              height: 8,
                              decoration: const BoxDecoration(color: AppTheme.primaryLight, shape: BoxShape.circle),
                            ),
                          ],
                        ],
                      ),
                      const SizedBox(height: 5),
                      Text(n.cuerpo,
                          style: const TextStyle(fontSize: 13, height: 1.4, color: AppTheme.textMuted)),
                      const SizedBox(height: 10),
                      Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          _chip(n.esUnaHora ? 'En 1 hora' : '24 h antes', color),
                          _chip(n.esVirtual ? 'Teleconsulta' : 'Presencial', AppTheme.textMuted,
                              icon: n.esVirtual ? Icons.videocam_outlined : Icons.place_outlined),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          Text(n.esVirtual ? 'Abrir teleconsulta' : 'Ver detalle de la cita',
                              style: TextStyle(color: color, fontWeight: FontWeight.w700, fontSize: 12.5)),
                          const SizedBox(width: 4),
                          Icon(Icons.arrow_forward_rounded, size: 16, color: color),
                        ],
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

  Widget _chip(String t, Color c, {IconData? icon}) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
        decoration: BoxDecoration(
          color: c.withOpacity(0.12),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: c.withOpacity(0.25)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon != null) ...[Icon(icon, size: 13, color: c), const SizedBox(width: 4)],
            Text(t, style: TextStyle(color: c, fontSize: 11.5, fontWeight: FontWeight.w700)),
          ],
        ),
      );

  Widget _vacio() => Padding(
        padding: const EdgeInsets.only(top: 50),
        child: Column(
          children: [
            Container(
              width: 84,
              height: 84,
              decoration: BoxDecoration(color: AppTheme.cardBgElevated, shape: BoxShape.circle,
                  border: Border.all(color: AppTheme.borderSubtle)),
              child: const Icon(Icons.notifications_off_outlined, color: AppTheme.textSubtle, size: 38),
            ),
            const SizedBox(height: 18),
            const Text('No tienes notificaciones',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textMain)),
            const SizedBox(height: 6),
            const Text(
              'Cuando tengas una cita confirmada, recibirás aquí\ny en tu teléfono un recordatorio 24 h y 1 h antes.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, height: 1.45, color: AppTheme.textMuted),
            ),
          ],
        ),
      );
}

// ─────────────────────────── Detalle de la cita (c) ───────────────────────────

class DetalleCitaScreen extends StatelessWidget {
  final CitaModel cita;
  const DetalleCitaScreen({super.key, required this.cita});

  @override
  Widget build(BuildContext context) {
    final estadoColor = cita.estado == 'CONFIRMADA'
        ? AppTheme.success
        : cita.estado == 'CANCELADA'
            ? AppTheme.danger
            : AppTheme.warning;
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(title: const Text('Detalle de la Cita', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18))),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(24),
              boxShadow: const [BoxShadow(color: AppTheme.glowMint, blurRadius: 24, offset: Offset(0, 8))],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(color: Colors.white.withOpacity(0.18), borderRadius: BorderRadius.circular(20)),
                      child: Text(cita.estado,
                          style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 0.6)),
                    ),
                    const Spacer(),
                    const Icon(Icons.event_available_rounded, color: Colors.white, size: 26),
                  ],
                ),
                const SizedBox(height: 16),
                Text(_fechaLarga(cita.fecha),
                    style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800)),
                const SizedBox(height: 4),
                Text('${cita.horaInicioCorta} – ${cita.horaFinCorta}',
                    style: const TextStyle(color: Color(0xFFE2F7EE), fontSize: 30, fontWeight: FontWeight.w900, letterSpacing: -0.5)),
              ],
            ),
          ),
          const SizedBox(height: 18),
          _fila(Icons.person_rounded, 'Psicólogo/a', cita.psicologoNombre.isEmpty ? '—' : cita.psicologoNombre),
          _fila(Icons.place_rounded, 'Modalidad', cita.isVirtual ? 'Teleconsulta (virtual)' : 'Presencial en el centro'),
          _fila(Icons.flag_rounded, 'Estado', cita.estado, color: estadoColor),
          if (cita.motivoConsulta.isNotEmpty) _fila(Icons.notes_rounded, 'Motivo', cita.motivoConsulta),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppTheme.info.withOpacity(0.08),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.info.withOpacity(0.25)),
            ),
            child: Row(
              children: [
                const Icon(Icons.info_outline_rounded, color: AppTheme.info, size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                      cita.isVirtual
                          ? 'La sala de teleconsulta se habilita 10 minutos antes del inicio. Vuelve a abrir el recordatorio a esa hora para unirte.'
                          : 'Llega 10 minutos antes. Si no puedes asistir, cancela con más de 24 h de anticipación.',
                      style: const TextStyle(color: AppTheme.textMuted, fontSize: 12.5, height: 1.4)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _fila(IconData icon, String label, String value, {Color? color}) => Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppTheme.cardBg,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.borderSubtle),
        ),
        child: Row(
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(color: AppTheme.cardBgElevated, borderRadius: BorderRadius.circular(12)),
              child: Icon(icon, color: color ?? AppTheme.primaryLight, size: 20),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label, style: const TextStyle(color: AppTheme.textSubtle, fontSize: 11.5, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 2),
                  Text(value,
                      style: TextStyle(color: color ?? AppTheme.textMain, fontSize: 14.5, fontWeight: FontWeight.w700)),
                ],
              ),
            ),
          ],
        ),
      );
}
