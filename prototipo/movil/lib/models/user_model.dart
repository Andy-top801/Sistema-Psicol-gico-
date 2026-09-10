class UserModel {
  final String id;
  final String email;
  final String nombre;
  final String apellido;
  final String? telefono;
  final String? rolNombre;
  final List<String> permisos;
  final bool activo;

  UserModel({
    required this.id,
    required this.email,
    required this.nombre,
    required this.apellido,
    this.telefono,
    this.rolNombre,
    this.permisos = const [],
    required this.activo,
  });

  bool get isSuperAdmin => rolNombre?.toLowerCase().contains('superadmin') ?? false;
  bool get isAdminCentro => (rolNombre?.toLowerCase().contains('admin') ?? false) && !isSuperAdmin;
  bool get isPsicologo => rolNombre?.toLowerCase().contains('psic') ?? false;
  bool get isPaciente => rolNombre?.toLowerCase().contains('paciente') ?? false;
  bool get isRecepcionista => rolNombre?.toLowerCase().contains('recep') ?? false;
  bool get isCoordinador => rolNombre?.toLowerCase().contains('coord') ?? false;

  bool hasPermission(String codigo) =>
      isSuperAdmin || isAdminCentro || permisos.contains(codigo);

  factory UserModel.fromJson(Map<String, dynamic> json) {
    String? rName;
    List<String> permsList = [];

    if (json['rol_detalle'] != null) {
      rName = json['rol_detalle']['nombre'];
      if (json['rol_detalle']['permisos'] != null && json['rol_detalle']['permisos'] is List) {
        for (var p in json['rol_detalle']['permisos']) {
          if (p is Map && p['codigo'] != null) {
            permsList.add(p['codigo'].toString());
          } else if (p is String) {
            permsList.add(p);
          }
        }
      }
    } else if (json['rol'] != null && json['rol'] is Map) {
      rName = json['rol']['nombre'];
    } else if (json['rol'] != null && json['rol'] is String) {
      rName = json['rol'];
    }

    if (json['permisos'] != null && json['permisos'] is List) {
      for (var p in json['permisos']) {
        if (p is String) {
          if (!permsList.contains(p)) permsList.add(p);
        } else if (p is Map && p['codigo'] != null) {
          final c = p['codigo'].toString();
          if (!permsList.contains(c)) permsList.add(c);
        }
      }
    }

    return UserModel(
      id: json['id']?.toString() ?? '',
      email: json['email'] ?? '',
      nombre: json['nombre'] ?? '',
      apellido: json['apellido'] ?? '',
      telefono: json['telefono'],
      rolNombre: rName,
      permisos: permsList,
      activo: json['activo'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'nombre': nombre,
      'apellido': apellido,
      'telefono': telefono,
      'rol': rolNombre,
      'rol_detalle': {
        'nombre': rolNombre,
      },
      'permisos': permisos,
      'activo': activo,
    };
  }
}
