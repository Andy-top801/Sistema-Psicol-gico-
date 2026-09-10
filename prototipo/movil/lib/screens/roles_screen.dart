// ==============================================================================
// MÓDULO: roles_screen.dart
// CAPA BCE: BOUNDARY (Interfaz de Usuario Móvil) — IU_GestionRoles
// CASOS DE USO: CU4: Gestionar Roles y Permisos (HU-06)
// DESCRIPCIÓN: Pantalla móvil Flutter para administración de la matriz de roles y capacidades
//              RBAC del centro, asignando o revocando permisos por cada perfil de usuario.
//              Implementa los pasos 1, 2, 11 y 12 del Diagrama de Comunicación BCE.
// ==============================================================================
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
  List<dynamic> _allPermisos = [];
  bool _isLoading = true;
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _loadRoles();
    _loadPermisos();
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

  Future<void> _loadPermisos() async {
    try {
      final url = Uri.parse('${widget.authService.baseUrl}${ApiConstants.permisos}');
      final response = await http.get(url, headers: widget.authService.getHeaders());
      if (response.statusCode == 200) {
        setState(() {
          _allPermisos = jsonDecode(response.body);
        });
      }
    } catch (_) {}
  }

  void _showEditPermissionsDialog(Map<String, dynamic> rol) {
    final List currentPerms = rol['permisos'] as List? ?? [];
    final selectedIds = <int>{};
    for (var p in currentPerms) {
      if (p is Map && p['id'] != null) {
        selectedIds.add(p['id'] as int);
      }
    }

    bool isSaving = false;
    String? errorMsg;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (dialogCtx, setDialogState) {
            return AlertDialog(
              backgroundColor: AppTheme.cardBg,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              title: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      gradient: AppTheme.accentGradient,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.security_rounded, color: Colors.white, size: 20),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Permisos: ${rol['nombre']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                        const Text('Marca o desmarca capacidades del rol', style: TextStyle(fontSize: 11, color: AppTheme.textMuted)),
                      ],
                    ),
                  ),
                ],
              ),
              content: SizedBox(
                width: double.maxFinite,
                height: 380,
                child: Column(
                  children: [
                    if (errorMsg != null)
                      Container(
                        padding: const EdgeInsets.all(8),
                        margin: const EdgeInsets.only(bottom: 10),
                        decoration: BoxDecoration(
                          color: AppTheme.danger.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: AppTheme.danger.withOpacity(0.3)),
                        ),
                        child: Text(errorMsg!, style: const TextStyle(fontSize: 11, color: AppTheme.danger)),
                      ),
                    Expanded(
                      child: _allPermisos.isEmpty
                          ? const Center(child: CircularProgressIndicator())
                          : ListView.builder(
                              itemCount: _allPermisos.length,
                              itemBuilder: (context, idx) {
                                final p = _allPermisos[idx];
                                final int pId = p['id'];
                                final bool isChecked = selectedIds.contains(pId);

                                return CheckboxListTile(
                                  value: isChecked,
                                  dense: true,
                                  activeColor: AppTheme.secondary,
                                  checkColor: Colors.white,
                                  title: Text(
                                    p['nombre'] ?? '',
                                    style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                                  ),
                                  subtitle: Text(
                                    '${p['modulo'] ?? ''} • ${p['codigo'] ?? ''}',
                                    style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                                  ),
                                  onChanged: (val) {
                                    setDialogState(() {
                                      if (val == true) {
                                        selectedIds.add(pId);
                                      } else {
                                        selectedIds.remove(pId);
                                      }
                                    });
                                  },
                                );
                              },
                            ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: isSaving ? null : () => Navigator.pop(dialogCtx),
                  child: const Text('Cancelar', style: TextStyle(color: AppTheme.textMuted)),
                ),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.secondary,
                    foregroundColor: Colors.white,
                  ),
                  onPressed: isSaving
                      ? null
                      : () async {
                          // --- Paso 1: Seleccionar permisos para el rol en IU_GestionRoles > ---
                          setDialogState(() {
                            isSaving = true;
                            errorMsg = null;
                          });

                          try {
                            final url = Uri.parse('${widget.authService.baseUrl}${ApiConstants.roles}${rol['id']}/');
                            // --- Paso 2: PUT /api/roles/{id}/ {permisos: [ids]} + JWT > ---
                            // IU_GestionRoles envía los IDs seleccionados al CTR_RolService
                            final response = await http.put(
                              url,
                              headers: widget.authService.getHeaders(),
                              body: jsonEncode({
                                'nombre': rol['nombre'],
                                'descripcion': rol['descripcion'],
                                'permiso_ids': selectedIds.toList(),
                              }),
                            );

                            // --- Paso 11: 200 OK {rol_actualizado} < ---
                            // CTR_RolService confirma persistencia en CE_Rol_y_Permiso
                            if (response.statusCode == 200) {
                              if (dialogCtx.mounted) Navigator.pop(dialogCtx);
                              _loadRoles();
                              await widget.authService.refreshProfile();
                              if (mounted) {
                                // --- Paso 12: Mostrar confirmación 'Permisos actualizados' en IU_GestionRoles < ---
                                ScaffoldMessenger.of(this.context).showSnackBar(
                                  SnackBar(
                                    content: Text('Permisos de "${rol['nombre']}" actualizados correctamente.'),
                                    backgroundColor: AppTheme.success,
                                    behavior: SnackBarBehavior.floating,
                                  ),
                                );
                              }
                            } else {
                              setDialogState(() {
                                isSaving = false;
                                errorMsg = 'Error al guardar: código ${response.statusCode}';
                              });
                            }
                          } catch (e) {
                            setDialogState(() {
                              isSaving = false;
                              errorMsg = 'Error de conexión al servidor.';
                            });
                          }
                        },
                  child: isSaving
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Text('Guardar Permisos'),
                ),
              ],
            );
          },
        );
      },
    );
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
                                  if (widget.authService.isAdminCentro || widget.authService.isSuperAdmin) ...[
                                    const SizedBox(height: 12),
                                    SizedBox(
                                      width: double.infinity,
                                      child: OutlinedButton.icon(
                                        style: OutlinedButton.styleFrom(
                                          side: const BorderSide(color: AppTheme.borderSubtle),
                                          foregroundColor: AppTheme.secondary,
                                          padding: const EdgeInsets.symmetric(vertical: 8),
                                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                        ),
                                        icon: const Icon(Icons.tune_rounded, size: 16),
                                        label: const Text('Modificar Permisos / Funciones', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                                        onPressed: () => _showEditPermissionsDialog(r),
                                      ),
                                    ),
                                  ],
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
