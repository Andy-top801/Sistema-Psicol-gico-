import os
import sys
import random
import uuid
from datetime import date, datetime, time, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django_tenants.utils import schema_context
from tenants.models import Tenant
from accounts.models import Usuario, Rol
from accounts.utils import seed_tenant_roles_and_permissions
from clinica.models import Especialidad, Psicologo, Paciente
from agenda.models import Cita, Teleconsulta, Alerta

HASHED_PASS = make_password("Password123*")

# ─────────────────────────────────────────────────────────────────────────────
# CATÁLOGO DE DATOS CLÍNICOS REALISTAS
# ─────────────────────────────────────────────────────────────────────────────
ESPECIALIDADES_DEF = [
    ("Psicología Clínica y de la Salud", "Evaluación, diagnóstico y tratamiento de trastornos psicológicos."),
    ("Terapia Cognitivo-Conductual (TCC)", "Intervención basada en reestructuración de pensamientos y patrones de conducta."),
    ("Neuropsicología Clínica", "Evaluación y rehabilitación de funciones cognitivas, memoria y atención."),
    ("Psicología Infantil y Adolescente", "Abordaje del desarrollo emocional, conductual y escolar en infantes."),
    ("Terapia de Pareja y Familiar", "Resolución de conflictos vinculares, dinámicas familiares y comunicación asertiva."),
    ("Psicooncología y Cuidados Paliativos", "Acompañamiento psicológico en enfermedades crónicas y terminales."),
    ("Trastornos de Ansiedad y Depresión", "Tratamiento focalizado en fobias, pánico, TAG y trastornos del ánimo."),
    ("Adicciones y Conductas Compulsivas", "Prevención de recaídas y deshabituación de conductas adictivas."),
]

NOMBRES_HOMBRES = [
    "Carlos", "Alejandro", "Roberto", "Fernando", "Mateo", "Gabriel", "Diego",
    "Andrés", "Javier", "Sebastián", "Rodrigo", "Mauricio", "Lucas", "Emilio"
]
NOMBRES_MUJERES = [
    "Mariana", "Valeria", "Sofía", "Camila", "Lucía", "Elena", "Daniela",
    "Paola", "Andrea", "Renata", "Gabriela", "Carolina", "Beatriz", "Jimena"
]
APELLIDOS = [
    "Mendoza", "Morales", "Vargas", "Guzmán", "Flores", "Rojas", "Suárez",
    "Quinteros", "Castillo", "Cabrera", "Salazar", "Paredes", "Romero", "Aguilar",
    "Peña", "Navarro", "Delgado", "Villanueva", "Campos", "Herrera"
]

MOTIVOS_CONSULTA = [
    "Cuadro de ansiedad generalizada y dificultades persistentes para conciliar el sueño.",
    "Sesión de seguimiento TCC para reestructuración de distorsiones cognitivas.",
    "Manejo de ataques de pánico y entrenamiento en técnicas de respiración diafragmática.",
    "Terapia de pareja: resolución de conflictos de convivencia y comunicación asertiva.",
    "Evaluación neuropsicológica por dificultades de atención sostenida y memoria de trabajo.",
    "Abordaje de sintomatología depresiva moderada y pérdida de interés en actividades habituales.",
    "Acompañamiento clínico en proceso de duelo por pérdida familiar reciente.",
    "Terapia infantil: manejo de rabietas, ansiedad por separación y adaptación escolar.",
    "Manejo del estrés laboral crónico, agotamiento y prevención del síndrome de burnout.",
    "Regulación emocional y desarrollo de tolerancia al malestar ante situaciones de incertidumbre.",
    "Seguimiento farmacoterapéutico coordinado y psicoeducación familiar.",
    "Fortalecimiento de autoestima, asertividad y establecimiento de límites saludables.",
    "Intervención focalizada en fobia social y temor al juicio negativo en público.",
    "Evaluación psicométrica para orientación vocacional y toma de decisiones académicas.",
    "Trastorno obsesivo-compulsivo: exposición y prevención de respuesta (EPR)."
]

MOTIVOS_CANCELACION = [
    "Cruce de horarios laborales imprevisto del paciente.",
    "Urgencia médica no psiquiátrica reportada con antelación.",
    "Reprogramación solicitada por viaje laboral del paciente.",
    "Inclemencias climáticas y dificultad de transporte hacia el centro.",
    "Solicitud del paciente para postergar sesión a la semana siguiente."
]

