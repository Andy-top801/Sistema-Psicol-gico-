// ==============================================================================
// MÓDULO: mis_citas_screen.dart
// CAPA BCE: BOUNDARY (Interfaz de Usuario Móvil) — IU_AgendaCitas
// CASOS DE USO: CU11: Programación, Reserva y Gestión de Citas (HU-15, HU-16, HU-17)
// DESCRIPCIÓN: Pantalla móvil Flutter para visualización de citas activas e historial,
//              acceso directo a teleconsultas virtuales y cancelación con anticipación.
//              Implementa los pasos del flujo principal y alternativo del Diagrama BCE.
// ==============================================================================
import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../services/agenda_service.dart';
import '../models/cita_model.dart';
import '../core/theme/app_theme.dart';
import 'reservar_cita_screen.dart';
import 'teleconsulta_jitsi_screen.dart';

class MisCitasScreen extends StatefulWidget {
  final AuthService authService;

  const MisCitasScreen({super.key, required this.authService});

  @override
  State<MisCitasScreen> createState() => _MisCitasScreenState();
}

class _MisCitasScreenState extends State<MisCitasScreen> with SingleTickerProviderStateMixin {
  late final AgendaService _agendaService;
  late final TabController _tabController;

  bool _isLoading = true;
  List<CitaModel> _todasLasCitas = [];

  @override
  void initState() {
    super.initState();
    _agendaService = AgendaService(authService: widget.authService);
    _tabController = TabController(length: 2, vsync: this);
    _cargarCitas();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _cargarCitas() async {
    setState(() => _isLoading = true);
    final citas = await _agendaService.getCitas();
    setState(() {
      _todasLasCitas = citas;
      _isLoading = false;
    });
  }

  List<CitaModel> get _citasProximas {
    return _todasLasCitas.where((c) => c.isActiva).toList();
  }

  List<CitaModel> get _citasHistorial {
    return _todasLasCitas.where((c) => !c.isActiva).toList();
  }

  void _abrirReservaCita() async {
    final res = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ReservarCitaScreen(authService: widget.authService),
      ),
    );

