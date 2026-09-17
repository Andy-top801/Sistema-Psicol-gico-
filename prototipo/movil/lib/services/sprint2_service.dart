// ==============================================================================
// MÓDULO: sprint2_service.dart
// CAPA BCE: CONTROL (Cliente Móvil / Service Adapter)
// CASOS DE USO: CU14 (HU-24): Formulario Previo / Intake Digital
//               CU17 (HU-30): Tareas Terapéuticas Inter-Sesiones
//               CU18 (HU-32): Consentimientos Informados con Firma Digital
// DESCRIPCIÓN: Servicio cliente Sprint 2 que conecta las pantallas Flutter
//              con los endpoints Django REST del backend clínico.
// ==============================================================================
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants/api_constants.dart';
import 'auth_service.dart';

class Sprint2Service {
  final AuthService authService;

  Sprint2Service({required this.authService});

  // ═══════════════════════════════════════════════════════════════════════════
  // CU14 (HU-24): Formulario Previo a la Consulta (Intake Digital)
  // Diagrama de Comunicación – Diligenciamiento Móvil:
  //   Actor  → Paciente Autenticado (Flutter)
  //   IU     → IU_IntakeFormScreen (Stepper Interactivo)
  //   CTR    → Sprint2Service ➔ RespuestaPreConsultaViewSet (Django REST)
  //   CE     → CE_RespuestaPreConsulta, CE_FormularioPreConsulta (PostgreSQL)
  // ═══════════════════════════════════════════════════════════════════════════

  /// CU14 Paso 2: Obtener formulario activo de pre-consulta
  Future<Map<String, dynamic>?> getFormularioActivo() async {
    try {
      final url = Uri.parse(
        '${authService.baseUrl}${ApiConstants.formulariosPreconsulta}?activo=true',
      );
      final response = await http.get(url, headers: authService.getHeaders())
          .timeout(const Duration(seconds: 8));
      if (response.statusCode == 200) {
        final List list = jsonDecode(utf8.decode(response.bodyBytes));
        if (list.isNotEmpty) return Map<String, dynamic>.from(list.first);
      }
    } catch (_) {}
    return null;
  }

