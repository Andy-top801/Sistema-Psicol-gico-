// ==============================================================================
// MÓDULO: paciente_perfil_screen.dart
// CAPA BCE: BOUNDARY (Interfaz de Usuario Móvil) — IU_GestionPacientes
// CASOS DE USO: CU7: Gestión de Pacientes Web y Móvil (HU-13, HU-14)
// DESCRIPCIÓN: Pantalla móvil Flutter para visualización y actualización del expediente
//              clínico del paciente, validación de minoría de edad y tutor legal obligatorio.
//              Implementa los pasos 1, 2, 7 y 8 del Diagrama de Comunicación BCE.
// ==============================================================================
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/auth_service.dart';
import '../services/clinica_service.dart';
import '../models/paciente_model.dart';
import '../core/theme/app_theme.dart';

class PacientePerfilScreen extends StatefulWidget {
  final AuthService authService;

  const PacientePerfilScreen({super.key, required this.authService});

  @override
  State<PacientePerfilScreen> createState() => _PacientePerfilScreenState();
}

class _PacientePerfilScreenState extends State<PacientePerfilScreen> {
  late final ClinicaService _clinicaService;
  final _formKey = GlobalKey<FormState>();

  bool _isLoading = true;
  bool _isSaving = false;
  PacienteModel? _paciente;

  // Form Controllers
  final _nombreCtrl = TextEditingController();
  final _apellidoCtrl = TextEditingController();
  final _ciCtrl = TextEditingController();
  final _telefonoCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _fechaNacCtrl = TextEditingController();
  final _emergenciaNombreCtrl = TextEditingController();
  final _emergenciaTelfCtrl = TextEditingController();
  final _tutorNombreCtrl = TextEditingController();
  final _tutorCiCtrl = TextEditingController();

  String _genero = 'M';
  DateTime? _fechaNacimiento;
  int? _edadCalculada;
  bool _esMenorDeEdad = false;

