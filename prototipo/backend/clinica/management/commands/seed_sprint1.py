from typing import Any
from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from django_tenants.utils import schema_context, get_tenant_model
from accounts.models import Usuario, Rol, Permiso, RolPermiso
from clinica.models import Especialidad, Psicologo, Disponibilidad, Paciente
from agenda.models import Cita, Teleconsulta, Alerta


class Command(BaseCommand):
    help = "Siembra datos iniciales y de prueba del Sprint 1 (Especialidades, Psicólogos, Disponibilidad, Pacientes, Citas) y Sprint 2 (Casos de Uso CU14 a CU19 y HU-35)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            default='centro_esperanza',
            help='Slug o schema_name del tenant donde sembrar los datos (o "all" para sembrar en todos los tenants activos)'
        )
        parser.add_argument(
            '--skip-sprint2',
            action='store_true',
            help='Omitir la siembra automática de los casos de uso clínicos del Sprint 2'
        )

    def handle(self, *args, **options):
        tenant_target = options['tenant']
        skip_sprint2 = options['skip_sprint2']
        Tenant = get_tenant_model()

        if tenant_target == 'all':
            tenants = Tenant.objects.exclude(schema_name='public').filter(activo=True)
        else:
            try:
                t = Tenant.objects.get(schema_name=tenant_target)
            except Tenant.DoesNotExist:
                try:
                    t = Tenant.objects.get(slug=tenant_target)
                except Tenant.DoesNotExist:
                    self.stderr.write(f"Tenant '{tenant_target}' no encontrado.")
                    return
            tenants = [t]

        for tenant in tenants:
            self.stdout.write(self.style.NOTICE(f"\n========================================================"))
            self.stdout.write(self.style.NOTICE(f"==> Sembrando datos del Sprint 1 en esquema: {tenant.schema_name}"))
            self.stdout.write(self.style.NOTICE(f"========================================================"))
            self.seed_tenant_sprint1(tenant)

            if not skip_sprint2:
                self.stdout.write(self.style.NOTICE(f"\n==> Conectando automáticamente con la siembra del Sprint 2 para {tenant.schema_name}..."))
                call_command('seed_sprint2', tenant=tenant.schema_name)

        self.stdout.write(self.style.SUCCESS("\n==> [FINALIZADO] Siembra integral de datos completada con exito. <==\n"))

    def seed_tenant_sprint1(self, tenant):
        with schema_context(tenant.schema_name):
            atomic_tx: Any = transaction.atomic()
            with atomic_tx:
                # 0. Roles y Permisos del Sistema en el Tenant
                from accounts.utils import seed_tenant_roles_and_permissions
                from core.models import Centro

                roles_map = seed_tenant_roles_and_permissions()
                rol_admin = roles_map[Rol.ADMIN_CENTRO]
                rol_coord = roles_map[Rol.COORDINADOR]
                rol_psico = roles_map[Rol.PSICOLOGO]
                rol_recep = roles_map[Rol.RECEPCIONISTA]
                rol_paciente = roles_map[Rol.PACIENTE]

                # Reparar cualquier usuario previo sin rol
                for u in Usuario.objects.filter(rol__isnull=True):
                    email_low = u.email.lower()
                    if 'admin' in email_low or u.is_superuser or u.is_staff:
                        u.rol = rol_admin
                    elif 'coord' in email_low:
                        u.rol = rol_coord
                    elif 'recep' in email_low:
                        u.rol = rol_recep
                    elif Psicologo.objects.filter(usuario=u).exists() or 'psic' in email_low or any(k in email_low for k in ['mendoza', 'vargas', 'torrico', 'montes', 'rios']):
                        u.rol = rol_psico
                    else:
                        u.rol = rol_paciente
                    u.save(update_fields=['rol'])

                # Asegurar Configuración del Centro
                Centro.objects.get_or_create(
                    defaults={
                        "nombre": tenant.nombre,
                        "direccion": tenant.direccion or "Av. Las Américas #450, Santa Cruz",
                        "telefono": tenant.telefono or "+591 3 3456789",
                        "email": tenant.email_contacto or f"contacto@{tenant.slug}.com",
                        "horarios_atencion": {
                            "lunes_viernes": "08:00 - 19:00",
                            "sabado": "08:00 - 14:00"
                        },
                        "configuracion": {
                            "cancelacion_horas_anticipacion": 24,
                            "duracion_sesion_minutos": 50,
                            "modalidad_predeterminada": "Mixta (Presencial / Virtual)"
                        }
                    }
                )

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
                    RolPermiso.objects.get_or_create(rol=rol_admin, permiso=p)
                    if 'cita' in cod or 'teleconsulta' in cod or 'psicologo' in cod or 'especialidad' in cod or 'paciente' in cod or 'dashboard' in cod or 'alerta' in cod:
                        RolPermiso.objects.get_or_create(rol=rol_psico, permiso=p)
                    if 'cita' in cod or 'paciente' in cod or 'view' in cod:
                        RolPermiso.objects.get_or_create(rol=rol_recep, permiso=p)
                    if 'dashboard' in cod or 'alerta' in cod or 'cita' in cod or 'view' in cod:
                        RolPermiso.objects.get_or_create(rol=rol_coord, permiso=p)

                # Asegurar Personal Demo Institucional
                domain_clean = tenant.slug.replace('_', '')
                usuarios_demo = [
                    (f"admin@{domain_clean}.com", "Admin1234*", "Admin", f"{tenant.nombre}", rol_admin, "+591 70011111"),
                    (f"psicologo@{domain_clean}.com", "Psico1234*", "Lic. Carlos", "Mendoza", rol_psico, "+591 70022222"),
                    (f"recepcion@{domain_clean}.com", "Recep1234*", "María", "González", rol_recep, "+591 70033333"),
                    (f"coordinador@{domain_clean}.com", "Coord1234*", "Dr. Roberto", "Paz", rol_coord, "+591 70044444"),
                ]

                if tenant.slug == 'centro_esperanza':
                    usuarios_demo.append(
                        ("beto.caleb.delgado.rojas@gmail.com", "Admin1234*", "Alberto", "Delgado", rol_admin, "+591 70000000")
                    )

                for email, pwd, nom, ape, r_obj, tel in usuarios_demo:
                    u = Usuario.objects.filter(email=email).first()
                    if not u:
                        Usuario.objects.create_user(
                            email=email, password=pwd, nombre=nom, apellido=ape,
                            telefono=tel, rol=r_obj, activo=True
                        )
                    else:
                        u.nombre = nom
                        u.apellido = ape
                        u.rol = r_obj
                        u.activo = True
                        u.set_password(pwd)
                        u.save()

                # 2. Catálogo de Especialidades Clínicas (8 especialidades)
                especialidades_data = [
                    ("Terapia Cognitivo-Conductual (TCC)", "Reestructuración cognitiva y abordaje de esquemas desadaptativos y ansiedad."),
                    ("Psicología Clínica y de la Salud", "Evaluación, diagnóstico y tratamiento de trastornos emocionales y del estado de ánimo."),
                    ("Terapia Familiar y Sistémica", "Intervención sistémica orientada a la resolución de conflictos vinculares y de pareja."),
                    ("Neuropsicología y Rehabilitación", "Evaluación de funciones cognitivas, memoria, atención y estimulación neurocognitiva."),
                    ("Psicología Infantil y del Desarrollo", "Abordaje de trastornos del neurodesarrollo, conducta y apego en infancia y adolescencia."),
                    ("Terapia de Aceptación y Compromiso (ACT)", "Intervenciones contextuales de tercera generación para flexibilidad psicológica."),
                    ("Psicooncología y Cuidados Paliativos", "Acompañamiento psicológico en enfermedades crónicas, duelo y trauma vital."),
                    ("Adicciones y Conductas Compulsivas", "Prevención de recaídas y modificación conductual en dependencias.")
                ]

                especialidades_objs = {}
                for nom, desc in especialidades_data:
                    esp, _ = Especialidad.objects.get_or_create(nombre=nom, defaults={'descripcion': desc})
                    especialidades_objs[nom] = esp
                self.stdout.write(f"  [OK] {len(especialidades_objs)} especialidades clínicas aseguradas.")

                # 4. Psicólogos de Prueba (5 profesionales de distintas áreas)
                domain_clean = tenant.slug.replace('_', '')
                psicologos_seed = [
                    {
                        "email": f"carlos.mendoza@{domain_clean}.com",
                        "nombre": "Carlos",
                        "apellido": "Mendoza Rojas",
                        "telefono": "70112233",
                        "colegiado": "COL-PSI-4589",
                        "biografia": "Psicólogo clínico con 10 años de experiencia en TCC y manejo de trastornos de ansiedad y pánico.",
                        "modalidad": "MIXTA",
                        "tarifa": 180.00,
                        "especialidades": ["Terapia Cognitivo-Conductual (TCC)", "Psicología Clínica y de la Salud"]
                    },
                    {
                        "email": f"mariana.vargas@{domain_clean}.com",
                        "nombre": "Mariana",
                        "apellido": "Vargas Arce",
                        "telefono": "70445566",
                        "colegiado": "COL-PSI-7821",
                        "biografia": "Especialista en terapia sistémica familiar y psicología infantil. Magíster en Terapia Vincular.",
                        "modalidad": "MIXTA",
                        "tarifa": 200.00,
                        "especialidades": ["Terapia Familiar y Sistémica", "Psicología Infantil y del Desarrollo"]
                    },
                    {
                        "email": f"fernando.torrico@{domain_clean}.com",
                        "nombre": "Fernando",
                        "apellido": "Torrico Peña",
                        "telefono": "70889900",
                        "colegiado": "COL-PSI-9340",
                        "biografia": "Neuropsicólogo clínico. Evaluaciones psicométricas integrales WISC/WAIS y rehabilitación cognitiva.",
                        "modalidad": "VIRTUAL",
                        "tarifa": 220.00,
                        "especialidades": ["Neuropsicología y Rehabilitación"]
                    },
                    {
                        "email": f"gabriel.montes@{domain_clean}.com",
                        "nombre": "Gabriel",
                        "apellido": "Montes Claros",
                        "telefono": "70223344",
                        "colegiado": "COL-SP2-9988",
                        "biografia": "Especialista en terapias contextuales de tercera generación (ACT, Mindfulness) y prevención de crisis.",
                        "modalidad": "MIXTA",
                        "tarifa": 190.00,
                        "especialidades": ["Terapia de Aceptación y Compromiso (ACT)", "Terapia Cognitivo-Conductual (TCC)"]
                    },
                    {
                        "email": f"lucia.rios@{domain_clean}.com",
                        "nombre": "Lucía",
                        "apellido": "Ríos Sotomayor",
                        "telefono": "70334455",
                        "colegiado": "COL-PSI-3120",
                        "biografia": "Especialista en trauma complejo, duelo patológico y psicooncología. Certificación internacional en EMDR.",
                        "modalidad": "PRESENCIAL",
                        "tarifa": 210.00,
                        "especialidades": ["Psicooncología y Cuidados Paliativos", "Psicología Clínica y de la Salud"]
                    }
                ]

                psicologos_creados = []
                for p_data in psicologos_seed:
                    psico = Psicologo.objects.filter(numero_colegiado=p_data['colegiado']).first()
                    user = Usuario.objects.filter(email=p_data['email']).first()
                    if not user:
                        if psico and psico.usuario:
                            user = psico.usuario
                            user.email = p_data['email']
                            user.nombre = p_data['nombre']
                            user.apellido = p_data['apellido']
                            user.telefono = p_data['telefono']
                            user.rol = rol_psico
                            user.activo = True
                            user.set_password('Psicologo123*')
                            user.save()
                        else:
                            user = Usuario.objects.create_user(
                                email=p_data['email'],
                                password='Psicologo123*',
                                nombre=p_data['nombre'],
                                apellido=p_data['apellido'],
                                telefono=p_data['telefono'],
                                rol=rol_psico,
                                activo=True
                            )
                    else:
                        user.nombre = p_data['nombre']
                        user.apellido = p_data['apellido']
                        user.telefono = p_data['telefono']
                        user.rol = rol_psico
                        user.activo = True
                        user.set_password('Psicologo123*')
                        user.save()

                    if not psico:
                        psico = Psicologo.objects.filter(usuario=user).first()

                    if not psico:
                        psico = Psicologo.objects.create(
                            usuario=user,
                            numero_colegiado=p_data['colegiado'],
                            biografia=p_data['biografia'],
                            modalidad=p_data['modalidad'],
                            tarifa_base=p_data['tarifa'],
                            activo=True
                        )
                    else:
                        psico.usuario = user
                        psico.numero_colegiado = p_data['colegiado']
                        psico.biografia = p_data['biografia']
                        psico.modalidad = p_data['modalidad']
                        psico.tarifa_base = p_data['tarifa']
                        psico.activo = True
                        psico.save()

                    esp_list: Any = p_data.get('especialidades', [])
                    for esp_nom in esp_list:
                        if esp_nom in especialidades_objs:
                            psico.especialidades.add(especialidades_objs[esp_nom])

                    # Disponibilidad semanal (L-V 08:00 - 12:00 y 14:00 - 18:00)
                    for dia in range(1, 6):
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
                self.stdout.write(f"  [OK] {len(psicologos_creados)} psicólogos colegiados con horarios semanales completos.")

                # 5. Pacientes de Prueba (7 perfiles variados)
                pac_juan_email = "juan.perez@paciente.com" if tenant.slug == 'centro_esperanza' else f"juan.perez@{domain_clean}.com"
                pac_sofia_email = "sofia.castro@paciente.com" if tenant.slug == 'centro_esperanza' else f"sofia.castro@{domain_clean}.com"

                pac_mateo_email = "mateo.quispe@paciente.com" if tenant.slug == 'centro_esperanza' else f"mateo.quispe@{domain_clean}.com"

                pacientes_seed = [
                    {
                        "email": pac_juan_email,
                        "nombre": "Juan",
                        "apellido": "Pérez Morales",
                        "telefono": "76543210",
                        "expediente": f"EXP-{tenant.slug.upper()[:4]}-001",
                        "ci": "8472910-LP",
                        "fecha_nac": date(1994, 5, 12),
                        "genero": "M",
                        "contacto_nombre": "Rosa Morales (Madre)",
                        "contacto_telf": "71234567",
                        "tutor_nombre": "",
                        "tutor_ci": ""
                    },
                    {
                        "email": pac_sofia_email,
                        "nombre": "Sofía",
                        "apellido": "Castro Vega",
                        "telefono": "78901234",
                        "expediente": f"EXP-{tenant.slug.upper()[:4]}-002",
                        "ci": "10928374-CB",
                        "fecha_nac": date(2001, 11, 23),
                        "genero": "F",
                        "contacto_nombre": "Carlos Castro (Hermano)",
                        "contacto_telf": "72345678",
                        "tutor_nombre": "",
                        "tutor_ci": ""
                    },
                    {
                        "email": pac_mateo_email,
                        "nombre": "Mateo",
                        "apellido": "Quispe Lima",
                        "telefono": "79012345",
                        "expediente": f"EXP-{tenant.slug.upper()[:4]}-003",
                        "ci": "13459872-SC",
                        "fecha_nac": date(2014, 3, 15), # 12 años (Menor de edad)
                        "genero": "M",
                        "contacto_nombre": "Beatriz Lima (Madre y Tutora)",
                        "contacto_telf": "73456789",
                        "tutor_nombre": "Beatriz Lima Flores",
                        "tutor_ci": "4892301-SC"
                    },
                    {
                        "email": f"elena.valverde@{domain_clean}.com",
                        "nombre": "Elena",
                        "apellido": "Valverde Méndez",
                        "telefono": "77112288",
                        "expediente": f"EXP-{tenant.slug.upper()[:4]}-004",
                        "ci": "7382914-TJ",
                        "fecha_nac": date(1988, 9, 4),
                        "genero": "F",
                        "contacto_nombre": "Marcos Valverde (Esposo)",
                        "contacto_telf": "71889900",
                        "tutor_nombre": "",
                        "tutor_ci": ""
                    },
                    {
                        "email": f"diego.alarcon@{domain_clean}.com",
                        "nombre": "Diego",
                        "apellido": "Alarcón Siles",
                        "telefono": "78129034",
                        "expediente": f"EXP-{tenant.slug.upper()[:4]}-005",
                        "ci": "9182736-OR",
                        "fecha_nac": date(1981, 4, 18),
                        "genero": "M",
                        "contacto_nombre": "Patricia Siles (Hermana)",
                        "contacto_telf": "72110033",
                        "tutor_nombre": "",
                        "tutor_ci": ""
                    },
                    {
                        "email": f"valentina.ramos@{domain_clean}.com",
                        "nombre": "Valentina",
                        "apellido": "Ramos Justiniano",
                        "telefono": "79901122",
                        "expediente": f"EXP-{tenant.slug.upper()[:4]}-006",
                        "ci": "12345678-SC",
                        "fecha_nac": date(1997, 12, 10),
                        "genero": "F",
                        "contacto_nombre": "Jorge Ramos (Padre)",
                        "contacto_telf": "73004455",
                        "tutor_nombre": "",
                        "tutor_ci": ""
                    },
                    {
                        "email": f"rodrigo.guzman@{domain_clean}.com",
                        "nombre": "Rodrigo",
                        "apellido": "Guzmán Camacho",
                        "telefono": "76655443",
                        "expediente": f"EXP-{tenant.slug.upper()[:4]}-007",
                        "ci": "6574839-BN",
                        "fecha_nac": date(2007, 2, 8),
                        "genero": "M",
                        "contacto_nombre": "Silvia Camacho (Madre)",
                        "contacto_telf": "71992233",
                        "tutor_nombre": "",
                        "tutor_ci": ""
                    }
                ]

                pacientes_creados = []
                for pac_data in pacientes_seed:
                    pac = Paciente.objects.filter(ci=pac_data['ci']).first() or Paciente.objects.filter(codigo_expediente=pac_data['expediente']).first()
                    u_pac = Usuario.objects.filter(email=pac_data['email']).first()
                    if not u_pac:
                        if pac and pac.usuario:
                            u_pac = pac.usuario
                            u_pac.email = pac_data['email']
                            u_pac.nombre = pac_data['nombre']
                            u_pac.apellido = pac_data['apellido']
                            u_pac.telefono = pac_data['telefono']
                            u_pac.rol = rol_paciente
                            u_pac.activo = True
                            u_pac.set_password('Paciente123*')
                            u_pac.save()
                        else:
                            u_pac = Usuario.objects.create_user(
                                email=pac_data['email'],
                                password='Paciente123*',
                                nombre=pac_data['nombre'],
                                apellido=pac_data['apellido'],
                                telefono=pac_data['telefono'],
                                rol=rol_paciente,
                                activo=True
                            )
                    else:
                        u_pac.nombre = pac_data['nombre']
                        u_pac.apellido = pac_data['apellido']
                        u_pac.telefono = pac_data['telefono']
                        u_pac.rol = rol_paciente
                        u_pac.activo = True
                        u_pac.set_password('Paciente123*')
                        u_pac.save()

                    if not pac:
                        pac = Paciente.objects.filter(usuario=u_pac).first()

                    if not pac:
                        pac = Paciente.objects.create(
                            usuario=u_pac,
                            codigo_expediente=pac_data['expediente'],
                            ci=pac_data['ci'],
                            fecha_nacimiento=pac_data['fecha_nac'],
                            genero=pac_data['genero'],
                            contacto_emergencia_nombre=pac_data['contacto_nombre'],
                            contacto_emergencia_telf=pac_data['contacto_telf'],
                            tutor_legal_nombre=pac_data['tutor_nombre'],
                            tutor_legal_ci=pac_data['tutor_ci']
                        )
                    else:
                        pac.usuario = u_pac
                        pac.codigo_expediente = pac_data['expediente']
                        pac.ci = pac_data['ci']
                        pac.fecha_nacimiento = pac_data['fecha_nac']
                        pac.genero = pac_data['genero']
                        pac.contacto_emergencia_nombre = pac_data['contacto_nombre']
                        pac.contacto_emergencia_telf = pac_data['contacto_telf']
                        pac.tutor_legal_nombre = pac_data['tutor_nombre']
                        pac.tutor_legal_ci = pac_data['tutor_ci']
                        pac.save()

                    pacientes_creados.append(pac)
                self.stdout.write(f"  [OK] {len(pacientes_creados)} pacientes registrados (adultos y menores con tutor legal acreditado).")

                if tenant.slug == 'centro_esperanza':
                    aliases = [
                        ("juan.perez@centroesperanza.com", "Juan", "Pérez Morales"),
                        ("sofia.castro@centroesperanza.com", "Sofía", "Castro Vega"),
                        ("mateo.quispe@centroesperanza.com", "Mateo", "Quispe Lima"),
                    ]
                    for a_email, a_nom, a_ape in aliases:
                        u_alias = Usuario.objects.filter(email=a_email).first()
                        if not u_alias:
                            Usuario.objects.create_user(
                                email=a_email, password="Paciente123*",
                                nombre=a_nom, apellido=a_ape,
                                rol=rol_paciente, activo=True
                            )
                        else:
                            u_alias.rol = rol_paciente
                            u_alias.set_password("Paciente123*")
                            u_alias.save()

                # 6. Citas Operativas Distribuidas
                hoy = date.today()
                manana = hoy + timedelta(days=1)
                ayer = hoy - timedelta(days=1)
                hace_siete_dias = hoy - timedelta(days=7)
                hace_catorce_dias = hoy - timedelta(days=14)

                psico_carlos = psicologos_creados[0]
                psico_mariana = psicologos_creados[1]
                psico_gabriel = psicologos_creados[3]

                pac_juan = pacientes_creados[0]
                pac_sofia = pacientes_creados[1]
                pac_mateo = pacientes_creados[2]
                pac_elena = pacientes_creados[3]
                pac_rodrigo = pacientes_creados[6]

                # Citas históricas realizadas
                Cita.objects.get_or_create(
                    paciente=pac_juan,
                    psicologo=psico_carlos,
                    fecha=hace_catorce_dias,
                    hora_inicio=time(9, 0),
                    hora_fin=time(9, 50),
                    defaults={
                        'modalidad': 'PRESENCIAL',
                        'estado': 'REALIZADA',
                        'motivo_consulta': 'Sesión 1 de Evaluación Diagnóstica y encuadre psicoterapéutico.',
                        'costo': psico_carlos.tarifa_base
                    }
                )

                Cita.objects.get_or_create(
                    paciente=pac_juan,
                    psicologo=psico_carlos,
                    fecha=hace_siete_dias,
                    hora_inicio=time(9, 0),
                    hora_fin=time(9, 50),
                    defaults={
                        'modalidad': 'PRESENCIAL',
                        'estado': 'REALIZADA',
                        'motivo_consulta': 'Sesión 2: Psicoeducación sobre el pánico y técnica diafragmática.',
                        'costo': psico_carlos.tarifa_base
                    }
                )

                # Cita de HOY (Presencial - En curso / Programada)
                Cita.objects.get_or_create(
                    paciente=pac_juan,
                    psicologo=psico_carlos,
                    fecha=hoy,
                    hora_inicio=time(9, 0),
                    hora_fin=time(9, 50),
                    defaults={
                        'modalidad': 'PRESENCIAL',
                        'estado': 'PROGRAMADA',
                        'motivo_consulta': 'Sesión 3: Reestructuración de interpretaciones catastróficas.',
                        'costo': psico_carlos.tarifa_base
                    }
                )

                # Cita de HOY (Virtual con Teleconsulta)
                cita_virtual, _ = Cita.objects.get_or_create(
                    paciente=pac_sofia,
                    psicologo=psico_carlos,
                    fecha=hoy,
                    hora_inicio=time(11, 0),
                    hora_fin=time(11, 50),
                    defaults={
                        'modalidad': 'VIRTUAL',
                        'estado': 'CONFIRMADA',
                        'motivo_consulta': 'Teleconsulta para seguimiento anímico y activación conductual.',
                        'costo': psico_carlos.tarifa_base
                    }
                )
                Teleconsulta.objects.get_or_create(
                    cita=cita_virtual,
                    defaults={'sala_id': f"sigepsi-teleconsulta-{str(cita_virtual.id)[:8]}"}
                )

                # Cita de MAÑANA (<24 horas) - Rodrigo Guzmán (Con Formulario PENDIENTE para CP-23-02)
                Cita.objects.get_or_create(
                    paciente=pac_rodrigo,
                    psicologo=psico_gabriel,
                    fecha=manana,
                    hora_inicio=time(15, 0),
                    hora_fin=time(15, 50),
                    defaults={
                        'modalidad': 'PRESENCIAL',
                        'estado': 'PROGRAMADA',
                        'motivo_consulta': 'Primera consulta por crisis vocacional y sintomatología ansiosa leve.',
                        'costo': psico_gabriel.tarifa_base
                    }
                )

                # Cita Cancelada con motivo justificado
                Cita.objects.get_or_create(
                    paciente=pac_elena,
                    psicologo=psico_carlos,
                    fecha=ayer,
                    hora_inicio=time(16, 0),
                    hora_fin=time(16, 50),
                    defaults={
                        'modalidad': 'PRESENCIAL',
                        'estado': 'CANCELADA',
                        'motivo_consulta': 'Sesión de seguimiento.',
                        'motivo_cancelacion': 'Inconveniente laboral imprevisto notificado con antelación.',
                        'costo': psico_carlos.tarifa_base
                    }
                )

                # 7. Alertas Operativas en el Dashboard Clínico
                Alerta.objects.get_or_create(
                    paciente=pac_juan,
                    tipo='URGENCIA_CLINICA',
                    defaults={
                        'severidad': 'ALTA',
                        'descripcion': 'Paciente reportó malestar nivel 4/5 en preconsulta por crisis de angustia reiteradas.',
                        'resuelta': True,
                        'nota_resolucion': 'Se coordinó interconsulta con psiquiatría y se entrenó en técnica de desactivación respiratoria.'
                    }
                )
                Alerta.objects.get_or_create(
                    paciente=pac_rodrigo,
                    tipo='URGENCIA_CLINICA',
                    defaults={
                        'severidad': 'MEDIA',
                        'descripcion': 'Cita en menos de 24 horas sin cuestionario de preconsulta diligenciado (Formulario Pendiente).',
                        'resuelta': False
                    }
                )

                self.stdout.write(self.style.SUCCESS(f"  [OK] Citas operativas (hoy, pasadas, teleconsulta, manana, canceladas) y alertas clinicas sembradas."))
