import os
import sys
import django

# Setup django environment
backend_dir = r"c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\prototipo\backend"
sys.path.insert(0, backend_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sigepsi.settings")
django.setup()

from django_tenants.utils import schema_context
from django.db import connection
from rest_framework.test import APIClient
from tenants.models import Tenant
from accounts.models import Usuario, Rol
from clinica.models import Paciente, Psicologo, Especialidad, Disponibilidad
from agenda.models import Cita
from datetime import date, time, timedelta

print("=" * 70)
print("INICIANDO PRUEBAS DE VERIFICACIÓN INTEGRAL DE CORRECCIONES")
print("=" * 70)

client = APIClient()

# 1. TEST LOGIN ADMIN CENTRO (Sin enviar X-Tenant-ID explícito para probar resolución automática)
print("\n[TEST 1] Login Admin Centro (admin@centroesperanza.com) con auto-resolución...")
res_login = client.post('/api/auth/login/', {
    'email': 'admin@centroesperanza.com',
    'password': 'Admin1234*'
}, format='json')

assert res_login.status_code == 200, f"Error en login: {res_login.status_code} - {res_login.data}"
login_data = res_login.data
token = login_data['access']
print(" -> Login exitoso! Token obtenido.")
print(f" -> Rol: {login_data.get('rol')}")
print(f" -> Tenant detectado en respuesta: {login_data.get('tenant', {}).get('schema_name')}")
assert login_data.get('tenant') is not None, "El tenant no vino en la respuesta de login"
assert login_data['tenant']['schema_name'] == 'centro_esperanza', "El schema no es centro_esperanza"

client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

# 2. TEST REGISTRO DE PACIENTE (Sin codigo_expediente manual, debe autogenerarse)
print("\n[TEST 2] Registro de Nuevo Paciente (CU7) sin codigo_expediente...")
import random
rnd_id = random.randint(10000, 99999)
nuevo_paciente_payload = {
    'nombre': f'Valeria_{rnd_id}',
    'apellido': 'Montaño',
    'email': f'valeria.{rnd_id}@gmail.com',
    'password': 'Password123*',
    'telefono': '+591 78899001',
    'ci': f'CI-{rnd_id}',
    'fecha_nacimiento': '2000-05-15',
    'genero': 'F',
    'contacto_emergencia_nombre': 'Carlos Montaño',
    'contacto_emergencia_telf': '+591 78899002'
}
res_paciente = client.post('/api/clinica/pacientes/', nuevo_paciente_payload, format='json')
assert res_paciente.status_code == 201, f"Error al registrar paciente: {res_paciente.status_code} - {res_paciente.data}"
paciente_data = res_paciente.data
paciente_id = paciente_data['id']
codigo_exp = paciente_data['codigo_expediente']
print(f" -> Paciente registrado con éxito! ID: {paciente_id}, Código: {codigo_exp}")
assert codigo_exp.startswith("EXP-"), f"Código de expediente no tiene formato EXP-: {codigo_exp}"

# 3. TEST EDICIÓN DE PACIENTE
print("\n[TEST 3] Edición de Paciente (modificando teléfono y contacto de emergencia)...")
edit_paciente_payload = {
    'telefono': '+591 79991122',
    'contacto_emergencia_nombre': 'Carlos Montaño (Padre)'
}
res_edit_pac = client.patch(f'/api/clinica/pacientes/{paciente_id}/', edit_paciente_payload, format='json')
assert res_edit_pac.status_code == 200, f"Error al editar paciente: {res_edit_pac.status_code} - {res_edit_pac.data}"
print(f" -> Paciente editado con éxito! Teléfono actualizado: {res_edit_pac.data['usuario_datos']['telefono']}")

# 4. TEST REGISTRO DE PSICÓLOGO
print("\n[TEST 4] Registro de Psicólogo con especialidad_ids...")
with schema_context('centro_esperanza'):
    esp = Especialidad.objects.first()
    esp_id = esp.id if esp else None

nuevo_psico_payload = {
    'nombre': f'Lic. Andrea_{rnd_id}',
    'apellido': 'Salazar',
    'email': f'andrea.{rnd_id}@centroesperanza.com',
    'password': 'PsicoPass123*',
    'telefono': '+591 77788990',
    'numero_colegiado': '',  # Debe autogenerarse
    'biografia': 'Especialista en terapia conductual cognitiva',
    'modalidad': 'MIXTA',
    'tarifa_base': 180.00,
    'especialidad_ids': [esp_id] if esp_id else []
}
res_psico = client.post('/api/clinica/psicologos/', nuevo_psico_payload, format='json')
assert res_psico.status_code == 201, f"Error al registrar psicólogo: {res_psico.status_code} - {res_psico.data}"
psico_data = res_psico.data
psico_id = psico_data['id']
print(f" -> Psicólogo registrado con éxito! ID: {psico_id}, Colegiado: {psico_data['numero_colegiado']}")

# 5. TEST EDICIÓN DE PSICÓLOGO
print("\n[TEST 5] Edición de Psicólogo (modificando tarifa y biografía)...")
edit_psico_payload = {
    'tarifa_base': 200.00,
    'biografia': 'Especialista en terapia conductual cognitiva y mindfulness'
}
res_edit_psico = client.patch(f'/api/clinica/psicologos/{psico_id}/', edit_psico_payload, format='json')
assert res_edit_psico.status_code == 200, f"Error al editar psicólogo: {res_edit_psico.status_code} - {res_edit_psico.data}"
print(f" -> Psicólogo editado con éxito! Tarifa: {res_edit_psico.data['tarifa_base']}")

# 6. TEST CONFIGURACIÓN DE DISPONIBILIDAD (Payload { franjas: [...] })
print("\n[TEST 6] Configuración de Disponibilidad Semanal ({ franjas: [...] })...")
franjas_payload = {
    'franjas': [
        {
            'dia_semana': 2, # Martes (0=Dom, 1=Lun, 2=Mar, 3=Mie, 4=Jue, 5=Vie, 6=Sab)
            'hora_inicio': '09:00:00',
            'hora_fin': '12:00:00',
            'duracion_bloque_minutos': 50,
            'modalidad_permitida': 'MIXTA',
            'activo': True
        },
        {
            'dia_semana': 3, # Jueves
            'hora_inicio': '14:00:00',
            'hora_fin': '18:00:00',
            'duracion_bloque_minutos': 50,
            'modalidad_permitida': 'MIXTA',
            'activo': True
        }
    ]
}
res_disp = client.post(f'/api/clinica/psicologos/{psico_id}/disponibilidad/', franjas_payload, format='json')
assert res_disp.status_code == 200, f"Error al guardar disponibilidad: {res_disp.status_code} - {res_disp.data}"
print(f" -> Disponibilidad guardada con éxito! Franjas configuradas: {res_disp.data['count']}")

# 7. TEST SLOTS DISPONIBLES
print("\n[TEST 7] Consulta de Slots Disponibles en fecha correspondiente...")
# Buscar el próximo martes
hoy = date.today()
dias_hasta_martes = (1 - hoy.weekday() + 7) % 7
if dias_hasta_martes == 0:
    dias_hasta_martes = 7
proximo_martes = hoy + timedelta(days=dias_hasta_martes)
fecha_martes_str = proximo_martes.strftime('%Y-%m-%d')

res_slots = client.get(f'/api/agenda/citas/slots-disponibles/?psicologo_id={psico_id}&fecha={fecha_martes_str}')
assert res_slots.status_code == 200, f"Error al consultar slots: {res_slots.status_code} - {res_slots.data}"
slots_data = res_slots.data
print(f" -> Slots obtenidos para {fecha_martes_str}: {len(slots_data.get('slots', []))} slots libres.")
assert len(slots_data.get('slots', [])) > 0, "No se generaron slots para el horario configurado"

slot_elegido = slots_data['slots'][0]
hora_ini = slot_elegido['hora_inicio']
hora_fin = slot_elegido['hora_fin']

# 8. TEST RESERVA CONCURRENTE DE CITA
print(f"\n[TEST 8] Reserva de Cita en slot {hora_ini} - {hora_fin}...")
cita_payload = {
    'paciente': paciente_id,
    'psicologo': psico_id,
    'fecha': fecha_martes_str,
    'hora_inicio': hora_ini,
    'hora_fin': hora_fin,
    'modalidad': 'VIRTUAL',
    'motivo_consulta': 'Consulta inicial de evaluación de estrés y ansiedad'
}
res_cita = client.post('/api/agenda/citas/', cita_payload, format='json')
assert res_cita.status_code == 201, f"Error al reservar cita: {res_cita.status_code} - {res_cita.data}"
cita_data = res_cita.data
cita_id = cita_data['id']
print(f" -> Cita reservada con éxito! ID: {cita_id}")
print(f" -> Paciente: {cita_data.get('paciente_nombre')}, Psicólogo: {cita_data.get('psicologo_nombre')}")
assert cita_data.get('paciente_nombre') == f'Valeria_{rnd_id} Montaño', "paciente_nombre no corresponde"

# 9. TEST EDICIÓN DE USUARIO (PUT/PATCH sin email, verifica que no exija email)
print("\n[TEST 9] Edición de Usuario (sin enviar email en payload)...")
with schema_context('centro_esperanza'):
    user_test = Usuario.objects.filter(email=f'valeria.{rnd_id}@gmail.com').first()
    assert user_test is not None, "Usuario de prueba no encontrado"
    user_test_id = str(user_test.id)

edit_user_payload = {
    'nombre': 'Valeria Actualizada',
    'apellido': 'Montaño Paz',
    'telefono': '+591 70009999'
}
res_edit_user = client.patch(f'/api/users/{user_test_id}/', edit_user_payload, format='json')
assert res_edit_user.status_code == 200, f"Error al editar usuario: {res_edit_user.status_code} - {res_edit_user.data}"
print(f" -> Usuario editado con éxito sin enviar email! Nombre: {res_edit_user.data['nombre']} {res_edit_user.data['apellido']}")

# Test PUT también
res_put_user = client.put(f'/api/users/{user_test_id}/', edit_user_payload, format='json')
assert res_put_user.status_code == 200, f"Error en PUT usuario: {res_put_user.status_code} - {res_put_user.data}"
print(f" -> PUT Usuario completado con éxito con kwargs['partial']=True!")

print("\n" + "=" * 70)
print("¡TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE (100% OK)!")
print("=" * 70)