  @override
  void initState() {
    super.initState();
    _clinicaService = ClinicaService(authService: widget.authService);
    _cargarPerfil();
  }

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _apellidoCtrl.dispose();
    _ciCtrl.dispose();
    _telefonoCtrl.dispose();
    _emailCtrl.dispose();
    _fechaNacCtrl.dispose();
    _emergenciaNombreCtrl.dispose();
    _emergenciaTelfCtrl.dispose();
    _tutorNombreCtrl.dispose();
    _tutorCiCtrl.dispose();
    super.dispose();
  }

  Future<void> _cargarPerfil() async {
    setState(() => _isLoading = true);
    final paciente = await _clinicaService.getMiPerfil();
    if (paciente != null) {
      _paciente = paciente;
      _nombreCtrl.text = paciente.nombre;
      _apellidoCtrl.text = paciente.apellido;
      _ciCtrl.text = paciente.ci;
      _telefonoCtrl.text = paciente.telefono;
      _emailCtrl.text = paciente.email;
      _fechaNacCtrl.text = paciente.fechaNacimiento ?? '';
      _emergenciaNombreCtrl.text = paciente.contactoEmergenciaNombre;
      _emergenciaTelfCtrl.text = paciente.contactoEmergenciaTelf;
      _tutorNombreCtrl.text = paciente.tutorLegalNombre;
      _tutorCiCtrl.text = paciente.tutorLegalCi;
      _genero = ['M', 'F', 'O'].contains(paciente.genero) ? paciente.genero : 'M';

      if (paciente.fechaNacimiento != null && paciente.fechaNacimiento!.isNotEmpty) {
        try {
          _fechaNacimiento = DateTime.parse(paciente.fechaNacimiento!);
          _calcularEdad(_fechaNacimiento!);
        } catch (_) {}
      }
    }
    setState(() => _isLoading = false);
  }

  void _calcularEdad(DateTime nac) {
    final hoy = DateTime.now();
    int edad = hoy.year - nac.year;
    if (hoy.month < nac.month || (hoy.month == nac.month && hoy.day < nac.day)) {
      edad--;
    }
    setState(() {
      _edadCalculada = edad;
      _esMenorDeEdad = edad < 18;
    });
  }

  Future<void> _seleccionarFechaNacimiento() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _fechaNacimiento ?? DateTime(2000, 1, 1),
      firstDate: DateTime(1920),
      lastDate: DateTime.now(),
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

    if (picked != null) {
      setState(() {
        _fechaNacimiento = picked;
        _fechaNacCtrl.text = DateFormat('yyyy-MM-dd').format(picked);
        _calcularEdad(picked);
      });
    }
  }

  /// ═══════════════════════════════════════════════════════════════════════════
  /// CU7: Gestión de Pacientes Web y Móvil (HU-13, HU-14)
  /// Diagrama de Comunicación – Pasos del Flujo:
  ///   Actor  → Paciente / Usuario Móvil
  ///   IU     → IU_GestionPacientes (PacientePerfilScreen)
  ///   CTR    → CTR_PacienteService (Django REST - PATCH /api/clinica/pacientes/{id}/)
  ///   CE     → CE_Paciente_y_Expediente (PostgreSQL)
  /// ═══════════════════════════════════════════════════════════════════════════
  Future<void> _guardarPerfil() async {
    // --- Paso 1: Ingresar datos (CI, fecha nac, tutor si menor) en IU_GestionPacientes > ---
    if (!_formKey.currentState!.validate()) return;
    if (_paciente == null) return;

    if (_esMenorDeEdad) {
      if (_tutorNombreCtrl.text.trim().isEmpty || _tutorCiCtrl.text.trim().isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            backgroundColor: AppTheme.danger,
            content: Text('Para menores de edad (< 18 años) es obligatorio registrar el tutor legal y su CI.'),
          ),
        );
        return;
      }
    }

    setState(() => _isSaving = true);

    final datos = {
      'nombre': _nombreCtrl.text.trim(),
      'apellido': _apellidoCtrl.text.trim(),
      'ci': _ciCtrl.text.trim(),
      'telefono': _telefonoCtrl.text.trim(),
      'genero': _genero,
      'fecha_nacimiento': _fechaNacCtrl.text.trim().isNotEmpty ? _fechaNacCtrl.text.trim() : null,
      'contacto_emergencia_nombre': _emergenciaNombreCtrl.text.trim(),
      'contacto_emergencia_telf': _emergenciaTelfCtrl.text.trim(),
      'tutor_legal_nombre': _tutorNombreCtrl.text.trim(),
      'tutor_legal_ci': _tutorCiCtrl.text.trim(),
    };

    // --- Paso 2: PUT/PATCH /api/clinica/pacientes/{id}/ + Header Tenant > ---
    // IU_GestionPacientes envía datos actualizados al CTR_PacienteService
    final res = await _clinicaService.updateMiPerfil(_paciente!.id, datos);

    setState(() => _isSaving = false);

    if (mounted) {
      // --- Paso 7: 200 OK {paciente_id, expediente} < ---
      // CTR_PacienteService confirma la actualización
      if (res['success'] == true) {
        setState(() {
          _paciente = res['paciente'];
        });
        // --- Paso 8: Mostrar 'Expediente clínico actualizado' en IU_GestionPacientes < ---
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            backgroundColor: AppTheme.success,
            content: Row(
              children: [
                Icon(Icons.check_circle_outline, color: Colors.white),
                SizedBox(width: 8),
                Text('Expediente y datos actualizados correctamente.'),
              ],
            ),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: AppTheme.danger,
            content: Text(res['error'] ?? 'Error al guardar los cambios.'),
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
        title: const Text('Mi Perfil y Expediente', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Recargar perfil',
            onPressed: _cargarPerfil,
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _paciente == null
              ? _buildSinExpediente()
              : SafeArea(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(20.0),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // Tarjeta de Identidad Clínica / Expediente
                          _buildHeaderCard(),
                          const SizedBox(height: 20),

                          // Sección: Datos Personales
                          _buildSectionTitle('DATOS PERSONALES', Icons.person_outline_rounded),
                          const SizedBox(height: 12),
                          _buildPersonalFields(),
                          const SizedBox(height: 24),

                          // Sección: Contacto de Emergencia
                          _buildSectionTitle('CONTACTO DE EMERGENCIA', Icons.emergency_outlined),
                          const SizedBox(height: 12),
                          _buildEmergencyFields(),
                          const SizedBox(height: 24),

                          // Sección: Tutor Legal (HU-14: Obligatorio si < 18 años)
                          _buildTutorSection(),
                          const SizedBox(height: 28),

                          // Botón Guardar Cambios
                          ElevatedButton.icon(
                            onPressed: _isSaving ? null : _guardarPerfil,
                            icon: _isSaving
                                ? const SizedBox(
                                    width: 18,
                                    height: 18,
                                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                  )
                                : const Icon(Icons.save_rounded),
                            label: Text(_isSaving ? 'GUARDANDO CAMBIOS...' : 'GUARDAR EXPEDIENTE'),
                          ),
                          const SizedBox(height: 30),
                        ],
                      ),
                    ),
                  ),
                ),
    );
  }

  Widget _buildSinExpediente() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppTheme.warning.withOpacity(0.12),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.folder_off_outlined, color: AppTheme.warning, size: 48),
            ),
            const SizedBox(height: 18),
            const Text(
              'Sin Expediente Clínico',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.textMain),
            ),
            const SizedBox(height: 8),
            const Text(
              'Tu cuenta no tiene aún un expediente de paciente asignado en este centro. Solicita tu registro en la recepción clínica.',
              textAlign: TextAlign.center,
              style: TextStyle(color: AppTheme.textMuted, fontSize: 13),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: _cargarPerfil,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Reintentar'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeaderCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: AppTheme.heroGradient,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: AppTheme.borderSubtle),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(3),
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              gradient: AppTheme.primaryGradient,
            ),
            child: CircleAvatar(
              radius: 30,
              backgroundColor: AppTheme.background,
              child: Text(
                _paciente?.nombre.isNotEmpty == true ? _paciente!.nombre[0].toUpperCase() : 'P',
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.primaryLight),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _paciente?.nombreCompleto ?? 'Paciente',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppTheme.textMain),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    const Icon(Icons.badge_outlined, size: 13, color: AppTheme.primaryLight),
                    const SizedBox(width: 4),
                    Text(
                      'Expediente: ${_paciente?.codigoExpediente ?? "N/D"}',
                      style: const TextStyle(color: AppTheme.primaryLight, fontSize: 12, fontWeight: FontWeight.w700),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: _esMenorDeEdad
                            ? AppTheme.warning.withOpacity(0.18)
                            : AppTheme.success.withOpacity(0.18),
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(
                          color: _esMenorDeEdad
                              ? AppTheme.warning.withOpacity(0.4)
                              : AppTheme.success.withOpacity(0.4),
                        ),
                      ),
                      child: Text(
                        _esMenorDeEdad ? 'MENOR DE EDAD' : 'MAYOR DE EDAD',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w800,
                          color: _esMenorDeEdad ? AppTheme.warning : AppTheme.success,
                        ),
                      ),
                    ),
                    if (_edadCalculada != null) ...[
                      const SizedBox(width: 8),
                      Text(
                        '$_edadCalculada años',
                        style: const TextStyle(color: AppTheme.textMuted, fontSize: 12),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 16, color: AppTheme.primaryLight),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 0.5, color: AppTheme.textMuted),
        ),
      ],
    );
  }

  Widget _buildPersonalFields() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderSubtle),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: _nombreCtrl,
                  decoration: const InputDecoration(labelText: 'Nombre *', prefixIcon: Icon(Icons.person_outline)),
                  validator: (v) => v == null || v.trim().isEmpty ? 'Requerido' : null,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextFormField(
                  controller: _apellidoCtrl,
                  decoration: const InputDecoration(labelText: 'Apellido', prefixIcon: Icon(Icons.badge_outlined)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: _ciCtrl,
                  decoration: const InputDecoration(labelText: 'Documento CI *', prefixIcon: Icon(Icons.credit_card_outlined)),
                  validator: (v) => v == null || v.trim().isEmpty ? 'Requerido' : null,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextFormField(
                  controller: _telefonoCtrl,
                  decoration: const InputDecoration(labelText: 'Teléfono', prefixIcon: Icon(Icons.phone_outlined)),
                  keyboardType: TextInputType.phone,
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          InkWell(
            onTap: _seleccionarFechaNacimiento,
            borderRadius: BorderRadius.circular(14),
            child: IgnorePointer(
              child: TextFormField(
                controller: _fechaNacCtrl,
                decoration: const InputDecoration(
                  labelText: 'Fecha de Nacimiento *',
                  prefixIcon: Icon(Icons.cake_outlined),
                  suffixIcon: Icon(Icons.calendar_today_rounded, size: 18),
                ),
                validator: (v) => v == null || v.trim().isEmpty ? 'Selecciona una fecha' : null,
              ),
            ),
          ),
          const SizedBox(height: 14),
          // Género Selector
          DropdownButtonFormField<String>(
            value: _genero,
            dropdownColor: AppTheme.cardBg,
            decoration: const InputDecoration(labelText: 'Género', prefixIcon: Icon(Icons.wc_outlined)),
            items: const [
              DropdownMenuItem(value: 'M', child: Text('Masculino')),
              DropdownMenuItem(value: 'F', child: Text('Femenino')),
              DropdownMenuItem(value: 'O', child: Text('Otro / Prefiero no decir')),
            ],
            onChanged: (val) {
              if (val != null) setState(() => _genero = val);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildEmergencyFields() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderSubtle),
      ),
      child: Column(
        children: [
          TextFormField(
            controller: _emergenciaNombreCtrl,
            decoration: const InputDecoration(
              labelText: 'Nombre del Contacto de Emergencia',
              prefixIcon: Icon(Icons.contact_phone_outlined),
            ),
          ),
          const SizedBox(height: 14),
          TextFormField(
            controller: _emergenciaTelfCtrl,
            decoration: const InputDecoration(
              labelText: 'Teléfono del Contacto de Emergencia',
              prefixIcon: Icon(Icons.phone_callback_outlined),
            ),
            keyboardType: TextInputType.phone,
          ),
        ],
      ),
    );
  }

  Widget _buildTutorSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _esMenorDeEdad ? AppTheme.warning.withOpacity(0.08) : AppTheme.cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _esMenorDeEdad ? AppTheme.warning.withOpacity(0.4) : AppTheme.borderSubtle,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.supervisor_account_outlined,
                size: 18,
                color: _esMenorDeEdad ? AppTheme.warning : AppTheme.primaryLight,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  _esMenorDeEdad
                      ? 'TUTOR LEGAL (OBLIGATORIO PARA MENORES)'
                      : 'TUTOR LEGAL (OPCIONAL / MAYORES DE EDAD)',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.3,
                    color: _esMenorDeEdad ? AppTheme.warning : AppTheme.textMuted,
                  ),
                ),
              ),
            ],
          ),
          if (_esMenorDeEdad) ...[
            const SizedBox(height: 6),
            const Text(
              'Según la normativa legal clínica (HU-14), los menores de 18 años requieren los datos y CI de un apoderado.',
              style: TextStyle(fontSize: 11, color: AppTheme.textSubtle),
            ),
          ],
          const SizedBox(height: 14),
          TextFormField(
            controller: _tutorNombreCtrl,
            decoration: InputDecoration(
              labelText: _esMenorDeEdad ? 'Nombre Completo del Tutor *' : 'Nombre del Tutor',
              prefixIcon: const Icon(Icons.person_outline),
            ),
            validator: _esMenorDeEdad
                ? (v) => v == null || v.trim().isEmpty ? 'El nombre del tutor es obligatorio' : null
                : null,
          ),
          const SizedBox(height: 14),
          TextFormField(
            controller: _tutorCiCtrl,
            decoration: InputDecoration(
              labelText: _esMenorDeEdad ? 'Documento CI del Tutor *' : 'CI del Tutor',
              prefixIcon: const Icon(Icons.badge_outlined),
            ),
            validator: _esMenorDeEdad
                ? (v) => v == null || v.trim().isEmpty ? 'El CI del tutor es obligatorio' : null
                : null,
          ),
        ],
      ),
    );
  }
}
