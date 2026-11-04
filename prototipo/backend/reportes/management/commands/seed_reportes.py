# ==============================================================================
# MÓDULO: reportes/management/commands/seed_reportes.py
# DESCRIPCIÓN: Comando de siembra masiva de datos analíticos para el Módulo de
#              Reportes y Exportaciones (CU25, QBE, Inteligencia de Negocio).
#              Genera histórico temporal completo (Enero a Diciembre 2026) en
#              todas las 8 fuentes de datos: Citas, Ingresos, Pacientes,
#              Psicólogos, Alertas Clínicas, Teleconsultas, Usuarios y Bitácora.
# ==============================================================================
import uuid
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django_tenants.utils import schema_context, get_tenant_model, get_public_schema_name

from accounts.models import Usuario, Rol
from clinica.models import Especialidad, Psicologo, Paciente
from agenda.models import Cita, Teleconsulta, Alerta
from audit.services import write_event


# Catálogo extendido de pacientes para dar volumen analítico
PACIENTES_EXTENDIDOS = [
    {"email_user": "camila.vargas", "nombre": "Camila", "apellido": "Vargas Céspedes", "ci": "8374921-SC", "genero": "F", "fecha_nac": date(1995, 3, 14), "tel": "77123450", "contacto": "Mario Vargas (Padre)", "contacto_tel": "71029384", "mes_reg": 1},
    {"email_user": "javier.montano", "nombre": "Javier", "apellido": "Montaño Torrico", "ci": "5928371-CB", "genero": "M", "fecha_nac": date(1989, 7, 22), "tel": "77234561", "contacto": "Lorena Torrico (Esposa)", "contacto_tel": "71130495", "mes_reg": 2},
    {"email_user": "luciana.paz", "nombre": "Luciana", "apellido": "Paz Barrientos", "ci": "9482710-LP", "genero": "F", "fecha_nac": date(2001, 11, 5), "tel": "77345672", "contacto": "Clara Barrientos (Madre)", "contacto_tel": "71241506", "mes_reg": 2},
    {"email_user": "esteban.soliz", "nombre": "Esteban", "apellido": "Soliz Quiroga", "ci": "6291847-OR", "genero": "M", "fecha_nac": date(1984, 5, 30), "tel": "77456783", "contacto": "Ramiro Soliz (Hermano)", "contacto_tel": "71352617", "mes_reg": 3},
    {"email_user": "mariana.choque", "nombre": "Mariana", "apellido": "Choque Mamani", "ci": "7483920-PT", "genero": "F", "fecha_nac": date(1998, 9, 17), "tel": "77567894", "contacto": "Elena Mamani (Madre)", "contacto_tel": "71463728", "mes_reg": 3},
    {"email_user": "andres.rojas", "nombre": "Andrés", "apellido": "Rojas Melgar", "ci": "8192034-BN", "genero": "M", "fecha_nac": date(1992, 1, 12), "tel": "77678905", "contacto": "Carla Melgar (Hermana)", "contacto_tel": "71574839", "mes_reg": 4},
    {"email_user": "valeria.aguilar", "nombre": "Valeria", "apellido": "Aguilar Hurtado", "ci": "9028374-SC", "genero": "F", "fecha_nac": date(1987, 8, 25), "tel": "77789016", "contacto": "Gonzalo Hurtado (Esposo)", "contacto_tel": "71685940", "mes_reg": 5},
    {"email_user": "gabriel.tellez", "nombre": "Gabriel", "apellido": "Téllez Suarez", "ci": "6748291-TJ", "genero": "M", "fecha_nac": date(2003, 10, 8), "tel": "77890127", "contacto": "Teresa Suarez (Madre)", "contacto_tel": "71796051", "mes_reg": 6},
    {"email_user": "paola.valencia", "nombre": "Paola", "apellido": "Valencia Mercado", "ci": "7384910-CH", "genero": "F", "fecha_nac": date(1996, 4, 3), "tel": "77901238", "contacto": "Raúl Valencia (Padre)", "contacto_tel": "71807162", "mes_reg": 7},
    {"email_user": "nicolas.castedo", "nombre": "Nicolás", "apellido": "Castedo Pinto", "ci": "8593021-PA", "genero": "M", "fecha_nac": date(1978, 12, 19), "tel": "77012349", "contacto": "Silvia Pinto (Esposa)", "contacto_tel": "71918273", "mes_reg": 8},
    {"email_user": "daniela.flores", "nombre": "Daniela", "apellido": "Flores Justiniano", "ci": "9182045-SC", "genero": "F", "fecha_nac": date(2000, 6, 15), "tel": "77134560", "contacto": "Patricia Justiniano (Tía)", "contacto_tel": "71039485", "mes_reg": 9},
    {"email_user": "matias.balderrama", "nombre": "Matías", "apellido": "Balderrama Cuellar", "ci": "6473829-CB", "genero": "M", "fecha_nac": date(2012, 2, 28), "tel": "77245671", "contacto": "Claudia Cuellar (Madre/Tutora)", "contacto_tel": "71140596", "tutor": "Claudia Cuellar", "tutor_ci": "4839201-CB", "mes_reg": 9},
]

