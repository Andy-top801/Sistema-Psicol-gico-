/// Perfil del usuario autenticado, tal como lo devuelve `/users/me/` y el
/// campo `user` de `/users/auth/register/` (UserProfileSerializer).
class Usuario {
  final String id;
  final String email;
  final String firstName;
  final String lastName;
  final String phone;
  final List<String> roles;

  const Usuario({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.phone,
    required this.roles,
  });

  bool get esPaciente => roles.contains('Paciente');

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
    );
  }
}
