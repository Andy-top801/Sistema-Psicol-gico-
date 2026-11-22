import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants/api_constants.dart';
import 'auth_service.dart';

class Sprint4Service {
  final AuthService authService;

  Sprint4Service({required this.authService});

  Map<String, String> get _headers => authService.getHeaders();
  String get _base => authService.baseUrl;

  Map<String, dynamic> _parseError(http.Response r, String fallback) {
    try {
      final body = jsonDecode(utf8.decode(r.bodyBytes));
      if (body is Map) {
        final msg = body['detail'] ?? body['error'] ?? body.values.first;
        return {'success': false, 'error': msg.toString()};
      }
    } catch (_) {}
    return {'success': false, 'error': '$fallback (HTTP ${r.statusCode})'};
  }

  // =========================================================================
  // HU-52: CAJA CLÍNICA, COBROS Y EXTRACTO HISTÓRICO TIPO BANCO (20 AÑOS)
  // =========================================================================
  Future<List<Map<String, dynamic>>> getCuentas({String q = '', bool sync = false}) async {
    final qp = <String, String>{};
    if (q.isNotEmpty) qp['q'] = q;
    if (sync) qp['sync'] = 'true';
    final uri = Uri.parse('$_base${ApiConstants.finanzasCuentas}').replace(queryParameters: qp.isEmpty ? null : qp);
    final r = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(utf8.decode(r.bodyBytes)));
    }
    throw Exception(_parseError(r, 'Error al cargar cuentas')['error']);
  }

  Future<Map<String, dynamic>> getCuentaDetalle(String pacienteId) async {
    final uri = Uri.parse('$_base${ApiConstants.finanzasCuentas}$pacienteId/');
    final r = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      return Map<String, dynamic>.from(jsonDecode(utf8.decode(r.bodyBytes)));
    }
    throw Exception(_parseError(r, 'Error al cargar detalle de cuenta')['error']);
  }

  // CU26A-paso 2: Registra cobro directo soportando moneda origen BOB/USD (T.C. 6.96)
  Future<Map<String, dynamic>> registrarPago({
    required String pacienteId,
    required double monto,
    required String metodoPago,
    String monedaOrigen = 'BOB',
    String referenciaExterna = '',
    String observaciones = '',
  }) async {
    final uri = Uri.parse('$_base${ApiConstants.finanzasPagos}');
    final r = await http.post(
      uri,
      headers: _headers,
      body: jsonEncode({
        'paciente_id': pacienteId,
        'monto': monto,
        'moneda_origen': monedaOrigen,
        'metodo_pago': metodoPago,
        'referencia_externa': referenciaExterna,
        'observaciones': observaciones,
      }),
    ).timeout(const Duration(seconds: 20));
    if (r.statusCode == 201 || r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al registrar cobro');
  }

  // CU26-A: Extracto de Planes Terapéuticos y Tabla de Amortización (BOB/USD)
  Future<Map<String, dynamic>> getExtractoAmortizacion(String pacienteId) async {
    final uri = Uri.parse('$_base${ApiConstants.finanzasExtractoPaciente}$pacienteId/');
    final r = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      return Map<String, dynamic>.from(jsonDecode(utf8.decode(r.bodyBytes)));
    }
    throw Exception(_parseError(r, 'Error al cargar planes de amortización')['error']);
  }

  Future<Map<String, dynamic>> crearPlanAmortizacion({
    required String pacienteId,
    required String nombrePlan,
    required double montoTotal,
    String moneda = 'USD',
    int numeroCuotas = 6,
    int sesionesIncluidas = 6,
    double tasaInteresAnual = 0.0,
    double porcentajeSeguro = 1.5,
  }) async {
    final uri = Uri.parse('$_base${ApiConstants.finanzasPlanesAmortizacion}');
    final r = await http.post(
      uri,
      headers: _headers,
      body: jsonEncode({
        'paciente_id': pacienteId,
        'nombre_plan': nombrePlan,
        'monto_total': montoTotal,
        'moneda': moneda,
        'numero_cuotas': numeroCuotas,
        'sesiones_incluidas': sesionesIncluidas,
        'tasa_interes_anual': tasaInteresAnual,
        'porcentaje_seguro': porcentajeSeguro,
      }),
    ).timeout(const Duration(seconds: 20));
    if (r.statusCode == 201 || r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al generar plan de amortización');
  }

  // CU26A-paso 2: Pagar cuota con conversión USD -> BOB (T.C. 6.96)
  Future<Map<String, dynamic>> pagarCuotaMultimoneda({
    required String cuotaId,
    required String moneda,
    String metodoPago = 'QR_BANCARIO',
    String referenciaExterna = '',
  }) async {
    final uri = Uri.parse('$_base${ApiConstants.finanzasPagosRegistrar}');
    final r = await http.post(
      uri,
      headers: _headers,
      body: jsonEncode({
        'cuota_id': cuotaId,
        'moneda': moneda,
        'metodo_pago': metodoPago,
        'referencia_externa': referenciaExterna,
      }),
    ).timeout(const Duration(seconds: 20));
    if (r.statusCode == 201 || r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al liquidar cuota');
  }

  Future<Map<String, dynamic>> getExtractoBancario({
    String? pacienteId,
    String? fechaDesde,
    String? fechaHasta,
    int page = 1,
    int pageSize = 25,
  }) async {
    final qp = <String, String>{
      'page': '$page',
      'page_size': '$pageSize',
    };
    if (pacienteId != null && pacienteId.isNotEmpty) qp['paciente_id'] = pacienteId;
    if (fechaDesde != null && fechaDesde.isNotEmpty) qp['fecha_desde'] = fechaDesde;
    if (fechaHasta != null && fechaHasta.isNotEmpty) qp['fecha_hasta'] = fechaHasta;

    final uri = Uri.parse('$_base${ApiConstants.finanzasExtracto}').replace(queryParameters: qp);
    final r = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 30));
    if (r.statusCode == 200) {
      return Map<String, dynamic>.from(jsonDecode(utf8.decode(r.bodyBytes)));
    }
    throw Exception(_parseError(r, 'Error al consultar extracto')['error']);
  }

  // =========================================================================
  // HU-53 / CU26-B: DASHBOARD FINANCIERO, GASTOS FIJOS Y CRM (1-5★ CSAT/NPS)
  // =========================================================================
  // CU26B-paso 2: Consulta Estado de Resultados y métrica CRM consolidada
  Future<Map<String, dynamic>> getDashboardFinanciero({String horizonte = '24m'}) async {
    final uri = Uri.parse('$_base${ApiConstants.finanzasDashboard}')
        .replace(queryParameters: {'horizonte': horizonte});
    final r = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 25));
    if (r.statusCode == 200) {
      return Map<String, dynamic>.from(jsonDecode(utf8.decode(r.bodyBytes)));
    }
    throw Exception(_parseError(r, 'Error al cargar dashboard financiero')['error']);
  }

  Future<Map<String, dynamic>> registrarGastoFijo({
    required String categoria,
    required String descripcion,
    required double monto,
    String moneda = 'BOB',
  }) async {
    final uri = Uri.parse('$_base${ApiConstants.finanzasGastosFijos}');
    final r = await http.post(
      uri,
      headers: _headers,
      body: jsonEncode({
        'categoria': categoria,
        'descripcion': descripcion,
        'monto': monto,
        'moneda': moneda,
      }),
    ).timeout(const Duration(seconds: 20));
    if (r.statusCode == 201 || r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al registrar gasto fijo');
  }

  // CU26B-paso 1, 15: Envía encuesta de satisfacción CRM 1-5★ desde la app
  Future<Map<String, dynamic>> registrarCalificacionCRM({
    String? pacienteId,
    required int puntuacionEstrellas,
    String comentario = '',
  }) async {
    final uri = Uri.parse('$_base${ApiConstants.crmCalificaciones}');
    final body = <String, dynamic>{
      'puntuacion_estrellas': puntuacionEstrellas,
      'comentario': comentario,
    };
    if (pacienteId != null && pacienteId.isNotEmpty) body['paciente_id'] = pacienteId;
    final r = await http.post(uri, headers: _headers, body: jsonEncode(body)).timeout(const Duration(seconds: 20));
    if (r.statusCode == 201 || r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al enviar calificación CRM');
  }

  Future<Map<String, dynamic>> atenderTicketCRM(String calificacionId, String notaSeguimiento) async {
    final uri = Uri.parse('$_base${ApiConstants.crmCalificaciones}$calificacionId/atender/');
    final r = await http.patch(
      uri,
      headers: _headers,
      body: jsonEncode({'nota_seguimiento': notaSeguimiento}),
    ).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al atender alerta CRM');
  }

  // =========================================================================
  // HU-54: LIQUIDACIÓN DE HONORARIOS A PSICÓLOGOS (Bs.)
  // =========================================================================
  Future<List<Map<String, dynamic>>> getLiquidaciones() async {
    final uri = Uri.parse('$_base${ApiConstants.finanzasLiquidaciones}');
    final r = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(utf8.decode(r.bodyBytes)));
    }
    throw Exception(_parseError(r, 'Error al cargar liquidaciones')['error']);
  }

  Future<Map<String, dynamic>> previewLiquidacion({
    required String psicologoId,
    required String fechaInicio,
    required String fechaFin,
    double porcentajeComision = 30.0,
  }) async {
    final uri = Uri.parse('$_base${ApiConstants.finanzasLiquidacionesPreview}').replace(
      queryParameters: {
        'psicologo_id': psicologoId,
        'fecha_inicio': fechaInicio,
        'fecha_fin': fechaFin,
        'porcentaje_comision_centro': '$porcentajeComision',
      },
    );
    final r = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al previsualizar liquidación');
  }

  Future<Map<String, dynamic>> generarLiquidacion({
    required String psicologoId,
    required String fechaInicio,
    required String fechaFin,
    double porcentajeComision = 30.0,
  }) async {
    final uri = Uri.parse('$_base${ApiConstants.finanzasLiquidaciones}');
    final r = await http.post(
      uri,
      headers: _headers,
      body: jsonEncode({
        'psicologo_id': psicologoId,
        'fecha_inicio': fechaInicio,
        'fecha_fin': fechaFin,
        'porcentaje_comision_centro': porcentajeComision,
      }),
    ).timeout(const Duration(seconds: 20));
    if (r.statusCode == 201 || r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al generar liquidación');
  }

  Future<Map<String, dynamic>> pagarLiquidacion(String liquidacionId, String referenciaBancaria) async {
    final uri = Uri.parse('$_base${ApiConstants.finanzasLiquidaciones}$liquidacionId/pagar/');
    final r = await http.patch(
      uri,
      headers: _headers,
      body: jsonEncode({'referencia_bancaria': referenciaBancaria}),
    ).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al marcar liquidación como pagada');
  }

  // =========================================================================
  // HU-49: RESUMEN CLÍNICO LONGITUDINAL IA (HITL)
  // =========================================================================
  Future<List<Map<String, dynamic>>> listarPacientes() async {
    final uri = Uri.parse('$_base${ApiConstants.pacientes}');
    final r = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      final decoded = jsonDecode(utf8.decode(r.bodyBytes));
      final list = decoded is Map ? (decoded['results'] ?? []) : decoded;
      return List<Map<String, dynamic>>.from(list);
    }
    return [];
  }

  Future<List<Map<String, dynamic>>> listarResumenesIA(String pacienteId) async {
    final uri = Uri.parse('$_base/clinica/pacientes/$pacienteId/resumenes-ia/');
    final r = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(utf8.decode(r.bodyBytes)));
    }
    throw Exception(_parseError(r, 'No autorizado para ver resúmenes IA')['error']);
  }

  // CU23-paso 2: Solicita resumen longitudinal IA sobre ventana clínica
  Future<Map<String, dynamic>> generarResumenIA(String pacienteId, {String? fechaIni, String? fechaFin}) async {
    final uri = Uri.parse('$_base${ApiConstants.iaResumenLongitudinal}');
    final payload = <String, dynamic>{'paciente_id': pacienteId, 'usar_hf': true};
    if (fechaIni != null && fechaIni.isNotEmpty) payload['fecha_ini'] = fechaIni;
    if (fechaFin != null && fechaFin.isNotEmpty) payload['fecha_fin'] = fechaFin;
    final r = await http.post(
      uri,
      headers: _headers,
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 25));
    if (r.statusCode == 201 || r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al generar resumen IA');
  }

  // CU23-paso 18: Confirma edición humana y aprueba resumen (HITL)
  Future<Map<String, dynamic>> aprobarResumenHITL(String resumenId, String textoResumen) async {
    final uri = Uri.parse('$_base${ApiConstants.resumenesIA}$resumenId/aprobar/');
    final r = await http.patch(
      uri,
      headers: _headers,
      body: jsonEncode({'texto_resumen': textoResumen}),
    ).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al aprobar resumen HITL');
  }

  // =========================================================================
  // HU-50 & HU-51: MOTOR Y CONSOLA DE ALERTAS DE RIESGO IA
  // =========================================================================
  Future<Map<String, dynamic>> listarAlertasRiesgo({String? estado, String? severidad}) async {
    final qp = <String, String>{};
    if (estado != null && estado.isNotEmpty) qp['estado'] = estado;
    if (severidad != null && severidad.isNotEmpty) qp['severidad'] = severidad;
    final uri = Uri.parse('$_base${ApiConstants.alertasRiesgoIA}').replace(queryParameters: qp.isEmpty ? null : qp);
    final r = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      return Map<String, dynamic>.from(jsonDecode(utf8.decode(r.bodyBytes)));
    }
    throw Exception(_parseError(r, 'Error al cargar alertas de riesgo')['error']);
  }

  // CU24-paso 2: Dispara motor ML predictivo sobre historias activas
  Future<Map<String, dynamic>> evaluarAlertasRiesgo({int ventanaMeses = 3}) async {
    final uri = Uri.parse('$_base${ApiConstants.alertasRiesgoEvaluar}');
    final r = await http.post(
      uri,
      headers: _headers,
      body: jsonEncode({'ventana_meses': ventanaMeses}),
    ).timeout(const Duration(seconds: 25));
    if (r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al ejecutar barrido IA');
  }

  // CU24-paso 14: Registra intervención o resolución clínica sobre alerta
  Future<Map<String, dynamic>> transicionarAlerta(String alertaId, String estado, String notaIntervencion) async {
    final uri = Uri.parse('$_base${ApiConstants.mlAlertasBase}$alertaId/intervenir/');
    final r = await http.patch(
      uri,
      headers: _headers,
      body: jsonEncode({'estado': estado, 'nota_intervencion': notaIntervencion}),
    ).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al actualizar alerta');
  }

  // =========================================================================
  // HU-55: CONSOLA SUPERADMIN SAAS (USD)
  // =========================================================================
  Future<Map<String, dynamic>> getSaasAdminDashboard() async {
    final uri = Uri.parse('$_base${ApiConstants.saasAdminDashboard}');
    final r = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 25));
    if (r.statusCode == 200) {
      return Map<String, dynamic>.from(jsonDecode(utf8.decode(r.bodyBytes)));
    }
    throw Exception(_parseError(r, 'Error al cargar consola SaaS')['error']);
  }

  Future<Map<String, dynamic>> actualizarPlanTenant(String tenantId, {String? plan, String? estado}) async {
    final uri = Uri.parse('$_base${ApiConstants.saasAdminTenants}$tenantId/');
    final payload = <String, dynamic>{};
    if (plan != null) payload['plan'] = plan;
    if (estado != null) payload['estado'] = estado;
    final r = await http.patch(uri, headers: _headers, body: jsonEncode(payload)).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      return {'success': true, 'data': jsonDecode(utf8.decode(r.bodyBytes))};
    }
    return _parseError(r, 'Error al actualizar suscripción');
  }
}
