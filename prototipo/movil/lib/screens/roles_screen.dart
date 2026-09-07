import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../services/auth_service.dart';
import '../core/theme/app_theme.dart';
import '../core/constants/api_constants.dart';

class RolesScreen extends StatefulWidget {
  final AuthService authService;

  const RolesScreen({super.key, required this.authService});

  @override
  State<RolesScreen> createState() => _RolesScreenState();
}

/// ═════════════════════════════════════════════════════════════════════════
/// CU4: Gestionar Roles y Permisos (HU-06)
/// Diagrama de Comunicación – Matriz de Roles y Permisos (Móvil Flutter)
/// Participantes:
///   Actor  → Administrador del Centro
///   IU     → IU_GestionRoles (Móvil)  ← ESTE ARCHIVO
///   CTR    → CTR_RolService (Django REST)
///   CE     → CE_Rol_y_Permiso (PostgreSQL)
/// ═════════════════════════════════════════════════════════════════════════
class _RolesScreenState extends State<RolesScreen> {
  List<dynamic> _roles = [];
  bool _isLoading = true;
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _loadRoles();
  }

  Future<void> _loadRoles() async {
    setState(() => _isLoading = true);
    try {
      final url = Uri.parse('${widget.authService.baseUrl}${ApiConstants.roles}');
      final response = await http.get(url, headers: widget.authService.getHeaders());
      if (response.statusCode == 200) {
        setState(() {
          _roles = jsonDecode(response.body);
        });
      }
    } catch (_) {}
    setState(() => _isLoading = false);
  }

  List<dynamic> get _filteredRoles {
    if (_searchQuery.isEmpty) return _roles;
    final query = _searchQuery.toLowerCase();
    return _roles.where((r) {
      final nombre = (r['nombre'] ?? '').toString().toLowerCase();
      final descripcion = (r['descripcion'] ?? '').toString().toLowerCase();
      final perms = (r['permisos'] as List? ?? []);
      final matchesPerm = perms.any((p) => (p['nombre'] ?? '').toString().toLowerCase().contains(query));
      return nombre.contains(query) || descripcion.contains(query) || matchesPerm;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final rolesToShow = _filteredRoles;

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Roles y Permisos (RBAC)'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Actualizar',
            onPressed: _loadRoles,
          ),
        ],
      ),
      body: Column(
        children: [
          // Banner Informativo y Buscador
          Container(
            padding: const EdgeInsets.all(16),
            decoration: const BoxDecoration(
              color: AppTheme.cardBg,
              border: Border(bottom: BorderSide(color: AppTheme.borderSubtle)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Info banner
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppTheme.secondary.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppTheme.secondary.withOpacity(0.25)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.security_rounded, color: AppTheme.secondary, size: 20),
                      SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'Matriz de seguridad granular. Los permisos determinan los accesos a datos clínicos y funciones operativas.',
                          style: TextStyle(fontSize: 11, color: Color(0xFFC7D2FE)),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                // Buscador
                TextField(
                  onChanged: (val) => setState(() => _searchQuery = val),
                  decoration: InputDecoration(
                    hintText: 'Buscar rol o permiso (ej. usuarios, reportes)...',
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
              ],
            ),
          ),

          // Lista de Roles
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : rolesToShow.isEmpty
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
                              child: const Icon(Icons.shield_outlined, size: 44, color: AppTheme.textMuted),
                            ),
                            const SizedBox(height: 14),
                            const Text('No se encontraron roles', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                            const SizedBox(height: 4),
                            const Text('Intenta con otro término de búsqueda.', style: TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: rolesToShow.length,
                        itemBuilder: (context, index) {
                          final r = rolesToShow[index];
                          final List perms = r['permisos'] ?? [];

                          return Container(
                            margin: const EdgeInsets.only(bottom: 16),
                            decoration: BoxDecoration(
                              color: AppTheme.cardBg,
                              borderRadius: BorderRadius.circular(18),
                              border: Border.all(color: AppTheme.borderSubtle),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.2),
                                  blurRadius: 10,
                                  offset: const Offset(0, 3),
                                ),
                              ],
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Encabezado del Rol
                                  Row(
                                    children: [
                                      Container(
                                        width: 42,
                                        height: 42,
                                        decoration: BoxDecoration(
                                          gradient: AppTheme.accentGradient,
                                          borderRadius: BorderRadius.circular(12),
                                        ),
                                        child: const Icon(Icons.shield_rounded, color: Colors.white, size: 22),
                                      ),
                                      const SizedBox(width: 12),
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              r['nombre'] ?? '',
                                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textMain),
                                            ),
                                            if (r['descripcion'] != null && (r['descripcion'] as String).isNotEmpty)
                                              Text(
                                                r['descripcion'],
                                                style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                                              ),
                                          ],
                                        ),
                                      ),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: AppTheme.secondary.withOpacity(0.15),
                                          borderRadius: BorderRadius.circular(10),
                                          border: Border.all(color: AppTheme.secondary.withOpacity(0.3)),
                                        ),
                                        child: Text(
                                          '${perms.length} Permisos',
                                          style: const TextStyle(
                                            fontSize: 11,
                                            fontWeight: FontWeight.w700,
                                            color: Color(0xFFA5B4FC),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 14),
                                  const Divider(height: 1, color: AppTheme.borderSubtle),
                                  const SizedBox(height: 12),

                                  // Lista de Permisos
                                  const Row(
                                    children: [
                                      Icon(Icons.vpn_key_outlined, size: 13, color: AppTheme.textSubtle),
                                      SizedBox(width: 5),
                                      Text(
                                        'CAPACIDADES ASIGNADAS:',
                                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 0.5, color: AppTheme.textSubtle),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),

                                  if (perms.isEmpty)
                                    const Text('Sin permisos asignados actualmente.', style: TextStyle(fontSize: 12, color: AppTheme.textMuted))
                                  else
                                    Wrap(
                                      spacing: 6,
                                      runSpacing: 6,
                                      children: perms.map<Widget>((p) {
                                        return Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
                                          decoration: BoxDecoration(
                                            color: AppTheme.inputBg,
                                            borderRadius: BorderRadius.circular(8),
                                            border: Border.all(color: AppTheme.borderSubtle),
                                          ),
                                          child: Row(
                                            mainAxisSize: MainAxisSize.min,
                                            children: [
                                              const Icon(Icons.check_rounded, size: 12, color: AppTheme.success),
                                              const SizedBox(width: 4),
                                              Text(
                                                p['nombre'] ?? '',
                                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                                              ),
                                            ],
                                          ),
                                        );
                                      }).toList(),
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
}
