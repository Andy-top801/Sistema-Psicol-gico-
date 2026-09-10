// ==============================================================================
// MÓDULO: users_screen.dart
// CAPA BCE: BOUNDARY (Interfaz de Usuario Móvil) — IU_GestionUsuarios
// CASOS DE USO: CU3: Gestionar Usuarios (HU-05)
// DESCRIPCIÓN: Pantalla móvil Flutter para administración de personal del centro
//              psicológico, terapeutas, psicólogos y recepcionistas.
//              Implementa los pasos 1, 2, 11 y 12 del Diagrama de Comunicación BCE.
// ==============================================================================
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../services/auth_service.dart';
import '../models/user_model.dart';
import '../core/theme/app_theme.dart';
import '../core/constants/api_constants.dart';

class UsersScreen extends StatefulWidget {
  final AuthService authService;

  const UsersScreen({super.key, required this.authService});

  @override
  State<UsersScreen> createState() => _UsersScreenState();
}

class _UsersScreenState extends State<UsersScreen> {
  List<UserModel> _users = [];
  List<Map<String, dynamic>> _roles = [];
  bool _isLoading = true;
  String _searchQuery = '';
  String _selectedFilter = 'Todos'; // 'Todos', 'Activos', 'Inactivos'

  @override
  void initState() {
    super.initState();
    _loadUsers();
    _loadRoles();
  }

  Future<void> _loadUsers() async {
    setState(() => _isLoading = true);
    try {
      final url = Uri.parse('${widget.authService.baseUrl}${ApiConstants.users}');
      final response = await http.get(url, headers: widget.authService.getHeaders());
      if (response.statusCode == 200) {
        final List list = jsonDecode(response.body);
        setState(() {
          _users = list.map((e) => UserModel.fromJson(e)).toList();
        });
      }
    } catch (_) {}
    setState(() => _isLoading = false);
  }

  Future<void> _loadRoles() async {
    try {
      final url = Uri.parse('${widget.authService.baseUrl}${ApiConstants.roles}');
      final response = await http.get(url, headers: widget.authService.getHeaders());
      if (response.statusCode == 200) {
        final List list = jsonDecode(response.body);
        setState(() {
          _roles = list.map((e) => e as Map<String, dynamic>).toList();
        });
      }
    } catch (_) {}
  }

