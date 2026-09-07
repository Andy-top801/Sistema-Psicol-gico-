import os
import sys
from datetime import date, time, timedelta
import django

# Inicializar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')
django.setup()

from django.utils import timezone
from rest_framework.test import APIClient
from django_tenants.utils import schema_context
from accounts.models import Usuario, Rol
from clinica.models import Especialidad, Psicologo, Disponibilidad, Paciente
from agenda.models import Cita, Teleconsulta, Alerta

class Sprint1Verifier:
    def __init__(self):
        self.client = APIClient()
        self.tenant_schema = 'centro_esperanza'
        self.results = []
        self.passed = 0
        self.failed = 0

    def log_result(self, test_id, hu, description, status, details=""):
        res = {
            "id": test_id,
            "hu": hu,
            "desc": description,
            "status": "APROBADO" if status else "FALLIDO",
            "details": details
        }
        self.results.append(res)
        if status:
            self.passed += 1
            print(f"  [OK] {test_id} ({hu}): {description}")
        else:
            self.failed += 1
            print(f"  [FAIL] {test_id} ({hu}): {description} -> {details}")

    def auth_headers(self, email, password):
        res = self.client.post('/api/auth/login/', {
            "email": email,
            "password": password
        }, format='json', HTTP_X_TENANT_ID=self.tenant_schema)
        data = res.data if isinstance(res.data, dict) else {}
        if res.status_code == 200 and 'access' in data:
            return {
                'HTTP_AUTHORIZATION': f"Bearer {data['access']}",
                'HTTP_X_TENANT_ID': self.tenant_schema
            }
        return {'HTTP_X_TENANT_ID': self.tenant_schema}

    def run_all(self):
        print("\n========================================================")
        print("   EJECUCIÓN DE PLAN DE PRUEBAS - SPRINT 1 (SIGEPSI)")
        print("   Clínica, Agenda, Teleconsulta WebRTC, Dashboard y Alertas")
        print("========================================================\n")

        with schema_context(self.tenant_schema):
            # Obtener tokens para Admin, Psicólogo y Paciente
            admin_headers = self.auth_headers("admin@centroesperanza.com", "Admin1234*")
            psico_headers = self.auth_headers("carlos.mendoza@centroesperanza.com", "Psicologo123*")
            paciente_headers = self.auth_headers("juan.perez@paciente.com", "Paciente123*")

            # -----------------------------------------------------------------
            # HU-11: Gestión de Especialidades y Perfiles de Psicólogos
            # -----------------------------------------------------------------
            print("--- Módulo 1: Especialidades y Directorio de Psicólogos (HU-11) ---")
            
            # TP-26: Listar especialidades
            res = self.client.get('/api/clinica/especialidades/', **admin_headers)
            self.log_result("TP-26", "HU-11", "Listar especialidades clínicas disponibles", res.status_code == 200 and len(res.data) >= 4)

            # TP-27: Crear perfil de psicólogo válido
            Psicologo.objects.filter(numero_colegiado="COL-TEST-9999").delete()
            Usuario.objects.filter(email="nuevo.psicologo@test.com").delete()
            res = self.client.post('/api/clinica/psicologos/', {
                "email": "nuevo.psicologo@test.com",
                "password": "Password123*",
                "nombre": "Roberto",
                "apellido": "Gómez",
                "telefono": "71112233",
                "numero_colegiado": "COL-TEST-9999",
                "biografia": "Terapeuta infantil",
                "modalidad": "MIXTA",
                "tarifa_base": 160.00
            }, format='json', **admin_headers)
            psico_valido = (res.status_code == 201)
            psico_id = res.data.get('id') if psico_valido else None
            self.log_result("TP-27", "HU-11", "Crear perfil de psicólogo con credenciales y colegiatura", psico_valido)

            # TP-28: Rechazo de tarifa base negativa
            res = self.client.post('/api/clinica/psicologos/', {
                "email": "invalido.tarifa@test.com",
                "password": "Password123*",
                "nombre": "Invalido",
                "numero_colegiado": "COL-TEST-0000",
                "tarifa_base": -50.00
            }, format='json', **admin_headers)
            self.log_result("TP-28", "HU-11", "Rechazar tarifa arancelaria negativa (< 0)", res.status_code == 400)

            # TP-29: Rechazo de colegiatura duplicada
            res = self.client.post('/api/clinica/psicologos/', {
                "email": "duplicado.cole@test.com",
                "password": "Password123*",
                "nombre": "Duplicado",
                "numero_colegiado": "COL-TEST-9999",
                "tarifa_base": 150.00
            }, format='json', **admin_headers)
            self.log_result("TP-29", "HU-11", "Rechazar número de colegiado duplicado", res.status_code == 400)


            # -----------------------------------------------------------------
            # HU-12: Disponibilidad y Carga Horaria Semanal
            # -----------------------------------------------------------------
            print("\n--- Módulo 2: Disponibilidad Horaria Semanal (HU-12) ---")
            psico_carlos = Psicologo.objects.get(usuario__email="carlos.mendoza@centroesperanza.com")

            # TP-30: Configurar bloques de disponibilidad válidos
            Disponibilidad.objects.filter(psicologo=psico_carlos, dia_semana=6).delete()
            res = self.client.post(f'/api/clinica/psicologos/{psico_carlos.id}/disponibilidad/', {
                "dia_semana": 6, # Sábado
                "hora_inicio": "08:00:00",
                "hora_fin": "12:00:00",
                "duracion_bloque_min": 50
            }, format='json', **psico_headers)
            self.log_result("TP-30", "HU-12", "Configurar franja horaria válida de atención", res.status_code == 201)

            # TP-31: Rechazo de rango horario invertido (inicio >= fin)
            res = self.client.post(f'/api/clinica/psicologos/{psico_carlos.id}/disponibilidad/', {
                "dia_semana": 6,
                "hora_inicio": "14:00:00",
                "hora_fin": "10:00:00",
                "duracion_bloque_min": 50
            }, format='json', **psico_headers)
            self.log_result("TP-31", "HU-12", "Rechazar franja horaria incoherente (hora_fin <= hora_inicio)", res.status_code == 400)

            # TP-32: Rechazo de traslape en el mismo día
            res = self.client.post(f'/api/clinica/psicologos/{psico_carlos.id}/disponibilidad/', {
                "dia_semana": 6,
                "hora_inicio": "09:00:00",
                "hora_fin": "11:00:00",
                "duracion_bloque_min": 50
            }, format='json', **psico_headers)
            self.log_result("TP-32", "HU-12", "Rechazar franja horaria traslapada con otra existente", res.status_code == 400)


            # -----------------------------------------------------------------
            # HU-13 & HU-14: Expediente de Pacientes (Web & Móvil)
            # -----------------------------------------------------------------
            print("\n--- Módulo 3: Expedientes Clínicos y Validación de Tutor (HU-13, HU-14) ---")

            # TP-33: Registrar paciente adulto válido
            Paciente.objects.filter(ci="99887766-LP").delete()
            Usuario.objects.filter(email="paciente.adulto@test.com").delete()
            res = self.client.post('/api/clinica/pacientes/', {
                "email": "paciente.adulto@test.com",
                "password": "Password123*",
                "nombre": "Andrés",
                "apellido": "Cáceres",
                "telefono": "75544332",
                "codigo_expediente": "EXP-TEST-ADULTO",
                "ci": "99887766-LP",
                "fecha_nacimiento": "1998-07-20",
                "genero": "M"
            }, format='json', **admin_headers)
            self.log_result("TP-33", "HU-13", "Registrar paciente mayor de edad sin requerir tutor legal", res.status_code == 201)

            # TP-34: Rechazo de paciente menor de 18 años SIN tutor legal
            Paciente.objects.filter(ci="11223344-SC").delete()
            Usuario.objects.filter(email="menor.sintutor@test.com").delete()
            res = self.client.post('/api/clinica/pacientes/', {
                "email": "menor.sintutor@test.com",
                "password": "Password123*",
                "nombre": "Lucas",
                "apellido": "Menor",
                "telefono": "78899001",
                "codigo_expediente": "EXP-TEST-MENOR-1",
                "ci": "11223344-SC",
                "fecha_nacimiento": "2015-08-10", # 11 años
                "genero": "M",
                "tutor_legal_nombre": "",
                "tutor_legal_ci": ""
            }, format='json', **admin_headers)
            tiene_error_tutor = (res.status_code == 400) and ('tutor_legal_nombre' in str(res.data))
            self.log_result("TP-34", "HU-13", "Exigir obligatoriamente tutor legal para pacientes menores de edad", tiene_error_tutor)

            # TP-35: Aceptación de paciente menor de 18 años CON tutor legal
            Paciente.objects.filter(ci="11223344-SC").delete()
            Usuario.objects.filter(email="menor.contutor@test.com").delete()
            res = self.client.post('/api/clinica/pacientes/', {
                "email": "menor.contutor@test.com",
                "password": "Password123*",
                "nombre": "Lucas",
                "apellido": "Menor",
                "telefono": "78899001",
                "codigo_expediente": "EXP-TEST-MENOR-2",
                "ci": "11223344-SC",
                "fecha_nacimiento": "2015-08-10",
                "genero": "M",
                "tutor_legal_nombre": "María Elena Menor",
                "tutor_legal_ci": "33445566-SC"
            }, format='json', **admin_headers)
            self.log_result("TP-35", "HU-13", "Registrar paciente menor de edad con datos de tutor legal completos", res.status_code == 201)

            # TP-36: Consulta de expediente propio desde app móvil / web
            res = self.client.get('/api/clinica/pacientes/me/', **paciente_headers)
            self.log_result("TP-36", "HU-14", "Consulta segura de expediente propio del paciente (/api/clinica/pacientes/me/)", res.status_code == 200)


            # -----------------------------------------------------------------
            # HU-15 & HU-16: Programación y Concurrencia de Citas
            # -----------------------------------------------------------------
            print("\n--- Módulo 4: Motor de Citas y Concurrencia Transaccional (HU-15, HU-16) ---")
            pac_juan = Paciente.objects.get(usuario__email="juan.perez@paciente.com")
            pac_sofia = Paciente.objects.get(usuario__email="sofia.castro@paciente.com")

            # Próximo lunes para asegurar disponibilidad laboral activa
            hoy = date.today()
            dias_hasta_lunes = (0 - hoy.weekday() + 7) % 7
            if dias_hasta_lunes == 0:
                dias_hasta_lunes = 7
            proximo_lunes = hoy + timedelta(days=dias_hasta_lunes)

            # TP-37: Consultar slots libres
            res = self.client.get(f'/api/agenda/citas/slots-disponibles/?psicologo_id={psico_carlos.id}&fecha={proximo_lunes.strftime("%Y-%m-%d")}', **paciente_headers)
            slots_data = res.data if isinstance(res.data, dict) else {}
            has_slots = (res.status_code == 200) and ('slots' in slots_data) and isinstance(slots_data['slots'], list) and len(slots_data['slots']) > 0
            self.log_result("TP-37", "HU-15", "Consultar matriz de intervalos libres (slots de 50 min)", has_slots)

            # Limpiar citas previas en ese slot de prueba
            Cita.objects.filter(psicologo=psico_carlos, fecha=proximo_lunes, hora_inicio=time(11, 0)).delete()

            # TP-38: Reservar cita dentro de franja disponible
            res = self.client.post('/api/agenda/citas/', {
                "paciente": str(pac_juan.id),
                "psicologo": str(psico_carlos.id),
                "fecha": proximo_lunes.strftime("%Y-%m-%d"),
                "hora_inicio": "11:00:00",
                "hora_fin": "11:50:00",
                "modalidad": "PRESENCIAL",
                "motivo_consulta": "Sesión de evaluación terapéutica"
            }, format='json', **paciente_headers)
            cita_creada = (res.status_code == 201)
            cita_id = res.data.get('id') if cita_creada else None
            self.log_result("TP-38", "HU-15", "Reservar cita en franja libre con estado 'PROGRAMADA'", cita_creada)

            # TP-39: Rechazo de colisión / concurrencia (doble reserva simultánea en el mismo slot)
            res = self.client.post('/api/agenda/citas/', {
                "paciente": str(pac_sofia.id),
                "psicologo": str(psico_carlos.id),
                "fecha": proximo_lunes.strftime("%Y-%m-%d"),
                "hora_inicio": "11:00:00",
                "hora_fin": "11:50:00",
                "modalidad": "PRESENCIAL",
                "motivo_consulta": "Intento de colisión simultánea"
            }, format='json', **admin_headers)
            self.log_result("TP-39", "HU-15", "Bloqueo pesimista: Rechazar solapamiento de dos pacientes en el mismo slot", res.status_code == 400)

            # TP-40: Reserva virtual genera sala de teleconsulta
            Cita.objects.filter(psicologo=psico_carlos, fecha=proximo_lunes, hora_inicio=time(14, 0)).delete()
            res = self.client.post('/api/agenda/citas/', {
                "paciente": str(pac_sofia.id),
                "psicologo": str(psico_carlos.id),
                "fecha": proximo_lunes.strftime("%Y-%m-%d"),
                "hora_inicio": "14:00:00",
                "hora_fin": "14:50:00",
                "modalidad": "VIRTUAL",
                "motivo_consulta": "Sesión virtual de teleconsulta"
            }, format='json', **admin_headers)
            cita_virtual_creada = (res.status_code == 201) and (res.data.get('teleconsulta') is not None)
            cita_virtual_id = res.data.get('id') if cita_virtual_creada else None
            self.log_result("TP-40", "HU-16", "Reserva de cita virtual aprovisiona automáticamente registro de Teleconsulta", cita_virtual_creada)


            # -----------------------------------------------------------------
            # HU-17: Reprogramación y Cancelación con Anticipación
            # -----------------------------------------------------------------
            print("\n--- Módulo 5: Cancelación y Políticas de Anticipación (HU-17) ---")

            # TP-41: Cancelación exitosa con anticipación mayor a 2 horas (cita del próximo lunes)
            if cita_id:
                res = self.client.post(f'/api/agenda/citas/{cita_id}/cancelar/', {
                    "motivo": "Viaje imprevisto de trabajo del paciente"
                }, format='json', **paciente_headers)
                cancelacion_ok = (res.status_code == 200) and (res.data.get('cita', {}).get('estado') == 'CANCELADA')
                self.log_result("TP-41", "HU-17", "Cancelar cita con anticipación válida (> 2h)", cancelacion_ok)

            # TP-42: Paciente no puede cancelar cita que está a menos de 2 horas
            ahora = timezone.localtime()
            en_30_min = ahora + timedelta(minutes=30)
            cita_inminente = Cita.objects.create(
                paciente=pac_juan,
                psicologo=psico_carlos,
                fecha=en_30_min.date(),
                hora_inicio=en_30_min.time(),
                hora_fin=(en_30_min + timedelta(minutes=50)).time(),
                modalidad="PRESENCIAL",
                estado="PROGRAMADA"
            )
            res = self.client.post(f'/api/agenda/citas/{cita_inminente.id}/cancelar/', {
                "motivo": "Cancelación de último momento"
            }, format='json', **paciente_headers)
            tiene_error_anticipacion = (res.status_code == 400) and ('anticipacion' in str(res.data))
            self.log_result("TP-42", "HU-17", "Bloquear cancelación autónoma de paciente con menos de 2 horas de anticipación", tiene_error_anticipacion)


            # -----------------------------------------------------------------
            # HU-18 & HU-19: Teleconsulta WebRTC y Jitsi Meet (Web & Móvil)
            # -----------------------------------------------------------------
            print("\n--- Módulo 6: Teleconsulta Jitsi Meet y Tokens WebRTC (HU-18, HU-19) ---")

            if cita_virtual_id:
                # TP-43: Acceso a teleconsulta entrega room y JWT
                res = self.client.get(f'/api/agenda/teleconsulta/{cita_virtual_id}/access/', **psico_headers)
                data_tele = res.data if isinstance(res.data, dict) else {}
                acceso_ok = (res.status_code == 200) and ('jwt_token' in data_tele) and ('sala_id' in data_tele)
                self.log_result("TP-43", "HU-18", "Obtener sala y token criptográfico JWT para Jitsi Meet", acceso_ok)

                # TP-44: Diferenciación de roles (Psicólogo = Moderador, Paciente = Invitado, Ajeno = 403)
                es_mod = bool(data_tele.get('es_moderador', False))
                sofia_headers = self.auth_headers("sofia.castro@paciente.com", "Paciente123*")
                res_pac = self.client.get(f'/api/agenda/teleconsulta/{cita_virtual_id}/access/', **sofia_headers)
                data_pac = res_pac.data if isinstance(res_pac.data, dict) else {}
                pac_no_mod = (res_pac.status_code == 200) and (data_pac.get('es_moderador') is False)
                res_unauth = self.client.get(f'/api/agenda/teleconsulta/{cita_virtual_id}/access/', **paciente_headers)
                unauth_bloqueado = (res_unauth.status_code == 403)
                self.log_result("TP-44", "HU-18", "Diferenciación de roles WebRTC: Psicólogo (Moderador) vs Paciente (Invitado) y bloqueo a ajenos", es_mod and pac_no_mod and unauth_bloqueado)

                # TP-45: Finalizar teleconsulta registra duración y cambia estado a REALIZADA
                res = self.client.post(f'/api/agenda/teleconsulta/{cita_virtual_id}/finish/', {
                    "duracion_segundos": 2850 # 47.5 min
                }, format='json', **psico_headers)
                data_fin = res.data if isinstance(res.data, dict) else {}
                finalizacion_ok = (res.status_code == 200) and (data_fin.get('estado') == 'REALIZADA') and (data_fin.get('duracion_segundos') == 2850)
                self.log_result("TP-45", "HU-18", "Finalizar teleconsulta registra duración (2850 seg) y estado 'REALIZADA'", finalizacion_ok)


            # -----------------------------------------------------------------
            # HU-20: Dashboard Clínico y KPIs en Tiempo Real
            # -----------------------------------------------------------------
            print("\n--- Módulo 7: Dashboard Clínico y Métricas (HU-20) ---")

            # TP-46: Consulta de KPIs consolidados
            res = self.client.get('/api/agenda/dashboard/kpis/', **admin_headers)
            data_kpi = res.data if isinstance(res.data, dict) else {}
            mes_dict = data_kpi.get('citas_mes', {}) if isinstance(data_kpi.get('citas_mes'), dict) else {}
            kpis_validos = (
                res.status_code == 200 and
                'citas_hoy' in data_kpi and
                'citas_mes' in data_kpi and
                'tasa_ausentismo_pct' in mes_dict and
                'ocupacion_psicologos' in data_kpi
            )
            self.log_result("TP-46", "HU-20", "Consultar Dashboard con KPIs de citas, tasa de ausentismo y ocupación", kpis_validos)


            # -----------------------------------------------------------------
            # HU-21: Alertas Clínicas y Detección de Ausentismo
            # -----------------------------------------------------------------
            print("\n--- Módulo 8: Alertas Clínicas de Priorización (HU-21) ---")

            # TP-47: Registrar 2 inasistencias consecutivas dispara automáticamente Alerta de Severidad ALTA
            u_riesgo, _ = Usuario.objects.get_or_create(
                email="paciente.riesgo@test.com",
                defaults={
                    "nombre": "Valeria",
                    "apellido": "Riesgo",
                    "rol": Rol.objects.filter(nombre__icontains="Paciente").first()
                }
            )
            paciente_riesgo, _ = Paciente.objects.get_or_create(
                usuario=u_riesgo,
                defaults={
                    "codigo_expediente": "EXP-RIESGO-01",
                    "ci": "77889911-ALERTA",
                    "fecha_nacimiento": date(1996, 4, 12),
                    "genero": "F"
                }
            )
            Cita.objects.filter(paciente=paciente_riesgo).delete()
            Alerta.objects.filter(paciente=paciente_riesgo).delete()

            # Crear 2 citas en inasistencia consecutivas
            c1 = Cita.objects.create(
                paciente=paciente_riesgo,
                psicologo=psico_carlos,
                fecha=hoy - timedelta(days=5),
                hora_inicio=time(8, 0),
                hora_fin=time(8, 50),
                estado='INASISTENCIA'
            )
            c2 = Cita.objects.create(
                paciente=paciente_riesgo,
                psicologo=psico_carlos,
                fecha=hoy - timedelta(days=2),
                hora_inicio=time(8, 0),
                hora_fin=time(8, 50),
                estado='PROGRAMADA'
            )
            # Marcar la segunda a INASISTENCIA vía API para disparar la señal/servicio
            res = self.client.patch(f'/api/agenda/citas/{c2.id}/', {"estado": "INASISTENCIA"}, format='json', **admin_headers)
            alerta_creada = Alerta.objects.filter(
                paciente=paciente_riesgo,
                tipo='INASISTENCIA_REITERADA',
                severidad='ALTA',
                resuelta=False
            ).first()
            self.log_result("TP-47", "HU-21", "Generación reactiva de Alerta ALTA por 2 inasistencias consecutivas", alerta_creada is not None)

            # TP-48: Resolver alerta clínica con notas
            if alerta_creada:
                res = self.client.post(f'/api/agenda/alertas/{alerta_creada.id}/resolver/', {
                    "nota_resolucion": "Se contactó telefónicamente al paciente. Reagendó sesión para la próxima semana."
                }, format='json', **admin_headers)
                alerta_resuelta = (res.status_code == 200) and (res.data.get('alerta', {}).get('resuelta') is True)
                self.log_result("TP-48", "HU-21", "Resolver alerta clínica con registro de notas de seguimiento", alerta_resuelta)


            # -----------------------------------------------------------------
            # HU-22: Calendario Interactivo Multi-Vista
            # -----------------------------------------------------------------
            print("\n--- Módulo 9: Calendario Interactivo Clínico (HU-22) ---")

            # TP-49: Formato nativo para FullCalendar
            res = self.client.get('/api/agenda/citas/calendario/', **admin_headers)
            cal_valido = (res.status_code == 200) and isinstance(res.data, list) and len(res.data) > 0
            has_fc_fields = cal_valido and ('start' in res.data[0]) and ('backgroundColor' in res.data[0]) and ('extendedProps' in res.data[0])
            self.log_result("TP-49", "HU-22", "Retornar eventos con formato estructurado para FullCalendar", has_fc_fields)

        # -----------------------------------------------------------------
        # Resumen Final
        # -----------------------------------------------------------------
        print("\n========================================================")
        print(f" RESUMEN DE PRUEBAS SPRINT 1: {self.passed}/{len(self.results)} APROBADAS ({self.failed} Fallidas)")
        print("========================================================\n")
        return self.failed == 0


if __name__ == '__main__':
    verifier = Sprint1Verifier()
    success = verifier.run_all()
    sys.exit(0 if success else 1)
