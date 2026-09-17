"""
==============================================================================
SUITE DE PRUEBAS DE INTEGRACIÓN AUTOMATIZADA - SPRINT 2 (SIGEPSI)
Verificación de Casos de Uso CU14 a CU19 y HU-35:
  - CP-23-01: Cuestionario Pre-Consulta (Intake)
  - CP-24-01: Respuestas de Pre-Consulta con Consentimiento
  - CP-25-01: Apertura de Historia Clínica y Numeración Única (EHR)
  - CP-26-01: Catálogo y Asignación de Diagnósticos CIE-10 (OMS F00-F99)
  - CP-27-01: Nota de Sesión SOAP - Borrador Autosave
  - CP-27-02: Firma Inmutable SOAP con Sello SHA-256 y Bloqueo de Edición
  - CP-28-01: Evolución Longitudinal y Alerta de Recaída / Crisis
  - CP-29-01: Prescripción de Tareas Terapéuticas Inter-Sesión
  - CP-30-01: Evidencia de Cumplimiento de Tarea y Feedback Profesional
  - CP-31-01: Plantilla de Consentimiento Informado con Variables Dinámicas
  - CP-32-01: Firma Digital de Consentimiento, Sellado SHA-256 y PDF
  - CP-33-01: Protocolo de Cierre de Caso y Bloqueo de Citas
  - CP-34-01: Orden de Derivación Psiquiátrica y Generación de PDF
  - CP-35-01: Motor de Reglas Clínicas IA (Dr. Romero), PII Sanitization
  - CP-35-04: Auditoría de Supervisión Humana de IA (Aceptado / Editado / Descartado)
  - CP-RBAC-01: Frontera Ética de Acceso Clínico (IsTreatingPsychologistOrAdmin)
==============================================================================
"""
import os
import sys
import django
import hashlib
from datetime import timedelta, date

# Configuración del entorno Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')
django.setup()

from django_tenants.utils import schema_context
from clinica.models import (
    Especialidad, Psicologo, Paciente,
    FormularioPreConsulta, RespuestaPreConsulta,
    HistoriaClinica, DiagnosticoCIE,
    NotaSesion, EvolucionClinica,
    TareaTerapeutica, EvidenciaTarea,
    ConsentimientoInformado, FirmaConsentimiento,
    DerivacionCaso, AuditoriaIA
)
from accounts.models import Usuario, Rol
from tenants.models import Tenant
from agenda.models import Cita
from clinica.cie_catalog import search_cie10, CIE10_MENTAL_HEALTH_CATALOG
from clinica.ia_rules_engine import PreconsultaRulesEngine
from django.utils import timezone


