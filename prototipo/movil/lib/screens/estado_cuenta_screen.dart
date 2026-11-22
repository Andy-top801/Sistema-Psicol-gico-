import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../services/auth_service.dart';
import '../services/sprint4_service.dart';

class EstadoCuentaScreen extends StatefulWidget {
  final AuthService authService;
  const EstadoCuentaScreen({super.key, required this.authService});

  @override
  State<EstadoCuentaScreen> createState() => _EstadoCuentaScreenState();
}

class _EstadoCuentaScreenState extends State<EstadoCuentaScreen> with SingleTickerProviderStateMixin {
  late final Sprint4Service _svc;
  late final TabController _tabs;

  bool _cargando = true;
  String? _error;
  List<Map<String, dynamic>> _cuentas = [];
  Map<String, dynamic>? _cuentaActiva;
  List<Map<String, dynamic>> _pagosRecientes = [];

  // Extracto 20 años
  Map<String, dynamic>? _extracto;
  int _aniosPreset = 20;
  int _paginaExtracto = 1;
  bool _cargandoExtracto = false;

  bool get _esStaffCaja =>
      widget.authService.isAdminCentro ||
      widget.authService.isSuperAdmin ||
      widget.authService.isRecepcionista;

  @override
  void initState() {
    super.initState();
    _svc = Sprint4Service(authService: widget.authService);
    _tabs = TabController(length: 2, vsync: this);
    _cargarCuentas();
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  Future<void> _cargarCuentas({bool sync = false}) async {
    setState(() {
      _cargando = true;
      _error = null;
    });
    try {
      final rows = await _svc.getCuentas(sync: sync);
      if (!mounted) return;
      setState(() {
        _cuentas = rows;
        _cargando = false;
      });
      if (rows.isNotEmpty) {
        await _seleccionarCuenta(rows.first);
      }
      await _cargarExtracto(1);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _cargando = false;
      });
    }
  }

  Future<void> _seleccionarCuenta(Map<String, dynamic> cta) async {
    try {
      final det = await _svc.getCuentaDetalle(cta['paciente_id'].toString());
      if (!mounted) return;
      setState(() {
        _cuentaActiva = Map<String, dynamic>.from(det['cuenta'] ?? cta);
        _pagosRecientes = List<Map<String, dynamic>>.from(det['pagos_recientes'] ?? []);
      });
    } catch (_) {
      if (mounted) setState(() => _cuentaActiva = cta);
    }
  }

  Future<void> _cargarExtracto(int page) async {
    setState(() => _cargandoExtracto = true);
    try {
      final hoy = DateTime.now();
      final desde = DateTime(hoy.year - _aniosPreset, hoy.month, hoy.day);
      final fmt = (DateTime d) =>
          '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

      final String? pacFiltro = _esStaffCaja ? (_cuentaActiva?['paciente_id']?.toString()) : null;
      final res = await _svc.getExtractoBancario(
        pacienteId: pacFiltro,
        fechaDesde: fmt(desde),
        fechaHasta: fmt(hoy),
        page: page,
        pageSize: 20,
      );
      if (!mounted) return;
      setState(() {
        _extracto = res;
        _paginaExtracto = page;
        _cargandoExtracto = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _cargandoExtracto = false;
      });
    }
  }

  void _abrirDialogoCobro() {
    final cta = _cuentaActiva;
    if (cta == null) return;
    final saldo = double.tryParse(cta['saldo_pendiente'].toString()) ?? 0.0;
    final montoCtrl = TextEditingController(text: saldo > 0 ? saldo.toStringAsFixed(2) : '150.00');
    final refCtrl = TextEditingController();
    String metodo = 'QR_BANCARIO';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDlg) => AlertDialog(
          backgroundColor: AppTheme.cardBg,
          title: Text('Registrar Cobro (Bs.) — ${cta['codigo_expediente']}',
              style: const TextStyle(color: AppTheme.textMain, fontSize: 16)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Paciente: ${cta['paciente_nombre']}', style: const TextStyle(color: AppTheme.textMuted)),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: metodo,
                  dropdownColor: AppTheme.cardBgElevated,
                  decoration: const InputDecoration(labelText: 'Método de Pago'),
                  items: const [
                    DropdownMenuItem(value: 'EFECTIVO', child: Text('Efectivo')),
                    DropdownMenuItem(value: 'QR_BANCARIO', child: Text('QR Bancario')),
                    DropdownMenuItem(value: 'TRANSFERENCIA', child: Text('Transferencia')),
                    DropdownMenuItem(value: 'TARJETA_STRIPE', child: Text('Tarjeta / Stripe')),
                  ],
                  onChanged: (v) => setDlg(() => metodo = v ?? 'QR_BANCARIO'),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: montoCtrl,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(labelText: 'Monto a Cobrar (Bs.)'),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: refCtrl,
                  decoration: const InputDecoration(labelText: 'Referencia Bancaria / Voucher (opcional)'),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            ElevatedButton(
              onPressed: () async {
                final monto = double.tryParse(montoCtrl.text.trim()) ?? -1;
                Navigator.pop(ctx);
                final res = await _svc.registrarPago(
                  pacienteId: cta['paciente_id'].toString(),
                  monto: monto,
                  metodoPago: metodo,
                  referenciaExterna: refCtrl.text.trim(),
                );
                if (!mounted) return;
                if (res['success'] == true) {
                  final rec = res['data']?['numero_recibo'] ?? '';
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Cobro registrado — Recibo $rec'), backgroundColor: AppTheme.success),
                  );
                  await _cargarCuentas();
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(res['error'].toString()), backgroundColor: AppTheme.danger),
                  );
                }
              },
              child: const Text('Confirmar Cobro'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _kpiCard(String label, dynamic valor, Color color) {
    final numVal = double.tryParse(valor.toString()) ?? 0.0;
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: AppTheme.glassDecoration(radius: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
            const SizedBox(height: 4),
            Text('Bs. ${numVal.toStringAsFixed(2)}',
                style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 14)),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text(_esStaffCaja ? 'Caja Clínica y Extracto (Bs.)' : 'Mi Estado de Cuenta (Bs.)'),
        actions: [
          if (_esStaffCaja)
            IconButton(
              icon: const Icon(Icons.sync_rounded),
              tooltip: 'Sincronizar cargos',
              onPressed: () => _cargarCuentas(sync: true),
            ),
        ],
        bottom: TabBar(
          controller: _tabs,
          indicatorColor: AppTheme.primaryLight,
          tabs: const [
            Tab(icon: Icon(Icons.account_balance_wallet_outlined), text: 'Cuenta y Pagos'),
            Tab(icon: Icon(Icons.account_balance_outlined), text: 'Extracto 20 Años'),
          ],
        ),
      ),
      body: _cargando
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Padding(padding: const EdgeInsets.all(16), child: Text(_error!, style: const TextStyle(color: AppTheme.danger))))
              : TabBarView(
                  controller: _tabs,
                  children: [_buildTabCaja(), _buildTabExtracto()],
                ),
      floatingActionButton: _esStaffCaja && _cuentaActiva != null
          ? FloatingActionButton.extended(
              backgroundColor: AppTheme.primaryLight,
              foregroundColor: AppTheme.secondary,
              onPressed: _abrirDialogoCobro,
              icon: const Icon(Icons.payments_rounded),
              label: const Text('Registrar Cobro'),
            )
          : null,
    );
  }

  Widget _buildTabCaja() {
    final cta = _cuentaActiva;
    return RefreshIndicator(
      onRefresh: () => _cargarCuentas(),
      child: ListView(
        padding: const EdgeInsets.all(14),
        children: [
          if (_esStaffCaja && _cuentas.isNotEmpty) ...[
            DropdownButtonFormField<String>(
              value: cta?['paciente_id']?.toString(),
              dropdownColor: AppTheme.cardBgElevated,
              decoration: const InputDecoration(labelText: 'Seleccionar Paciente'),
              items: _cuentas
                  .map((c) => DropdownMenuItem<String>(
                        value: c['paciente_id'].toString(),
                        child: Text('${c['codigo_expediente']} — ${c['paciente_nombre']} (Saldo Bs. ${c['saldo_pendiente']})'),
                      ))
                  .toList(),
              onChanged: (id) {
                final found = _cuentas.firstWhere((c) => c['paciente_id'].toString() == id);
                _seleccionarCuenta(found);
              },
            ),
            const SizedBox(height: 12),
          ],
          if (cta != null) ...[
            Row(
              children: [
                _kpiCard('Total Cargado', cta['total_cargado'], AppTheme.textMain),
                const SizedBox(width: 8),
                _kpiCard('Total Pagado', cta['total_pagado'], AppTheme.success),
                const SizedBox(width: 8),
                _kpiCard('Saldo Pendiente', cta['saldo_pendiente'], AppTheme.warning),
              ],
            ),
            const SizedBox(height: 16),
            const Text('Pagos Recientes y Recibos (Bs.)',
                style: TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 8),
            if (_pagosRecientes.isEmpty)
              const Padding(
                padding: EdgeInsets.all(16),
                child: Text('Sin pagos registrados aún.', style: TextStyle(color: AppTheme.textMuted)),
              )
            else
              ..._pagosRecientes.map((p) => Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: AppTheme.glassDecoration(radius: 12),
                    child: Row(
                      children: [
                        const Icon(Icons.receipt_long_rounded, color: AppTheme.primaryLight),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('${p['numero_recibo']} • ${p['metodo_pago_display'] ?? p['metodo_pago']}',
                                  style: const TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.w600)),
                              Text('Verif: ${p['codigo_verificacion']}',
                                  style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                            ],
                          ),
                        ),
                        Text('Bs. ${p['monto']}',
                            style: const TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  )),
          ],
          const SizedBox(height: 70),
        ],
      ),
    );
  }

  Widget _buildTabExtracto() {
    final ext = _extracto;
    final movs = List<Map<String, dynamic>>.from(ext?['movimientos'] ?? []);
    final res = Map<String, dynamic>.from(ext?['resumen'] ?? {});
    final pag = Map<String, dynamic>.from(ext?['paginacion'] ?? {});

    return ListView(
      padding: const EdgeInsets.all(14),
      children: [
        Wrap(
          spacing: 8,
          children: [1, 2, 10, 20].map((a) {
            final sel = _aniosPreset == a;
            return ChoiceChip(
              label: Text('$a ${a == 1 ? "Año" : "Años"}'),
              selected: sel,
              onSelected: (_) {
                setState(() => _aniosPreset = a);
                _cargarExtracto(1);
              },
            );
          }).toList(),
        ),
        const SizedBox(height: 10),
        if (ext != null) ...[
          Row(
            children: [
              _kpiCard('Saldo Inicial', res['saldo_inicial'] ?? 0, AppTheme.textMain),
              const SizedBox(width: 8),
              _kpiCard('Total Haber', res['total_haber'] ?? 0, AppTheme.success),
              const SizedBox(width: 8),
              _kpiCard('Saldo Final', res['saldo_final'] ?? 0, AppTheme.warning),
            ],
          ),
          const SizedBox(height: 12),
          Text('Movimientos (${res['total_registros'] ?? 0}) — Pág. ${pag['page'] ?? 1}/${pag['total_paginas'] ?? 1}',
              style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
          const SizedBox(height: 8),
        ],
        if (_cargandoExtracto)
          const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()))
        else
          ...movs.map((m) => Container(
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.all(10),
                decoration: AppTheme.glassDecoration(radius: 10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('${m['fecha']} • ${m['numero_documento']}',
                            style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                        Text('Saldo: Bs. ${m['saldo_acumulado']}',
                            style: const TextStyle(color: AppTheme.primaryLight, fontWeight: FontWeight.bold, fontSize: 12)),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text('${m['concepto']}', style: const TextStyle(color: AppTheme.textMain, fontSize: 13)),
                    const SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Debe: Bs. ${m['debe']}', style: const TextStyle(color: AppTheme.warning, fontSize: 12)),
                        Text('Haber: Bs. ${m['haber']}', style: const TextStyle(color: AppTheme.success, fontSize: 12)),
                      ],
                    ),
                  ],
                ),
              )),
        if (ext != null)
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              TextButton(
                onPressed: _paginaExtracto > 1 ? () => _cargarExtracto(_paginaExtracto - 1) : null,
                child: const Text('← Anterior'),
              ),
              TextButton(
                onPressed: _paginaExtracto < ((pag['total_paginas'] ?? 1) as int)
                    ? () => _cargarExtracto(_paginaExtracto + 1)
                    : null,
                child: const Text('Siguiente →'),
              ),
            ],
          ),
      ],
    );
  }
}
