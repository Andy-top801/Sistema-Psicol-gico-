# -*- coding: utf-8 -*-
import sys, os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from django.utils import timezone
from django_tenants.utils import schema_context
from tenants.models import Tenant

def test_fcm_notification_service_and_dispatch():
    tenant = Tenant.objects.exclude(schema_name='public').first()
    assert tenant is not None, "Debe existir al menos un tenant para las pruebas."

    with schema_context(tenant.schema_name):
        from clinica.models import Paciente, TokenFCM, Psicologo
        from agenda.models import Cita, NotificacionCita
        from agenda.services import FCMNotificationService

        paciente = Paciente.objects.first()
        assert paciente is not None, "Debe existir un paciente en el tenant."

        # 1. Registrar token FCM
        token_str = "fcm_test_token_patient_device_12345"
        TokenFCM.objects.filter(paciente=paciente).delete()
        token_obj, created = TokenFCM.objects.update_or_create(
            paciente=paciente,
            token=token_str,
            defaults={
                'plataforma': 'ANDROID',
                'activo': True
            }
        )
        assert token_obj.activo is True

        # 2. Despachar push al paciente (HU-43 / CU12)
        exito = FCMNotificationService.enviar_push_paciente(
            paciente=paciente,
            titulo="Recordatorio de Consulta Psicológica",
            cuerpo="Su consulta está programada en 24 horas. Modalidad: Virtual.",
            payload_data={"tipo": "RECORDATORIO_24H", "paciente_id": str(paciente.id)}
        )
        assert exito is True, "El despacho push debe retornar True para paciente con token activo."

        # 3. Caso sin tokens activos -> debe retornar False
        token_obj.activo = False
        token_obj.save()
        exito_inactivo = FCMNotificationService.enviar_push_paciente(
            paciente=paciente,
            titulo="Prueba sin token",
            cuerpo="No debe enviarse."
        )
        assert exito_inactivo is False, "No debe enviar push si no hay tokens activos."

        # Restaurar token
        token_obj.activo = True
        token_obj.save()

        # 4. Procesar recordatorios automáticos de citas próximas
        from datetime import time
        psicologo = Psicologo.objects.first()
        manana = timezone.now().date() + timedelta(days=1)
        hora_cita = time(10, 0)
        hora_fin = time(11, 0)

        cita = Cita.objects.create(
            paciente=paciente,
            psicologo=psicologo,
            fecha=manana,
            hora_inicio=hora_cita,
            hora_fin=hora_fin,
            modalidad='VIRTUAL',
            estado='PROGRAMADA',
            motivo_consulta="Seguimiento de ansiedad"
        )

        # Crear notificación en cola programada
        notif = NotificacionCita.objects.create(
            cita=cita,
            tipo_evento='RECORDATORIO_24H',
            canal='PUSH_FCM',
            enviada=False,
            fecha_programada=timezone.now() - timedelta(minutes=5)
        )

        despachadas = FCMNotificationService.procesar_recordatorios_programados()
        assert despachadas >= 1, "Debe procesar al menos 1 recordatorio programado."

        notif.refresh_from_db()
        assert notif.enviada is True, "La notificación debe quedar marcada como enviada."
        assert notif.fecha_envio is not None

        # Limpiar datos de prueba
        notif.delete()
        cita.delete()

if __name__ == "__main__":
    test_fcm_notification_service_and_dispatch()
    print("ALL FCM NOTIFICATION TESTS PASSED [OK]")
