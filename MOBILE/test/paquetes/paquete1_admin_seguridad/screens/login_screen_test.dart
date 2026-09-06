import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:provider/provider.dart';

import 'package:sigepsi_mobile/core/network/api_client.dart';
import 'package:sigepsi_mobile/paquetes/paquete1_admin_seguridad/providers/auth_provider.dart';
import 'package:sigepsi_mobile/paquetes/paquete1_admin_seguridad/screens/login_screen.dart';
import 'package:sigepsi_mobile/paquetes/paquete1_admin_seguridad/services/auth_service.dart';

import '../../../helpers/fake_token_storage.dart';

/// CU02 — Gestionar inicio de sesión y autenticación.
Widget _wrapWithProvider(Widget child, {required http.Client httpClient}) {
  final tokenStorage = FakeTokenStorage();
  final apiClient = ApiClient(
    httpClient: httpClient,
    tokenStorage: tokenStorage,
  );
  final authService = AuthService(
    apiClient: apiClient,
    tokenStorage: tokenStorage,
  );

  return ChangeNotifierProvider(
    create: (_) => AuthProvider(authService: authService),
    child: MaterialApp(home: child),
  );
}

void main() {
  testWidgets(
    'muestra errores de validación y no llama al backend si el formulario está vacío',
    (tester) async {
      var networkCalled = false;
      final mockClient = MockClient((request) async {
        networkCalled = true;
        return http.Response('{}', 200);
      });

      await tester.pumpWidget(
        _wrapWithProvider(const LoginScreen(), httpClient: mockClient),
      );

      await tester.ensureVisible(find.text('Ingresar'));
      await tester.tap(find.text('Ingresar'));
      await tester.pump();

      expect(find.text('Ingresa tu correo electrónico'), findsOneWidget);
      expect(find.text('Ingresa tu contraseña'), findsOneWidget);
      expect(networkCalled, isFalse);
    },
  );

  testWidgets(
    'rechaza un correo con formato inválido antes de llamar al backend',
    (tester) async {
      var networkCalled = false;
      final mockClient = MockClient((request) async {
        networkCalled = true;
        return http.Response('{}', 200);
      });

      await tester.pumpWidget(
        _wrapWithProvider(const LoginScreen(), httpClient: mockClient),
      );

      await tester.enterText(
        find.byType(TextFormField).at(0),
        'correo-invalido',
      );
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'ClaveSegura123',
      );
      await tester.ensureVisible(find.text('Ingresar'));
      await tester.tap(find.text('Ingresar'));
      await tester.pump();

      expect(find.text('Ingresa un correo electrónico válido'), findsOneWidget);
      expect(networkCalled, isFalse);
    },
  );
}