  /// -----------------------------------------------------------------------
  /// CU3: Alternar estado de activación de usuario
  /// Paso 1: Administrador pulsa alternar estado en IU_GestionUsuarios
  /// Paso 2: Solicitud POST a CTR_UsuarioService (alternar_estado)
  /// Paso 11/12: Retorno 200 OK y actualización visual del estado en UI
  /// -----------------------------------------------------------------------
  Future<void> _toggleStatus(UserModel user) async {
    try {
      final url = Uri.parse('${widget.authService.baseUrl}${ApiConstants.users}${user.id}/alternar_estado/');
      final response = await http.post(url, headers: widget.authService.getHeaders());
      if (response.statusCode == 200) {
        _loadUsers();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Row(
                children: [
                  Icon(user.activo ? Icons.person_off_rounded : Icons.person_add_alt_1_rounded, color: Colors.white, size: 20),
                  const SizedBox(width: 8),
                  Text(user.activo ? 'Usuario desactivado' : 'Usuario activado'),
                ],
              ),
              backgroundColor: user.activo ? AppTheme.danger : AppTheme.success,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Error al cambiar el estado del usuario.'),
            backgroundColor: AppTheme.danger,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        );
      }
    }
  }

  // --- Validación de contraseña ---
  bool _hasUppercase(String pwd) => RegExp(r'[A-Z]').hasMatch(pwd);
  bool _hasLowercase(String pwd) => RegExp(r'[a-z]').hasMatch(pwd);
  bool _hasNumber(String pwd) => RegExp(r'[0-9]').hasMatch(pwd);
  bool _hasSpecial(String pwd) => RegExp(r'[^A-Za-z0-9]').hasMatch(pwd);
  bool _isPasswordValid(String pwd) =>
      pwd.length >= 8 && _hasUppercase(pwd) && _hasLowercase(pwd) && _hasNumber(pwd) && _hasSpecial(pwd);

  Widget _buildPasswordHint(String text, bool isValid) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4.0),
      child: Row(
        children: [
          Icon(
            isValid ? Icons.check_circle_rounded : Icons.radio_button_unchecked_rounded,
            size: 14,
            color: isValid ? AppTheme.success : AppTheme.textSubtle,
          ),
          const SizedBox(width: 6),
          Text(
            text,
            style: TextStyle(
              fontSize: 11,
              fontWeight: isValid ? FontWeight.w600 : FontWeight.normal,
              color: isValid ? AppTheme.success : AppTheme.textMuted,
            ),
          ),
        ],
      ),
    );
  }

  Color _getRoleColor(String? roleName) {
    final lower = (roleName ?? '').toLowerCase();
    if (lower.contains('psic') || lower.contains('terap')) {
      return AppTheme.success;
    } else if (lower.contains('admin')) {
      return AppTheme.secondary;
    } else if (lower.contains('recep')) {
      return AppTheme.warning;
    }
    return AppTheme.primaryLight;
  }

  List<UserModel> get _filteredUsers {
    return _users.where((u) {
      final matchesSearch = _searchQuery.isEmpty ||
          u.nombre.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          u.apellido.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          u.email.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          (u.rolNombre ?? '').toLowerCase().contains(_searchQuery.toLowerCase());

      final matchesFilter = _selectedFilter == 'Todos' ||
          (_selectedFilter == 'Activos' && u.activo) ||
          (_selectedFilter == 'Inactivos' && !u.activo);

      return matchesSearch && matchesFilter;
    }).toList();
  }

  static const List<Map<String, dynamic>> _defaultRoles = [
    {'id': 1, 'nombre': 'Admin Centro'},
    {'id': 2, 'nombre': 'Coordinador Clínico'},
    {'id': 3, 'nombre': 'Psicólogo'},
    {'id': 4, 'nombre': 'Recepcionista'},
    {'id': 5, 'nombre': 'Paciente'},
  ];

  List<Map<String, dynamic>> get effectiveRoles => _roles.isNotEmpty ? _roles : _defaultRoles;

  void _showCreateEditDialog({UserModel? user}) {
    final isEditing = user != null;
    final nombreCtrl = TextEditingController(text: user?.nombre ?? '');
    final apellidoCtrl = TextEditingController(text: user?.apellido ?? '');
    final emailCtrl = TextEditingController(text: isEditing ? user.email : '');
    final passwordCtrl = TextEditingController(text: '');
    final telefonoCtrl = TextEditingController(text: user?.telefono ?? '');

    final rolesToUse = effectiveRoles;
    int? selectedRolId;

    if (isEditing) {
      final matchingRol = rolesToUse.where((r) => r['nombre'] == user.rolNombre);
      if (matchingRol.isNotEmpty) {
        selectedRolId = matchingRol.first['id'] as int;
      } else {
        selectedRolId = rolesToUse.first['id'] as int;
      }
    } else {
      // Para terapeutas y nuevo personal, predeterminar a Psicólogo si existe
      final defaultPsico = rolesToUse.where((r) => (r['nombre'] as String).toLowerCase().contains('psic'));
      selectedRolId = defaultPsico.isNotEmpty ? defaultPsico.first['id'] as int : rolesToUse.first['id'] as int;
    }

    String? errorMsg;
    String currentPassword = '';
    bool obscurePwd = true;

    showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              backgroundColor: AppTheme.cardBg,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22)),
              titlePadding: const EdgeInsets.fromLTRB(24, 20, 24, 10),
              contentPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
              actionsPadding: const EdgeInsets.fromLTRB(24, 10, 24, 20),
              title: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppTheme.primary.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      isEditing ? Icons.edit_note_rounded : Icons.person_add_alt_1_rounded,
                      color: AppTheme.primaryLight,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isEditing ? 'Editar Usuario' : 'Nuevo Usuario / Terapeuta',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 17),
                        ),
                        Text(
                          isEditing ? 'Modificar datos del personal' : 'Registrar en el centro psicológico',
                          style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              content: SizedBox(
                width: double.maxFinite,
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (errorMsg != null)
                        Container(
                          width: double.infinity,
                          margin: const EdgeInsets.only(bottom: 14),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: AppTheme.danger.withOpacity(0.12),
                            border: Border.all(color: AppTheme.danger.withOpacity(0.35)),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Icon(Icons.error_outline_rounded, color: AppTheme.danger, size: 18),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  errorMsg!,
                                  style: const TextStyle(color: Color(0xFFFECDD3), fontSize: 12),
                                ),
                              ),
                            ],
                          ),
                        ),

                      // SECCIÓN 1: Datos Personales
                      const Text(
                        'DATOS PERSONALES',
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 0.5, color: AppTheme.textMuted),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: nombreCtrl,
                        decoration: const InputDecoration(
                          labelText: 'Nombres *',
                          prefixIcon: Icon(Icons.person_outline_rounded, size: 20),
                        ),
                      ),
                      const SizedBox(height: 10),
                      TextField(
                        controller: apellidoCtrl,
                        decoration: const InputDecoration(
                          labelText: 'Apellidos',
                          prefixIcon: Icon(Icons.badge_outlined, size: 20),
                        ),
                      ),
                      const SizedBox(height: 10),
                      TextField(
                        controller: telefonoCtrl,
                        decoration: const InputDecoration(
                          labelText: 'Teléfono',
                          prefixIcon: Icon(Icons.phone_outlined, size: 20),
                        ),
                        keyboardType: TextInputType.phone,
                      ),
                      const SizedBox(height: 16),

                      // SECCIÓN 2: Credenciales y Rol
                      const Text(
                        'CREDENCIALES Y ROL',
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 0.5, color: AppTheme.textMuted),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: emailCtrl,
                        decoration: InputDecoration(
                          labelText: isEditing ? 'Correo Electrónico (no editable)' : 'Correo Electrónico *',
                          prefixIcon: const Icon(Icons.alternate_email_rounded, size: 20),
                        ),
                        keyboardType: TextInputType.emailAddress,
                        readOnly: isEditing,
                        enabled: !isEditing,
                      ),
                      const SizedBox(height: 12),

                      // Selector de Rol (Siempre visible y con roles clínicos)
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'ROL CLÍNICO / ASIGNACIÓN *',
                            style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 0.5, color: AppTheme.textMuted),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: AppTheme.primary.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              _roles.isNotEmpty ? '${_roles.length} Roles Activos' : 'Roles Clínicos',
                              style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w700, color: AppTheme.primaryLight),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      DropdownButtonFormField<int>(
                        value: selectedRolId,
                        decoration: const InputDecoration(
                          labelText: 'Rol en el Centro *',
                          prefixIcon: Icon(Icons.shield_outlined, size: 20),
                        ),
                        dropdownColor: AppTheme.cardBgElevated,
                        items: rolesToUse.map((r) {
                          final rName = r['nombre']?.toString() ?? 'Sin nombre';
                          final rColor = _getRoleColor(rName);
                          return DropdownMenuItem<int>(
                            value: r['id'] as int,
                            child: Row(
                              children: [
                                Container(
                                  width: 9,
                                  height: 9,
                                  decoration: BoxDecoration(
                                    color: rColor,
                                    shape: BoxShape.circle,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(rName, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                              ],
                            ),
                          );
                        }).toList(),
                        onChanged: (v) {
                          setDialogState(() => selectedRolId = v);
                        },
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: passwordCtrl,
                        decoration: InputDecoration(
                          labelText: isEditing ? 'Nueva Contraseña (opcional)' : 'Contraseña *',
                          hintText: isEditing ? 'Dejar vacío para mantener la actual' : 'Mínimo 8 caracteres',
                          prefixIcon: const Icon(Icons.lock_outline_rounded, size: 20),
                          suffixIcon: IconButton(
                            icon: Icon(
                              obscurePwd ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                              size: 20,
                            ),
                            onPressed: () => setDialogState(() => obscurePwd = !obscurePwd),
                          ),
                        ),
                        obscureText: obscurePwd,
                        onChanged: (v) {
                          setDialogState(() => currentPassword = v);
                        },
                      ),
                      if (currentPassword.isNotEmpty) ...[
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: AppTheme.inputBg,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: AppTheme.borderSubtle),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Requisitos de seguridad:', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.textMuted)),
                              const SizedBox(height: 6),
                              _buildPasswordHint('Mínimo 8 caracteres', currentPassword.length >= 8),
                              _buildPasswordHint('Al menos una mayúscula (A-Z)', _hasUppercase(currentPassword)),
                              _buildPasswordHint('Al menos una minúscula (a-z)', _hasLowercase(currentPassword)),
                              _buildPasswordHint('Al menos un número (0-9)', _hasNumber(currentPassword)),
                              _buildPasswordHint('Un carácter especial (!@#\$%^&*)', _hasSpecial(currentPassword)),
                            ],
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx),
                  child: const Text('Cancelar', style: TextStyle(color: AppTheme.textMuted)),
                ),
                ElevatedButton(
                  onPressed: () async {
                    /// ═════════════════════════════════════════════════════════════════════════
                    /// CU3: Gestionar Usuarios (HU-05)
                    /// Diagrama de Comunicación – Creación/Edición de Usuario (Móvil)
                    /// Participantes:
                    ///   Actor  → Administrador del Centro
                    ///   IU     → IU_GestionUsuarios (Móvil)  ← ESTE ARCHIVO
                    ///   CTR    → CTR_UsuarioService (Django REST: UsuarioViewSet)
                    ///   CE     → CE_Usuario_y_Rol (PostgreSQL: accounts_usuario)
                    /// ═════════════════════════════════════════════════════════════════════════
                    // -----------------------------------------------------------------------
                    // CU3 Paso 1: Administrador ingresa datos del usuario/personal en IU_GestionUsuarios
                    // -----------------------------------------------------------------------
                    if (nombreCtrl.text.trim().isEmpty) {
                      setDialogState(() => errorMsg = 'El nombre es obligatorio.');
                      return;
                    }
                    if (selectedRolId == null) {
                      setDialogState(() => errorMsg = 'Debe seleccionar un rol para el personal o terapeuta.');
                      return;
                    }
                    if (!isEditing && emailCtrl.text.trim().isEmpty) {
                      setDialogState(() => errorMsg = 'El correo es obligatorio.');
                      return;
                    }
                    if (!isEditing && passwordCtrl.text.trim().isEmpty) {
                      setDialogState(() => errorMsg = 'La contraseña es obligatoria.');
                      return;
                    }
                    if (passwordCtrl.text.isNotEmpty && !_isPasswordValid(passwordCtrl.text)) {
                      setDialogState(() => errorMsg = 'La contraseña debe cumplir todos los requisitos de seguridad.');
                      return;
                    }

                    try {
                      // ---------------------------------------------------------------------
                      // CU3 Paso 2: IU_GestionUsuarios envía solicitud POST/PUT a CTR_UsuarioService
                      // ---------------------------------------------------------------------
                      http.Response response;
                      if (isEditing) {
                        final url = Uri.parse('${widget.authService.baseUrl}${ApiConstants.users}${user.id}/');
                        final body = <String, dynamic>{
                          'nombre': nombreCtrl.text.trim(),
                          'apellido': apellidoCtrl.text.trim(),
                          'telefono': telefonoCtrl.text.trim(),
                          'rol_id': selectedRolId,
                        };
                        if (passwordCtrl.text.isNotEmpty) {
                          body['password'] = passwordCtrl.text.trim();
                        }
                        response = await http.put(
                          url,
                          headers: widget.authService.getHeaders(),
                          body: jsonEncode(body),
                        );
                      } else {
                        final url = Uri.parse('${widget.authService.baseUrl}${ApiConstants.users}');
                        final body = {
                          'nombre': nombreCtrl.text.trim(),
                          'apellido': apellidoCtrl.text.trim(),
                          'email': emailCtrl.text.trim(),
                          'password': passwordCtrl.text.trim(),
                          'telefono': telefonoCtrl.text.trim(),
                          'rol_id': selectedRolId,
                        };
                        response = await http.post(
                          url,
                          headers: widget.authService.getHeaders(),
                          body: jsonEncode(body),
                        );
                      }

                      if (response.statusCode == 200 || response.statusCode == 201) {
                        // -------------------------------------------------------------------
                        // CU3 Paso 11: CTR_UsuarioService retorna 201 Created / 200 OK con usuario registrado
                        // CU3 Paso 12: IU_GestionUsuarios muestra confirmación visual y refresca listado
                        // -------------------------------------------------------------------
                        if (ctx.mounted) Navigator.pop(ctx);
                        _loadUsers();
                        if (mounted) {
                          ScaffoldMessenger.of(this.context).showSnackBar(
                            SnackBar(
                              content: Text(isEditing ? 'Usuario actualizado exitosamente.' : 'Usuario registrado exitosamente.'),
                              backgroundColor: AppTheme.success,
                              behavior: SnackBarBehavior.floating,
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                          );
                        }
                      } else {
                        String msg = 'Error al guardar.';
                        try {
                          final errData = jsonDecode(response.body);
                          if (errData is Map) {
                            final parts = <String>[];
                            errData.forEach((key, val) {
                              if (val is List) {
                                parts.add('$key: ${val.join(", ")}');
                              } else if (val is String) {
                                parts.add('$key: $val');
                              }
                            });
                            if (parts.isNotEmpty) msg = parts.join('\n');
                          }
                        } catch (_) {}
                        setDialogState(() => errorMsg = msg);
                      }
                    } catch (e) {
                      setDialogState(() => errorMsg = 'Error de conexión: $e');
                    }
                  },
                  child: Text(isEditing ? 'Guardar Cambios' : 'Registrar Usuario'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final usersToShow = _filteredUsers;
    final totalCount = _users.length;
    final activeCount = _users.where((u) => u.activo).length;

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Personal y Terapeutas'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Actualizar lista',
            onPressed: () {
              _loadUsers();
              _loadRoles();
            },
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showCreateEditDialog(),
        backgroundColor: AppTheme.primary,
        icon: const Icon(Icons.person_add_rounded, color: Colors.white),
        label: const Text(
          'NUEVO USUARIO',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 13),
        ),
      ),
      body: Column(
        children: [
          // Barra de Búsqueda y Filtros
          Container(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
            decoration: const BoxDecoration(
              color: AppTheme.cardBg,
              border: Border(bottom: BorderSide(color: AppTheme.borderSubtle)),
            ),
            child: Column(
              children: [
                // Buscador
                TextField(
                  onChanged: (val) => setState(() => _searchQuery = val),
                  decoration: InputDecoration(
                    hintText: 'Buscar por nombre, correo o rol...',
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

                // Filtros y Métricas
                Row(
                  children: [
                    Expanded(
                      child: SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Row(
                          children: ['Todos', 'Activos', 'Inactivos'].map((filter) {
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
                    ),
                    // Counter pill
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppTheme.inputBg,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: AppTheme.borderSubtle),
                      ),
                      child: Text(
                        '$activeCount/$totalCount Activos',
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.textMuted),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Lista de Usuarios
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : usersToShow.isEmpty
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
                              child: const Icon(Icons.person_search_rounded, size: 48, color: AppTheme.textMuted),
                            ),
                            const SizedBox(height: 16),
                            const Text(
                              'No se encontraron usuarios',
                              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                            ),
                            const SizedBox(height: 4),
                            const Text(
                              'Prueba ajustando el término de búsqueda o filtros.',
                              style: TextStyle(color: AppTheme.textMuted, fontSize: 12),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.fromLTRB(16, 16, 16, 80),
                        itemCount: usersToShow.length,
                        itemBuilder: (context, index) {
                          final u = usersToShow[index];
                          final roleColor = _getRoleColor(u.rolNombre);

                          return Container(
                            margin: const EdgeInsets.only(bottom: 12),
                            decoration: BoxDecoration(
                              color: AppTheme.cardBg,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: AppTheme.borderSubtle),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.15),
                                  blurRadius: 8,
                                  offset: const Offset(0, 2),
                                ),
                              ],
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(14.0),
                              child: Column(
                                children: [
                                  Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      // Avatar con anillo de rol
                                      Container(
                                        padding: const EdgeInsets.all(2),
                                        decoration: BoxDecoration(
                                          shape: BoxShape.circle,
                                          border: Border.all(color: roleColor, width: 2),
                                        ),
                                        child: CircleAvatar(
                                          radius: 22,
                                          backgroundColor: roleColor.withOpacity(0.15),
                                          child: Text(
                                            u.nombre.isNotEmpty ? u.nombre[0].toUpperCase() : 'U',
                                            style: TextStyle(
                                              color: roleColor,
                                              fontWeight: FontWeight.w800,
                                              fontSize: 16,
                                            ),
                                          ),
                                        ),
                                      ),
                                      const SizedBox(width: 12),

                                      // Datos del Usuario
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Row(
                                              children: [
                                                Expanded(
                                                  child: Text(
                                                    '${u.nombre} ${u.apellido}'.trim(),
                                                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                                                    overflow: TextOverflow.ellipsis,
                                                  ),
                                                ),
                                                // Live Status Pill
                                                Container(
                                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                                  decoration: BoxDecoration(
                                                    color: u.activo ? AppTheme.success.withOpacity(0.12) : AppTheme.danger.withOpacity(0.12),
                                                    borderRadius: BorderRadius.circular(12),
                                                    border: Border.all(
                                                      color: u.activo ? AppTheme.success.withOpacity(0.3) : AppTheme.danger.withOpacity(0.3),
                                                    ),
                                                  ),
                                                  child: Row(
                                                    mainAxisSize: MainAxisSize.min,
                                                    children: [
                                                      Container(
                                                        width: 6,
                                                        height: 6,
                                                        decoration: BoxDecoration(
                                                          color: u.activo ? AppTheme.success : AppTheme.danger,
                                                          shape: BoxShape.circle,
                                                        ),
                                                      ),
                                                      const SizedBox(width: 4),
                                                      Text(
                                                        u.activo ? 'Activo' : 'Inactivo',
                                                        style: TextStyle(
                                                          fontSize: 10,
                                                          fontWeight: FontWeight.w700,
                                                          color: u.activo ? AppTheme.success : AppTheme.danger,
                                                        ),
                                                      ),
                                                    ],
                                                  ),
                                                ),
                                              ],
                                            ),
                                            const SizedBox(height: 4),
                                            // Correo
                                            Row(
                                              children: [
                                                const Icon(Icons.alternate_email_rounded, size: 13, color: AppTheme.textSubtle),
                                                const SizedBox(width: 4),
                                                Expanded(
                                                  child: Text(
                                                    u.email,
                                                    style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                                                    overflow: TextOverflow.ellipsis,
                                                  ),
                                                ),
                                              ],
                                            ),
                                            if (u.telefono != null && u.telefono!.isNotEmpty) ...[
                                              const SizedBox(height: 2),
                                              Row(
                                                children: [
                                                  const Icon(Icons.phone_outlined, size: 13, color: AppTheme.textSubtle),
                                                  const SizedBox(width: 4),
                                                  Text(
                                                    u.telefono!,
                                                    style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                                                  ),
                                                ],
                                              ),
                                            ],
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),
                                  const Divider(height: 1, color: AppTheme.borderSubtle),
                                  const SizedBox(height: 8),

                                  // Barra Inferior de la Tarjeta (Rol e Interacciones)
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      // Rol Badge
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                        decoration: BoxDecoration(
                                          color: roleColor.withOpacity(0.12),
                                          borderRadius: BorderRadius.circular(8),
                                          border: Border.all(color: roleColor.withOpacity(0.25)),
                                        ),
                                        child: Row(
                                          mainAxisSize: MainAxisSize.min,
                                          children: [
                                            Icon(Icons.shield_outlined, size: 12, color: roleColor),
                                            const SizedBox(width: 4),
                                            Text(
                                              u.rolNombre ?? 'Sin Rol Asignado',
                                              style: TextStyle(
                                                fontSize: 11,
                                                fontWeight: FontWeight.w700,
                                                color: roleColor,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),

                                      // Botones de Acción
                                      Row(
                                        children: [
                                          InkWell(
                                            onTap: () => _showCreateEditDialog(user: u),
                                            borderRadius: BorderRadius.circular(8),
                                            child: Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                              decoration: BoxDecoration(
                                                color: AppTheme.primary.withOpacity(0.12),
                                                borderRadius: BorderRadius.circular(8),
                                              ),
                                              child: const Row(
                                                children: [
                                                  Icon(Icons.edit_rounded, size: 14, color: AppTheme.primaryLight),
                                                  SizedBox(width: 4),
                                                  Text(
                                                    'Editar',
                                                    style: TextStyle(fontSize: 11, color: AppTheme.primaryLight, fontWeight: FontWeight.bold),
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ),
                                          const SizedBox(width: 8),
                                          InkWell(
                                            onTap: () => _toggleStatus(u),
                                            borderRadius: BorderRadius.circular(8),
                                            child: Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                              decoration: BoxDecoration(
                                                color: u.activo ? AppTheme.danger.withOpacity(0.12) : AppTheme.success.withOpacity(0.12),
                                                borderRadius: BorderRadius.circular(8),
                                              ),
                                              child: Row(
                                                children: [
                                                  Icon(
                                                    u.activo ? Icons.block_rounded : Icons.check_circle_outline_rounded,
                                                    size: 14,
                                                    color: u.activo ? AppTheme.danger : AppTheme.success,
                                                  ),
                                                  const SizedBox(width: 4),
                                                  Text(
                                                    u.activo ? 'Desactivar' : 'Activar',
                                                    style: TextStyle(
                                                      fontSize: 11,
                                                      color: u.activo ? AppTheme.danger : AppTheme.success,
                                                      fontWeight: FontWeight.bold,
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
