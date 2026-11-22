// ==============================================================================
// MÓDULO: mis_citas_movil_screen.dart
// CAPA BCE: BOUNDARY — IU_MisCitasMovil
// CASO DE USO: CU11 Móvil — Gestión y Cancelación de Cita con Política >24h
// HISTORIAS: HU-41 (consulta y navegación de citas) · HU-42 (cancelación / reprogramación)
//
// Métodos del Diagrama de Clases de Análisis:
//   abrir_agenda_movil()            → carga 'Próximas' e 'Historial' (HU-41)
//   mostrar_citas_por_estado()      → pestañas + tags de estado y modalidad (HU-41)
//   presionar_cancelar_cita()       → CU11-paso 1 y CU11-paso 2 del Diagrama de Secuencia (HU-42)
//   mostrar_confirmacion_cancelacion() → CU11-paso 17 (rama alt > 24 h)
//   mostrar_aviso_politica_24h()    → CU11-paso 19 (rama else <= 24 h) + WhatsApp a Recepción
//
// Las decisiones temporales (puede_cancelar, puede_entrar_teleconsulta) llegan
// calculadas por el SERVIDOR; la app no usa el reloj del teléfono (HU-42 c).
// ==============================================================================
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

import '../core/theme/app_theme.dart';
import '../models/cita_model.dart';
import '../services/agenda_service.dart';
import '../services/auth_service.dart';
import 'reservar_cita_screen.dart';
import 'teleconsulta_jitsi_screen.dart';

/// Vista de una cita tal como la entrega GET /api/v1/citas/mis-citas/
class CitaMovil {
  final Map<String, dynamic> d;
  CitaMovil(this.d);

  String get id => d['id'] ?? '';
  String get fecha => d['fecha'] ?? '';
  String get horaInicio => d['hora_inicio'] ?? '';
  String get horaFin => d['hora_fin'] ?? '';
  String get modalidad => d['modalidad'] ?? 'PRESENCIAL';
  String get estado => d['estado'] ?? '';
  String get estadoEtiqueta => d['estado_etiqueta'] ?? estado;
  String get psicologo => d['psicologo_nombre'] ?? 'Psicólogo/a';
  String get iniciales => (d['psicologo_iniciales'] ?? 'PS').toString();
  String? get foto => d['psicologo_foto'];
  String get especialidad => d['especialidad'] ?? '';
  String get consultorio => d['consultorio'] ?? '';
  String get enlaceVirtual => d['enlace_virtual'] ?? '';
  String get motivoCancelacion => d['motivo_cancelacion'] ?? '';
  int get minutosParaInicio => (d['minutos_para_inicio'] ?? 0) as int;
  bool get esVirtual => modalidad == 'VIRTUAL';
  bool get puedeEntrar => d['puede_entrar_teleconsulta'] == true;
  bool get puedeCancelar => d['puede_cancelar'] == true;
  DateTime? get fechaDt => DateTime.tryParse(fecha);

  CitaModel toCitaModel() => CitaModel(
        id: id,
        pacienteId: '',
        pacienteNombre: '',
        psicologoId: d['psicologo_id'] ?? '',
        psicologoNombre: psicologo,
        fecha: fecha,
        horaInicio: '$horaInicio:00',
        horaFin: '$horaFin:00',
        modalidad: modalidad,
        estado: estado,
        motivoConsulta: d['motivo_consulta'] ?? '',
        costo: (d['costo'] ?? 0).toDouble(),
      );
}

class MisCitasMovilScreen extends StatefulWidget {
  final AuthService authService;
  const MisCitasMovilScreen({super.key, required this.authService});

  @override
  State<MisCitasMovilScreen> createState() => _MisCitasMovilScreenState();
}

class _MisCitasMovilScreenState extends State<MisCitasMovilScreen> with SingleTickerProviderStateMixin {
  late final AgendaService _agenda = AgendaService(authService: widget.authService);
  late final TabController _tabs = TabController(length: 2, vsync: this);
  Timer? _timer;

