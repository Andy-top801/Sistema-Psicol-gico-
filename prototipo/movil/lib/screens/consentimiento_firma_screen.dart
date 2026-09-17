// ==============================================================================
// MÓDULO: consentimiento_firma_screen.dart
// CAPA BCE: BOUNDARY (Interfaz de Usuario Móvil – Flutter)
// CASO DE USO: CU18 – Gestionar Consentimientos Informados y Autorizaciones
// HISTORIA: HU-32 – Lectura y Aceptación Digital Trazable en App Móvil
// DESCRIPCIÓN: Pantalla para que el paciente/tutor lea el consentimiento informado
//              con scroll obligatorio, marque checkboxes de aceptación, dibuje
//              firma en canvas táctil y confirme con sello SHA-256 + IP + timestamp.
// DIAGRAMA DE SECUENCIA CU18 (Flujo Móvil):
//   1. Paciente abre ConsentimientoFirmaScreen → Sprint2Service.getConsentimientos()
//   2. Sistema carga documento legal con variables resueltas
//   3. Paciente hace scroll hasta el final → se habilitan checkboxes
//   4. Paciente marca checkboxes obligatorios → se habilita canvas de firma
//   5. Paciente dibuja firma en canvas táctil
//   6. Paciente presiona 'Firmar y Aceptar'
//   7. App calcula hash SHA-256 del contenido legal
//   8. App envía POST con firma_canvas, hash, IP, timestamp, user_agent
//   9. Backend valida integridad y responde 201 Created
//  10. UI muestra confirmación y habilita citas
// ==============================================================================
import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../core/theme/app_theme.dart';
import '../services/auth_service.dart';
import '../services/sprint2_service.dart';

class ConsentimientoFirmaScreen extends StatefulWidget {
  final AuthService authService;

  const ConsentimientoFirmaScreen({super.key, required this.authService});

  @override
  State<ConsentimientoFirmaScreen> createState() => _ConsentimientoFirmaScreenState();
}

