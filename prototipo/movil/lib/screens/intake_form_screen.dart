// ==============================================================================
// MÓDULO: intake_form_screen.dart
// CAPA BCE: BOUNDARY (Interfaz de Usuario Móvil – Flutter)
// CASO DE USO: CU14 – Gestionar Formulario Previo a la Consulta (Intake Digital)
// HISTORIA: HU-24 – Diligenciamiento de formulario previo en App Móvil
// DESCRIPCIÓN: Stepper interactivo de 4 pasos para que el paciente complete su
//              formulario pre-consulta desde la app móvil. Incluye validación por
//              paso, barra de progreso porcentual y bloqueo tras envío exitoso.
// DIAGRAMA DE SECUENCIA CU14 (Flujo Móvil):
//   1. Paciente abre IntakeFormScreen → Sprint2Service.getFormularioActivo()
//   2. Paciente completa Paso 1 (Motivo) → Validación local
//   3. Paciente completa Paso 2 (Síntomas) → Validación multi-selección
//   4. Paciente completa Paso 3 (Malestar) → Slider 1-5
//   5. Paciente completa Paso 4 (Antecedentes) → Texto libre
//   6. Paciente presiona 'Enviar' → Sprint2Service.enviarRespuestaIntake()
//   7. Backend retorna 201 Created → UI bloquea ediciones y muestra confirmación
// ==============================================================================
import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../services/auth_service.dart';
import '../services/sprint2_service.dart';

class IntakeFormScreen extends StatefulWidget {
  final AuthService authService;

  const IntakeFormScreen({super.key, required this.authService});

  @override
  State<IntakeFormScreen> createState() => _IntakeFormScreenState();
}

class _IntakeFormScreenState extends State<IntakeFormScreen> with TickerProviderStateMixin {
  late final Sprint2Service _sprint2Service;
  late final AnimationController _fadeController;
  late final Animation<double> _fadeAnimation;

  int _currentStep = 0;
  bool _isLoading = true;
  bool _isSubmitting = false;
  bool _isSubmitted = false;
  String? _errorMsg;
  Map<String, dynamic>? _formulario;

  // Form data
  final _motivoController = TextEditingController();
  final _antecedentesController = TextEditingController();
  double _nivelMalestar = 3;
  final List<String> _sintomasDisponibles = [
    'Ansiedad',
    'Tristeza o depresión',
    'Insomnio',
    'Irritabilidad',
    'Fatiga constante',
    'Dificultad para concentrarse',
    'Pensamientos negativos recurrentes',
    'Aislamiento social',
    'Cambios en el apetito',
    'Ataques de pánico',
    'Estrés laboral / académico',
    'Problemas de autoestima',
  ];
  final Set<String> _sintomasSeleccionados = {};

