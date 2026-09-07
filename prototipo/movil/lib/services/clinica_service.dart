import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants/api_constants.dart';
import '../models/paciente_model.dart';
import '../models/psicologo_model.dart';
import 'auth_service.dart';

class ClinicaService {
  final AuthService authService;

  ClinicaService({required this.authService});

  /// HU-14: Obtener perfil clínico y expediente del paciente autenticado
  Future<PacienteModel?> getMiPerfil() async {
    try {
      final url = Uri.parse('${authService.baseUrl}${ApiConstants.pacienteMe}');
      final response = await http.get(url, headers: authService.getHeaders());
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        return PacienteModel.fromJson(data);
      }
    } catch (_) {}
    return null;
  }

  /// HU-14: Actualizar datos personales, contacto de emergencia y tutor legal
  Future<Map<String, dynamic>> updateMiPerfil(String pacienteId, Map<String, dynamic> datos) async {
    try {
      final url = Uri.parse('${authService.baseUrl}${ApiConstants.pacientes}$pacienteId/');
      final response = await http.patch(
        url,
        headers: authService.getHeaders(),
        body: jsonEncode(datos),
      );

      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 200) {
        return {'success': true, 'paciente': PacienteModel.fromJson(body)};
      } else {
        String errorMsg = 'Error al actualizar expediente.';
        if (body is Map) {
          final firstVal = body.values.first;
          if (firstVal is List && firstVal.isNotEmpty) {
            errorMsg = firstVal.first.toString();
          } else if (firstVal is String) {
            errorMsg = firstVal;
          }
        }
        return {'success': false, 'error': errorMsg};
      }
    } catch (e) {
      return {'success': false, 'error': 'Error de conexión: $e'};
    }
  }

  /// HU-11 / HU-16: Obtener directorio de psicólogos activos con sus tarifas y especialidades
  Future<List<PsicologoModel>> getPsicologos() async {
    try {
      final url = Uri.parse('${authService.baseUrl}${ApiConstants.psicologos}');
      final response = await http.get(url, headers: authService.getHeaders());
      if (response.statusCode == 200) {
        final List list = jsonDecode(utf8.decode(response.bodyBytes));
        return list.map((e) => PsicologoModel.fromJson(e)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// HU-15 / HU-16: Obtener slots horarios libres para un psicólogo en una fecha
  Future<List<String>> getSlotsDisponibles(String psicologoId, String fecha) async {
    try {
      final url = Uri.parse(
        '${authService.baseUrl}${ApiConstants.citasSlotsDisponibles}?psicologo_id=$psicologoId&fecha=$fecha',
      );
      final response = await http.get(url, headers: authService.getHeaders());
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['slots'] is List) {
          return (data['slots'] as List).map((s) => s.toString()).toList();
        }
      }
    } catch (_) {}
    return [];
  }
}