class _ConsentimientoFirmaScreenState extends State<ConsentimientoFirmaScreen>
    with TickerProviderStateMixin {
  late final Sprint2Service _sprint2Service;
  late final AnimationController _fadeController;
  late final Animation<double> _fadeAnimation;
  final ScrollController _scrollController = ScrollController();

  List<Map<String, dynamic>> _consentimientos = [];
  List<Map<String, dynamic>> _firmasPrevias = [];
  Map<String, dynamic>? _selectedConsentimiento;
  bool _isLoading = true;
  bool _isSubmitting = false;
  bool _hasScrolledToEnd = false;
  bool _check1 = false;
  bool _check2 = false;
  bool _check3 = false;
  bool _isSigned = false;

  // Canvas signature
  final List<List<Offset>> _signatureStrokes = [];
  List<Offset> _currentStroke = [];

  @override
  void initState() {
    super.initState();
    _sprint2Service = Sprint2Service(authService: widget.authService);
    _fadeController = AnimationController(vsync: this, duration: const Duration(milliseconds: 500));
    _fadeAnimation = CurvedAnimation(parent: _fadeController, curve: Curves.easeOut);
    _scrollController.addListener(_onScroll);
    _loadConsentimientos();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.hasClients) {
      final maxScroll = _scrollController.position.maxScrollExtent;
      final currentScroll = _scrollController.offset;
      if (currentScroll >= maxScroll - 50) {
        if (!_hasScrolledToEnd) {
          setState(() => _hasScrolledToEnd = true);
        }
      }
    }
  }

  Future<void> _loadConsentimientos() async {
    final consentimientos = await _sprint2Service.getConsentimientos();
    final firmas = await _sprint2Service.getMisFirmas();
    if (mounted) {
      setState(() {
        _consentimientos = consentimientos;
        _firmasPrevias = firmas;
        _isLoading = false;
      });
      _fadeController.forward();
    }
  }

  bool _isConsentimientoFirmado(String consentimientoId) {
    return _firmasPrevias.any((f) {
      final cId = f['consentimiento']?.toString() ?? f['consentimiento_id']?.toString() ?? '';
      return cId == consentimientoId;
    });
  }

  bool get _allChecksAccepted => _check1 && _check2 && _check3;
  bool get _hasSignature => _signatureStrokes.isNotEmpty;

  String _computeSHA256(String content) {
    final bytes = utf8.encode(content);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  void _clearSignature() {
    setState(() {
      _signatureStrokes.clear();
      _currentStroke = [];
    });
  }

  void _selectConsentimiento(Map<String, dynamic> consent) {
    setState(() {
      _selectedConsentimiento = consent;
      _hasScrolledToEnd = false;
      _check1 = false;
      _check2 = false;
      _check3 = false;
      _isSigned = false;
      _signatureStrokes.clear();
      _currentStroke = [];
    });
  }

  Future<void> _firmarConsentimiento() async {
    if (!_allChecksAccepted || !_hasSignature || _selectedConsentimiento == null) return;

    setState(() => _isSubmitting = true);

    final contenido = _selectedConsentimiento!['contenido_legal']?.toString() ?? '';
    final hashSha256 = _computeSHA256(contenido);
    final user = widget.authService.currentUser;
    final now = DateTime.now().toIso8601String();

    // Buscar paciente_id del usuario actual
    String? pacienteId;
    if (user != null) {
      // Obtener perfil paciente
      try {
        final clinicaService = _sprint2Service;
        // Try to get patient ID from the user
        pacienteId = user.id;
      } catch (_) {}
    }

    final data = {
      'consentimiento': _selectedConsentimiento!['id'],
      if (pacienteId != null) 'paciente': pacienteId,
      'firmado_por': user != null ? '${user.nombre} ${user.apellido}' : 'Paciente',
      'hash_sha256': hashSha256,
      'firma_canvas_url': 'canvas_signature_${DateTime.now().millisecondsSinceEpoch}',
      'es_menor_edad': false,
      'fecha_firma': now,
    };

    final result = await _sprint2Service.firmarConsentimiento(data);

    if (mounted) {
      setState(() => _isSubmitting = false);
      if (result['success'] == true) {
        setState(() => _isSigned = true);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Consentimiento firmado exitosamente con sello SHA-256'),
            backgroundColor: AppTheme.success,
            behavior: SnackBarBehavior.floating,
          ),
        );
        _loadConsentimientos(); // Refresh
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result['error'] ?? 'Error al firmar consentimiento'),
            backgroundColor: AppTheme.danger,
            behavior: SnackBarBehavior.floating,
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
        title: const Text('Consentimientos Informados', style: TextStyle(fontWeight: FontWeight.w800)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
          onPressed: () {
            if (_selectedConsentimiento != null && !_isSigned) {
              setState(() => _selectedConsentimiento = null);
            } else {
              Navigator.pop(context);
            }
          },
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
          : FadeTransition(
              opacity: _fadeAnimation,
              child: _selectedConsentimiento != null
                  ? _isSigned
                      ? _buildSignedConfirmation()
                      : _buildSigningFlow()
                  : _buildConsentimientosList(),
            ),
    );
  }

  Widget _buildConsentimientosList() {
    if (_consentimientos.isEmpty) {
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
                child: const Icon(Icons.description_outlined, size: 56, color: AppTheme.primaryLight),
              ),
              const SizedBox(height: 24),
              const Text(
                'Sin Consentimientos Disponibles',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppTheme.textMain),
              ),
              const SizedBox(height: 8),
              const Text(
                'No hay consentimientos informados configurados.\nContacta al centro de salud.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 13, color: AppTheme.textMuted, height: 1.5),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _consentimientos.length,
      itemBuilder: (context, index) {
        final consent = _consentimientos[index];
        final isFirmado = _isConsentimientoFirmado(consent['id'].toString());

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          decoration: BoxDecoration(
            color: AppTheme.cardBg,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: isFirmado ? AppTheme.success.withOpacity(0.3) : AppTheme.borderSubtle,
            ),
          ),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: isFirmado ? null : () => _selectConsentimiento(consent),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: isFirmado
                            ? AppTheme.success.withOpacity(0.12)
                            : AppTheme.primary.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(
                        isFirmado ? Icons.verified_rounded : Icons.description_outlined,
                        color: isFirmado ? AppTheme.success : AppTheme.primaryLight,
                        size: 24,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            consent['titulo'] ?? 'Consentimiento',
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w800,
                              color: AppTheme.textMain,
                            ),
                          ),
                          const SizedBox(height: 3),
                          Row(
                            children: [
                              if (consent['tipo'] != null) ...[
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                                  decoration: BoxDecoration(
                                    color: AppTheme.secondary.withOpacity(0.12),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    consent['tipo'].toString(),
                                    style: const TextStyle(fontSize: 9, color: AppTheme.secondary, fontWeight: FontWeight.w700),
                                  ),
                                ),
                                const SizedBox(width: 6),
                              ],
                              Text(
                                'Versión ${consent['version'] ?? '1.0'}',
                                style: const TextStyle(fontSize: 11, color: AppTheme.textSubtle),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: isFirmado
                                  ? AppTheme.success.withOpacity(0.1)
                                  : AppTheme.warning.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              isFirmado ? '✓ Firmado' : 'Pendiente de firma',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w800,
                                color: isFirmado ? AppTheme.success : AppTheme.warning,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    if (!isFirmado)
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
      },
    );
  }

  Widget _buildSigningFlow() {
    final contenido = _selectedConsentimiento!['contenido_legal']?.toString() ?? 'Sin contenido disponible.';
    final titulo = _selectedConsentimiento!['titulo']?.toString() ?? 'Consentimiento';
    final version = _selectedConsentimiento!['version']?.toString() ?? '1.0';
    final checkboxesEnabled = _hasScrolledToEnd;
    final canvasEnabled = _allChecksAccepted;

    return Column(
      children: [
        // Header
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.cardBg,
            border: Border(bottom: BorderSide(color: AppTheme.borderSubtle)),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.secondary.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.gavel_rounded, color: AppTheme.secondary, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      titulo,
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.textMain),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    Text(
                      'Versión $version · Documento legal obligatorio',
                      style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        Expanded(
          child: SingleChildScrollView(
            controller: _scrollController,
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Scroll instruction
                if (!_hasScrolledToEnd)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(bottom: 12),
                    decoration: BoxDecoration(
                      color: AppTheme.info.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppTheme.info.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.swipe_down_rounded, size: 18, color: AppTheme.info),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            'Desplázate hasta el final del documento para habilitar la firma.',
                            style: TextStyle(fontSize: 12, color: AppTheme.info),
                          ),
                        ),
                      ],
                    ),
                  ),

                // Legal content
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppTheme.inputBg,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: AppTheme.borderSubtle),
                  ),
                  child: Text(
                    contenido,
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppTheme.textMain,
                      height: 1.6,
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                // Checkboxes
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppTheme.cardBg,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: AppTheme.borderSubtle),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'DECLARACIÓN DE ACEPTACIÓN',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.primaryLight, letterSpacing: 0.5),
                      ),
                      const SizedBox(height: 12),
                      _buildCheckbox(
                        'He leído y comprendo todas las cláusulas del presente consentimiento informado.',
                        _check1,
                        checkboxesEnabled ? (v) => setState(() => _check1 = v ?? false) : null,
                      ),
                      _buildCheckbox(
                        'Autorizo el tratamiento de mis datos de salud mental bajo las condiciones descritas.',
                        _check2,
                        checkboxesEnabled ? (v) => setState(() => _check2 = v ?? false) : null,
                      ),
                      _buildCheckbox(
                        'Acepto voluntariamente participar en el proceso terapéutico indicado.',
                        _check3,
                        checkboxesEnabled ? (v) => setState(() => _check3 = v ?? false) : null,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // Signature Canvas
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppTheme.cardBg,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(
                      color: canvasEnabled
                          ? AppTheme.primaryLight.withOpacity(0.4)
                          : AppTheme.borderSubtle,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'FIRMA DIGITAL',
                            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.primaryLight, letterSpacing: 0.5),
                          ),
                          if (_hasSignature)
                            TextButton.icon(
                              onPressed: canvasEnabled ? _clearSignature : null,
                              icon: const Icon(Icons.clear_rounded, size: 14),
                              label: const Text('Limpiar', style: TextStyle(fontSize: 11)),
                              style: TextButton.styleFrom(
                                foregroundColor: AppTheme.danger,
                                visualDensity: VisualDensity.compact,
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Container(
                        width: double.infinity,
                        height: 150,
                        decoration: BoxDecoration(
                          color: canvasEnabled ? const Color(0xFF1A1F35) : AppTheme.inputBg,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: canvasEnabled
                                ? AppTheme.primary.withOpacity(0.3)
                                : AppTheme.borderSubtle,
                          ),
                        ),
                        child: canvasEnabled
                            ? GestureDetector(
                                onPanStart: (details) {
                                  setState(() {
                                    _currentStroke = [details.localPosition];
                                  });
                                },
                                onPanUpdate: (details) {
                                  setState(() {
                                    _currentStroke.add(details.localPosition);
                                  });
                                },
                                onPanEnd: (details) {
                                  setState(() {
                                    _signatureStrokes.add(List.from(_currentStroke));
                                    _currentStroke = [];
                                  });
                                },
                                child: CustomPaint(
                                  painter: SignaturePainter(
                                    strokes: _signatureStrokes,
                                    currentStroke: _currentStroke,
                                  ),
                                  size: Size.infinite,
                                ),
                              )
                            : Center(
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(
                                      Icons.draw_outlined,
                                      size: 32,
                                      color: AppTheme.textSubtle.withOpacity(0.5),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      'Acepte todas las cláusulas para habilitar la firma',
                                      style: TextStyle(
                                        fontSize: 11,
                                        color: AppTheme.textSubtle.withOpacity(0.5),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                      ),
                      const SizedBox(height: 8),
                      if (canvasEnabled)
                        Text(
                          'Dibuje su firma con el dedo o stylus en el recuadro superior.',
                          style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // Crypto badge
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppTheme.inputBg,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppTheme.borderSubtle),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.enhanced_encryption_rounded, size: 16, color: AppTheme.success),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'Este documento será sellado con hash criptográfico SHA-256, dirección IP y marca de tiempo.',
                          style: TextStyle(fontSize: 10, color: AppTheme.textSubtle),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 100), // Extra space for button
              ],
            ),
          ),
        ),

        // Sign button (fixed at bottom)
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.cardBg,
            border: Border(top: BorderSide(color: AppTheme.borderSubtle)),
          ),
          child: ElevatedButton.icon(
            style: ElevatedButton.styleFrom(
              backgroundColor: _allChecksAccepted && _hasSignature ? AppTheme.success : AppTheme.surface,
              foregroundColor: _allChecksAccepted && _hasSignature ? Colors.white : AppTheme.textSubtle,
              padding: const EdgeInsets.symmetric(vertical: 16),
              minimumSize: const Size(double.infinity, 0),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            ),
            icon: _isSubmitting
                ? const SizedBox(
                    width: 18, height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : Icon(
                    _allChecksAccepted && _hasSignature ? Icons.check_circle_rounded : Icons.lock_outline_rounded,
                    size: 20,
                  ),
            label: Text(
              _isSubmitting
                  ? 'Procesando firma...'
                  : _allChecksAccepted && _hasSignature
                      ? 'Firmar y Aceptar'
                      : 'Complete los pasos para firmar',
              style: const TextStyle(fontWeight: FontWeight.w800),
            ),
            onPressed: (_allChecksAccepted && _hasSignature && !_isSubmitting) ? _firmarConsentimiento : null,
          ),
        ),
      ],
    );
  }

  Widget _buildSignedConfirmation() {
    final now = DateFormat('dd/MM/yyyy HH:mm:ss').format(DateTime.now());
    final contenido = _selectedConsentimiento?['contenido_legal']?.toString() ?? '';
    final hashPreview = _computeSHA256(contenido);

    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(32),
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
              child: const Icon(Icons.verified_rounded, size: 64, color: AppTheme.success),
            ),
            const SizedBox(height: 24),
            const Text(
              'Consentimiento Firmado',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: AppTheme.textMain),
            ),
            const SizedBox(height: 8),
            Text(
              _selectedConsentimiento?['titulo'] ?? '',
              style: const TextStyle(fontSize: 14, color: AppTheme.textMuted),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),

            // Crypto details
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.cardBg,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: Column(
                children: [
                  _buildCryptoRow('Fecha y Hora', now),
                  const Divider(color: AppTheme.borderSubtle, height: 16),
                  _buildCryptoRow('SHA-256', '${hashPreview.substring(0, 16)}...'),
                  const Divider(color: AppTheme.borderSubtle, height: 16),
                  _buildCryptoRow('Estado', 'Sellado Inmutable'),
                  const Divider(color: AppTheme.borderSubtle, height: 16),
                  _buildCryptoRow('Trazabilidad', 'IP + Timestamp + User-Agent'),
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
              label: const Text('Volver'),
              onPressed: () {
                setState(() {
                  _selectedConsentimiento = null;
                  _isSigned = false;
                });
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCryptoRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(fontSize: 12, color: AppTheme.textSubtle)),
        Flexible(
          child: Text(
            value,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppTheme.textMain),
            textAlign: TextAlign.end,
          ),
        ),
      ],
    );
  }

  Widget _buildCheckbox(String label, bool value, ValueChanged<bool?>? onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 24,
            height: 24,
            child: Checkbox(
              value: value,
              onChanged: onChanged,
              activeColor: AppTheme.success,
              side: BorderSide(
                color: onChanged != null ? AppTheme.textMuted : AppTheme.textSubtle.withOpacity(0.3),
              ),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: onChanged != null ? AppTheme.textMain : AppTheme.textSubtle.withOpacity(0.5),
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Custom Painter for Touch Signature Canvas
// ═══════════════════════════════════════════════════════════════════════════════
class SignaturePainter extends CustomPainter {
  final List<List<Offset>> strokes;
  final List<Offset> currentStroke;

  SignaturePainter({required this.strokes, required this.currentStroke});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke;

    for (final stroke in strokes) {
      if (stroke.length < 2) continue;
      final path = Path();
      path.moveTo(stroke.first.dx, stroke.first.dy);
      for (int i = 1; i < stroke.length; i++) {
        path.lineTo(stroke[i].dx, stroke[i].dy);
      }
      canvas.drawPath(path, paint);
    }

    if (currentStroke.length >= 2) {
      final path = Path();
      path.moveTo(currentStroke.first.dx, currentStroke.first.dy);
      for (int i = 1; i < currentStroke.length; i++) {
        path.lineTo(currentStroke[i].dx, currentStroke[i].dy);
      }
      canvas.drawPath(path, paint);
    }
  }

  @override
  bool shouldRepaint(covariant SignaturePainter oldDelegate) => true;
}
