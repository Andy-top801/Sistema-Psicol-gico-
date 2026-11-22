// CU25 (móvil): Reportes por clínica.
// El SuperAdmin elige la clínica (tenant) y el backend genera el reporte dentro de su esquema;
// el Admin de Centro siempre ve su propia clínica (el backend rechaza "clinica" para él).
// Los filtros se construyen desde /reportes/metadata/, los mismos que usa la web.
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../core/constants/api_constants.dart';
import '../core/theme/app_theme.dart';
import '../services/auth_service.dart';

class ReportesScreen extends StatefulWidget {
  final AuthService authService;
  const ReportesScreen({super.key, required this.authService});

  @override
  State<ReportesScreen> createState() => _ReportesScreenState();
}

class _ReportesScreenState extends State<ReportesScreen> {
  static const _fuentes = {
    'citas': 'Citas',
    'pacientes': 'Pacientes',
    'psicologos': 'Psicólogos',
    'ingresos': 'Ingresos',
    'alertas': 'Alertas',
    'teleconsultas': 'Teleconsultas',
  };

  Map<String, dynamic> _metadata = {};
  List<String> _clinicas = [];
  String? _clinica;
  String _fuente = 'citas';
  final Map<String, String> _filtros = {};

  List<Map<String, dynamic>> _columnas = [];
  List<Map<String, dynamic>> _datos = [];
  int _total = 0;
  String? _clinicaResultado;
  bool _cargando = false;
  String? _error;
  int _consulta = 0; // descarta respuestas de una consulta anterior

  bool get _esSuper => widget.authService.isSuperAdmin;

  @override
  void initState() {
    super.initState();
    _iniciar();
  }

  Future<void> _iniciar() async {
    setState(() => _cargando = true);
    try {
      final r = await http
          .get(Uri.parse('${widget.authService.baseUrl}${ApiConstants.reportesMetadata}'),
              headers: widget.authService.getHeaders())
          .timeout(const Duration(seconds: 15));
      if (r.statusCode == 200) _metadata = jsonDecode(utf8.decode(r.bodyBytes));
      if (_esSuper) {
        final tenants = await widget.authService.getPublicTenants();
        _clinicas = tenants.where((t) => t.schemaName != 'public').map((t) => t.nombre).toList()..sort();
        _clinica ??= widget.authService.currentTenant?.nombre;
        if (_clinica == null || !_clinicas.contains(_clinica)) _clinica = _clinicas.isNotEmpty ? _clinicas.first : null;
      }
    } catch (_) {}
    if (!mounted) return;
    await _generar();
  }

  Future<void> _generar() async {
    if (_esSuper && _clinica == null) {
      setState(() {
        _cargando = false;
        _error = 'No hay clínicas disponibles para elegir.';
      });
      return;
    }
    final id = ++_consulta;
    setState(() {
      _cargando = true;
      _error = null;
    });
    try {
      final r = await http
          .post(
            Uri.parse('${widget.authService.baseUrl}${ApiConstants.reportesPersonalizado}'),
            headers: widget.authService.getHeaders(),
            body: jsonEncode({
              'fuente': _fuente,
              'filtros': _filtros,
              if (_esSuper) 'clinica': _clinica,
            }),
          )
          .timeout(const Duration(seconds: 30));
      if (id != _consulta || !mounted) return;
      final body = jsonDecode(utf8.decode(r.bodyBytes));
      setState(() {
        if (r.statusCode == 200) {
          _columnas = List<Map<String, dynamic>>.from(body['columnas'] ?? []);
          _datos = List<Map<String, dynamic>>.from(body['datos'] ?? []);
          _total = body['total'] ?? _datos.length;
          _clinicaResultado = body['clinica'];
        } else {
          _datos = [];
          _total = 0;
          _error = (body is Map ? body['error'] ?? body['detail'] : null)?.toString() ?? 'Error ${r.statusCode}';
        }
      });
    } catch (e) {
      if (id != _consulta || !mounted) return;
      setState(() {
        _datos = [];
        _error = 'No se pudo conectar con el servidor: $e';
      });
    } finally {
      if (id == _consulta && mounted) setState(() => _cargando = false);
    }
  }

  void _cambiarFuente(String f) {
    if (f == _fuente) return;
    setState(() {
      _fuente = f;
      _filtros.clear(); // cada fuente tiene sus propios filtros
    });
    _generar();
  }

  String _valor(dynamic v) {
    if (v == null || v == '') return '—';
    if (v is bool) return v ? 'Sí' : 'No';
    return v.toString();
  }

  // ───────────────────────────── UI ─────────────────────────────

