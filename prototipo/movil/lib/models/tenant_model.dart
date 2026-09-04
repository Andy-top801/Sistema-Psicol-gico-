class TenantModel {
  final String id;
  final String nombre;
  final String slug;
  final String schemaName;
  final String? direccion;
  final String? telefono;
  final String? emailContacto;
  final String plan;
  final bool activo;

  TenantModel({
    required this.id,
    required this.nombre,
    required this.slug,
    required this.schemaName,
    this.direccion,
    this.telefono,
    this.emailContacto,
    this.plan = 'PRO',
    this.activo = true,
  });

  factory TenantModel.fromJson(Map<String, dynamic> json) {
    return TenantModel(
      id: json['id'] ?? '',
      nombre: json['nombre'] ?? '',
      slug: json['slug'] ?? '',
      schemaName: json['schema_name'] ?? '',
      direccion: json['direccion'],
      telefono: json['telefono'],
      emailContacto: json['email_contacto'],
      plan: json['plan'] ?? 'PRO',
      activo: json['activo'] ?? true,
    );
  }
}
