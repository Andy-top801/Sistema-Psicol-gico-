import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../services/auth_service.dart';
import '../services/sprint4_service.dart';

class AlertasRiesgoIaScreen extends StatefulWidget {
  final AuthService authService;
  const AlertasRiesgoIaScreen({super.key, required this.authService});

  @override
  State<AlertasRiesgoIaScreen> createState() => _AlertasRiesgoIaScreenState();
}

class _AlertasRiesgoIaScreenState extends State<AlertasRiesgoIaScreen> {
  late final Sprint4Service _svc;
  bool _cargando = true;
  bool _evaluando = false;
  String? _error;
  String _filtroEstado = '';
  String _filtroSeveridad = '';
  Map<String, dynamic> _resumen = {};
  List<Map<String, dynamic>> _alertas = [];

  @override
  void initState() {
    super.initState();
    _svc = Sprint4Service(authService: widget.authService);
    _cargar();
  }

  Future<void> _cargar() async {
    setState(() {
      _cargando = true;
      _error = null;
    });
    try {
      final res = await _svc.listarAlertasRiesgo(
        estado: _filtroEstado.isEmpty ? null : _filtroEstado,
        severidad: _filtroSeveridad.isEmpty ? null : _filtroSeveridad,
      );
      if (!mounted) return;
      setState(() {
        _resumen = Map<String, dynamic>.from(res['resumen'] ?? {});
        _alertas = List<Map<String, dynamic>>.from(res['alertas'] ?? []);
        _cargando = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _cargando = false;
      });
    }
  }

