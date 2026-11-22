import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../services/auth_service.dart';
import '../services/sprint4_service.dart';
import 'reportes_screen.dart';

class DashboardFinancieroScreen extends StatefulWidget {
  final AuthService authService;
  const DashboardFinancieroScreen({super.key, required this.authService});

  @override
  State<DashboardFinancieroScreen> createState() => _DashboardFinancieroScreenState();
}

class _DashboardFinancieroScreenState extends State<DashboardFinancieroScreen> {
  late final Sprint4Service _svc;
  String _horizonte = '24m';
  bool _cargando = true;
  String? _error;
  Map<String, dynamic>? _data;

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
      final res = await _svc.getDashboardFinanciero(horizonte: _horizonte);
      if (!mounted) return;
      setState(() {
        _data = res;
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

  Widget _kpiTile(String title, String value, String sub, Color accent) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: AppTheme.glassDecoration(radius: 14, borderColor: accent.withOpacity(0.4)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
          const SizedBox(height: 6),
          Text(value, style: TextStyle(color: accent, fontWeight: FontWeight.bold, fontSize: 17)),
          const SizedBox(height: 4),
          Text(sub, style: const TextStyle(color: AppTheme.textSubtle, fontSize: 11)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final kpis = Map<String, dynamic>.from(_data?['kpis'] ?? {});
    final yoy = Map<String, dynamic>.from(_data?['comparativa_yoy']?['variacion_pct'] ?? {});
    final metodos = List<Map<String, dynamic>>.from(_data?['distribucion_metodo_pago'] ?? []);
    final psicos = List<Map<String, dynamic>>.from(_data?['rendimiento_psicologos'] ?? []);
    final serie = List<Map<String, dynamic>>.from(_data?['serie_mensual'] ?? []);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Dashboard Financiero (Bs.)'),
        actions: [
          IconButton(
            icon: const Icon(Icons.pie_chart_outline_rounded),
            tooltip: 'Todos los Reportes',
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => ReportesScreen(authService: widget.authService)),
            ),
          ),
        ],
      ),
      body: _cargando
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Padding(padding: const EdgeInsets.all(16), child: Text(_error!, style: const TextStyle(color: AppTheme.danger))))
              : RefreshIndicator(
                  onRefresh: _cargar,
                  child: ListView(
                    padding: const EdgeInsets.all(14),
                    children: [
                      Wrap(
                        spacing: 8,
                        children: const [
                          ['12m', '12 Meses'],
                          ['24m', '24 Meses (2 Años)'],
                          ['36m', '36 Meses'],
                          ['all', 'Todo'],
                        ].map((item) {
                          final sel = _horizonte == item[0];
                          return ChoiceChip(
                            label: Text(item[1]),
                            selected: sel,
                            onSelected: (_) {
                              setState(() => _horizonte = item[0]);
                              _cargar();
                            },
                          );
                        }).toList(),
                      ),
                      const SizedBox(height: 12),
                      GridView.count(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        crossAxisCount: 2,
                        crossAxisSpacing: 10,
                        mainAxisSpacing: 10,
                        childAspectRatio: 1.45,
                        children: [
                          _kpiTile(
                            'Ingreso Bruto',
                            'Bs. ${(kpis['ingreso_bruto'] ?? 0).toStringAsFixed(2)}',
                            'YoY: ${yoy['ingreso_bruto'] ?? 0}%',
                            AppTheme.textMain,
                          ),
                          _kpiTile(
                            'Honorarios Psico.',
                            'Bs. ${(kpis['honorarios_psicologos'] ?? 0).toStringAsFixed(2)}',
                            'Retención: Bs. ${(kpis['comision_retenida_centro'] ?? 0).toStringAsFixed(2)}',
                            AppTheme.info,
                          ),
                          _kpiTile(
                            'Margen Neto Real',
                            'Bs. ${(kpis['margen_neto_centro'] ?? 0).toStringAsFixed(2)}',
                            'YoY: ${yoy['margen_neto'] ?? 0}%',
                            AppTheme.success,
                          ),
                          _kpiTile(
                            'Cartera / Morosidad',
                            'Bs. ${(kpis['cartera_por_cobrar'] ?? 0).toStringAsFixed(2)}',
                            'Índice: ${kpis['indice_morosidad_pct'] ?? 0}%',
                            AppTheme.warning,
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Text('Serie Longitudinal (${serie.length} meses)',
                          style: const TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.bold, fontSize: 15)),
                      const SizedBox(height: 8),
                      ...serie.reversed.take(12).map((m) => Container(
                            margin: const EdgeInsets.only(bottom: 6),
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            decoration: AppTheme.glassDecoration(radius: 10),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text('${m['periodo']}', style: const TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.w600)),
                                Text('Bruto: Bs. ${m['ingreso_bruto']}', style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                                Text('Neto: Bs. ${m['margen_neto']}', style: const TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold, fontSize: 12)),
                              ],
                            ),
                          )),
                      const SizedBox(height: 14),
                      const Text('Recaudación por Método de Pago',
                          style: TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.bold, fontSize: 15)),
                      const SizedBox(height: 8),
                      ...metodos.map((mp) => ListTile(
                            dense: true,
                            tileColor: AppTheme.cardBg,
                            title: Text('${mp['metodo_pago']}', style: const TextStyle(color: AppTheme.textMain)),
                            subtitle: Text('${mp['cantidad']} pagos', style: const TextStyle(color: AppTheme.textMuted)),
                            trailing: Text('Bs. ${mp['total_bob']}',
                                style: const TextStyle(color: AppTheme.primaryLight, fontWeight: FontWeight.bold)),
                          )),
                      const SizedBox(height: 14),
                      const Text('Rendimiento por Psicólogo',
                          style: TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.bold, fontSize: 15)),
                      const SizedBox(height: 8),
                      ...psicos.map((p) => Container(
                            margin: const EdgeInsets.only(bottom: 6),
                            padding: const EdgeInsets.all(10),
                            decoration: AppTheme.glassDecoration(radius: 10),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Text('${p['nombre']} (${p['sesiones_realizadas']} ses.)',
                                      style: const TextStyle(color: AppTheme.textMain, fontSize: 13)),
                                ),
                                Text('Margen Bs. ${p['margen_centro_bob']}',
                                    style: const TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold, fontSize: 12)),
                              ],
                            ),
                          )),
                    ],
                  ),
                ),
    );
  }
}
