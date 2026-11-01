import 'package:flutter_test/flutter_test.dart';
import 'package:sigepsi_movil/core/constants/api_constants.dart';
import 'package:sigepsi_movil/models/cita_model.dart';

void main() {
  group('Sprint 3 Mobile Suite Tests', () {
    test('ApiConstants contain Sprint 3 endpoints', () {
      expect(ApiConstants.misCitas, contains('/agenda/citas/mis-citas/'));
      expect(ApiConstants.fcmToken, contains('/agenda/fcm-token/'));
      expect(ApiConstants.registroAnimo, contains('/clinica/registro-animo/'));
      expect(ApiConstants.clasificacionIA, contains('/clinica/clasificacion-ia/'));
      expect(ApiConstants.triajeAlertas, contains('/clinica/triaje/alertas/'));
      expect(ApiConstants.triajeAsignar, contains('/clinica/triaje/asignar/'));
    });

    test('CitaModel parses correctly for Mis Citas Sprint 3 view', () {
      final jsonSample = {
        'id': 'cita-uuid-1234',
        'paciente': 'pac-uuid-5678',
        'paciente_nombre': 'Ana Perez',
        'psicologo': 'psi-uuid-9999',
        'psicologo_nombre': 'Lic. Elena Ramos',
        'fecha': '2026-10-28',
        'hora_inicio': '14:00:00',
        'hora_fin': '15:00:00',
        'modalidad': 'VIRTUAL',
        'estado': 'PROGRAMADA',
        'motivo_consulta': 'Seguimiento de ansiedad',
        'costo': '150.00',
        'sala_jitsi_token': 'sigepsi-cita1234',
      };

      final cita = CitaModel.fromJson(jsonSample);
      expect(cita.id, equals('cita-uuid-1234'));
      expect(cita.isVirtual, isTrue);
      expect(cita.isActiva, isTrue);
      expect(cita.psicologoNombre, equals('Lic. Elena Ramos'));
    });
  });
}