MOTIVOS_CONSULTA = [
    "Evaluación diagnóstica inicial por sintomatología ansiosa persistente",
    "Psicoeducación y reestructuración cognitiva para manejo de estrés laboral agudo",
    "Tratamiento psicoterapéutico de episodio depresivo moderado",
    "Terapia focalizada en duelo por pérdida significativa reciente",
    "Entrenamiento en habilidades de autorregulación emocional y tolerancia al malestar",
    "Intervención cognitivo-conductual en fobia social y evitación",
    "Terapia de pareja: comunicación asertiva y resolución constructiva de conflictos",
    "Terapia infanto-juvenil: problemas de conducta y adaptación escolar",
    "Seguimiento farmacopsicoterapéutico coordinado y prevención de recaídas",
    "Sesión de cierre de tratamiento y balance de metas clínicas alcanzadas",
    "Revisión de plan terapéutico inter-sesiones y autorregistro de pensamientos automáticos",
    "Manejo de crisis de pánico y técnicas de respiración diafragmática"
]

MOTIVOS_CANCELACION = [
    "Cruce de horarios imprevisto por compromisos laborales",
    "Problemas de salud agudos (cuadro gripal / gastroenteritis)",
    "Viaje de trabajo no programado fuera de la ciudad",
    "Solicitó reprogramación de fecha con más de 24 horas de anticipación",
    "Falta de disponibilidad de transporte particular o público",
    "Emergencia familiar de fuerza mayor justificada"
]