ALERTAS_DEF = [
    ("INASISTENCIA_REITERADA", "ALTA", "Paciente no asistió a 2 sesiones continuas sin notificación previa. Riesgo de deserción.", "Se estableció contacto telefónico y se reacomodó el horario de atención según la disponibilidad del paciente."),
    ("INASISTENCIA_REITERADA", "MEDIA", "Inasistencia a sesión de seguimiento post-crisis. Requiere verificación de estado.", "Recepción contactó al familiar de emergencia; se confirmó estabilidad y se agendó cita de control."),
    ("RIESGO_DESERCION", "ALTA", "Paciente muestra resistencia e irregularidad tras 4 sesiones de tratamiento TCC.", "El terapeuta realizó llamada de encuadre psicoterapéutico reforzando los objetivos acordados."),
    ("RIESGO_DESERCION", "MEDIA", "Pérdida de adherencia terapéutica debido a dificultades económicas manifestadas.", "Administración aprobó ajuste de arancel social y modalidad virtual parcial."),
    ("URGENCIA_CLINICA", "CRITICA", "Intensificación severa de ideación pesimista y aislamiento afectivo agudo.", "Activación inmediata de red de apoyo familiar y derivación coordinada a psiquiatría de guardia."),
    ("URGENCIA_CLINICA", "ALTA", "Crisis de pánico aguda reportada durante la jornada laboral con descompensación.", "Sesión de contención emocional de urgencia brindada vía teleconsulta."),
    ("RIESGO_DESERCION", "BAJA", "Postergación reiterada de sesión quincenal por compromisos de estudio.", ""),
    ("INASISTENCIA_REITERADA", "ALTA", "Falta no justificada a sesión de evaluación neuropsicológica programada.", ""),
    ("URGENCIA_CLINICA", "CRITICA", "Crisis familiar aguda que afecta el bienestar del paciente menor de edad.", ""),
]

SLOTS_HORARIOS = [
    (time(8, 0), time(9, 0)),
    (time(9, 0), time(10, 0)),
    (time(10, 0), time(11, 0)),
    (time(11, 0), time(12, 0)),
    (time(14, 0), time(15, 0)),
    (time(15, 0), time(16, 0)),
    (time(16, 0), time(17, 0)),
    (time(17, 0), time(18, 0)),
    (time(18, 0), time(19, 0)),
]

TARIFAS = [120.00, 150.00, 180.00, 200.00, 220.00, 250.00]


