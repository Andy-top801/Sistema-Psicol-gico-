# ==============================================================================
# TEST SUITE: test_fase1_intake.py
# FASE 1: Formulario Pre-Consulta e Intake Digital JSONB (SP2-35 / HU-23 / CU14)
# RESPONSABLE: Andy Mauricio Mújica Vallejos
# ==============================================================================
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')
django.setup()

from django_tenants.utils import schema_context
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from accounts.models import Usuario, Rol
from tenants.models import Tenant
from clinica.models import Paciente, Psicologo, FormularioPreConsulta, RespuestaPreConsulta
from clinica.validators import validar_esquema_preguntas, validar_respuestas_contra_esquema
from clinica.serializers import FormularioPreConsultaSerializer, RespuestaPreConsultaSerializer
from agenda.models import Cita
from agenda.serializers import CitaSerializer


def run_tests():
    print("=" * 80)
    print("INICIANDO TEST SUITE FASE 1: INTAKE DIGITAL Y ESQUEMAS DINÁMICOS JSONB")
    print("=" * 80)

    tenant = Tenant.objects.filter(activo=True).exclude(schema_name='public').first()
    if not tenant:
        print("[ERROR]: No se encontró ningún tenant activo para pruebas.")
        sys.exit(1)

    print(f"[TENANT]: Utilizando '{tenant.nombre}' (Esquema: {tenant.schema_name})")

    with schema_context(tenant.schema_name):
        # ----------------------------------------------------------------------
        # TEST 1: Validación de Esquema JSONB Válido
        # ----------------------------------------------------------------------
        print("\n[TEST 1]: Validación de Esquema JSONB de Preguntas Válido")
        schema_valido = [
            {'id': 'motivo', 'texto': 'Motivo principal de consulta', 'tipo': 'texto', 'requerido': True},
            {'id': 'ansiedad', 'texto': 'Nivel de malestar emocional (1 a 5)', 'tipo': 'escala_1_5', 'requerido': True},
            {'id': 'panico', 'texto': '¿Ha experimentado crisis de angustia?', 'tipo': 'booleano', 'requerido': False},
            {
                'id': 'frecuencia_sueno',
                'texto': 'Frecuencia de dificultades para dormir',
                'tipo': 'opcion_multiple',
                'opciones': ['Nunca', '1-2 veces por semana', 'Casi a diario'],
                'requerido': True
            },
            {
                'id': 'animo',
                'texto': 'En las últimas 2 semanas, ¿con qué frecuencia se sintió desanimado?',
                'tipo': 'likert',
                'opciones': ['Ningún día', 'Varios días', 'Más de la mitad de los días', 'Casi todos los días'],
                'requerido': True
            }
        ]
        res = validar_esquema_preguntas(schema_valido)
        assert len(res) == 5
        print("  ✓ Esquema con 5 preguntas clínicas de tipos diversos validado exitosamente.")

        # ----------------------------------------------------------------------
        # TEST 2: Rechazo de Esquema con Tipo Inválido o sin Opciones
        # ----------------------------------------------------------------------
        print("\n[TEST 2]: Rechazo de Esquemas Corruptos o Malformados")
        # Tipo no permitido
        try:
            validar_esquema_preguntas([{'id': 'q1', 'texto': '¿Color favorito?', 'tipo': 'color_picker', 'requerido': True}])
            assert False, "Debió rechazar tipo_pregunta inválido"
        except ValidationError as e:
            print(f"  ✓ Tipo inválido rechazado correctamente: {e.detail}")

        # Opciones insuficientes en opcion_multiple
        try:
            validar_esquema_preguntas([{'id': 'q2', 'texto': 'Seleccione', 'tipo': 'opcion_multiple', 'opciones': ['Solo una'], 'requerido': True}])
            assert False, "Debió rechazar opcion_multiple con menos de 2 opciones"
        except ValidationError as e:
            print(f"  ✓ Opciones insuficientes rechazadas correctamente: {e.detail}")

        # IDs duplicados
        try:
            validar_esquema_preguntas([
                {'id': 'mismo_id', 'texto': 'Pregunta A', 'tipo': 'texto', 'requerido': True},
                {'id': 'mismo_id', 'texto': 'Pregunta B', 'tipo': 'texto', 'requerido': True}
            ])
            assert False, "Debió rechazar IDs duplicados"
        except ValidationError as e:
            print(f"  ✓ IDs duplicados rechazados correctamente: {e.detail}")

        # ----------------------------------------------------------------------
        # TEST 3: Creación de Formulario Institucional con FormularioPreConsultaSerializer
        # ----------------------------------------------------------------------
        print("\n[TEST 3]: Persistencia de Formulario Institucional con DRF Serializer")
        form_data = {
            'titulo': 'Cuestionario de Intake Psicológico v2 - Fase 1',
            'version': 'v2.0',
            'descripcion': 'Cuestionario estandarizado previo a la sesión de evaluación.',
            'preguntas_schema': schema_valido,
            'activo': True
        }
        form_serializer = FormularioPreConsultaSerializer(data=form_data)
        assert form_serializer.is_valid(), form_serializer.errors
        form_instancia = form_serializer.save()
        assert form_instancia.id is not None
        rep = form_serializer.to_representation(form_instancia)
        assert rep['preguntas_total'] == 5
        print(f"  ✓ Formulario preconsulta guardado (ID: {form_instancia.id}, Preguntas total: {rep['preguntas_total']})")

        # ----------------------------------------------------------------------
        # TEST 4: Validación Cruzada de Respuestas del Paciente vs. Esquema
        # ----------------------------------------------------------------------
        print("\n[TEST 4]: Validación Cruzada de Respuestas vs. Esquema Dinámico")
        # Faltante campo requerido
        respuestas_incompletas = {
            'motivo': 'Ansiedad y palpitaciones al salir a la calle',
            # Falta 'ansiedad' que es requerido escala_1_5
            'frecuencia_sueno': 'Casi a diario',
            'animo': 'Varios días'
        }
        try:
            validar_respuestas_contra_esquema(form_instancia, respuestas_incompletas)
            assert False, "Debió rechazar por pregunta requerida faltante"
        except ValidationError as e:
            print(f"  ✓ Omisión de campo obligatorio detectada: {e.detail}")

        # Valor fuera de rango para escala_1_5
        respuestas_rango_invalido = {
            'motivo': 'Ansiedad severa',
            'ansiedad': 9,  # Fuera de rango 1-5
            'frecuencia_sueno': 'Casi a diario',
            'animo': 'Casi todos los días'
        }
        try:
            validar_respuestas_contra_esquema(form_instancia, respuestas_rango_invalido)
            assert False, "Debió rechazar valor 9 en escala 1-5"
        except ValidationError as e:
            print(f"  ✓ Escala numérica fuera de rango detectada: {e.detail}")

        # Opción inexistente en opción múltiple
        respuestas_opcion_invalida = {
            'motivo': 'Estrés laboral',
            'ansiedad': 4,
            'frecuencia_sueno': 'Opción inventada que no existe',
            'animo': 'Varios días'
        }
        try:
            validar_respuestas_contra_esquema(form_instancia, respuestas_opcion_invalida)
            assert False, "Debió rechazar opción inexistente"
        except ValidationError as e:
            print(f"  ✓ Opción no permitida rechazada: {e.detail}")

        # Respuestas 100% conformes
        respuestas_validas = {
            'motivo': 'Crisis de pánico agudas y dificultades de sueño intermitente.',
            'ansiedad': 5,
            'panico': True,
            'frecuencia_sueno': 'Casi a diario',
            'animo': 'Casi todos los días'
        }
        respuestas_limpias = validar_respuestas_contra_esquema(form_instancia, respuestas_validas)
        assert len(respuestas_limpias) == 5
        print("  ✓ Respuestas válidas verificadas contra el esquema dinámico.")

        # ----------------------------------------------------------------------
        # TEST 5: Alerta Temprana en Agenda (<24 horas)
        # ----------------------------------------------------------------------
        print("\n[TEST 5]: Alerta Temprana en Agenda ('formulario_pendiente' <24h)")
        paciente = Paciente.objects.select_related('usuario').first()
        psicologo = Psicologo.objects.select_related('usuario').first()
        assert paciente is not None and psicologo is not None

        ahora = timezone.localtime()
        # Cita a 10 horas en el futuro (debe disparar alerta si no hay intake)
        cita_proxima = Cita.objects.create(
            paciente=paciente,
            psicologo=psicologo,
            fecha=ahora.date(),
            hora_inicio=(ahora + timedelta(hours=10)).time(),
            hora_fin=(ahora + timedelta(hours=11)).time(),
            modalidad='PRESENCIAL',
            estado='PROGRAMADA',
            motivo_consulta='Evaluación clínica previa'
        )

        cita_ser = CitaSerializer(cita_proxima)
        assert cita_ser.data['formulario_pendiente'] is True, "Cita a 10h debe tener formulario_pendiente=True"
        assert cita_ser.data['intake_id'] is None
        print(f"  ✓ Cita a 10h sin intake retorna correctamente: formulario_pendiente={cita_ser.data['formulario_pendiente']}")

        # Diligenciar el intake para esa cita
        resp_data = {
            'formulario': form_instancia.id,
            'paciente': paciente.id,
            'cita': cita_proxima.id,
            'motivo_consulta': 'Crisis de pánico y angustia',
            'sintomas_principales': 'Taquicardia, opresión torácica',
            'nivel_urgencia_percibido': 5,
            'respuestas_detalle': respuestas_validas,
            'estado': 'ENVIADO'
        }
        resp_ser = RespuestaPreConsultaSerializer(data=resp_data)
        assert resp_ser.is_valid(), resp_ser.errors
        resp_instancia = resp_ser.save()
        assert resp_instancia.tiene_urgencia_alta is True

        # Volver a serializar la cita: ahora formulario_pendiente debe ser False e intake_id debe estar presente
        cita_ser_actualizada = CitaSerializer(cita_proxima)
        assert cita_ser_actualizada.data['formulario_pendiente'] is False
        assert cita_ser_actualizada.data['intake_id'] == str(resp_instancia.id)
        print(f"  ✓ Tras enviar intake, la cita actualiza: formulario_pendiente={cita_ser_actualizada.data['formulario_pendiente']}, intake_id={cita_ser_actualizada.data['intake_id']}")

        # Cita a 48 horas en el futuro (no debe disparar alerta temprana)
        cita_lejana = Cita.objects.create(
            paciente=paciente,
            psicologo=psicologo,
            fecha=(ahora + timedelta(days=2)).date(),
            hora_inicio=ahora.time(),
            hora_fin=(ahora + timedelta(hours=1)).time(),
            modalidad='VIRTUAL',
            estado='PROGRAMADA',
            motivo_consulta='Seguimiento regular'
        )
        cita_lejana_ser = CitaSerializer(cita_lejana)
        assert cita_lejana_ser.data['formulario_pendiente'] is False, "Cita a >24h no debe estar en alerta temprana"
        print(f"  ✓ Cita a 48h en el futuro: formulario_pendiente={cita_lejana_ser.data['formulario_pendiente']} (Sin alerta prematura)")

    print("\n" + "=" * 80)
    print("¡TODOS LOS TESTS DE LA FASE 1 (INTAKE DINÁMICO JSONB) PASARON CON ÉXITO (5/5)!")
    print("=" * 80)


if __name__ == '__main__':
    run_tests()
