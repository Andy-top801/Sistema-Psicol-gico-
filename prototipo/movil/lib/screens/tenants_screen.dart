import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../services/auth_service.dart';
import '../models/tenant_model.dart';
import '../core/theme/app_theme.dart';
import '../core/constants/api_constants.dart';

class TenantsScreen extends StatefulWidget {
  final AuthService authService;

  const TenantsScreen({super.key, required this.authService});

  @override
  State<TenantsScreen> createState() => _TenantsScreenState();
}

/// ═════════════════════════════════════════════════════════════════════════
/// CU1: Gestionar Centros Psicológicos y Configuración Multi-Tenant
///      (HU-03, HU-04, HU-07, HU-08)
/// Diagrama de Comunicación – Centros Psicológicos (Móvil Flutter)
/// Participantes:
///   Actor  → SuperAdministrador
///   IU     → IU_FormularioCentro / IU_Tenants (Móvil)  ← ESTE ARCHIVO
///   CTR    → CTR_TenantService (Django)
///   CE     → CE_Tenant_y_Dominio (PostgreSQL)
/// ═════════════════════════════════════════════════════════════════════════
class _TenantsScreenState extends State<TenantsScreen> {
  List<TenantModel> _tenants = [];
  bool _isLoading = true;
  String _searchQuery = '';
  String _selectedFilter = 'Todos';

  @override
  void initState() {
    super.initState();
    _loadTenants();
  }

  Future<void> _loadTenants() async {
    setState(() => _isLoading = true);
    try {
      final url = Uri.parse('${widget.authService.baseUrl}${ApiConstants.tenants}');
      final response = await http.get(url, headers: widget.authService.getHeaders());
      if (response.statusCode == 200) {
        final List list = jsonDecode(response.body);
        setState(() {
          _tenants = list.map((e) => TenantModel.fromJson(e)).toList();
        });
      }
    } catch (_) {}
    setState(() => _isLoading = false);
  }