  @override
  void initState() {
    super.initState();
    _sprint2Service = Sprint2Service(authService: widget.authService);
    _fadeController = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));
    _fadeAnimation = CurvedAnimation(parent: _fadeController, curve: Curves.easeOut);
    _loadFormulario();
  }

  @override
  void dispose() {
    _motivoController.dispose();
    _antecedentesController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  Future<void> _loadFormulario() async {
    final form = await _sprint2Service.getFormularioActivo();
    final previas = await _sprint2Service.getMisRespuestasIntake();
    if (mounted) {
      setState(() {
        _formulario = form;
        _isLoading = false;
        if (previas.isNotEmpty) {
          _isSubmitted = true;
        }
      });
      _fadeController.forward();
    }
  }

  bool _validateCurrentStep() {
    switch (_currentStep) {
      case 0:
        return _motivoController.text.trim().length >= 10;
      case 1:
        return _sintomasSeleccionados.isNotEmpty;
      case 2:
        return true; // Slider always has a value
      case 3:
        return true; // Antecedentes is optional
      default:
        return true;
    }
  }

  String _getStepValidationError() {
    switch (_currentStep) {
      case 0:
        return 'El motivo de consulta debe tener al menos 10 caracteres.';
      case 1:
        return 'Selecciona al menos un síntoma frecuente.';
      default:
        return '';
    }
  }

  void _nextStep() {
    if (!_validateCurrentStep()) {
      setState(() => _errorMsg = _getStepValidationError());
      return;
    }
    setState(() {
      _errorMsg = null;
      if (_currentStep < 3) {
        _currentStep++;
      }
    });
  }

  void _prevStep() {
    setState(() {
      _errorMsg = null;
      if (_currentStep > 0) _currentStep--;
    });
  }

  Future<void> _submitIntake() async {
    if (!_validateCurrentStep()) {
      setState(() => _errorMsg = _getStepValidationError());
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMsg = null;
    });

    final data = {
      if (_formulario != null) 'formulario': _formulario!['id'],
      'motivo_consulta': _motivoController.text.trim(),
      'nivel_urgencia': _nivelMalestar.round(),
      'respuestas_detalle': {
        'sintomas_frecuentes': _sintomasSeleccionados.toList(),
        'nivel_malestar_emocional': _nivelMalestar.round(),
        'antecedentes': _antecedentesController.text.trim(),
      },
      'estado': 'ENVIADO',
    };

    final result = await _sprint2Service.enviarRespuestaIntake(data);

    if (mounted) {
      setState(() => _isSubmitting = false);
      if (result['success'] == true) {
        setState(() => _isSubmitted = true);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Formulario previo enviado exitosamente'),
            backgroundColor: AppTheme.success,
            behavior: SnackBarBehavior.floating,
          ),
        );
      } else {
        setState(() => _errorMsg = result['error'] ?? 'Error al enviar formulario.');
      }
    }
  }

  Color _getMalestarColor(double value) {
    if (value <= 1.5) return AppTheme.success;
    if (value <= 2.5) return const Color(0xFF84CC16);
    if (value <= 3.5) return AppTheme.warning;
    if (value <= 4.5) return const Color(0xFFF97316);
    return AppTheme.danger;
  }

  String _getMalestarLabel(double value) {
    final v = value.round();
    switch (v) {
      case 1: return 'Mínimo';
      case 2: return 'Leve';
      case 3: return 'Moderado';
      case 4: return 'Alto';
      case 5: return 'Muy Alto';
      default: return 'Moderado';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Formulario Pre-Consulta', style: TextStyle(fontWeight: FontWeight.w800)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
          : _isSubmitted
              ? _buildSuccessView()
              : _buildStepperForm(),
    );
  }

  Widget _buildSuccessView() {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [AppTheme.success.withOpacity(0.2), AppTheme.success.withOpacity(0.05)],
                  ),
                  shape: BoxShape.circle,
                  border: Border.all(color: AppTheme.success.withOpacity(0.4)),
                ),
                child: const Icon(Icons.check_circle_rounded, size: 64, color: AppTheme.success),
              ),
              const SizedBox(height: 24),
              const Text(
                'Formulario Enviado',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: AppTheme.textMain),
              ),
              const SizedBox(height: 12),
              Text(
                'Tu formulario previo a la consulta ha sido recibido.\nTu psicólogo/a lo revisará antes de la sesión.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 14, color: AppTheme.textMuted, height: 1.5),
              ),
              const SizedBox(height: 32),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppTheme.cardBg,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppTheme.borderSubtle),
                ),
                child: Row(
                  children: [
                    Icon(Icons.lock_outline_rounded, size: 20, color: AppTheme.textSubtle),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'El formulario ya no puede ser editado para preservar la integridad clínica.',
                        style: TextStyle(fontSize: 12, color: AppTheme.textSubtle),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                ),
                icon: const Icon(Icons.arrow_back_rounded, size: 18),
                label: const Text('Volver al Dashboard'),
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStepperForm() {
    final progress = (_currentStep + 1) / 4;
    final stepLabels = ['Motivo', 'Síntomas', 'Malestar', 'Antecedentes'];

    return FadeTransition(
      opacity: _fadeAnimation,
      child: Column(
        children: [
          // Progress header
          Container(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 16),
            decoration: BoxDecoration(
              color: AppTheme.cardBg,
              border: Border(bottom: BorderSide(color: AppTheme.borderSubtle)),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Paso ${_currentStep + 1} de 4',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppTheme.primaryLight),
                    ),
                    Text(
                      '${(progress * 100).round()}%',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppTheme.primary),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: LinearProgressIndicator(
                    value: progress,
                    minHeight: 8,
                    backgroundColor: AppTheme.inputBg,
                    valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primary),
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: List.generate(4, (i) {
                    final isActive = i == _currentStep;
                    final isCompleted = i < _currentStep;
                    return Expanded(
                      child: Container(
                        margin: EdgeInsets.only(right: i < 3 ? 6 : 0),
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        decoration: BoxDecoration(
                          color: isActive
                              ? AppTheme.primary.withOpacity(0.15)
                              : isCompleted
                                  ? AppTheme.success.withOpacity(0.1)
                                  : AppTheme.inputBg,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: isActive
                                ? AppTheme.primary.withOpacity(0.5)
                                : isCompleted
                                    ? AppTheme.success.withOpacity(0.3)
                                    : Colors.transparent,
                          ),
                        ),
                        child: Column(
                          children: [
                            Icon(
                              isCompleted ? Icons.check_circle_rounded : Icons.circle_outlined,
                              size: 14,
                              color: isActive ? AppTheme.primary : isCompleted ? AppTheme.success : AppTheme.textSubtle,
                            ),
                            const SizedBox(height: 2),
                            Text(
                              stepLabels[i],
                              style: TextStyle(
                                fontSize: 9,
                                fontWeight: isActive ? FontWeight.w800 : FontWeight.w600,
                                color: isActive ? AppTheme.primary : isCompleted ? AppTheme.success : AppTheme.textSubtle,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }),
                ),
              ],
            ),
          ),

          // Error message
          if (_errorMsg != null)
            Container(
              width: double.infinity,
              margin: const EdgeInsets.fromLTRB(16, 12, 16, 0),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppTheme.danger.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.danger.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline_rounded, size: 18, color: AppTheme.danger),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(_errorMsg!, style: const TextStyle(fontSize: 12, color: AppTheme.danger)),
                  ),
                ],
              ),
            ),

          // Step content
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 300),
                child: _buildStepContent(_currentStep),
              ),
            ),
          ),

          // Navigation buttons
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.cardBg,
              border: Border(top: BorderSide(color: AppTheme.borderSubtle)),
            ),
            child: Row(
              children: [
                if (_currentStep > 0)
                  Expanded(
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppTheme.textMain,
                        side: const BorderSide(color: AppTheme.borderSubtle),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                      ),
                      icon: const Icon(Icons.arrow_back_rounded, size: 18),
                      label: const Text('Anterior', style: TextStyle(fontWeight: FontWeight.w700)),
                      onPressed: _prevStep,
                    ),
                  ),
                if (_currentStep > 0) const SizedBox(width: 12),
                Expanded(
                  flex: 2,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _currentStep == 3 ? AppTheme.success : AppTheme.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    ),
                    icon: _isSubmitting
                        ? const SizedBox(
                            width: 18, height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          )
                        : Icon(
                            _currentStep == 3 ? Icons.send_rounded : Icons.arrow_forward_rounded,
                            size: 18,
                          ),
                    label: Text(
                      _currentStep == 3 ? 'Enviar Formulario' : 'Continuar',
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                    onPressed: _isSubmitting
                        ? null
                        : _currentStep == 3
                            ? _submitIntake
                            : _nextStep,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStepContent(int step) {
    switch (step) {
      case 0:
        return _buildMotivoStep();
      case 1:
        return _buildSintomasStep();
      case 2:
        return _buildMalestarStep();
      case 3:
        return _buildAntecedentesStep();
      default:
        return const SizedBox();
    }
  }

  Widget _buildMotivoStep() {
    return Column(
      key: const ValueKey('step0'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildStepHeader(
          icon: Icons.chat_bubble_outline_rounded,
          title: 'Motivo de Consulta',
          subtitle: 'Describe brevemente por qué buscas atención psicológica.',
        ),
        const SizedBox(height: 20),
        TextFormField(
          controller: _motivoController,
          maxLines: 6,
          maxLength: 500,
          style: const TextStyle(color: AppTheme.textMain, fontSize: 14),
          decoration: InputDecoration(
            hintText: 'Ejemplo: Me siento ansioso/a frecuentemente y me cuesta dormir...',
            alignLabelWithHint: true,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
          ),
          onChanged: (_) => setState(() => _errorMsg = null),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppTheme.info.withOpacity(0.08),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppTheme.info.withOpacity(0.2)),
          ),
          child: Row(
            children: [
              Icon(Icons.info_outline_rounded, size: 16, color: AppTheme.info),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  'Esta información es confidencial y solo será visible para tu psicólogo/a tratante.',
                  style: TextStyle(fontSize: 11, color: AppTheme.info),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSintomasStep() {
    return Column(
      key: const ValueKey('step1'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildStepHeader(
          icon: Icons.healing_rounded,
          title: 'Síntomas Frecuentes',
          subtitle: 'Selecciona los síntomas que has experimentado recientemente.',
        ),
        const SizedBox(height: 16),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _sintomasDisponibles.map((sintoma) {
            final selected = _sintomasSeleccionados.contains(sintoma);
            return FilterChip(
              label: Text(
                sintoma,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                  color: selected ? Colors.white : AppTheme.textMuted,
                ),
              ),
              selected: selected,
              onSelected: (val) {
                setState(() {
                  if (val) {
                    _sintomasSeleccionados.add(sintoma);
                  } else {
                    _sintomasSeleccionados.remove(sintoma);
                  }
                  _errorMsg = null;
                });
              },
              selectedColor: AppTheme.primary,
              backgroundColor: AppTheme.inputBg,
              checkmarkColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
                side: BorderSide(
                  color: selected ? AppTheme.primary : AppTheme.borderSubtle,
                ),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
            );
          }).toList(),
        ),
        const SizedBox(height: 16),
        Text(
          '${_sintomasSeleccionados.length} síntoma(s) seleccionado(s)',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: _sintomasSeleccionados.isNotEmpty ? AppTheme.primaryLight : AppTheme.textSubtle,
          ),
        ),
      ],
    );
  }

  Widget _buildMalestarStep() {
    final color = _getMalestarColor(_nivelMalestar);
    return Column(
      key: const ValueKey('step2'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildStepHeader(
          icon: Icons.mood_rounded,
          title: 'Nivel de Malestar Emocional',
          subtitle: 'Indica cómo te sientes en general en una escala del 1 al 5.',
        ),
        const SizedBox(height: 32),
        Center(
          child: Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: [color.withOpacity(0.3), color.withOpacity(0.08)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              border: Border.all(color: color.withOpacity(0.5), width: 3),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  '${_nivelMalestar.round()}',
                  style: TextStyle(fontSize: 36, fontWeight: FontWeight.w900, color: color),
                ),
                Text(
                  _getMalestarLabel(_nivelMalestar),
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: color),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 32),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('1 - Mínimo', style: TextStyle(fontSize: 11, color: AppTheme.success, fontWeight: FontWeight.w600)),
            Text('5 - Muy Alto', style: TextStyle(fontSize: 11, color: AppTheme.danger, fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: 8),
        SliderTheme(
          data: SliderThemeData(
            activeTrackColor: color,
            inactiveTrackColor: color.withOpacity(0.15),
            thumbColor: color,
            overlayColor: color.withOpacity(0.2),
            trackHeight: 8,
            thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 14),
          ),
          child: Slider(
            value: _nivelMalestar,
            min: 1,
            max: 5,
            divisions: 4,
            onChanged: (v) => setState(() => _nivelMalestar = v),
          ),
        ),
        const SizedBox(height: 20),
        if (_nivelMalestar >= 4)
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.warning.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.warning.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                Icon(Icons.warning_amber_rounded, size: 18, color: AppTheme.warning),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Tu psicólogo/a será notificado/a de este nivel de malestar para priorizar tu atención.',
                    style: TextStyle(fontSize: 11, color: AppTheme.warning),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildAntecedentesStep() {
    return Column(
      key: const ValueKey('step3'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildStepHeader(
          icon: Icons.history_edu_rounded,
          title: 'Antecedentes',
          subtitle: 'Comparte antecedentes médicos o psicológicos relevantes (opcional).',
        ),
        const SizedBox(height: 20),
        TextFormField(
          controller: _antecedentesController,
          maxLines: 5,
          maxLength: 500,
          style: const TextStyle(color: AppTheme.textMain, fontSize: 14),
          decoration: InputDecoration(
            hintText: 'Ejemplo: Tratamiento previo con psicólogo hace 2 años, medicación actual...',
            alignLabelWithHint: true,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
          ),
        ),
        const SizedBox(height: 20),

        // Summary card
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.cardBg,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.borderSubtle),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'RESUMEN DEL FORMULARIO',
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.primaryLight, letterSpacing: 0.5),
              ),
              const SizedBox(height: 12),
              _buildSummaryRow('Motivo', _motivoController.text.trim().isEmpty ? '—' : '${_motivoController.text.trim().substring(0, _motivoController.text.trim().length > 40 ? 40 : _motivoController.text.trim().length)}...'),
              _buildSummaryRow('Síntomas', '${_sintomasSeleccionados.length} seleccionados'),
              _buildSummaryRow('Malestar', '${_nivelMalestar.round()}/5 (${_getMalestarLabel(_nivelMalestar)})'),
              _buildSummaryRow('Antecedentes', _antecedentesController.text.trim().isEmpty ? 'No especificado' : 'Incluido'),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 12, color: AppTheme.textSubtle)),
          Flexible(
            child: Text(
              value,
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppTheme.textMain),
              textAlign: TextAlign.end,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStepHeader({
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: AppTheme.primary.withOpacity(0.12),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: AppTheme.primaryLight, size: 24),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textMain)),
              const SizedBox(height: 2),
              Text(subtitle, style: const TextStyle(fontSize: 12, color: AppTheme.textMuted)),
            ],
          ),
        ),
      ],
    );
  }
}