  bool _cargando = true;
  String? _error;
  List<CitaMovil> _proximas = [];
  List<CitaMovil> _historial = [];
  String _whatsapp = '';
  String _telefono = '';
  String _centro = '';
  int _politicaHoras = 24;

  @override
  void initState() {
    super.initState();
    abrirAgendaMovil();
    // Re-consulta periódica: habilita 'Entrar a Teleconsulta' cuando faltan < 10 min (HU-41 c)
    _timer = Timer.periodic(const Duration(seconds: 30), (_) => abrirAgendaMovil(silencioso: true));
  }

  @override
  void dispose() {
    _timer?.cancel();
    _tabs.dispose();
    super.dispose();
  }

  // ───────────────────────────── HU-41 ─────────────────────────────

  /// abrir_agenda_movil()
  Future<void> abrirAgendaMovil({bool silencioso = false}) async {
    if (!silencioso) setState(() => _cargando = true);
    final r = await _agenda.listarCitasPaciente();
    if (!mounted) return;
    setState(() {
      _cargando = false;
      if (r['success'] == true) {
        _error = null;
        _proximas = (r['proximas'] as List).map((e) => CitaMovil(Map<String, dynamic>.from(e))).toList();
        _historial = (r['historial'] as List).map((e) => CitaMovil(Map<String, dynamic>.from(e))).toList();
        _whatsapp = r['whatsapp_recepcion'] ?? '';
        _telefono = r['telefono_recepcion'] ?? '';
        _centro = r['centro_nombre'] ?? '';
        _politicaHoras = r['politica_cancelacion_horas'] ?? 24;
      } else if (!silencioso) {
        _error = r['error'];
      }
    });
  }

