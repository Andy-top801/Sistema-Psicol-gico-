/// Par de tokens JWT devuelto por `/auth/login/`, `/auth/register/` y
/// `/auth/refresh/` (mismas claves que ya usa el login web en Angular).
class AuthTokens {
  final String access;
  final String refresh;

  const AuthTokens({required this.access, required this.refresh});

  factory AuthTokens.fromJson(Map<String, dynamic> json) {
    return AuthTokens(
      access: json['access'] as String,
      refresh: json['refresh'] as String,
    );
  }
}