    if (res == true) {
      _cargarCitas();
    }
  }

  void _abrirTeleconsulta(CitaModel cita) async {
    final res = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => TeleconsultaJitsiScreen(
          authService: widget.authService,
          cita: cita,
        ),
      ),
    );

    if (res == true) {
      _cargarCitas();
    }
  }

  void _abrirTeleconsultaDemo() {
    final demoCita = CitaModel(
      id: 'demo-teleconsulta',
      pacienteId: widget.authService.currentUser?.id ?? '1',
      pacienteNombre: widget.authService.currentUser?.nombre ?? 'Paciente',
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
    _abrirTeleconsulta(demoCita);
  }

  void _confirmarCancelarCita(CitaModel cita) {
    final motivoCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardBg,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.cancel_outlined, color: AppTheme.danger, size: 22),
            SizedBox(width: 8),
            Text('Cancelar Cita', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '¿Deseas cancelar la cita con ${cita.psicologoNombre.isNotEmpty ? cita.psicologoNombre : "el terapeuta"} programada para el ${cita.fecha}?',
              style: const TextStyle(color: AppTheme.textMuted, fontSize: 13),
            ),
            const SizedBox(height: 14),
            TextField(
              controller: motivoCtrl,
              maxLines: 2,
              decoration: const InputDecoration(
                labelText: 'Motivo de cancelación *',
                hintText: 'Ej: Motivos personales, cambio de horario...',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Volver', style: TextStyle(color: AppTheme.textMuted)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.danger),
            onPressed: () async {
              if (motivoCtrl.text.trim().isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    backgroundColor: AppTheme.danger,
                    content: Text('Por favor especifica el motivo de la cancelación.'),
                  ),
                );
                return;
              }
              Navigator.pop(ctx);
              await _cancelarCita(cita.id, motivoCtrl.text.trim());
            },
            child: const Text('Confirmar Cancelación'),
          ),
        ],
      ),
    );
  }

  /// CU11 – Cancelación de Cita con Anticipación (HU-17)
  ///   Paso 1: Actor ingresa motivo en diálogo de cancelación
  ///   Paso 2: POST /api/agenda/citas/{id}/cancelar/
  ///   (Pasos 3-6: CTR valida 2h mínimas de anticipación y libera slot en base de datos)
  ///   Paso 7: 200 OK con confirmación de cita cancelada
  ///   Paso 8: Mostrar notificación de éxito y refrescar listado
  Future<void> _cancelarCita(String citaId, String motivo) async {
    // --- Paso 2: POST /api/agenda/citas/{id}/cancelar/ > ---
    final res = await _agendaService.cancelarCita(citaId, motivo);
    if (mounted) {
      // --- Paso 7: 200 OK < ---
      if (res['success'] == true) {
        // --- Paso 8: Notificar confirmación de cancelación en pantalla móvil < ---
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            backgroundColor: AppTheme.success,
            content: Text('La cita ha sido cancelada exitosamente.'),
          ),
        );
        _cargarCitas();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: AppTheme.danger,
            content: Text(res['error'] ?? 'Error al cancelar la cita.'),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Mis Citas y Agenda', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Actualizar citas',
            onPressed: _cargarCitas,
          ),
          const SizedBox(width: 8),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppTheme.primary,
          indicatorWeight: 3,
          labelColor: AppTheme.primaryLight,
          unselectedLabelColor: AppTheme.textMuted,
          labelStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13),
          tabs: [
            Tab(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.event_available_rounded, size: 16),
                  const SizedBox(width: 6),
                  Text('Próximas (${_citasProximas.length})'),
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.history_rounded, size: 16),
                  const SizedBox(width: 6),
                  Text('Historial (${_citasHistorial.length})'),
                ],
              ),
            ),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildCitasList(_citasProximas, esProximas: true),
                _buildCitasList(_citasHistorial, esProximas: false),
              ],
            ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add_rounded),
        label: const Text('Agendar Cita', style: TextStyle(fontWeight: FontWeight.bold)),
        onPressed: _abrirReservaCita,
      ),
    );
  }

  Widget _buildCitasList(List<CitaModel> citas, {required bool esProximas}) {
    if (citas.isEmpty) {
      return RefreshIndicator(
        onRefresh: _cargarCitas,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Container(
            height: MediaQuery.of(context).size.height * 0.65,
            alignment: Alignment.center,
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppTheme.primary.withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    esProximas ? Icons.event_note_outlined : Icons.history_outlined,
                    size: 48,
                    color: AppTheme.primaryLight,
                  ),
                ),
                const SizedBox(height: 18),
                Text(
                  esProximas ? 'No tienes citas programadas' : 'No hay historial de citas',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                ),
                const SizedBox(height: 6),
                Text(
                  esProximas
                      ? 'Agenda tu próxima sesión de terapia con nuestros profesionales.'
                      : 'Aquí aparecerán las citas realizadas o canceladas.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: AppTheme.textMuted, fontSize: 12),
                ),
                if (esProximas) ...[
                  const SizedBox(height: 20),
                  ElevatedButton.icon(
                    onPressed: _abrirReservaCita,
                    icon: const Icon(Icons.calendar_month_rounded),
                    label: const Text('Reservar Ahora'),
                  ),
                  const SizedBox(height: 10),
                  OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppTheme.secondary,
                      side: const BorderSide(color: AppTheme.secondary),
                    ),
                    onPressed: _abrirTeleconsultaDemo,
                    icon: const Icon(Icons.videocam_rounded),
                    label: const Text('Probar Videollamada / Teleconsulta'),
                  ),
                ],
              ],
            ),
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _cargarCitas,
      child: ListView.builder(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 80),
        itemCount: citas.length,
        itemBuilder: (context, index) {
          final cita = citas[index];
          return _buildCitaCard(cita, esProximas: esProximas);
        },
      ),
    );
  }

  Widget _buildCitaCard(CitaModel cita, {required bool esProximas}) {
    Color estadoColor = AppTheme.primary;
    switch (cita.estado.toUpperCase()) {
      case 'CONFIRMADA':
        estadoColor = AppTheme.success;
        break;
      case 'REALIZADA':
        estadoColor = AppTheme.textMuted;
        break;
      case 'CANCELADA':
        estadoColor = AppTheme.danger;
        break;
      case 'INASISTENCIA':
        estadoColor = AppTheme.warning;
        break;
      default:
        estadoColor = AppTheme.primary;
    }

    final isTeleconsultaHabilitada = cita.isTeleconsultaReady;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: isTeleconsultaHabilitada ? AppTheme.secondary.withOpacity(0.6) : AppTheme.borderSubtle,
          width: isTeleconsultaHabilitada ? 1.8 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: isTeleconsultaHabilitada
                ? AppTheme.secondary.withOpacity(0.15)
                : Colors.black.withOpacity(0.25),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header: Modalidad y Estado
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Modalidad Badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: cita.isVirtual
                        ? AppTheme.secondary.withOpacity(0.2)
                        : AppTheme.primary.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        cita.isVirtual ? Icons.videocam_outlined : Icons.apartment_rounded,
                        size: 13,
                        color: cita.isVirtual ? const Color(0xFFA5B4FC) : AppTheme.primaryLight,
                      ),
                      const SizedBox(width: 5),
                      Text(
                        cita.isVirtual ? 'TELECONSULTA' : 'PRESENCIAL',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w800,
                          color: cita.isVirtual ? const Color(0xFFA5B4FC) : AppTheme.primaryLight,
                        ),
                      ),
                    ],
                  ),
                ),
                // Estado Badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: estadoColor.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: estadoColor.withOpacity(0.3)),
                  ),
                  child: Text(
                    cita.estado.toUpperCase(),
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: estadoColor),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Terapeuta y Fecha
            Row(
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    gradient: AppTheme.primaryGradient,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.psychology_outlined, color: Colors.white, size: 24),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        cita.psicologoNombre.isNotEmpty ? cita.psicologoNombre : 'Psicólogo Asignado',
                        style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: AppTheme.textMain),
                      ),
                      const SizedBox(height: 2),
                      Row(
                        children: [
                          const Icon(Icons.calendar_today_rounded, size: 12, color: AppTheme.textSubtle),
                          const SizedBox(width: 4),
                          Text(
                            cita.fecha,
                            style: const TextStyle(color: AppTheme.textMuted, fontSize: 12),
                          ),
                          const SizedBox(width: 10),
                          const Icon(Icons.access_time_rounded, size: 12, color: AppTheme.textSubtle),
                          const SizedBox(width: 4),
                          Text(
                            '${cita.horaInicioCorta} - ${cita.horaFinCorta}',
                            style: const TextStyle(color: AppTheme.textMuted, fontSize: 12, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Motivo y Costo
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: AppTheme.inputBg,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Motivo de Consulta', style: TextStyle(fontSize: 10, color: AppTheme.textSubtle)),
                        const SizedBox(height: 2),
                        Text(
                          cita.motivoConsulta.isNotEmpty ? cita.motivoConsulta : 'Consulta general',
                          style: const TextStyle(fontSize: 12, color: AppTheme.textMain),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 10),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      const Text('Tarifa', style: TextStyle(fontSize: 10, color: AppTheme.textSubtle)),
                      const SizedBox(height: 2),
                      Text(
                        'Bs. ${cita.costo.toStringAsFixed(2)}',
                        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.success),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            if (cita.motivoCancelacion != null && cita.motivoCancelacion!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                'Cancelada: ${cita.motivoCancelacion}',
                style: const TextStyle(fontSize: 11, color: AppTheme.danger, fontStyle: FontStyle.italic),
              ),
            ],

            // Botones de Acción para citas activas
            if (esProximas) ...[
              const SizedBox(height: 14),
              Row(
                children: [
                  // Botón Unirse a Teleconsulta / Videollamada (HU-19)
                  Expanded(
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: cita.isVirtual ? AppTheme.secondary : const Color(0xFF6366F1),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 11),
                      ),
                      onPressed: () => _abrirTeleconsulta(cita),
                      icon: const Icon(
                        Icons.videocam_rounded,
                        size: 18,
                        color: Colors.white,
                      ),
                      label: Text(
                        cita.isVirtual ? 'UNIRSE A TELECONSULTA' : 'VIDEOCONSULTA EN VIVO',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),

                  // Botón Cancelar Cita
                  OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppTheme.danger,
                      side: BorderSide(color: AppTheme.danger.withOpacity(0.4)),
                      padding: const EdgeInsets.symmetric(vertical: 11, horizontal: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    ),
                    onPressed: () => _confirmarCancelarCita(cita),
                    icon: const Icon(Icons.close_rounded, size: 16),
                    label: const Text('Cancelar', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
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
