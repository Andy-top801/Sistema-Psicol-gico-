import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants/api_constants.dart';
import '../models/cita_model.dart';
import 'auth_service.dart';

class AgendaService {
  final AuthService authService;

  AgendaService({required this.authService});

  /// HU-16 / HU-22: Obtener citas del usuario (paciente o psicólogo)
  Future<List<CitaModel>> getCitas({String? estado, String? fecha}) async {
    try {
      var urlStr = '${authService.baseUrl}${ApiConstants.citas}';
      List<String> query = [];
      if (estado != null && estado.isNotEmpty) query.add('estado=$estado');
      if (fecha != null && fecha.isNotEmpty) query.add('fecha=$fecha');
      if (query.isNotEmpty) urlStr = '$urlStr?${query.join('&')}';

      final url = Uri.parse(urlStr);
      final response = await http.get(url, headers: authService.getHeaders());
      if (response.statusCode == 200) {
        final List list = jsonDecode(utf8.decode(response.bodyBytes));
        return list.map((e) => CitaModel.fromJson(e)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// HU-15 / HU-16: Reservar cita médica con control de concurrencia
  Future<Map<String, dynamic>> reservarCita({
    required String pacienteId,
    required String psicologoId,
    required String fecha,
    required String horaInicio,
    required String horaFin,
    required String modalidad,
    required String motivoConsulta,
    double? costo,
  }) async {
    try {
      final url = Uri.parse('${authService.baseUrl}${ApiConstants.citas}');
      final response = await http.post(
        url,
        headers: authService.getHeaders(),
        body: jsonEncode({
          'paciente': pacienteId,
          'psicologo': psicologoId,
          'fecha': fecha,
          'hora_inicio': horaInicio,
          'hora_fin': horaFin,
          'modalidad': modalidad.toUpperCase(),
          'motivo_consulta': motivoConsulta,
          if (costo != null) 'costo': costo,
        }),
      );

      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 201 || response.statusCode == 200) {
        return {'success': true, 'cita': CitaModel.fromJson(body)};
      } else {
        String errorMsg = 'Error al reservar cita.';
        if (body is Map) {
          if (body['non_field_errors'] is List && (body['non_field_errors'] as List).isNotEmpty) {
            errorMsg = body['non_field_errors'][0];
          } else if (body['detail'] != null) {
            errorMsg = body['detail'].toString();
          } else if (body['error'] != null) {
            errorMsg = body['error'].toString();
          } else {
            final firstVal = body.values.first;
            if (firstVal is List && firstVal.isNotEmpty) {
              errorMsg = firstVal.first.toString();
            }
          }
        }
        return {'success': false, 'error': errorMsg};
      }
    } catch (e) {
      return {'success': false, 'error': 'Error de conexión: $e'};
    }
  }

  /// HU-17: Cancelar cita con motivo
  Future<Map<String, dynamic>> cancelarCita(String citaId, String motivo) async {
    try {
      final url = Uri.parse('${authService.baseUrl}${ApiConstants.citas}$citaId/cancelar/');
      final response = await http.post(
        url,
        headers: authService.getHeaders(),
        body: jsonEncode({'motivo': motivo}),
      );

      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 200) {
        return {'success': true, 'mensaje': body['mensaje'] ?? 'Cita cancelada con éxito.'};
      } else {
        return {'success': false, 'error': body['error'] ?? body['motivo']?[0] ?? 'No se pudo cancelar la cita.'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Error de conexión: $e'};
    }
  }

  /// HU-18 / HU-19: Obtener credenciales y sala de teleconsulta Jitsi Meet
  Future<Map<String, dynamic>> getTeleconsultaAccess(String citaId) async {
    try {
      final url = Uri.parse('${authService.baseUrl}${ApiConstants.teleconsultaAccess}$citaId/access/');
      final response = await http.get(url, headers: authService.getHeaders());
      final body = jsonDecode(utf8.decode(response.bodyBytes));

      if (response.statusCode == 200) {
        return {'success': true, 'data': body};
      } else {
        return {
          'success': false,
          'error': body['error'] ?? body['detail'] ?? 'No se pudo acceder a la sala de teleconsulta.',
          'codigo': body['codigo'],
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Error de conexión: $e'};
    }
  }

  /// HU-18 / HU-19: Concluir sesión de teleconsulta y registrar duración real
  Future<Map<String, dynamic>> finishTeleconsulta(String citaId, int duracionSegundos) async {
    try {
      final url = Uri.parse('${authService.baseUrl}${ApiConstants.teleconsultaAccess}$citaId/finish/');
      final response = await http.post(
        url,
        headers: authService.getHeaders(),
        body: jsonEncode({'duracion_segundos': duracionSegundos}),
      );

      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 200) {
        return {'success': true, 'data': body};
      } else {
        return {'success': false, 'error': body['error'] ?? 'Error al cerrar teleconsulta.'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Error de conexión: $e'};
    }
  }
}