  Future<void> _agendarCita() async {
    final ok = await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => ReservarCitaScreen(authService: widget.authService)),
    );
    if (ok == true) abrirAgendaMovil();
  }

  Future<void> _entrarTeleconsulta(CitaMovil c) async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => TeleconsultaJitsiScreen(authService: widget.authService, cita: c.toCitaModel())),
    );
    abrirAgendaMovil(silencioso: true);
  }

  // ───────────────────────────── HU-42 ─────────────────────────────

  /// CU11-paso 1: presionar_cancelar_cita(cita_id, motivo) — el Paciente toca 'Cancelar' en IU_MisCitasMovil.
  Future<void> presionarCancelarCita(CitaMovil c) async {
    // Criterio (b): con < 24 h el botón está deshabilitado y se informa la política
    if (!c.puedeCancelar) {
      mostrarAvisoPoliticaCita(c);
      return;
    }
    final motivo = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _ConfirmarCancelacionSheet(cita: c),
    );
    if (motivo == null || !mounted) return;

    _mostrarProgreso();
    // CU11-paso 2: POST /api/v1/citas/{id}/cancelar/ (motivo) → CTR_CitaMovilController
    final r = await _agenda.cancelarCitaMovil(c.id, motivo);
    if (!mounted) return;
    Navigator.of(context, rootNavigator: true).pop(); // cierra progreso

    // CU11-paso 16: HTTP 200 OK {'Cita cancelada y bloque liberado'} [retorno]
    if (r['status'] == 200) {
      await abrirAgendaMovil(silencioso: true);
      // CU11-paso 17: mostrar_confirmacion_cancelacion('Cita cancelada con éxito')
      if (mounted) mostrarConfirmacionCancelacion(c);
    } else if (r['codigo'] == 'CANCELLATION_WINDOW_EXPIRED') {
      // CU11-paso 18: HTTP 400 Bad Request {'Plazo expirado: cancelaciones requieren > 24h'} [retorno]
      _whatsapp = r['whatsapp_recepcion'] ?? _whatsapp;
      // CU11-paso 19: mostrar_aviso_politica_24h('Cancelación rechazada por política 24h')
      mostrarAvisoPolitica24h(c, mensajeServidor: r['error']);
      abrirAgendaMovil(silencioso: true);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        behavior: SnackBarBehavior.floating,
        backgroundColor: AppTheme.danger,
        content: Text(r['error'] ?? 'No se pudo cancelar la cita.'),
      ));
    }
  }

  void _mostrarProgreso() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator(color: AppTheme.primaryLight)),
    );
  }

  /// CU11-paso 17: mostrar_confirmacion_cancelacion('Cita cancelada con éxito') [retorno al Paciente]
  void mostrarConfirmacionCancelacion(CitaMovil c) {
    showDialog(
      context: context,
      builder: (ctx) => _DialogoBase(
        icono: Icons.check_circle_rounded,
        color: AppTheme.success,
        titulo: 'Cita cancelada con éxito',
        texto: 'Tu sesión con ${c.psicologo} del ${_fechaCorta(c)} a las ${c.horaInicio} fue cancelada '
            'y el horario quedó liberado. Recibirás la confirmación como notificación.',
        acciones: [
          _BotonDialogo(
            texto: 'Reprogramar ahora',
            icono: Icons.event_repeat_rounded,
            primario: true,
            onTap: () {
              Navigator.pop(ctx);
              _agendarCita();
            },
          ),
          _BotonDialogo(texto: 'Listo', onTap: () => Navigator.pop(ctx)),
        ],
      ),
    );
  }

  void mostrarAvisoPoliticaCita(CitaMovil c) => mostrarAvisoPolitica24h(c);

  /// CU11-paso 19: mostrar_aviso_politica_24h('Cancelación rechazada por política 24h') [retorno al Paciente] — criterio (b)
  void mostrarAvisoPolitica24h(CitaMovil c, {String? mensajeServidor}) {
    showDialog(
      context: context,
      builder: (ctx) => _DialogoBase(
        icono: Icons.schedule_rounded,
        color: AppTheme.warning,
        titulo: 'Cancelación no disponible',
        texto: 'La política del centro permite cancelar o reprogramar desde la app solo con más de '
            '$_politicaHoras horas de anticipación. Para esta cita comunícate con Recepción'
            '${_centro.isNotEmpty ? ' de $_centro' : ''}.',
        detalle: mensajeServidor,
        acciones: [
          _BotonDialogo(
            texto: 'Contactar por WhatsApp a Recepción',
            icono: Icons.chat_rounded,
            primario: true,
            colorPrimario: const Color(0xFF25D366),
            onTap: () {
              Navigator.pop(ctx);
              _abrirWhatsApp(c);
            },
          ),
          _BotonDialogo(texto: 'Entendido', onTap: () => Navigator.pop(ctx)),
        ],
      ),
    );
  }

  Future<void> _abrirWhatsApp(CitaMovil c) async {
    final texto = Uri.encodeComponent(
        'Hola, necesito cancelar o reprogramar mi cita con ${c.psicologo} del ${_fechaCorta(c)} a las ${c.horaInicio}.');
    final uri = Uri.parse('https://wa.me/$_whatsapp?text=$texto');
    final ok = _whatsapp.isNotEmpty && await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!ok && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        behavior: SnackBarBehavior.floating,
        content: Text('No se pudo abrir WhatsApp. Llama a Recepción: ${_telefono.isEmpty ? 'sin teléfono' : _telefono}'),
      ));
    }
  }

  // ───────────────────────────── UI ─────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Mis Citas', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 19)),
        actions: [
          IconButton(
            tooltip: 'Actualizar',
            onPressed: abrirAgendaMovil,
            icon: const Icon(Icons.refresh_rounded, color: AppTheme.primaryLight),
          ),
          const SizedBox(width: 4),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(62),
          child: _segmentos(),
        ),
      ),
      body: _cargando
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryLight))
          : _error != null
              ? _errorView()
              : TabBarView(
                  controller: _tabs,
                  children: [mostrarCitasPorEstado(_proximas, true), mostrarCitasPorEstado(_historial, false)],
                ),
      floatingActionButton: _proximas.isEmpty || _cargando
          ? null
          : FloatingActionButton.extended(
              onPressed: _agendarCita,
              backgroundColor: AppTheme.primary,
              foregroundColor: Colors.white,
              icon: const Icon(Icons.add_rounded),
              label: const Text('Agendar cita', style: TextStyle(fontWeight: FontWeight.w800)),
            ),
    );
  }

  Widget _segmentos() {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 4, 16, 12),
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: AppTheme.inputBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderSubtle),
      ),
      child: TabBar(
        controller: _tabs,
        dividerColor: Colors.transparent,
        indicatorSize: TabBarIndicatorSize.tab,
        indicator: BoxDecoration(gradient: AppTheme.primaryGradient, borderRadius: BorderRadius.circular(12)),
        labelColor: Colors.white,
        unselectedLabelColor: AppTheme.textMuted,
        labelStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13.5),
        tabs: [
          Tab(height: 40, text: 'Próximas (${_proximas.length})'),
          Tab(height: 40, text: 'Historial (${_historial.length})'),
        ],
      ),
    );
  }

  /// mostrar_citas_por_estado()
  Widget mostrarCitasPorEstado(List<CitaMovil> citas, bool proximas) {
    if (citas.isEmpty) return proximas ? _vacioProximas() : _vacioHistorial();
    return RefreshIndicator(
      color: AppTheme.primary,
      onRefresh: abrirAgendaMovil,
      child: ListView.builder(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
        itemCount: citas.length + (proximas ? 1 : 0),
        itemBuilder: (_, i) {
          if (proximas && i == 0) return _avisoPolitica();
          final c = citas[proximas ? i - 1 : i];
          return _CitaCard(
            cita: c,
            proxima: proximas,
            onEntrar: () => _entrarTeleconsulta(c),
            onCancelar: () => presionarCancelarCita(c),
          );
        },
      ),
    );
  }

  Widget _avisoPolitica() => Container(
        margin: const EdgeInsets.only(bottom: 14),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: AppTheme.info.withOpacity(0.08),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppTheme.info.withOpacity(0.22)),
        ),
        child: Row(
          children: [
            const Icon(Icons.info_outline_rounded, size: 18, color: AppTheme.info),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                'Puedes cancelar desde la app hasta $_politicaHoras h antes de tu cita.',
                style: const TextStyle(color: AppTheme.textMuted, fontSize: 12.5),
              ),
            ),
          ],
        ),
      );

  // Criterio (b) HU-41: ilustración amigable + acción rápida para agendar
  Widget _vacioProximas() => RefreshIndicator(
        color: AppTheme.primary,
        onRefresh: abrirAgendaMovil,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(28, 60, 28, 40),
          children: [
            Center(
              child: SizedBox(
                width: 170,
                height: 150,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    Container(
                      width: 150,
                      height: 150,
                      decoration: BoxDecoration(shape: BoxShape.circle, color: AppTheme.primary.withOpacity(0.10)),
                    ),
                    Container(
                      width: 104,
                      height: 104,
                      decoration: BoxDecoration(shape: BoxShape.circle, color: AppTheme.primary.withOpacity(0.18)),
                    ),
                    Container(
                      width: 70,
                      height: 70,
                      decoration: BoxDecoration(
                        gradient: AppTheme.primaryGradient,
                        borderRadius: BorderRadius.circular(22),
                        boxShadow: const [BoxShadow(color: AppTheme.glowMint, blurRadius: 24)],
                      ),
                      child: const Icon(Icons.calendar_month_rounded, color: Colors.white, size: 36),
                    ),
                    Positioned(
                      top: 14,
                      right: 18,
                      child: _burbuja(Icons.favorite_rounded, AppTheme.danger),
                    ),
                    Positioned(
                      bottom: 16,
                      left: 14,
                      child: _burbuja(Icons.psychology_alt_rounded, AppTheme.info),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 26),
            const Text('Aún no tienes citas próximas',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 19, fontWeight: FontWeight.w800, color: AppTheme.textMain)),
            const SizedBox(height: 8),
            const Text(
              'Cuidar tu bienestar empieza con un paso. Agenda una sesión con uno de nuestros profesionales.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13.5, height: 1.45, color: AppTheme.textMuted),
            ),
            const SizedBox(height: 26),
            SizedBox(
              height: 52,
              child: ElevatedButton.icon(
                onPressed: _agendarCita,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primary,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                ),
                icon: const Icon(Icons.add_circle_outline_rounded),
                label: const Text('Agendar una cita', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 15)),
              ),
            ),
          ],
        ),
      );

  Widget _burbuja(IconData i, Color c) => Container(
        width: 34,
        height: 34,
        decoration: BoxDecoration(
          color: AppTheme.cardBgElevated,
          shape: BoxShape.circle,
          border: Border.all(color: c.withOpacity(0.5)),
        ),
        child: Icon(i, size: 17, color: c),
      );

  Widget _vacioHistorial() => ListView(
        padding: const EdgeInsets.fromLTRB(28, 90, 28, 40),
        children: const [
          Icon(Icons.history_rounded, size: 54, color: AppTheme.textSubtle),
          SizedBox(height: 14),
          Text('Sin sesiones anteriores',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textMain)),
          SizedBox(height: 6),
          Text('Aquí verás tus sesiones realizadas, canceladas o no asistidas.',
              textAlign: TextAlign.center, style: TextStyle(color: AppTheme.textMuted, fontSize: 13)),
        ],
      );

  Widget _errorView() => Center(
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.wifi_off_rounded, size: 46, color: AppTheme.textSubtle),
              const SizedBox(height: 12),
              Text(_error ?? '', textAlign: TextAlign.center, style: const TextStyle(color: AppTheme.textMuted)),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: abrirAgendaMovil,
                icon: const Icon(Icons.refresh_rounded),
                label: const Text('Reintentar'),
              ),
            ],
          ),
        ),
      );
}

