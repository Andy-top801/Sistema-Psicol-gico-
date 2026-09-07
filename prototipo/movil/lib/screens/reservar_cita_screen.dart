import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/auth_service.dart';
import '../services/agenda_service.dart';
import '../services/clinica_service.dart';
import '../models/psicologo_model.dart';
import '../models/paciente_model.dart';
import '../core/theme/app_theme.dart';

class ReservarCitaScreen extends StatefulWidget {
  final AuthService authService;

  const ReservarCitaScreen({super.key, required this.authService});

  @override
  State<ReservarCitaScreen> createState() => _ReservarCitaScreenState();
}

class _ReservarCitaScreenState extends State<ReservarCitaScreen> {
  late final AgendaService _agendaService;
  late final ClinicaService _clinicaService;

  bool _isLoadingInitial = true;
  bool _isLoadingSlots = false;
  bool _isSubmitting = false;

  PacienteModel? _paciente;
  List<PsicologoModel> _psicologos = [];

  PsicologoModel? _selectedPsicologo;
  DateTime _selectedDate = DateTime.now();
  String? _selectedSlot; // e.g. "08:00 - 08:50" or "08:00"
  List<String> _slotsDisponibles = [];
  String _modalidad = 'PRESENCIAL'; // 'PRESENCIAL' | 'VIRTUAL'
  final _motivoCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _agendaService = AgendaService(authService: widget.authService);
    _clinicaService = ClinicaService(authService: widget.authService);
    _initData();
  }

  @override
  void dispose() {
    _motivoCtrl.dispose();
    super.dispose();
  }

  Future<void> _initData() async {
    setState(() => _isLoadingInitial = true);
    final results = await Future.wait([
      _clinicaService.getMiPerfil(),
      _clinicaService.getPsicologos(),
    ]);

    _paciente = results[0] as PacienteModel?;
    _psicologos = results[1] as List<PsicologoModel>;

    if (_psicologos.isNotEmpty) {
      _selectedPsicologo = _psicologos.first;
      _cargarSlots();
    } else {
      setState(() => _isLoadingInitial = false);
    }
  }

  Future<void> _cargarSlots() async {
    if (_selectedPsicologo == null) return;
    setState(() {
      _isLoadingSlots = true;
      _selectedSlot = null;
      _slotsDisponibles = [];
    });

    final fechaStr = DateFormat('yyyy-MM-dd').format(_selectedDate);
    final slots = await _clinicaService.getSlotsDisponibles(_selectedPsicologo!.id, fechaStr);

    setState(() {
      _slotsDisponibles = slots;
      _isLoadingSlots = false;
      _isLoadingInitial = false;
    });
  }

  Future<void> _pickDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate.isBefore(now) ? now : _selectedDate,
      firstDate: now,
      lastDate: now.add(const Duration(days: 90)),
      builder: (context, child) {
        return Theme(
          data: ThemeData.dark().copyWith(
            colorScheme: const ColorScheme.dark(
              primary: AppTheme.primary,
              onPrimary: Colors.white,
              surface: AppTheme.cardBg,
              onSurface: AppTheme.textMain,
            ),
            dialogBackgroundColor: AppTheme.cardBg,
          ),
          child: child!,
        );
      },
    );

    if (picked != null && picked != _selectedDate) {
      setState(() => _selectedDate = picked);
      _cargarSlots();
    }
  }

  Future<void> _confirmarReserva() async {
    if (_paciente == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: AppTheme.danger,
          content: Text('No cuentas con un perfil de paciente activo para agendar citas.'),
        ),
      );
      return;
    }

    if (_selectedPsicologo == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: AppTheme.danger,
          content: Text('Selecciona un terapeuta.'),
        ),
      );
      return;
    }

    if (_selectedSlot == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: AppTheme.danger,
          content: Text('Por favor selecciona un horario disponible.'),
        ),
      );
      return;
    }

    // Calcular hora inicio y fin a partir del slot
    // Formatos comunes de slot: "08:00 - 08:50" o "08:00"
    String horaInicio = '08:00:00';
    String horaFin = '08:50:00';

    if (_selectedSlot!.contains('-')) {
      final parts = _selectedSlot!.split('-');
      horaInicio = '${parts[0].trim()}:00';
      horaFin = '${parts[1].trim()}:00';
    } else {
      horaInicio = '${_selectedSlot!.trim()}:00';
      // calcular +50 minutos
      try {
        final timeParts = _selectedSlot!.split(':');
        int h = int.parse(timeParts[0]);
        int m = int.parse(timeParts[1]) + 50;
        if (m >= 60) {
          h += 1;
          m -= 60;
        }
        horaFin = '${h.toString().padLeft(2, '0')}:${m.toString().padLeft(2, '0')}:00';
      } catch (_) {}
    }

    setState(() => _isSubmitting = true);

    final fechaStr = DateFormat('yyyy-MM-dd').format(_selectedDate);

    final res = await _agendaService.reservarCita(
      pacienteId: _paciente!.id,
      psicologoId: _selectedPsicologo!.id,
      fecha: fechaStr,
      horaInicio: horaInicio,
      horaFin: horaFin,
      modalidad: _modalidad,
      motivoConsulta: _motivoCtrl.text.trim().isNotEmpty ? _motivoCtrl.text.trim() : 'Consulta general de psicología',
      costo: _selectedPsicologo!.tarifaBase,
    );

    setState(() => _isSubmitting = false);

    if (mounted) {
      if (res['success'] == true) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (ctx) => AlertDialog(
            backgroundColor: AppTheme.cardBg,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            title: const Row(
              children: [
                Icon(Icons.check_circle_rounded, color: AppTheme.success, size: 28),
                SizedBox(width: 10),
                Text('¡Cita Confirmada!', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Tu cita fue reservada con éxito en el sistema.',
                  style: TextStyle(color: AppTheme.textMuted, fontSize: 13),
                ),
                const SizedBox(height: 14),
                _buildModalDetail('Terapeuta', _selectedPsicologo!.nombreCompleto),
                _buildModalDetail('Fecha', DateFormat('dd/MM/yyyy').format(_selectedDate)),
                _buildModalDetail('Horario', _selectedSlot!),
                _buildModalDetail('Modalidad', _modalidad),
                _buildModalDetail('Tarifa', 'Bs. ${_selectedPsicologo!.tarifaBase.toStringAsFixed(2)}'),
                if (_modalidad == 'VIRTUAL') ...[
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppTheme.primary.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.videocam_outlined, size: 18, color: AppTheme.primaryLight),
                        SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'La sala de teleconsulta se habilitará 15 minutos antes de la hora acordada.',
                            style: TextStyle(fontSize: 11, color: AppTheme.primaryLight),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
            actions: [
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(ctx);
                  Navigator.pop(context, true); // Retorna indicando que se creó cita
                },
                child: const Text('Ver Mis Citas'),
              ),
            ],
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: AppTheme.danger,
            content: Text(res['error'] ?? 'Error al agendar la cita. Es posible que el horario ya esté reservado.'),
          ),
        );
      }
    }
  }

  Widget _buildModalDetail(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: AppTheme.textSubtle, fontSize: 12)),
          Text(value, style: const TextStyle(color: AppTheme.textMain, fontSize: 12, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final fechaFormateada = DateFormat('EEEE, d MMMM yyyy', 'es').format(_selectedDate);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Reservar Cita', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
      ),
      body: _isLoadingInitial
          ? const Center(child: CircularProgressIndicator())
          : SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Paso 1: Seleccionar Terapeuta
                    _buildStepHeader('1', 'SELECCIONA TU PSICÓLOGO / TERAPEUTA'),
                    const SizedBox(height: 10),
                    _buildPsicologoSelector(),
                    const SizedBox(height: 20),

                    // Paso 2: Seleccionar Modalidad (Presencial o Virtual)
                    _buildStepHeader('2', 'MODALIDAD DE ATENCIÓN'),
                    const SizedBox(height: 10),
                    _buildModalidadToggle(),
                    const SizedBox(height: 20),

                    // Paso 3: Seleccionar Fecha
                    _buildStepHeader('3', 'SELECCIONA LA FECHA'),
                    const SizedBox(height: 10),
                    _buildDateSelector(fechaFormateada),
                    const SizedBox(height: 20),

                    // Paso 4: Horarios Disponibles
                    _buildStepHeader('4', 'HORARIOS DISPONIBLES EN AGENDA'),
                    const SizedBox(height: 10),
                    _buildSlotsGrid(),
                    const SizedBox(height: 20),

                    // Paso 5: Motivo de Consulta
                    _buildStepHeader('5', 'MOTIVO DE CONSULTA (OPCIONAL)'),
                    const SizedBox(height: 10),
                    TextFormField(
                      controller: _motivoCtrl,
                      maxLines: 2,
                      decoration: const InputDecoration(
                        hintText: 'Ej: Consulta por ansiedad, seguimiento terapéutico...',
                        prefixIcon: Icon(Icons.notes_rounded),
                      ),
                    ),
                    const SizedBox(height: 26),

                    // Botón Confirmar Cita
                    ElevatedButton.icon(
                      onPressed: _isSubmitting ? null : _confirmarReserva,
                      icon: _isSubmitting
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                            )
                          : const Icon(Icons.calendar_month_rounded),
                      label: Text(_isSubmitting ? 'CONFIRMANDO RESERVA...' : 'CONFIRMAR Y AGENDAR CITA'),
                    ),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildStepHeader(String stepNum, String title) {
    return Row(
      children: [
        Container(
          width: 22,
          height: 22,
          decoration: BoxDecoration(
            gradient: AppTheme.primaryGradient,
            shape: BoxShape.circle,
          ),
          alignment: Alignment.center,
          child: Text(
            stepNum,
            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 0.4, color: AppTheme.textMuted),
        ),
      ],
    );
  }

  Widget _buildPsicologoSelector() {
    if (_psicologos.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppTheme.cardBg,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppTheme.borderSubtle),
        ),
        child: const Text(
          'No hay terapeutas disponibles registrados en este centro.',
          style: TextStyle(color: AppTheme.textMuted, fontSize: 13),
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.borderSubtle),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<PsicologoModel>(
          value: _selectedPsicologo,
          isExpanded: true,
          dropdownColor: AppTheme.cardBgElevated,
          items: _psicologos.map((psi) {
            return DropdownMenuItem<PsicologoModel>(
              value: psi,
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 14,
                    backgroundColor: AppTheme.primary.withOpacity(0.2),
                    child: Text(
                      psi.nombre.isNotEmpty ? psi.nombre[0].toUpperCase() : 'T',
                      style: const TextStyle(fontSize: 12, color: AppTheme.primaryLight, fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          psi.nombreCompleto,
                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                          overflow: TextOverflow.ellipsis,
                        ),
                        Text(
                          '${psi.especialidades.isNotEmpty ? psi.especialidades.join(", ") : "Psicología General"} • Bs. ${psi.tarifaBase.toStringAsFixed(0)}',
                          style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
          onChanged: (val) {
            if (val != null && val != _selectedPsicologo) {
              setState(() => _selectedPsicologo = val);
              _cargarSlots();
            }
          },
        ),
      ),
    );
  }

  Widget _buildModalidadToggle() {
    return Row(
      children: [
        Expanded(
          child: InkWell(
            onTap: () => setState(() => _modalidad = 'PRESENCIAL'),
            borderRadius: BorderRadius.circular(14),
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
              decoration: BoxDecoration(
                color: _modalidad == 'PRESENCIAL' ? AppTheme.primary.withOpacity(0.2) : AppTheme.cardBg,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: _modalidad == 'PRESENCIAL' ? AppTheme.primary : AppTheme.borderSubtle,
                  width: _modalidad == 'PRESENCIAL' ? 1.8 : 1,
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.location_on_outlined,
                    size: 18,
                    color: _modalidad == 'PRESENCIAL' ? AppTheme.primaryLight : AppTheme.textMuted,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Presencial',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                      color: _modalidad == 'PRESENCIAL' ? AppTheme.textMain : AppTheme.textMuted,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: InkWell(
            onTap: () => setState(() => _modalidad = 'VIRTUAL'),
            borderRadius: BorderRadius.circular(14),
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
              decoration: BoxDecoration(
                color: _modalidad == 'VIRTUAL' ? AppTheme.secondary.withOpacity(0.2) : AppTheme.cardBg,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: _modalidad == 'VIRTUAL' ? AppTheme.secondary : AppTheme.borderSubtle,
                  width: _modalidad == 'VIRTUAL' ? 1.8 : 1,
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.videocam_outlined,
                    size: 18,
                    color: _modalidad == 'VIRTUAL' ? const Color(0xFFA5B4FC) : AppTheme.textMuted,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Teleconsulta',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                      color: _modalidad == 'VIRTUAL' ? AppTheme.textMain : AppTheme.textMuted,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDateSelector(String fechaTexto) {
    return InkWell(
      onTap: _pickDate,
      borderRadius: BorderRadius.circular(14),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppTheme.cardBg,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppTheme.borderSubtle),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppTheme.primary.withOpacity(0.15),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.calendar_today_rounded, color: AppTheme.primaryLight, size: 20),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Fecha seleccionada', style: TextStyle(fontSize: 11, color: AppTheme.textSubtle)),
                  const SizedBox(height: 2),
                  Text(
                    DateFormat('dd/MM/yyyy').format(_selectedDate),
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: AppTheme.inputBg,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: const Text('Cambiar', style: TextStyle(fontSize: 11, color: AppTheme.primaryLight, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSlotsGrid() {
    if (_isLoadingSlots) {
      return Container(
        padding: const EdgeInsets.all(24),
        alignment: Alignment.center,
        child: const Column(
          children: [
            CircularProgressIndicator(strokeWidth: 2),
            SizedBox(height: 8),
            Text('Consultando disponibilidad en tiempo real...', style: TextStyle(color: AppTheme.textMuted, fontSize: 12)),
          ],
        ),
      );
    }

    if (_slotsDisponibles.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppTheme.cardBg,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppTheme.borderSubtle),
        ),
        child: const Column(
          children: [
            Icon(Icons.event_busy_outlined, color: AppTheme.warning, size: 28),
            SizedBox(height: 8),
            Text(
              'No hay horarios disponibles para esta fecha.',
              textAlign: TextAlign.center,
              style: TextStyle(color: AppTheme.textMuted, fontSize: 13),
            ),
            SizedBox(height: 4),
            Text(
              'Intenta seleccionando otro día o terapeuta.',
              style: TextStyle(color: AppTheme.textSubtle, fontSize: 11),
            ),
          ],
        ),
      );
    }

    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: _slotsDisponibles.map((slot) {
        final isSelected = _selectedSlot == slot;
        return InkWell(
          onTap: () => setState(() => _selectedSlot = slot),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: isSelected ? AppTheme.primary : AppTheme.cardBg,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isSelected ? AppTheme.primaryLight : AppTheme.borderSubtle,
                width: isSelected ? 1.5 : 1,
              ),
              boxShadow: isSelected
                  ? [BoxShadow(color: AppTheme.primary.withOpacity(0.4), blurRadius: 8, offset: const Offset(0, 3))]
                  : null,
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.access_time_rounded,
                  size: 14,
                  color: isSelected ? Colors.white : AppTheme.primaryLight,
                ),
                const SizedBox(width: 6),
                Text(
                  slot,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                    color: isSelected ? Colors.white : AppTheme.textMain,
                  ),
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }
}
