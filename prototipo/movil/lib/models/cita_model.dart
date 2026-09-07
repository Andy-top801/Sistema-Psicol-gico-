class CitaModel {
  final String id;
  final String pacienteId;
  final String pacienteNombre;
  final String pacienteExpediente;
  final String psicologoId;
  final String psicologoNombre;
  final String fecha; // YYYY-MM-DD
  final String horaInicio; // HH:MM:SS
  final String horaFin; // HH:MM:SS
  final String modalidad; // PRESENCIAL o VIRTUAL
  final String estado; // PROGRAMADA, CONFIRMADA, REALIZADA, CANCELADA, INASISTENCIA
  final String motivoConsulta;
  final double costo;
  final String? motivoCancelacion;
  final Map<String, dynamic>? teleconsulta;

  CitaModel({
    required this.id,
    required this.pacienteId,
    required this.pacienteNombre,
    required this.pacienteExpediente,
    required this.psicologoId,
    required this.psicologoNombre,
    required this.fecha,
    required this.horaInicio,
    required this.horaFin,
    required this.modalidad,
    required this.estado,
    required this.motivoConsulta,
    required this.costo,
    this.motivoCancelacion,
    this.teleconsulta,
  });

  bool get isVirtual => modalidad.toUpperCase() == 'VIRTUAL';
  bool get isRealizada => estado.toUpperCase() == 'REALIZADA';
  bool get isCancelada => estado.toUpperCase() == 'CANCELADA';
  bool get isActiva => estado.toUpperCase() == 'PROGRAMADA' || estado.toUpperCase() == 'CONFIRMADA';

  /// HU-18 / HU-19: Verifica si la teleconsulta está habilitada
  /// (Habilitada desde 15 minutos antes de la hora de inicio y durante el transcurso)
  bool get isTeleconsultaReady {
    if (!isVirtual || !isActiva) return false;
    try {
      final partsDate = fecha.split('-');
      final partsTime = horaInicio.split(':');
      if (partsDate.length < 3 || partsTime.length < 2) return false;

      final citaStart = DateTime(
        int.parse(partsDate[0]),
        int.parse(partsDate[1]),
        int.parse(partsDate[2]),
        int.parse(partsTime[0]),
        int.parse(partsTime[1]),
      );

      final now = DateTime.now();
      final diff = citaStart.difference(now);

      // Si faltan 15 min o menos, o si la cita ya comenzó (hasta 2 horas posteriores)
      return diff.inMinutes <= 15 && diff.inMinutes >= -120;
    } catch (_) {
      return false;
    }
  }

  String get horaInicioCorta {
    final parts = horaInicio.split(':');
    return parts.length >= 2 ? '${parts[0]}:${parts[1]}' : horaInicio;
  }

  String get horaFinCorta {
    final parts = horaFin.split(':');
    return parts.length >= 2 ? '${parts[0]}:${parts[1]}' : horaFin;
  }

  factory CitaModel.fromJson(Map<String, dynamic> json) {
    String pNombre = json['paciente_nombre']?.toString() ?? '';
    String pExp = json['paciente_expediente']?.toString() ?? '';
    String pId = json['paciente']?.toString() ?? '';
    if (json['paciente_datos'] is Map<String, dynamic>) {
      final pd = json['paciente_datos'];
      pNombre = pd['nombre']?.toString() ?? pNombre;
      pExp = pd['codigo_expediente']?.toString() ?? pExp;
      pId = pd['id']?.toString() ?? pId;
    }

    String psiNombre = json['psicologo_nombre']?.toString() ?? '';
    String psiId = json['psicologo']?.toString() ?? '';
    if (json['psicologo_datos'] is Map<String, dynamic>) {
      final psd = json['psicologo_datos'];
      psiNombre = psd['nombre']?.toString() ?? psiNombre;
      psiId = psd['id']?.toString() ?? psiId;
    }

    double c = 0.0;
    if (json['costo'] != null) {
      c = double.tryParse(json['costo'].toString()) ?? 0.0;
    }

    return CitaModel(
      id: json['id']?.toString() ?? '',
      pacienteId: pId,
      pacienteNombre: pNombre,
      pacienteExpediente: pExp,
      psicologoId: psiId,
      psicologoNombre: psiNombre,
      fecha: json['fecha']?.toString() ?? '',
      horaInicio: json['hora_inicio']?.toString() ?? '',
      horaFin: json['hora_fin']?.toString() ?? '',
      modalidad: json['modalidad']?.toString() ?? 'PRESENCIAL',
      estado: json['estado']?.toString() ?? 'PROGRAMADA',
      motivoConsulta: json['motivo_consulta']?.toString() ?? '',
      costo: c,
      motivoCancelacion: json['motivo_cancelacion']?.toString(),
      teleconsulta: json['teleconsulta'] is Map<String, dynamic> ? json['teleconsulta'] : null,
    );
  }
}
