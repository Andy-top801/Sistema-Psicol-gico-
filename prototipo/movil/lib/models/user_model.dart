class UserModel {
  final String id;
  final String email;
  final String nombre;
  final String apellido;
  final String? telefono;
  final String? rolNombre;
  final bool activo;

  UserModel({
    required this.id,
    required this.email,
    required this.nombre,
    required this.apellido,
    this.telefono,
    this.rolNombre,
    required this.activo,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    String? rName;
    if (json['rol_detalle'] != null) {
      rName = json['rol_detalle']['nombre'];
    } else if (json['rol'] != null && json['rol'] is Map) {
      rName = json['rol']['nombre'];
    } else if (json['rol'] != null && json['rol'] is String) {
      rName = json['rol'];
    }

    return UserModel(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      nombre: json['nombre'] ?? '',
      apellido: json['apellido'] ?? '',
      telefono: json['telefono'],
      rolNombre: rName,
      activo: json['activo'] ?? true,
    );
  }
}
