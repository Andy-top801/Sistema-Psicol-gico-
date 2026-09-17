// ==============================================================================
// MÓDULO: mis_tareas_screen.dart
// CAPA BCE: BOUNDARY (Interfaz de Usuario Móvil – Flutter)
// CASO DE USO: CU17 – Gestionar Evolución, Tareas y Seguimiento Terapéutico
// HISTORIA: HU-30 – Visualización y Reporte de Avance de Tareas en App Móvil
// DESCRIPCIÓN: Pantalla para que el paciente visualice sus tareas terapéuticas
//              inter-sesiones, con cards de estado, badge de progreso y modal de
//              reporte de cumplimiento con reflexión y dificultad percibida.
// DIAGRAMA DE SECUENCIA CU17 (Flujo Móvil):
//   1. Paciente abre MisTareasScreen → Sprint2Service.getMisTareas()
//   2. Paciente ve lista con badges de estado y fecha límite
//   3. Paciente presiona 'Reportar Cumplimiento' → Modal con reflexión + slider
//   4. Paciente envía reporte → Sprint2Service.enviarEvidenciaTarea()
//   5. Backend retorna 201 + actualiza estado → UI refleja COMPLETADA
// ==============================================================================
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../core/theme/app_theme.dart';
import '../services/auth_service.dart';
import '../services/sprint2_service.dart';

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

  int get _completadas => _tareas.where((t) => (t['estado'] ?? '').toString().toUpperCase() == 'COMPLETADA').length;
  int get _total => _tareas.length;
  double get _porcentaje => _total > 0 ? _completadas / _total : 0;

  Color _getEstadoColor(String estado) {
    switch (estado.toUpperCase()) {
      case 'COMPLETADA': return AppTheme.success;
      case 'PENDIENTE': return AppTheme.warning;
      case 'EN_PROGRESO': return AppTheme.primary;
      case 'VENCIDA': return AppTheme.danger;
      default: return AppTheme.textSubtle;
    }
  }

  String _getEstadoLabel(String estado) {
    switch (estado.toUpperCase()) {
      case 'COMPLETADA': return 'Completada';
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

  void _showReportModal(Map<String, dynamic> tarea) {
    final reflexionController = TextEditingController();
    double dificultad = 3;
    bool isSubmitting = false;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return Container(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).viewInsets.bottom,
              ),
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
                    // Handle
                    Center(
                      child: Container(
                        width: 40, height: 4,
                        decoration: BoxDecoration(
                          color: AppTheme.borderSubtle,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Header
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: AppTheme.success.withOpacity(0.15),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(Icons.check_circle_outline_rounded, color: AppTheme.success, size: 24),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Reportar Cumplimiento',
                                style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16, color: AppTheme.textMain),
                              ),
                              Text(
                                tarea['titulo'] ?? 'Tarea',
                                style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),

                    // Reflexión
                    const Text(
                      'NOTAS DE AUTORREFLEXIÓN',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.primaryLight, letterSpacing: 0.5),
                    ),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: reflexionController,
                      maxLines: 4,
                      maxLength: 500,
                      style: const TextStyle(color: AppTheme.textMain, fontSize: 14),
                      decoration: InputDecoration(
                        hintText: '¿Cómo te sentiste realizando el ejercicio? ¿Qué descubriste?',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Dificultad
                    const Text(
                      'DIFICULTAD PERCIBIDA',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.primaryLight, letterSpacing: 0.5),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('1 - Fácil', style: TextStyle(fontSize: 11, color: AppTheme.success)),
                        Text(
                          '${dificultad.round()}/5',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w900,
                            color: _getDificultadColor(dificultad),
                          ),
                        ),
                        const Text('5 - Difícil', style: TextStyle(fontSize: 11, color: AppTheme.danger)),
                      ],
                    ),
                    SliderTheme(
                      data: SliderThemeData(
                        activeTrackColor: _getDificultadColor(dificultad),
                        inactiveTrackColor: _getDificultadColor(dificultad).withOpacity(0.15),
                        thumbColor: _getDificultadColor(dificultad),
                        overlayColor: _getDificultadColor(dificultad).withOpacity(0.2),
                        trackHeight: 6,
                      ),
                      child: Slider(
                        value: dificultad,
                        min: 1,
                        max: 5,
                        divisions: 4,
                        onChanged: (v) => setModalState(() => dificultad = v),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Submit button
                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.success,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                      ),
                      icon: isSubmitting
                          ? const SizedBox(
                              width: 18, height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                            )
                          : const Icon(Icons.send_rounded, size: 18),
                      label: Text(
                        isSubmitting ? 'Enviando...' : 'Enviar a mi Psicólogo/a',
                        style: const TextStyle(fontWeight: FontWeight.w800),
                      ),
                      onPressed: isSubmitting
                          ? null
                          : () async {
                              setModalState(() => isSubmitting = true);
                              final result = await _sprint2Service.enviarEvidenciaTarea(
                                tarea['id'].toString(),
                                {
                                  'texto_reflexion': reflexionController.text.trim(),
                                  'dificultad_percibida': dificultad.round(),
                                },
                              );
                              if (context.mounted) {
                                Navigator.pop(context);
                                if (result['success'] == true) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('✅ Reporte enviado exitosamente'),
                                      backgroundColor: AppTheme.success,
                                      behavior: SnackBarBehavior.floating,
                                    ),
                                  );
                                  _loadTareas(); // Refresh list
                                } else {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text(result['error'] ?? 'Error al enviar reporte'),
                                      backgroundColor: AppTheme.danger,
                                      behavior: SnackBarBehavior.floating,
                                    ),
                                  );
                                }
                              }
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
                      '$_completadas de $_total tareas completadas',
                      style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        _buildMiniKpi('Pendientes', '${_total - _completadas}', AppTheme.warning),
                        const SizedBox(width: 12),
                        _buildMiniKpi('Completadas', '$_completadas', AppTheme.success),
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
    final isCompletada = estado == 'COMPLETADA';
    final categoria = tarea['categoria']?.toString() ?? '';
    final categoriaColor = _getCategoriaColor(categoria);
    final estadoColor = _getEstadoColor(estado);

    String fechaLimite = '';
    if (tarea['fecha_limite'] != null) {
      try {
        final dt = DateTime.parse(tarea['fecha_limite'].toString());
        fechaLimite = DateFormat('dd MMM yyyy', 'es').format(dt);
      } catch (_) {
        fechaLimite = tarea['fecha_limite'].toString();
      }
    }

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
                if (!isCompletada)
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.success,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                      visualDensity: VisualDensity.compact,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    icon: const Icon(Icons.check_rounded, size: 16),
                    label: const Text('Reportar', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800)),
                    onPressed: () => _showReportModal(tarea),
                  ),
                if (isCompletada)
                  Row(
                    children: [
                      Icon(Icons.check_circle_rounded, size: 16, color: AppTheme.success),
                      const SizedBox(width: 4),
                      Text(
                        'Enviada',
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