String _fechaCorta(CitaMovil c) {
  final f = c.fechaDt;
  return f == null ? c.fecha : DateFormat('dd/MM/yyyy').format(f);
}

// ─────────────────────────────── Tarjeta de cita ───────────────────────────────

class _CitaCard extends StatelessWidget {
  final CitaMovil cita;
  final bool proxima;
  final VoidCallback onEntrar;
  final VoidCallback onCancelar;
  const _CitaCard({required this.cita, required this.proxima, required this.onEntrar, required this.onCancelar});

  static Color colorEstado(String e) {
    switch (e) {
      case 'CONFIRMADA':
        return AppTheme.success;
      case 'PENDIENTE':
        return AppTheme.warning;
      case 'CANCELADA':
        return AppTheme.danger;
      case 'INASISTENCIA':
        return const Color(0xFFFB923C);
      default:
        return AppTheme.textMuted; // REALIZADA
    }
  }

  String _cuando() {
    final m = cita.minutosParaInicio;
    if (m <= 0) return 'En curso';
    if (m < 60) return 'Comienza en $m min';
    if (m < 24 * 60) return 'En ${m ~/ 60} h ${m % 60} min';
    final d = (m / (24 * 60)).floor();
    return d == 1 ? 'Mañana' : 'En $d días';
  }

