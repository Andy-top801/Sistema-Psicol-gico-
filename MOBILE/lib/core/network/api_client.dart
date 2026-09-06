import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../storage/token_storage.dart';
import 'api_exception.dart';

/// Envoltorio delgado sobre `package:http` para hablar con la API
/// Django REST Framework: arma la URL completa, agrega el header
/// `Authorization: Bearer <token>` cuando corresponde, y traduce
/// cualquier respuesta fuera de 2xx en un [ApiException] con el mensaje
/// que ya viene del backend.
class ApiClient {
  ApiClient({http.Client? httpClient, TokenStorage? tokenStorage})
    : _httpClient = httpClient ?? http.Client(),
      _tokenStorage = tokenStorage ?? TokenStorage();

  final http.Client _httpClient;
  final TokenStorage _tokenStorage;

  Future<Map<String, dynamic>> post(
    String path,
    Map<String, dynamic> body, {
    bool authenticated = false,
  }) async {
    final headers = await _buildHeaders(authenticated: authenticated);
    final response = await _httpClient.post(
      Uri.parse('${ApiConfig.baseUrl}$path'),
      headers: headers,
      body: jsonEncode(body),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> get(
    String path, {
    bool authenticated = true,
  }) async {
    final headers = await _buildHeaders(authenticated: authenticated);
    final response = await _httpClient.get(
      Uri.parse('${ApiConfig.baseUrl}$path'),
      headers: headers,
    );
    return _decode(response);
  }

  Future<Map<String, String>> _buildHeaders({
    required bool authenticated,
  }) async {
    final headers = {'Content-Type': 'application/json'};
    if (authenticated) {
      final token = await _tokenStorage.readAccessToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    return headers;
  }

  Map<String, dynamic> _decode(http.Response response) {
    final decodedBody = response.body.isEmpty
        ? <String, dynamic>{}
        : jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decodedBody;
    }

    throw ApiException(
      statusCode: response.statusCode,
      message: _extractMessage(decodedBody),
      errors: decodedBody,
    );
  }

  String _extractMessage(Map<String, dynamic> body) {
    if (body.containsKey('detail')) {
      return body['detail'].toString();
    }
    // DRF suele devolver {"campo": ["mensaje1", "mensaje2"]}
    for (final value in body.values) {
      if (value is List && value.isNotEmpty) {
        return value.first.toString();
      }
    }
    return 'Ocurrió un error inesperado. Intenta de nuevo.';
  }
}
