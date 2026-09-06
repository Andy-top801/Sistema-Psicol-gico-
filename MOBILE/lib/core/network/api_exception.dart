/// Excepción lanzada por [ApiClient] cuando el backend responde con un
/// status fuera del rango 2xx. Conserva el mensaje del backend (DRF suele
/// responder `{"campo": ["mensaje"]}` o `{"detail": "mensaje"}`) para que la
/// UI pueda mostrarlo directamente.
class ApiException implements Exception {
  final int statusCode;
  final String message;
  final Map<String, dynamic>? errors;

  ApiException({required this.statusCode, required this.message, this.errors});

  @override
  String toString() => 'ApiException($statusCode): $message';
}
