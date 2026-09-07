class PacienteModel {
  final String id;
  final String? usuarioId;
  final String nombre;
  final String apellido;
  final String email;
  final String telefono;
  final String codigoExpediente;
  final String ci;
  final String? fechaNacimiento;
  final String genero;
  final String contactoEmergenciaNombre;
  final String contactoEmergenciaTelf;
  final String tutorLegalNombre;
  final String tutorLegalCi;
  final String? fechaRegistro;
  final int? edad;
  final bool esMenorDeEdad;

  PacienteModel({
    required this.id,
    this.usuarioId,
    required this.nombre,
    required this.apellido,
    required this.email,
    required this.telefono,
    required this.codigoExpediente,
    required this.ci,
    this.fechaNacimiento,
    required this.genero,
    required this.contactoEmergenciaNombre,
    required this.contactoEmergenciaTelf,
    required this.tutorLegalNombre,
    required this.tutorLegalCi,
    this.fechaRegistro,
    this.edad,
    required this.esMenorDeEdad,
  });

  String get nombreCompleto => '$nombre $apellido'.trim();
  bool get esMenor => esMenorDeEdad || (edad != null && edad! < 18);

  factory PacienteModel.fromJson(Map<String, dynamic> json) {
    // Usuario info may come nested or flattened
    final u = json['usuario'] is Map<String, dynamic>
        ? json['usuario']
        : (json['usuario_datos'] is Map<String, dynamic> ? json['usuario_datos'] : null);

    return PacienteModel(
      id: json['id']?.toString() ?? '',
      usuarioId: json['usuario_id']?.toString() ?? u?['id']?.toString(),
      nombre: json['nombre']?.toString() ?? u?['nombre']?.toString() ?? '',
      apellido: json['apellido']?.toString() ?? u?['apellido']?.toString() ?? '',
      email: json['email']?.toString() ?? u?['email']?.toString() ?? '',
      telefono: json['telefono']?.toString() ?? u?['telefono']?.toString() ?? '',
      codigoExpediente: json['codigo_expediente']?.toString() ?? '',
      ci: json['ci']?.toString() ?? '',
      fechaNacimiento: json['fecha_nacimiento']?.toString(),
      genero: json['genero']?.toString() ?? 'O',
      contactoEmergenciaNombre: json['contacto_emergencia_nombre']?.toString() ?? '',
      contactoEmergenciaTelf: json['contacto_emergencia_telf']?.toString() ?? '',
      tutorLegalNombre: json['tutor_legal_nombre']?.toString() ?? '',
      tutorLegalCi: json['tutor_legal_ci']?.toString() ?? '',
      fechaRegistro: json['fecha_registro']?.toString(),
      edad: json['edad'] is int ? json['edad'] : int.tryParse(json['edad']?.toString() ?? ''),
      esMenorDeEdad: json['es_menor_de_edad'] == true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'ci': ci,
      'fecha_nacimiento': fechaNacimiento,
      'genero': genero,
      'contacto_emergencia_nombre': contactoEmergenciaNombre,
      'contacto_emergencia_telf': contactoEmergenciaTelf,
      'tutor_legal_nombre': tutorLegalNombre,
      'tutor_legal_ci': tutorLegalCi,
      'nombre': nombre,
      'apellido': apellido,
      'telefono': telefono,
      'email': email,
    };
  }
}
