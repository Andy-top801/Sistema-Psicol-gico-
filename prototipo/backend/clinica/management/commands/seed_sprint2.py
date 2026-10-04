import hashlib
from typing import Any
from datetime import date, timedelta
from django.core.management.base import BaseCommand
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
    DerivacionCaso, AuditoriaIA
)
from agenda.models import Cita
from clinica.ia_rules_engine import PreconsultaRulesEngine


class Command(BaseCommand):
    help = "Siembra datos clinicos y eticos exhaustivos para el Incremento Sprint 2 (CU14 a CU19 y HU-35)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            default='centro_esperanza',
            help='Slug o schema_name del tenant donde sembrar los datos (o "all" para todos los tenants activos)'
        )

    def handle(self, *args, **options):
        tenant_arg = options['tenant']
        Tenant = get_tenant_model()

        if tenant_arg == 'all':
            tenants = Tenant.objects.exclude(schema_name='public').filter(activo=True)
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

        for tenant in tenants:
            self.stdout.write(self.style.NOTICE(f"\n========================================================"))
            self.stdout.write(self.style.NOTICE(f"==> Sembrando datos Sprint 2 en: {tenant.nombre} ({tenant.schema_name})"))
            self.stdout.write(self.style.NOTICE(f"========================================================"))
            self.seed_tenant_sprint2(tenant)

        self.stdout.write(self.style.SUCCESS("\n[EXITO] Siembra de datos del Sprint 2 finalizada exitosamente.\n"))

    def seed_tenant_sprint2(self, tenant):
        with schema_context(tenant.schema_name):
            atomic_tx: Any = transaction.atomic()
            with atomic_tx:
                # ------------------------------------------------------------------
                # 0. VERIFICAR ACTORES PRINCIPALES (Psicólogos y Pacientes)
                # ------------------------------------------------------------------
                psicologos = list(Psicologo.objects.select_related('usuario').all())
                pacientes = list(Paciente.objects.select_related('usuario').all())

                if not psicologos or not pacientes:
                    self.stdout.write(self.style.WARNING("  [AVISO] No se encontraron suficientes psicologos o pacientes. Ejecute seed_sprint1 primero."))
                    return

                psico_principal = Psicologo.objects.filter(numero_colegiado="COL-PSI-4589").first() or psicologos[0]
                psico_secundario = Psicologo.objects.filter(numero_colegiado="COL-PSI-7821").first() or (psicologos[1] if len(psicologos) > 1 else psico_principal)
                psico_neuro = Psicologo.objects.filter(numero_colegiado="COL-PSI-9340").first() or (psicologos[2] if len(psicologos) > 2 else psico_principal)

                pac_juan = Paciente.objects.filter(ci="8472910-LP").first() or pacientes[0]
                pac_sofia = Paciente.objects.filter(ci="10928374-CB").first() or (pacientes[1] if len(pacientes) > 1 else pac_juan)
                pac_mateo = Paciente.objects.filter(ci="13459872-SC").first() or (pacientes[2] if len(pacientes) > 2 else pac_juan)

                citas = list(Cita.objects.all())

                # ------------------------------------------------------------------
                # 1. CU14 / HU-23, HU-24: FORMULARIOS PRE-CONSULTA E INTAKE DIGITAL
                # ------------------------------------------------------------------
                self.stdout.write("  -> 1. Configurando Cuestionarios Pre-Consulta (Intake Digital - CU14)...")
                
                preguntas_intake_1 = [
                    {
                        "id": "p_motivo",
                        "texto": "¿Cuál es el motivo principal por el que decide consultar?",
                        "tipo": "texto",
                        "requerido": True
                    },
                    {
                        "id": "p_escala",
                        "texto": "En una escala de 1 a 5, ¿cuál es su nivel de malestar o urgencia percibido?",
                        "tipo": "escala_1_5",
                        "requerido": True
                    },
                    {
                        "id": "p_panico",
                        "texto": "¿Ha experimentado opresión en el pecho, palpitaciones o sensación de falta de aire (ataques de pánico)?",
                        "tipo": "booleano",
                        "requerido": True
                    },
                    {
                        "id": "p_insomnio",
                        "texto": "Frecuencia de dificultades para dormir o conciliar el sueño:",
                        "tipo": "opcion_multiple",
                        "opciones": ["Nunca", "1 a 2 días por semana", "Casi todos los días", "Todas las noches"],
                        "requerido": True
                    },
                    {
                        "id": "p_tratamiento_previo",
                        "texto": "¿Ha recibido atención psicológica o psiquiátrica previa?",
                        "tipo": "booleano",
                        "requerido": False
                    }
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
                else:
                    form_intake_gral.preguntas_schema = preguntas_intake_1
                    form_intake_gral.activo = True
                    form_intake_gral.save()

                preguntas_intake_2 = [
                    {
                        "id": "p_animo",
                        "texto": "En las últimas 2 semanas, ¿con qué frecuencia ha sentido tristeza o desánimo?",
                        "tipo": "opcion_multiple",
                        "opciones": ["Rara vez", "Varios días", "Más de la mitad de los días", "Casi a diario"],
                        "requerido": True
                    },
                    {
                        "id": "p_intensidad",
                        "texto": "Nivel de interferencia emocional en su trabajo o estudio (1 a 5)",
                        "tipo": "escala_1_5",
                        "requerido": True
                    },
                    {
                        "id": "p_red_apoyo",
                        "texto": "¿Cuenta con familiares o personas de confianza a quienes recurrir en caso de crisis?",
                        "tipo": "booleano",
                        "requerido": True
                    }
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
                else:
                    form_intake_animo.preguntas_schema = preguntas_intake_2
                    form_intake_animo.activo = True
                    form_intake_animo.save()

                # Respuestas Pre-Consulta de Pacientes
                cita_juan = citas[0] if citas else None
                cita_sofia = citas[1] if len(citas) > 1 else None

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

                resp_sofia = RespuestaPreConsulta.objects.filter(paciente=pac_sofia, formulario=form_intake_gral).first()
                if not resp_sofia:
                    resp_sofia = RespuestaPreConsulta.objects.create(
                        paciente=pac_sofia,
                        formulario=form_intake_gral,
                        cita=cita_sofia,
                        motivo_consulta="Sensación persistente de agotamiento, pérdida de interés en la universidad y tristeza profunda.",
                        sintomas_principales="Apatía, llanto esporádico, dificultad para concentrarse y anhedonia.",
                        nivel_urgencia_percibido=3,
                        antecedentes_medicos="Hipotiroidismo subclínico en tratamiento con Levotiroxina 50mcg.",
                        antecedentes_psiquiatricos="Acompañamiento psicológico breve en 2024 por duelo familiar.",
                        medicacion_actual="Levotiroxina 50mcg / día.",
                        respuestas_detalle={
                            "p_motivo": "Sensación persistente de agotamiento y pérdida de interés en la universidad.",
                            "p_escala": 3,
                            "p_panico": False,
                            "p_insomnio": "1 a 2 días por semana",
                            "p_tratamiento_previo": True
                        },
                        estado="ENVIADO"
                    )

                if len(pacientes) > 3:
                    pac_urgencia = pacientes[3]
                    if not RespuestaPreConsulta.objects.filter(paciente=pac_urgencia, formulario=form_intake_gral).exists():
                        RespuestaPreConsulta.objects.create(
                            paciente=pac_urgencia,
                            formulario=form_intake_gral,
                            motivo_consulta="Flashbacks intrusivos y sobresalto extremo tras sufrir accidente de tránsito.",
                            sintomas_principales="Pesadillas vívidas, evitación fóbica de vehículos e hipervigilancia intensa.",
                            nivel_urgencia_percibido=5,
                            antecedentes_medicos="Politraumatismo leve resuelto.",
                            antecedentes_psiquiatricos="Sin antecedentes.",
                            medicacion_actual="Analgésicos según requerimiento.",
                            respuestas_detalle={
                                "p_motivo": "Flashbacks intrusivos y sobresalto extremo.",
                                "p_escala": 5,
                                "p_panico": True,
                                "p_insomnio": "Todas las noches",
                                "p_tratamiento_previo": False
                            },
                            estado="ENVIADO"
                        )

                self.stdout.write(self.style.SUCCESS(f"     [OK] Formularios pre-consulta y respuestas registradas."))

                # ------------------------------------------------------------------
                # 2. HU-35: MOTOR DE REGLAS CLÍNICAS IA (ROMERO) Y AUDITORÍA ÉTICA
                # ------------------------------------------------------------------
                self.stdout.write("  -> 2. Evaluando Asistente Piloto IA (HU-35 - Reglas Dr. Romero)...")

                analisis_ia_juan = PreconsultaRulesEngine.evaluar_preconsulta(resp_juan)
                if not AuditoriaIA.objects.filter(formulario_respuesta_id=resp_juan.id).exists():
                    AuditoriaIA.objects.create(
                        formulario_respuesta_id=resp_juan.id,
                        psicologo=psico_principal,
                        hash_prompt=analisis_ia_juan['hash_prompt'],
                        resumen_generado=analisis_ia_juan['resumen_generado'],
                        prioridad_sugerida=analisis_ia_juan['prioridad_sugerida'],
                        reglas_aplicadas=analisis_ia_juan['reglas_aplicadas'],
                        evaluacion_humana="EDITADO",
                        observaciones_profesional="Se valida sugerencia asistiva. Cuadro compatible con crisis de angustia / pánico reactivo a sobrecarga laboral. Se programa sesión prioritaria.",
                        fecha_decision=timezone.now(),
                        ip_origen="192.168.1.45"
                    )

                analisis_ia_sofia = PreconsultaRulesEngine.evaluar_preconsulta(resp_sofia)
                if not AuditoriaIA.objects.filter(formulario_respuesta_id=resp_sofia.id).exists():
                    AuditoriaIA.objects.create(
                        formulario_respuesta_id=resp_sofia.id,
                        psicologo=psico_principal,
                        hash_prompt=analisis_ia_sofia['hash_prompt'],
                        resumen_generado=analisis_ia_sofia['resumen_generado'],
                        prioridad_sugerida=analisis_ia_sofia['prioridad_sugerida'],
                        reglas_aplicadas=analisis_ia_sofia['reglas_aplicadas'],
                        evaluacion_humana="PENDIENTE",
                        observaciones_profesional="",
                        ip_origen="192.168.1.50"
                    )

                self.stdout.write(self.style.SUCCESS(f"     [OK] Registros de auditoría IA generados (Supervisión humana verificada)."))

                # ------------------------------------------------------------------
                # 3. CU15 / HU-25, HU-26: HISTORIAS CLÍNICAS (EHR) Y DIAGNÓSTICOS CIE-10
                # ------------------------------------------------------------------
                self.stdout.write("  -> 3. Aperturando Historias Clínicas Electrónicas y Diagnósticos CIE-10 (CU15)...")

                # HC 1: Juan Pérez Morales
                hc_juan = HistoriaClinica.objects.filter(paciente=pac_juan).first()
                if not hc_juan:
                    cod1 = f"HC-{tenant.slug.upper()[:4]}-2026-0001"
                    hc_juan = HistoriaClinica.objects.filter(codigo_historia=cod1).first()
                    if not hc_juan:
                        hc_juan = HistoriaClinica.objects.create(
                            paciente=pac_juan,
                            psicologo_apertura=psico_principal,
                            codigo_historia=cod1,
                            motivo_consulta_inicial="Episodios agudos de ansiedad, hiperventilación y sensación inminente de colapso físico desencadenados en entorno laboral.",
                            antecedentes_personales="No patológicos: Sedentarismo moderado, ingesta de 3 tazas de café diarias. Patológicos: Sin enfermedades crónicas conocidas.",
                            antecedentes_familiares="Madre con antecedentes de trastorno de pánico tratado en la adultez temprana.",
                            historia_evolutiva="Paciente refiere inicio del cuadro hace 4 meses tras ascenso laboral con incremento drástico de responsabilidades. El primer episodio ocurrió en una reunión directiva con temblor distal y sensación de asfixia.",
                            examen_mental_inicial="Paciente lúcido, orientado en las tres esferas. Discurso coherente y fluido pero acelerado al relatar los síntomas somáticos. Afecto ansioso, reactivo. Sin alteraciones sensoperceptivas ni ideación autolítica.",
                            plan_tratamiento="Terapia Cognitivo-Conductual (TCC) focalizada en: 1) Psicoeducación sobre el pánico, 2) Respiración diafragmática lenta, 3) Reestructuración de interpretaciones catastróficas, 4) Exposición interoceptiva gradual.",
                            cerrada=False
                        )

                # Diagnósticos CIE-10 para Juan
                DiagnosticoCIE.objects.get_or_create(
                    historia_clinica=hc_juan,
                    codigo_cie="F41.1",
                    defaults={
                        "descripcion": "Trastorno de ansiedad generalizada",
                        "tipo": "CONFIRMADO",
                        "observaciones": "Cumple criterios de preocupación excesiva, tensión muscular e insomnio por más de 6 meses.",
                        "fecha_diagnostico": date.today() - timedelta(days=20)
                    }
                )
                DiagnosticoCIE.objects.get_or_create(
                    historia_clinica=hc_juan,
                    codigo_cie="F41.0",
                    defaults={
                        "descripcion": "Trastorno de pánico (ansiedad episódica paroxística)",
                        "tipo": "CONFIRMADO",
                        "observaciones": "Ataques de pánico imprevistos con sintomatología adrenérgica aguda.",
                        "fecha_diagnostico": date.today() - timedelta(days=20)
                    }
                )

                # HC 2: Sofía Castro Vega
                hc_sofia = HistoriaClinica.objects.filter(paciente=pac_sofia).first()
                if not hc_sofia:
                    cod2 = f"HC-{tenant.slug.upper()[:4]}-2026-0002"
                    hc_sofia = HistoriaClinica.objects.filter(codigo_historia=cod2).first()
                    if not hc_sofia:
                        hc_sofia = HistoriaClinica.objects.create(
                            paciente=pac_sofia,
                            psicologo_apertura=psico_principal,
                            codigo_historia=cod2,
                            motivo_consulta_inicial="Decaimiento anímico prolongado, rumiación pesimista y baja energía con repercusión en rendimiento académico universitario.",
                            antecedentes_personales="Hipotiroidismo controlado con tratamiento farmacológico sustitutivo.",
                            antecedentes_familiares="Tía materna con trastorno depresivo recurrente.",
                            historia_evolutiva="Cuadro insidioso de aproximadamente 6 meses de evolución caracterizado por anhedonia y postergación recurrente de metas académicas.",
                            examen_mental_inicial="Presentación cuidada, lenguaje de tono bajo, bradipsiquia leve. Expresión facial melancólica con llanto fácil durante el relato. Insight adecuado.",
                            plan_tratamiento="Terapia Cognitiva de Beck y Activación Conductual: Registro diario de actividades placenteras y de dominio, reatribución cognitiva y técnica de resolución de problemas.",
                            cerrada=False
                        )

                DiagnosticoCIE.objects.get_or_create(
                    historia_clinica=hc_sofia,
                    codigo_cie="F32.1",
                    defaults={
                        "descripcion": "Episodio depresivo moderado",
                        "tipo": "CONFIRMADO",
                        "observaciones": "Presencia de humor depresivo, pérdida de energía y disminución del disfrute.",
                        "fecha_diagnostico": date.today() - timedelta(days=14)
                    }
                )

                # HC 3: Mateo Quispe Lima (Menor de edad)
                hc_mateo = HistoriaClinica.objects.filter(paciente=pac_mateo).first()
                if not hc_mateo:
                    cod3 = f"HC-{tenant.slug.upper()[:4]}-2026-0003"
                    hc_mateo = HistoriaClinica.objects.filter(codigo_historia=cod3).first()
                    if not hc_mateo:
                        hc_mateo = HistoriaClinica.objects.create(
                            paciente=pac_mateo,
                            psicologo_apertura=psico_secundario,
                            codigo_historia=cod3,
                            motivo_consulta_inicial="Inquietud motriz constante en clase, dificultad para completar tareas escolares y desobediencia en el hogar.",
                            antecedentes_personales="Parto eutócico a término sin complicaciones neonatales. Hitos del desarrollo psicomotor en rangos esperados.",
                            antecedentes_familiares="Padre con dificultades atencionales no diagnosticadas formalmente en la infancia.",
                            historia_evolutiva="El rendimiento académico se ha visto comprometido en el 6to de primaria debido a impulsividad y distracción fácil ante estímulos irrelevantes.",
                            examen_mental_inicial="Niño colaborador, contacto visual intermitente, inquietud psicomotriz evidente durante la sesión. Pensamiento ágil y coherente.",
                            plan_tratamiento="Entrenamiento conductual para padres y maestros, técnicas de autocontrol y economía de fichas para estructuración de rutinas de estudio.",
                            cerrada=False
                        )

                DiagnosticoCIE.objects.get_or_create(
                    historia_clinica=hc_mateo,
                    codigo_cie="F90.0",
                    defaults={
                        "descripcion": "Perturbación de la actividad y de la atención (TDAH)",
                        "tipo": "CONFIRMADO",
                        "observaciones": "Patrón persistente de inatención e hiperactividad manifestado en más de 2 contextos.",
                        "fecha_diagnostico": date.today() - timedelta(days=10)
                    }
                )
                DiagnosticoCIE.objects.get_or_create(
                    historia_clinica=hc_mateo,
                    codigo_cie="F93.0",
                    defaults={
                        "descripcion": "Trastorno de ansiedad de separación en la niñez",
                        "tipo": "DIFERENCIAL",
                        "observaciones": "A descartar ante quejas somáticas matutinas antes de ingresar a la escuela.",
                        "fecha_diagnostico": date.today() - timedelta(days=10)
                    }
                )

                self.stdout.write(self.style.SUCCESS(f"     [OK] Historias Clínicas aseguradas con diagnósticos CIE-10."))

                # ------------------------------------------------------------------
                # 4. CU16 / HU-27: NOTAS DE SESIÓN CLÍNICAS (MODELO SOAP)
                # ------------------------------------------------------------------
                self.stdout.write("  -> 4. Registrando Notas de Sesión SOAP Estructuradas (CU16)...")

                cita_juan_disp = cita_juan if (cita_juan and not NotaSesion.objects.filter(cita=cita_juan).exists()) else None

                nota_juan_1 = NotaSesion.objects.filter(historia_clinica=hc_juan, numero_sesion=1).first()
                if not nota_juan_1 and cita_juan:
                    nota_juan_1 = NotaSesion.objects.filter(cita=cita_juan).first()

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
                        plan="1. Revisión de autorregistro de pensamientos distorsionados. 2. Identificación de distorsión de catastrofización ('me voy a morir'). 3. Formulación de pensamientos alternativos basados en evidencia.",
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

                cita_sofia_disp = cita_sofia if (cita_sofia and not NotaSesion.objects.filter(cita=cita_sofia).exists()) else None

                nota_sofia_1 = NotaSesion.objects.filter(historia_clinica=hc_sofia, numero_sesion=1).first()
                if not nota_sofia_1 and cita_sofia:
                    nota_sofia_1 = NotaSesion.objects.filter(cita=cita_sofia).first()

                if not nota_sofia_1:
                    nota_sofia_1 = NotaSesion.objects.create(
                        historia_clinica=hc_sofia,
                        numero_sesion=1,
                        cita=cita_sofia_disp,
                        psicologo=psico_principal,
                        fecha_sesion=timezone.now() - timedelta(days=5),
                        subjetivo="Paciente relata: 'Me cuesta levantarme de la cama y siento que he perdido el rumbo. Nada de lo que antes me gustaba me genera satisfacción'.",
                        objetivo="Tono de voz pausado, contacto visual esquivo al inicio, afecto apagado de cualidad depresiva. Sin ideación delirante ni suicida.",
                        analisis="Episodio depresivo moderado reactivo con componentes de aislamiento social y reforzamiento negativo del reposo excesivo.",
                        plan="1. Introducción al modelo de Activación Conductual. 2. Monitoreo diario de actividades y calificación de placer (P) y dominio (D) en escala de 1 a 10. 3. Pactar caminata matutina de 15 minutos.",
                        tecnicas_aplicadas="Activación Conductual, Programación de Actividades",
                        conducta_observada="Receptiva al encuadre aunque con expectativas moderadas de eficacia inicial.",
                        estado_guardado="FIRMADA",
                        fecha_firma=timezone.now() - timedelta(days=5)
                    )

                self.stdout.write(self.style.SUCCESS(f"     [OK] Notas de Sesión SOAP registradas (Firmadas y en Borrador con Autosave)."))

                # ------------------------------------------------------------------
                # 5. CU17 / HU-28, HU-29, HU-30: EVOLUCIÓN LONGITUDINAL Y TAREAS
                # ------------------------------------------------------------------
                self.stdout.write("  -> 5. Prescribiendo Tareas Terapéuticas y Registrando Evolución Longitudinal (CU17)...")

                if not EvolucionClinica.objects.filter(historia_clinica=hc_juan, nota_sesion=nota_juan_2).exists():
                    EvolucionClinica.objects.create(
                        historia_clinica=hc_juan,
                        nota_sesion=nota_juan_2,
                        estado_avance="PROGRESO_NOTABLE",
                        justificacion="El paciente logró abortar un ataque de pánico incipiente aplicando respiración diafragmática sin abandonar el puesto de trabajo.",
                        acuerdos_pactados="Mantener registro de pensamientos y realizar 2 prácticas diafragmáticas preventivas diarias."
                    )

                if not EvolucionClinica.objects.filter(historia_clinica=hc_sofia, nota_sesion=nota_sofia_1).exists():
                    EvolucionClinica.objects.create(
                        historia_clinica=hc_sofia,
                        nota_sesion=nota_sofia_1,
                        estado_avance="EN_PROCESO",
                        justificacion="Inicio de tratamiento. Se acordó la línea base de actividades y compromiso de no permanencia en cama posterior a las 08:30.",
                        acuerdos_pactados="Completar la planilla de actividades placenteras y caminar 15 minutos en las mañanas."
                    )

                # Tareas Terapéuticas
                tarea_juan_1 = TareaTerapeutica.objects.filter(historia_clinica=hc_juan, titulo__icontains="Autorregistro").first()
                if not tarea_juan_1:
                    tarea_juan_1 = TareaTerapeutica.objects.create(
                        historia_clinica=hc_juan,
                        psicologo=psico_principal,
                        paciente=pac_juan,
                        titulo="Autorregistro de Pensamientos Automáticos ante la Ansiedad",
                        descripcion="Registrar en la planilla: 1) Situación desencadenante, 2) Emoción y nivel (0-100), 3) Pensamiento automático, 4) Pensamiento alternativo racional.",
                        categoria="AUTOREGISTRO",
                        fecha_limite=date.today() + timedelta(days=4),
                        estado="COMPLETADA"
                    )
                if not hasattr(tarea_juan_1, 'evidencia') or not tarea_juan_1.evidencia:
                    EvidenciaTarea.objects.get_or_create(
                        tarea=tarea_juan_1,
                        defaults={
                            "texto_reflexion": "Logré identificar que cuando mi superior me llamó imprevisto pensé inmediatamente: 'Me van a despedir y me dará un ataque'. Al cuestionarlo recordé que las evaluaciones trimestrales siempre fueron excelentes, lo cual calmó mi taquicardia.",
                            "dificultad_percibida": 3
                        }
                    )

                if not TareaTerapeutica.objects.filter(historia_clinica=hc_juan, titulo__icontains="Respiración Diafragmática").exists():
                    TareaTerapeutica.objects.create(
                        historia_clinica=hc_juan,
                        psicologo=psico_principal,
                        paciente=pac_juan,
                        titulo="Práctica Diaria de Respiración Diafragmática (10 min)",
                        descripcion="Realizar 2 series diarias de 10 minutos de respiración lenta (4 seg inhalar, 2 sostener, 6 exhalar) antes del almuerzo y al finalizar la jornada laboral.",
                        categoria="MINDFULNESS",
                        fecha_limite=date.today() + timedelta(days=6),
                        estado="PENDIENTE"
                    )

                if not TareaTerapeutica.objects.filter(historia_clinica=hc_sofia, titulo__icontains="Activación Conductual").exists():
                    TareaTerapeutica.objects.create(
                        historia_clinica=hc_sofia,
                        psicologo=psico_principal,
                        paciente=pac_sofia,
                        titulo="Planilla Semanal de Activación Conductual",
                        descripcion="Calificar cada bloque de 2 horas con valores del 1 al 10 en: Nivel de Placer (P) y Nivel de Logro o Dominio (D).",
                        categoria="CONDUCTUAL",
                        fecha_limite=date.today() + timedelta(days=5),
                        estado="PENDIENTE"
                    )

                if not TareaTerapeutica.objects.filter(historia_clinica=hc_mateo, titulo__icontains="Estrellas de Conducta").exists():
                    TareaTerapeutica.objects.create(
                        historia_clinica=hc_mateo,
                        psicologo=psico_secundario,
                        paciente=pac_mateo,
                        titulo="Cuadro de Estrellas de Conducta Escolar",
                        descripcion="Completar la cartilla de metas diarias con la profesora de curso y la tutora en casa.",
                        categoria="CONDUCTUAL",
                        fecha_limite=date.today() - timedelta(days=2),
                        estado="VENCIDA"
                    )

                self.stdout.write(self.style.SUCCESS(f"     [OK] Tareas terapéuticas inter-sesión y evidencias de adherencia creadas."))

                # ------------------------------------------------------------------
                # 6. CU18 / HU-31, HU-32: PLANTILLAS Y FIRMAS DE CONSENTIMIENTO DIGITAL
                # ------------------------------------------------------------------
                self.stdout.write("  -> 6. Generando Plantillas y Firmas de Consentimiento Informado con SHA-256 (CU18)...")

                plantilla_gral, _ = ConsentimientoInformado.objects.get_or_create(
                    tipo="ATENCION_GENERAL",
                    defaults={
                        "titulo": "Consentimiento Informado para Tratamiento Psicoterapéutico General",
                        "version": "v1.0",
                        "contenido_legal": (
                            "Yo, {PACIENTE_NOMBRE}, con Documento de Identidad {PACIENTE_CI}, declaro de manera libre, consciente y voluntaria que he sido informado/a adecuadamente por el profesional tratante {PSICOLOGO_CABECERA} acerca de los objetivos, alcance, metodología, duración estimada y encuadre del proceso psicoterapéutico que inicio en {CENTRO_NOMBRE}.\n\n"
                            "Comprendo que la confidencialidad de la información compartida en sesión está amparada por el secreto profesional y el Código de Ética Psicológica, salvo en situaciones excepcionales tipificadas por ley: a) Riesgo inminente y grave para mi propia vida o integridad física, b) Riesgo inminente para la vida o integridad de terceras personas, c) Requerimiento judicial formal expedido por autoridad competente.\n\n"
                            "Acepto las normas del centro sobre puntualidad, cancelación de citas con 24 horas de anticipación y aranceles profesionales acordados."
                        ),
                        "activo": True
                    }
                )

                plantilla_tele, _ = ConsentimientoInformado.objects.get_or_create(
                    tipo="TELEPSICOLOGIA",
                    defaults={
                        "titulo": "Consentimiento Específico para Servicios de Telepsicología y Videoatención Cifrada",
                        "version": "v1.0",
                        "contenido_legal": (
                            "Yo, {PACIENTE_NOMBRE}, con CI {PACIENTE_CI}, acepto recibir atención psicológica a distancia mediante la plataforma de teleconsulta segura de SIGEPSI con {PSICOLOGO_CABECERA}.\n\n"
                            "Reconozco que la sesión cuenta con cifrado extremo a extremo. Me comprometo a conectarme desde un entorno privado, libre de interrupciones, y declaro conocer que está prohibida la grabación de audio o video de las sesiones sin consentimiento expreso por escrito de ambas partes."
                        ),
                        "activo": True
                    }
                )

                plantilla_menor, _ = ConsentimientoInformado.objects.get_or_create(
                    tipo="MENORES_EDAD",
                    defaults={
                        "titulo": "Autorización Legal de Tratamiento y Evaluación Psicológica para Menores de Edad",
                        "version": "v1.0",
                        "contenido_legal": (
                            "Yo, {TUTOR_NOMBRE}, con Cédula de Identidad {TUTOR_CI}, en mi condición legal y acreditada de madre/padre/tutor(a) legal del menor {PACIENTE_NOMBRE}, autorizo formalmente su evaluación y atención psicoterapéutica con el equipo profesional de {CENTRO_NOMBRE}.\n\n"
                            "Declaro haber recibido orientación detallada sobre los procedimientos de evaluación diagnóstica infanto-juvenil."
                        ),
                        "activo": True
                    }
                )

                plantilla_ia, _ = ConsentimientoInformado.objects.get_or_create(
                    tipo="DATOS_SENSIBLES",
                    defaults={
                        "titulo": "Consentimiento Informado para Tratamiento de Datos Sensibles y Asistencia Tecnológica",
                        "version": "v1.0",
                        "contenido_legal": (
                            "Yo, {PACIENTE_NOMBRE}, autorizo a {CENTRO_NOMBRE} al almacenamiento seguro de mi expediente de salud mental bajo los estándares de la Ley de Protección de Datos Personales. Autorizo el análisis asistivo previo de cuestionarios bajo supervisión humana obligatoria y sin diagnóstico automático."
                        ),
                        "activo": True
                    }
                )

                # Firmas de Consentimiento Digitales con Sello Criptográfico SHA-256
                texto_firma_juan = f"Yo, {pac_juan.usuario.nombre} {pac_juan.usuario.apellido}, con CI {pac_juan.ci}, acepto tratamiento con {psico_principal.usuario.nombre} {psico_principal.usuario.apellido} en {tenant.nombre}."
                hash_juan = hashlib.sha256(texto_firma_juan.encode('utf-8')).hexdigest()

                if not FirmaConsentimiento.objects.filter(paciente=pac_juan, consentimiento=plantilla_gral).exists():
                    FirmaConsentimiento.objects.create(
                        paciente=pac_juan,
                        consentimiento=plantilla_gral,
                        firmado_por=f"{pac_juan.usuario.nombre} {pac_juan.usuario.apellido}",
                        es_menor_edad=False,
                        hash_sha256=hash_juan,
                        ip_origen="192.168.1.45",
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) SIGEPSI-Web/2.0",
                        fecha_firma=timezone.now() - timedelta(days=21)
                    )

                texto_firma_sofia = f"Yo, {pac_sofia.usuario.nombre} {pac_sofia.usuario.apellido}, con CI {pac_sofia.ci}, acepto telepsicología con {psico_principal.usuario.nombre} en {tenant.nombre}."
                hash_sofia = hashlib.sha256(texto_firma_sofia.encode('utf-8')).hexdigest()

                if not FirmaConsentimiento.objects.filter(paciente=pac_sofia, consentimiento=plantilla_tele).exists():
                    FirmaConsentimiento.objects.create(
                        paciente=pac_sofia,
                        consentimiento=plantilla_tele,
                        firmado_por=f"{pac_sofia.usuario.nombre} {pac_sofia.usuario.apellido}",
                        es_menor_edad=False,
                        hash_sha256=hash_sofia,
                        ip_origen="190.181.25.10",
                        user_agent="Dart/3.3 (dart:io) Flutter-SIGEPSI/2.1",
                        fecha_firma=timezone.now() - timedelta(days=14)
                    )

                tutora_nombre = pac_mateo.tutor_legal_nombre or "Beatriz Lima Flores"
                tutora_ci = pac_mateo.tutor_legal_ci or "4892301-SC"
                texto_firma_mateo = f"Yo, {tutora_nombre}, CI {tutora_ci}, autorizo a {pac_mateo.usuario.nombre} {pac_mateo.usuario.apellido} en {tenant.nombre}."
                hash_mateo = hashlib.sha256(texto_firma_mateo.encode('utf-8')).hexdigest()

                if not FirmaConsentimiento.objects.filter(paciente=pac_mateo, consentimiento=plantilla_menor).exists():
                    FirmaConsentimiento.objects.create(
                        paciente=pac_mateo,
                        consentimiento=plantilla_menor,
                        firmado_por=tutora_nombre,
                        es_menor_edad=True,
                        tutor_nombre=tutora_nombre,
                        tutor_ci=tutora_ci,
                        hash_sha256=hash_mateo,
                        ip_origen="192.168.1.60",
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) SIGEPSI-Web/2.0",
                        fecha_firma=timezone.now() - timedelta(days=11)
                    )

                self.stdout.write(self.style.SUCCESS(f"     [OK] Plantillas legales y firmas criptográficas SHA-256 registradas."))

                # ------------------------------------------------------------------
                # 7. CU19 / HU-33, HU-34: CIERRE DE CASO Y DERIVACIONES MÉDICAS
                # ------------------------------------------------------------------
                self.stdout.write("  -> 7. Registrando Protocolos de Cierre y Órdenes de Derivación Psiquiátrica (CU19)...")

                # Derivación 1: Interconsulta Psiquiátrica Externa (Urgencia)
                if not DerivacionCaso.objects.filter(historia_clinica=hc_juan, tipo_derivacion="EXTERNA_PSIQUIATRIA").exists():
                    DerivacionCaso.objects.create(
                        historia_clinica=hc_juan,
                        tipo_derivacion="EXTERNA_PSIQUIATRIA",
                        psicologo_emisor=psico_principal,
                        motivo_clinico="Interconsulta médica para evaluación de tratamiento psicofarmacológico coadyuvante (ISRS) debido a la frecuencia y severidad de las crisis de pánico.",
                        sintomatologia_relevante="Crisis de pánico paroxísticas con cortejo autonómico intenso (taquicardia, opresión torácica) y agorafobia incipiente.",
                        profesional_destino="Dr. Hugo Gómez Mercado (Médico Psiquiatra)",
                        institucion_destino="Hospital San Juan de Dios - Servicio de Salud Mental",
                        nivel_riesgo="ALTO",
                        aceptada=True,
                        documento_pdf_url="/media/derivaciones/orden_psiquiatria_juan_perez.pdf"
                    )

                # Derivación 2: Interconsulta Interna a Neuropsicología para Mateo
                if not DerivacionCaso.objects.filter(historia_clinica=hc_mateo, tipo_derivacion="INTERNA_COLEGA").exists():
                    DerivacionCaso.objects.create(
                        historia_clinica=hc_mateo,
                        tipo_derivacion="INTERNA_COLEGA",
                        psicologo_emisor=psico_secundario,
                        motivo_clinico="Derivación interna al servicio de Neuropsicología para aplicación de batería psicométrica WISC-V y perfil de funciones ejecutivas.",
                        sintomatologia_relevante="Inquietud motora, distractibilidad severa y desinhibición conductual.",
                        profesional_destino=f"Dr. {psico_neuro.usuario.nombre} {psico_neuro.usuario.apellido}",
                        institucion_destino=f"{tenant.nombre} - Área de Neuropsicología",
                        nivel_riesgo="MEDIO",
                        aceptada=True,
                        documento_pdf_url=""
                    )

                # Caso 3: Paciente con Alta Terapéutica formal (Cierre de Caso)
                # Buscar paciente por CI '9182736-OR' o crearlo
                pac_alta = Paciente.objects.filter(ci="9182736-OR").first()
                if not pac_alta:
                    domain_clean = tenant.slug.replace('_', '')
                    rol_paciente = Rol.objects.filter(nombre__icontains="Paciente").first()
                    u_alta = Usuario.objects.filter(email=f"diego.alarcon@{domain_clean}.com").first() or Usuario.objects.filter(email=f"diego.alarcon@{tenant.slug}.com").first()
                    if not u_alta:
                        u_alta = Usuario.objects.create_user(
                            email=f"diego.alarcon@{domain_clean}.com",
                            password="Paciente123*",
                            nombre="Diego",
                            apellido="Alarcón Siles",
                            telefono="78129034",
                            rol=rol_paciente,
                            activo=True
                        )
                    pac_alta = Paciente.objects.create(
                        usuario=u_alta,
                        codigo_expediente=f"EXP-{tenant.slug.upper()[:4]}-005",
                        ci="9182736-OR",
                        fecha_nacimiento=date(1981, 4, 18),
                        genero="M",
                        contacto_emergencia_nombre="Patricia Siles (Hermana)",
                        contacto_emergencia_telf="72110033"
                    )

                hc_alta = HistoriaClinica.objects.filter(paciente=pac_alta).first()
                if not hc_alta:
                    hc_alta = HistoriaClinica.objects.create(
                        paciente=pac_alta,
                        psicologo_apertura=psico_principal,
                        codigo_historia=f"HC-{tenant.slug.upper()[:4]}-2026-ALTA",
                        motivo_consulta_inicial="Fobia social circunscrita a exposiciones públicas y presentaciones académicas.",
                        plan_tratamiento="Tratamiento TCC de 16 sesiones con exposición en vivo y desensibilización sistemática.",
                        cerrada=True,
                        fecha_cierre=timezone.now() - timedelta(days=3)
                    )
                else:
                    hc_alta.cerrada = True
                    hc_alta.fecha_cierre = timezone.now() - timedelta(days=3)
                    hc_alta.save()

                if not DerivacionCaso.objects.filter(historia_clinica=hc_alta, tipo_derivacion="CIERRE_ALTA").exists():
                    DerivacionCaso.objects.create(
                        historia_clinica=hc_alta,
                        tipo_derivacion="CIERRE_ALTA",
                        psicologo_emisor=psico_principal,
                        motivo_clinico="Alta Terapéutica por consecución completa de los objetivos terapéuticos. Reducción sostenida del malestar situacional al 100%.",
                        sintomatologia_relevante="Asintomático. Desenvolvimiento social y laboral óptimo.",
                        profesional_destino="N/A (Cierre de Expediente)",
                        institucion_destino=f"{tenant.nombre}",
                        nivel_riesgo="BAJO",
                        aceptada=True,
                        documento_pdf_url="/media/derivaciones/acta_alta_diego_alarcon.pdf"
                    )

                self.stdout.write(self.style.SUCCESS(f"     [OK] Derivación psiquiátrica externa, derivación interna y Alta Terapéutica (Caso cerrado) registradas."))
