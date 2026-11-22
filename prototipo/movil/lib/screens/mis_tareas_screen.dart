// ==============================================================================
// MÓDULO: mis_tareas_screen.dart
// CAPA BCE: BOUNDARY (Interfaz de Usuario Móvil – Flutter) — IU_GestionTareas
// CASO DE USO: CU17 Móvil – Tareas Terapéuticas y Mood Tracker Diario (HU-45, HU-46)
//
// DIAGRAMA DE SECUENCIA "Secuencia_Corregido_CU17_Tareas_Mood_Movil":
//   1 : Paciente → IU_SeguimientoTerapeuticoMovil.entregar_tarea_y_animo(tarea_id, reflexión, dificultad, ánimo)
//   2 : IU → CTR  POST /api/clinica/tareas/{id}/entregar/
//   3-6 : CTR valida plazo/archivo y actualiza estado → 'COMPLETADA' (se muestra 'Entregada')
//   alt [plazo_valido && archivo_valido]
//     7-16 : persistir_evidencia · obtener_paciente · registrar_animo · supervisar_avance · registrar_acceso
//     17-18: 200 OK → mostrar_entrega_exito('Tarea entregada y ánimo registrado')
//   else
//     19-20: 400 Bad Request → mostrar_error_entrega('No se puede entregar la tarea fuera de plazo')
// HU-45 (a) etiqueta 'Pendiente' + fecha límite · (b) 'Completar Tarea' abre reflexión + dificultad 1-5
//       (c) estado 'Entregada', edición bloqueada; el psicólogo la ve en la historia clínica web.
// ==============================================================================
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../core/theme/app_theme.dart';
import '../services/auth_service.dart';
import '../services/sprint2_service.dart';
import 'mood_tracker_sheet.dart';

class MisTareasScreen extends StatefulWidget {
  final AuthService authService;

  const MisTareasScreen({super.key, required this.authService});

  @override
  State<MisTareasScreen> createState() => _MisTareasScreenState();
}

class _MisTareasScreenState extends State<MisTareasScreen> with TickerProviderStateMixin {
  late final Sprint2Service _sprint2Service;
  late final AnimationController _fadeController;
  late final Animation<double> _fadeAnimation;