  Future<void> _toggleSuspend(TenantModel tenant) async {
    final willSuspend = tenant.activo;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardBg,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Icon(
              willSuspend ? Icons.warning_amber_rounded : Icons.check_circle_outline_rounded,
              color: willSuspend ? AppTheme.danger : AppTheme.success,
              size: 24,
            ),
            const SizedBox(width: 10),
            Text(
              willSuspend ? '¿Suspender Centro?' : '¿Activar Centro?',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 17),
            ),
          ],
        ),
        content: Text(
          willSuspend
              ? 'El centro "${tenant.nombre}" y todos sus psicólogos perderán acceso inmediato a la plataforma.'
              : 'Se reactivará el esquema y acceso para el centro "${tenant.nombre}".',
          style: const TextStyle(color: AppTheme.textMuted, fontSize: 13),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancelar', style: TextStyle(color: AppTheme.textMuted)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: willSuspend ? AppTheme.danger : AppTheme.success,
              foregroundColor: Colors.white,
            ),
            onPressed: () => Navigator.pop(ctx, true),
            child: Text(willSuspend ? 'Suspender' : 'Activar'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    try {
      final action = willSuspend ? 'suspender' : 'activar';
      final url = Uri.parse('${widget.authService.baseUrl}${ApiConstants.tenants}${tenant.id}/$action/');
      final res = await http.post(url, headers: widget.authService.getHeaders());
      if (res.statusCode == 200) {
        _loadTenants();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(willSuspend ? 'Centro suspendido exitosamente' : 'Centro activado'),
              backgroundColor: willSuspend ? AppTheme.danger : AppTheme.success,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          );
        }
      }
    } catch (_) {}
  }

  List<TenantModel> get _filteredTenants {
    return _tenants.where((t) {
      final matchesSearch = _searchQuery.isEmpty ||
          t.nombre.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          t.slug.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          t.plan.toLowerCase().contains(_searchQuery.toLowerCase());

      final matchesFilter = _selectedFilter == 'Todos' ||
          (_selectedFilter == 'Activos' && t.activo) ||
          (_selectedFilter == 'Suspendidos' && !t.activo);

      return matchesSearch && matchesFilter;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final list = _filteredTenants;
    final total = _tenants.length;
    final activos = _tenants.where((t) => t.activo).length;
    final suspendidos = total - activos;

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Centros Psicológicos'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Actualizar',
            onPressed: _loadTenants,
          ),
        ],
      ),
      body: Column(
        children: [
          // Métricas y Buscador
          Container(
            padding: const EdgeInsets.all(16),
            decoration: const BoxDecoration(
              color: AppTheme.cardBg,
              border: Border(bottom: BorderSide(color: AppTheme.borderSubtle)),
            ),
            child: Column(
              children: [
                // Fila de Métricas Rápidas
                Row(
                  children: [
                    _buildMetricCard('Total Centros', total.toString(), Icons.domain_rounded, AppTheme.primaryLight),
                    const SizedBox(width: 8),
                    _buildMetricCard('Activos', activos.toString(), Icons.check_circle_outline_rounded, AppTheme.success),
                    const SizedBox(width: 8),
                    _buildMetricCard('Suspendidos', suspendidos.toString(), Icons.block_rounded, AppTheme.danger),
                  ],
                ),
                const SizedBox(height: 12),

                // Buscador
                TextField(
                  onChanged: (val) => setState(() => _searchQuery = val),
                  decoration: InputDecoration(
                    hintText: 'Buscar por nombre, slug o plan...',
                    prefixIcon: const Icon(Icons.search_rounded, size: 20),
                    suffixIcon: _searchQuery.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear_rounded, size: 18),
                            onPressed: () => setState(() => _searchQuery = ''),
                          )
                        : null,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  ),
                ),
                const SizedBox(height: 10),

                // Filtros
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: ['Todos', 'Activos', 'Suspendidos'].map((filter) {
                      final isSelected = _selectedFilter == filter;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8.0),
                        child: ChoiceChip(
                          label: Text(filter),
                          selected: isSelected,
                          onSelected: (sel) {
                            if (sel) setState(() => _selectedFilter = filter);
                          },
                          selectedColor: AppTheme.primary.withOpacity(0.2),
                          backgroundColor: AppTheme.inputBg,
                          labelStyle: TextStyle(
                            color: isSelected ? AppTheme.primaryLight : AppTheme.textMuted,
                            fontWeight: isSelected ? FontWeight.w700 : FontWeight.normal,
                            fontSize: 12,
                          ),
                          side: BorderSide(
                            color: isSelected ? AppTheme.primary : AppTheme.borderSubtle,
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ),

          // Lista de Centros
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : list.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(20),
                              decoration: BoxDecoration(
                                color: AppTheme.cardBg,
                                shape: BoxShape.circle,
                                border: Border.all(color: AppTheme.borderSubtle),
                              ),
                              child: const Icon(Icons.apartment_rounded, size: 44, color: AppTheme.textMuted),
                            ),
                            const SizedBox(height: 14),
                            const Text('No se encontraron centros', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                            const SizedBox(height: 4),
                            const Text('Ajusta el filtro o término de búsqueda.', style: TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: list.length,
                        itemBuilder: (context, index) {
                          final t = list[index];

                          return Container(
                            margin: const EdgeInsets.only(bottom: 12),
                            decoration: BoxDecoration(
                              color: AppTheme.cardBg,
                              borderRadius: BorderRadius.circular(18),
                              border: Border.all(color: AppTheme.borderSubtle),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.18),
                                  blurRadius: 8,
                                  offset: const Offset(0, 2),
                                ),
                              ],
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                children: [
                                  Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Container(
                                        width: 46,
                                        height: 46,
                                        decoration: BoxDecoration(
                                          gradient: AppTheme.primaryGradient,
                                          borderRadius: BorderRadius.circular(14),
                                        ),
                                        child: const Icon(Icons.local_hospital_rounded, color: Colors.white, size: 24),
                                      ),
                                      const SizedBox(width: 12),
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Row(
                                              children: [
                                                Expanded(
                                                  child: Text(
                                                    t.nombre,
                                                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                                                    overflow: TextOverflow.ellipsis,
                                                  ),
                                                ),
                                                // Status Pill
                                                Container(
                                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                                  decoration: BoxDecoration(
                                                    color: t.activo ? AppTheme.success.withOpacity(0.12) : AppTheme.danger.withOpacity(0.12),
                                                    borderRadius: BorderRadius.circular(12),
                                                    border: Border.all(
                                                      color: t.activo ? AppTheme.success.withOpacity(0.3) : AppTheme.danger.withOpacity(0.3),
                                                    ),
                                                  ),
                                                  child: Row(
                                                    mainAxisSize: MainAxisSize.min,
                                                    children: [
                                                      Container(
                                                        width: 6,
                                                        height: 6,
                                                        decoration: BoxDecoration(
                                                          color: t.activo ? AppTheme.success : AppTheme.danger,
                                                          shape: BoxShape.circle,
                                                        ),
                                                      ),
                                                      const SizedBox(width: 4),
                                                      Text(
                                                        t.activo ? 'Operativo' : 'Suspendido',
                                                        style: TextStyle(
                                                          fontSize: 10,
                                                          fontWeight: FontWeight.w700,
                                                          color: t.activo ? AppTheme.success : AppTheme.danger,
                                                        ),
                                                      ),
                                                    ],
                                                  ),
                                                ),
                                              ],
                                            ),
                                            const SizedBox(height: 4),
                                            Row(
                                              children: [
                                                const Icon(Icons.dataset_rounded, size: 13, color: AppTheme.textSubtle),
                                                const SizedBox(width: 4),
                                                Text(
                                                  'Schema: ${t.slug}',
                                                  style: const TextStyle(fontSize: 12, color: AppTheme.textMuted, fontFamily: 'monospace'),
                                                ),
                                              ],
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),
                                  const Divider(height: 1, color: AppTheme.borderSubtle),
                                  const SizedBox(height: 8),

                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      // Plan Badge
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                        decoration: BoxDecoration(
                                          color: AppTheme.accent.withOpacity(0.12),
                                          borderRadius: BorderRadius.circular(8),
                                          border: Border.all(color: AppTheme.accent.withOpacity(0.25)),
                                        ),
                                        child: Text(
                                          'Plan: ${t.plan.toUpperCase()}',
                                          style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: Color(0xFFC4B5FD)),
                                        ),
                                      ),

                                      // Acción Suspender / Activar
                                      InkWell(
                                        onTap: () => _toggleSuspend(t),
                                        borderRadius: BorderRadius.circular(8),
                                        child: Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                          decoration: BoxDecoration(
                                            color: t.activo ? AppTheme.danger.withOpacity(0.12) : AppTheme.success.withOpacity(0.12),
                                            borderRadius: BorderRadius.circular(8),
                                          ),
                                          child: Row(
                                            children: [
                                              Icon(
                                                t.activo ? Icons.block_rounded : Icons.check_circle_rounded,
                                                size: 14,
                                                color: t.activo ? AppTheme.danger : AppTheme.success,
                                              ),
                                              const SizedBox(width: 4),
                                              Text(
                                                t.activo ? 'Suspender Centro' : 'Reactivar Centro',
                                                style: TextStyle(
                                                  fontSize: 11,
                                                  fontWeight: FontWeight.bold,
                                                  color: t.activo ? AppTheme.danger : AppTheme.success,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricCard(String label, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 10),
        decoration: BoxDecoration(
          color: AppTheme.inputBg,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppTheme.borderSubtle),
        ),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, size: 13, color: color),
                const SizedBox(width: 4),
                Text(
                  label,
                  style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.textMuted),
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: color),
            ),
          ],
        ),
      ),
    );
  }
}
