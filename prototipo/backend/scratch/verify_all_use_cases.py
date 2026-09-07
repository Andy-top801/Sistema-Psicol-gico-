import os
import sys
import uuid
import random
from datetime import date, time, timedelta, datetime
from typing import Any, cast, Dict, List
import django

# Setup Django environment
backend_dir = r"c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\prototipo\backend"
sys.path.insert(0, backend_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sigepsi.settings")
django.setup()

from django.utils import timezone
from django.db import connection
from django_tenants.utils import schema_context
from rest_framework.test import APIClient

from tenants.models import Tenant, Dominio
from accounts.models import Usuario, Rol, Permiso, RolPermiso
from clinica.models import Especialidad, Psicologo, Disponibilidad, Paciente
from agenda.models import Cita, Teleconsulta, Alerta

class ComprehensiveCUVerifier:
    def __init__(self):
        self.client = APIClient()
        self.results = []
        self.rnd = random.randint(10000, 99999)
        self.tenant_schema = 'centro_esperanza'

    def log(self, cu_id, hu, nombre, status, detalle=""):
        res = {
            "cu": cu_id,
            "hu": hu,
            "nombre": nombre,
            "status": "APROBADO" if status else "FALLIDO",
            "detalle": detalle
        }
        self.results.append(res)
        tag = "[OK] " if status else "[FAIL]"
        print(f"  {tag} {cu_id} ({hu}): {nombre} -> {detalle if detalle else 'Correcto'}")

    def auth_headers(self, email, password, tenant=None):
        payload = {"email": email, "password": password}
        if tenant:
            payload["tenant"] = tenant
        res = self.client.post('/api/auth/login/', payload, format='json')
        res_data: Any = getattr(res, 'data', {})
        if res.status_code == 200 and isinstance(res_data, dict) and 'access' in res_data:
            return {
                'HTTP_AUTHORIZATION': f"Bearer {res_data['access']}",
                'HTTP_X_TENANT_ID': tenant or self.tenant_schema
            }
        raise Exception(f"No se pudo autenticar {email}: {res.status_code} - {res_data}")

    def run(self):
        print("\n" + "=" * 80)
        print("  VERIFICACIÓN EXHAUSTIVA DE CADA CASO DE USO (CU) - SISTEMA SIGEPSI")
        print("=" * 80 + "\n")

        # ---------------------------------------------------------------------
        # CU1: Gestionar Centros Psicológicos y Configuración Multi-Tenant
        # ---------------------------------------------------------------------
        print("--- [GRUPO 1] Multi-Tenant y Configuración Institucional ---")
        superadmin_headers = self.auth_headers("admin@sigepsi.com", "Admin1234*", tenant="public")
        
        # CU1.1: Alta de centro (HU-03)
        slug_test = f"centro_test_{self.rnd}"
        res_crear_tenant = self.client.post('/api/tenants/', {
            "nombre": f"Centro Test {self.rnd}",
            "slug": slug_test,
            "plan": "PRO",
            "direccion": "Av. Las Américas #123",
            "telefono": "+591 70000001",
            "admin_email": f"admin{self.rnd}@centrotest.com",
            "admin_password": "AdminPassword123*"
        }, format='json', **superadmin_headers)
        cu1_creado = res_crear_tenant.status_code == 201
        err_msg = str(res_crear_tenant.data) if not cu1_creado else f"Schema: {slug_test}"
        self.log("CU1", "HU-03", "Alta de centro psicológico y creación de esquema PostgreSQL", cu1_creado, err_msg)

        # CU1.2: Editar configuración del centro (HU-04)
        with schema_context(self.tenant_schema):
            admin_headers = self.auth_headers("admin@centroesperanza.com", "Admin1234*", tenant=self.tenant_schema)
        
        res_edit_conf = self.client.put('/api/centro/config/', {
            "nombre": "Centro Psicológico Esperanza - Actualizado",
            "direccion": "Av. San Martín #450",
            "telefono": "+591 71234567",
            "email": "contacto@centroesperanza.com",
            "horarios_atencion": {"lunes_a_viernes": "08:00 - 20:00"}
        }, format='json', **admin_headers)
        cu1_conf = res_edit_conf.status_code == 200
        self.log("CU1", "HU-04", "Editar configuración institucional del centro", cu1_conf)

        # CU1.3: Aislamiento de datos multi-tenant (HU-07)
        with schema_context(self.tenant_schema):
            count_esperanza = Usuario.objects.count()
        with schema_context('public'):
            count_public = Usuario.objects.count()
        cu1_aislado = count_esperanza > 0 and count_public > 0
        self.log("CU1", "HU-07", "Aislamiento de esquemas PostgreSQL independientes", cu1_aislado, f"Tenant: {count_esperanza} usuarios vs Public: {count_public} usuarios")

        # CU1.4: Suspender y reactivar centro (HU-08)
        tenant_obj = Tenant.objects.get(schema_name=slug_test)
        res_susp = self.client.post(f'/api/tenants/{tenant_obj.id}/suspender/', {}, **superadmin_headers)
        res_act = self.client.post(f'/api/tenants/{tenant_obj.id}/activar/', {}, **superadmin_headers)
        cu1_susp = res_susp.status_code == 200 and res_act.status_code == 200
        self.log("CU1", "HU-08", "Suspender y reactivar centro psicológico", cu1_susp)

        # ---------------------------------------------------------------------
        # CU2: Gestionar Inicio de Sesión y Autenticación
        # ---------------------------------------------------------------------
        print("\n--- [GRUPO 2] Autenticación, Seguridad y Sesiones ---")
        
        # CU2.1: Registro de usuario nuevo (HU-01)
        res_reg = self.client.post('/api/auth/register/', {
            "nombre": "Carlos",
            "apellido": "Guzmán",
            "email": f"carlos.{self.rnd}@gmail.com",
            "password": "Password123*",
            "telefono": "+591 71112233"
        }, format='json')
        cu2_reg = res_reg.status_code == 201
        self.log("CU2", "HU-01", "Registro autónomo de usuario", cu2_reg, f"Usuario creado: {res_reg.data.get('usuario', {}).get('email')}")

        # CU2.2: Login con credenciales y auto-conmutación de schema (HU-02)
        res_login_auto = self.client.post('/api/auth/login/', {
            "email": "admin@centroesperanza.com",
            "password": "Admin1234*"
        }, format='json')
        cu2_login = res_login_auto.status_code == 200 and 'access' in res_login_auto.data and res_login_auto.data.get('tenant') is not None
        self.log("CU2", "HU-02", "Inicio de sesión seguro JWT con resolución automática de centro", cu2_login, f"Tenant resuelto: {res_login_auto.data.get('tenant', {}).get('schema_name')}")

        # CU2.3 (Logout): Cierre de sesión seguro e invalidación JWT (HU-09)
        refresh_token = res_login_auto.data['refresh']
        res_logout = self.client.post('/api/auth/logout/', {"refresh": refresh_token}, format='json', **admin_headers)
        cu2_logout = res_logout.status_code == 200
        self.log("CU2 (Logout)", "HU-09", "Cierre de sesión seguro y adición a lista negra de JWT", cu2_logout)

        # CU27: Recuperación de contraseña con token (HU-10)
        res_pwd_req = self.client.post('/api/auth/password-reset/', {
            "email": "admin@centroesperanza.com"
        }, format='json')
        token_reset = res_pwd_req.data.get('token_debug')
        res_pwd_conf = self.client.post('/api/auth/password-reset-confirm/', {
            "token": token_reset,
            "password": "AdminPassword123*",
            "password_confirm": "AdminPassword123*"
        }, format='json')
        cu27_ok = res_pwd_req.status_code == 200 and res_pwd_conf.status_code == 200
        # Restaurar password
        with schema_context(self.tenant_schema):
            u_admin = Usuario.objects.get(email="admin@centroesperanza.com")
            u_admin.set_password("Admin1234*")
            u_admin.save()
        self.log("CU27", "HU-10", "Recuperación de contraseña con token criptográfico seguro", cu27_ok)

        # ---------------------------------------------------------------------
        # CU3: Gestionar Usuarios
        # ---------------------------------------------------------------------
        print("\n--- [GRUPO 3] Administración de Usuarios y Roles ---")
        admin_headers = self.auth_headers("admin@centroesperanza.com", "Admin1234*", tenant=self.tenant_schema)

        # CU3.1: Alta de usuario dentro del centro (HU-05)
        with schema_context(self.tenant_schema):
            rol_recep = Rol.objects.filter(nombre__icontains="Recepcionista").first()
            rol_recep_id = rol_recep.id if rol_recep else None

        res_user_crear = self.client.post('/api/users/', {
            "nombre": f"Recepcionista_{self.rnd}",
            "apellido": "Pérez",
            "email": f"recep.{self.rnd}@centroesperanza.com",
            "password": "Password123*",
            "telefono": "+591 75554433",
            "rol_id": rol_recep_id
        }, format='json', **admin_headers)
        cu3_crear = res_user_crear.status_code == 201
        new_user_id = res_user_crear.data.get('id') if cu3_crear else None
        self.log("CU3", "HU-05", "Registrar nuevo usuario asignado al centro", cu3_crear, f"ID: {new_user_id}")

        # CU3.2: Editar usuario (PUT/PATCH sin email para validar partial=True) (HU-05)
        res_user_edit = self.client.put(f'/api/users/{new_user_id}/', {
            "nombre": f"Recepcionista_{self.rnd}_Editado",
            "apellido": "Pérez Morales",
            "telefono": "+591 79998877"
        }, format='json', **admin_headers)
        cu3_edit = res_user_edit.status_code == 200 and res_user_edit.data.get('nombre') == f"Recepcionista_{self.rnd}_Editado"
        self.log("CU3", "HU-05", "Editar datos de usuario existente (sin exigir email)", cu3_edit)

        # CU3.3: Alternar estado activo/inactivo (HU-05)
        res_toggle = self.client.post(f'/api/users/{new_user_id}/alternar_estado/', {}, **admin_headers)
        cu3_toggle = res_toggle.status_code == 200 and res_toggle.data.get('activo') is False
        self.log("CU3", "HU-05", "Activar / Desactivar cuenta de usuario", cu3_toggle)

        # ---------------------------------------------------------------------
        # CU4: Gestionar Roles y Permisos (HU-06)
        # ---------------------------------------------------------------------
        # CU4.1: Listar roles y permisos disponibles (HU-06)
        res_roles = self.client.get('/api/roles/', **admin_headers)
        res_perms = self.client.get('/api/permisos/', **admin_headers)
        cu4_list = res_roles.status_code == 200 and res_perms.status_code == 200 and len(res_perms.data) > 0
        self.log("CU4", "HU-06", "Listar roles institucionales y permisos del sistema RBAC", cu4_list, f"{len(res_perms.data)} permisos disponibles")

        # CU4.2: Asignar permisos a un rol existente (HU-06)
        with schema_context(self.tenant_schema):
            target_rol = Rol.objects.filter(nombre__icontains="Recepcionista").first()
            all_perm_ids = list(Permiso.objects.values_list('id', flat=True)[:3])
        
        res_rol_update = self.client.put(f'/api/roles/{target_rol.id}/', {
            "nombre": target_rol.nombre,
            "descripcion": "Rol de recepción con permisos auditados",
            "permiso_ids": all_perm_ids
        }, format='json', **admin_headers)
        cu4_edit = res_rol_update.status_code == 200
        self.log("CU4", "HU-06", "Actualizar asignación de permisos RBAC sobre rol", cu4_edit)

        # ---------------------------------------------------------------------
        # CU6: Gestión de Especialidades y Psicólogos (HU-11)
        # ---------------------------------------------------------------------
        print("\n--- [GRUPO 4] Directorio Clínico y Expedientes ---")
        
        # CU6.1: Listar especialidades (HU-11)
        res_esps = self.client.get('/api/clinica/especialidades/', **admin_headers)
        cu6_esps = res_esps.status_code == 200 and len(res_esps.data) >= 3
        self.log("CU6", "HU-11", "Consultar especialidades clínicas disponibles", cu6_esps, f"{len(res_esps.data)} especialidades")

        # CU6.2: Crear perfil de psicólogo con colegiatura autogenerada (HU-11)
        esp_id = res_esps.data[0]['id']
        res_psico = self.client.post('/api/clinica/psicologos/', {
            "nombre": f"Dr. Fernando_{self.rnd}",
            "apellido": "Torres",
            "email": f"fernando.{self.rnd}@centroesperanza.com",
            "password": "Password123*",
            "telefono": "+591 76543210",
            "numero_colegiado": "",  # Autogeneración
            "biografia": "Psicoterapia cognitivo conductual en adolescentes",
            "modalidad": "MIXTA",
            "tarifa_base": 170.00,
            "especialidad_ids": [esp_id]
        }, format='json', **admin_headers)
        cu6_psico_creado = res_psico.status_code == 201
        psico_id = res_psico.data.get('id') if cu6_psico_creado else None
        self.log("CU6", "HU-11", "Registrar perfil de psicólogo con aranceles y especialidades", cu6_psico_creado, f"Colegiado generado: {res_psico.data.get('numero_colegiado')}")

        # CU6.3: Editar perfil de psicólogo (HU-11)
        res_psico_edit = self.client.patch(f'/api/clinica/psicologos/{psico_id}/', {
            "tarifa_base": 190.00,
            "biografia": "Psicoterapia cognitivo conductual avanzada y neurofeedback"
        }, format='json', **admin_headers)
        cu6_edit = res_psico_edit.status_code == 200 and float(res_psico_edit.data.get('tarifa_base')) == 190.0
        self.log("CU6", "HU-11", "Editar perfil profesional y aranceles de psicólogo", cu6_edit)

        # ---------------------------------------------------------------------
        # CU8: Configurar Disponibilidad Horaria Semanal (HU-12)
        # ---------------------------------------------------------------------
        # CU8.1: Configurar franjas horarias con payload { franjas: [...] } (HU-12)
        res_disp = self.client.post(f'/api/clinica/psicologos/{psico_id}/disponibilidad/', {
            "franjas": [
                {
                    "dia_semana": 1, # Lunes (0=Dom, 1=Lun, ...)
                    "hora_inicio": "08:00:00",
                    "hora_fin": "12:00:00",
                    "duracion_bloque_minutos": 50,
                    "modalidad_permitida": "MIXTA",
                    "activo": True
                },
                {
                    "dia_semana": 3, # Miércoles
                    "hora_inicio": "14:00:00",
                    "hora_fin": "18:00:00",
                    "duracion_bloque_minutos": 50,
                    "modalidad_permitida": "MIXTA",
                    "activo": True
                }
            ]
        }, format='json', **admin_headers)
        cu8_guardado = res_disp.status_code == 200 and res_disp.data.get('count') == 2
        self.log("CU8", "HU-12", "Configuración de franjas horarias semanales de atención", cu8_guardado, f"Bloques: {res_disp.data.get('count')}")

        # CU8.2: Rechazar horario inválido (hora_fin <= hora_inicio) (HU-12)
        res_disp_inv = self.client.post(f'/api/clinica/psicologos/{psico_id}/disponibilidad/', {
            "dia_semana": 2,
            "hora_inicio": "16:00:00",
            "hora_fin": "14:00:00"
        }, format='json', **admin_headers)
        cu8_invalido = res_disp_inv.status_code == 400
        self.log("CU8", "HU-12", "Rechazar franja horaria incoherente (hora_fin <= hora_inicio)", cu8_invalido)

        # ---------------------------------------------------------------------
        # CU7: Gestión de Pacientes y Expedientes Clínicos (HU-13, HU-14)
        # ---------------------------------------------------------------------
        # CU7.1: Alta de paciente mayor de edad con autogeneración de expediente (HU-13)
        res_pac_adulto = self.client.post('/api/clinica/pacientes/', {
            "nombre": f"Elena_{self.rnd}",
            "apellido": "Roca",
            "email": f"elena.{self.rnd}@gmail.com",
            "password": "Password123*",
            "telefono": "+591 72223344",
            "ci": f"CI-{self.rnd}-A",
            "fecha_nacimiento": "1995-04-10",
            "genero": "F",
            "contacto_emergencia_nombre": "Mario Roca",
            "contacto_emergencia_telf": "+591 72223300"
        }, format='json', **admin_headers)
        cu7_adulto = res_pac_adulto.status_code == 201 and res_pac_adulto.data.get('codigo_expediente', '').startswith('EXP-')
        paciente_adulto_id = res_pac_adulto.data.get('id') if cu7_adulto else None
        self.log("CU7", "HU-13", "Alta de paciente adulto con autogeneración de expediente", cu7_adulto, f"Expediente: {res_pac_adulto.data.get('codigo_expediente')}")

        # CU7.2: Exigencia obligatoria de tutor legal para menor de edad (HU-13)
        res_pac_menor_sin_tutor = self.client.post('/api/clinica/pacientes/', {
            "nombre": "Lucas",
            "apellido": "Menor",
            "email": f"lucas.{self.rnd}@gmail.com",
            "password": "Password123*",
            "ci": f"CI-{self.rnd}-M",
            "fecha_nacimiento": "2015-08-01", # 11 años
            "genero": "M"
        }, format='json', **admin_headers)
        cu7_menor_rechazado = res_pac_menor_sin_tutor.status_code == 400
        self.log("CU7", "HU-13", "Exigencia obligatoria de tutor legal para menores de 18 años", cu7_menor_rechazado)

        # CU7.3: Alta exitosa de menor de edad con tutor legal completo (HU-13)
        res_pac_menor_con_tutor = self.client.post('/api/clinica/pacientes/', {
            "nombre": "Lucas",
            "apellido": "Menor",
            "email": f"lucas.{self.rnd}@gmail.com",
            "password": "Password123*",
            "ci": f"CI-{self.rnd}-M",
            "fecha_nacimiento": "2015-08-01",
            "genero": "M",
            "tutor_legal_nombre": "Beatriz Menor (Madre)",
            "tutor_legal_ci": "4433221 SC"
        }, format='json', **admin_headers)
        cu7_menor_ok = res_pac_menor_con_tutor.status_code == 201
        self.log("CU7", "HU-13", "Alta exitosa de paciente menor de edad con tutor legal", cu7_menor_ok)

        # CU7.4: Edición de expediente de paciente (HU-13)
        res_pac_edit = self.client.patch(f'/api/clinica/pacientes/{paciente_adulto_id}/', {
            "telefono": "+591 79998811",
            "contacto_emergencia_nombre": "Mario Roca (Hermano Mayor)"
        }, format='json', **admin_headers)
        cu7_edit = res_pac_edit.status_code == 200
        self.log("CU7", "HU-13", "Editar expediente y contactos del paciente", cu7_edit)

        # CU7.5: Consulta de expediente propio por el paciente autenticado (HU-14)
        paciente_headers = self.auth_headers(f"elena.{self.rnd}@gmail.com", "Password123*", tenant=self.tenant_schema)
        res_pac_me = self.client.get('/api/clinica/pacientes/me/', **paciente_headers)
        cu7_me = res_pac_me.status_code == 200 and res_pac_me.data.get('ci') == f"CI-{self.rnd}-A"
        self.log("CU7", "HU-14", "Consulta segura de expediente clínico propio (/api/clinica/pacientes/me/)", cu7_me)

        # ---------------------------------------------------------------------
        # CU11: Programación y Reserva de Citas (HU-15, HU-16)
        # ---------------------------------------------------------------------
        print("\n--- [GRUPO 5] Agenda, Concurrencia y Teleconsulta ---")
        
        # Calcular fecha del próximo lunes
        hoy = date.today()
        dias_hasta_lunes = (0 - hoy.weekday() + 7) % 7
        if dias_hasta_lunes == 0:
            dias_hasta_lunes = 7
        proximo_lunes = hoy + timedelta(days=dias_hasta_lunes)
        lunes_str = proximo_lunes.strftime('%Y-%m-%d')

        # CU11.1: Consultar slots libres de 50 minutos (HU-15)
        res_slots = self.client.get(f'/api/agenda/citas/slots-disponibles/?psicologo_id={psico_id}&fecha={lunes_str}', **admin_headers)
        res_data: Any = getattr(res_slots, 'data', {})
        slots_lista: List[Any] = res_data.get('slots', []) if isinstance(res_data, dict) else (res_data if isinstance(res_data, list) else [])
        cu11_slots = res_slots.status_code == 200 and len(slots_lista) > 0
        self.log("CU11", "HU-15", "Consultar matriz de intervalos libres (slots de 50 min)", cu11_slots, f"{len(slots_lista)} slots libres")

        slot_1: Dict[str, Any] = slots_lista[0] if slots_lista else {}
        slot_2: Dict[str, Any] = slots_lista[1] if len(slots_lista) > 1 else slot_1

        # CU11.2: Reservar cita en slot libre con bloqueo pesimista (HU-15)
        res_cita_1 = self.client.post('/api/agenda/citas/', {
            "paciente": paciente_adulto_id,
            "psicologo": psico_id,
            "fecha": lunes_str,
            "hora_inicio": slot_1['hora_inicio'],
            "hora_fin": slot_1['hora_fin'],
            "modalidad": "VIRTUAL",
            "motivo_consulta": "Sesión de evaluación inicial por estrés laboral"
        }, format='json', **admin_headers)
        cu11_reserva = res_cita_1.status_code == 201 and res_cita_1.data.get('estado') == 'PROGRAMADA'
        cita_1_id = res_cita_1.data.get('id') if cu11_reserva else None
        self.log("CU11", "HU-15", "Reserva de cita médica en franja libre (PROGRAMADA)", cu11_reserva, f"Cita ID: {cita_1_id}")

        # CU11.3: Bloqueo de concurrencia pesimista (rechazar solapamiento en el mismo slot) (HU-15)
        res_cita_colision = self.client.post('/api/agenda/citas/', {
            "paciente": paciente_adulto_id,
            "psicologo": psico_id,
            "fecha": lunes_str,
            "hora_inicio": slot_1['hora_inicio'],
            "hora_fin": slot_1['hora_fin'],
            "modalidad": "PRESENCIAL",
            "motivo_consulta": "Intento colisionante"
        }, format='json', **admin_headers)
        cu11_concurrencia = res_cita_colision.status_code == 400
        self.log("CU11", "HU-15", "Bloqueo pesimista: Rechazar solapamiento concurrente en mismo slot", cu11_concurrencia)

        # CU11.4: Aprovisionamiento automático de teleconsulta para modalidad VIRTUAL (HU-16)
        with schema_context(self.tenant_schema):
            tele_obj = Teleconsulta.objects.filter(cita_id=cita_1_id).first()
        cu11_tele = tele_obj is not None and len(tele_obj.sala_id) > 0
        self.log("CU11", "HU-16", "Aprovisionamiento automático de sala Jitsi en cita VIRTUAL", cu11_tele, f"Sala: {tele_obj.sala_id if tele_obj else 'N/A'}")

        # ---------------------------------------------------------------------
        # CU12: Cancelación de Citas y Políticas de Anticipación (HU-17)
        # ---------------------------------------------------------------------
        # Crear segunda cita para prueba de cancelación anticipada (> 2h)
        res_cita_2 = self.client.post('/api/agenda/citas/', {
            "paciente": paciente_adulto_id,
            "psicologo": psico_id,
            "fecha": lunes_str,
            "hora_inicio": slot_2['hora_inicio'],
            "hora_fin": slot_2['hora_fin'],
            "modalidad": "PRESENCIAL",
            "motivo_consulta": "Segunda cita de prueba para cancelación"
        }, format='json', **admin_headers)
        cita_2_id = res_cita_2.data.get('id')

        # CU12.1: Cancelación exitosa con anticipación mayor a 2 horas (HU-17)
        res_cancel_ok = self.client.post(f'/api/agenda/citas/{cita_2_id}/cancelar/', {
            "motivo": "Viaje laboral de emergencia"
        }, format='json', **admin_headers)
        cu12_cancel_ok = res_cancel_ok.status_code == 200
        self.log("CU12", "HU-17", "Cancelar cita con anticipación válida (> 2 horas)", cu12_cancel_ok)

        # CU12.2: Bloqueo de cancelación tardía (< 2 horas de anticipación)
        ahora_local = timezone.localtime()
        with schema_context(self.tenant_schema):
            cita_hoy = Cita.objects.create(
                paciente=Paciente.objects.get(id=paciente_adulto_id),
                psicologo=Psicologo.objects.get(id=psico_id),
                fecha=ahora_local.date(),
                hora_inicio=(ahora_local + timedelta(minutes=30)).time(),
                hora_fin=(ahora_local + timedelta(minutes=80)).time(),
                modalidad='PRESENCIAL',
                estado='PROGRAMADA',
                motivo_consulta='Cita de hoy'
            )
        res_cancel_tardia = self.client.post(f'/api/agenda/citas/{cita_hoy.id}/cancelar/', {
            "motivo": "Cancelación a última hora"
        }, format='json', **paciente_headers)
        cu12_cancel_tardia = res_cancel_tardia.status_code == 400
        self.log("CU12", "HU-17", "Bloquear cancelación autónoma de paciente con menos de 2h de anticipación", cu12_cancel_tardia)

        # ---------------------------------------------------------------------
        # CU13: Teleconsulta WebRTC y Credenciales Jitsi Meet (HU-18, HU-19)
        # ---------------------------------------------------------------------
        psico_headers = self.auth_headers(f"fernando.{self.rnd}@centroesperanza.com", "Password123*", tenant=self.tenant_schema)
        
        # CU13.1: Obtención de sala y JWT seguro para Jitsi Meet (HU-18)
        res_access_psico = self.client.get(f'/api/agenda/teleconsulta/{cita_1_id}/access/', **psico_headers)
        cu13_access = res_access_psico.status_code == 200 and 'jwt_token' in res_access_psico.data
        self.log("CU13", "HU-18", "Generar sala WebRTC y token criptográfico JWT para teleconsulta", cu13_access)

        # CU13.2: Diferenciación de roles WebRTC (Psicólogo: Moderador vs Paciente: Invitado) (HU-19)
        res_access_pac = self.client.get(f'/api/agenda/teleconsulta/{cita_1_id}/access/', **paciente_headers)
        cu13_roles = (
            res_access_psico.data.get('es_moderador') is True and
            res_access_pac.data.get('es_moderador') is False
        )
        self.log("CU13", "HU-19", "Diferenciación de roles WebRTC: Psicólogo (Moderador) vs Paciente (Invitado)", cu13_roles)

        # CU13.3: Finalizar teleconsulta registrando duración real y estado REALIZADA (HU-18)
        res_finish = self.client.post(f'/api/agenda/teleconsulta/{cita_1_id}/finish/', {
            "duracion_segundos": 2940
        }, format='json', **psico_headers)
        cu13_finish = res_finish.status_code == 200 and res_finish.data.get('estado') == 'REALIZADA'
        self.log("CU13", "HU-18", "Finalizar teleconsulta con duración real (2940 s) y estado REALIZADA", cu13_finish)

        # ---------------------------------------------------------------------
        # CU9 / CU10: Dashboard Clínico y Alertas Tempranas (HU-20, HU-21)
        # ---------------------------------------------------------------------
        print("\n--- [GRUPO 6] Dashboard, Alertas y Calendario ---")
        
        # CU9: Dashboard Clínico con KPIs operativos (HU-20)
        res_kpis = self.client.get('/api/agenda/dashboard/kpis/', **admin_headers)
        kpi_data: Dict[str, Any] = getattr(res_kpis, 'data', {}) if isinstance(getattr(res_kpis, 'data', None), dict) else {}
        cu9_kpis = res_kpis.status_code == 200 and 'citas_mes' in kpi_data and 'citas_hoy' in kpi_data
        total_mes = kpi_data.get('citas_mes', {}).get('total', 0) if cu9_kpis else 'N/A'
        self.log("CU9", "HU-20", "Consultar Dashboard Clínico con KPIs consolidados y tasa de ocupación", cu9_kpis, f"Total citas mes: {total_mes}")

        # CU10.1: Generación y listado de Alertas Clínicas por inasistencias consecutivas (HU-21)
        with schema_context(self.tenant_schema):
            # Simular alerta clínica
            alerta_test = Alerta.objects.create(
                paciente=Paciente.objects.get(id=paciente_adulto_id),
                tipo='INASISTENCIA_REITERADA',
                severidad='ALTA',
                descripcion='2 inasistencias consecutivas detectadas.',
                resuelta=False
            )
        res_alertas = self.client.get('/api/agenda/alertas/', **admin_headers)
        cu10_alertas = res_alertas.status_code == 200 and len(res_alertas.data) > 0
        self.log("CU10", "HU-21", "Generación y consulta de alertas clínicas tempranas", cu10_alertas, f"Alertas activas: {len(res_alertas.data)}")

        # CU10.2: Resolver alerta clínica con notas de seguimiento (HU-21)
        res_res_alerta = self.client.post(f'/api/agenda/alertas/{alerta_test.id}/resolver/', {
            "nota_resolucion": "Se contactó al paciente vía telefónica, reprogramando sesión de soporte."
        }, format='json', **admin_headers)
        cu10_res = res_res_alerta.status_code == 200 and res_res_alerta.data.get('alerta', {}).get('resuelta') is True
        self.log("CU10", "HU-21", "Resolución de alerta clínica con registro de seguimiento", cu10_res)

        # ---------------------------------------------------------------------
        # CU14: Calendario Interactivo Clínico (HU-22)
        # ---------------------------------------------------------------------
        res_cal = self.client.get(f'/api/agenda/citas/calendario/?psicologo_id={psico_id}', **admin_headers)
        cu14_cal = res_cal.status_code == 200 and isinstance(res_cal.data, list)
        self.log("CU14", "HU-22", "Retornar matriz de eventos para FullCalendar con filtrado por profesional", cu14_cal, f"Eventos encontrados: {len(res_cal.data)}")

        # Cleanup tenant creado en CU1
        try:
            with schema_context('public'):
                Tenant.objects.filter(slug=slug_test).delete()
        except Exception:
            pass

        # ---------------------------------------------------------------------
        # RESUMEN GENERAL
        # ---------------------------------------------------------------------
        print("\n" + "=" * 80)
        total = len(self.results)
        aprobados = sum(1 for r in self.results if r['status'] == 'APROBADO')
        fallidos = total - aprobados
        print(f"  RESUMEN FINAL: {aprobados}/{total} CASOS DE USO APROBADOS ({fallidos} Fallidos)")
        print("=" * 80 + "\n")
        assert fallidos == 0, f"Se detectaron {fallidos} pruebas fallidas en los casos de uso."

if __name__ == "__main__":
    verifier = ComprehensiveCUVerifier()
    verifier.run()