  /// CU14 Paso 5: Enviar respuesta de intake completada por el paciente
  Future<Map<String, dynamic>> enviarRespuestaIntake(Map<String, dynamic> data) async {
    try {
      final url = Uri.parse(
        '${authService.baseUrl}${ApiConstants.respuestasPreconsulta}',
      );
      final response = await http.post(
        url,
        headers: authService.getHeaders(),
        body: jsonEncode(data),
      ).timeout(const Duration(seconds: 10));

      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 201 || response.statusCode == 200) {
        return {'success': true, 'data': body};
      } else {
        String errorMsg = 'Error al enviar formulario.';
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

  /// CU14: Obtener respuestas previas del paciente
  Future<List<Map<String, dynamic>>> getMisRespuestasIntake() async {
    try {
      final url = Uri.parse(
        '${authService.baseUrl}${ApiConstants.respuestasPreconsulta}',
      );
      final response = await http.get(url, headers: authService.getHeaders())
          .timeout(const Duration(seconds: 8));
      if (response.statusCode == 200) {
        final List list = jsonDecode(utf8.decode(response.bodyBytes));
        return list.map((e) => Map<String, dynamic>.from(e)).toList();
      }
    } catch (_) {}
    return [];
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // CU17 (HU-30): Tareas Terapéuticas Inter-Sesiones (Visualización Móvil)
  // Diagrama de Comunicación – Reporte de Cumplimiento:
  //   Actor  → Paciente Autenticado (Flutter)
  //   IU     → IU_MisTareasScreen (Lista de Tareas + Modal de Reporte)
  //   CTR    → Sprint2Service ➔ TareaTerapeuticaViewSet (Django REST)
  //   CE     → CE_TareaTerapeutica, CE_EvidenciaTarea (PostgreSQL)
  // ═══════════════════════════════════════════════════════════════════════════

  /// CU17 Paso 2: Obtener tareas asignadas al paciente
  Future<List<Map<String, dynamic>>> getMisTareas() async {
    try {
      final url = Uri.parse(
        '${authService.baseUrl}${ApiConstants.tareas}',
      );
      final response = await http.get(url, headers: authService.getHeaders())
          .timeout(const Duration(seconds: 8));
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        final List list = data is List ? data : (data['results'] ?? []);
        return list.map((e) => Map<String, dynamic>.from(e)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// CU17 Paso 6: Enviar evidencia de cumplimiento de tarea
  Future<Map<String, dynamic>> enviarEvidenciaTarea(
    String tareaId,
    Map<String, dynamic> data,
  ) async {
    try {
      final url = Uri.parse(
        '${authService.baseUrl}${ApiConstants.tareas}$tareaId/evidencia/',
      );
      final response = await http.post(
        url,
        headers: authService.getHeaders(),
        body: jsonEncode(data),
      ).timeout(const Duration(seconds: 10));

      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 201 || response.statusCode == 200) {
        return {'success': true, 'data': body};
      } else {
        String errorMsg = 'Error al enviar evidencia.';
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

  // ═══════════════════════════════════════════════════════════════════════════
  // CU18 (HU-32): Consentimientos Informados – Lectura y Firma Digital
  // Diagrama de Comunicación – Firma Trazable con SHA-256:
  //   Actor  → Paciente / Tutor Legal (Flutter)
  //   IU     → IU_ConsentimientoFirmaScreen (Scroll + Canvas Táctil)
  //   CTR    → Sprint2Service ➔ ConsentimientoInformadoViewSet + FirmaConsentimientoViewSet
  //   CE     → CE_ConsentimientoInformado, CE_FirmaConsentimiento (PostgreSQL)
  // ═══════════════════════════════════════════════════════════════════════════

  /// CU18 Paso 2: Obtener consentimientos informados disponibles
  Future<List<Map<String, dynamic>>> getConsentimientos() async {
    try {
      final url = Uri.parse(
        '${authService.baseUrl}${ApiConstants.consentimientos}',
      );
      final response = await http.get(url, headers: authService.getHeaders())
          .timeout(const Duration(seconds: 8));
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        final List list = data is List ? data : (data['results'] ?? []);
        return list.map((e) => Map<String, dynamic>.from(e)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// CU18: Obtener firmas previas del paciente
  Future<List<Map<String, dynamic>>> getMisFirmas() async {
    try {
      final url = Uri.parse(
        '${authService.baseUrl}${ApiConstants.firmasConsentimiento}',
      );
      final response = await http.get(url, headers: authService.getHeaders())
          .timeout(const Duration(seconds: 8));
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        final List list = data is List ? data : (data['results'] ?? []);
        return list.map((e) => Map<String, dynamic>.from(e)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// CU18 Paso 7: Registrar firma de consentimiento informado con hash SHA-256
  Future<Map<String, dynamic>> firmarConsentimiento(Map<String, dynamic> data) async {
    try {
      final url = Uri.parse(
        '${authService.baseUrl}${ApiConstants.firmasConsentimiento}',
      );
      final response = await http.post(
        url,
        headers: authService.getHeaders(),
        body: jsonEncode(data),
      ).timeout(const Duration(seconds: 10));

      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 201 || response.statusCode == 200) {
        return {'success': true, 'data': body};
      } else {
        String errorMsg = 'Error al registrar firma.';
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

  /// CU18: Renderizar preview del consentimiento con datos del paciente
  Future<Map<String, dynamic>?> renderConsentimientoPreview(
    String consentimientoId,
    String? pacienteId,
  ) async {
    try {
      String urlStr =
          '${authService.baseUrl}${ApiConstants.consentimientos}$consentimientoId/render-preview/';
      if (pacienteId != null) {
        urlStr += '?paciente=$pacienteId';
      }
      final url = Uri.parse(urlStr);
      final response = await http.get(url, headers: authService.getHeaders())
          .timeout(const Duration(seconds: 8));
      if (response.statusCode == 200) {
        return Map<String, dynamic>.from(jsonDecode(utf8.decode(response.bodyBytes)));
      }
    } catch (_) {}
    return null;
  }
}
