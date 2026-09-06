import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:sigepsi_mobile/core/network/api_client.dart';
import 'package:sigepsi_mobile/core/network/api_exception.dart';
import 'package:sigepsi_mobile/paquetes/paquete1_admin_seguridad/services/auth_service.dart';

import '../../../helpers/fake_token_storage.dart';

/// CU02 — Gestionar inicio de sesión y autenticación.
void main() {
  late FakeTokenStorage tokenStorage;

  setUp(() {
    tokenStorage = FakeTokenStorage();
  });

  AuthService buildAuthService(http.Client mockClient) {
    final apiClient = ApiClient(
      httpClient: mockClient,
      tokenStorage: tokenStorage,
    );
    return AuthService(apiClient: apiClient, tokenStorage: tokenStorage);
  }

  test(
    'register envía los campos correctos y guarda los tokens devueltos',
    () async {
      late http.Request capturedRequest;

      final mockClient = MockClient((request) async {
        capturedRequest = request;
        return http.Response(
          jsonEncode({
            'user': {
              'id': '1',
              'email': 'paciente.nuevo@test.com',
              'first_name': 'Nuevo',
              'last_name': 'Paciente',
              'phone': '999999999',
              'roles': ['Paciente'],
            },
            'access': 'access-token',
            'refresh': 'refresh-token',
          }),
          201,
        );
      });

      final authService = buildAuthService(mockClient);

      final usuario = await authService.register(
        email: 'paciente.nuevo@test.com',
        password: 'ClaveSegura123',
        firstName: 'Nuevo',
        lastName: 'Paciente',
        phone: '999999999',
      );

      expect(capturedRequest.url.path, '/api/users/auth/register/');
      final sentBody = jsonDecode(capturedRequest.body) as Map<String, dynamic>;
      expect(sentBody['email'], 'paciente.nuevo@test.com');
      expect(sentBody['password'], 'ClaveSegura123');

      expect(usuario.email, 'paciente.nuevo@test.com');
      expect(usuario.roles, ['Paciente']);
      expect(await tokenStorage.readAccessToken(), 'access-token');
      expect(await tokenStorage.readRefreshToken(), 'refresh-token');
    },
  );

  test(
    'login guarda tokens y luego consulta /me/ con el Bearer token',
    () async {
      final mockClient = MockClient((request) async {
        if (request.url.path == '/api/users/auth/login/') {
          return http.Response(
            jsonEncode({'access': 'access-token', 'refresh': 'refresh-token'}),
            200,
          );
        }
        if (request.url.path == '/api/users/me/') {
          expect(request.headers['Authorization'], 'Bearer access-token');
          return http.Response(
            jsonEncode({
              'id': '1',
              'email': 'paciente@sanamente.com',
              'first_name': 'Ana',
              'last_name': 'Martínez',
              'phone': '',
              'roles': ['Paciente'],
            }),
            200,
          );
        }
        return http.Response('not found', 404);
      });

      final authService = buildAuthService(mockClient);

      final usuario = await authService.login(
        email: 'paciente@sanamente.com',
        password: 'password123',
      );

      expect(usuario.firstName, 'Ana');
      expect(usuario.esPaciente, isTrue);
    },
  );

  test(
    'una respuesta 400 del backend se traduce en ApiException con el mensaje del servidor',
    () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'email': [
              'Ya existe una cuenta registrada con este correo electrónico.',
            ],
          }),
          400,
        );
      });

      final authService = buildAuthService(mockClient);

      expect(
        () => authService.register(
          email: 'paciente@sanamente.com',
          password: 'ClaveSegura123',
          firstName: 'Ana',
          lastName: 'Martínez',
        ),
        throwsA(
          isA<ApiException>().having(
            (e) => e.message,
            'message',
            'Ya existe una cuenta registrada con este correo electrónico.',
          ),
        ),
      );
    },
  );

  test('logout limpia el almacenamiento local de tokens', () async {
    await tokenStorage.saveTokens(access: 'a', refresh: 'b');
    final authService = buildAuthService(
      MockClient((_) async => http.Response('', 200)),
    );

    await authService.logout();

    expect(await tokenStorage.readAccessToken(), isNull);
    expect(await authService.hasSession(), isFalse);
  });
}