  @override
  Widget build(BuildContext context) {
    final c = cita;
    final destacada = proxima && c.puedeEntrar; // HU-41 (c)
    final f = c.fechaDt;
    final cEstado = colorEstado(c.estadoEtiqueta);

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: destacada ? const Color(0xFF143F35) : AppTheme.cardBg,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: destacada ? AppTheme.primaryLight : AppTheme.borderSubtle, width: destacada ? 1.8 : 1),
        boxShadow: [
          BoxShadow(
            color: destacada ? AppTheme.glowMint : Colors.black.withOpacity(0.22),
            blurRadius: destacada ? 22 : 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (destacada)
              Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: AppTheme.primaryLight.withOpacity(0.16),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.circle, size: 9, color: AppTheme.primaryLight),
                    const SizedBox(width: 7),
                    Text(c.minutosParaInicio > 0 ? 'Tu sesión comienza en ${c.minutosParaInicio} min' : 'Tu sesión está en curso',
                        style: const TextStyle(color: AppTheme.primaryLight, fontWeight: FontWeight.w800, fontSize: 12.5)),
                  ],
                ),
              ),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Bloque de fecha
                Container(
                  width: 60,
                  padding: const EdgeInsets.symmetric(vertical: 9),
                  decoration: BoxDecoration(
                    color: proxima ? AppTheme.primary.withOpacity(0.22) : AppTheme.cardBgElevated,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: proxima ? AppTheme.primary.withOpacity(0.5) : AppTheme.borderSubtle),
                  ),
                  child: Column(
                    children: [
                      Text(f == null ? '' : DateFormat('MMM', 'es').format(f).toUpperCase().replaceAll('.', ''),
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.primaryLight)),
                      Text(f == null ? '--' : '${f.day}',
                          style: const TextStyle(fontSize: 24, height: 1.1, fontWeight: FontWeight.w900, color: AppTheme.textMain)),
                      Text(f == null ? '' : DateFormat('EEE', 'es').format(f).replaceAll('.', ''),
                          style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          _Avatar(iniciales: c.iniciales, foto: c.foto),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(c.psicologo,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(fontSize: 14.5, fontWeight: FontWeight.w800, color: AppTheme.textMain)),
                                Text(c.especialidad,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        children: [
                          _Tag(texto: c.estadoEtiqueta, color: cEstado),
                          _Tag(
                            texto: c.esVirtual ? 'VIRTUAL' : 'PRESENCIAL',
                            color: c.esVirtual ? AppTheme.info : AppTheme.primaryLight,
                            icono: c.esVirtual ? Icons.videocam_rounded : Icons.apartment_rounded,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _Linea(
              icono: Icons.schedule_rounded,
              texto: '${c.horaInicio} – ${c.horaFin}',
              extra: proxima ? _cuando() : null,
            ),
            const SizedBox(height: 6),
            _Linea(
              icono: c.esVirtual ? Icons.link_rounded : Icons.place_rounded,
              texto: c.esVirtual
                  ? (c.enlaceVirtual.isNotEmpty ? 'Sala virtual: ${c.enlaceVirtual}' : 'Enlace virtual se habilita antes de la sesión')
                  : (c.consultorio.isNotEmpty ? 'Consultorio: ${c.consultorio}' : 'Consultorio del centro'),
            ),
            if (c.estado == 'CANCELADA' && c.motivoCancelacion.isNotEmpty) ...[
              const SizedBox(height: 10),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppTheme.danger.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppTheme.danger.withOpacity(0.2)),
                ),
                child: Text('Motivo de cancelación: ${c.motivoCancelacion}',
                    style: const TextStyle(fontSize: 12, color: Color(0xFFFDA4AF))),
              ),
            ],
            if (proxima) ...[
              const SizedBox(height: 14),
              Row(
                children: [
                  if (c.esVirtual) ...[
                    Expanded(
                      child: SizedBox(
                        height: 46,
                        child: ElevatedButton.icon(
                          onPressed: c.puedeEntrar ? onEntrar : null,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppTheme.primaryLight,
                            foregroundColor: const Color(0xFF06231A),
                            disabledBackgroundColor: AppTheme.cardBgElevated,
                            disabledForegroundColor: AppTheme.textSubtle,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                          icon: Icon(c.puedeEntrar ? Icons.videocam_rounded : Icons.lock_clock_rounded, size: 18),
                          label: Text(
                            c.puedeEntrar ? 'Entrar a Teleconsulta' : 'Abre 10 min antes',
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 12.5),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                  ],
                  _anchoBoton(
                    expandir: !c.esVirtual,
                    child: SizedBox(
                      height: 46,
                      child: OutlinedButton.icon(
                        // Criterio (b) HU-42: deshabilitado visualmente; al tocar muestra la política
                        onPressed: onCancelar,
                        style: OutlinedButton.styleFrom(
                          foregroundColor: c.puedeCancelar ? AppTheme.danger : AppTheme.textSubtle,
                          backgroundColor: c.puedeCancelar ? Colors.transparent : AppTheme.cardBgElevated.withOpacity(0.6),
                          side: BorderSide(
                              color: c.puedeCancelar ? AppTheme.danger.withOpacity(0.5) : AppTheme.borderSubtle),
                          padding: const EdgeInsets.symmetric(horizontal: 14),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                        ),
                        icon: Icon(c.puedeCancelar ? Icons.event_busy_rounded : Icons.lock_rounded, size: 17),
                        label: Text(
                          c.puedeCancelar ? 'Cancelar' : (c.esVirtual ? '< 24 h' : 'Cancelación no disponible (< 24 h)'),
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 12.5),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

Widget _anchoBoton({required bool expandir, required Widget child}) => expandir ? Expanded(child: child) : child;

class _Avatar extends StatelessWidget {
  final String iniciales;
  final String? foto;
  const _Avatar({required this.iniciales, this.foto});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 38,
      height: 38,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: AppTheme.coldGradient,
        border: Border.all(color: Colors.white.withOpacity(0.25), width: 1.5),
        image: (foto != null && foto!.isNotEmpty) ? DecorationImage(image: NetworkImage(foto!), fit: BoxFit.cover) : null,
      ),
      alignment: Alignment.center,
      child: (foto != null && foto!.isNotEmpty)
          ? null
          : Text(iniciales, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 13)),
    );
  }
}

class _Tag extends StatelessWidget {
  final String texto;
  final Color color;
  final IconData? icono;
  const _Tag({required this.texto, required this.color, this.icono});

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: color.withOpacity(0.14),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.35)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icono != null) ...[Icon(icono, size: 12, color: color), const SizedBox(width: 4)],
            Text(texto, style: TextStyle(fontSize: 10.5, fontWeight: FontWeight.w900, color: color, letterSpacing: 0.4)),
          ],
        ),
      );
}

class _Linea extends StatelessWidget {
  final IconData icono;
  final String texto;
  final String? extra;
  const _Linea({required this.icono, required this.texto, this.extra});

  @override
  Widget build(BuildContext context) => Row(
        children: [
          Icon(icono, size: 16, color: AppTheme.textSubtle),
          const SizedBox(width: 8),
          Expanded(
            child: Text(texto,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 13, color: AppTheme.textMain, fontWeight: FontWeight.w600)),
          ),
          if (extra != null)
            Text(extra!, style: const TextStyle(fontSize: 12, color: AppTheme.primaryLight, fontWeight: FontWeight.w700)),
        ],
      );
}

// ─────────────── Modal "Confirmar Cancelación de Cita" (Figma HU-42) ───────────────

class _ConfirmarCancelacionSheet extends StatefulWidget {
  final CitaMovil cita;
  const _ConfirmarCancelacionSheet({required this.cita});

  @override
  State<_ConfirmarCancelacionSheet> createState() => _ConfirmarCancelacionSheetState();
}

class _ConfirmarCancelacionSheetState extends State<_ConfirmarCancelacionSheet> {
  final _ctrl = TextEditingController();
  String? _error;
  static const _rapidos = ['Imprevisto laboral', 'Motivos de salud', 'Viaje', 'Problema de transporte'];

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  void _confirmar() {
    final m = _ctrl.text.trim();
    if (m.length < 5) {
      setState(() => _error = 'Escribe un motivo (mínimo 5 caracteres).');
      return;
    }
    Navigator.pop(context, m);
  }

  @override
  Widget build(BuildContext context) {
    final c = widget.cita;
    return Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: Container(
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 22),
        decoration: const BoxDecoration(
          color: AppTheme.cardBg,
          borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
          border: Border(top: BorderSide(color: AppTheme.borderSubtle)),
        ),
        child: SafeArea(
          top: false,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(width: 42, height: 5, decoration: BoxDecoration(color: AppTheme.textSubtle, borderRadius: BorderRadius.circular(4))),
              const SizedBox(height: 18),
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(color: AppTheme.danger.withOpacity(0.14), shape: BoxShape.circle),
                child: const Icon(Icons.priority_high_rounded, color: AppTheme.danger, size: 32),
              ),
              const SizedBox(height: 14),
              const Text('Confirmar Cancelación de Cita',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppTheme.textMain)),
              const SizedBox(height: 8),
              Text(
                'Lamentamos que no puedas asistir. Tu sesión con ${c.psicologo} del ${_fechaCorta(c)} a las ${c.horaInicio} '
                'será cancelada y el horario quedará libre para otro paciente.',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 13, height: 1.45, color: AppTheme.textMuted),
              ),
              const SizedBox(height: 16),
              Align(
                alignment: Alignment.centerLeft,
                child: Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: _rapidos
                      .map((t) => ActionChip(
                            label: Text(t, style: const TextStyle(fontSize: 12, color: AppTheme.textMain)),
                            backgroundColor: AppTheme.cardBgElevated,
                            side: const BorderSide(color: AppTheme.borderSubtle),
                            onPressed: () => setState(() {
                              _ctrl.text = t;
                              _error = null;
                            }),
                          ))
                      .toList(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _ctrl,
                maxLines: 2,
                maxLength: 300,
                onChanged: (_) => setState(() => _error = null),
                decoration: InputDecoration(
                  labelText: 'Motivo de la cancelación *',
                  hintText: 'Cuéntanos brevemente por qué no podrás asistir',
                  errorText: _error,
                ),
              ),
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _confirmar,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.danger,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  child: const Text('Confirmar cancelación', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 15)),
                ),
              ),
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                height: 46,
                child: TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Mantener mi cita', style: TextStyle(color: AppTheme.textMuted, fontWeight: FontWeight.w700)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────── Diálogos ───────────────────────────────

