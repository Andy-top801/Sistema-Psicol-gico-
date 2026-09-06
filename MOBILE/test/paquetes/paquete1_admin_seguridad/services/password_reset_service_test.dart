import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:sigepsi_mobile/core/network/api_client.dart';
import 'package:sigepsi_mobile/core/network/api_exception.dart';
import 'package:sigepsi_mobile/paquetes/paquete1_admin_seguridad/services/password_reset_service.dart';

/// CU27 — Recuperar contraseña o credenciales de acceso (HU-10 / RF-31).
void main() {
  PasswordResetService buildService(http.Client mockClient) {
    final apiClient = ApiClient(httpClient: mockClient);
    return PasswordResetService(apiClient: apiClient);
  }

  test(
    'requestPasswordReset llama al endpoint correcto con el correo',
    () async {
      late http.Request capturedRequest;
      final mockClient = MockClient((request) async {
        capturedRequest = request;
        return http.Response(jsonEncode({'detail': 'ok'}), 200);
      });

      final service = buildService(mockClient);
      await service.requestPasswordReset(email: 'paciente@sanamente.com');

      expect(capturedRequest.url.path, '/api/users/auth/password-reset/');
      final sentBody = jsonDecode(capturedRequest.body) as Map<String, dynamic>;
      expect(sentBody['email'], 'paciente@sanamente.com');
    },
  );

  test('verifyResetCode llama al endpoint correcto con el código', () async {
    late http.Request capturedRequest;
    final mockClient = MockClient((request) async {
      capturedRequest = request;
      return http.Response(jsonEncode({'detail': 'Código válido.'}), 200);
    });

    final service = buildService(mockClient);
    await service.verifyResetCode(code: 'abc.def');

    expect(capturedRequest.url.path, '/api/users/auth/password-reset-verify/');
    final sentBody = jsonDecode(capturedRequest.body) as Map<String, dynamic>;
    expect(sentBody['code'], 'abc.def');
  });

  test('un código inválido en verifyResetCode lanza ApiException', () async {
    final mockClient = MockClient((request) async {
      return http.Response(
        jsonEncode({
          'code': ['El código no es válido o ya expiró. Solicita uno nuevo.'],
        }),
        400,
      );
    });

    final service = buildService(mockClient);

    expect(
      () => service.verifyResetCode(code: 'invalido'),
      throwsA(isA<ApiException>()),
    );
  });

  test('confirmPasswordReset envía el código y la nueva contraseña', () async {
    late http.Request capturedRequest;
    final mockClient = MockClient((request) async {
      capturedRequest = request;
      return http.Response(jsonEncode({'detail': 'ok'}), 200);
    });

    final service = buildService(mockClient);
    await service.confirmPasswordReset(
      code: 'abc.def',
      newPassword: 'ClaveNueva456',
    );

    expect(capturedRequest.url.path, '/api/users/auth/password-reset-confirm/');
    final sentBody = jsonDecode(capturedRequest.body) as Map<String, dynamic>;
    expect(sentBody['code'], 'abc.def');
    expect(sentBody['new_password'], 'ClaveNueva456');
  });

  test(
    'un código inválido en confirmPasswordReset lanza ApiException',
    () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'code': ['El código no es válido o ya expiró. Solicita uno nuevo.'],
          }),
          400,
        );
      });

      final service = buildService(mockClient);

      expect(
        () => service.confirmPasswordReset(
          code: 'invalido',
          newPassword: 'ClaveNueva456',
        ),
        throwsA(isA<ApiException>()),
      );
    },
  );
}
