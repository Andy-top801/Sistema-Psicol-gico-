from typing import Any
from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django_tenants.utils import schema_context, get_tenant_model
from accounts.models import Usuario, Rol, Permiso, RolPermiso
from clinica.models import Especialidad, Psicologo, Disponibilidad, Paciente
from agenda.models import Cita, Teleconsulta, Alerta

class Command(BaseCommand):
    help = "Siembra datos iniciales y de prueba del Sprint 1 (Especialidades, Psicólogos, Disponibilidad, Pacientes, Citas)"

    def add_arguments(self, parser):
        parser.add_argument('--tenant', type=str, default='centro_esperanza', help='Slug o schema_name del tenant donde sembrar los datos')

    def handle(self, *args, **options):
        tenant_target = options['tenant']
        Tenant = get_tenant_model()

        try:
            tenant = Tenant.objects.get(schema_name=tenant_target)
        except Tenant.DoesNotExist:
            try:
                tenant = Tenant.objects.get(slug=tenant_target)
            except Tenant.DoesNotExist:
                self.stderr.write(f"Tenant '{tenant_target}' no encontrado.")
                return

        self.stdout.write(f"==> Sembrando datos del Sprint 1 en esquema: {tenant.schema_name}")

        with schema_context(tenant.schema_name):
            atomic_tx: Any = transaction.atomic()
            with atomic_tx:
                # 1. Permisos del Sprint 1
                permisos_sprint1 = [
                    ('clinica.view_especialidad', 'Ver Especialidades', 'clinica'),
                    ('clinica.add_especialidad', 'Crear Especialidades', 'clinica'),
                    ('clinica.view_psicologo', 'Ver Psicólogos', 'clinica'),
                    ('clinica.add_psicologo', 'Crear Psicólogo', 'clinica'),
                    ('clinica.change_psicologo', 'Editar Psicólogo', 'clinica'),
                    ('clinica.change_disponibilidad', 'Editar Disponibilidad', 'clinica'),
                    ('clinica.view_paciente', 'Ver Pacientes', 'clinica'),
                    ('clinica.add_paciente', 'Crear Pacientes', 'clinica'),
                    ('clinica.change_paciente', 'Editar Pacientes', 'clinica'),
                    ('agenda.view_cita', 'Ver Citas', 'agenda'),
                    ('agenda.add_cita', 'Agendar Cita', 'agenda'),
                    ('agenda.change_cita', 'Modificar Cita', 'agenda'),
                    ('agenda.cancel_cita', 'Cancelar Cita', 'agenda'),
                    ('agenda.access_teleconsulta', 'Acceder a Teleconsulta', 'agenda'),
                    ('agenda.view_dashboard', 'Ver Dashboard Clínico', 'agenda'),
                    ('agenda.manage_alerta', 'Gestionar Alertas', 'agenda'),
                ]

                for cod, nom, mod in permisos_sprint1:
                    p, _ = Permiso.objects.get_or_create(
                        codigo=cod,
                        defaults={'nombre': nom, 'modulo': mod}
                    )
                    # Asignar a Admin de Centro
                    admin_rol = Rol.objects.filter(nombre__icontains="Admin").first()
                    if admin_rol:
                        RolPermiso.objects.get_or_create(rol=admin_rol, permiso=p)

                # 2. Especialidades Clínicas
                especialidades_data = [
                    ("Terapia Cognitivo-Conductual (TCC)", "Reestructuración cognitiva y abordaje de esquemas desadaptativos."),
                    ("Psicología Clínica y de la Salud", "Evaluación, diagnóstico y tratamiento de trastornos emocionales y del estado de ánimo."),
                    ("Terapia Familiar y de Pareja", "Intervención sistémica orientada a la resolución de conflictos vinculares."),
                    ("Neuropsicología y Rehabilitación", "Evaluación de funciones cognitivas y programas de estimulación en niños y adultos."),
                    ("Psicología Infantil y del Desarrollo", "Abordaje de trastornos del neurodesarrollo, conducta y apego en infancia y adolescencia.")
                ]

                especialidades_objs = {}
                for nom, desc in especialidades_data:
                    esp, _ = Especialidad.objects.get_or_create(nombre=nom, defaults={'descripcion': desc})
                    especialidades_objs[nom] = esp
                self.stdout.write(f"  [OK] {len(especialidades_objs)} especialidades aseguradas.")

                # 3. Roles
                rol_psico = Rol.objects.filter(nombre__icontains="Psicólogo").first()
                rol_paciente = Rol.objects.filter(nombre__icontains="Paciente").first()

                # 4. Psicólogos de Prueba
                psicologos_seed = [
                    {
                        "email": "carlos.mendoza@centroesperanza.com",
                        "nombre": "Carlos",
                        "apellido": "Mendoza Rojas",
                        "telefono": "70112233",
                        "colegiado": "COL-PSI-4589",
                        "biografia": "Psicólogo clínico con 10 años de experiencia en TCC y manejo de trastornos de ansiedad y depresión.",
                        "modalidad": "MIXTA",
                        "tarifa": 180.00,
                        "especialidades": ["Terapia Cognitivo-Conductual (TCC)", "Psicología Clínica y de la Salud"]
                    },
                    {
                        "email": "mariana.vargas@centroesperanza.com",
                        "nombre": "Mariana",
                        "apellido": "Vargas Arce",
                        "telefono": "70445566",
                        "colegiado": "COL-PSI-7821",
                        "biografia": "Especialista en terapia sistémica familiar y psicología infantil. Magíster en Terapia Vincular.",
                        "modalidad": "MIXTA",
                        "tarifa": 200.00,
                        "especialidades": ["Terapia Familiar y de Pareja", "Psicología Infantil y del Desarrollo"]
                    },
                    {
                        "email": "fernando.torrico@centroesperanza.com",
                        "nombre": "Fernando",
                        "apellido": "Torrico Peña",
                        "telefono": "70889900",
                        "colegiado": "COL-PSI-9340",
                        "biografia": "Neuropsicólogo clínico. Evaluaciones psicométricas y rehabilitación neurocognitiva.",
                        "modalidad": "VIRTUAL",
                        "tarifa": 220.00,
                        "especialidades": ["Neuropsicología y Rehabilitación"]
                    }
                ]

                psicologos_creados = []
                for p_data in psicologos_seed:
                    user, u_created = Usuario.objects.get_or_create(
                        email=p_data['email'],
                        defaults={
                            'nombre': p_data['nombre'],
                            'apellido': p_data['apellido'],
                            'telefono': p_data['telefono'],
                            'rol': rol_psico
                        }
                    )
                    if u_created:
                        user.set_password('Psicologo123*')
                        user.save()

                    psico, p_created = Psicologo.objects.get_or_create(
                        usuario=user,
                        defaults={
                            'numero_colegiado': p_data['colegiado'],
                            'biografia': p_data['biografia'],
                            'modalidad': p_data['modalidad'],
                            'tarifa_base': p_data['tarifa'],
                            'activo': True
                        }
                    )
                    esp_list: Any = p_data.get('especialidades', [])
                    for esp_nom in esp_list:
                        if esp_nom in especialidades_objs:
                            psico.especialidades.add(especialidades_objs[esp_nom])

                    # Configurar disponibilidad semanal estándar (Lunes a Viernes 08:00 - 12:00 y 14:00 - 18:00)
                    for dia in range(1, 6): # Lunes (1) a Viernes (5)
                        Disponibilidad.objects.get_or_create(
                            psicologo=psico,
                            dia_semana=dia,
                            hora_inicio=time(8, 0),
                            hora_fin=time(12, 0),
                            defaults={'duracion_bloque_min': 50, 'activo': True}
                        )
                        Disponibilidad.objects.get_or_create(
                            psicologo=psico,
                            dia_semana=dia,
                            hora_inicio=time(14, 0),
                            hora_fin=time(18, 0),
                            defaults={'duracion_bloque_min': 50, 'activo': True}
                        )

                    psicologos_creados.append(psico)
                self.stdout.write(f"  [OK] {len(psicologos_creados)} psicólogos y horarios creados.")

                # 5. Pacientes de Prueba (Adulto y Menor de edad con tutor)
                pacientes_seed = [
                    {
                        "email": "juan.perez@paciente.com",
                        "nombre": "Juan",
                        "apellido": "Pérez Morales",
                        "telefono": "76543210",
                        "expediente": "EXP-2026-001",
                        "ci": "8472910-LP",
                        "fecha_nac": date(1994, 5, 12),
                        "genero": "M",
                        "contacto_nombre": "Rosa Morales (Madre)",
                        "contacto_telf": "71234567",
                        "tutor_nombre": "",
                        "tutor_ci": ""
                    },
                    {
                        "email": "sofia.castro@paciente.com",
                        "nombre": "Sofía",
                        "apellido": "Castro Vega",
                        "telefono": "78901234",
                        "expediente": "EXP-2026-002",
                        "ci": "10928374-CB",
                        "fecha_nac": date(2001, 11, 23),
                        "genero": "F",
                        "contacto_nombre": "Carlos Castro (Hermano)",
                        "contacto_telf": "72345678",
                        "tutor_nombre": "",
                        "tutor_ci": ""
                    },
                    {
                        "email": "mateo.quispe@paciente.com",
                        "nombre": "Mateo",
                        "apellido": "Quispe Lima",
                        "telefono": "79012345",
                        "expediente": "EXP-2026-003",
                        "ci": "13459872-SC",
                        "fecha_nac": date(2014, 3, 15), # 12 años (Menor de edad)
                        "genero": "M",
                        "contacto_nombre": "Beatriz Lima (Madre y Tutora)",
                        "contacto_telf": "73456789",
                        "tutor_nombre": "Beatriz Lima Flores",
                        "tutor_ci": "4892301-SC"
                    }
                ]

                pacientes_creados = []
                for pac_data in pacientes_seed:
                    u_pac, u_created = Usuario.objects.get_or_create(
                        email=pac_data['email'],
                        defaults={
                            'nombre': pac_data['nombre'],
                            'apellido': pac_data['apellido'],
                            'telefono': pac_data['telefono'],
                            'rol': rol_paciente
                        }
                    )
                    if u_created:
                        u_pac.set_password('Paciente123*')
                        u_pac.save()

                    pac, _ = Paciente.objects.get_or_create(
                        usuario=u_pac,
                        defaults={
                            'codigo_expediente': pac_data['expediente'],
                            'ci': pac_data['ci'],
                            'fecha_nacimiento': pac_data['fecha_nac'],
                            'genero': pac_data['genero'],
                            'contacto_emergencia_nombre': pac_data['contacto_nombre'],
                            'contacto_emergencia_telf': pac_data['contacto_telf'],
                            'tutor_legal_nombre': pac_data['tutor_nombre'],
                            'tutor_legal_ci': pac_data['tutor_ci']
                        }
                    )
                    pacientes_creados.append(pac)
                self.stdout.write(f"  [OK] {len(pacientes_creados)} pacientes creados (incluye menor de edad validado).")

                # 6. Citas de Demostración y KPIs
                hoy = date.today()
                manana = hoy + timedelta(days=1)
                ayer = hoy - timedelta(days=1)
                hace_dos_dias = hoy - timedelta(days=2)

                psico_carlos = psicologos_creados[0]
                pac_juan = pacientes_creados[0]
                pac_sofia = pacientes_creados[1]

                # Cita de hoy (Presencial)
                Cita.objects.get_or_create(
                    paciente=pac_juan,
                    psicologo=psico_carlos,
                    fecha=hoy,
                    hora_inicio=time(9, 0),
                    hora_fin=time(9, 50),
                    defaults={
                        'modalidad': 'PRESENCIAL',
                        'estado': 'PROGRAMADA',
                        'motivo_consulta': 'Sesión regular de seguimiento TCC para ansiedad.',
                        'costo': psico_carlos.tarifa_base
                    }
                )

                # Cita de hoy (Virtual con Teleconsulta)
                cita_virtual, _ = Cita.objects.get_or_create(
                    paciente=pac_sofia,
                    psicologo=psico_carlos,
                    fecha=hoy,
                    hora_inicio=time(10, 0),
                    hora_fin=time(10, 50),
                    defaults={
                        'modalidad': 'VIRTUAL',
                        'estado': 'CONFIRMADA',
                        'motivo_consulta': 'Teleconsulta para evaluación del estado anímico.',
                        'costo': psico_carlos.tarifa_base
                    }
                )
                Teleconsulta.objects.get_or_create(
                    cita=cita_virtual,
                    defaults={'sala_id': f"sigepsi-{str(cita_virtual.id)[:8]}-demo"}
                )

                # Cita histórica realizada
                Cita.objects.get_or_create(
                    paciente=pac_juan,
                    psicologo=psico_carlos,
                    fecha=hace_dos_dias,
                    hora_inicio=time(8, 0),
                    hora_fin=time(8, 50),
                    defaults={
                        'modalidad': 'PRESENCIAL',
                        'estado': 'REALIZADA',
                        'motivo_consulta': 'Sesión diagnóstica inicial.',
                        'costo': psico_carlos.tarifa_base
                    }
                )

                self.stdout.write(self.style.SUCCESS("  [LISTO] Datos del Sprint 1 sembrados con éxito."))
