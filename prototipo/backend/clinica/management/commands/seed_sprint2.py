import hashlib
from typing import Any
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from django.utils import timezone
from django_tenants.utils import schema_context, get_tenant_model
from accounts.models import Usuario, Rol
from clinica.models import (
    Especialidad, Psicologo, Paciente,
    FormularioPreConsulta, RespuestaPreConsulta,
    HistoriaClinica, DiagnosticoCIE,
    NotaSesion, EvolucionClinica,
    TareaTerapeutica, EvidenciaTarea,
    ConsentimientoInformado, FirmaConsentimiento,
    DerivacionCaso, AuditoriaIA,
    ConversacionChatbot, MensajeChatbot
)
from agenda.models import Cita
from clinica.ia_rules_engine import PreconsultaRulesEngine
from audit.services import write_event


class Command(BaseCommand):
    help = "Siembra datos clínicos, éticos y forenses exhaustivos para el Sprint 2 (CU14 a CU20 y HU-35, HU-37) en todos los tenants"

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            default='centro_esperanza',
            help='Slug o schema_name del tenant donde sembrar los datos (o "all" para sembrar en todos los tenants activos)'
        )

    def handle(self, *args, **options):
        tenant_arg = options['tenant']
        Tenant = get_tenant_model()

        if tenant_arg == 'all':
            tenants = list(Tenant.objects.exclude(schema_name='public').filter(activo=True).order_by('schema_name'))
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

        self.stdout.write(self.style.SUCCESS(f"\n========================================================"))
        self.stdout.write(self.style.SUCCESS(f"INICIANDO SIEMBRA SPRINT 2 EN {len(tenants)} TENANT(S) ACTIVOS"))
        self.stdout.write(self.style.SUCCESS(f"========================================================\n"))

        for tenant in tenants:
            self.stdout.write(self.style.NOTICE(f"\n--------------------------------------------------------"))
            self.stdout.write(self.style.NOTICE(f"==> Sembrando Sprint 2 en: {tenant.nombre} ({tenant.schema_name})"))
            self.stdout.write(self.style.NOTICE(f"--------------------------------------------------------"))
            self.seed_tenant_sprint2(tenant)

        self.stdout.write(self.style.SUCCESS("\n[EXITO] Siembra de datos del Sprint 2 finalizada exitosamente en todos los tenants seleccionados.\n"))

    def seed_tenant_sprint2(self, tenant):
        # ------------------------------------------------------------------
        # 0. VERIFICAR ACTORES PRINCIPALES Y AUTO-PROVISIÓN SPRINT 1 SI FALTAN
        # ------------------------------------------------------------------
        with schema_context(tenant.schema_name):
            psicologos = list(Psicologo.objects.select_related('usuario').all())
            pacientes = list(Paciente.objects.select_related('usuario').all())

            if len(psicologos) < 3 or len(pacientes) < 5:
                self.stdout.write(self.style.WARNING(f"  [AUTO-PROVISIÓN] Aprovisionando actores base del Sprint 1 para {tenant.schema_name}..."))
                try:
                    call_command('seed_sprint1', tenant=tenant.schema_name, skip_sprint2=True)
                except Exception as ex:
                    self.stderr.write(f"  [ERROR] Falló aprovisionamiento Sprint 1 en {tenant.schema_name}: {ex}")
                psicologos = list(Psicologo.objects.select_related('usuario').all())
                pacientes = list(Paciente.objects.select_related('usuario').all())

            if not psicologos or not pacientes:
                self.stderr.write(f"  [ERROR] No se pudieron asegurar psicólogos y pacientes en {tenant.schema_name}.")
                return

            atomic_tx: Any = transaction.atomic()
            with atomic_tx:
                # Mapeo de psicólogos
                psico_principal = Psicologo.objects.filter(numero_colegiado="COL-PSI-4589").first() or psicologos[0]
                psico_secundario = Psicologo.objects.filter(numero_colegiado="COL-PSI-7821").first() or (psicologos[1] if len(psicologos) > 1 else psico_principal)
                psico_neuro = Psicologo.objects.filter(numero_colegiado="COL-PSI-9340").first() or (psicologos[2] if len(psicologos) > 2 else psico_principal)
                psico_context = Psicologo.objects.filter(numero_colegiado="COL-SP2-9988").first() or (psicologos[3] if len(psicologos) > 3 else psico_principal)
                psico_trauma = Psicologo.objects.filter(numero_colegiado="COL-PSI-3120").first() or (psicologos[4] if len(psicologos) > 4 else psico_principal)

                # Mapeo de pacientes
                pac_juan = Paciente.objects.filter(ci="8472910-LP").first() or pacientes[0]
                pac_sofia = Paciente.objects.filter(ci="10928374-CB").first() or (pacientes[1] if len(pacientes) > 1 else pac_juan)
                pac_mateo = Paciente.objects.filter(ci="13459872-SC").first() or (pacientes[2] if len(pacientes) > 2 else pac_juan)
                pac_elena = Paciente.objects.filter(ci="7382914-TJ").first() or (pacientes[3] if len(pacientes) > 3 else pac_juan)
                pac_diego = Paciente.objects.filter(ci="9182736-OR").first() or (pacientes[4] if len(pacientes) > 4 else pac_juan)
                pac_valentina = Paciente.objects.filter(ci="12345678-SC").first() or (pacientes[5] if len(pacientes) > 5 else pac_juan)
                pac_rodrigo = Paciente.objects.filter(ci="6574839-BN").first() or (pacientes[6] if len(pacientes) > 6 else pac_juan)

                citas = list(Cita.objects.all())
                cita_juan = citas[0] if citas else None
                cita_sofia = citas[1] if len(citas) > 1 else None

                # Prefijo de código de HC único
                clean_slug = tenant.schema_name.upper().replace('CENTRO_', '').replace('_', '')
                slug_prefix = clean_slug[:6] if clean_slug else "CLI"

                # ------------------------------------------------------------------
                # 1. CU14 / HU-23, HU-24: FORMULARIOS PRE-CONSULTA E INTAKE DIGITAL
                # ------------------------------------------------------------------
                self.stdout.write("  -> 1. Configurando Cuestionarios Pre-Consulta (Intake Digital - CU14)...")

                preguntas_intake_1 = [
                    {"id": "p_motivo", "texto": "¿Cuál es el motivo principal por el que decide consultar?", "tipo": "texto", "requerido": True},
                    {"id": "p_escala", "texto": "En una escala de 1 a 5, ¿cuál es su nivel de malestar o urgencia percibido?", "tipo": "escala_1_5", "requerido": True},
                    {"id": "p_panico", "texto": "¿Ha experimentado opresión en el pecho, palpitaciones o sensación de falta de aire (ataques de pánico)?", "tipo": "booleano", "requerido": True},
                    {"id": "p_insomnio", "texto": "Frecuencia de dificultades para dormir o conciliar el sueño:", "tipo": "opcion_multiple", "opciones": ["Nunca", "1 a 2 días por semana", "Casi todos los días", "Todas las noches"], "requerido": True},
                    {"id": "p_tratamiento_previo", "texto": "¿Ha recibido atención psicológica o psiquiátrica previa?", "tipo": "booleano", "requerido": False}
                ]

                form_intake_gral = FormularioPreConsulta.objects.filter(titulo__icontains="Cuestionario Integral").first()
                if not form_intake_gral:
                    form_intake_gral = FormularioPreConsulta.objects.create(
                        titulo="Cuestionario Integral de Sintomatología y Preconsulta v1.0",
                        version="v1.0",
                        descripcion="Instrumento anamnésico estructurado para recopilar el motivo de consulta, nivel de malestar y antecedentes antes de la primera sesión.",
                        preguntas_schema=preguntas_intake_1,
                        activo=True
                    )

                preguntas_intake_2 = [
                    {"id": "p_animo", "texto": "En las últimas 2 semanas, ¿con qué frecuencia ha sentido tristeza o desánimo?", "tipo": "opcion_multiple", "opciones": ["Rara vez", "Varios días", "Más de la mitad de los días", "Casi a diario"], "requerido": True},
                    {"id": "p_intensidad", "texto": "Nivel de interferencia emocional en su trabajo o estudio (1 a 5)", "tipo": "escala_1_5", "requerido": True},
                    {"id": "p_red_apoyo", "texto": "¿Cuenta con familiares o personas de confianza a quienes recurrir en caso de crisis?", "tipo": "booleano", "requerido": True}
                ]

                form_intake_animo = FormularioPreConsulta.objects.filter(titulo__icontains="Escala de Tamizaje").first()
                if not form_intake_animo:
                    form_intake_animo = FormularioPreConsulta.objects.create(
                        titulo="Escala de Tamizaje y Regulación Emocional v2.0",
                        version="v2.0",
                        descripcion="Tamizaje breve para evaluar afectividad, soporte social y funcionamiento adaptativo inter-sesiones.",
                        preguntas_schema=preguntas_intake_2,
                        activo=True
                    )

                preguntas_intake_3 = [
                    {"id": "p_conducta_escolar", "texto": "¿Se han reportado quejas de conducta o bajo rendimiento escolar?", "tipo": "booleano", "requerido": True},
                    {"id": "p_inquietud_motriz", "texto": "¿El menor muestra dificultad constante para permanecer sentado o concentrado?", "tipo": "booleano", "requerido": True},
                    {"id": "p_edad_inicio", "texto": "Edad aproximada en la que comenzaron las dificultades observadas:", "tipo": "texto", "requerido": True}
                ]

                form_intake_infantil = FormularioPreConsulta.objects.filter(titulo__icontains="Evaluación Infanto-Juvenil").first()
                if not form_intake_infantil:
                    form_intake_infantil = FormularioPreConsulta.objects.create(
                        titulo="Cuestionario de Evaluación Infanto-Juvenil y Escolar v1.0",
                        version="v1.0",
                        descripcion="Evaluación estructurada para padres y tutores sobre el desarrollo conductual y atencional del menor.",
                        preguntas_schema=preguntas_intake_3,
                        activo=True
                    )

                preguntas_intake_4 = [
                    {"id": "p_agotamiento_laboral", "texto": "¿Siente agotamiento mental y físico extremo al comenzar o finalizar su jornada?", "tipo": "booleano", "requerido": True},
                    {"id": "p_cinismo", "texto": "¿Ha experimentado distanciamiento emocional o apatía hacia sus actividades habituales?", "tipo": "booleano", "requerido": True},
                    {"id": "p_somatizacion", "texto": "Presencia de cefaleas tensionales o dolores gástricos recurrentes:", "tipo": "opcion_multiple", "opciones": ["Nunca", "Ocasional", "Frecuente", "Diario"], "requerido": True}
                ]

                form_intake_burnout = FormularioPreConsulta.objects.filter(titulo__icontains="Estrés y Desgaste").first()
                if not form_intake_burnout:
                    form_intake_burnout = FormularioPreConsulta.objects.create(
                        titulo="Inventario Breve de Estrés y Desgaste Psicológico (Burnout) v1.0",
                        version="v1.0",
                        descripcion="Evaluación de sobrecarga laboral crónica, agotamiento psicofísico y somatización.",
                        preguntas_schema=preguntas_intake_4,
                        activo=True
                    )

                # Respuestas Pre-Consulta de Pacientes
                resp_juan = RespuestaPreConsulta.objects.filter(paciente=pac_juan, formulario=form_intake_gral).first()
                if not resp_juan:
                    resp_juan = RespuestaPreConsulta.objects.create(
                        paciente=pac_juan,
                        formulario=form_intake_gral,
                        cita=cita_juan,
                        motivo_consulta="Crisis recurrentes de angustia, taquicardia intensa y temor constante a sufrir un infarto en el trabajo.",
                        sintomas_principales="Palpitaciones, opresión torácica, mareo, hiperventilación e insomnio de conciliación.",
                        nivel_urgencia_percibido=4,
                        antecedentes_medicos="Descarte cardiológico completo sin anomalías orgánicas (marzo 2026).",
                        antecedentes_psiquiatricos="Sin tratamientos psiquiátricos previos.",
                        medicacion_actual="Ninguna medicación psiquiátrica prescrita.",
                        respuestas_detalle={
                            "p_motivo": "Crisis recurrentes de angustia, taquicardia intensa y temor constante a sufrir un infarto.",
                            "p_escala": 4,
                            "p_panico": True,
                            "p_insomnio": "Casi todos los días",
                            "p_tratamiento_previo": False
                        },
                        estado="REVISADO"
                    )

                resp_sofia = RespuestaPreConsulta.objects.filter(paciente=pac_sofia, formulario=form_intake_animo).first()
                if not resp_sofia:
                    resp_sofia = RespuestaPreConsulta.objects.create(
                        paciente=pac_sofia,
                        formulario=form_intake_animo,
                        cita=cita_sofia,
                        motivo_consulta="Sensación persistente de agotamiento, pérdida de interés en la universidad y tristeza profunda.",
                        sintomas_principales="Apatía, llanto esporádico, dificultad para concentrarse y anhedonia.",
                        nivel_urgencia_percibido=3,
                        antecedentes_medicos="Hipotiroidismo subclínico en tratamiento con Levotiroxina 50mcg.",
                        antecedentes_psiquiatricos="Acompañamiento psicológico breve en 2024 por duelo familiar.",
                        medicacion_actual="Levotiroxina 50mcg / día.",
                        respuestas_detalle={
                            "p_animo": "Más de la mitad de los días",
                            "p_intensidad": 3,
                            "p_red_apoyo": True
                        },
                        estado="ENVIADO"
                    )

                resp_mateo = RespuestaPreConsulta.objects.filter(paciente=pac_mateo, formulario=form_intake_infantil).first()
                if not resp_mateo:
                    resp_mateo = RespuestaPreConsulta.objects.create(
                        paciente=pac_mateo,
                        formulario=form_intake_infantil,
                        motivo_consulta="Dificultad severa para mantener la atención en clases, desobediencia e inquietud motriz constante reportada por profesores.",
                        sintomas_principales="Impulsividad, interrupciones constantes, olvido de útiles escolares y dificultad para seguir instrucciones complejas.",
                        nivel_urgencia_percibido=3,
                        antecedentes_medicos="Desarrollo psicomotor dentro de parámetros normales.",
                        antecedentes_psiquiatricos="Sin diagnósticos neurológicos previos.",
                        medicacion_actual="Ninguna.",
                        respuestas_detalle={
                            "p_conducta_escolar": True,
                            "p_inquietud_motriz": True,
                            "p_edad_inicio": "A partir de los 7 años"
                        },
                        estado="REVISADO"
                    )

                resp_elena = RespuestaPreConsulta.objects.filter(paciente=pac_elena, formulario=form_intake_animo).first()
                if not resp_elena:
                    resp_elena = RespuestaPreConsulta.objects.create(
                        paciente=pac_elena,
                        formulario=form_intake_animo,
                        motivo_consulta="Duelo patológico tras el fallecimiento de su cónyuge, episodios de llanto descontrolado y aislamiento social.",
                        sintomas_principales="Insomnio terminal, pérdida de peso, dolor torácico por somatización y anhedonia.",
                        nivel_urgencia_percibido=3,
                        antecedentes_medicos="Hipertensión arterial controlada con Enalapril 10mg.",
                        antecedentes_psiquiatricos="Sin antecedentes.",
                        medicacion_actual="Enalapril 10mg / día.",
                        respuestas_detalle={
                            "p_animo": "Casi a diario",
                            "p_intensidad": 4,
                            "p_red_apoyo": True
                        },
                        estado="REVISADO"
                    )

                resp_valentina = RespuestaPreConsulta.objects.filter(paciente=pac_valentina, formulario=form_intake_gral).first()
                if not resp_valentina:
                    resp_valentina = RespuestaPreConsulta.objects.create(
                        paciente=pac_valentina,
                        formulario=form_intake_gral,
                        motivo_consulta="Flashbacks intrusivos, sobresalto extremo e insomnio severo tras sobrevivir a un accidente vehicular con impacto.",
                        sintomas_principales="Pesadillas vívidas, evitación fóbica de vehículos, hipervigilancia extrema y taquicardia paroxística.",
                        nivel_urgencia_percibido=5,
                        antecedentes_medicos="Politraumatismo leve en recuperación traumatológica.",
                        antecedentes_psiquiatricos="Sin antecedentes previos.",
                        medicacion_actual="Analgésicos según requerimiento.",
                        respuestas_detalle={
                            "p_motivo": "Flashbacks intrusivos y sobresalto extremo tras accidente vehicular.",
                            "p_escala": 5,
                            "p_panico": True,
                            "p_insomnio": "Todas las noches",
                            "p_tratamiento_previo": False
                        },
                        estado="ENVIADO"
                    )

                resp_rodrigo = RespuestaPreConsulta.objects.filter(paciente=pac_rodrigo, formulario=form_intake_burnout).first()
                if not resp_rodrigo:
                    resp_rodrigo = RespuestaPreConsulta.objects.create(
                        paciente=pac_rodrigo,
                        formulario=form_intake_burnout,
                        motivo_consulta="Síndrome de Burnout agudo: agotamiento emocional crónico, sensación de incompetencia y cefaleas tensionales diarias.",
                        sintomas_principales="Fatiga constante, irritabilidad laboral, dificultades de concentración y despersonalización.",
                        nivel_urgencia_percibido=4,
                        antecedentes_medicos="Gastritis crónica reactiva al estrés.",
                        antecedentes_psiquiatricos="Sin antecedentes.",
                        medicacion_actual="Omeprazol 20mg en ayunas.",
                        respuestas_detalle={
                            "p_agotamiento_laboral": True,
                            "p_cinismo": True,
                            "p_somatizacion": "Diario"
                        },
                        estado="ENVIADO"
                    )

                self.stdout.write(self.style.SUCCESS(f"     [OK] 4 Formularios y 6 Respuestas Pre-Consulta registradas."))

                # ------------------------------------------------------------------
                # 2. HU-35: MOTOR DE REGLAS CLÍNICAS IA (ROMERO) Y AUDITORÍA ÉTICA
                # ------------------------------------------------------------------
                self.stdout.write("  -> 2. Evaluando Asistente Piloto IA (HU-35 - Reglas Dr. Romero)...")

                respuestas_para_ia = [
                    (resp_juan, psico_principal, "EDITADO", "Se valida sugerencia asistiva. Cuadro compatible con crisis de angustia / pánico reactivo a sobrecarga laboral. Se programa sesión prioritaria."),
                    (resp_sofia, psico_principal, "ACEPTADO", "Convalido análisis preliminar. Sintomatología depresiva moderada sin ideación autolítica. Se iniciará protocolo de Activación Conductual."),
                    (resp_mateo, psico_secundario, "EDITADO", "Ajuste de sugerencia para enfocar evaluación de funciones ejecutivas y estructuración de rutinas escolares con la tutora legal."),
                    (resp_elena, psico_trauma, "ACEPTADO", "Se confirma pertinencia de abordaje en duelo complejo. Se acuerda espacio de validación afectiva semanal."),
                    (resp_valentina, psico_trauma, "ACEPTADO", "Alerta de prioridad crítica confirmada por reactivación postraumática aguda con riesgo de descompensación autonómica. Se prioriza sobreturnos."),
                    (resp_rodrigo, psico_context, "PENDIENTE", "")
                ]

                for resp_obj, psico_rev, dec_humana, obs in respuestas_para_ia:
                    if not AuditoriaIA.objects.filter(formulario_respuesta_id=resp_obj.id).exists():
                        analisis = PreconsultaRulesEngine.evaluar_preconsulta(resp_obj)
                        AuditoriaIA.objects.create(
                            formulario_respuesta_id=resp_obj.id,
                            psicologo=psico_rev,
                            hash_prompt=analisis['hash_prompt'],
                            resumen_generado=analisis['resumen_generado'],
                            prioridad_sugerida=analisis['prioridad_sugerida'],
                            reglas_aplicadas=analisis['reglas_aplicadas'],
                            evaluacion_humana=dec_humana,
                            observaciones_profesional=obs,
                            fecha_decision=timezone.now() if dec_humana != "PENDIENTE" else None,
                            ip_origen="192.168.1.55"
                        )

                self.stdout.write(self.style.SUCCESS(f"     [OK] Registros de auditoría IA generados (Romero Rules, PII Sanitization y Supervisión Humana)."))

                # ------------------------------------------------------------------
                # 3. CU15 / HU-25, HU-26: HISTORIAS CLÍNICAS (EHR) Y DIAGNÓSTICOS CIE-10
                # ------------------------------------------------------------------
                self.stdout.write("  -> 3. Aperturando Historias Clínicas Electrónicas y Diagnósticos CIE-10 (CU15)...")

                historias_data = [
                    {
                        "paciente": pac_juan,
                        "psico": psico_principal,
                        "codigo": f"HC-{slug_prefix}-2026-0001",
                        "motivo": "Episodios agudos de ansiedad, hiperventilación y sensación inminente de colapso físico desencadenados en entorno laboral.",
                        "personales": "Sedentarismo moderado, consumo de 3 cafés diarios. Sin cardiopatías.",
                        "familiares": "Madre con antecedentes de crisis de pánico en la juventud.",
                        "evolutiva": "Inicio del cuadro hace 4 meses tras ascenso laboral con incremento drástico de responsabilidades.",
                        "mental": "Lúcido, orientado. Discurso coherente y acelerado. Afecto ansioso, reactivo. Sin ideación suicida.",
                        "plan": "Terapia Cognitivo-Conductual: 1) Psicoeducación, 2) Respiración diafragmática, 3) Reestructuración cognitiva, 4) Exposición interoceptiva.",
                        "cerrada": False,
                        "cie10": [
                            ("F41.0", "Trastorno de pánico (ansiedad episódica paroxística)", "CONFIRMADO", "Ataques de pánico imprevistos con sintomatología adrenérgica aguda."),
                            ("F41.1", "Trastorno de ansiedad generalizada", "CONFIRMADO", "Preocupación excesiva e hiperactivación autonómica por más de 6 meses.")
                        ]
                    },
                    {
                        "paciente": pac_sofia,
                        "psico": psico_principal,
                        "codigo": f"HC-{slug_prefix}-2026-0002",
                        "motivo": "Decaimiento anímico prolongado, rumiación pesimista y baja energía con repercusión en rendimiento académico universitario.",
                        "personales": "Hipotiroidismo controlado con Levotiroxina.",
                        "familiares": "Tía materna con trastorno depresivo recurrente.",
                        "evolutiva": "Cuadro insidioso de 6 meses de evolución caracterizado por anhedonia y postergación recurrente de metas.",
                        "mental": "Lenguaje pausado, bradipsiquia leve, afecto melancólico con llanto fácil. Insight conservado.",
                        "plan": "Terapia Cognitiva de Beck y Activación Conductual: Monitoreo diario de placer y dominio, reatribución de culpa y resolución de problemas.",
                        "cerrada": False,
                        "cie10": [
                            ("F32.1", "Episodio depresivo moderado", "CONFIRMADO", "Humor depresivo persistente, anhedonia y disminución marcada de la energía vital.")
                        ]
                    },
                    {
                        "paciente": pac_mateo,
                        "psico": psico_secundario,
                        "codigo": f"HC-{slug_prefix}-2026-0003",
                        "motivo": "Inquietud motriz constante en clase, dificultad para completar tareas escolares y desobediencia en el hogar.",
                        "personales": "Parto eutócico a término sin complicaciones. Hitos del desarrollo en rangos esperados.",
                        "familiares": "Padre con historial de dispersión atencional en la infancia.",
                        "evolutiva": "Rendimiento escolar comprometido en el 6to de primaria debido a impulsividad y distracción fácil.",
                        "mental": "Niño colaborador, contacto visual intermitente, inquietud psicomotriz evidente. Pensamiento ágil y coherente.",
                        "plan": "Entrenamiento conductual para padres y maestros, economía de fichas, técnicas de autocontrol y estructuración ambiental.",
                        "cerrada": False,
                        "cie10": [
                            ("F90.0", "Perturbación de la actividad y de la atención (TDAH)", "CONFIRMADO", "Patrón persistente de inatención e hiperactividad en más de dos contextos."),
                            ("F93.0", "Trastorno de ansiedad de separación en la niñez", "DIFERENCIAL", "A descartar ante quejas somáticas matutinas previas a la escuela.")
                        ]
                    },
                    {
                        "paciente": pac_elena,
                        "psico": psico_trauma,
                        "codigo": f"HC-{slug_prefix}-2026-0004",
                        "motivo": "Trastorno de adaptación con reacción depresiva prolongada tras pérdida conyugal reciente.",
                        "personales": "Hipertensión arterial bajo control médico regular.",
                        "familiares": "Sin antecedentes psiquiátricos familiares reportados.",
                        "evolutiva": "Duelo de 8 meses con dificultades marcadas para retomar actividades de la vida diaria y somatizaciones torácicas.",
                        "mental": "Orientada, facies de profunda aflicción, labilidad afectiva reactiva al recuerdo del cónyuge.",
                        "plan": "Psicoterapia de duelo y reconstrucción de significados (Neimeyer), validación emocional y reactivación gradual de redes vinculares.",
                        "cerrada": False,
                        "cie10": [
                            ("F43.2", "Trastornos de adaptación (reacción depresiva prolongada)", "CONFIRMADO", "Dificultad adaptativa con síntomas afectivos subsiguientes a evento estresante biográfico.")
                        ]
                    },
                    {
                        "paciente": pac_valentina,
                        "psico": psico_trauma,
                        "codigo": f"HC-{slug_prefix}-2026-0005",
                        "motivo": "Reexperimentación traumática aguda, pesadillas y sobresaltos autonómicos severos tras accidente de tránsito.",
                        "personales": "Contusiones menores en extremidades ya cicatrizadas.",
                        "familiares": "Sin antecedentes psiquiátricos familiares de relevancia.",
                        "evolutiva": "El accidente ocurrió hace 5 semanas. Desde entonces presenta evitación de vehículos y respuestas de pánico ante bocinas.",
                        "mental": "Hipervigilante, postura en tensión, contacto visual ansioso. Temblor fino en manos. Sin pérdida de contacto con la realidad.",
                        "plan": "Protocolo de procesamiento del trauma (EMDR / TCC focalizada en trauma), grounding sensorial 5-4-3-2-1 y desensibilización sistemática.",
                        "cerrada": False,
                        "cie10": [
                            ("F43.1", "Trastorno de estrés postraumático", "PRESUNTIVO", "Reexperimentación intrusiva, hiperreactividad y conductas de evitación persistentes.")
                        ]
                    },
                    {
                        "paciente": pac_diego,
                        "psico": psico_principal,
                        "codigo": f"HC-{slug_prefix}-2026-ALTA",
                        "motivo": "Fobia social circunscrita a exposiciones orales en público y presentaciones directivas.",
                        "personales": "Sin antecedentes patológicos. Buena salud física general.",
                        "familiares": "Madre con rasgos de personalidad ansiosa.",
                        "evolutiva": "Tratamiento de 16 sesiones completado con éxito mediante reestructuración cognitiva y exposición en vivo gradual.",
                        "mental": "Lúcido, tranquilo, afecto eutímico, discurso fluido y seguro. Total remisión de sintomatología ansiosa.",
                        "plan": "Alta terapéutica por cumplimiento integral de objetivos. Sesiones de seguimiento preventivo a los 3 y 6 meses.",
                        "cerrada": True,
                        "cie10": [
                            ("F40.1", "Fobias sociales", "CONFIRMADO", "Miedo al escrutinio ajeno resuelto tras 16 sesiones de TCC con remisión total.")
                        ]
                    }
                ]

                hc_map = {}
                for h_data in historias_data:
                    hc = HistoriaClinica.objects.filter(paciente=h_data['paciente']).first()
                    if not hc:
                        hc = HistoriaClinica.objects.filter(codigo_historia=h_data['codigo']).first()
                    if not hc:
                        hc = HistoriaClinica.objects.create(
                            paciente=h_data['paciente'],
                            psicologo_apertura=h_data['psico'],
                            codigo_historia=h_data['codigo'],
                            motivo_consulta_inicial=h_data['motivo'],
                            antecedentes_personales=h_data['personales'],
                            antecedentes_familiares=h_data['familiares'],
                            historia_evolutiva=h_data['evolutiva'],
                            examen_mental_inicial=h_data['mental'],
                            plan_tratamiento=h_data['plan'],
                            cerrada=h_data['cerrada'],
                            fecha_cierre=timezone.now() - timedelta(days=3) if h_data['cerrada'] else None
                        )
                    else:
                        if h_data['cerrada'] and not hc.cerrada:
                            hc.cerrada = True
                            hc.fecha_cierre = timezone.now() - timedelta(days=3)
                            hc.save()

                    hc_map[h_data['paciente'].ci] = hc

                    # Diagnósticos CIE-10
                    for cod_cie, desc_cie, tipo_cie, obs_cie in h_data['cie10']:
                        DiagnosticoCIE.objects.get_or_create(
                            historia_clinica=hc,
                            codigo_cie=cod_cie,
                            defaults={
                                "descripcion": desc_cie,
                                "tipo": tipo_cie,
                                "observaciones": obs_cie,
                                "fecha_diagnostico": date.today() - timedelta(days=15)
                            }
                        )

                hc_juan = hc_map[pac_juan.ci]
                hc_sofia = hc_map[pac_sofia.ci]
                hc_mateo = hc_map[pac_mateo.ci]
                hc_elena = hc_map[pac_elena.ci]
                hc_valentina = hc_map[pac_valentina.ci]
                hc_diego = hc_map[pac_diego.ci]

                self.stdout.write(self.style.SUCCESS(f"     [OK] 6 Historias Clínicas aseguradas con diagnósticos CIE-10 clasificados."))

                # ------------------------------------------------------------------
                # 4. CU16 / HU-27: NOTAS DE SESIÓN CLÍNICAS (MODELO SOAP)
                # ------------------------------------------------------------------
                self.stdout.write("  -> 4. Registrando Notas de Sesión SOAP Estructuradas (CU16)...")

                cita_juan_disp = cita_juan if (cita_juan and not NotaSesion.objects.filter(cita=cita_juan).exists()) else None
                cita_sofia_disp = cita_sofia if (cita_sofia and not NotaSesion.objects.filter(cita=cita_sofia).exists()) else None

                # Notas Juan
                nota_juan_1 = NotaSesion.objects.filter(historia_clinica=hc_juan, numero_sesion=1).first()
                if not nota_juan_1:
                    nota_juan_1 = NotaSesion.objects.create(
                        historia_clinica=hc_juan,
                        numero_sesion=1,
                        cita=cita_juan_disp,
                        psicologo=psico_principal,
                        fecha_sesion=timezone.now() - timedelta(days=14),
                        subjetivo="Paciente refiere: 'Siento que en cualquier momento mi corazón va a fallar cuando tengo que presentar informes en el trabajo. No puedo estar tranquilo en lugares cerrados'. Manifiesta agotamiento mental.",
                        objetivo="Presentación adecuada. Facies de preocupación marcada, hiperhidrosis palmar y respiración apical superficial. Tensión muscular visible en cuello y hombros. Escala de malestar inicial: 8/10.",
                        analisis="Cuadro clínicamente significativo correspondiente a crisis de angustia con agorafobia incipiente. Se evidencia sesgo atencional hacia sensaciones interoceptivas viscerales.",
                        plan="1. Psicoeducación integral sobre el modelo cognitivo del pánico (bucle somato-psíquico de Clark). 2. Entrenamiento en respiración diafragmática lenta (ritmo 4-2-6). 3. Prescripción de autorregistro diario.",
                        tecnicas_aplicadas="Psicoeducación, Entrenamiento en Respiración Diafragmática",
                        conducta_observada="Ansiedad situacional reactiva al relato, alta colaboración y receptividad.",
                        estado_guardado="FIRMADA",
                        fecha_firma=timezone.now() - timedelta(days=14)
                    )

                nota_juan_2 = NotaSesion.objects.filter(historia_clinica=hc_juan, numero_sesion=2).first()
                if not nota_juan_2:
                    nota_juan_2 = NotaSesion.objects.create(
                        historia_clinica=hc_juan,
                        numero_sesion=2,
                        psicologo=psico_principal,
                        fecha_sesion=timezone.now() - timedelta(days=7),
                        subjetivo="Paciente comenta: 'Practiqué la respiración dos veces al día. Cuando sentí las palpitaciones el jueves en la oficina pude frenar el ataque antes de salir corriendo'.",
                        objetivo="Facies relajada, postura corporal más distendida. Demuestra en consulta la técnica respiratoria logrando 6 respiraciones por minuto con adecuada expansión abdominal.",
                        analisis="Excelente adherencia a las técnicas de desactivación fisiológica. Inicio de flexibilización cognitiva sobre las sensaciones corporales normales.",
                        plan="1. Revisión de autorregistro de pensamientos distorsionados. 2. Identificación de catastrofización ('me voy a morir'). 3. Formulación de pensamientos alternativos basados en evidencia.",
                        tecnicas_aplicadas="Reestructuración Cognitiva, Técnica de Flecha Descendente",
                        conducta_observada="Optimismo moderado y motivación alta.",
                        estado_guardado="FIRMADA",
                        fecha_firma=timezone.now() - timedelta(days=7)
                    )

                nota_juan_3 = NotaSesion.objects.filter(historia_clinica=hc_juan, numero_sesion=3).first()
                if not nota_juan_3:
                    nota_juan_3 = NotaSesion.objects.create(
                        historia_clinica=hc_juan,
                        numero_sesion=3,
                        psicologo=psico_principal,
                        fecha_sesion=timezone.now(),
                        subjetivo="Paciente ingresa comentando que esta semana tuvo un reto en el transporte público con ligera ansiedad, pero logró mantenerse en el lugar utilizando el diálogo interno alternativo.",
                        objetivo="Afecto eutímico reactivo, lenguaje fluido, buena modulación emocional.",
                        analisis="Consolidación de logros terapéuticos y disminución de conductas de evitación fóbica.",
                        plan="Planificar jerarquía de exposición in vivo a situaciones cotidianas temidas (ascensor, reuniones largas). Continuar autorregistro semanal.",
                        tecnicas_aplicadas="Diseño de Jerarquía de Exposición In Vivo",
                        conducta_observada="Autonomía creciente y reducción del miedo al miedo.",
                        estado_guardado="BORRADOR"
                    )

                # Notas Sofía
                nota_sofia_1 = NotaSesion.objects.filter(historia_clinica=hc_sofia, numero_sesion=1).first()
                if not nota_sofia_1:
                    nota_sofia_1 = NotaSesion.objects.create(
                        historia_clinica=hc_sofia,
                        numero_sesion=1,
                        cita=cita_sofia_disp,
                        psicologo=psico_principal,
                        fecha_sesion=timezone.now() - timedelta(days=10),
                        subjetivo="Paciente relata: 'Me cuesta levantarme de la cama y siento que he perdido el rumbo. Nada de lo que antes me gustaba me genera satisfacción'.",
                        objetivo="Tono de voz pausado, contacto visual esquivo al inicio, afecto apagado de cualidad depresiva. Sin ideación delirante ni autolítica.",
                        analisis="Episodio depresivo moderado reactivo con componentes de aislamiento social y reforzamiento negativo del reposo excesivo.",
                        plan="1. Introducción al modelo de Activación Conductual. 2. Monitoreo diario de actividades y calificación de placer (P) y dominio (D) en escala 1 a 10. 3. Pactar caminata matutina de 15 minutos.",
                        tecnicas_aplicadas="Activación Conductual, Programación de Actividades",
                        conducta_observada="Receptiva al encuadre aunque con expectativas moderadas de eficacia inicial.",
                        estado_guardado="FIRMADA",
                        fecha_firma=timezone.now() - timedelta(days=10)
                    )

                nota_sofia_2 = NotaSesion.objects.filter(historia_clinica=hc_sofia, numero_sesion=2).first()
                if not nota_sofia_2:
                    nota_sofia_2 = NotaSesion.objects.create(
                        historia_clinica=hc_sofia,
                        numero_sesion=2,
                        psicologo=psico_principal,
                        fecha_sesion=timezone.now() - timedelta(days=3),
                        subjetivo="Paciente refiere haber salido a caminar 3 de los 5 días propuestos y haber retomado contacto con una compañera de estudios.",
                        objetivo="Mejora en contacto visual, sonrisa social conservada, mayor fluidez verbal.",
                        analisis="Respuesta favorable al incremento gradual de fuentes de reforzamiento positivo en el medio ambiente.",
                        plan="Continuar registro de actividades e incorporar una meta de dominio académico (leer 10 páginas por día).",
                        tecnicas_aplicadas="Activación Conductual, Asignación Gradual de Tareas",
                        conducta_observada="Incremento visible de la autoeficacia percibida.",
                        estado_guardado="FIRMADA",
                        fecha_firma=timezone.now() - timedelta(days=3)
                    )

                # Notas Mateo
                nota_mateo_1 = NotaSesion.objects.filter(historia_clinica=hc_mateo, numero_sesion=1).first()
                if not nota_mateo_1:
                    nota_mateo_1 = NotaSesion.objects.create(
                        historia_clinica=hc_mateo,
                        numero_sesion=1,
                        psicologo=psico_secundario,
                        fecha_sesion=timezone.now() - timedelta(days=12),
                        subjetivo="Tutora refiere constantes llamados de atención del colegio por levantarse del asiento y extraviar cuadernos.",
                        objetivo="Inquietud motora en el consultorio, manipulación rápida de objetos, atención sostenida menor a 5 minutos sin reforzador.",
                        analisis="Perfil sintomático concordante con Trastorno por Déficit de Atención con Hiperactividad de presentación combinada.",
                        plan="1. Psicoeducación a la tutora legal. 2. Diseño de cartilla de economía de fichas para el hogar y aula.",
                        tecnicas_aplicadas="Economía de Fichas, Psicoeducación Familiar",
                        conducta_observada="Sociable, simpático, con dificultad marcada de inhibición conductual.",
                        estado_guardado="FIRMADA",
                        fecha_firma=timezone.now() - timedelta(days=12)
                    )

                # Notas Valentina
                nota_val_1 = NotaSesion.objects.filter(historia_clinica=hc_valentina, numero_sesion=1).first()
                if not nota_val_1:
                    nota_val_1 = NotaSesion.objects.create(
                        historia_clinica=hc_valentina,
                        numero_sesion=1,
                        psicologo=psico_trauma,
                        fecha_sesion=timezone.now() - timedelta(days=4),
                        subjetivo="Paciente refiere pesadillas todas las noches donde revive el choque vehicular: 'Siento el olor a humo y el estruendo de los vidrios rompiéndose'.",
                        objetivo="Hiperreactividad a sonidos externos durante la sesión (sobresalto ante cierre de puerta). Taquicardia referida.",
                        analisis="Cuadro agudo de estrés postraumático con reexperimentación intrusiva y desregulación autonómica importante.",
                        plan="1. Ejercicios de anclaje sensorial en el presente (Grounding 5-4-3-2-1). 2. Psicoeducación sobre la respuesta de lucha/huida del sistema nervioso. 3. Prohibir exposición forzada al tráfico.",
                        tecnicas_aplicadas="Grounding Sensorial, Estabilización de Trauma",
                        conducta_observada="Afecto angustiado con estado de alerta permanente.",
                        estado_guardado="FIRMADA",
                        fecha_firma=timezone.now() - timedelta(days=4)
                    )

                # Nota Diego (Alta)
                nota_diego_cierre = NotaSesion.objects.filter(historia_clinica=hc_diego, numero_sesion=16).first()
                if not nota_diego_cierre:
                    nota_diego_cierre = NotaSesion.objects.create(
                        historia_clinica=hc_diego,
                        numero_sesion=16,
                        psicologo=psico_principal,
                        fecha_sesion=timezone.now() - timedelta(days=3),
                        subjetivo="Paciente afirma con serenidad: 'Hice la presentación ante 50 personas del directorio sin ansiedad anticipatoria y sintiéndome completamente seguro'.",
                        objetivo="Excelente aplomo, postura segura, contacto visual firme, humor eutímico.",
                        analisis="Cumplimiento pleno de objetivos terapéuticos. Consolidación de autoesquemas adaptativos de competencia social.",
                        plan="Cierre formal de caso y firma de Alta Terapéutica. Se acuerda pauta de prevención de recaídas y sesión de control opcional a los 6 meses.",
                        tecnicas_aplicadas="Consolidación de Logros, Prevención de Recaídas, Cierre de Proceso",
                        conducta_observada="Seguro, agradecido y autónomo.",
                        estado_guardado="FIRMADA",
                        fecha_firma=timezone.now() - timedelta(days=3)
                    )

                self.stdout.write(self.style.SUCCESS(f"     [OK] Notas SOAP registradas (Firmadas e inmutables y Borradores de autosave)."))

                # ------------------------------------------------------------------
                # 5. CU17 / HU-28, HU-29, HU-30: EVOLUCIÓN LONGITUDINAL Y TAREAS
                # ------------------------------------------------------------------
                self.stdout.write("  -> 5. Prescribiendo Tareas Terapéuticas y Registrando Evolución Longitudinal (CU17)...")

                evoluciones_data = [
                    (hc_juan, nota_juan_2, "PROGRESO_NOTABLE", "El paciente logró abortar un ataque de pánico incipiente aplicando respiración diafragmática sin abandonar el puesto de trabajo.", "Mantener registro de pensamientos y realizar 2 prácticas diafragmáticas preventivas diarias."),
                    (hc_sofia, nota_sofia_1, "EN_PROCESO", "Inicio de tratamiento. Se acordó la línea base de actividades y compromiso de no permanencia en cama posterior a las 08:30.", "Completar la planilla de actividades placenteras y caminar 15 minutos en las mañanas."),
                    (hc_mateo, nota_mateo_1, "EN_PROCESO", "Establecimiento de normas claras y reforzadores positivos en el hogar.", "Revisar cumplimiento diario de fichas escolares."),
                    (hc_valentina, nota_val_1, "RETROCESO_CRISIS", "Reactivación severa de sobresalto autonómico y pánico ante bocinazo de camión en la avenida. Requiere protocolo de crisis y grounding.", "Práctica estricta de respiración 4-2-6 y grounding en momentos de intrusión mnémica."),
                    (hc_diego, nota_diego_cierre, "PROGRESO_NOTABLE", "Alta clínica. Paciente desenvuelto en eventos sociales y laborales con 0 conductas de evitación.", "Mantener hábitos de exposición voluntaria.")
                ]

                for hc_item, nota_item, est_avance, just, acuer in evoluciones_data:
                    if not EvolucionClinica.objects.filter(historia_clinica=hc_item, nota_sesion=nota_item).exists():
                        EvolucionClinica.objects.create(
                            historia_clinica=hc_item,
                            nota_sesion=nota_item,
                            estado_avance=est_avance,
                            justificacion=just,
                            acuerdos_pactados=acuer
                        )

                # Tareas Terapéuticas (Todas las categorías: AUTOREGISTRO, MINDFULNESS, CONDUCTUAL, COGNITIVA)
                tareas_seed = [
                    {
                        "hc": hc_juan,
                        "psico": psico_principal,
                        "paciente": pac_juan,
                        "titulo": "Autorregistro de Pensamientos Automáticos ante la Ansiedad",
                        "desc": "Registrar en la planilla: 1) Situación desencadenante, 2) Emoción y nivel (0-100), 3) Pensamiento automático, 4) Pensamiento alternativo racional.",
                        "cat": "AUTOREGISTRO",
                        "estado": "COMPLETADA",
                        "limite": date.today() + timedelta(days=4),
                        "evidencia": {
                            "reflexion": "Logré identificar que cuando mi superior me llamó imprevisto pensé inmediatamente: 'Me van a despedir y me dará un ataque'. Al cuestionarlo recordé que las evaluaciones trimestrales siempre fueron excelentes, lo cual calmó mi taquicardia.",
                            "dificultad": 3
                        }
                    },
                    {
                        "hc": hc_juan,
                        "psico": psico_principal,
                        "paciente": pac_juan,
                        "titulo": "Práctica Diaria de Respiración Diafragmática (10 min)",
                        "desc": "Realizar 2 series diarias de 10 minutos de respiración lenta (4 seg inhalar, 2 sostener, 6 exhalar) antes del almuerzo y al finalizar la jornada laboral.",
                        "cat": "MINDFULNESS",
                        "estado": "PENDIENTE",
                        "limite": date.today() + timedelta(days=6),
                        "evidencia": None
                    },
                    {
                        "hc": hc_sofia,
                        "psico": psico_principal,
                        "paciente": pac_sofia,
                        "titulo": "Planilla Semanal de Activación Conductual (Placer y Dominio)",
                        "desc": "Calificar cada bloque de 2 horas con valores del 1 al 10 en: Nivel de Placer (P) y Nivel de Logro o Dominio (D).",
                        "cat": "CONDUCTUAL",
                        "estado": "COMPLETADA",
                        "limite": date.today() + timedelta(days=5),
                        "evidencia": {
                            "reflexion": "Pude salir a caminar al parque 3 días a las 9 am. Me di cuenta de que al regresar a casa mi nivel de energía aumentaba de 2 a 6. El placer no fue total pero me sentí útil.",
                            "dificultad": 2
                        }
                    },
                    {
                        "hc": hc_sofia,
                        "psico": psico_principal,
                        "paciente": pac_sofia,
                        "titulo": "Identificación de Sesgos de Todo o Nada y Autoexigencia",
                        "desc": "Anotar cuando surja la idea de 'si no saco la máxima nota soy un fracaso' y escribir al menos dos matices intermedios objetivos.",
                        "cat": "COGNITIVA",
                        "estado": "PENDIENTE",
                        "limite": date.today() + timedelta(days=7),
                        "evidencia": None
                    },
                    {
                        "hc": hc_mateo,
                        "psico": psico_secundario,
                        "paciente": pac_mateo,
                        "titulo": "Cuadro de Estrellas de Conducta Escolar y Casa",
                        "desc": "Completar la cartilla de metas diarias con la profesora de curso y la tutora en casa.",
                        "cat": "CONDUCTUAL",
                        "estado": "VENCIDA",
                        "limite": date.today() - timedelta(days=2),
                        "evidencia": None
                    },
                    {
                        "hc": hc_valentina,
                        "psico": psico_trauma,
                        "paciente": pac_valentina,
                        "titulo": "Ejercicio de Grounding Sensorial 5-4-3-2-1 ante Desrealización",
                        "desc": "En el momento en que comience el mareo o flashback: nombrar 5 cosas que ves, 4 que tocas, 3 que escuchas, 2 que hueles y 1 que saboreas.",
                        "cat": "MINDFULNESS",
                        "estado": "COMPLETADA",
                        "limite": date.today() + timedelta(days=2),
                        "evidencia": {
                            "reflexion": "Ayer sentí que perdía el control al escuchar un frenazo en la esquina. Me senté en una banca y empecé a tocar la textura de madera y mirar las hojas de los árboles. Me ayudó a darme cuenta de que estaba a salvo hoy.",
                            "dificultad": 4
                        }
                    },
                    {
                        "hc": hc_elena,
                        "psico": psico_trauma,
                        "paciente": pac_elena,
                        "titulo": "Registro de Gratitud y Reconocimiento de Recursos Personales",
                        "desc": "Escribir tres momentos del día en que haya sentido acompañamiento o tranquilidad en su entorno familiar.",
                        "cat": "COGNITIVA",
                        "estado": "PENDIENTE",
                        "limite": date.today() + timedelta(days=8),
                        "evidencia": None
                    }
                ]

                for t_seed in tareas_seed:
                    tar = TareaTerapeutica.objects.filter(historia_clinica=t_seed['hc'], titulo=t_seed['titulo']).first()
                    if not tar:
                        tar = TareaTerapeutica.objects.create(
                            historia_clinica=t_seed['hc'],
                            psicologo=t_seed['psico'],
                            paciente=t_seed['paciente'],
                            titulo=t_seed['titulo'],
                            descripcion=t_seed['desc'],
                            categoria=t_seed['cat'],
                            fecha_limite=t_seed['limite'],
                            estado=t_seed['estado']
                        )
                    if t_seed['evidencia']:
                        if not hasattr(tar, 'evidencia') or not tar.evidencia:
                            EvidenciaTarea.objects.get_or_create(
                                tarea=tar,
                                defaults={
                                    "texto_reflexion": t_seed['evidencia']['reflexion'],
                                    "dificultad_percibida": t_seed['evidencia']['dificultad']
                                }
                            )

                self.stdout.write(self.style.SUCCESS(f"     [OK] 7 Tareas terapéuticas (Cognitiva, Conductual, Mindfulness, Autorregistro) y Evidencias creadas."))

                # ------------------------------------------------------------------
                # 6. CU18 / HU-31, HU-32: PLANTILLAS Y FIRMAS DE CONSENTIMIENTO DIGITAL
                # ------------------------------------------------------------------
                self.stdout.write("  -> 6. Generando Plantillas y Firmas de Consentimiento Informado con SHA-256 (CU18)...")

                plantilla_gral = ConsentimientoInformado.objects.filter(tipo="ATENCION_GENERAL").first()
                if not plantilla_gral:
                    plantilla_gral = ConsentimientoInformado.objects.create(
                        tipo="ATENCION_GENERAL",
                        titulo="Consentimiento Informado para Tratamiento Psicoterapéutico General",
                        version="v1.0",
                        contenido_legal=(
                            "Yo, {PACIENTE_NOMBRE}, con Documento de Identidad {PACIENTE_CI}, declaro de manera libre, consciente y voluntaria que he sido informado/a adecuadamente por el profesional tratante {PSICOLOGO_CABECERA} acerca de los objetivos, alcance, metodología, duración estimada y encuadre del proceso psicoterapéutico que inicio en {CENTRO_NOMBRE}.\n\n"
                            "Comprendo que la confidencialidad de la información compartida en sesión está amparada por el secreto profesional y el Código de Ética Psicológica, salvo en situaciones excepcionales tipificadas por ley: a) Riesgo inminente y grave para mi propia vida o integridad física, b) Riesgo inminente para la vida o integridad de terceras personas, c) Requerimiento judicial formal expedido por autoridad competente.\n\n"
                            "Acepto las normas del centro sobre puntualidad, cancelación de citas con 24 horas de anticipación y aranceles profesionales acordados."
                        ),
                        activo=True
                    )

                plantilla_tele = ConsentimientoInformado.objects.filter(tipo="TELEPSICOLOGIA").first()
                if not plantilla_tele:
                    plantilla_tele = ConsentimientoInformado.objects.create(
                        tipo="TELEPSICOLOGIA",
                        titulo="Consentimiento Específico para Servicios de Telepsicología y Videoatención Cifrada",
                        version="v1.0",
                        contenido_legal=(
                            "Yo, {PACIENTE_NOMBRE}, con CI {PACIENTE_CI}, acepto recibir atención psicológica a distancia mediante la plataforma de teleconsulta segura de SIGEPSI con {PSICOLOGO_CABECERA}.\n\n"
                            "Reconozco que la sesión cuenta con cifrado extremo a extremo. Me comprometo a conectarme desde un entorno privado, libre de interrupciones, y declaro conocer que está prohibida la grabación de audio o video de las sesiones sin consentimiento expreso por escrito de ambas partes."
                        ),
                        activo=True
                    )

                plantilla_menor = ConsentimientoInformado.objects.filter(tipo="MENORES_EDAD").first()
                if not plantilla_menor:
                    plantilla_menor = ConsentimientoInformado.objects.create(
                        tipo="MENORES_EDAD",
                        titulo="Autorización Legal de Tratamiento y Evaluación Psicológica para Menores de Edad",
                        version="v1.0",
                        contenido_legal=(
                            "Yo, {TUTOR_NOMBRE}, con Cédula de Identidad {TUTOR_CI}, en mi condición legal y acreditada de madre/padre/tutor(a) legal del menor {PACIENTE_NOMBRE}, autorizo formalmente su evaluación y atención psicoterapéutica con el equipo profesional de {CENTRO_NOMBRE}.\n\n"
                            "Declaro haber recibido orientación detallada sobre los procedimientos de evaluación diagnóstica infanto-juvenil."
                        ),
                        activo=True
                    )

                plantilla_ia = ConsentimientoInformado.objects.filter(tipo="DATOS_SENSIBLES").first()
                if not plantilla_ia:
                    plantilla_ia = ConsentimientoInformado.objects.create(
                        tipo="DATOS_SENSIBLES",
                        titulo="Consentimiento Informado para Tratamiento de Datos Sensibles y Asistencia Tecnológica",
                        version="v1.0",
                        contenido_legal=(
                            "Yo, {PACIENTE_NOMBRE}, autorizo a {CENTRO_NOMBRE} al almacenamiento seguro de mi expediente de salud mental bajo los estándares de la Ley de Protección de Datos Personales. Autorizo el análisis asistivo previo de cuestionarios bajo supervisión humana obligatoria y sin diagnóstico automático."
                        ),
                        activo=True
                    )

                # Firmas de Consentimiento Digitales con Sello Criptográfico SHA-256
                firmas_seed = [
                    (pac_juan, plantilla_gral, False, "", "", "192.168.1.45", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SIGEPSI-Web/2.0", 21),
                    (pac_sofia, plantilla_tele, False, "", "", "190.181.25.10", "Dart/3.3 (dart:io) Flutter-SIGEPSI/2.1", 14),
                    (pac_mateo, plantilla_menor, True, pac_mateo.tutor_legal_nombre or "Beatriz Lima Flores", pac_mateo.tutor_legal_ci or "4892301-SC", "192.168.1.60", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SIGEPSI-Web/2.0", 11),
                    (pac_elena, plantilla_ia, False, "", "", "192.168.1.75", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36", 9),
                    (pac_valentina, plantilla_gral, False, "", "", "192.168.1.88", "Dart/3.3 (dart:io) Flutter-SIGEPSI/2.1", 5),
                ]

                for p_pac, p_plant, es_menor, tut_nom, tut_ci, ip_f, ua_f, dias_atras in firmas_seed:
                    if not FirmaConsentimiento.objects.filter(paciente=p_pac, consentimiento=p_plant).exists():
                        firmante = tut_nom if es_menor else f"{p_pac.usuario.nombre} {p_pac.usuario.apellido}"
                        texto_base = f"Yo, {firmante}, CI {tut_ci if es_menor else p_pac.ci}, acepto {p_plant.titulo} en {tenant.nombre}."
                        hash_f = hashlib.sha256(texto_base.encode('utf-8')).hexdigest()
                        FirmaConsentimiento.objects.create(
                            paciente=p_pac,
                            consentimiento=p_plant,
                            firmado_por=firmante,
                            es_menor_edad=es_menor,
                            tutor_nombre=tut_nom,
                            tutor_ci=tut_ci,
                            hash_sha256=hash_f,
                            ip_origen=ip_f,
                            user_agent=ua_f,
                            firma_canvas_url="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMzAiPjxwYXRoIGQ9Ik0xMCAyMCBRIDIwIDUgMzAgMjAgVCA1MCAyMCIgc3Ryb2tlPSJibGFjayIgZmlsbD0idHJhbnNwYXJlbnQiLz48L3N2Zz4=",
                            fecha_firma=timezone.now() - timedelta(days=dias_atras)
                        )

                self.stdout.write(self.style.SUCCESS(f"     [OK] 4 Plantillas legales y 5 Firmas criptográficas SHA-256 aseguradas."))

                # ------------------------------------------------------------------
                # 7. CU19 / HU-33, HU-34: CIERRE DE CASO Y DERIVACIONES MÉDICAS
                # ------------------------------------------------------------------
                self.stdout.write("  -> 7. Registrando Protocolos de Cierre y Órdenes de Derivación Psiquiátrica (CU19)...")

                derivaciones_seed = [
                    {
                        "hc": hc_diego,
                        "tipo": "CIERRE_ALTA",
                        "psico": psico_principal,
                        "motivo": "Alta Terapéutica por consecución completa de los objetivos terapéuticos. Reducción sostenida del malestar situacional al 100%.",
                        "logros": "Superación de la fobia social, realización exitosa de presentaciones públicas sin sintomatología adrenérgica.",
                        "mantenimiento": "Continuar con exposiciones sociales voluntarias y aplicación de técnicas de reestructuración cognitiva.",
                        "sintomas": "Asintomático. Desenvolvimiento social y laboral óptimo.",
                        "destino_prof": "N/A (Cierre de Expediente)",
                        "destino_inst": f"{tenant.nombre}",
                        "riesgo": "BAJO",
                        "aceptada": True,
                        "pdf": "/media/derivaciones/acta_alta_diego_alarcon.pdf"
                    },
                    {
                        "hc": hc_juan,
                        "tipo": "EXTERNA_PSIQUIATRIA",
                        "psico": psico_principal,
                        "motivo": "Interconsulta médica para evaluación de tratamiento psicofarmacológico coadyuvante (ISRS) debido a la frecuencia y severidad de las crisis de pánico.",
                        "logros": "",
                        "mantenimiento": "",
                        "sintomas": "Crisis de pánico paroxísticas con cortejo autonómico intenso (taquicardia, opresión torácica) y agorafobia incipiente.",
                        "destino_prof": "Dr. Hugo Gómez Mercado (Médico Psiquiatra)",
                        "destino_inst": "Hospital San Juan de Dios - Servicio de Salud Mental",
                        "riesgo": "ALTO",
                        "aceptada": True,
                        "pdf": "/media/derivaciones/orden_psiquiatria_juan_perez.pdf"
                    },
                    {
                        "hc": hc_mateo,
                        "tipo": "INTERNA_COLEGA",
                        "psico": psico_secundario,
                        "motivo": "Derivación interna al servicio de Neuropsicología para aplicación de batería psicométrica WISC-V y perfil de funciones ejecutivas.",
                        "logros": "",
                        "mantenimiento": "",
                        "sintomas": "Inquietud motora, distractibilidad severa y desinhibición conductual.",
                        "destino_prof": f"Lic. {psico_neuro.usuario.nombre} {psico_neuro.usuario.apellido}",
                        "destino_inst": f"{tenant.nombre} - Área de Neuropsicología",
                        "riesgo": "MEDIO",
                        "aceptada": True,
                        "pdf": ""
                    },
                    {
                        "hc": hc_valentina,
                        "tipo": "EXTERNA_PSIQUIATRIA",
                        "psico": psico_trauma,
                        "motivo": "Interconsulta urgente a Psiquiatría por trastorno de estrés postraumático severo con insomnio refractario de 5 semanas.",
                        "logros": "",
                        "mantenimiento": "",
                        "sintomas": "Reexperimentación traumática diurna y nocturna, hipervigilancia paroxística y reactivación autonómica severa.",
                        "destino_prof": "Dra. Claudia Benítez (Psiquiatra de Enlace)",
                        "destino_inst": "Centro Médico de Especialidades y Urgencias",
                        "riesgo": "CRITICO",
                        "aceptada": True,
                        "pdf": "/media/derivaciones/orden_psiquiatria_valentina_ramos.pdf"
                    }
                ]

                for d_data in derivaciones_seed:
                    if not DerivacionCaso.objects.filter(historia_clinica=d_data['hc'], tipo_derivacion=d_data['tipo']).exists():
                        DerivacionCaso.objects.create(
                            historia_clinica=d_data['hc'],
                            tipo_derivacion=d_data['tipo'],
                            psicologo_emisor=d_data['psico'],
                            motivo_clinico=d_data['motivo'],
                            logros_alcanzados=d_data['logros'],
                            recomendaciones_mantenimiento=d_data['mantenimiento'],
                            sintomatologia_relevante=d_data['sintomas'],
                            profesional_destino=d_data['destino_prof'],
                            institucion_destino=d_data['destino_inst'],
                            nivel_riesgo=d_data['riesgo'],
                            aceptada=d_data['aceptada'],
                            documento_pdf_url=d_data['pdf']
                        )

                self.stdout.write(self.style.SUCCESS(f"     [OK] 4 Protocolos de Derivación y Cierre de Caso asegurados (Alta y Psiquiatría)."))

                # ------------------------------------------------------------------
                # 8. CU20 / HU-36: CHATBOT ASISTENTE CON DETECCIÓN DE RIESGO Y CRISIS
                # ------------------------------------------------------------------
                self.stdout.write("  -> 8. Sembrando Conversaciones y Mensajes de Chatbot con Alertas de Crisis (CU20 / HU-36)...")

                # Conversación 1: Consulta General y Agendamiento (Riesgo NORMAL)
                sess_gral_id = f"session-{tenant.schema_name}-gral-001"
                conv_gral = ConversacionChatbot.objects.filter(session_id=sess_gral_id).first()
                if not conv_gral:
                    conv_gral = ConversacionChatbot.objects.create(
                        session_id=sess_gral_id,
                        paciente=pac_juan,
                        usuario=pac_juan.usuario,
                        estado='FINALIZADA',
                        nivel_riesgo='NORMAL'
                    )
                    MensajeChatbot.objects.create(
                        conversacion=conv_gral,
                        remitente='USUARIO',
                        texto="Hola, quisiera saber los horarios de atención y especialidades del centro."
                    )
                    MensajeChatbot.objects.create(
                        conversacion=conv_gral,
                        remitente='BOT',
                        texto=f"¡Hola! En {tenant.nombre} atendemos de lunes a viernes de 08:00 a 18:00. Contamos con especialistas en Terapia Cognitivo-Conductual, Psicología Infantil, Neuropsicología y Terapias Contextuales. ¿Deseas agendar una cita o ver los profesionales?",
                        opciones_sugeridas=['Ver psicólogos disponibles', 'Agendar cita', 'Horarios de atención']
                    )
                    MensajeChatbot.objects.create(
                        conversacion=conv_gral,
                        remitente='USUARIO',
                        texto="Me gustaría agendar una cita para manejo de ansiedad."
                    )
                    MensajeChatbot.objects.create(
                        conversacion=conv_gral,
                        remitente='BOT',
                        texto="Excelente decisión. Contamos con el Lic. Carlos Mendoza y el Lic. Gabriel Montes especializados en manejo de ansiedad y pánico. Puedes reservar directamente desde tu panel o solicitar asistencia de recepción.",
                        opciones_sugeridas=['Reservar cita', 'Hablar con recepción']
                    )

                # Conversación 2: Detección de Crisis Vital y Protocolo de Emergencia Inmediata (Riesgo CRISIS)
                sess_crisis_id = f"session-{tenant.schema_name}-crisis-002"
                conv_crisis = ConversacionChatbot.objects.filter(session_id=sess_crisis_id).first()
                if not conv_crisis:
                    conv_crisis = ConversacionChatbot.objects.create(
                        session_id=sess_crisis_id,
                        paciente=pac_valentina,
                        usuario=pac_valentina.usuario,
                        estado='ESCALADA_HUMANO',
                        nivel_riesgo='CRISIS'
                    )
                    MensajeChatbot.objects.create(
                        conversacion=conv_crisis,
                        remitente='USUARIO',
                        texto="Por favor necesito ayuda urgente... no doy más, siento que me voy a morir o hacerme daño, no puedo frenar esta desesperación y no le encuentro sentido a nada."
                    )
                    MensajeChatbot.objects.create(
                        conversacion=conv_crisis,
                        remitente='BOT',
                        texto=(
                            f"⚠️ PROTOCOLO DE APOYO INMEDIATO ACTIVADO: Tu vida y bienestar son lo más importante. No estás solo/a en este momento de angustia. Por favor, comunícate de inmediato con una línea gratuita de contención emocional o acude al servicio de urgencias:\n\n"
                            f"• Línea Gratuita de Apoyo y Prevención del Suicidio: 800-11-3040 (24 horas)\n"
                            f"• Emergencias Médicas Nacionales: 911 / 110\n"
                            f"• Servicio de Urgencias de Salud Mental\n\n"
                            f"Hemos notificado con máxima prioridad al equipo de recepción y guardia de {tenant.nombre} para asistirte de inmediato."
                        ),
                        es_alerta_crisis=True,
                        opciones_sugeridas=['Llamar al 800-11-3040', 'Llamar al 911', 'Contactar recepción de guardia', 'Guía de respiración para calmarme']
                    )
                    MensajeChatbot.objects.create(
                        conversacion=conv_crisis,
                        remitente='OPERADOR',
                        texto=f"Hola Valentina, soy la Lic. de guardia en {tenant.nombre}. Recibimos tu alerta de emergencia prioritaria. Estamos aquí contigo. Por favor mantente en un lugar seguro y respira despacio. ¿Te encuentras con alguien de confianza a tu lado?"
                    )

                # Conversación 3: Solicitud de Teleconsulta y Orientación (Riesgo MODERADO)
                sess_tele_id = f"session-{tenant.schema_name}-tele-003"
                conv_tele = ConversacionChatbot.objects.filter(session_id=sess_tele_id).first()
                if not conv_tele:
                    conv_tele = ConversacionChatbot.objects.create(
                        session_id=sess_tele_id,
                        paciente=pac_sofia,
                        usuario=pac_sofia.usuario,
                        estado='EN_ATENCION',
                        nivel_riesgo='MODERADO',
                        operador_asignado=psico_principal.usuario
                    )
                    MensajeChatbot.objects.create(
                        conversacion=conv_tele,
                        remitente='USUARIO',
                        texto="Hola, me siento muy decaída y no vivo cerca de la clínica. ¿Tienen opción de atención virtual por videollamada?"
                    )
                    MensajeChatbot.objects.create(
                        conversacion=conv_tele,
                        remitente='BOT',
                        texto=f"¡Hola Sofía! Sí, en {tenant.nombre} disponemos de la plataforma de Telepsicología Cifrada para que puedas recibir tus sesiones con total seguridad y confidencialidad sin trasladarte.",
                        opciones_sugeridas=['¿Cómo funciona la teleconsulta?', 'Requisitos técnicos', 'Hablar con un asesor']
                    )
                    MensajeChatbot.objects.create(
                        conversacion=conv_tele,
                        remitente='OPERADOR',
                        texto="Hola Sofía, un gusto saludarte. Con mucho gusto te ayudamos a coordinar tu teleconsulta. Ya activamos tu opción en el panel para que puedas agendar con el especialista de tu preferencia."
                    )

                self.stdout.write(self.style.SUCCESS(f"     [OK] 3 Conversaciones de Chatbot y Mensajes sembrados (Riesgo Normal, Crisis con Protocolo Vital y Operador Humano)."))

                # ------------------------------------------------------------------
                # 9. HU-37: REGISTRO FORENSE EN DISCO CIFRADO (AUDIT LOG)
                # ------------------------------------------------------------------
                self.stdout.write("  -> 9. Registrando Trazas Forenses Cifradas en Disco (HU-37)...")
                try:
                    write_event({
                        "event_type": "CLINICAL_RECORD_SEED",
                        "tenant": tenant.schema_name,
                        "user_id": str(psico_principal.usuario.id),
                        "user_email": psico_principal.usuario.email,
                        "resource": "HistoriaClinica",
                        "action": "SEED_VERIFIED_SPRINT2",
                        "details": f"Siembra de historias clínicas, SOAP, consentimientos SHA-256 y chatbot en {tenant.nombre}"
                    })
                    write_event({
                        "event_type": "CRISIS_ALERT_TRIGGERED",
                        "tenant": tenant.schema_name,
                        "user_id": str(pac_valentina.usuario.id),
                        "user_email": pac_valentina.usuario.email,
                        "resource": "Chatbot",
                        "action": "CRISIS_PROTOCOL_ACTIVATED",
                        "details": "Detección de ideación/crisis inminente en chatbot y notificación inmediata a operador"
                    })
                    self.stdout.write(self.style.SUCCESS(f"     [OK] Trazas forenses cifradas grabadas en disco con Fernet."))
                except Exception as audit_err:
                    self.stdout.write(self.style.WARNING(f"     [AVISO] No se pudo escribir traza forense HU-37: {audit_err}"))