def sembrar_tenant(tenant: Tenant):
    print(f"\n{'='*65}")
    print(f"SEMBRANDO DATOS PARA: {tenant.nombre} (Schema: {tenant.schema_name})")
    print(f"{'='*65}")

    with schema_context(tenant.schema_name):
        with transaction.atomic():
            # 1. Roles y Permisos
            roles_map = seed_tenant_roles_and_permissions()
            rol_admin = roles_map[Rol.ADMIN_CENTRO]
            rol_psico = roles_map[Rol.PSICOLOGO]
            rol_recep = roles_map[Rol.RECEPCIONISTA]
            rol_paciente = roles_map[Rol.PACIENTE]

            # 2. Especialidades
            especialidades_objs = []
            for nom, desc in ESPECIALIDADES_DEF:
                esp, _ = Especialidad.objects.get_or_create(
                    nombre=nom,
                    defaults={"descripcion": desc}
                )
                especialidades_objs.append(esp)
            print(f"  [OK] {len(especialidades_objs)} Especialidades verificadas.")

            # 3. Usuarios del Personal (Recepcionista adicional)
            recep_email = f"recepcion@{tenant.slug}.com"
            if not Usuario.objects.filter(email=recep_email).exists():
                Usuario.objects.create(
                    email=recep_email,
                    password=HASHED_PASS,
                    nombre="Carla",
                    apellido="Recepcionista",
                    telefono="77889901",
                    rol=rol_recep,
                    activo=True
                )
                print(f"  [OK] Recepcionista creada: {recep_email}")

            # 4. Psicólogos (4 a 5 psicólogos por centro)
            psicologos_creados = []
            for i in range(1, 6):
                email_psico = f"psicologo{i}@{tenant.slug}.com"
                user_psico = Usuario.objects.filter(email=email_psico).first()
                if not user_psico:
                    es_mujer = (i % 2 == 0)
                    nom = random.choice(NOMBRES_MUJERES if es_mujer else NOMBRES_HOMBRES)
                    ape = random.choice(APELLIDOS)
                    user_psico = Usuario.objects.create(
                        email=email_psico,
                        password=HASHED_PASS,
                        nombre=nom,
                        apellido=ape,
                        telefono=f"7{random.randint(1000000, 9999999)}",
                        rol=rol_psico,
                        activo=True
                    )

                psico_obj = Psicologo.objects.filter(usuario=user_psico).first()
                if not psico_obj:
                    modalidades = ['PRESENCIAL', 'VIRTUAL', 'MIXTA']
                    mod = modalidades[(i - 1) % len(modalidades)]
                    tarifa = TARIFAS[(i - 1) % len(TARIFAS)]
                    col_num = f"COL-{tenant.slug[:4].upper()}-{100 + i}"
                    psico_obj = Psicologo.objects.create(
                        usuario=user_psico,
                        numero_colegiado=col_num,
                        biografia=f"Especialista clínico con enfoque humanista y cognitivo-conductual. Graduado con honores y más de {i * 3} años de experiencia clínica institucional y privada.",
                        modalidad=mod,
                        tarifa_base=tarifa,
                        activo=True,
                        fecha_ingreso=date(2025, 1, 15) + timedelta(days=i * 45)
                    )
                    # Asignar 2-3 especialidades
                    sample_esp = random.sample(especialidades_objs, min(3, len(especialidades_objs)))
                    psico_obj.especialidades.set(sample_esp)

                psicologos_creados.append(psico_obj)

            print(f"  [OK] {len(psicologos_creados)} Psicólogos activos y con especialidades configuradas.")

            # 5. Pacientes (16 a 20 pacientes diversos)
            pacientes_creados = []
            total_pacientes_target = 18
            for i in range(1, total_pacientes_target + 1):
                email_pac = f"paciente{i}@{tenant.slug}.com"
                user_pac = Usuario.objects.filter(email=email_pac).first()
                if not user_pac:
                    es_mujer = (i % 2 == 0)
                    nom = random.choice(NOMBRES_MUJERES if es_mujer else NOMBRES_HOMBRES)
                    ape = random.choice(APELLIDOS)
                    user_pac = Usuario.objects.create(
                        email=email_pac,
                        password=HASHED_PASS,
                        nombre=nom,
                        apellido=ape,
                        telefono=f"6{random.randint(1000000, 9999999)}",
                        rol=rol_paciente,
                        activo=True
                    )

                pac_obj = Paciente.objects.filter(usuario=user_pac).first()
                if not pac_obj:
                    # Algunos menores de edad (ej. i in [3, 7, 12])
                    es_menor = (i in [3, 7, 12])
                    if es_menor:
                        anio_nac = random.randint(2010, 2016)
                        tutor_nom = f"Padre/Tutor de {user_pac.nombre} {user_pac.apellido}"
                        tutor_ci = f"{random.randint(3000000, 7000000)}"
                    else:
                        anio_nac = random.randint(1975, 2004)
                        tutor_nom = ""
                        tutor_ci = ""

                    fecha_nac = date(anio_nac, random.randint(1, 12), random.randint(1, 28))
                    ci_val = f"{random.randint(4000000, 9000000)}"
                    exp_codigo = f"EXP-{tenant.slug[:3].upper()}-2026-{1000 + i}"
                    genero = 'F' if (i % 2 == 0) else 'M'
                    fecha_reg = date(2026, 1, 10) + timedelta(days=i * 12)

                    pac_obj = Paciente.objects.create(
                        usuario=user_pac,
                        codigo_expediente=exp_codigo,
                        ci=ci_val,
                        fecha_nacimiento=fecha_nac,
                        genero=genero,
                        contacto_emergencia_nombre=f"Familiar {user_pac.apellido}",
                        contacto_emergencia_telf=f"7{random.randint(1000000, 9999999)}",
                        tutor_legal_nombre=tutor_nom,
                        tutor_legal_ci=tutor_ci,
                        fecha_registro=fecha_reg
                    )

                pacientes_creados.append(pac_obj)

            print(f"  [OK] {len(pacientes_creados)} Pacientes clínicos registrados.")

            # 6. Citas Clínicas (35 a 45 citas con variedad de estados, fechas, horas y costos)
            citas_target = 42
            citas_existentes = Cita.objects.count()
            citas_a_crear = max(0, citas_target - citas_existentes)
            citas_creadas = 0

            # Generar fechas distribuidas a lo largo del año 2026
            fechas_base = []
            # Pasadas
            for d in range(1, 60, 2):
                fechas_base.append(date(2026, 9, 17) - timedelta(days=d))
            # Presente / Hoy
            fechas_base.append(date(2026, 9, 17))
            # Futuras
            for d in range(1, 30, 2):
                fechas_base.append(date(2026, 9, 17) + timedelta(days=d))

            for i in range(citas_a_crear):
                fec = fechas_base[i % len(fechas_base)]
                slot = SLOTS_HORARIOS[i % len(SLOTS_HORARIOS)]
                h_ini, h_fin = slot
                pac = pacientes_creados[i % len(pacientes_creados)]
                psi = psicologos_creados[(i // 2) % len(psicologos_creados)]

                # Modalidad
                es_virtual = (i % 3 == 0)
                modalidad = 'VIRTUAL' if es_virtual else 'PRESENCIAL'

                # Estado según la fecha
                if fec < date(2026, 9, 17):
                    # Pasadas: Realizada, Inasistencia, Cancelada
                    if i % 8 == 0:
                        est = 'INASISTENCIA'
                        mot_canc = ""
                    elif i % 6 == 0:
                        est = 'CANCELADA'
                        mot_canc = random.choice(MOTIVOS_CANCELACION)
                    else:
                        est = 'REALIZADA'
                        mot_canc = ""
                elif fec == date(2026, 9, 17):
                    # Hoy: Confirmada o Programada
                    est = 'CONFIRMADA'
                    mot_canc = ""
                else:
                    # Futuras: Programada o Confirmada
                    est = 'CONFIRMADA' if (i % 2 == 0) else 'PROGRAMADA'
                    mot_canc = ""

                motivo = MOTIVOS_CONSULTA[i % len(MOTIVOS_CONSULTA)]
                costo = psi.tarifa_base

                cita = Cita.objects.create(
                    paciente=pac,
                    psicologo=psi,
                    fecha=fec,
                    hora_inicio=h_ini,
                    hora_fin=h_fin,
                    modalidad=modalidad,
                    estado=est,
                    motivo_consulta=motivo,
                    motivo_cancelacion=mot_canc,
                    costo=costo
                )
                citas_creadas += 1

                # 7. Si es virtual, crear Teleconsulta WebRTC
                if modalidad == 'VIRTUAL':
                    sala = f"sigepsi-{tenant.slug}-{cita.id.hex[:8]}"
                    h_ini_real = None
                    h_fin_real = None
                    dur_seg = 0
                    if est == 'REALIZADA':
                        dt_ini = timezone.make_aware(datetime.combine(fec, h_ini))
                        h_ini_real = dt_ini + timedelta(minutes=random.randint(1, 3))
                        dur_seg = random.randint(2700, 3300) # 45 a 55 min
                        h_fin_real = h_ini_real + timedelta(seconds=dur_seg)

                    Teleconsulta.objects.get_or_create(
                        cita=cita,
                        defaults={
                            "sala_id": sala,
                            "hora_inicio_real": h_ini_real,
                            "hora_fin_real": h_fin_real,
                            "duracion_segundos": dur_seg,
                        }
                    )

            print(f"  [OK] {Cita.objects.count()} Citas Clínicas disponibles en agenda.")
            print(f"  [OK] {Teleconsulta.objects.count()} Teleconsultas WebRTC enlazadas.")

            # 8. Alertas Clínicas (8 a 10 alertas con severidades y tipos diversos)
            alertas_target = 8
            if Alerta.objects.count() < alertas_target:
                alertas_creadas = 0
                for i, (tipo_alerta, severidad, desc, resol) in enumerate(ALERTAS_DEF):
                    pac = pacientes_creados[i % len(pacientes_creados)]
                    esta_resuelta = bool(resol)
                    fec_resol = timezone.now() - timedelta(days=random.randint(1, 10)) if esta_resuelta else None

                    Alerta.objects.create(
                        paciente=pac,
                        tipo=tipo_alerta,
                        severidad=severidad,
                        descripcion=desc,
                        resuelta=esta_resuelta,
                        fecha_resolucion=fec_resol,
                        nota_resolucion=resol
                    )
                    alertas_creadas += 1
                print(f"  [OK] {alertas_creadas} Alertas Clínicas registradas (Pendientes y Resueltas).")
            else:
                print(f"  [OK] {Alerta.objects.count()} Alertas Clínicas ya presentes.")


def main():
    tenants = Tenant.objects.exclude(schema_name='public').order_by('nombre')
    print(f"Iniciando siembra masiva de datos para {tenants.count()} centros registrados...\n")
    for t in tenants:
        sembrar_tenant(t)

    print("\n" + "="*65)
    print("RESUMEN GENERAL CONSOLIDADO DE TODOS LOS TENANTS")
    print("="*65)
    for t in tenants:
        with schema_context(t.schema_name):
            print(f"Tenant: {t.nombre:<32} (Schema: {t.schema_name:<20})")
            print(f"  • Usuarios:      {Usuario.objects.count():>3}")
            print(f"  • Psicólogos:    {Psicologo.objects.count():>3}")
            print(f"  • Pacientes:     {Paciente.objects.count():>3}")
            print(f"  • Citas:         {Cita.objects.count():>3}")
            print(f"  • Teleconsultas: {Teleconsulta.objects.count():>3}")
            print(f"  • Alertas:       {Alerta.objects.count():>3}")


if __name__ == "__main__":
    main()