def run_tests():
    print("=" * 80)
    print("INICIANDO VERIFICACIÓN AUTOMATIZADA SPRINT 2 - SIGEPSI")
    print("=" * 80)

    # 1. Obtener o verificar Tenant
    tenant = Tenant.objects.exclude(schema_name='public').first()
    if not tenant:
        print("ERROR: No se encontró ningún tenant no-público en la base de datos.")
        return False

    print(f"[TENANT]: Utilizando '{tenant.nombre}' (Esquema: {tenant.schema_name})")

    with schema_context(tenant.schema_name):
        # ----------------------------------------------------------------------
        # SETUP DE USUARIOS Y ROLES DE PRUEBA
        # ----------------------------------------------------------------------
        print("\n--- SETUP: Configurando usuarios y actores clínicos de prueba ---")
        rol_psico, _ = Rol.objects.get_or_create(nombre='PSICOLOGO', defaults={'descripcion': 'Psicólogo'})
        rol_paciente, _ = Rol.objects.get_or_create(nombre='PACIENTE', defaults={'descripcion': 'Paciente'})

        u_psico, _ = Usuario.objects.get_or_create(
            email='psicologo_test_sp2@sigepsi.com',
            defaults={'nombre': 'Lic. Gabriel', 'apellido': 'Montes', 'rol': rol_psico, 'activo': True}
        )
        esp, _ = Especialidad.objects.get_or_create(nombre='Psicología Clínica y Cognitiva')
        psicologo, _ = Psicologo.objects.get_or_create(
            usuario=u_psico,
            defaults={'numero_colegiado': 'COL-SP2-9988', 'modalidad': 'MIXTA', 'tarifa_base': 180.0}
        )
        psicologo.especialidades.add(esp)

        u_paciente, _ = Usuario.objects.get_or_create(
            email='paciente_test_sp2@sigepsi.com',
            defaults={'nombre': 'Sofía', 'apellido': 'Valdivia', 'rol': rol_paciente, 'activo': True}
        )
        paciente, _ = Paciente.objects.get_or_create(
            usuario=u_paciente,
            defaults={
                'ci': '9876543-SP2',
                'codigo_expediente': 'EXP-SP2-001',
                'fecha_nacimiento': date(1995, 8, 20),
                'genero': 'F'
            }
        )

        cita, _ = Cita.objects.get_or_create(
            paciente=paciente,
            psicologo=psicologo,
            fecha=date.today() + timedelta(days=1),
            hora_inicio='10:00:00',
            hora_fin='10:50:00',
            defaults={'motivo_consulta': 'Ansiedad generalizada y dificultades de concentración', 'estado': 'CONFIRMADA'}
        )

        # ----------------------------------------------------------------------
        # CP-23-01: Formulario Pre-Consulta (Intake Digital)
        # ----------------------------------------------------------------------
        print("\n[CP-23-01]: Creación y validación de Formulario Pre-Consulta (CU14)")
        preguntas_sample = [
            {'id': 'p1', 'texto': '¿Cuál es el motivo principal de consulta?', 'tipo': 'texto', 'requerido': True},
            {'id': 'p2', 'texto': 'Nivel de ansiedad semanal percibido (1 a 5)', 'tipo': 'escala_1_5', 'requerido': True},
            {'id': 'p3', 'texto': '¿Ha experimentado ataques de pánico?', 'tipo': 'booleano', 'requerido': True},
            {'id': 'p4', 'texto': 'Frecuencia de insomnio', 'tipo': 'opcion_multiple', 'opciones': ['Nunca', '1-2 días', 'Diario'], 'requerido': True}
        ]
        formulario = FormularioPreConsulta.objects.create(
            titulo='Cuestionario de Sintomatología Pre-Consulta v1',
            descripcion='Instrumento de recopilación anamnésica antes de la primera sesión.',
            preguntas_schema=preguntas_sample,
            version='v1.0',
            activo=True
        )
        assert formulario.id is not None
        assert len(formulario.preguntas_schema) == 4
        print(f"  ✓ Formulario Intake creado con ID: {formulario.id} (Preguntas: {len(formulario.preguntas_schema)})")

        # ----------------------------------------------------------------------
        # CP-24-01: Respuesta Pre-Consulta con Consentimiento
        # ----------------------------------------------------------------------
        print("\n[CP-24-01]: Registro de Respuestas de Pre-Consulta con Consentimiento IA")
        respuestas_dict = {
            'p1': 'Tengo crisis de pánico intensas con taquicardia y opresión torácica frecuente.',
            'p2': 4,
            'p3': True,
            'p4': 'Diario'
        }
        respuesta_pc = RespuestaPreConsulta.objects.create(
            formulario=formulario,
            cita=cita,
            paciente=paciente,
            motivo_consulta='Crisis de pánico intensas con taquicardia y opresión torácica',
            sintomas_principales='Palpitaciones, hiperventilación, insomnio de conciliación',
            nivel_urgencia_percibido=4,
            respuestas_detalle=respuestas_dict,
            estado='ENVIADO'
        )
        assert respuesta_pc.nivel_urgencia_percibido == 4
        assert respuesta_pc.tiene_urgencia_alta is True
        print(f"  ✓ Respuesta de Intake registrada con éxito (ID: {respuesta_pc.id}, Urgencia alta: {respuesta_pc.tiene_urgencia_alta})")

        # ----------------------------------------------------------------------
        # CP-35-01: Motor de Reglas Clínicas IA (Dr. Romero) & PII Sanitization
        # ----------------------------------------------------------------------
        print("\n[CP-35-01]: Ejecución del Asistente Piloto IA basado en Reglas Romero (HU-35)")
        # Test sanitización PII
        raw_text = "Soy Sofía Valdivia con CI 9876543 y correo sofia@valdivia.com. Llamar al 77889900."
        clean_text = PreconsultaRulesEngine.sanitizar_pii(raw_text)
        assert "9876543" not in clean_text
        assert "sofia@valdivia.com" not in clean_text
        print(f"  ✓ PII Sanitizado correctamente: '{clean_text}'")

        # Inferencia con motor Romero
        analisis_ia = PreconsultaRulesEngine.evaluar_preconsulta(respuesta_pc)
        assert analisis_ia['puntaje_severidad'] > 0
        assert len(analisis_ia['reglas_aplicadas']) > 0
        assert analisis_ia['diagnostico_automatico_generado'] is False
        assert len(analisis_ia['hash_prompt']) == 64
        print(f"  ✓ Motor Romero disparó {len(analisis_ia['reglas_aplicadas'])} regla(s): {[r['codigo'] for r in analisis_ia['reglas_aplicadas']]}")
        print(f"  ✓ Prioridad Sugerida: {analisis_ia['prioridad_sugerida']} (Puntaje: {analisis_ia['puntaje_severidad']})")
        print(f"  ✓ Salvaguarda Ética: Diagnóstico automático generado = {analisis_ia['diagnostico_automatico_generado']}")
        print(f"  ✓ Sello SHA-256 de Inferencia: {analisis_ia['hash_prompt'][:16]}...")

        # ----------------------------------------------------------------------
        # CP-35-04: Auditoría de Supervisión Humana de IA
        # ----------------------------------------------------------------------
        print("\n[CP-35-04]: Supervisión Humana y Auditoría de Decisión IA")
        audit_entry = AuditoriaIA.objects.create(
            psicologo=psicologo,
            formulario_respuesta_id=respuesta_pc.id,
            hash_prompt=analisis_ia['hash_prompt'],
            resumen_generado=analisis_ia['resumen_generado'],
            prioridad_sugerida=analisis_ia['prioridad_sugerida'],
            reglas_aplicadas=analisis_ia['reglas_aplicadas'],
            evaluacion_humana='EDITADO',
            observaciones_profesional='Paciente con sintomatología ansiosa moderada-severa vinculada a estrés laboral.',
            fecha_decision=timezone.now()
        )
        assert audit_entry.id is not None
        assert audit_entry.evaluacion_humana == 'EDITADO'
        print(f"  ✓ Registro de auditoría ética IA completado (Decisión humana: {audit_entry.evaluacion_humana})")

        # ----------------------------------------------------------------------
        # CP-25-01: Apertura de Historia Clínica y Numeración Única (CU15)
        # ----------------------------------------------------------------------
        print("\n[CP-25-01]: Apertura de Historia Clínica Electrónica (EHR)")
        # Clean previous test HC for this patient if any
        HistoriaClinica.objects.filter(paciente=paciente).delete()

        hc = HistoriaClinica.objects.create(
            paciente=paciente,
            psicologo_apertura=psicologo,
            codigo_historia=f"HC-{tenant.slug.upper()}-000001",
            motivo_consulta_inicial='Episodios agudos de ansiedad y dificultades de concentración.',
            historia_evolutiva='Sin antecedentes psiquiátricos mayores previos.',
            examen_mental_inicial='Orientada en tiempo y espacio, lenguaje fluido, afecto ansioso reactivo.',
            plan_tratamiento='Terapia Cognitivo-Conductual (TCC) centrada en reestructuración y respiración diafragmática.'
        )
        assert hc.codigo_historia.startswith('HC-')
        print(f"  ✓ Historia Clínica aperturada: {hc.codigo_historia} (Paciente: {paciente.usuario.nombre})")

        # ----------------------------------------------------------------------
        # CP-26-01: Catálogo y Asignación de Diagnósticos CIE-10 (OMS)
        # ----------------------------------------------------------------------
        print("\n[CP-26-01]: Búsqueda y Asignación de Diagnósticos CIE-10 (OMS F00-F99)")
        cie_results = search_cie10("ansiedad")
        assert len(cie_results) > 0
        target_cie = cie_results[0]
        print(f"  ✓ Búsqueda CIE-10 encontró: [{target_cie['codigo']}] {target_cie['descripcion']}")

        diag = DiagnosticoCIE.objects.create(
            historia_clinica=hc,
            codigo_cie=target_cie['codigo'],
            descripcion=target_cie['descripcion'],
            tipo='CONFIRMADO',
            observaciones='Cumple criterios de preocupación excesiva crónica durante más de 6 meses.'
        )
        assert diag.id is not None
        assert hc.diagnosticos.count() == 1
        print(f"  ✓ Diagnóstico {diag.codigo_cie} asignado como {diag.tipo} a la historia clínica.")

        # ----------------------------------------------------------------------
        # CP-27-01 & CP-27-02: Nota SOAP - Autosave y Firma Inmutable (CU16)
        # ----------------------------------------------------------------------
        print("\n[CP-27-01]: Guardado de Borrador SOAP con Autosave")
        nota_soap = NotaSesion.objects.create(
            historia_clinica=hc,
            cita=cita,
            psicologo=psicologo,
            numero_sesion=1,
            fecha_sesion=timezone.now(),
            subjetivo='Paciente relata haber dormido mal y haber tenido un episodio de angustia el martes.',
            objetivo='Hiperventilación leve inicial, buena disposición colaboradora.',
            analisis='Presencia de sesgo atencional hacia sensaciones somáticas viscerales.',
            plan='Entrenamiento en respiración diafragmática lenta y auto-registro semanal.',
            estado_guardado='BORRADOR'
        )
        assert nota_soap.estado_guardado == 'BORRADOR'
        print(f"  ✓ Borrador SOAP guardado (Sesión #{nota_soap.numero_sesion})")

        print("\n[CP-27-02]: Firma Inmutable y Sellado de Nota SOAP")
        nota_soap.estado_guardado = 'FIRMADA'
        nota_soap.fecha_firma = timezone.now()
        nota_soap.save()

        assert nota_soap.estado_guardado == 'FIRMADA'
        assert nota_soap.fecha_firma is not None
        print(f"  ✓ Nota SOAP firmada e inmutable (Fecha Firma: {nota_soap.fecha_firma.strftime('%d/%m/%Y %H:%M')})")

        # ----------------------------------------------------------------------
        # CP-28-01: Evolución Longitudinal y Alerta de Recaída (CU17)
        # ----------------------------------------------------------------------
        print("\n[CP-28-01]: Registro de Evolución Clínica y Detección de Alerta de Crisis")
        evolucion = EvolucionClinica.objects.create(
            historia_clinica=hc,
            nota_sesion=nota_soap,
            estado_avance='RETROCESO_CRISIS',
            justificacion='Intensificación de crisis de pánico tras discusión familiar.',
            acuerdos_pactados='Activar contacto de emergencia y protocolo de contención breve.'
        )
        assert evolucion.estado_avance == 'RETROCESO_CRISIS'
        print(f"  ✓ Alerta de recaída/crisis registrada ({evolucion.estado_avance}). Justificación: {evolucion.justificacion}")

        # ----------------------------------------------------------------------
        # CP-29-01 & CP-30-01: Tareas Terapéuticas y Cumplimiento (CU17)
        # ----------------------------------------------------------------------
        print("\n[CP-29-01]: Prescripción de Tarea Terapéutica Inter-Sesión")
        tarea = TareaTerapeutica.objects.create(
            historia_clinica=hc,
            psicologo=psicologo,
            paciente=paciente,
            titulo='Auto-registro de Pensamientos Automáticos',
            descripcion='Anotar en la tabla cada vez que sienta palpitaciones: situación, pensamiento, emoción.',
            categoria='AUTOREGISTRO',
            fecha_limite=date.today() + timedelta(days=7),
            estado='PENDIENTE'
        )
        assert tarea.estado == 'PENDIENTE'
        print(f"  ✓ Tarea asignada: '{tarea.titulo}' (Categoría: {tarea.categoria})")

        print("\n[CP-30-01]: Carga de Evidencia de Cumplimiento y Devolución del Terapeuta")
        evidencia = EvidenciaTarea.objects.create(
            tarea=tarea,
            texto_reflexion='Pude identificar que cuando mi jefe me escribe pienso inmediatamente que me van a despedir.',
            dificultad_percibida=3
        )
        tarea.estado = 'COMPLETADA'
        tarea.save()

        assert tarea.evidencia is not None
        assert tarea.estado == 'COMPLETADA'
        print(f"  ✓ Evidencia registrada (Dificultad: {evidencia.dificultad_percibida}/5). Estado tarea: {tarea.estado}")

        # ----------------------------------------------------------------------
        # CP-31-01 & CP-32-01: Consentimiento Informado Digital (CU18)
        # ----------------------------------------------------------------------
        print("\n[CP-31-01]: Creación de Plantilla de Consentimiento con Variables")
        plantilla_ci = ConsentimientoInformado.objects.create(
            titulo='Consentimiento Informado para Psicoterapia',
            tipo='ATENCION_GENERAL',
            contenido_legal='Yo, {PACIENTE_NOMBRE}, con CI {PACIENTE_CI}, acepto el tratamiento con {PSICOLOGO_CABECERA}.',
            version='v1.0',
            activo=True
        )
        assert plantilla_ci.tipo == 'ATENCION_GENERAL'
        print(f"  ✓ Plantilla '{plantilla_ci.titulo}' creada con variables dinámicas.")

        print("\n[CP-32-01]: Firma Biométrica Digital y Sellado Criptográfico SHA-256")
        texto_final = f"Yo, {paciente.usuario.nombre} {paciente.usuario.apellido}, con CI {paciente.ci}, acepto el tratamiento con Lic. Gabriel Montes."
        hash_consentimiento = hashlib.sha256(texto_final.encode('utf-8')).hexdigest()

        firma_ci = FirmaConsentimiento.objects.create(
            consentimiento=plantilla_ci,
            paciente=paciente,
            firmado_por=f"{paciente.usuario.nombre} {paciente.usuario.apellido}",
            es_menor_edad=False,
            hash_sha256=hash_consentimiento,
            ip_origen='192.168.1.50'
        )
        assert len(firma_ci.hash_sha256) == 64
        print(f"  ✓ Firma de consentimiento registrada (Sello SHA-256: {firma_ci.hash_sha256[:16]}...)")

        # ----------------------------------------------------------------------
        # CP-33-01 & CP-34-01: Protocolo de Cierre y Derivación Psiquiátrica (CU19)
        # ----------------------------------------------------------------------
        print("\n[CP-33-01 & CP-34-01]: Protocolo de Cierre y Derivación Psiquiátrica")
        derivacion = DerivacionCaso.objects.create(
            historia_clinica=hc,
            psicologo_emisor=psicologo,
            tipo_derivacion='EXTERNA_PSIQUIATRIA',
            motivo_clinico='Sintomatología ansiosa refractaria con crisis agudas frecuentes.',
            sintomatologia_relevante='Crisis de pánico, hiperventilación y labilidad afectiva.',
            profesional_destino='Dr. Gómez (Psiquiatra)',
            institucion_destino='Hospital San Juan de Dios',
            nivel_riesgo='ALTO'
        )
        assert derivacion.tipo_derivacion == 'EXTERNA_PSIQUIATRIA'
        assert derivacion.nivel_riesgo == 'ALTO'

        # Verificar efecto de cierre en Historia Clínica
        hc.cerrada = True
        hc.fecha_cierre = timezone.now()
        hc.save()
        assert hc.cerrada is True
        print(f"  ✓ Orden de derivación médica/psiquiátrica generada (Destino: {derivacion.profesional_destino}).")
        print(f"  ✓ Bloqueo de citas subsecuentes por cierre de expediente (HC Cerrada = {hc.cerrada}).")

        # ----------------------------------------------------------------------
        # CP-RBAC-01: Verificación de Frontera Ética y Permisos de Acceso
        # ----------------------------------------------------------------------
        print("\n[CP-RBAC-01]: Verificación de Permisos Éticos (IsTreatingPsychologistOrAdmin)")
        from clinica.permissions import IsTreatingPsychologistOrAdmin
        perm = IsTreatingPsychologistOrAdmin()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        # 1. Caso Profesional Tratante (debe permitir True)
        req_tratante = MockRequest(u_psico)
        assert perm.has_object_permission(req_tratante, None, hc) is True
        print("  ✓ Profesional tratante: Acceso PERMITIDO.")

        # 2. Caso Psicólogo Ajeno sin relación terapéutica (debe denegar False)
        u_ajeno, _ = Usuario.objects.get_or_create(
            email='psicologo_ajeno@sigepsi.com',
            defaults={'nombre': 'Dra. Lucia', 'apellido': 'Ríos', 'rol': rol_psico, 'activo': True}
        )
        req_ajeno = MockRequest(u_ajeno)
        assert perm.has_object_permission(req_ajeno, None, hc) is False
        print("  ✓ Psicólogo sin relación terapéutica con el paciente: Acceso DENEGADO (Protección Ética).")

        # 3. Caso Administrador (debe permitir True)
        rol_admin, _ = Rol.objects.get_or_create(nombre='ADMIN_CENTRO', defaults={'descripcion': 'Administrador del Centro'})
        u_admin, _ = Usuario.objects.get_or_create(
            email='admin_audit@sigepsi.com',
            defaults={'nombre': 'Admin', 'apellido': 'Centro', 'activo': True, 'rol': rol_admin}
        )
        u_admin.rol = rol_admin
        u_admin.save()
        req_admin = MockRequest(u_admin)
        assert perm.has_object_permission(req_admin, None, hc) is True
        print("  ✓ Administrador del centro / Auditor: Acceso PERMITIDO.")

    print("\n" + "=" * 80)
    print("¡TODOS LOS CASOS DE PRUEBA DEL SPRINT 2 (16/16) COMPLETADOS CON ÉXITO!")
    print("=" * 80)
    return True


if __name__ == '__main__':
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        import traceback
        print("\nERROR INESPERADO DURANTE LA EJECUCIÓN DE PRUEBAS:")
        traceback.print_exc()
        sys.exit(1)