class Command(BaseCommand):
    help = "Siembra un historial analítico exhaustivo y completo (Enero a Diciembre 2026) para que todos los reportes muestren datos reales en todos los tenants."

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            default='all',
            help='Slug o schema_name del tenant (o "all" para sembrar en todos los tenants activos)'
        )

    def handle(self, *args, **options):
        tenant_arg = options['tenant']
        Tenant = get_tenant_model()

        if tenant_arg == 'all':
            tenants = list(Tenant.objects.exclude(schema_name='public').filter(activo=True).order_by('schema_name'))
            # También incluimos public para cuando SuperAdmin consulta sin tenant
            public_t = Tenant.objects.filter(schema_name=get_public_schema_name()).first()
            if public_t:
                tenants.append(public_t)
        else:
            try:
                t = Tenant.objects.get(schema_name=tenant_arg)
            except Tenant.DoesNotExist:
                try:
                    t = Tenant.objects.get(slug=tenant_arg)
                except Tenant.DoesNotExist:
                    self.stderr.write(f"Tenant '{tenant_arg}' no encontrado.")
                    return
            tenants = [t]

        self.stdout.write(self.style.NOTICE("======================================================================"))
        self.stdout.write(self.style.NOTICE(f"==> INICIANDO SIEMBRA ANALITICA PARA REPORTES EN {len(tenants)} ESQUEMA(S)"))
        self.stdout.write(self.style.NOTICE("======================================================================"))

        for tenant in tenants:
            self.stdout.write(self.style.NOTICE(f"\n--> Generando datos analiticos en esquema: '{tenant.schema_name}' ({tenant.nombre})..."))
            self.seed_tenant_reportes(tenant)

        self.stdout.write(self.style.SUCCESS("\n======================================================================"))
        self.stdout.write(self.style.SUCCESS("[EXITO] ¡SIEMBRA DE REPORTES COMPLETADA CON EXITO EN TODOS LOS TENANTS!"))
        self.stdout.write(self.style.SUCCESS("======================================================================\n"))

    def seed_tenant_reportes(self, tenant):
        with schema_context(tenant.schema_name):
            with transaction.atomic():
                # 1. Asegurar roles
                rol_paciente = Rol.objects.filter(nombre=Rol.PACIENTE).first()
                if not rol_paciente:
                    from accounts.utils import seed_tenant_roles_and_permissions
                    roles_map = seed_tenant_roles_and_permissions()
                    rol_paciente = roles_map.get(Rol.PACIENTE)

                clean_slug = tenant.slug.replace('_', '')

                # 2. Asegurar Psicólogos (usar existentes o crear de respaldo)
                psicologos = list(Psicologo.objects.select_related('usuario').all())
                if not psicologos:
                    # Crear al menos 3 psicólogos si no hubiera
                    from clinica.management.commands.seed_sprint1 import Command as SeedSprint1Cmd
                    s1 = SeedSprint1Cmd()
                    s1.seed_tenant_sprint1(tenant)
                    psicologos = list(Psicologo.objects.select_related('usuario').all())

                if not psicologos:
                    self.stderr.write(f"  [AVISO] No se encontraron psicólogos en {tenant.schema_name}. Omitiendo citas.")
                    return

                # 3. Crear o asegurar Pacientes Extendidos
                pacientes_activos = list(Paciente.objects.select_related('usuario').all())
                nuevos_pacs_count = 0

                for idx, p_info in enumerate(PACIENTES_EXTENDIDOS, start=10):
                    email = f"{p_info['email_user']}@{clean_slug}.com"
                    exp = f"EXP-{clean_slug.upper()[:4]}-{idx:03d}"
                    u = Usuario.objects.filter(email=email).first()
                    if not u:
                        u = Usuario.objects.create_user(
                            email=email,
                            password="Paciente123*",
                            nombre=p_info["nombre"],
                            apellido=p_info["apellido"],
                            telefono=p_info["tel"],
                            rol=rol_paciente,
                            activo=True
                        )
                    pac = Paciente.objects.filter(codigo_expediente=exp).first() or Paciente.objects.filter(ci=p_info["ci"]).first()
                    if not pac:
                        fecha_reg = date(2026, p_info["mes_reg"], min(15 + (idx % 10), 28))
                        pac = Paciente.objects.create(
                            usuario=u,
                            codigo_expediente=exp,
                            ci=p_info["ci"],
                            fecha_nacimiento=p_info["fecha_nac"],
                            genero=p_info["genero"],
                            contacto_emergencia_nombre=p_info["contacto"],
                            contacto_emergencia_telf=p_info["contacto_tel"],
                            tutor_legal_nombre=p_info.get("tutor", ""),
                            tutor_legal_ci=p_info.get("tutor_ci", "")
                        )
                        pacientes_activos.append(pac)
                        nuevos_pacs_count += 1
                    elif pac not in pacientes_activos:
                        pacientes_activos.append(pac)

                self.stdout.write(f"  [OK] Pacientes asegurados: {len(pacientes_activos)} (creados nuevos: {nuevos_pacs_count})")

                # 4. Generar Matriz Histórica de Citas (Enero 2026 a Diciembre 2026)
                # Generamos ~60-80 citas por tenant con distribución mensual consistente
                citas_creadas = 0
                teleconsultas_creadas = 0
                estados_dist = [
                    ('REALIZADA', 0.65),
                    ('PROGRAMADA', 0.12),
                    ('CONFIRMADA', 0.08),
                    ('CANCELADA', 0.10),
                    ('INASISTENCIA', 0.05),
                ]

                # Meses del año 2026 a sembrar
                # Enero a Noviembre (históricos y actuales) + Diciembre (futuros programados)
                hoy = date.today()
                meses_config = [
                    (1, 31, 6),   # Enero: 6 citas
                    (2, 28, 6),   # Febrero: 6 citas
                    (3, 31, 7),   # Marzo: 7 citas
                    (4, 30, 7),   # Abril: 7 citas
                    (5, 31, 8),   # Mayo: 8 citas
                    (6, 30, 8),   # Junio: 8 citas
                    (7, 31, 8),   # Julio: 8 citas
                    (8, 31, 8),   # Agosto: 8 citas
                    (9, 30, 8),   # Septiembre: 8 citas
                    (10, 31, 10), # Octubre: 10 citas
                    (11, 28, 8),  # Noviembre: 8 citas (algunas realizadas, algunas programadas)
                    (12, 20, 5),  # Diciembre: 5 citas (futuras programadas)
                ]

                horas_posibles = [
                    (time(8, 0), time(8, 50)),
                    (time(9, 0), time(9, 50)),
                    (time(10, 0), time(10, 50)),
                    (time(11, 0), time(11, 50)),
                    (time(14, 0), time(14, 50)),
                    (time(15, 0), time(15, 50)),
                    (time(16, 0), time(16, 50)),
                    (time(17, 0), time(17, 50)),
                    (time(18, 0), time(18, 50)),
                ]

                costos_posibles = [Decimal("150.00"), Decimal("180.00"), Decimal("200.00"), Decimal("220.00"), Decimal("250.00")]

                cita_index = 0
                for mes, max_dia, num_citas in meses_config:
                    for i in range(num_citas):
                        cita_index += 1
                        # Día distribuido
                        dia = min(max(1, (i * (max_dia // num_citas)) + 2), max_dia)
                        fecha_cita = date(2026, mes, dia)

                        # Decidir estado según si es pasado o futuro
                        if fecha_cita > hoy:
                            estado_cita = random.choice(['PROGRAMADA', 'CONFIRMADA'])
                        elif fecha_cita == hoy:
                            estado_cita = random.choice(['PROGRAMADA', 'CONFIRMADA', 'REALIZADA'])
                        else:
                            # Cita pasada: mayormente REALIZADA
                            rnd = random.random()
                            if rnd < 0.70:
                                estado_cita = 'REALIZADA'
                            elif rnd < 0.85:
                                estado_cita = 'CANCELADA'
                            elif rnd < 0.95:
                                estado_cita = 'INASISTENCIA'
                            else:
                                estado_cita = 'CONFIRMADA'

                        # Seleccionar paciente y psicólogo rotativos
                        pac = pacientes_activos[cita_index % len(pacientes_activos)]
                        psico = psicologos[cita_index % len(psicologos)]
                        h_inicio, h_fin = horas_posibles[cita_index % len(horas_posibles)]
                        modalidad = 'VIRTUAL' if (cita_index % 3 == 0) else 'PRESENCIAL'
                        costo = costos_posibles[cita_index % len(costos_posibles)]
                        motivo = MOTIVOS_CONSULTA[cita_index % len(MOTIVOS_CONSULTA)]
                        motivo_canc = MOTIVOS_CANCELACION[cita_index % len(MOTIVOS_CANCELACION)] if estado_cita == 'CANCELADA' else ""

                        # Evitar duplicados por psicologo y fecha_hora
                        if Cita.objects.filter(psicologo=psico, fecha=fecha_cita, hora_inicio=h_inicio).exists():
                            continue

                        cita = Cita.objects.create(
                            paciente=pac,
                            psicologo=psico,
                            fecha=fecha_cita,
                            hora_inicio=h_inicio,
                            hora_fin=h_fin,
                            modalidad=modalidad,
                            estado=estado_cita,
                            costo=costo,
                            motivo_consulta=motivo,
                            motivo_cancelacion=motivo_canc
                        )
                        citas_creadas += 1

                        # Si es virtual, crear Teleconsulta vinculada
                        if modalidad == 'VIRTUAL':
                            room_id = f"sigepsi-{clean_slug}-teleconsulta-{cita.id.hex[:8]}"
                            h_ini_real = None
                            h_fin_real = None
                            dur_seg = 0
                            if estado_cita == 'REALIZADA':
                                dt_base = datetime.combine(fecha_cita, h_inicio)
                                dt_base = timezone.make_aware(dt_base, timezone.get_current_timezone())
                                h_ini_real = dt_base
                                h_fin_real = dt_base + timedelta(minutes=random.choice([45, 50, 52, 55]))
                                dur_seg = int((h_fin_real - h_ini_real).total_seconds())

                            Teleconsulta.objects.get_or_create(
                                cita=cita,
                                defaults={
                                    "sala_id": room_id,
                                    "hora_inicio_real": h_ini_real,
                                    "hora_fin_real": h_fin_real,
                                    "duracion_segundos": dur_seg,
                                    "jwt_room_token": f"header.payload-token-fake-{cita.id.hex[:6]}.signature"
                                }
                            )
                            teleconsultas_creadas += 1

                self.stdout.write(f"  [OK] Citas históricas generadas: {citas_creadas} (Teleconsultas asociadas: {teleconsultas_creadas})")

                # 5. Generar Alertas Clínicas Diversas
                alertas_def = [
                    {"tipo": "INASISTENCIA_REITERADA", "sev": "ALTA", "desc": "Paciente no asistió a 2 sesiones consecutivas sin previo aviso.", "resuelta": True, "dias_atras": 40, "nota": "Contacto telefónico con paciente; justificó por viaje y se reprogramó."},
                    {"tipo": "INASISTENCIA_REITERADA", "sev": "ALTA", "desc": "Segunda falta consecutiva a consulta de seguimiento farmacológico.", "resuelta": False, "dias_atras": 5, "nota": ""},
                    {"tipo": "RIESGO_DESERCION", "sev": "MEDIA", "desc": "Paciente verbaliza dudas sobre continuar el tratamiento por motivos de tiempo.", "resuelta": True, "dias_atras": 60, "nota": "Se acordó cambio de modalidad presencial a virtual los días sábados."},
                    {"tipo": "RIESGO_DESERCION", "sev": "MEDIA", "desc": "Distanciamiento inter-sesiones mayor a 30 días sin confirmación de cita.", "resuelta": False, "dias_atras": 12, "nota": ""},
                    {"tipo": "URGENCIA_CLINICA", "sev": "CRITICA", "desc": "Ideación suicida pasiva identificada en preconsulta. Requiere triaje prioritario.", "resuelta": True, "dias_atras": 25, "nota": "Activación de protocolo de crisis, evaluación presencial y contacto con tutor."},
                    {"tipo": "URGENCIA_CLINICA", "sev": "CRITICA", "desc": "Agudización de crisis de angustia con sintomatología somática severa.", "resuelta": False, "dias_atras": 2, "nota": ""},
                    {"tipo": "CRISIS_RETROCESO", "sev": "MEDIA", "desc": "Puntuación en registro de ánimo muestra retroceso sostenido en la última semana.", "resuelta": True, "dias_atras": 18, "nota": "Revisión de técnicas cognitivas y ajuste de tareas terapéuticas."},
                    {"tipo": "CRISIS_RETROCESO", "sev": "BAJA", "desc": "Paciente reporta dificultad leve para completar tareas de autorregistro.", "resuelta": False, "dias_atras": 4, "nota": ""},
                    {"tipo": "RIESGO_DESERCION", "sev": "ALTA", "desc": "Cancelaciones reiteradas (3) en el transcurso del último mes.", "resuelta": True, "dias_atras": 75, "nota": "Entrevista motivacional realizada con el paciente; compromiso renovado."},
                    {"tipo": "URGENCIA_CLINICA", "sev": "ALTA", "desc": "Sintomatología disociativa reportada durante la sesión virtual.", "resuelta": True, "dias_atras": 90, "nota": "Derivación para interconsulta psiquiátrica complementaria."}
                ]

                alertas_creadas = 0
                for a_idx, a_data in enumerate(alertas_def):
                    pac = pacientes_activos[a_idx % len(pacientes_activos)]
                    # Verificar si ya existe alerta similar para este paciente
                    if Alerta.objects.filter(paciente=pac, tipo=a_data["tipo"], descripcion=a_data["desc"]).exists():
                        continue

                    f_creac = timezone.now() - timedelta(days=a_data["dias_atras"])
                    f_resol = (f_creac + timedelta(days=2)) if a_data["resuelta"] else None

                    Alerta.objects.create(
                        paciente=pac,
                        tipo=a_data["tipo"],
                        severidad=a_data["sev"],
                        descripcion=a_data["desc"],
                        resuelta=a_data["resuelta"],
                        fecha_resolucion=f_resol,
                        nota_resolucion=a_data["nota"]
                    )
                    alertas_creadas += 1

                self.stdout.write(f"  [OK] Alertas clínicas creadas: {alertas_creadas}")

                # 6. Registrar Eventos de Auditoría (Bitácora)
                audit_samples = [
                    {"action": "LOGIN_SUCCESS", "method": "POST", "path": "/api/auth/token/", "status_code": 200, "user": f"admin@{clean_slug}.com", "tenant": tenant.schema_name, "ip": "127.0.0.1"},
                    {"action": "REPORTE_GENERADO", "method": "GET", "path": "/api/reportes/citas/", "status_code": 200, "user": f"admin@{clean_slug}.com", "tenant": tenant.schema_name, "ip": "127.0.0.1"},
                    {"action": "REPORTE_EXPORT_CSV", "method": "GET", "path": "/api/reportes/citas/export/csv/", "status_code": 200, "user": f"admin@{clean_slug}.com", "tenant": tenant.schema_name, "ip": "127.0.0.1"},
                    {"action": "REPORTE_EXPORT_HTML", "method": "GET", "path": "/api/reportes/ingresos/export/html/", "status_code": 200, "user": f"admin@{clean_slug}.com", "tenant": tenant.schema_name, "ip": "127.0.0.1"},
                    {"action": "CITA_CREADA", "method": "POST", "path": "/api/agenda/citas/", "status_code": 201, "user": f"recepcion@{clean_slug}.com", "tenant": tenant.schema_name, "ip": "192.168.1.15"},
                    {"action": "CITA_REALIZADA", "method": "PATCH", "path": "/api/agenda/citas/status/", "status_code": 200, "user": f"psicologo@{clean_slug}.com", "tenant": tenant.schema_name, "ip": "192.168.1.22"},
                ]
                for evt in audit_samples:
                    try:
                        write_event(evt)
                    except Exception:
                        pass
                self.stdout.write(f"  [OK] Bitácora forense de auditoría sincronizada.")