  List<Map<String, dynamic>> _tareas = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _sprint2Service = Sprint2Service(authService: widget.authService);
    _fadeController = AnimationController(vsync: this, duration: const Duration(milliseconds: 500));
    _fadeAnimation = CurvedAnimation(parent: _fadeController, curve: Curves.easeOut);
    _loadTareas();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    super.dispose();
  }

  Future<void> _loadTareas() async {
    final tareas = await _sprint2Service.getMisTareas();
    if (mounted) {
      setState(() {
        _tareas = tareas;
        _isLoading = false;
      });
      _fadeController.forward();
    }
  }

  int get _completadas => _tareas.where((t) {
    final st = (t['estado'] ?? '').toString().toUpperCase();
    return st == 'COMPLETADA' || st == 'COMPLETADA_CON_RETRASO';
  }).length;
  int get _total => _tareas.length;
  double get _porcentaje => _total > 0 ? _completadas / _total : 0;

  Color _getEstadoColor(String estado) {
    switch (estado.toUpperCase()) {
      case 'COMPLETADA': return AppTheme.success;
      case 'COMPLETADA_CON_RETRASO': return const Color(0xFFF97316);
      case 'PENDIENTE': return AppTheme.warning;
      case 'EN_PROGRESO': return AppTheme.primary;
      case 'VENCIDA': return AppTheme.danger;
      default: return AppTheme.textSubtle;
    }
  }

  String _getEstadoLabel(String estado) {
    switch (estado.toUpperCase()) {
      case 'COMPLETADA': return 'Entregada';
      case 'COMPLETADA_CON_RETRASO': return 'Entregada con retraso';
      case 'PENDIENTE': return 'Pendiente';
      case 'EN_PROGRESO': return 'En Progreso';
      case 'VENCIDA': return 'Vencida';
      default: return estado;
    }
  }


  IconData _getCategoriaIcon(String? categoria) {
    switch ((categoria ?? '').toUpperCase()) {
      case 'CONDUCTUAL': return Icons.directions_walk_rounded;
      case 'COGNITIVA': return Icons.psychology_rounded;
      case 'MINDFULNESS': return Icons.self_improvement_rounded;
      case 'ESCRITURA': return Icons.edit_note_rounded;
      default: return Icons.assignment_rounded;
    }
  }

  Color _getCategoriaColor(String? categoria) {
    switch ((categoria ?? '').toUpperCase()) {
      case 'CONDUCTUAL': return const Color(0xFF10B981);
      case 'COGNITIVA': return const Color(0xFF6366F1);
      case 'MINDFULNESS': return const Color(0xFF8B5CF6);
      case 'ESCRITURA': return const Color(0xFFF59E0B);
      default: return AppTheme.primary;
    }
  }

  bool _estaEntregada(String estado) => estado == 'COMPLETADA' || estado == 'COMPLETADA_CON_RETRASO';

  /// Plazo vencido: la entrega móvil se rechaza (CU17-paso 19 → 400 'Plazo expirado').
  bool _plazoVencido(Map<String, dynamic> tarea) {
    final limite = DateTime.tryParse((tarea['fecha_limite'] ?? '').toString());
    if (limite == null) return false;
    final hoy = DateTime.now();
    return limite.isBefore(DateTime(hoy.year, hoy.month, hoy.day));
  }

  String _formatearFecha(dynamic valor) {
    final dt = DateTime.tryParse((valor ?? '').toString());
    return dt == null ? (valor ?? '').toString() : DateFormat('dd MMM yyyy', 'es').format(dt);
  }

  /// HU-45 (b): formulario con reflexión libre + dificultad 1-5 (+ ánimo opcional, HU-46).
  void _showReportModal(Map<String, dynamic> tarea) {
    final reflexionController = TextEditingController();
    int dificultad = 3;
    int? animo;
    bool isSubmitting = false;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            final reflexionValida = reflexionController.text.trim().isNotEmpty;
            return Container(
              padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
              decoration: const BoxDecoration(
                color: AppTheme.cardBg,
                borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
                border: Border(
                  top: BorderSide(color: AppTheme.borderSubtle),
                  left: BorderSide(color: AppTheme.borderSubtle),
                  right: BorderSide(color: AppTheme.borderSubtle),
                ),
              ),
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Center(
                      child: Container(
                        width: 40, height: 4,
                        decoration: BoxDecoration(color: AppTheme.borderSubtle, borderRadius: BorderRadius.circular(2)),
                      ),
                    ),
                    const SizedBox(height: 20),
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: AppTheme.success.withOpacity(0.15),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(Icons.task_alt_rounded, color: AppTheme.success, size: 24),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Completar Tarea',
                                  style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16, color: AppTheme.textMain)),
                              Text(tarea['titulo'] ?? 'Tarea',
                                  style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                                  maxLines: 2, overflow: TextOverflow.ellipsis),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // Instrucciones completas y fecha límite (HU-45 conversación)
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppTheme.background,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: AppTheme.borderSubtle),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('INSTRUCCIONES',
                              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.primaryLight, letterSpacing: 0.5)),
                          const SizedBox(height: 6),
                          Text((tarea['descripcion'] ?? '').toString(),
                              style: const TextStyle(fontSize: 13, color: AppTheme.textMain, height: 1.4)),
                          if (tarea['fecha_limite'] != null) ...[
                            const SizedBox(height: 8),
                            Text('Fecha límite: ${_formatearFecha(tarea['fecha_limite'])}',
                                style: const TextStyle(fontSize: 11, color: AppTheme.textSubtle)),
                          ],
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),

                    const Text('TUS REFLEXIONES',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.primaryLight, letterSpacing: 0.5)),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: reflexionController,
                      maxLines: 4,
                      maxLength: 500,
                      onChanged: (_) => setModalState(() {}),
                      style: const TextStyle(color: AppTheme.textMain, fontSize: 14),
                      decoration: InputDecoration(
                        hintText: '¿Cómo te sentiste realizando el ejercicio? ¿Qué descubriste?',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Dificultad 1-5 (estrellas, prototipo Figma)
                    Row(
                      children: [
                        const Text('DIFICULTAD DE LA TAREA',
                            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.primaryLight, letterSpacing: 0.5)),
                        const Spacer(),
                        Text('$dificultad/5',
                            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w900, color: _getDificultadColor(dificultad.toDouble()))),
                      ],
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: List.generate(5, (i) {
                        final n = i + 1;
                        return IconButton(
                          tooltip: 'Dificultad $n de 5',
                          iconSize: 34,
                          onPressed: () => setModalState(() => dificultad = n),
                          icon: Icon(
                            n <= dificultad ? Icons.star_rounded : Icons.star_outline_rounded,
                            color: n <= dificultad ? _getDificultadColor(dificultad.toDouble()) : AppTheme.textSubtle,
                          ),
                        );
                      }),
                    ),
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('1 - Muy fácil', style: TextStyle(fontSize: 10, color: AppTheme.textSubtle)),
                        Text('5 - Muy difícil', style: TextStyle(fontSize: 10, color: AppTheme.textSubtle)),
                      ],
                    ),
                    const SizedBox(height: 20),

                    // HU-46: ánimo del día (opcional) — lo guarda CU17-paso 11 registrar_animo_diario en el servidor
                    const Text('¿CÓMO TE SIENTES HOY? (OPCIONAL)',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.primaryLight, letterSpacing: 0.5)),
                    const SizedBox(height: 8),
                    MoodSelector(
                      seleccionado: animo,
                      onChanged: (v) => setModalState(() => animo = animo == v ? null : v),
                    ),
                    const SizedBox(height: 24),

                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.success,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                      ),
                      icon: isSubmitting
                          ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Icon(Icons.send_rounded, size: 18),
                      label: Text(isSubmitting ? 'Enviando...' : 'Enviar a mi Psicólogo/a',
                          style: const TextStyle(fontWeight: FontWeight.w800)),
                      // CU17-paso 1: entregar_tarea_y_animo(tarea_id, archivo, animo_val, nota) — el Paciente pulsa 'Enviar'
                      // CU17-paso 2: POST /api/v1/clinica/tareas/{id}/entregar/ (vía Sprint2Service.enviarEvidenciaTarea)
                      onPressed: isSubmitting || !reflexionValida
                          ? null
                          : () async {
                              setModalState(() => isSubmitting = true);
                              final messenger = ScaffoldMessenger.of(this.context);
                              final opcion = animo == null ? null : kMoodOpciones.firstWhere((m) => m['val'] == animo);
                              final result = await _sprint2Service.enviarEvidenciaTarea(
                                tarea['id'].toString(),
                                {
                                  'texto_reflexion': reflexionController.text.trim(),
                                  'dificultad_percibida': dificultad,
                                  if (opcion != null) 'escala_animo': opcion['val'],
                                  if (opcion != null) 'estado_animo': opcion['code'],
                                },
                              );
                              if (!context.mounted) return;
                              Navigator.pop(context);
                              final ok = result['success'] == true;
                              final data = result['data'] is Map ? result['data'] as Map : const {};
                              // CU17-paso 17 / CU17-paso 19: respuesta 200 OK o 400 Bad Request [retorno]
                              // CU17-paso 18: mostrar_animacion_exito_y_racha('Entrega confirmada') si ok
                              // CU17-paso 20: mostrar_error_entrega('No se puede entregar la tarea fuera de plazo') si falla
                              messenger.showSnackBar(SnackBar(
                                content: Text(ok
                                    ? '✅ ${data['mensaje'] ?? 'Tarea entregada'}'
                                    : (result['error'] ?? 'No se pudo entregar la tarea.').toString()),
                                backgroundColor: ok ? AppTheme.success : AppTheme.danger,
                                behavior: SnackBarBehavior.floating,
                              ));
                              if (mounted) _loadTareas();
                            },
                    ),
                    const SizedBox(height: 12),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Color _getDificultadColor(double value) {
    if (value <= 1.5) return AppTheme.success;
    if (value <= 2.5) return const Color(0xFF84CC16);
    if (value <= 3.5) return AppTheme.warning;
    if (value <= 4.5) return const Color(0xFFF97316);
    return AppTheme.danger;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Mis Tareas Terapéuticas', style: TextStyle(fontWeight: FontWeight.w800)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, size: 22, color: AppTheme.primaryLight),
            onPressed: () {
              setState(() => _isLoading = true);
              _loadTareas();
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
          : FadeTransition(
              opacity: _fadeAnimation,
              child: _tareas.isEmpty ? _buildEmptyState() : _buildTareasList(),
            ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: AppTheme.primary.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.assignment_outlined, size: 56, color: AppTheme.primaryLight),
            ),
            const SizedBox(height: 24),
            const Text(
              'Sin Tareas Asignadas',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppTheme.textMain),
            ),
            const SizedBox(height: 8),
            const Text(
              'Tu psicólogo/a aún no ha asignado tareas terapéuticas.\nRevisaremos en tu próxima sesión.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: AppTheme.textMuted, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTareasList() {
    return Column(
      children: [
        // Progress header
        Container(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                AppTheme.primary.withOpacity(0.2),
                AppTheme.secondary.withOpacity(0.1),
              ],
            ),
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: AppTheme.primaryLight.withOpacity(0.3)),
          ),
          child: Row(
            children: [
              // Circular progress
              SizedBox(
                width: 64,
                height: 64,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    CircularProgressIndicator(
                      value: _porcentaje,
                      strokeWidth: 6,
                      backgroundColor: AppTheme.borderSubtle,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        _porcentaje >= 1 ? AppTheme.success : AppTheme.primary,
                      ),
                    ),
                    Text(
                      '${(_porcentaje * 100).round()}%',
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w900, color: AppTheme.textMain),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 20),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Progreso Semanal',
                      style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: AppTheme.textMain),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '$_completadas de $_total tareas entregadas',
                      style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        _buildMiniKpi('Pendientes', '${_total - _completadas}', AppTheme.warning),
                        const SizedBox(width: 12),
                        _buildMiniKpi('Entregadas', '$_completadas', AppTheme.success),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        // Tasks list
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            itemCount: _tareas.length,
            itemBuilder: (context, index) => _buildTareaCard(_tareas[index]),
          ),
        ),
      ],
    );
  }

  Widget _buildMiniKpi(String label, String value, Color color) {
    return Row(
      children: [
        Container(
          width: 8, height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(
          '$label: $value',
          style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: color),
        ),
      ],
    );
  }

  Widget _buildTareaCard(Map<String, dynamic> tarea) {
    final estado = (tarea['estado'] ?? 'PENDIENTE').toString().toUpperCase();
    final isCompletada = _estaEntregada(estado);
    final vencida = !isCompletada && _plazoVencido(tarea);

    final categoria = tarea['categoria']?.toString() ?? '';
    final categoriaColor = _getCategoriaColor(categoria);
    final estadoColor = _getEstadoColor(estado);

    final fechaLimite = tarea['fecha_limite'] == null ? '' : _formatearFecha(tarea['fecha_limite']);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isCompletada ? AppTheme.success.withOpacity(0.3) : AppTheme.borderSubtle,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.15),
            blurRadius: 8,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: categoriaColor.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(_getCategoriaIcon(categoria), size: 20, color: categoriaColor),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        tarea['titulo'] ?? 'Tarea',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w800,
                          color: AppTheme.textMain,
                          decoration: isCompletada ? TextDecoration.lineThrough : null,
                        ),
                      ),
                      if (categoria.isNotEmpty) ...[
                        const SizedBox(height: 2),
                        Text(
                          categoria,
                          style: TextStyle(fontSize: 11, color: categoriaColor, fontWeight: FontWeight.w600),
                        ),
                      ],
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: estadoColor.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: estadoColor.withOpacity(0.3)),
                  ),
                  child: Text(
                    _getEstadoLabel(estado),
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: estadoColor),
                  ),
                ),
              ],
            ),
            if (tarea['descripcion'] != null && tarea['descripcion'].toString().isNotEmpty) ...[
              const SizedBox(height: 10),
              Text(
                tarea['descripcion'].toString(),
                style: const TextStyle(fontSize: 12, color: AppTheme.textMuted, height: 1.4),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
            ],
            const SizedBox(height: 12),
            Row(
              children: [
                if (fechaLimite.isNotEmpty) ...[
                  const Icon(Icons.calendar_today_rounded, size: 13, color: AppTheme.textSubtle),
                  const SizedBox(width: 4),
                  Text(
                    'Fecha límite: $fechaLimite',
                    style: const TextStyle(fontSize: 11, color: AppTheme.textSubtle),
                  ),
                ],
                const Spacer(),
                if (vencida)
                  const Text('Plazo vencido',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.danger)),
                if (!isCompletada && !vencida)
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.success,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                      visualDensity: VisualDensity.compact,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    icon: const Icon(Icons.task_alt_rounded, size: 16),
                    label: const Text('Completar Tarea', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800)),
                    onPressed: () => _showReportModal(tarea),
                  ),
                if (isCompletada)
                  Row(
                    children: [
                      Icon(Icons.check_circle_rounded, size: 16, color: AppTheme.success),
                      const SizedBox(width: 4),
                      Text(
                        'Entregada',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.success),
                      ),
                    ],
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
