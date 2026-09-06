/// Perfil del usuario autenticado, tal como lo devuelve `/users/me/` y el
/// campo `user` de `/users/auth/register/` (UserProfileSerializer).
class Usuario {
  final String id;
  final String email;
  final String firstName;
  final String lastName;
  final String phone;
  final List<String> roles;
  final bool isSuperuser;
  final bool isStaff;
  final String? pacienteId;

  const Usuario({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.phone,
    required this.roles,
    this.isSuperuser = false,
    this.isStaff = false,
    this.pacienteId,
  });

  /// Normaliza un nombre de rol: sin acentos, minúsculas, sin espacios.
  static String _norm(String value) {
    const from = 'áàäâéèëêíìïîóòöôúùüûñ';
    const to = 'aaaaeeeeiiiioooouuuun';
    var s = value.toLowerCase();
    for (var i = 0; i < from.length; i++) {
      s = s.replaceAll(from[i], to[i]);
    }
    return s.replaceAll(RegExp(r'\s+'), '');
  }

  List<String> get rolesNormalizados => roles.map(_norm).toList();

  bool get esPaciente => rolesNormalizados.contains('paciente');

  bool get esStaff =>
      isSuperuser ||
      isStaff ||
      rolesNormalizados.any(
        (r) => const {
          'superadmin',
          'admincentro',
          'coordinador',
          'psicologo',
          'recepcionista',
        }.contains(r),
      );

  factory Usuario.fromJson(Map<String, dynamic> json) {
    return Usuario(
      id: json['id'].toString(),
      email: json['email'] as String,
      firstName: (json['first_name'] as String?) ?? '',
      lastName: (json['last_name'] as String?) ?? '',
      phone: (json['phone'] as String?) ?? '',
      roles: (json['roles'] as List<dynamic>? ?? [])
          .map((r) => r.toString())
          .toList(),
      isSuperuser: json['is_superuser'] as bool? ?? false,
      isStaff: json['is_staff'] as bool? ?? false,
      pacienteId: json['paciente_id']?.toString(),
    );
  }
}