class _BotonDialogo {
  final String texto;
  final IconData? icono;
  final bool primario;
  final Color? colorPrimario;
  final VoidCallback onTap;
  _BotonDialogo({required this.texto, required this.onTap, this.icono, this.primario = false, this.colorPrimario});
}

class _DialogoBase extends StatelessWidget {
  final IconData icono;
  final Color color;
  final String titulo;
  final String texto;
  final String? detalle;
  final List<_BotonDialogo> acciones;
  const _DialogoBase({
    required this.icono,
    required this.color,
    required this.titulo,
    required this.texto,
    required this.acciones,
    this.detalle,
  });

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: AppTheme.cardBg,
      insetPadding: const EdgeInsets.symmetric(horizontal: 24),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24), side: const BorderSide(color: AppTheme.borderSubtle)),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(22, 26, 22, 18),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 62,
              height: 62,
              decoration: BoxDecoration(color: color.withOpacity(0.15), shape: BoxShape.circle),
              child: Icon(icono, color: color, size: 34),
            ),
            const SizedBox(height: 14),
            Text(titulo,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppTheme.textMain)),
            const SizedBox(height: 8),
            Text(texto,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 13.5, height: 1.45, color: AppTheme.textMuted)),
            if (detalle != null && detalle!.isNotEmpty) ...[
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(10)),
                child: Text(detalle!, textAlign: TextAlign.center, style: TextStyle(fontSize: 11.5, color: color, fontWeight: FontWeight.w700)),
              ),
            ],
            const SizedBox(height: 20),
            ...acciones.map((a) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: SizedBox(
                    width: double.infinity,
                    child: a.primario
                        ? ElevatedButton.icon(
                            onPressed: a.onTap,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: a.colorPrimario ?? AppTheme.primary,
                              foregroundColor: Colors.white,
                              minimumSize: const Size.fromHeight(48),
                              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            ),
                            icon: Icon(a.icono ?? Icons.check_rounded, size: 19),
                            label: Text(a.texto,
                                textAlign: TextAlign.center,
                                style: const TextStyle(fontWeight: FontWeight.w800, height: 1.25)),
                          )
                        : TextButton(
                            onPressed: a.onTap,
                            style: TextButton.styleFrom(minimumSize: const Size.fromHeight(46)),
                            child: Text(a.texto, style: const TextStyle(color: AppTheme.textMuted, fontWeight: FontWeight.w700)),
                          ),
                  ),
                )),
          ],
        ),
      ),
    );
  }
}
