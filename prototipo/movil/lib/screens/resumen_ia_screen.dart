import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../services/auth_service.dart';
import '../services/sprint4_service.dart';

class ResumenIaScreen extends StatefulWidget {
  final AuthService authService;
  const ResumenIaScreen({super.key, required this.authService});

  @override
  State<ResumenIaScreen> createState() => _ResumenIaScreenState();
}

class _ResumenIaScreenState extends State<ResumenIaScreen> {
  late final Sprint4Service _svc;
  bool _cargando = true;
  bool _generando = false;
  String? _error;
  List<Map<String, dynamic>> _pacientes = [];
  String? _pacienteId;
  Map<String, dynamic>? _resumenActivo;
  final TextEditingController _textoCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _svc = Sprint4Service(authService: widget.authService);
    _cargarPacientes();
  }

  @override
  void dispose() {
    _textoCtrl.dispose();
    super.dispose();
  }

  Future<void> _cargarPacientes() async {
    setState(() => _cargando = true);
    final rows = await _svc.listarPacientes();
    if (!mounted) return;
    setState(() {
      _pacientes = rows;
      _pacienteId = rows.isNotEmpty ? rows.first['id'].toString() : null;
      _cargando = false;
    });
    if (_pacienteId != null) _cargarResumenes(_pacienteId!);
  }

  Future<void> _cargarResumenes(String pacId) async {
    setState(() => _error = null);
    try {
      final rows = await _svc.listarResumenesIA(pacId);
      if (!mounted) return;
      setState(() {
        _resumenActivo = rows.isNotEmpty ? rows.first : null;
        _textoCtrl.text = (_resumenActivo?['texto_resumen'] ?? '').toString();
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _resumenActivo = null;
        _textoCtrl.clear();
        _error = e.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  Future<void> _generar() async {
    if (_pacienteId == null) return;
    // CU23-paso 1, 16: Solicita resumen clínico IA longitudinal y despliega borrador editable
    setState(() {
      _generando = true;
      _error = null;
    });
    final res = await _svc.generarResumenIA(_pacienteId!);
    if (!mounted) return;
    setState(() => _generando = false);
    if (res['success'] == true) {
      setState(() {
        _resumenActivo = Map<String, dynamic>.from(res['data']);
        _textoCtrl.text = (_resumenActivo?['texto_resumen'] ?? '').toString();
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Borrador IA generado con SHA-256. Revise y apruebe (HITL).'), backgroundColor: AppTheme.success),
      );
    } else {
      setState(() => _error = res['error'].toString());
    }
  }

  Future<void> _aprobarHitl() async {
    if (_resumenActivo == null) return;
    // CU23-paso 17, 22: Valida texto editado y confirma aprobación HITL
    final res = await _svc.aprobarResumenHITL(_resumenActivo!['id'].toString(), _textoCtrl.text);
    if (!mounted) return;
    if (res['success'] == true) {
      setState(() => _resumenActivo = Map<String, dynamic>.from(res['data']));
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Resumen aprobado (HITL) y auditado.'), backgroundColor: AppTheme.success),
      );
    } else {
      setState(() => _error = res['error'].toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final r = _resumenActivo;
    final aprobado = r?['estado'] == 'APROBADO_HITL';

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(title: const Text('Resumen Clínico IA (HITL)')),
      body: _cargando
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(14),
              children: [
                if (_pacientes.isNotEmpty)
                  DropdownButtonFormField<String>(
                    value: _pacienteId,
                    dropdownColor: AppTheme.cardBgElevated,
                    decoration: const InputDecoration(labelText: 'Seleccionar Paciente'),
                    items: _pacientes.map((p) {
                      final u = p['usuario'] is Map ? p['usuario'] : {};
                      final nom = '${u['nombre'] ?? ''} ${u['apellido'] ?? ''}'.trim();
                      return DropdownMenuItem(
                        value: p['id'].toString(),
                        child: Text('${p['codigo_expediente']} — ${nom.isEmpty ? p['id'] : nom}'),
                      );
                    }).toList(),
                    onChanged: (v) {
                      if (v == null) return;
                      setState(() => _pacienteId = v);
                      _cargarResumenes(v);
                    },
                  ),
                const SizedBox(height: 12),
                ElevatedButton.icon(
                  onPressed: _generando ? null : _generar,
                  icon: _generando
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.auto_awesome_rounded),
                  label: Text(_generando ? 'Generando borrador...' : 'Generar Borrador IA Longitudinal'),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppTheme.danger.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(_error!, style: const TextStyle(color: AppTheme.danger, fontSize: 12)),
                  ),
                ],
                if (r != null) ...[
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: (aprobado ? AppTheme.success : AppTheme.warning).withOpacity(0.18),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: aprobado ? AppTheme.success : AppTheme.warning),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          aprobado ? 'Aprobado por Profesional (HITL)' : '${r['etiqueta_cumplimiento']}',
                          style: TextStyle(
                            color: aprobado ? AppTheme.success : AppTheme.warning,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text('Modelo: ${r['fuente_modelo']} • SHA-256: ${(r['hash_sha256'] ?? '').toString().substring(0, 14)}...',
                            style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _textoCtrl,
                    maxLines: 12,
                    style: const TextStyle(color: AppTheme.textMain, fontSize: 13),
                    decoration: const InputDecoration(labelText: 'Resumen Longitudinal (Editable antes de Aprobar HITL)'),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primary),
                    onPressed: _aprobarHitl,
                    icon: const Icon(Icons.verified_outlined),
                    label: const Text('Editar y Aprobar (HITL)'),
                  ),
                ],
              ],
            ),
    );
  }
}
