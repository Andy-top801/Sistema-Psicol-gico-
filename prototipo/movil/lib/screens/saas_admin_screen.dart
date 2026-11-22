import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../services/auth_service.dart';
import '../services/sprint4_service.dart';

class SaasAdminScreen extends StatefulWidget {
  final AuthService authService;
  const SaasAdminScreen({super.key, required this.authService});

  @override
  State<SaasAdminScreen> createState() => _SaasAdminScreenState();
}

class _SaasAdminScreenState extends State<SaasAdminScreen> {
  late final Sprint4Service _svc;
  bool _cargando = true;
  String? _error;
  Map<String, dynamic>? _dashboard;

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
      final res = await _svc.getSaasAdminDashboard();
      if (!mounted) return;
      setState(() {
        _dashboard = res;
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

  void _mostrarFacturas(Map<String, dynamic> tenant) {
    final facturas = List<Map<String, dynamic>>.from(tenant['facturas'] ?? []);
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.cardBg,
      builder: (_) => Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Facturas SaaS (USD) — ${tenant['nombre']}',
                style: const TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 12),
            ...facturas.map((f) => ListTile(
                  dense: true,
                  title: Text('${f['numero_factura']} • ${f['plan']}', style: const TextStyle(color: AppTheme.textMain)),
                  subtitle: Text('${f['fecha_emision']} • Renov: ${f['fecha_renovacion'] ?? '-'}',
                      style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                  trailing: Text('\$ ${f['monto_usd']} USD',
                      style: const TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold)),
                )),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final kpis = Map<String, dynamic>.from(_dashboard?['kpis'] ?? {});
    final tenants = List<Map<String, dynamic>>.from(_dashboard?['tenants'] ?? []);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(title: const Text('Suscripciones SaaS (USD)')),
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
                          Expanded(
                            child: Container(
                              padding: const EdgeInsets.all(12),
                              decoration: AppTheme.glassDecoration(radius: 12),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text('MRR Mensual', style: TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                                  Text('\$ ${kpis['mrr_usd'] ?? 0} USD',
                                      style: const TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold, fontSize: 18)),
                                  Text('ARR: \$ ${kpis['arr_estimado_usd'] ?? 0}', style: const TextStyle(color: AppTheme.textSubtle, fontSize: 11)),
                                ],
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Container(
                              padding: const EdgeInsets.all(12),
                              decoration: AppTheme.glassDecoration(radius: 12),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text('Centros Activos', style: TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                                  Text('${kpis['tenants_activos'] ?? 0} / ${kpis['tenants_totales'] ?? 0}',
                                      style: const TextStyle(color: AppTheme.primaryLight, fontWeight: FontWeight.bold, fontSize: 18)),
                                  Text('Facturado: \$ ${kpis['total_facturado_usd'] ?? 0}',
                                      style: const TextStyle(color: AppTheme.textSubtle, fontSize: 11)),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 14),
                      ...tenants.map((t) {
                        final cupos = Map<String, dynamic>.from(t['cupos'] ?? {});
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
                                  Expanded(
                                    child: Text('${t['nombre']}',
                                        style: const TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.bold)),
                                  ),
                                  Text('\$ ${t['precio_mensual_usd']}/mes',
                                      style: const TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold)),
                                ],
                              ),
                              Text('${t['schema_name']} • ${t['estado_suscripcion']} • Plan ${t['plan_nombre']}',
                                  style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                              const SizedBox(height: 4),
                              Text(
                                'Cupos: ${cupos['psicologos_activos'] ?? 0}/${cupos['max_psicologos'] ?? '-'} psicólogos · '
                                '${cupos['pacientes_activos'] ?? 0}/${cupos['max_pacientes'] ?? '-'} pacientes',
                                style: TextStyle(
                                  color: (cupos['alerta_cupo_psicologos'] == true || cupos['alerta_cupo_pacientes'] == true)
                                      ? AppTheme.warning
                                      : AppTheme.textSubtle,
                                  fontSize: 11,
                                ),
                              ),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.end,
                                children: [
                                  DropdownButton<String>(
                                    value: (t['plan_id'] ?? 'profesional').toString(),
                                    dropdownColor: AppTheme.cardBgElevated,
                                    underline: const SizedBox(),
                                    items: const [
                                      DropdownMenuItem(value: 'basico', child: Text('Básico \$29')),
                                      DropdownMenuItem(value: 'profesional', child: Text('Pro \$59')),
                                      DropdownMenuItem(value: 'empresarial', child: Text('Emp \$99')),
                                    ],
                                    onChanged: (p) async {
                                      if (p == null) return;
                                      final res = await _svc.actualizarPlanTenant(t['tenant_id'].toString(), plan: p);
                                      if (!mounted) return;
                                      if (res['success'] == true) _cargar();
                                    },
                                  ),
                                  TextButton(
                                    onPressed: () => _mostrarFacturas(t),
                                    child: const Text('Facturas USD'),
                                  ),
                                ],
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
}
