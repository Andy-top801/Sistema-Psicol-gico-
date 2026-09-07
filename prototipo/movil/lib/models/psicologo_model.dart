class PsicologoModel {
  final String id;
  final String usuarioId;
  final String nombre;
  final String apellido;
  final String email;
  final String telefono;
  final String numeroColegiado;
  final double tarifaBase;
  final String modalidad;
  final List<String> especialidades;
  final String biografia;

  PsicologoModel({
    required this.id,
    required this.usuarioId,
    required this.nombre,
    required this.apellido,
    required this.email,
    required this.telefono,
    required this.numeroColegiado,
    required this.tarifaBase,
    required this.modalidad,
    required this.especialidades,
    required this.biografia,
  });

  String get nombreCompleto => '$nombre $apellido'.trim();

  factory PsicologoModel.fromJson(Map<String, dynamic> json) {
    final u = json['usuario'] is Map<String, dynamic>
        ? json['usuario']
        : (json['usuario_datos'] is Map<String, dynamic> ? json['usuario_datos'] : null);

    List<String> espList = [];
    if (json['especialidades_detalle'] is List) {
      espList = (json['especialidades_detalle'] as List)
          .map((e) => e['nombre']?.toString() ?? '')
          .where((s) => s.isNotEmpty)
          .toList();
    } else if (json['especialidades'] is List) {
      espList = (json['especialidades'] as List)
          .map((e) => e is Map ? (e['nombre']?.toString() ?? '') : e.toString())
          .where((s) => s.isNotEmpty)
          .toList();
    }

    double tarifa = 0.0;
    if (json['tarifa_base'] != null) {
      tarifa = double.tryParse(json['tarifa_base'].toString()) ?? 0.0;
    }

    return PsicologoModel(
      id: json['id']?.toString() ?? '',
      usuarioId: u?['id']?.toString() ?? json['usuario_id']?.toString() ?? '',
      nombre: u?['nombre']?.toString() ?? json['nombre']?.toString() ?? '',
      apellido: u?['apellido']?.toString() ?? json['apellido']?.toString() ?? '',
      email: u?['email']?.toString() ?? json['email']?.toString() ?? '',
      telefono: u?['telefono']?.toString() ?? json['telefono']?.toString() ?? '',
      numeroColegiado: json['numero_colegiado']?.toString() ?? '',
      tarifaBase: tarifa,
      modalidad: json['modalidad']?.toString() ?? 'HIBRIDA',
      especialidades: espList,
      biografia: json['biografia']?.toString() ?? '',
    );
  }
}
