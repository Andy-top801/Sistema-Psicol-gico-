import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../services/auth_service.dart';
import '../services/clinica_service.dart';
import '../services/sprint4_service.dart';
import '../models/psicologo_model.dart';

class LiquidacionesScreen extends StatefulWidget {
  final AuthService authService;
  const LiquidacionesScreen({super.key, required this.authService});

  @override
  State<LiquidacionesScreen> createState() => _LiquidacionesScreenState();
}

class _LiquidacionesScreenState extends State<LiquidacionesScreen> {
  late final Sprint4Service _svc;
  late final ClinicaService _clinicaSvc;

  bool _cargando = true;
  String? _error;
  List<Map<String, dynamic>> _liquidaciones = [];
  List<PsicologoModel> _psicologos = [];

  bool get _esAdmin => widget.authService.isAdminCentro || widget.authService.isSuperAdmin;

  @override
  void initState() {
    super.initState();
    _svc = Sprint4Service(authService: widget.authService);
    _clinicaSvc = ClinicaService(authService: widget.authService);
    _cargar();
  }

  Future<void> _cargar() async {
    setState(() {
      _cargando = true;
      _error = null;
    });
    try {
      final rows = await _svc.getLiquidaciones();
      List<PsicologoModel> ps = [];
      if (_esAdmin) {
        ps = await _clinicaSvc.getPsicologos();
      }
      if (!mounted) return;
      setState(() {
        _liquidaciones = rows;
        _psicologos = ps;
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

  void _abrirGenerarDialog() {
    if (_psicologos.isEmpty) return;
    String psicoId = _psicologos.first.id;
    final hoy = DateTime.now();
    final inicioMes = DateTime(hoy.year, hoy.month, 1);
    final fmt = (DateTime d) => '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
    final fIniCtrl = TextEditingController(text: fmt(inicioMes));
    final fFinCtrl = TextEditingController(text: fmt(hoy));
    final pctCtrl = TextEditingController(text: '30');

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDlg) => AlertDialog(
          backgroundColor: AppTheme.cardBg,
          title: const Text('Generar Liquidación (Bs.)', style: TextStyle(color: AppTheme.textMain, fontSize: 16)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  value: psicoId,
                  dropdownColor: AppTheme.cardBgElevated,
                  decoration: const InputDecoration(labelText: 'Psicólogo'),
                  items: _psicologos
                      .map((p) => DropdownMenuItem(value: p.id, child: Text(p.nombreCompleto)))
                      .toList(),
                  onChanged: (v) => setDlg(() => psicoId = v ?? psicoId),
                ),
                const SizedBox(height: 8),
                TextField(controller: fIniCtrl, decoration: const InputDecoration(labelText: 'Desde (YYYY-MM-DD)')),
                const SizedBox(height: 8),
                TextField(controller: fFinCtrl, decoration: const InputDecoration(labelText: 'Hasta (YYYY-MM-DD)')),
                const SizedBox(height: 8),
                TextField(
                  controller: pctCtrl,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Comisión Centro (%)'),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(ctx);
                final res = await _svc.generarLiquidacion(
                  psicologoId: psicoId,
                  fechaInicio: fIniCtrl.text.trim(),
                  fechaFin: fFinCtrl.text.trim(),
                  porcentajeComision: double.tryParse(pctCtrl.text.trim()) ?? 30.0,
                );
                if (!mounted) return;
                if (res['success'] == true) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Liquidación emitida correctamente.'), backgroundColor: AppTheme.success),
                  );
                  _cargar();
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(res['error'].toString()), backgroundColor: AppTheme.danger),
                  );
                }
              },
              child: const Text('Emitir'),
            ),
          ],
        ),
      ),
    );
  }

  void _marcarPagada(Map<String, dynamic> liq) {
    final refCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardBg,
        title: Text('Pagar ${liq['codigo_liquidacion']}', style: const TextStyle(color: AppTheme.textMain, fontSize: 16)),
        content: TextField(
          controller: refCtrl,
          decoration: const InputDecoration(labelText: 'Referencia Bancaria / Comprobante'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              final res = await _svc.pagarLiquidacion(liq['id'].toString(), refCtrl.text.trim());
              if (!mounted) return;
              if (res['success'] == true) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Liquidación marcada como PAGADA.'), backgroundColor: AppTheme.success),
                );
                _cargar();
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(res['error'].toString()), backgroundColor: AppTheme.danger),
                );
              }
            },
            child: const Text('Confirmar Pago'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(title: const Text('Liquidación de Honorarios (Bs.)')),
      floatingActionButton: _esAdmin
          ? FloatingActionButton.extended(
              backgroundColor: AppTheme.primaryLight,
              foregroundColor: AppTheme.secondary,
              onPressed: _abrirGenerarDialog,
              icon: const Icon(Icons.add_card_rounded),
              label: const Text('Nueva Liquidación'),
            )
          : null,
      body: _cargando
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: AppTheme.danger)))
              : RefreshIndicator(
                  onRefresh: _cargar,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(14),
                    itemCount: _liquidaciones.length,
                    itemBuilder: (_, i) {
                      final l = _liquidaciones[i];
                      final pagada = l['estado'] == 'PAGADA';
                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.all(12),
                        decoration: AppTheme.glassDecoration(radius: 12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text('${l['codigo_liquidacion']}',
                                    style: const TextStyle(color: AppTheme.primaryLight, fontWeight: FontWeight.bold)),
                                Chip(
                                  label: Text('${l['estado']}', style: const TextStyle(fontSize: 11)),
                                  backgroundColor: pagada ? AppTheme.success.withOpacity(0.25) : AppTheme.warning.withOpacity(0.25),
                                ),
                              ],
                            ),
                            Text('${l['psicologo_nombre']} • ${l['total_sesiones']} sesiones',
                                style: const TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.w600)),
                            Text('Periodo: ${l['fecha_inicio']} al ${l['fecha_fin']}',
                                style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                            const SizedBox(height: 6),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text('Bruto: Bs. ${l['monto_bruto']}', style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                                Text('Neto: Bs. ${l['monto_neto_psicologo']}',
                                    style: const TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold)),
                              ],
                            ),
                            if (_esAdmin && l['estado'] == 'GENERADA')
                              Align(
                                alignment: Alignment.centerRight,
                                child: TextButton.icon(
                                  onPressed: () => _marcarPagada(l),
                                  icon: const Icon(Icons.check_circle_outline, size: 18),
                                  label: const Text('Marcar Pagada'),
                                ),
                              ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