  @override
  Widget build(BuildContext context) {
    final filtrosDef = List<Map<String, dynamic>>.from(_metadata[_fuente]?['filtros'] ?? []);
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        backgroundColor: AppTheme.cardBg,
        title: const Text('Reportes'),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _cargando ? null : _generar)],
      ),
      body: RefreshIndicator(
        onRefresh: _generar,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_esSuper) ...[
              DropdownButtonFormField<String>(
                value: _clinica,
                isExpanded: true,
                decoration: const InputDecoration(labelText: 'Clínica', prefixIcon: Icon(Icons.local_hospital_outlined)),
                items: _clinicas.map((c) => DropdownMenuItem(value: c, child: Text(c, overflow: TextOverflow.ellipsis))).toList(),
                onChanged: (c) {
                  setState(() {
                    _clinica = c;
                    _datos = []; // no dejar en pantalla datos de otra clínica
                  });
                  _generar();
                },
              ),
              const SizedBox(height: 12),
            ],
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _fuentes.entries
                  .map((e) => ChoiceChip(
                        label: Text(e.value),
                        selected: _fuente == e.key,
                        onSelected: (_) => _cambiarFuente(e.key),
                      ))
                  .toList(),
            ),
            if (filtrosDef.isNotEmpty)
              ExpansionTile(
                tilePadding: EdgeInsets.zero,
                title: Text('Filtros${_filtros.isEmpty ? '' : ' (${_filtros.length})'}',
                    style: const TextStyle(color: AppTheme.textMain)),
                children: [
                  ...filtrosDef.map(_campoFiltro),
                  Row(children: [
                    TextButton(
                      onPressed: () {
                        setState(_filtros.clear);
                        _generar();
                      },
                      child: const Text('Limpiar'),
                    ),
                    const Spacer(),
                    FilledButton.icon(onPressed: _generar, icon: const Icon(Icons.search), label: const Text('Aplicar')),
                  ]),
                ],
              ),
            const SizedBox(height: 8),
            if (_cargando) const Padding(padding: EdgeInsets.all(24), child: Center(child: CircularProgressIndicator())),
            if (_error != null)
              Card(
                color: AppTheme.danger.withOpacity(0.15),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text(_error!, style: const TextStyle(color: AppTheme.textMain)),
                ),
              ),
            if (!_cargando && _error == null) ...[
              Text(
                '$_total registro(s) de ${_fuentes[_fuente]}${_clinicaResultado != null ? ' · $_clinicaResultado' : ''}',
                style: const TextStyle(color: AppTheme.textMuted, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              if (_datos.isEmpty)
                const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: Text('Sin resultados para estos filtros.', style: TextStyle(color: AppTheme.textMuted))),
                ),
              ..._datos.map(_tarjetaFila),
            ],
          ],
        ),
      ),
    );
  }

  Widget _campoFiltro(Map<String, dynamic> f) {
    final key = f['key'] as String;
    final label = f['label'] as String;
    final actual = _filtros[key];
    void poner(String? v) => setState(() => (v == null || v.isEmpty) ? _filtros.remove(key) : _filtros[key] = v);

    switch (f['type']) {
      case 'select':
        final opciones = List<String>.from(f['opciones'] ?? []);
        return Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: DropdownButtonFormField<String>(
            value: opciones.contains(actual) ? actual : null,
            isExpanded: true,
            decoration: InputDecoration(labelText: label),
            items: [
              const DropdownMenuItem<String>(value: null, child: Text('Todos')),
              ...opciones.map((o) => DropdownMenuItem(value: o, child: Text(o))),
            ],
            onChanged: poner,
          ),
        );
      case 'date':
        return ListTile(
          contentPadding: EdgeInsets.zero,
          leading: const Icon(Icons.event, color: AppTheme.textMuted),
          title: Text(label, style: const TextStyle(color: AppTheme.textMain)),
          subtitle: Text(actual ?? 'Cualquiera', style: const TextStyle(color: AppTheme.textMuted)),
          trailing: actual == null ? null : IconButton(icon: const Icon(Icons.clear), onPressed: () => poner(null)),
          onTap: () async {
            final d = await showDatePicker(
              context: context,
              initialDate: DateTime.tryParse(actual ?? '') ?? DateTime.now(),
              firstDate: DateTime(2020),
              lastDate: DateTime(2035),
            );
            if (d != null) poner(d.toIso8601String().substring(0, 10));
          },
        );
      default:
        return Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: TextFormField(
            key: ValueKey('$_fuente-$key-${actual == null}'),
            initialValue: actual,
            decoration: InputDecoration(labelText: label, helperText: 'Puedes escribir el nombre'),
            onChanged: poner,
            onFieldSubmitted: (_) => _generar(),
          ),
        );
    }
  }

  Widget _tarjetaFila(Map<String, dynamic> fila) {
    if (_columnas.isEmpty) return const SizedBox.shrink();
    final titulo = _columnas.firstWhere(
      (c) => (c['key'] as String).contains('nombre'),
      orElse: () => _columnas.first,
    );
    final resto = _columnas.where((c) => c != titulo).take(6);
    return Card(
      color: AppTheme.cardBg,
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(_valor(fila[titulo['key']]),
                style: const TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.w700, fontSize: 15)),
            const SizedBox(height: 6),
            ...resto.map((c) => Padding(
                  padding: const EdgeInsets.only(bottom: 2),
                  child: Text('${c['label']}: ${_valor(fila[c['key']])}',
                      style: const TextStyle(color: AppTheme.textMuted, fontSize: 13)),
                )),
          ],
        ),
      ),
    );
  }
}