  Future<void> _ejecutarBarrido() async {
    // CU24-paso 1, 15: Lanza evaluación ML sobre historias clínicas activas
    setState(() => _evaluando = true);
    final res = await _svc.evaluarAlertasRiesgo();
    if (!mounted) return;
    setState(() => _evaluando = false);
    if (res['success'] == true) {
      final d = res['data'] ?? {};
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Barrido IA: ${d['pacientes_evaluados']} pacientes, ${d['alertas_activas_actualizadas']} alertas actualizadas.'),
          backgroundColor: AppTheme.success,
        ),
      );
      _cargar();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(res['error'].toString()), backgroundColor: AppTheme.danger),
      );
    }
  }

  void _abrirIntervencion(Map<String, dynamic> alerta) {
    String estado = alerta['estado'] == 'ABIERTA' ? 'EN_ATENCION' : 'RESUELTA';
    final notaCtrl = TextEditingController(text: (alerta['nota_intervencion'] ?? '').toString());

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDlg) => AlertDialog(
          backgroundColor: AppTheme.cardBg,
          title: Text('Intervención — ${alerta['expediente']}',
              style: const TextStyle(color: AppTheme.textMain, fontSize: 16)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('${alerta['explicacion']}', style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                const SizedBox(height: 10),
                DropdownButtonFormField<String>(
                  value: estado,
                  dropdownColor: AppTheme.cardBgElevated,
                  decoration: const InputDecoration(labelText: 'Nuevo Estado'),
                  items: const [
                    DropdownMenuItem(value: 'EN_ATENCION', child: Text('En Atención')),
                    DropdownMenuItem(value: 'RESUELTA', child: Text('Resuelta (Nota obligatoria)')),
                    DropdownMenuItem(value: 'DESCARTADA', child: Text('Descartada (Nota obligatoria)')),
                  ],
                  onChanged: (v) => setDlg(() => estado = v ?? estado),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: notaCtrl,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    labelText: 'Nota de Intervención Clínica',
                    hintText: 'Llamada de contención, derivación o reagendamiento...',
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            ElevatedButton(
              onPressed: () async {
                final res = await _svc.transicionarAlerta(
                  alerta['id'].toString(),
                  estado,
                  notaCtrl.text.trim(),
                );
                if (!mounted) return;
                if (res['success'] == true) {
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Intervención auditada en CE_AuditLog.'), backgroundColor: AppTheme.success),
                  );
                  _cargar();
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(res['error'].toString()), backgroundColor: AppTheme.danger),
                  );
                }
              },
              child: const Text('Guardar'),
            ),
          ],
        ),
      ),
    );
  }

  Color _sevColor(String sev) {
    switch (sev.toUpperCase()) {
      case 'CRITICO':
        return AppTheme.danger;
      case 'ALTO':
        return AppTheme.warning;
      case 'MEDIO':
        return AppTheme.info;
      default:
        return AppTheme.primaryLight;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Alertas de Riesgo IA (CU24)'),
        actions: [
          IconButton(
            icon: _evaluando
                ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.radar_rounded),
            tooltip: 'Ejecutar Barrido IA',
            onPressed: _evaluando ? null : _ejecutarBarrido,
          ),
        ],
      ),
      body: _cargando
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: AppTheme.danger)))
              : RefreshIndicator(
                  onRefresh: _cargar,
                  child: ListView(
                    padding: const EdgeInsets.all(14),
                    children: [
                      Row(
                        children: [
                          _statPill('Críticas', _resumen['criticas_abiertas'] ?? 0, AppTheme.danger),
                          const SizedBox(width: 8),
                          _statPill('Abiertas', _resumen['abiertas'] ?? 0, AppTheme.warning),
                          const SizedBox(width: 8),
                          _statPill('Resueltas', _resumen['resueltas'] ?? 0, AppTheme.success),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Wrap(
                        spacing: 6,
                        children: [
                          ChoiceChip(
                            label: const Text('Todas'),
                            selected: _filtroEstado.isEmpty && _filtroSeveridad.isEmpty,
                            onSelected: (_) {
                              setState(() {
                                _filtroEstado = '';
                                _filtroSeveridad = '';
                              });
                              _cargar();
                            },
                          ),
                          ChoiceChip(
                            label: const Text('Críticas'),
                            selected: _filtroSeveridad == 'CRITICO',
                            onSelected: (_) {
                              setState(() {
                                _filtroEstado = '';
                                _filtroSeveridad = 'CRITICO';
                              });
                              _cargar();
                            },
                          ),
                          ChoiceChip(
                            label: const Text('Abiertas'),
                            selected: _filtroEstado == 'ABIERTA',
                            onSelected: (_) {
                              setState(() {
                                _filtroEstado = 'ABIERTA';
                                _filtroSeveridad = '';
                              });
                              _cargar();
                            },
                          ),
                          ChoiceChip(
                            label: const Text('Resueltas'),
                            selected: _filtroEstado == 'RESUELTA',
                            onSelected: (_) {
                              setState(() {
                                _filtroEstado = 'RESUELTA';
                                _filtroSeveridad = '';
                              });
                              _cargar();
                            },
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      if (_alertas.isEmpty)
                        const Padding(
                          padding: EdgeInsets.all(24),
                          child: Text('No hay alertas para este filtro. Toca el ícono de radar arriba para ejecutar el barrido IA.',
                              textAlign: TextAlign.center, style: TextStyle(color: AppTheme.textMuted)),
                        )
                      else
                        ..._alertas.map((a) {
                          final sev = (a['severidad'] ?? 'MEDIO').toString();
                          final color = _sevColor(sev);
                          final factores = List<Map<String, dynamic>>.from(a['factores_detectados'] ?? []);
                          return Container(
                            margin: const EdgeInsets.only(bottom: 10),
                            padding: const EdgeInsets.all(12),
                            decoration: AppTheme.glassDecoration(radius: 12, borderColor: color.withOpacity(0.5)),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                      decoration: BoxDecoration(
                                        color: color.withOpacity(0.2),
                                        borderRadius: BorderRadius.circular(20),
                                      ),
                                      child: Text('$sev • ${a['score_riesgo']}/100',
                                          style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 11)),
                                    ),
                                    Text('${a['estado']}', style: const TextStyle(color: AppTheme.primaryLight, fontSize: 11, fontWeight: FontWeight.bold)),
                                  ],
                                ),
                                const SizedBox(height: 6),
                                Text('${a['expediente']} — ${a['paciente_nombre']}',
                                    style: const TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.bold)),
                                Text('${a['tipo']} • ${a['explicacion']}',
                                    style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                                if (factores.isNotEmpty) ...[
                                  const SizedBox(height: 6),
                                  Wrap(
                                    spacing: 4,
                                    runSpacing: 4,
                                    children: factores
                                        .map((f) => Chip(
                                              visualDensity: VisualDensity.compact,
                                              label: Text('${f['etiqueta']}', style: const TextStyle(fontSize: 10)),
                                            ))
                                        .toList(),
                                  ),
                                ],
                                Align(
                                  alignment: Alignment.centerRight,
                                  child: TextButton.icon(
                                    onPressed: () => _abrirIntervencion(a),
                                    icon: const Icon(Icons.medical_services_outlined, size: 17),
                                    label: const Text('Intervenir'),
                                  ),
                                ),
                              ],
                            ),
                          );
                        }),
                    ],
                  ),
                ),
    );
  }

  Widget _statPill(String label, dynamic count, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: AppTheme.glassDecoration(radius: 10, borderColor: color.withOpacity(0.4)),
        child: Column(
          children: [
            Text('$count', style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 18)),
            Text(label, style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
          ],
        ),
      ),
    );
  }
}
