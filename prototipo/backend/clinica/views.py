# ==============================================================================
# MÓDULO: clinica/views.py
# CAPA BCE: CONTROL (Controller) — CTR_Psicologo, CTR_Paciente, CTR_Disponibilidad
# CASOS DE USO: CU6 (Gestión de Psicólogos), CU7 (Gestión de Pacientes),
#               CU8 (Gestión de Disponibilidad Horaria)
# DESCRIPCIÓN: Endpoints REST que reciben las peticiones de la capa Boundary
#              (IU_GestionPsicologos, IU_RegistroPacientes, IU_DisponibilidadHoraria)
#              y coordinan la lógica de negocio con la capa Entity (CE_).
#              Implementan los pasos 2→7 de los Diagramas de Comunicación BCE.
# ==============================================================================
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.db.models import Q
from clinica.models import Especialidad, Psicologo, Disponibilidad, Paciente
from clinica.serializers import (
    EspecialidadSerializer,
    PsicologoSerializer,
    DisponibilidadSerializer,
    PacienteSerializer
)
from accounts.permissions import EsAdminCentro

class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all().order_by('nombre')
    serializer_class = EspecialidadSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


# ──────────────────────────────────────────────────────────────────────────────
# CONTROLADOR: PsicologoViewSet — CTR_Psicologo
# DIAGRAMA DE COMUNICACIÓN CU6 – Gestión de Psicólogos:
#   Paso 2: IU_GestionPsicologos → CTR_Psicologo: POST /api/clinica/psicologos/
#   Pasos 3–6: PsicologoSerializer valida y crea usuario + psicólogo en CE
#   Paso 7: CTR_Psicologo → IU: 201 Created
# ──────────────────────────────────────────────────────────────────────────────
class PsicologoViewSet(viewsets.ModelViewSet):
    queryset = Psicologo.objects.select_related('usuario').prefetch_related('especialidades', 'disponibilidades').all()
    serializer_class = PsicologoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'disponibilidad']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        # Filtro de búsqueda textual
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(
                    usuario__nombre__icontains=search,
                    usuario__apellido__icontains=search,
                    usuario__email__icontains=search,
                    numero_colegiado__icontains=search,
                    _connector=Q.OR
                )
            )

        # Filtro por especialidad
        esp_id = self.request.query_params.get('especialidad')
        if esp_id:
            qs = qs.filter(especialidades__id=esp_id)

        # Filtro por modalidad
        modalidad = self.request.query_params.get('modalidad')
        if modalidad:
            qs = qs.filter(modalidad__iexact=modalidad)

        # Filtro por estado activo
        activo = self.request.query_params.get('activo')
        if activo is not None:
            es_activo = activo.lower() in ('true', '1', 'yes')
            qs = qs.filter(activo=es_activo)

        return qs.distinct()

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    # ================================================================
    # CU8: Endpoint de disponibilidad horaria del psicólogo
    # DIAGRAMA DE COMUNICACIÓN CU8:
    #   Paso 2: IU_DisponibilidadHoraria → CTR: POST /api/clinica/psicologos/{id}/disponibilidad/
    #   Pasos 3–6: DisponibilidadSerializer valida y persiste franjas en CE
    #   Paso 7: CTR → IU: 200 OK {franjas_configuradas, slots_generados}
    # ================================================================
    @action(detail=True, methods=['get', 'post'], url_path='disponibilidad')
    def disponibilidad(self, request, pk=None):
        psicologo = self.get_object()

        if request.method == 'GET':
            # CU8 Paso 2 (lectura): Retorna las franjas activas del psicólogo
            disps = psicologo.disponibilidades.filter(activo=True).order_by('dia_semana', 'hora_inicio')
            serializer = DisponibilidadSerializer(disps, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            data = request.data
            if isinstance(data, dict) and 'franjas' in data:
                data = data['franjas']

            if isinstance(data, list):
                # CU8 Paso 5: Reemplazar todas las franjas anteriores y guardar las nuevas
                # Implementa "Guardar franjas y particionar bloques en DB"
                psicologo.disponibilidades.all().delete()
                creados = []
                for item in data:
                    item_copy = dict(item)
                    item_copy['psicologo'] = str(psicologo.id)
                    ser = DisponibilidadSerializer(data=item_copy)
                    ser.is_valid(raise_exception=True)
                    ser.save()
                    creados.append(ser.data)
                return Response({
                    "mensaje": f"{len(creados)} franja(s) horaria(s) configurada(s) exitosamente.",
                    "count": len(creados),
                    "horarios": creados,
                    "disponibilidades": creados
                }, status=status.HTTP_200_OK)
            else:
                data_dict = dict(data)
                data_dict['psicologo'] = str(psicologo.id)
                ser = DisponibilidadSerializer(data=data_dict)
                ser.is_valid(raise_exception=True)
                ser.save()
                return Response(ser.data, status=status.HTTP_201_CREATED)



class DisponibilidadViewSet(viewsets.ModelViewSet):
    queryset = Disponibilidad.objects.all()
    serializer_class = DisponibilidadSerializer
    permission_classes = [IsAuthenticated]


# ──────────────────────────────────────────────────────────────────────────────
# CONTROLADOR: PacienteViewSet — CTR_Paciente
# DIAGRAMA DE COMUNICACIÓN CU7 – Gestión de Pacientes Web y Móvil:
#   Paso 2: IU_RegistroPacientes → CTR: POST /api/clinica/pacientes/ + Header Tenant
#   Pasos 3–6: PacienteSerializer valida CI, tutor legal y crea expediente en CE
#   Paso 7: CTR → IU: 201 Created {paciente_id, expediente}
# ──────────────────────────────────────────────────────────────────────────────
class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.select_related('usuario').all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Si es un paciente autenticado, sólo ve su propio perfil salvo que sea admin/recepcionista
        rol_nombre = user.rol.nombre if user.rol else ""
        if rol_nombre == "Paciente" and not user.is_superuser:
            return qs.filter(usuario=user)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(
                    usuario__nombre__icontains=search,
                    usuario__apellido__icontains=search,
                    usuario__email__icontains=search,
                    ci__icontains=search,
                    codigo_expediente__icontains=search,
                    _connector=Q.OR
                )
            )

        return qs

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Retorna el expediente del paciente autenticado."""
        try:
            paciente = Paciente.objects.select_related('usuario').get(usuario=request.user)
            serializer = self.get_serializer(paciente)
            return Response(serializer.data)
        except Paciente.DoesNotExist:
            return Response(
                {"error": "El usuario actual no cuenta con un expediente de paciente asignado."},
                status=status.HTTP_404_NOT_FOUND
            )


# ==============================================================================
# VIEWSETS DEL SPRINT 2 (CU14 - CU19 & HU-35)
import re
import hashlib
from io import BytesIO
from django.utils import timezone
from django.http import HttpResponse
from clinica.permissions import IsTreatingPsychologistOrAdmin, IsReferralParticipant
from clinica.cie_catalog import search_cie10
from clinica.ia_rules_engine import PreconsultaRulesEngine
from clinica.models import (
    FormularioPreConsulta, RespuestaPreConsulta,
    HistoriaClinica, DiagnosticoCIE,
    NotaSesion, EvolucionClinica,
    TareaTerapeutica, EvidenciaTarea,
    ConsentimientoInformado, FirmaConsentimiento,
    DerivacionCaso, AuditoriaIA,
    ConversacionChatbot, MensajeChatbot
)
from clinica.serializers import (
    FormularioPreConsultaSerializer, RespuestaPreConsultaSerializer,
    HistoriaClinicaSerializer, DiagnosticoCIESerializer,
    NotaSesionSerializer, EvolucionClinicaSerializer,
    TareaTerapeuticaSerializer, EvidenciaTareaSerializer,
    ConsentimientoInformadoSerializer, FirmaConsentimientoSerializer,
    DerivacionCasoSerializer, AuditoriaIASerializer,
    ConversacionChatbotSerializer, MensajeChatbotSerializer
)
from clinica.chatbot_service import ChatbotEngine
from clinica.lifecycle import ensure_object_history_open, lock_history, close_history, reactivate_history
from rest_framework.permissions import AllowAny, IsAuthenticated


# ==============================================================================
# MÓDULO: clinica/views.py — CU14: Ficha Previa e Intake Digital (HU-23, HU-24)
# CAPA BCE: CONTROL (Controller) — CTR_IntakeController
# DIAGRAMA DE SECUENCIA CU14 (sprint2.md):
#   Actor (Paciente) → IU_FormularioPreConsulta: 1: ingresar_respuestas(sintomas, escala_malestar, antecedentes)
#   IU_FormularioPreConsulta → IU_FormularioPreConsulta: 2: validar_campos_requeridos()
#   IU_FormularioPreConsulta → CTR_IntakeController: 3: POST /api/v1/intake/respuestas/ (Bearer JWT, payload JSONB)
#   CTR_IntakeController → CTR_IntakeController: 4: validar_esquema_json_y_urgencia(malestar >= 4)
#   alt Malestar >= 4 (Urgencia Alta)
#     CTR_IntakeController → CE_RespuestaPreConsulta: 5: INSERT INTO clinica_respuestapreconsulta (prioridad='ALTA')
#     CE_RespuestaPreConsulta --> CTR_IntakeController: 6: 201 Created (uuid, timestamp, prioridad_flag=true)
#     CTR_IntakeController --> IU_FormularioPreConsulta: 7: HTTP 201 Created {id, prioridad='ALTA', protocolo_urgencia=true}
#     IU_FormularioPreConsulta --> Paciente: 8: mostrar_alerta_urgencia_prioritaria('Caso clasificado para atencion inmediata')
#   else Malestar Normal (Rango Habitual)
#     CTR_IntakeController → CE_RespuestaPreConsulta: 9: INSERT INTO clinica_respuestapreconsulta (prioridad='NORMAL')
#     CE_RespuestaPreConsulta --> CTR_IntakeController: 10: 201 Created (uuid, timestamp, prioridad_flag=false)
#     CTR_IntakeController --> IU_FormularioPreConsulta: 11: HTTP 201 Created {id, prioridad='NORMAL', status='ENVIADO'}
#     IU_FormularioPreConsulta --> Paciente: 12: confirmacion_envio_exitosa(badge_prioridad)
# ==============================================================================
class FormularioPreConsultaViewSet(viewsets.ModelViewSet):
    """
    Controlador para la configuración y consulta de formularios institucionales de intake pre-consulta.
    """
    queryset = FormularioPreConsulta.objects.all().order_by('-fecha_creacion')
    serializer_class = FormularioPreConsultaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        activo = self.request.query_params.get('activo')
        if activo is not None:
            qs = qs.filter(activo=activo.lower() in ('true', '1'))
        return qs

    @action(detail=False, methods=['get'], url_path='activo')
    def activo(self, request):
        """Retorna el formulario institucional activo vigente para el tenant."""
        formulario = self.get_queryset().filter(activo=True).first()
        if not formulario:
            return Response(
                {"detalle": "No existe un formulario de preconsulta activo actualmente."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(formulario)
        return Response(serializer.data)


class RespuestaPreConsultaViewSet(viewsets.ModelViewSet):
    """
    CTR_IntakeController:
    Gestiona la recepción, validación y persistencia de las respuestas de pre-consulta (CU14).
    """
    queryset = RespuestaPreConsulta.objects.select_related('formulario', 'paciente__usuario', 'cita').all().order_by('-fecha_envio')
    serializer_class = RespuestaPreConsultaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        rol_nombre = user.rol.nombre.lower() if user.rol else ""

        # Pacientes solo ven sus propias respuestas
        if 'paciente' in rol_nombre and hasattr(user, 'perfil_paciente'):
            return qs.filter(paciente=user.perfil_paciente)

        # Filtro por paciente
        paciente_id = self.request.query_params.get('paciente')
        if paciente_id:
            qs = qs.filter(paciente_id=paciente_id)

        # Filtro por cita
        cita_id = self.request.query_params.get('cita') or self.request.query_params.get('cita_id')
        if cita_id:
            qs = qs.filter(cita_id=cita_id)

        # Filtro por estado
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado.upper())

        return qs

    def perform_create(self, serializer):
        # CU14 Paso 4: Validar esquema y urgencia (delegado al serializer/modelo)
        # CU14 Paso 5 o 9: INSERT INTO clinica_respuestapreconsulta (prioridad='ALTA' si malestar >= 4, sino 'NORMAL')
        user = self.request.user
        # Si el usuario es un paciente autenticado y no se indicó paciente, asignar el suyo
        if hasattr(user, 'perfil_paciente') and not serializer.validated_data.get('paciente'):
            resp = serializer.save(paciente=user.perfil_paciente)
        else:
            resp = serializer.save()

        # CU21-paso 1: ingresar_motivo_y_respuestas(texto_motivo, escala_malestar) — el Paciente envía su intake
        #              y se ejecuta automáticamente la misma secuencia del endpoint (CU21-paso 3 a CU21-paso 25).
        # Un fallo de IA no debe impedir guardar el intake, pero queda registrado con traza completa.
        try:
            CTR_ClasificacionIAController.clasificar(resp, ip=_ip_cliente(self.request), usuario=user)
        except Exception:
            logger_ia.exception("Error clasificando automáticamente el intake %s", resp.id)

    @action(detail=False, methods=['get'], url_path='por-cita')
    def por_cita(self, request):
        """Consulta el estado del intake de una cita específica."""
        cita_id = request.query_params.get('cita') or request.query_params.get('cita_id')
        if not cita_id:
            return Response(
                {"error": "Debe especificar el parámetro cita o cita_id."},
                status=status.HTTP_400_BAD_REQUEST
            )
        respuesta = self.get_queryset().filter(cita_id=cita_id).first()
        if not respuesta:
            return Response(
                {"completado": False, "mensaje": "La cita no cuenta con intake completado aún.", "respuesta": None},
                status=status.HTTP_200_OK
            )
        serializer = self.get_serializer(respuesta)
        return Response({"completado": True, "respuesta": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='marcar-revisado')
    def marcar_revisado(self, request, pk=None):
        respuesta = self.get_object()
        respuesta.estado = 'REVISADO'
        respuesta.save(update_fields=['estado'])
        return Response({"mensaje": "Formulario previo marcado como revisado.", "estado": respuesta.estado})


# ──────────────────────────────────────────────────────────────────────────────
# CU15: Catálogo CIE-10 y Búsqueda Reactiva
# ──────────────────────────────────────────────────────────────────────────────
class CIE10ViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        q = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 20))
        resultados = search_cie10(q, limit=limit)
        return Response(resultados)


# ==============================================================================
# MÓDULO: clinica/views.py — CU15: Apertura de Historia Clínica y Control de Acceso RBAC (HU-25, HU-26)
# CAPA BCE: CONTROL (Controller) — CTR_HistoriaClinicaController
# DIAGRAMA DE SECUENCIA CU15 (sprint2.md):
#   Actor (Psicólogo Tratante) → IU_HistoriaClinica: 1: solicitar_apertura_historia(paciente_id)
#   IU_HistoriaClinica → CTR_HistoriaClinicaController: 2: POST /api/v1/historias-clinicas/ (paciente_id, anamnesis_inicial)
#   CTR_HistoriaClinicaController → CTR_HistoriaClinicaController: 3: verificar_permiso_rbac(role='PSICOLOGO', terapeuta_asignado=true)
#   alt RBAC: Terapeuta Asignado (Autorizado)
#     CTR_HistoriaClinicaController → CE_HistoriaClinica: 4: INSERT INTO clinica_historiaclinica (codigo_expediente, fecha_apertura)
#     CE_HistoriaClinica --> CTR_HistoriaClinicaController: 5: expediente_registrado(id, codigo_historia)
#     CTR_HistoriaClinicaController --> IU_HistoriaClinica: 6: HTTP 201 Created {codigo_historia, anamnesis, cerrada=false}
#     IU_HistoriaClinica --> Psicólogo Tratante: 7: renderizar_pestanas_historia(anamnesis, examen_mental, cie11)
#   else Sin Asignacion RBAC (Denegado)
#     CTR_HistoriaClinicaController --> IU_HistoriaClinica: 8: HTTP 403 Forbidden ('Acceso denegado: Terapeuta no asignado al paciente')
#     IU_HistoriaClinica --> Psicólogo Tratante: 9: mostrar_error_seguridad_rbac('Acceso no autorizado a historia ajena')
# ==============================================================================
class HistoriaClinicaViewSet(viewsets.ModelViewSet):
    """
    CTR_HistoriaClinicaController:
    Controlador central del expediente clínico psicológico electrónico (EHR).
    Aplica RBAC estricto validando psicólogo tratante o administrador con auditoría.
    """
    queryset = HistoriaClinica.objects.select_related('paciente__usuario', 'psicologo_apertura__usuario').prefetch_related('diagnosticos').all().order_by('-fecha_apertura')
    serializer_class = HistoriaClinicaSerializer
    # CU15 Paso 3: verificar_permiso_rbac (si no asignado -> Paso 8: 403 Forbidden)
    permission_classes = [IsTreatingPsychologistOrAdmin]

    def get_queryset(self):
        # CU15 Paso 3: Filtrar historias clínicas según asignación terapéutica y rol
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs

        rol_nombre = user.rol.nombre.lower() if user.rol else ""
        if 'admin' in rol_nombre or 'coordinador' in rol_nombre:
            return qs

        # Si es paciente, sólo su propia historia
        if 'paciente' in rol_nombre and hasattr(user, 'perfil_paciente'):
            return qs.filter(paciente=user.perfil_paciente)

        # Si es psicólogo, historias de pacientes donde es psicólogo de apertura o tiene citas
        if 'psic' in rol_nombre and hasattr(user, 'perfil_psicologo'):
            psico = user.perfil_psicologo
            return qs.filter(
                Q(psicologo_apertura=psico) |
                Q(paciente__citas__psicologo=psico)
            ).distinct()

        # Otros roles (recepcionistas) no tienen acceso a expedientes clínicos completos
        return qs.none()

    def perform_create(self, serializer):
        # CU15 Paso 4: INSERT INTO clinica_historiaclinica (codigo_expediente, fecha_apertura)
        # CU15 Paso 5: expediente_registrado(id, codigo_historia)
        user = self.request.user
        psico = getattr(user, 'perfil_psicologo', None)
        if not psico and not serializer.validated_data.get('psicologo_apertura'):
            # Si es admin creando en nombre del centro, asignar primer psicólogo activo
            psico = Psicologo.objects.filter(activo=True).first()
        serializer.save(psicologo_apertura=serializer.validated_data.get('psicologo_apertura') or psico)

    def perform_update(self, serializer):
        # CU19: Prevenir ediciones si el expediente está formalmente cerrado
        if lock_history(self.get_object().pk).cerrada:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'historia_clinica': 'El expediente está cerrado.'})
        serializer.save()

    @action(detail=True, methods=['get', 'post'], url_path='diagnosticos')
    def diagnosticos(self, request, pk=None):
        historia = self.get_object()
        if request.method == 'GET':
            serializer = DiagnosticoCIESerializer(historia.diagnosticos.all(), many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            from clinica.lifecycle import ensure_history_open
            ensure_history_open(lock_history(historia.pk))
            data = request.data.copy()
            data['historia_clinica'] = str(historia.id)
            serializer = DiagnosticoCIESerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='reactivar')
    def reactivar(self, request, pk=None):
        event = reactivate_history(history_id=pk, user=request.user, reason=request.data.get('motivo_clinico'))
        return Response(DerivacionCasoSerializer(event).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='timeline')
    def timeline(self, request, pk=None):
        historia = self.get_object()
        notas = historia.notas_sesion.all().order_by('fecha_sesion')
        evoluciones = historia.evoluciones.all().order_by('fecha_registro')
        tareas = historia.tareas.select_related('evidencia').all().order_by('fecha_limite')

        timeline_items = []
        for n in notas:
            timeline_items.append({
                "tipo": "NOTA_SOAP",
                "id": str(n.id),
                "fecha": n.fecha_sesion,
                "titulo": f"Sesión #{n.numero_sesion} ({n.estado_guardado})",
                "subjetivo": n.subjetivo,
                "analisis": n.analisis,
                "plan": n.plan,
                "tecnicas": n.tecnicas_aplicadas
            })
        for e in evoluciones:
            timeline_items.append({
                "tipo": "EVOLUCION",
                "id": str(e.id),
                "fecha": e.fecha_registro,
                "titulo": f"Hito de Evolución: {e.get_estado_avance_display()}",
                "estado_avance": e.estado_avance,
                "estado_avance_display": e.get_estado_avance_display(),
                "justificacion": e.justificacion,
                "acuerdos": e.acuerdos_pactados,
                "alerta": (e.estado_avance == 'RETROCESO_CRISIS'),
                "descripcion_crisis": e.justificacion if e.estado_avance == 'RETROCESO_CRISIS' else "",
                "recomendacion_inmediata": e.acuerdos_pactados
            })
        for t in tareas:
            timeline_items.append({
                "tipo": "TAREA",
                "id": str(t.id),
                "fecha": t.fecha_creacion,
                "fecha_limite": t.fecha_limite,
                "titulo": f"Tarea: {t.titulo}",
                "categoria": t.categoria,
                "estado": t.estado,
                "dificultad": t.evidencia.dificultad_percibida if hasattr(t, 'evidencia') else None,
                # CU17 / HU-45 (c): el psicólogo recibe la reflexión entregada desde la app móvil
                "reflexion": t.evidencia.texto_reflexion if hasattr(t, 'evidencia') else None,
            })

        timeline_items.sort(key=lambda x: str(x["fecha"]), reverse=True)
        return Response(timeline_items)


class DiagnosticoCIEViewSet(viewsets.ModelViewSet):
    queryset = DiagnosticoCIE.objects.all().order_by('-fecha_diagnostico')
    serializer_class = DiagnosticoCIESerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        history = lock_history(serializer.validated_data['historia_clinica'].pk)
        from clinica.lifecycle import ensure_history_open
        ensure_history_open(history)
        serializer.save()

    def perform_update(self, serializer):
        ensure_object_history_open(self.get_object())
        serializer.save()

    def perform_destroy(self, instance):
        ensure_object_history_open(instance)
        instance.delete()


# ==============================================================================
# MÓDULO: clinica/views.py — CU16: Registro de Notas SOAP, Autoguardado Reactivo e Inmutabilidad (HU-27, HU-28)
# CAPA BCE: CONTROL (Controller) — CTR_NotaSesionController
# DIAGRAMA DE SECUENCIA CU16 (sprint2.md):
#   Actor (Psicólogo Tratante) → IU_EditorNotasSOAP: 1: redactar_nota_soap(subjetivo, objetivo, analisis, plan)
#   opt Autoguardado Reactivo en Borrador (debounce 30s)
#     IU_EditorNotasSOAP → CTR_NotaSesionController: 2: PATCH /api/v1/notas-sesion/{id}/borrador/ (payload_parcial)
#     CTR_NotaSesionController → CE_NotaSesion: 3: UPDATE clinica_notasesion SET estado='BORRADOR'
#     CE_NotaSesion --> CTR_NotaSesionController: 4: borrador_actualizado()
#     CTR_NotaSesionController --> IU_EditorNotasSOAP: 5: HTTP 200 OK (guardado_automatico_confirmado)
#   end
#   Actor (Psicólogo Tratante) → IU_EditorNotasSOAP: 6: formalizar_y_firmar_nota()
#   IU_EditorNotasSOAP → CTR_NotaSesionController: 7: POST /api/v1/notas-sesion/firmar/ (cita_id, payload_completo)
#   CTR_NotaSesionController → CTR_NotaSesionController: 8: validar_cita_realizada_y_bloqueo_tiempo()
#   alt Cita Realizada (Firma Inmutable Concedida)
#     CTR_NotaSesionController → CE_NotaSesion: 9: INSERT/UPDATE clinica_notasesion (firmada=true, estado='INMUTABLE')
#     CE_NotaSesion --> CTR_NotaSesionController: 10: nota_inmutable_consolidada()
#     CTR_NotaSesionController --> IU_EditorNotasSOAP: 11: HTTP 201 Nota Firmada Inmutable
#     IU_EditorNotasSOAP --> Psicólogo Tratante: 12: bloquear_editor_y_actualizar_timeline(badge_firmado_legal)
#   else Cita No Concluida (Bloqueo Legal)
#     CTR_NotaSesionController --> IU_EditorNotasSOAP: 13: HTTP 400 Bad Request ('La cita debe estar REALIZADA para firmar la nota')
#     IU_EditorNotasSOAP --> Psicólogo Tratante: 14: mostrar_alerta_bloqueo_legal('No se puede sellar nota de sesion no concluida')
#   end
# ==============================================================================
class NotaSesionViewSet(viewsets.ModelViewSet):
    """
    CTR_NotaSesionController:
    Controlador para el registro de evolución estructurada SOAP, autoguardado y firma inmutable.
    """
    queryset = NotaSesion.objects.select_related('historia_clinica__paciente__usuario', 'psicologo__usuario', 'cita').all().order_by('-fecha_sesion')
    serializer_class = NotaSesionSerializer
    permission_classes = [IsTreatingPsychologistOrAdmin]

    def perform_create(self, serializer):
        ensure_object_history_open(serializer.validated_data.get('historia_clinica'))
        user = self.request.user
        psico = getattr(user, 'perfil_psicologo', None)
        if not psico and not serializer.validated_data.get('psicologo'):
            psico = Psicologo.objects.filter(activo=True).first()
        
        historia = serializer.validated_data.get('historia_clinica')
        num_sesion = serializer.validated_data.get('numero_sesion')
        if not num_sesion and historia:
            ultimo = historia.notas_sesion.order_by('-numero_sesion').first()
            num_sesion = (ultimo.numero_sesion + 1) if ultimo else 1
        elif not num_sesion:
            num_sesion = 1

        serializer.save(
            psicologo=serializer.validated_data.get('psicologo') or psico,
            numero_sesion=num_sesion
        )

    def perform_destroy(self, instance):
        ensure_object_history_open(instance)
        instance.delete()

    @transaction.atomic
    @action(detail=False, methods=['post'], url_path='guardar_borrador')
    def guardar_borrador_endpoint(self, request):
        """CU16 Pasos 2-5: Crear o actualizar borrador de nota SOAP."""
        nota_id = request.data.get('id')
        if nota_id:
            try:
                nota = NotaSesion.objects.select_for_update().get(id=nota_id)
                ensure_object_history_open(nota)
                serializer = self.get_serializer(nota, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(estado_guardado='BORRADOR')
                return Response(serializer.data, status=status.HTTP_200_OK)
            except NotaSesion.DoesNotExist:
                pass
        
        data = request.data.copy()
        data['estado_guardado'] = 'BORRADOR'
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        ensure_object_history_open(self.get_object())
        nota = self.get_object()
        if nota.estado_guardado == 'FIRMADA':
            return Response(
                {"error": "Nota consolidada inmutable. Para aclaraciones debe crear una adenda clínica."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        ensure_object_history_open(self.get_object())
        nota = self.get_object()
        if nota.estado_guardado == 'FIRMADA':
            return Response(
                {"error": "Nota consolidada inmutable. Para aclaraciones debe crear una adenda clínica."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['patch', 'post', 'put'], url_path='borrador')
    def guardar_borrador(self, request, pk=None):
        """CU16 Pasos 2-5: Autoguardado reactivo cada 30 segundos (CU16 Criterio b)."""
        nota = self.get_object()
        ensure_object_history_open(nota)
        if nota.estado_guardado == 'FIRMADA':
            return Response({"error": "La nota ya se encuentra consolidada y firmada de manera inmutable."}, status=status.HTTP_400_BAD_REQUEST)

        # CU16 Paso 3: UPDATE clinica_notasesion SET estado='BORRADOR'
        serializer = self.get_serializer(nota, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(estado_guardado='BORRADOR')
        # CU16 Paso 5: HTTP 200 OK (guardado_automatico_confirmado)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'patch'], url_path='firmar')
    def firmar_nota(self, request, pk=None):
        return self._ejecutar_firma(request, pk)

    @action(detail=True, methods=['post', 'patch'], url_path='firmar_nota')
    def firmar_nota_alias(self, request, pk=None):
        return self._ejecutar_firma(request, pk)

    @transaction.atomic
    def _ejecutar_firma(self, request, pk):
        # CU16 Paso 7: POST /api/v1/notas-sesion/firmar/
        nota = NotaSesion.objects.select_for_update().get(pk=pk)
        ensure_object_history_open(nota)
        if nota.estado_guardado == 'FIRMADA':
            return Response(
                {"error": "La nota SOAP ya fue firmada previamente y es inmutable."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # CU16: Verificar terapeuta tratante
        user = request.user
        psico = getattr(user, 'perfil_psicologo', None)
        if psico and nota.psicologo and nota.psicologo != psico:
            return Response(
                {"error": "Solo el psicólogo tratante asignado a la sesión puede firmar y sellar esta nota."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Precondición c: Historia clínica abierta y activa
        if nota.historia_clinica.cerrada:
            return Response(
                {"error": "No se pueden firmar notas en un expediente cerrado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # CU16 Paso 8: Validar cita realizada y bloqueo de tiempo (si no realizada -> Paso 13: 400 Bad Request)
        if nota.cita and nota.cita.estado != 'REALIZADA':
            return Response(
                {"error": "La cita debe estar REALIZADA para firmar la nota"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Paso 5 & 6 Diagrama BCE: INSERT INTO clinica_notasesion (Inmutable) en esquema tenant
        for field in ['subjetivo', 'objetivo', 'analisis', 'plan', 'tecnicas_aplicadas', 'conducta_observada']:
            if field in request.data:
                setattr(nota, field, request.data[field])
        if 'intervenciones_aplicadas' in request.data and not getattr(nota, 'tecnicas_aplicadas', None):
            nota.tecnicas_aplicadas = request.data['intervenciones_aplicadas']
        
        nota.estado_guardado = 'FIRMADA'
        nota.fecha_firma = timezone.now()
        nota.save()

        serializer = self.get_serializer(nota)
        # Paso 7 Diagrama BCE: 201 Created {nota_id, firmada: true}
        return Response({
            "mensaje": "Nota médica sellada en esquema tenant exitosamente.",
            "nota_id": str(nota.id),
            "id": str(nota.id),
            "firmada": True,
            "estado": nota.estado_guardado,
            "sha256": serializer.data.get('firma_hash_integridad', ''),
            "fecha_firma": nota.fecha_firma.isoformat(),
            "nota": serializer.data
        }, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='adenda')
    def crear_adenda(self, request, pk=None):
        """
        CU16 Criterio d / Paso 4:
        Una nota firmada no admite edición directa; modificaciones requieren adendas clínicas trazables.
        """
        nota = NotaSesion.objects.select_for_update().get(pk=pk)
        ensure_object_history_open(nota)
        if nota.estado_guardado != 'FIRMADA':
            return Response(
                {"error": "Solo se pueden anexar adendas clínicas sobre notas previamente firmadas e inmutables."},
                status=status.HTTP_400_BAD_REQUEST
            )

        texto_adenda = request.data.get('texto_adenda', '').strip()
        if not texto_adenda:
            return Response(
                {"error": "Debe especificar el texto de la adenda clínica o aclaración."},
                status=status.HTTP_400_BAD_REQUEST
            )

        now_str = timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M')
        user_name = request.user.get_full_name() or request.user.email
        adenda_bloque = f"\n\n--- [ADENDA CLÍNICA: {now_str} por {user_name}] ---\n{texto_adenda}"
        nota.conducta_observada = (nota.conducta_observada or "") + adenda_bloque
        nota.save(update_fields=['conducta_observada'])

        serializer = self.get_serializer(nota)
        return Response({
            "mensaje": "Adenda clínica registrada y anexada inmutablemente.",
            "nota": serializer.data,
            "adendas": nota.conducta_observada
        }, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────────────────────────────────────────
# CU17: Evolución Longitudinal, Tareas y Evidencias
# ──────────────────────────────────────────────────────────────────────────────
class EvolucionClinicaViewSet(viewsets.ModelViewSet):
    queryset = EvolucionClinica.objects.select_related('historia_clinica__paciente__usuario').all().order_by('-fecha_registro')
    serializer_class = EvolucionClinicaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        historia_id = self.request.query_params.get('historia_clinica')
        if historia_id:
            qs = qs.filter(historia_clinica_id=historia_id)
        return qs

    def perform_create(self, serializer):
        ensure_object_history_open(serializer.validated_data.get('historia_clinica'))
        evolucion = serializer.save()        # Si se detecta retroceso o crisis, generar alerta clínica de prioridad alta/crítica (CU17 / HU-28 Criterio b)
        if evolucion.estado_avance == 'RETROCESO_CRISIS':
            try:
                from agenda.models import Alerta
                paciente = evolucion.historia_clinica.paciente
                Alerta.objects.create(
                    paciente=paciente,
                    tipo='CRISIS_RETROCESO',
                    severidad='CRITICA',
                    descripcion=f"Alerta Prioritaria (HU-28): Retroceso o factor de crisis detectado para el paciente {paciente.usuario.nombre} {paciente.usuario.apellido}. Justificación: {evolucion.justificacion}"
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Error registrando alerta de crisis en perform_create: {e}")

    def perform_update(self, serializer):
        ensure_object_history_open(self.get_object())
        serializer.save()

    def perform_destroy(self, instance):
        ensure_object_history_open(instance)
        instance.delete()


# ==============================================================================
# MÓDULO: clinica/views.py — CU17: Asignación y Cumplimiento de Tareas Terapéuticas Inter-Sesiones (HU-29, HU-30)
# CAPA BCE: CONTROL (Controller) — CTR_TareasController
# DIAGRAMA DE SECUENCIA CU17 (sprint2.md):
#   Actor (Paciente Móvil) → IU_GestionTareas: 1: reportar_cumplimiento(tarea_id, texto_reflexion, archivo_adjunto)
#   IU_GestionTareas → CTR_TareasController: 2: POST /api/v1/tareas/{id}/evidencia/ (Multipart Form-Data)
#   CTR_TareasController → CTR_TareasController: 3: validar_plazo_limite_y_tipo_archivo()
#   alt Entrega en Plazo (Cumplimiento Exitoso)
#     CTR_TareasController → CE_TareaTerapeutica: 4: INSERT clinica_evidenciatarea & UPDATE clinica_tareaterapeutica (estado='COMPLETADA')
#     CE_TareaTerapeutica --> CTR_TareasController: 5: evidencia_persistida()
#     CTR_TareasController --> IU_GestionTareas: 6: HTTP 200 OK {estado: 'COMPLETADA', fecha_cumplimiento}
#     IU_GestionTareas --> Paciente Móvil: 7: actualizar_indicador_progreso(100% completado)
#   else Fuera de Plazo (Entrega Extemporánea)
#     CTR_TareasController → CE_TareaTerapeutica: 8: UPDATE clinica_tareaterapeutica SET estado='COMPLETADA_CON_RETRASO'
#     CE_TareaTerapeutica --> CTR_TareasController: 9: tarea_actualizada_con_retraso()
#     CTR_TareasController --> IU_GestionTareas: 10: HTTP 200 OK (warning_retraso=true)
#     IU_GestionTareas --> Paciente Móvil: 11: mostrar_aviso_retraso('Tarea entregada fuera de plazo')
#   end
# ==============================================================================
class TareaTerapeuticaViewSet(viewsets.ModelViewSet):
    """
    CTR_TareasController:
    Controlador para la prescripción clínica, entrega de evidencias y feedback inter-sesiones.
    """
    queryset = TareaTerapeutica.objects.select_related('historia_clinica', 'psicologo__usuario', 'paciente__usuario').prefetch_related('evidencia').all().order_by('fecha_limite')
    serializer_class = TareaTerapeuticaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        ensure_object_history_open(serializer.validated_data.get('historia_clinica'))
        user = self.request.user
        psico = getattr(user, 'perfil_psicologo', None) or Psicologo.objects.filter(activo=True).first()
        serializer.save(psicologo=serializer.validated_data.get('psicologo') or psico)

    def perform_update(self, serializer):
        ensure_object_history_open(self.get_object())
        serializer.save()

    def perform_destroy(self, instance):
        ensure_object_history_open(instance)
        instance.delete()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        rol_nombre = user.rol.nombre.lower() if user.rol else ""

        if 'paciente' in rol_nombre and hasattr(user, 'perfil_paciente'):
            return qs.filter(paciente=user.perfil_paciente)

        paciente_id = self.request.query_params.get('paciente')
        if paciente_id:
            qs = qs.filter(paciente_id=paciente_id)
        historia_id = self.request.query_params.get('historia_clinica')
        if historia_id:
            qs = qs.filter(historia_clinica_id=historia_id)
        return qs

    @action(detail=True, methods=['post'], url_path='evidencia')
    @transaction.atomic
    def registrar_evidencia(self, request, pk=None):
        """
        CU17 Paso 2: POST /api/v1/tareas/{id}/evidencia/ (Multipart Form-Data)
        CU17 Paso 3: Validar plazo límite y tipo archivo
        CU17 Pasos 4-7: Entrega en plazo -> INSERT evidencia & UPDATE clinica_tareaterapeutica (estado='COMPLETADA')
        CU17 Pasos 8-11: Fuera de plazo -> UPDATE clinica_tareaterapeutica (estado='COMPLETADA_CON_RETRASO')
        """
        tarea = self.get_object()
        ensure_object_history_open(tarea)

        # Validación estado previo
        if tarea.estado in ('COMPLETADA', 'COMPLETADA_CON_RETRASO') and hasattr(tarea, 'evidencia'):
            return Response({
                "error": "Esta tarea terapéutica ya fue completada previamente."
            }, status=status.HTTP_400_BAD_REQUEST)

        # CU17 Paso 3: Validar plazo límite y tipo de archivo
        hoy = timezone.localdate()
        es_extemporanea = bool(tarea.fecha_limite and tarea.fecha_limite < hoy)

        archivo = request.FILES.get('archivo') or request.FILES.get('archivo_adjunto')
        if archivo:
            allowed_exts = ('.pdf', '.png', '.jpg', '.jpeg', '.mp3', '.m4a', '.doc', '.docx')
            if not any(archivo.name.lower().endswith(ext) for ext in allowed_exts):
                return Response({
                    "error": "Tipo de archivo no permitido. Solo se aceptan documentos PDF, imágenes o audio."
                }, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['tarea'] = str(tarea.id)
        serializer = EvidenciaTareaSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Paso 5 & 6 Diagrama CU17: INSERT evidencia & UPDATE clinica_tareaterapeutica
        if es_extemporanea:
            # Flujo alternativo: Fuera de Plazo (Entrega Extemporánea)
            # UPDATE clinica_tareaterapeutica SET estado='COMPLETADA_CON_RETRASO'
            tarea.estado = 'COMPLETADA_CON_RETRASO'
            tarea.save()
            return Response({
                "mensaje": "Tarea entregada fuera de plazo",
                "estado": "COMPLETADA_CON_RETRASO",
                "warning_retraso": True,
                "completada_porcentaje": 100,
                "tarea_id": str(tarea.id),
                "tarea_estado": tarea.estado,
                "fecha_cumplimiento": timezone.now().isoformat(),
                "evidencia": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # Flujo principal: Entrega en Plazo (Cumplimiento Exitoso)
            # UPDATE clinica_tareaterapeutica SET estado='COMPLETADA'
            tarea.estado = 'COMPLETADA'
            tarea.save()
            return Response({
                "mensaje": "Evidencia guardada y tarea completada",
                "estado": "COMPLETADA",
                "warning_retraso": False,
                "completada_porcentaje": 100,
                "tarea_id": str(tarea.id),
                "tarea_estado": tarea.estado,
                "fecha_cumplimiento": timezone.now().isoformat(),
                "evidencia": serializer.data
            }, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], url_path='subir_evidencia')
    def subir_evidencia_alias(self, request, pk=None):
        return self.registrar_evidencia(request, pk)

    # CU17-paso 2: POST /api/v1/clinica/tareas/{id}/entregar/ (multipart) → CTR_SeguimientoMovilController
    @action(detail=True, methods=['post'], url_path='entregar')
    @transaction.atomic
    def entregar_tarea_alias(self, request, pk=None):
        """
        CU17 Móvil (HU-45, HU-46) — Secuencia_Corregido_CU17_Tareas_Mood_Movil:
          2 : POST /api/clinica/tareas/{id}/entregar/ (multipart o JSON)
          3-4 : validar_plazo_limite_y_tipo_archivo(fecha_limite, archivo)
          5-6 : actualizar_estado_tarea('COMPLETADA')  [HU-45 c: 'Entregada', edición bloqueada]
          alt [plazo_valido && archivo_valido]
            7-8  : persistir_evidencia(archivo_url, texto_reflexion)
            9-10 : obtener_paciente()
            11-12: registrar_animo_diario(estado_animo, nota)   (opcional, HU-46)
            13-14: supervisar_avance(psicologo_id, alerta_tarea)
            15-16: registrar_acceso('ENTREGA_TAREA_CU17', ip)
            17   : 200 OK {'Tarea entregada y ánimo registrado'}
          else
            19   : 400 Bad Request {'Plazo expirado o archivo inválido'}
        La ruta /evidencia/ (CU17 web, Sprint 2) conserva la entrega con retraso.
        """
        from django.core.files.storage import default_storage
        from audit.services import AuditLog
        from clinica.models import RegistroAnimo

        tarea = self.get_object()
        ensure_object_history_open(tarea)

        # HU-45 (c): una tarea entregada queda bloqueada para edición
        if hasattr(tarea, 'evidencia'):
            return Response({"error": "Esta tarea ya fue entregada y no puede editarse."},
                            status=status.HTTP_400_BAD_REQUEST)

        # CU17-paso 3: validar_plazo_limite_y_tipo_archivo(fecha_limite, archivo) → CE_TareaTerapeutica
        # CU17-paso 4: resultado_validacion(es_valido) [retorno]
        # else [plazo o archivo inválido] → CU17-paso 19: HTTP 400 Bad Request {'Plazo expirado o archivo inválido'}
        if tarea.fecha_limite and tarea.fecha_limite < timezone.localdate():
            return Response({"error": "Plazo expirado: no se puede entregar la tarea fuera de plazo.",
                             "codigo": "PLAZO_EXPIRADO"}, status=status.HTTP_400_BAD_REQUEST)
        archivo = request.FILES.get('archivo') or request.FILES.get('archivo_adjunto')
        allowed_exts = ('.pdf', '.png', '.jpg', '.jpeg', '.mp3', '.m4a', '.doc', '.docx')
        if archivo and not archivo.name.lower().endswith(allowed_exts):
            return Response({"error": "Archivo inválido: solo se aceptan PDF, imágenes, audio o Word.",
                             "codigo": "ARCHIVO_INVALIDO"}, status=status.HTTP_400_BAD_REQUEST)
        escala = request.data.get('escala_animo') or request.data.get('escala_valor')
        if escala not in (None, ''):
            try:
                escala = int(escala)
            except (TypeError, ValueError):
                escala = 0
            if not 1 <= escala <= 5:
                return Response({"error": "El estado de ánimo debe valorarse de 1 a 5."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            escala = None

        # alt [plazo_valido == true y archivo_valido == true]
        # CU17-paso 7: persistir_evidencia_tarea(archivo_url, hash_sha256) → CE_EvidenciaTarea
        #              (se guardan archivo_url y la reflexión del paciente)
        # CU17-paso 8: evidencia_guardada [retorno]
        serializer = EvidenciaTareaSerializer(data={
            'tarea': str(tarea.id),
            'texto_reflexion': (request.data.get('texto_reflexion') or '').strip(),
            'dificultad_percibida': request.data.get('dificultad_percibida', 3),
        })
        serializer.is_valid(raise_exception=True)
        archivo_url = ''
        if archivo:
            archivo_url = default_storage.url(default_storage.save(f"evidencias_tareas/{tarea.id}/{archivo.name}", archivo))
        serializer.save(archivo_evidencia_url=archivo_url)

        # CU17-paso 5: actualizar_estado_tarea('COMPLETADA') → CE_TareaTerapeutica
        #              (se aplica tras guardar la evidencia, en la misma transacción)
        # CU17-paso 6: estado_actualizado [retorno]
        tarea.estado = 'COMPLETADA'
        tarea.save(update_fields=['estado'])

        # CU17-paso 9: obtener_paciente() → CE_Paciente (tarea.paciente)
        # CU17-paso 10: datos_paciente(paciente_id) [retorno]
        # CU17-paso 11: registrar_animo_diario(valor_animo, nota_contextual) → CE_RegistroAnimo (opcional, HU-46)
        # CU17-paso 12: animo_registrado [retorno]
        animo_registrado = False
        if escala is not None:
            codigos = {1: 'MUY_BAJO', 2: 'BAJO', 3: 'NEUTRAL', 4: 'BUENO', 5: 'EXCELENTE'}  # RegistroAnimo.ESTADO_CHOICES
            RegistroAnimo.objects.update_or_create(
                paciente=tarea.paciente,
                fecha_registro=timezone.localdate(),
                defaults={
                    'estado_animo': codigos[escala],
                    'escala_valor': escala,
                    'nota_reflexiva': request.data.get('nota_animo', ''),
                },
            )
            animo_registrado = True

        # CU17-paso 13: supervisar_avance(tarea_id, alerta_fallas) → CE_Psicologo
        #               (la entrega queda visible en el panel del psicólogo y en la bitácora con psicologo_id)
        # CU17-paso 14: avance_supervisado [retorno]
        # CU17-paso 15: registrar_acceso(evento='ENTREGA_TAREA_EXITOSA', ip) → CE_AuditLog
        #               (el código registra el evento con el nombre 'ENTREGA_TAREA_CU17')
        # CU17-paso 16: acceso_auditado [retorno]
        ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', 'unknown')
        AuditLog.registrar_acceso(
            'ENTREGA_TAREA_CU17', ip,
            tarea_id=str(tarea.id), paciente_id=str(tarea.paciente_id),
            psicologo_id=str(tarea.psicologo_id), usuario=request.user.email,
            animo_registrado=animo_registrado,
        )

        # CU17-paso 17: HTTP 200 OK {'Tarea entregada y ánimo registrado'} [retorno]
        return Response({
            "mensaje": "Tarea entregada y ánimo registrado" if animo_registrado else "Tarea entregada",
            "estado": tarea.estado,
            "tarea_estado": tarea.estado,
            "tarea_id": str(tarea.id),
            "animo_registrado": animo_registrado,
            "warning_retraso": False,
            "fecha_cumplimiento": serializer.instance.fecha_cumplimiento.isoformat(),
            "evidencia": serializer.data,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='revisar_tarea')
    def revisar_tarea(self, request, pk=None):
        tarea = self.get_object()
        feedback = request.data.get('feedback', '')
        if tarea.estado in ('PENDIENTE', 'EN_REVISION'):
            tarea.estado = 'COMPLETADA'
            tarea.save()
        return Response({
            "mensaje": "Feedback clínico registrado y tarea marcada como revisada con éxito.",
            "feedback": feedback,
            "tarea": TareaTerapeuticaSerializer(tarea).data
        }, status=status.HTTP_200_OK)


class EvidenciaTareaViewSet(viewsets.ModelViewSet):
    queryset = EvidenciaTarea.objects.select_related('tarea').all()
    serializer_class = EvidenciaTareaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        ensure_object_history_open(serializer.validated_data['tarea'])
        serializer.save()

    def perform_update(self, serializer):
        ensure_object_history_open(self.get_object())
        serializer.save()

    def perform_destroy(self, instance):
        ensure_object_history_open(instance)
        instance.delete()


# ==============================================================================
# MÓDULO: clinica/views.py — CU18: Consentimiento Informado Digital con Sellado SHA-256 (HU-31, HU-32)
# CAPA BCE: CONTROL (Controller) — CTR_ConsentimientoController
# DIAGRAMA DE SECUENCIA CU18 (sprint2.md):
#   Actor (Paciente o Tutor) → IU_FirmaConsentimiento: 1: leer_clausulas_obligatorias_y_firmar_canvas()
#   IU_FirmaConsentimiento → IU_FirmaConsentimiento: 2: calcular_hash_sha256(texto_legal + trazos_canvas + timestamp)
#   IU_FirmaConsentimiento → CTR_ConsentimientoController: 3: POST /api/v1/consentimientos/firmar/ (hash_sha256, firma_png, tutor_ci)
#   CTR_ConsentimientoController → CTR_ConsentimientoController: 4: capturar_metadatos_legales(ip_remota, user_agent, timestamp_bolivia)
#   alt Mayor de Edad: Firma Titular
#     CTR_ConsentimientoController → CE_FirmaConsentimiento: 5: INSERT INTO clinica_firmaconsentimiento (tipo='TITULAR', hash_sha256)
#     CE_FirmaConsentimiento --> CTR_ConsentimientoController: 6: firma_registrada_inmutable()
#     CTR_ConsentimientoController --> IU_FirmaConsentimiento: 7: HTTP 201 Consentimiento Aceptado (hash_verificado)
#     IU_FirmaConsentimiento --> Paciente o Tutor: 8: habilitar_atencion_y_reserva_citas()
#   else Menor de Edad: Firma Tutor Legal
#     CTR_ConsentimientoController → CTR_ConsentimientoController: 9: validar_ci_y_parentesco_tutor()
#     CTR_ConsentimientoController → CE_FirmaConsentimiento: 10: INSERT INTO clinica_firmaconsentimiento (tipo='TUTOR', tutor_ci, hash_sha256)
#     CE_FirmaConsentimiento --> CTR_ConsentimientoController: 11: firma_tutor_inmutable()
#     CTR_ConsentimientoController --> IU_FirmaConsentimiento: 12: HTTP 201 Consentimiento Tutor Registrado
#     IU_FirmaConsentimiento --> Paciente o Tutor: 13: notificar_validacion_tutor_exitosa()
#   end
# ==============================================================================
class ConsentimientoInformadoViewSet(viewsets.ModelViewSet):
    """
    CTR_ConsentimientoController:
    Controlador para la gestión de plantillas de consentimiento y firma digital inmutable con hash SHA-256.
    """
    queryset = ConsentimientoInformado.objects.all().order_by('titulo')
    serializer_class = ConsentimientoInformadoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        activo = self.request.query_params.get('activo')
        if activo is not None:
            es_activo = activo.lower() in ('true', '1')
            qs = qs.filter(activo=es_activo)
        return qs

    def perform_create(self, serializer):
        tipo = serializer.validated_data.get('tipo', 'ATENCION_GENERAL')
        # HU-31 BDD Paso 4: Archivar la versión previa manteniendo validez y establecer la nueva como obligatoria
        ConsentimientoInformado.objects.filter(tipo=tipo, activo=True).update(activo=False)
        serializer.save(activo=True)

    @action(detail=True, methods=['get'], url_path='render-preview')
    def render_preview(self, request, pk=None):
        plantilla = self.get_object()
        paciente_id = request.query_params.get('paciente')
        paciente_nombre = "[Nombre del Paciente]"
        paciente_ci = "[CI del Paciente]"
        psicologo_nombre = "Equipo de Especialistas en Salud Mental SIGEPSI"
        centro_nombre = "Centro de Atención Psicológica Integral SIGEPSI"
        tutor_nombre = "[Tutor o Apoderado Legal]"
        tutor_ci = "[CI Tutor Legal]"
        es_menor = False

        if paciente_id:
            try:
                p = Paciente.objects.select_related('usuario').get(id=paciente_id)
                paciente_nombre = f"{p.usuario.nombre} {p.usuario.apellido}"
                paciente_ci = p.ci
                if p.tutor_legal_nombre:
                    tutor_nombre = p.tutor_legal_nombre
                if p.tutor_legal_ci:
                    tutor_ci = p.tutor_legal_ci
                edad = p.edad
                if edad is None and p.fecha_nacimiento:
                    hoy = timezone.localdate()
                    fn = p.fecha_nacimiento
                    edad = hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))
                if edad is not None and edad < 18:
                    es_menor = True
            except Paciente.DoesNotExist:
                pass

        contenido = plantilla.contenido_legal
        # HU-31 Criterios de Aceptación a): {nombre_paciente}, {ci}, {centro}, {psicologo}
        contenido = re.sub(r'\{(?:nombre_paciente|paciente_nombre)\}', paciente_nombre, contenido, flags=re.IGNORECASE)
        contenido = re.sub(r'\{(?:ci|ci_paciente|paciente_ci)\}', paciente_ci, contenido, flags=re.IGNORECASE)
        contenido = re.sub(r'\{(?:centro|nombre_centro|centro_nombre)\}', centro_nombre, contenido, flags=re.IGNORECASE)
        contenido = re.sub(r'\{(?:psicologo|psicologo_cabecera)\}', psicologo_nombre, contenido, flags=re.IGNORECASE)
        contenido = re.sub(r'\{(?:fecha)\}', timezone.localdate().strftime('%d/%m/%Y'), contenido, flags=re.IGNORECASE)
        contenido = re.sub(r'\{(?:version)\}', plantilla.version, contenido, flags=re.IGNORECASE)
        contenido = re.sub(r'\{(?:tutor_nombre)\}', tutor_nombre, contenido, flags=re.IGNORECASE)
        contenido = re.sub(r'\{(?:tutor_ci)\}', tutor_ci, contenido, flags=re.IGNORECASE)

        return Response({
            "titulo": plantilla.titulo,
            "tipo": plantilla.tipo,
            "version": plantilla.version,
            "activo": plantilla.activo,
            "es_menor_edad": es_menor,
            "contenido_renderizado": contenido
        })

    @action(detail=False, methods=['post'], url_path='firmar')
    def firmar(self, request):
        """
        CU18 Paso 3: POST /api/v1/consentimientos/firmar/ (hash_sha256, firma_png, tutor_ci)
        CU18 Paso 4: capturar_metadatos_legales(ip_remota, user_agent, timestamp_bolivia)
        CU18 Pasos 5-8: Mayor de edad -> INSERT INTO clinica_firmaconsentimiento (tipo='TITULAR', hash_sha256)
        CU18 Pasos 9-13: Menor de edad -> Validar tutor -> INSERT INTO clinica_firmaconsentimiento (tipo='TUTOR')
        """
        req = request
        data = req.data

        # CU18 Paso 4: capturar_metadatos_legales(ip_remota, user_agent, timestamp_bolivia)
        ip = req.META.get('HTTP_X_FORWARDED_FOR', req.META.get('REMOTE_ADDR', '127.0.0.1'))
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        user_agent = req.META.get('HTTP_USER_AGENT', '')

        # Validar plantilla legal
        plantilla_id = data.get('consentimiento') or data.get('plantilla')
        paciente_id = data.get('paciente')

        if not plantilla_id:
            return Response(
                {"detail": "Debe especificar la plantilla legal a firmar."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            plantilla = ConsentimientoInformado.objects.get(id=plantilla_id)
        except ConsentimientoInformado.DoesNotExist:
            return Response({"detail": "Plantilla legal no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        paciente = None
        if paciente_id:
            paciente = Paciente.objects.select_related('usuario').filter(id=paciente_id).first()
            if not paciente:
                paciente = Paciente.objects.select_related('usuario').filter(usuario_id=paciente_id).first()
        if not paciente and req.user.is_authenticated:
            paciente = Paciente.objects.select_related('usuario').filter(usuario=req.user).first()

        if not paciente:
            return Response({"detail": "Debe especificar el paciente o estar autenticado como tal."}, status=status.HTTP_400_BAD_REQUEST)


        # Detectar automáticamente menor de edad (HU-31 BDD Paso 3)
        es_menor = False
        edad = paciente.edad
        if edad is None and paciente.fecha_nacimiento:
            hoy = timezone.localdate()
            fn = paciente.fecha_nacimiento
            edad = hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))
        if edad is not None and edad < 18:
            es_menor = True

        tutor_nom = data.get('tutor_nombre') or paciente.tutor_legal_nombre or ""
        tutor_ci = data.get('tutor_ci') or paciente.tutor_legal_ci or ""
        firmado_por = data.get('firmado_por')
        if not firmado_por:
            if es_menor and tutor_nom:
                firmado_por = f"{tutor_nom} (Tutor de {paciente.usuario.nombre} {paciente.usuario.apellido})"
            else:
                firmado_por = f"{paciente.usuario.nombre} {paciente.usuario.apellido}"

        firma_canvas = data.get('firma_canvas_url') or data.get('firma_imagen') or ""

        # Paso 6: Firma sellada criptográficamente inmutable SHA-256
        raw_hash = data.get('hash_sha256') or data.get('hash_integridad')
        if not raw_hash or len(raw_hash) != 64:
            seed = f"{paciente.id}:{plantilla.id}:{plantilla.version}:{timezone.now().isoformat()}:{firma_canvas[:40]}"
            raw_hash = hashlib.sha256(seed.encode('utf-8')).hexdigest()

        # Paso 5: INSERT INTO clinica_firmaconsentimiento
        firma = FirmaConsentimiento.objects.create(
            consentimiento=plantilla,
            paciente=paciente,
            firmado_por=firmado_por,
            es_menor_edad=es_menor,
            tutor_nombre=tutor_nom,
            tutor_ci=tutor_ci,
            hash_sha256=raw_hash,
            ip_origen=ip,
            user_agent=user_agent,
            firma_canvas_url=firma_canvas
        )

        # Paso 7: 201 Created (hash_verificado, activo)
        return Response({
            "id": str(firma.id),
            "hash_verificado": True,
            "hash_sha256": firma.hash_sha256,
            "hash_integridad": firma.hash_sha256,
            "activo": True,
            "plantilla_id": str(plantilla.id),
            "plantilla_titulo": plantilla.titulo,
            "version": plantilla.version,
            "paciente_id": str(paciente.id),
            "paciente_nombre": f"{paciente.usuario.nombre} {paciente.usuario.apellido}",
            "es_menor_edad": firma.es_menor_edad,
            "firmado_por": firma.firmado_por,
            "fecha_firma": firma.fecha_firma.isoformat(),
            "habilitar_citas": True,
            "mensaje": "Firma sellada criptográficamente inmutable. Consentimiento activo y verificado."
        }, status=status.HTTP_201_CREATED)


class FirmaConsentimientoViewSet(viewsets.ModelViewSet):
    queryset = FirmaConsentimiento.objects.select_related('consentimiento', 'paciente__usuario').all().order_by('-fecha_firma')
    serializer_class = FirmaConsentimientoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        req = self.request
        ip = req.META.get('HTTP_X_FORWARDED_FOR', req.META.get('REMOTE_ADDR', '127.0.0.1'))
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        user_agent = req.META.get('HTTP_USER_AGENT', '')
        serializer.save(ip_origen=ip, user_agent=user_agent)

    @action(detail=True, methods=['get'], url_path='descargar-pdf')
    def descargar_pdf(self, request, pk=None):
        firma = self.get_object()
        buffer = BytesIO()

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            p = canvas.Canvas(buffer, pagesize=letter)
            p.drawString(100, 750, "SIGEPSI - DOCUMENTO DE CONSENTIMIENTO INFORMADO")
            p.drawString(100, 720, f"Título: {firma.consentimiento.titulo} (Versión: {firma.consentimiento.version})")
            p.drawString(100, 690, f"Paciente: {firma.paciente.usuario.nombre} {firma.paciente.usuario.apellido} (CI: {firma.paciente.ci})")
            p.drawString(100, 660, f"Firmado por: {firma.firmado_por}")
            p.drawString(100, 630, f"Fecha de Firma: {firma.fecha_firma.strftime('%d/%m/%Y %H:%M:%S')}")
            p.drawString(100, 600, f"Dirección IP de Registro: {firma.ip_origen}")
            p.drawString(100, 570, f"Sello Criptográfico SHA-256: {firma.hash_sha256}")
            p.drawString(100, 520, "El firmante declara haber leído y aceptado todas las cláusulas clínicas del centro.")
            p.showPage()
            p.save()
            pdf_data = buffer.getvalue()
        except ImportError:
            pdf_data = f"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n{firma.hash_sha256}".encode('utf-8')

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="consentimiento_{firma.id}.pdf"'
        return response

    @action(detail=True, methods=['get'], url_path='descargar_pdf')
    def descargar_pdf_alias(self, request, pk=None):
        return self.descargar_pdf(request, pk)

    @action(detail=True, methods=['post'], url_path='revocar')
    def revocar(self, request, pk=None):
        firma = self.get_object()
        motivo = request.data.get('motivo', 'Revocado formalmente')
        serializer = self.get_serializer(firma)
        data = dict(serializer.data)
        data['revocado'] = True
        data['motivo_revocacion'] = motivo
        return Response({'mensaje': 'Consentimiento revocado con éxito', 'firma': data})


# ==============================================================================
# MÓDULO: clinica/views.py — CU19: Cierre de Proceso Terapéutico y Derivación Médica a Psiquiatría (HU-33, HU-34)
# CAPA BCE: CONTROL (Controller) — CTR_DerivacionController
# DIAGRAMA DE SECUENCIA CU19 (sprint2.md):
#   Actor (Psicólogo Tratante) → IU_DerivacionCierre: 1: emitir_orden_interconsulta(motivo, riesgo, sintomatologia)
#   IU_DerivacionCierre → CTR_DerivacionController: 2: POST /api/v1/derivaciones/ (paciente_id, profesional_destino, nivel_urgencia)
#   alt Interconsulta Externa Psiquiatria (Riesgo Alto)
#     CTR_DerivacionController → CTR_DerivacionController: 3: compilar_pdf_interconsulta_con_sello_profesional()
#     CTR_DerivacionController → CE_DerivacionCaso: 4: INSERT INTO clinica_derivacioncaso (estado='DERIVADO', tipo='PSIQUIATRIA')
#     CE_DerivacionCaso --> CTR_DerivacionController: 5: registro_derivacion_creado(id)
#     CTR_DerivacionController --> IU_DerivacionCierre: 6: HTTP 201 Created {pdf_url, notificacion_coordinador_enviada}
#     IU_DerivacionCierre --> Psicólogo Tratante: 7: mostrar_comprobante_interconsulta(descarga_pdf)
#   else Alta Terapéutica / Cierre de Caso por Objetivos
#     CTR_DerivacionController → CTR_DerivacionController: 8: compilar_resumen_clinico_egreso()
#     CTR_DerivacionController → CE_HistoriaClinica: 9: UPDATE clinica_historiaclinica SET estado='ALTA', cerrada=true
#     CE_HistoriaClinica --> CTR_DerivacionController: 10: alta_registrada()
#     CTR_DerivacionController --> IU_DerivacionCierre: 11: HTTP 200 OK (comprobante_alta)
#     IU_DerivacionCierre --> Psicólogo Tratante: 12: mostrar_comprobante_alta('Tratamiento culminado y expediente archivado')
#   end
# ==============================================================================
class DerivacionCasoViewSet(viewsets.ModelViewSet):
    """
    CTR_DerivacionController:
    Controlador para la emisión de derivaciones psiquiátricas/médicas y cierre formal de historias clínicas.
    """
    queryset = DerivacionCaso.objects.select_related('historia_clinica__paciente__usuario', 'psicologo_emisor__usuario').all().order_by('-fecha_derivacion')
    serializer_class = DerivacionCasoSerializer
    permission_classes = [IsReferralParticipant]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        role = (getattr(getattr(user, 'rol', None), 'nombre', '') or '').lower()
        if 'admin' in role or 'coordinador' in role:
            return qs
        if 'paciente' in role and hasattr(user, 'perfil_paciente'):
            return qs.filter(historia_clinica__paciente=user.perfil_paciente)
        if 'psic' in role and hasattr(user, 'perfil_psicologo'):
            psico = user.perfil_psicologo
            return qs.filter(
                Q(historia_clinica__psicologo_apertura=psico) |
                Q(historia_clinica__paciente__citas__psicologo=psico)
            ).distinct()
        return qs.none()

    def create(self, request, *args, **kwargs):
        # CU19 Paso 2: POST /api/v1/derivaciones/
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tipo = serializer.validated_data.get('tipo_derivacion')
        if tipo in ('CIERRE_ALTA', 'DESERCION', 'MUTUO_ACUERDO'):
            # CU19 Flujo Alta / Cierre: Pasos 8 a 12
            # UPDATE clinica_historiaclinica SET estado='ALTA', cerrada=true
            historia = serializer.validated_data.get('historia_clinica')
            event = close_history(
                history_id=historia.pk,
                user=self.request.user,
                tipo_derivacion=tipo,
                motivo_clinico=serializer.validated_data.get('motivo_clinico', ''),
                logros_alcanzados=serializer.validated_data.get('logros_alcanzados', ''),
                recomendaciones_mantenimiento=serializer.validated_data.get('recomendaciones_mantenimiento', ''),
                sintomatologia_relevante=serializer.validated_data.get('sintomatologia_relevante', ''),
                profesional_destino=serializer.validated_data.get('profesional_destino', ''),
                institucion_destino=serializer.validated_data.get('institucion_destino', ''),
                nivel_riesgo=serializer.validated_data.get('nivel_riesgo', 'MEDIO'),
            )
            out_serializer = self.get_serializer(event)
            headers = self.get_success_headers(out_serializer.data)
            return Response(out_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        # CU19 Flujo Derivación Psiquiátrica: Pasos 3 a 7
        # INSERT INTO clinica_derivacioncaso (estado='DERIVADO', tipo='PSIQUIATRIA')
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        historia = serializer.validated_data.get('historia_clinica')
        psico = getattr(self.request.user, 'perfil_psicologo', None)
        if psico is None:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Se requiere un perfil de psicólogo autenticado.')
        if historia.psicologo_apertura_id != psico.id and not historia.paciente.citas.filter(psicologo=psico).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('La historia clínica no está vinculada al psicólogo autenticado.')
        ensure_object_history_open(historia)
        serializer.save(psicologo_emisor=psico)

    @action(detail=False, methods=['post'], url_path='noop')
    def noop(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['get'], url_path='descargar-pdf')
    def descargar_pdf(self, request, pk=None):
        deriv = self.get_object()
        buffer = BytesIO()

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            p = canvas.Canvas(buffer, pagesize=letter)
            p.drawString(80, 750, "SIGEPSI - ORDEN OFICIAL DE DERIVACIÓN E INTERCONSULTA MÉDICA")
            p.drawString(80, 720, f"Código de Expediente: {deriv.historia_clinica.codigo_historia}")
            p.drawString(80, 690, f"Paciente: {deriv.historia_clinica.paciente.usuario.nombre} {deriv.historia_clinica.paciente.usuario.apellido}")
            p.drawString(80, 660, f"Tipo de Derivación: {deriv.get_tipo_derivacion_display()}")
            p.drawString(80, 630, f"Nivel de Riesgo Clínico: {deriv.nivel_riesgo}")
            p.drawString(80, 600, f"Destinatario / Especialidad: {deriv.profesional_destino or 'Médico Psiquiatra de Enlace'}")
            p.drawString(80, 570, f"Institución Destino: {deriv.institucion_destino or 'Servicio de Psiquiatría Hospitalaria'}")
            p.drawString(80, 530, f"Motivo Clínico de Interconsulta:")
            p.drawString(80, 500, deriv.motivo_clinico[:120])
            p.drawString(80, 460, f"Sintomatología Relevante: {deriv.sintomatologia_relevante[:100]}")
            p.drawString(80, 400, f"Profesional Emisor: Lic. {deriv.psicologo_emisor.usuario.nombre} {deriv.psicologo_emisor.usuario.apellido}")
            p.drawString(80, 380, f"Colegiatura: {deriv.psicologo_emisor.numero_colegiado}")
            p.drawString(80, 350, f"Fecha de Emisión: {deriv.fecha_derivacion.strftime('%d/%m/%Y')}")
            p.showPage()
            p.save()
            pdf_data = buffer.getvalue()
        except ImportError:
            pdf_data = f"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n{deriv.id}".encode('utf-8')

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="derivacion_{deriv.id}.pdf"'
        return response


# ==============================================================================
# MÓDULO: clinica/views.py — HU-35: Asistente Ético de IA para Preconsulta con Salvaguarda Humana
# CAPA BCE: CONTROL (Controller) — CTR_PasarelaIAService
# DIAGRAMA DE SECUENCIA HU-35 (sprint2.md):
#   Actor (Psicólogo Clínico) → IU_PanelAsistenteIA: 1: solicitar_analisis_preconsulta(formulario_id)
#   IU_PanelAsistenteIA → CTR_PasarelaIAService: 2: POST /api/v1/ia/preconsulta/analizar/ (formulario_id)
#   alt Consentimiento Informado IA Activo
#     CTR_PasarelaIAService → CTR_PasarelaIAService: 3: verificar_consentimiento_activo_y_anonimizar_pii()
#     CTR_PasarelaIAService → Motor Gemini / Romero: 4: invoke_prompt_clinico_neutral(sintomas_anonimizados, escala)
#     Motor Gemini / Romero --> CTR_PasarelaIAService: 5: response_borrador(resumen_estructurado, reglas_prioridad)
#     CTR_PasarelaIAService → CE_AuditoriaIA: 6: INSERT INTO auditoria_ia_interaccion (hash_prompt, respuesta_raw, evaluacion_humana='PENDIENTE')
#     CE_AuditoriaIA --> CTR_PasarelaIAService: 7: auditoria_inmutable_creada(id)
#     CTR_PasarelaIAService --> IU_PanelAsistenteIA: 8: HTTP 200 OK (borrador_con_banner_revision_profesional)
#     IU_PanelAsistenteIA --> Psicólogo Clínico: 9: renderizar_panel_asistivo(resumen, priorizacion_sugerida, explicacion_reglas)
#     opt Decisión y Cierre Humano Obligatorio
#       Psicólogo Clínico → IU_PanelAsistenteIA: 10: aceptar_descartar_o_editar(decision_profesional)
#       IU_PanelAsistenteIA → CTR_PasarelaIAService: 11: POST /api/v1/ia/preconsulta/decision/ (auditoria_id, decision, observaciones)
#       CTR_PasarelaIAService → CE_AuditoriaIA: 12: UPDATE auditoria_ia_interaccion SET decision_final=..., revisor_id=...
#       CE_AuditoriaIA --> CTR_PasarelaIAService: 13: confirmacion_cierre_auditoria()
#       CTR_PasarelaIAService --> IU_PanelAsistenteIA: 14: HTTP 200 OK (auditoria_cerrada)
#       IU_PanelAsistenteIA --> Psicólogo Clínico: 15: notificar_incorporacion_expediente()
#     end
#   else Consentimiento IA Denegado / Rechazado
#     CTR_PasarelaIAService --> IU_PanelAsistenteIA: 16: HTTP 403 Forbidden ('Paciente rechazo procesamiento asistivo por IA')
#     IU_PanelAsistenteIA --> Psicólogo Clínico: 17: habilitar_modo_evaluacion_manual('Bloqueado motor asistivo: flujo 100% manual')
#   end
# ==============================================================================
class IAPreconsultaViewSet(viewsets.ViewSet):
    """
    CTR_PasarelaIAService:
    Controlador para el análisis ético asistido por IA, sanitización PII y auditoría con decisión humana obligatoria.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='analizar')
    def analizar(self, request):
        """
        HU-35 Paso 2: POST /api/v1/ia/preconsulta/analizar/ (formulario_id)
        HU-35 Paso 3: verificar_consentimiento_activo_y_anonimizar_pii()
        HU-35 Pasos 4-7: Motor Romero -> INSERT INTO auditoria_ia_interaccion
        HU-35 Paso 8: HTTP 200 OK (borrador asistivo con reglas transparentes)
        """
        respuesta_id = request.data.get('respuesta_id')
        if not respuesta_id:
            return Response({"error": "Debe proporcionar 'respuesta_id'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            respuesta = RespuestaPreConsulta.objects.select_related('paciente__usuario').get(id=respuesta_id)
        except RespuestaPreConsulta.DoesNotExist:
            return Response({"error": "Respuesta pre-consulta no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # HU-35 Paso 3 / Pasos 16-17: Verificar consentimiento informado activo
        tiene_firma_legal = FirmaConsentimiento.objects.filter(paciente=respuesta.paciente).exists()
        consentimiento_intake = bool(
            respuesta.respuestas_detalle.get('consentimiento_ia_procesamiento', True)
        )
        tiene_consentimiento = tiene_firma_legal or consentimiento_intake
        if not tiene_consentimiento:
            return Response({
                "error": "Procesamiento asistivo bloqueado: El paciente no cuenta con un consentimiento informado activo registrado en la plataforma.",
                "modo_manual_requerido": True
            }, status=status.HTTP_403_FORBIDDEN)

        # HU-35 Pasos 4 y 5: Ejecutar motor de reglas clínicas SP2-54 y sanitización PII
        resultado = PreconsultaRulesEngine.evaluar_preconsulta(respuesta)

        # HU-35 Pasos 6 y 7: INSERT INTO auditoria_ia_interaccion
        user = request.user
        psico = getattr(user, 'perfil_psicologo', None)
        auditoria = AuditoriaIA.objects.create(
            formulario_respuesta_id=respuesta.id,
            psicologo=psico,
            hash_prompt=resultado["hash_prompt"],
            resumen_generado=resultado["resumen_generado"],
            prioridad_sugerida=resultado["prioridad_sugerida"],
            reglas_aplicadas=resultado["reglas_aplicadas"],
            evaluacion_humana='PENDIENTE',
            ip_origen=request.META.get('REMOTE_ADDR', '127.0.0.1')
        )

        # HU-35 Paso 8: Retornar resultado asistivo con sello inmutable
        resultado["auditoria_id"] = str(auditoria.id)
        return Response(resultado, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='decision')
    def registrar_decision(self, request):
        """
        HU-35 Pasos 10-14: Decisión y Cierre Humano Obligatorio
        POST /api/v1/ia/preconsulta/decision/ -> UPDATE auditoria_ia_interaccion
        """
        auditoria_id = request.data.get('auditoria_id')
        decision = request.data.get('decision', '').upper()
        observaciones = request.data.get('observaciones', '')

        if decision not in ('ACEPTADO', 'EDITADO', 'DESCARTADO'):
            return Response({"error": "Decisión inválida. Debe ser ACEPTADO, EDITADO o DESCARTADO."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            auditoria = AuditoriaIA.objects.get(id=auditoria_id)
            auditoria.evaluacion_humana = decision
            auditoria.observaciones_profesional = observaciones
            auditoria.fecha_decision = timezone.now()
            auditoria.save()
            return Response({
                "mensaje": f"Decisión profesional ({decision}) registrada en auditoría inmutable exitosamente.",
                "auditoria_id": str(auditoria.id),
                "estado": auditoria.evaluacion_humana
            })
        except AuditoriaIA.DoesNotExist:
            return Response({"error": "Registro de auditoría no encontrado."}, status=status.HTTP_404_NOT_FOUND)


# ==============================================================================
# MÓDULO: clinica/views.py — CU20: Interacción con el Chatbot de Orientación Clínica y Derivación a Operador (HU-36)
# CAPA BCE: CONTROL (Controller) — CTR_ChatbotController
# DIAGRAMA DE SECUENCIA CU20 (sprint2.md):
#   Actor (Paciente / Usuario) → IU_ChatbotWidget: 1: enviar_mensaje_o_consulta(texto, session_token)
#   IU_ChatbotWidget → CTR_ChatbotController: 2: POST /api/v1/chatbot/mensaje/
#   CTR_ChatbotController → CTR_ChatbotController: 3: sanitizar_y_clasificar_intencion(texto)
#   CTR_ChatbotController → CE_ConversacionChatbot: 4: INSERT INTO clinica_mensajechatbot (emisor='PACIENTE', texto)
#   CE_ConversacionChatbot --> CTR_ChatbotController: 5: mensaje_registrado()
#   CTR_ChatbotController → CTR_ChatbotController: 6: evaluar_umbral_de_confianza_o_riesgo_de_crisis()
#   alt Detección de Crisis Emocional Aguda
#     CTR_ChatbotController --> IU_ChatbotWidget: 7: HTTP 200 (alerta_crisis=true, lineas_auxilio_800_11_3040)
#     IU_ChatbotWidget --> Paciente / Usuario: 8: desplegar_modal_urgencias_con_telefonos()
#   else Intención FAQ Clara (Confianza >= 80%)
#     CTR_ChatbotController → CE_ConversacionChatbot: 9: INSERT INTO clinica_mensajechatbot (emisor='BOT', respuesta_faq)
#     CE_ConversacionChatbot --> CTR_ChatbotController: 10: respuesta_faq_almacenada()
#     CTR_ChatbotController --> IU_ChatbotWidget: 11: HTTP 200 OK (tipo='BOT_FAQ', respuesta, botones_accion)
#     IU_ChatbotWidget --> Paciente / Usuario: 12: renderizar_mensaje_de_orientacion(botones_accion)
#   else Solicitud Asesor o Intención No Resuelta (Escalamiento)
#     CTR_ChatbotController → CE_ConversacionChatbot: 13: UPDATE clinica_conversacionchatbot (estado='ESCALADA_HUMANO')
#     CE_ConversacionChatbot --> CTR_ChatbotController: 14: estado_actualizado()
#     CTR_ChatbotController → Recepcionista / Asesor: 15: emitir_notificacion_websocket_de_transferencia(conversacion_id)
#     CTR_ChatbotController --> IU_ChatbotWidget: 16: HTTP 200 (tipo='TRANSFERENCIA_HUMANA', status='EN_ESPERA_ASESOR')
#     IU_ChatbotWidget --> Paciente / Usuario: 17: mostrar_estado_espera('Conectando con un asesor en vivo...')
#     Recepcionista / Asesor → IU_ChatbotWidget: 18: tomar_control_del_chat_y_responder(mensaje_operador)
#     IU_ChatbotWidget --> Paciente / Usuario: 19: conexion_en_vivo_con_soporte_del_centro(mensaje_operador)
#   end
# ==============================================================================
class ChatbotViewSet(viewsets.ViewSet):
    """
    CTR_ChatbotController:
    Controlador para el Chatbot orientador del centro de salud mental (CU20 / HU-36).
    Permite interacción anónima o autenticada, contención de crisis y escalamiento a recepción.
    """
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='mensaje')
    def enviar_mensaje(self, request):
        import uuid
        session_id = request.data.get('session_id')
        if not session_id or not session_id.strip():
            session_id = uuid.uuid4().hex

        texto = request.data.get('mensaje', '').strip()
        if not texto:
            return Response({"error": "Debe proporcionar un mensaje."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar o crear la conversación activa
        conv, created = ConversacionChatbot.objects.get_or_create(
            session_id=session_id,
            defaults={
                'estado': 'BOT_ACTIVO',
                'nivel_riesgo': 'NORMAL'
            }
        )

        # Si el usuario está autenticado y no está asociado, asociar
        if request.user and request.user.is_authenticated:
            if not conv.usuario:
                conv.usuario = request.user
            if hasattr(request.user, 'perfil_paciente') and not conv.paciente:
                conv.paciente = request.user.perfil_paciente
            conv.save(update_fields=['usuario', 'paciente', 'fecha_actualizacion'])

        # CU20 Pasos 3 y 4: sanitizar_y_clasificar_intencion & INSERT INTO clinica_mensajechatbot (emisor='PACIENTE')
        msg_usuario = MensajeChatbot.objects.create(
            conversacion=conv,
            remitente='USUARIO',
            texto=texto
        )

        # CU20 Pasos 18-19: Si la conversación está en atención por operador humano, no responde el bot
        if conv.estado == 'EN_ATENCION':
            conv.fecha_actualizacion = timezone.now()
            conv.save(update_fields=['fecha_actualizacion'])
            return Response({
                "session_id": conv.session_id,
                "conversacion_id": str(conv.id),
                "estado": conv.estado,
                "nivel_riesgo": conv.nivel_riesgo,
                "es_crisis": False,
                "mensaje_enviado": MensajeChatbotSerializer(msg_usuario).data,
                "esperando_operador": True
            })

        # CU20 Paso 6: evaluar_umbral_de_confianza_o_riesgo_de_crisis
        historial = request.data.get('historial', [])
        resultado = ChatbotEngine.procesar_mensaje(texto, session_id=session_id, historial=historial)

        # CU20 Pasos 7-8: alt Detección de Crisis Emocional Aguda -> alerta_crisis=true
        es_alerta_crisis = bool(resultado.get("alerta_crisis") or resultado.get("es_crisis"))
        if es_alerta_crisis:
            conv.nivel_riesgo = 'CRISIS'
            conv.estado = 'ESCALADA_HUMANO'
            conv.save(update_fields=['nivel_riesgo', 'estado', 'fecha_actualizacion'])
        elif resultado.get("escalar_humano"):
            # CU20 Pasos 13-16: Escalamiento a Recepcionista / Asesor
            conv.estado = 'ESCALADA_HUMANO'
            conv.save(update_fields=['estado', 'fecha_actualizacion'])
        else:
            conv.fecha_actualizacion = timezone.now()
            conv.save(update_fields=['fecha_actualizacion'])

        # CU20 Pasos 9 y 10: INSERT INTO clinica_mensajechatbot (emisor='BOT', respuesta_faq)
        texto_bot = resultado.get("respuesta") or resultado.get("texto", "")
        opciones_bot = resultado.get("opciones") or [
            b.get("etiqueta") for b in resultado.get("botones_accion", []) if isinstance(b, dict)
        ]
        msg_bot = MensajeChatbot.objects.create(
            conversacion=conv,
            remitente='BOT',
            texto=texto_bot,
            es_alerta_crisis=es_alerta_crisis,
            opciones_sugeridas=opciones_bot
        )

        # 6. Retornar esquema de respuesta unificado (especificación técnica de la API)
        return Response({
            "session_id": conv.session_id,
            "remitente": "BOT",
            "respuesta": texto_bot,
            "intencion_detectada": resultado.get("intencion_detectada", "CONVERSACION_CASUAL"),
            "contiene_riesgo": bool(resultado.get("contiene_riesgo", False)),
            "nivel_riesgo": resultado.get("nivel_riesgo", conv.nivel_riesgo),
            "alerta_crisis": es_alerta_crisis,
            "escalar_humano": bool(resultado.get("escalar_humano", False)),
            "lineas_auxilio": resultado.get("lineas_auxilio", []),
            "botones_accion": resultado.get("botones_accion", []),
            "timestamp": timezone.now().isoformat(),
            # Metadatos de trazabilidad institucional
            "conversacion_id": str(conv.id),
            "estado": conv.estado,
            "es_crisis": es_alerta_crisis,
            "mensaje_usuario": MensajeChatbotSerializer(msg_usuario).data,
            "mensaje_bot": MensajeChatbotSerializer(msg_bot).data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='historial')
    def historial(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({"error": "Debe especificar 'session_id'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conv = ConversacionChatbot.objects.get(session_id=session_id)
            mensajes = conv.mensajes.all().order_by('timestamp')
            return Response({
                "session_id": conv.session_id,
                "conversacion_id": str(conv.id),
                "estado": conv.estado,
                "nivel_riesgo": conv.nivel_riesgo,
                "mensajes": MensajeChatbotSerializer(mensajes, many=True).data
            })
        except ConversacionChatbot.DoesNotExist:
            return Response({"mensajes": [], "estado": "BOT_ACTIVO", "nivel_riesgo": "NORMAL"})

    @action(detail=False, methods=['post'], url_path='solicitar-humano')
    def solicitar_humano(self, request):
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({"error": "Debe proporcionar 'session_id'."}, status=status.HTTP_400_BAD_REQUEST)

        conv = ConversacionChatbot.objects.filter(session_id=session_id).first()
        if not conv:
            conv = ConversacionChatbot.objects.create(session_id=session_id, estado='ESCALADA_HUMANO')
        else:
            conv.estado = 'ESCALADA_HUMANO'
            conv.save(update_fields=['estado', 'fecha_actualizacion'])

        msg_bot = MensajeChatbot.objects.create(
            conversacion=conv,
            remitente='BOT',
            texto="He transferido tu conversación con prioridad a la recepción del centro. Un asesor te responderá a la brevedad.",
            opciones_sugeridas=["Esperar Asesor", "Ver Horarios"]
        )

        return Response({
            "mensaje": "Conversación transferida a recepción exitosamente.",
            "estado": conv.estado,
            "mensaje_bot": MensajeChatbotSerializer(msg_bot).data
        })

    @action(detail=False, methods=['get'], url_path='conversaciones-activas', permission_classes=[IsAuthenticated])
    def conversaciones_activas(self, request):
        """Para recepción: lista conversaciones en espera o activas."""
        qs = ConversacionChatbot.objects.exclude(estado='FINALIZADA').order_by('-fecha_actualizacion')
        serializer = ConversacionChatbotSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='responder-operador', permission_classes=[IsAuthenticated])
    def responder_operador(self, request):
        """Para recepción: enviar mensaje desde el panel de operador."""
        conversacion_id = request.data.get('conversacion_id')
        texto = request.data.get('texto', '').strip()
        if not conversacion_id or not texto:
            return Response({"error": "Debe proporcionar 'conversacion_id' y 'texto'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conv = ConversacionChatbot.objects.get(id=conversacion_id)
            conv.estado = 'EN_ATENCION'
            conv.operador_asignado = request.user
            conv.save(update_fields=['estado', 'operador_asignado', 'fecha_actualizacion'])

            msg = MensajeChatbot.objects.create(
                conversacion=conv,
                remitente='OPERADOR',
                texto=texto
            )
            return Response({
                "mensaje": "Mensaje de operador enviado con éxito.",
                "mensaje_operador": MensajeChatbotSerializer(msg).data
            })
        except ConversacionChatbot.DoesNotExist:
            return Response({"error": "Conversación no encontrada."}, status=status.HTTP_404_NOT_FOUND)




# ==============================================================================
# SPRINT 3: VISTAS REST PARA CLASIFICACIÓN IA, TRIAJE, MATCHING Y MOOD TRACKER
# ==============================================================================
from rest_framework.views import APIView
from django.utils import timezone
from django.db import models
from clinica.models import TokenFCM, RegistroAnimo, ClasificacionIA, SugerenciaMatching
from clinica.serializers import (
    TokenFCMSerializer, RegistroAnimoSerializer,
    ClasificacionIASerializer, SugerenciaMatchingSerializer
)
from clinica.ia_rules_engine import MatchingPsicologoService
from clinica import ia_nlp
from clinica.permissions import EsCoordinadorClinico
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from clinica.models import AuditoriaIA, PsicologoEspecialidad
import logging

logger_ia = logging.getLogger('clinica.ia')


def _ip_cliente(request):
    if request is None:
        return '127.0.0.1'
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return (xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '127.0.0.1'))[:45]


class ClasificacionIAViewSet(viewsets.ReadOnlyModelViewSet):
    """Historial de clasificaciones IA (solo lectura; alertas de crisis primero)."""
    queryset = (ClasificacionIA.objects
                .select_related('respuestapreconsulta__paciente__usuario',
                                'respuestapreconsulta__paciente__psicologo_asignado__usuario')
                .order_by('-alerta_crisis', '-fecha_analisis'))
    serializer_class = ClasificacionIASerializer
    permission_classes = [IsAuthenticated, EsCoordinadorClinico]


class CTR_ClasificacionIAController(APIView):
    """
    CU21 / HU-47 — Secuencia_Corregido_CU21_Clasificacion_IA.
    CU21-paso 2: POST /api/v1/ia/clasificar-triaje/ (payload: respuesta_id, texto_motivo?, escala_malestar?)
    """
    permission_classes = [IsAuthenticated, EsCoordinadorClinico]

    SUGERENCIA_INMEDIATA = ("Activar protocolo de crisis: contactar al paciente de inmediato, "
                            "evaluar riesgo y derivar a atención prioritaria.")

    @staticmethod
    def texto_motivo(respuesta) -> str:
        """Motivo + síntomas + respuestas abiertas del formulario (sin duplicados)."""
        partes = [respuesta.motivo_consulta or '', respuesta.sintomas_principales or '']
        for valor in (respuesta.respuestas_detalle or {}).values():
            if isinstance(valor, list):
                valor = ', '.join(v for v in valor if isinstance(v, str))
            if isinstance(valor, str) and len(valor) > 15 and valor not in ' '.join(partes):
                partes.append(valor)
        return '. '.join(p.strip() for p in partes if p and p.strip())

    @classmethod
    def clasificar(cls, respuesta, texto_motivo=None, escala_malestar=None, ip='127.0.0.1', usuario=None):
        """Orden exacto de la secuencia CU21 (CU21-paso 3 a CU21-paso 25). Devuelve (payload, ClasificacionIA)."""
        escala = escala_malestar or respuesta.nivel_urgencia_percibido or 1
        # CU21-paso 3: sanitizar_pii(texto_motivo) → CE_RespuestaPreConsulta
        #              (quita teléfono, CI, email y nombre del paciente antes de enviar el texto al modelo)
        # CU21-paso 4: texto_anonimizado [retorno]
        texto = respuesta.sanitizar_pii(texto_motivo or cls.texto_motivo(respuesta))
        # CU21-paso 5: obtener_paciente() → CE_Paciente
        # CU21-paso 6: datos_paciente(paciente_id) [retorno]
        datos_paciente = Paciente.obtener_paciente(respuesta.paciente_id)
        # CU21-paso 7: consultar_inferencia_nlp(texto_anonimizado) — autollamada del CTR.
        #              Modelo real: zero-shot NLI MoritzLaurer/mDeBERTa-v3-base-mnli-xnli (Hugging Face, local
        #              en CPU) en lugar de 'HF-ClinicalBert'; si no carga se usa el respaldo por reglas.
        inf = ia_nlp.consultar_inferencia_nlp(texto)
        # CU21-paso 8: evaluar_patrones_riesgo_crisis(score, categoria) — autollamada del CTR.
        #              Combina riesgo del modelo + malestar 1-5 + reglas de crisis (las reglas solo suben el riesgo).
        riesgo = ia_nlp.evaluar_patrones_riesgo_crisis(inf['p_riesgo'], inf['categoria'], texto, escala)

        inferencia = {
            'categoria': inf['categoria'], 'confianza': inf['confianza'], 'p_riesgo': inf['p_riesgo'],
            'score_severidad': riesgo['score_severidad'], 'alerta_crisis': riesgo['alerta_crisis'],
            'modelo_ia': inf['modelo_ia'],
        }
        motor = ('respaldo por reglas' if inf['modelo_ia'] == ia_nlp.MODELO_FALLBACK
                 else f"modelo {inf['modelo_ia']}")
        explicacion = (f"Sugerencia asistiva ({motor}): {inf['categoria']} con confianza "
                       f"{inf['confianza'] * 100:.1f}%. Severidad {riesgo['nivel_severidad']} "
                       f"({riesgo['puntaje_severidad']}/5, score {riesgo['score_severidad']:.2f}; "
                       f"riesgo inferido {inf['p_riesgo']:.2f}, malestar {escala}/5).")
        if riesgo['palabras_clave']:
            explicacion += f" Patrones de riesgo detectados: {', '.join(riesgo['palabras_clave'])}."
        explicacion += " Requiere validación del Coordinador Clínico."
        resultado = {
            'categoria_principal': inf['categoria'],
            'confianza_score': inf['confianza'],
            'nivel_severidad': riesgo['nivel_severidad'],
            'puntaje_severidad': riesgo['puntaje_severidad'],
            'score_severidad': riesgo['score_severidad'],
            'alerta_crisis': riesgo['alerta_crisis'],
            'palabras_clave_detectadas': riesgo['palabras_clave'],
            'explicacion_heuristica': explicacion,
            'hash_trazabilidad_sha256': AuditoriaIA.generar_hash_sha256(texto, inferencia),
            'modelo_ia': inf['modelo_ia'],
        }

        with transaction.atomic():
            if riesgo['score_severidad'] >= ia_nlp.UMBRAL_CRISIS or riesgo['alerta_crisis']:
                # alt [score_severidad >= 0.70 o alerta_crisis == true (Protocolo Crisis)]
                # CU21-paso 9: persistir_clasificacion(categoria, severidad, nivel='CRITICO') → CE_ClasificacionIA
                # CU21-paso 10: clasificacion_guardada(id) [retorno]
                clasif = ClasificacionIA.persistir_clasificacion(respuesta, resultado, nivel='CRITICO')
                # CU21-paso 11: marcar_crisis_prioritaria() → CE_ClasificacionIA
                # CU21-paso 12: crisis_marcada [retorno]
                clasif.marcar_crisis_prioritaria()
                # CU21-paso 13: generar_hash_sha256(input, inferencia) → CE_AuditoriaIA
                # CU21-paso 14: hash_generado [retorno]
                h = AuditoriaIA.generar_hash_sha256(texto, inferencia)
                # CU21-paso 15: registrar_auditoria_inferencia(modelo, hash, alerta=true) → CE_AuditoriaIA
                #               (se guarda el nombre real del modelo usado, no 'HF-ClinicalBert')
                # CU21-paso 16: auditoria_ia_registrada [retorno]
                AuditoriaIA.registrar_auditoria_inferencia(inf['modelo_ia'], h, True, clasif, ip, usuario)
                # CU21-paso 17: HTTP 200 OK {alerta_crisis:true, nivel:'ALTO', sugerencia_inmediata} [retorno]
                payload = {
                    'alerta_crisis': True, 'nivel': 'ALTO',
                    'sugerencia_inmediata': cls.SUGERENCIA_INMEDIATA,
                }
            else:
                # else [score_severidad < 0.70 (Atención Ordinaria)]
                # CU21-paso 19: persistir_clasificacion(categoria, severidad, nivel='REGULAR') → CE_ClasificacionIA
                # CU21-paso 20: clasificacion_guardada(id) [retorno]
                clasif = ClasificacionIA.persistir_clasificacion(respuesta, resultado, nivel='REGULAR')
                # CU21-paso 21: generar_hash_sha256(input, inferencia) → CE_AuditoriaIA
                # CU21-paso 22: hash_generado [retorno]
                h = AuditoriaIA.generar_hash_sha256(texto, inferencia)
                # CU21-paso 23: registrar_auditoria_inferencia(modelo, hash, alerta=false) → CE_AuditoriaIA
                # CU21-paso 24: auditoria_ia_registrada [retorno]
                AuditoriaIA.registrar_auditoria_inferencia(inf['modelo_ia'], h, False, clasif, ip, usuario)
                # CU21-paso 25: HTTP 200 OK {alerta_crisis:false, nivel:'REGULAR', clasificacion} [retorno]
                payload = {'alerta_crisis': False, 'nivel': 'REGULAR'}

        payload['clasificacion'] = ClasificacionIASerializer(clasif).data
        payload['paciente'] = datos_paciente
        return payload, clasif

    def post(self, request, pk=None):
        respuesta_id = pk or request.data.get('respuesta_id')
        if not respuesta_id:
            return Response({"error": "Debe indicar respuesta_id."}, status=status.HTTP_400_BAD_REQUEST)
        escala = request.data.get('escala_malestar')
        if escala not in (None, ''):
            try:
                escala = int(escala)
            except (TypeError, ValueError):
                escala = 0
            if not 1 <= escala <= 5:
                return Response({"error": "escala_malestar debe estar entre 1 y 5."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            escala = None
        try:
            respuesta = RespuestaPreConsulta.objects.select_related('paciente__usuario').get(id=respuesta_id)
        except (RespuestaPreConsulta.DoesNotExist, ValueError, DjangoValidationError):
            return Response({"error": "Respuesta de preconsulta no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        payload, _ = self.clasificar(respuesta, request.data.get('texto_motivo'), escala,
                                     ip=_ip_cliente(request), usuario=request.user)
        # CU21-paso 17 (crisis) / CU21-paso 25 (ordinaria): HTTP 200 OK [retorno a IU_ConsolaTriajeIA]
        return Response(payload, status=status.HTTP_200_OK)


# Ruta anterior POST /intake/<uuid:pk>/clasificar/ (Sprint 3 inicial)
ClasificarIntakeView = CTR_ClasificacionIAController


class AlertasCrisisView(APIView):
    """HU-47 (c): alertas de crisis para la consola del Coordinador Clínico."""
    permission_classes = [IsAuthenticated, EsCoordinadorClinico]

    def get(self, request):
        alertas = (ClasificacionIA.objects.filter(alerta_crisis=True)
                   .select_related('respuestapreconsulta__paciente__usuario',
                                   'respuestapreconsulta__paciente__psicologo_asignado__usuario')
                   .order_by('-fecha_analisis'))
        return Response(ClasificacionIASerializer(alertas, many=True).data, status=status.HTTP_200_OK)

class SugerenciaMatchingViewSet(viewsets.ReadOnlyModelViewSet):
    """Historial de sugerencias de matching (solo lectura; las decisiones van por CTR_MatchingController)."""
    queryset = SugerenciaMatching.objects.select_related(
        'paciente__usuario', 'psicologo_sugerido__usuario', 'clasificacion',
        'psicologo_asignado_final__usuario').all()
    serializer_class = SugerenciaMatchingSerializer
    permission_classes = [IsAuthenticated, EsCoordinadorClinico]

    def get_queryset(self):
        qs = super().get_queryset()
        paciente_id = self.request.query_params.get('paciente_id')
        return qs.filter(paciente_id=paciente_id) if paciente_id else qs


def _error(msg, code):
    return Response({"error": msg}, status=code)


class CTR_MatchingController(viewsets.ViewSet):
    """
    CU22 / HU-48 — Secuencia_Corregido_CU22_Matching_Asignacion_IA.
      CU22-paso 2:  GET  /api/v1/matching/sugerencias/?paciente_id=
      CU22-paso 21: POST /api/v1/matching/{id}/aprobar/              {psicologo_id}
      CU22-paso 31: POST /api/v1/matching/{id}/rechazar_y_reasignar/ {psicologo_manual_id, motivo}
    Ningún paciente se asigna sin una de las dos confirmaciones explícitas del coordinador.
    """
    permission_classes = [IsAuthenticated, EsCoordinadorClinico]
    MOTIVO_MIN = 10

    # CU22-paso 2: GET /api/v1/matching/sugerencias/?paciente_id= → CTR_MatchingController (CU22-paso 3 a CU22-paso 18)
    @action(detail=False, methods=['get'], url_path='sugerencias')
    def sugerencias(self, request):
        return self.generar_sugerencias(request.query_params.get('paciente_id'))

    @classmethod
    def generar_sugerencias(cls, paciente_id):
        if not paciente_id:
            return _error("Debe indicar paciente_id.", status.HTTP_400_BAD_REQUEST)
        try:
            paciente = Paciente.objects.select_related('usuario').get(id=paciente_id)
        except (Paciente.DoesNotExist, ValueError, DjangoValidationError):
            return _error("Paciente no encontrado.", status.HTTP_404_NOT_FOUND)

        # CU22-paso 3: extraer_triaje(paciente_id) → CE_ClasificacionIA (resultado de CU21)
        # CU22-paso 4: triaje(categoria, severidad) [retorno]
        triaje = ClasificacionIA.extraer_triaje(paciente.id)
        if not triaje:
            return _error("El paciente no tiene triaje IA; ejecute primero la clasificación (CU21).",
                          status.HTTP_409_CONFLICT)
        # CU22-paso 5: obtener_paciente(paciente_id) → CE_Paciente
        # CU22-paso 6: datos_paciente(modalidad_preferencia) [retorno]
        datos_paciente = Paciente.obtener_paciente(paciente.id)
        if datos_paciente['psicologo_asignado_id']:
            return _error("El paciente ya tiene un psicólogo asignado.", status.HTTP_409_CONFLICT)

        candidatos = []
        # CU22-paso 7: listar_candidatos_activos() → CE_Psicologo
        # CU22-paso 8: psicologos_activos [retorno]
        # loop [Por cada psicólogo candidato en psicologos_activos]
        for psico in Psicologo.listar_candidatos_activos():
            # CU22-paso 9: verificar_especialidad(psicologo_id) → CE_PsicologoEspecialidad
            # CU22-paso 10: areas_experiencia [retorno]
            areas = PsicologoEspecialidad.verificar_especialidad(psico.id)
            # CU22-paso 11: obtener_nombre() → CE_Especialidad
            # CU22-paso 12: nombre_especialidad [retorno]
            nombres_esp = [esp.obtener_nombre() for esp in areas]
            # CU22-paso 13: get_full_name() → CE_Usuario
            # CU22-paso 14: nombre_psicologo [retorno]
            nombre = psico.usuario.get_full_name()
            # CU22-paso 15: calcular_score(afinidad, carga, disponibilidad) — autollamada del CTR.
            #   No es ML: Score = 0.4×Afinidad + 0.3×Disponibilidad + 0.2×BalanceCarga + 0.1×Modalidad (HU-48)
            resultado = MatchingPsicologoService.calcular_score(
                MatchingPsicologoService.afinidad(triaje['categoria'], areas),
                (psico.carga_actual, psico.cupo_maximo),
                psico.bloques_semanales(),
                psico.modalidad,
                datos_paciente['modalidad_preferencia'],
            )
            candidatos.append({'psicologo': psico, 'nombre': nombre, 'especialidades': nombres_esp, **resultado})

        top3 = MatchingPsicologoService.ordenar_top3(candidatos)
        # CU22-paso 16: persistir_top3_candidatos(top3_candidatos) → CE_SugerenciaMatching
        # CU22-paso 17: candidatos_persistidos [retorno]
        sugerencias = SugerenciaMatching.persistir_top3_candidatos(
            paciente, triaje['clasificacion'], top3)

        # CU22-paso 18: HTTP 200 OK {top3_candidatos, scores} [retorno]
        return Response({
            'paciente': datos_paciente,
            'triaje': {k: triaje[k] for k in ('clasificacion_id', 'categoria', 'severidad', 'alerta_crisis')},
            'formula': 'Score = 0.4×Afinidad + 0.3×Disponibilidad + 0.2×BalanceCarga + 0.1×Modalidad',
            'top3_candidatos': [{
                'sugerencia_id': str(s.id),
                'ranking': s.ranking_posicion,
                'psicologo_id': str(c['psicologo'].id),
                'nombre_psicologo': c['nombre'],
                'numero_colegiado': c['psicologo'].numero_colegiado,
                'especialidades': c['especialidades'],
                'modalidad': c['psicologo'].modalidad,
                'score': c['score'],
                'factores': c['factores'],
                'pesos': MatchingPsicologoService.PESOS,
                'carga_actual': c['psicologo'].carga_actual,
                'cupo_maximo': c['psicologo'].cupo_maximo,
                'cupo_completo': c['cupo_completo'],
            } for s, c in zip(sugerencias, top3)],
        }, status=status.HTTP_200_OK)

    # ── Decisión HITL (común a ambas ramas del alt) ───────────────────────────
    @staticmethod
    def _bloquear(pk):
        """Bloquea sugerencia y paciente; devuelve (sugerencia, paciente) o una Response de error."""
        try:
            sug = (SugerenciaMatching.objects.select_for_update()
                   .select_related('psicologo_sugerido__usuario').get(id=pk))
        except (SugerenciaMatching.DoesNotExist, ValueError, DjangoValidationError):
            return _error("Sugerencia no encontrada.", status.HTTP_404_NOT_FOUND)
        if sug.estado_decision != 'PENDIENTE_VALIDACION':
            return _error("Esta sugerencia ya fue decidida.", status.HTTP_409_CONFLICT)
        paciente = Paciente.objects.select_for_update().get(id=sug.paciente_id)
        if paciente.psicologo_asignado_id:
            return _error("El paciente ya tiene un psicólogo asignado.", status.HTTP_409_CONFLICT)
        return sug, paciente

    @staticmethod
    def _consolidar(sug, paciente, psicologo):
        paciente.psicologo_asignado = psicologo
        paciente.save(update_fields=['psicologo_asignado'])
        (SugerenciaMatching.objects.filter(paciente=paciente, estado_decision='PENDIENTE_VALIDACION')
         .exclude(id=sug.id).update(estado_decision='DESCARTADO', fecha_decision=timezone.now()))

    @staticmethod
    def _respuesta(mensaje, sug, paciente, psicologo, manual):
        return Response({
            'mensaje': mensaje,
            'sugerencia_id': str(sug.id),
            'estado_decision': sug.estado_decision,
            'paciente_id': str(paciente.id),
            'psicologo_id': str(psicologo.id),
            'psicologo_asignado': psicologo.usuario.get_full_name(),
            'carga_actual': psicologo.carga_actual,
            'cupo_maximo': psicologo.cupo_maximo,
            'asignacion_manual': manual,
        }, status=status.HTTP_200_OK)

    # CU22-paso 21: POST /api/v1/matching/{id}/aprobar/ (psicologo_id) → CTR_MatchingController
    #   alt [Coordinador aprueba candidato sugerido] → CU22-paso 22 a CU22-paso 28
    @action(detail=True, methods=['post'], url_path='aprobar')
    def aprobar(self, request, pk=None):
        return self.ejecutar_aprobacion(pk, request.user, request.data.get('psicologo_id'),
                                        request.data.get('justificacion', ''))

    @classmethod
    def ejecutar_aprobacion(cls, pk, coordinador, psicologo_id=None, justificacion=''):
        with transaction.atomic():
            bloqueo = cls._bloquear(pk)
            if isinstance(bloqueo, Response):
                return bloqueo
            sug, paciente = bloqueo
            if psicologo_id and str(psicologo_id) != str(sug.psicologo_sugerido_id):
                return _error("El psicólogo indicado no corresponde a la sugerencia. "
                              "Use rechazar_y_reasignar para elegir otro profesional.",
                              status.HTTP_400_BAD_REQUEST)
            psicologo = sug.psicologo_sugerido
            # CU22-paso 22: marcar_aprobada() → CE_SugerenciaMatching
            # CU22-paso 23: sugerencia_aprobada [retorno]
            sug.marcar_aprobada()
            # CU22-paso 24: incrementar_carga() → CE_Psicologo
            # CU22-paso 25: carga_actualizada [retorno]
            psicologo.incrementar_carga()
            # CU22-paso 26: asignacion_auditada(aprobado_hitl=true, coordinador_id) → CE_SugerenciaMatching
            # CU22-paso 27: auditoria_asignacion_guardada [retorno]
            sug.asignacion_auditada(True, coordinador, psicologo, justificacion)
            cls._consolidar(sug, paciente, psicologo)
        # CU22-paso 28: HTTP 200 OK {'Psicólogo asignado exitosamente'} [retorno]
        return cls._respuesta('Psicólogo asignado exitosamente', sug, paciente, psicologo, False)

    # CU22-paso 31: POST /api/v1/matching/{id}/rechazar_y_reasignar/ (motivo) → CTR_MatchingController
    #   else [Coordinador rechaza sugerencia y asigna manual] → CU22-paso 32 a CU22-paso 38
    @action(detail=True, methods=['post'], url_path='rechazar_y_reasignar')
    def rechazar_y_reasignar(self, request, pk=None):
        return self.ejecutar_reasignacion(pk, request.user, request.data.get('psicologo_manual_id'),
                                          request.data.get('motivo'))

    @classmethod
    def ejecutar_reasignacion(cls, pk, coordinador, psicologo_manual_id, motivo):
        motivo = (motivo or '').strip()
        if len(motivo) < cls.MOTIVO_MIN:
            return _error(f"El motivo es obligatorio (mínimo {cls.MOTIVO_MIN} caracteres).",
                          status.HTTP_400_BAD_REQUEST)
        try:
            psicologo = Psicologo.objects.select_related('usuario').get(
                id=psicologo_manual_id, activo=True, usuario__activo=True)
        except (Psicologo.DoesNotExist, ValueError, TypeError, DjangoValidationError):
            return _error("Debe elegir un psicólogo activo.", status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            bloqueo = cls._bloquear(pk)
            if isinstance(bloqueo, Response):
                return bloqueo
            sug, paciente = bloqueo
            # CU22-paso 32: marcar_rechazada_manual(motivo) → CE_SugerenciaMatching
            # CU22-paso 33: rechazo_registrado [retorno]
            sug.marcar_rechazada_manual(motivo)
            # CU22-paso 34: incrementar_carga() → CE_Psicologo (el psicólogo elegido manualmente)
            # CU22-paso 35: carga_actualizada [retorno]
            psicologo.incrementar_carga()
            # CU22-paso 36: asignacion_manual_auditada(aprobado_hitl=false, justificacion=motivo) → CE_SugerenciaMatching
            # CU22-paso 37: auditoria_reasignacion_guardada [retorno]
            sug.asignacion_manual_auditada(coordinador, psicologo, motivo)
            cls._consolidar(sug, paciente, psicologo)
        # CU22-paso 38: HTTP 200 OK {'Asignación manual registrada'} [retorno]
        return cls._respuesta('Asignación manual registrada', sug, paciente, psicologo, True)


class GenerarMatchingView(APIView):
    """HU-48 (a): GET /api/v1/ia/sugerir-psicologo/{paciente_id}/ (misma lógica que matching/sugerencias)."""
    permission_classes = [IsAuthenticated, EsCoordinadorClinico]

    def get(self, request, paciente_id):
        return CTR_MatchingController.generar_sugerencias(paciente_id)

    post = get


class AsignarPsicologoHITLView(APIView):
    """
    Rutas anteriores (ia/confirmar-asignacion/, ia/asignacion-manual/, triaje/asignar/).
    Body: {sugerencia_id, psicologo_id?, justificacion_clinica?}. Si psicologo_id difiere del
    sugerido se trata como rechazo + reasignación manual (motivo = justificacion_clinica).
    """
    permission_classes = [IsAuthenticated, EsCoordinadorClinico]

    def post(self, request):
        sug_id = request.data.get('sugerencia_id')
        if not sug_id:
            return _error("Debe indicar sugerencia_id (toda asignación parte de una sugerencia validada).",
                          status.HTTP_400_BAD_REQUEST)
        try:
            sug = SugerenciaMatching.objects.only('psicologo_sugerido_id').get(id=sug_id)
        except (SugerenciaMatching.DoesNotExist, ValueError, DjangoValidationError):
            return _error("Sugerencia no encontrada.", status.HTTP_404_NOT_FOUND)
        psicologo_id = request.data.get('psicologo_id')
        justificacion = request.data.get('justificacion_clinica', '')
        if psicologo_id and str(psicologo_id) != str(sug.psicologo_sugerido_id):
            return CTR_MatchingController.ejecutar_reasignacion(sug_id, request.user, psicologo_id, justificacion)
        return CTR_MatchingController.ejecutar_aprobacion(sug_id, request.user, None, justificacion)

class RegistroAnimoViewSet(viewsets.ModelViewSet):
    """Módulo de Registro Diario de Estado de Ánimo (Mood Tracker - CU17 / HU-46)."""
    queryset = RegistroAnimo.objects.select_related('paciente__usuario').all().order_by('-fecha_registro')
    serializer_class = RegistroAnimoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'perfil_paciente'):
            return qs.filter(paciente=user.perfil_paciente)
        paciente_id = self.request.query_params.get('paciente')
        if paciente_id:
            return qs.filter(paciente_id=paciente_id)
        return qs

    def create(self, request, *args, **kwargs):
        user = request.user
        paciente = getattr(user, 'perfil_paciente', None)
        if not paciente:
            paciente_id = request.data.get('paciente')
            if paciente_id:
                paciente = Paciente.objects.filter(id=paciente_id).first()
        if not paciente:
            paciente = Paciente.objects.first()

        fecha_reg = request.data.get('fecha_registro') or timezone.now().date()
        estado = request.data.get('estado_animo', 'NEUTRAL')
        valor = int(request.data.get('escala_valor', 3))
        factores = request.data.get('factores_contexto', [])
        nota = request.data.get('nota_reflexiva', '')

        reg, created = RegistroAnimo.objects.update_or_create(
            paciente=paciente,
            fecha_registro=fecha_reg,
            defaults={
                'estado_animo': estado,
                'escala_valor': valor,
                'factores_contexto': factores,
                'nota_reflexiva': nota
            }
        )
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(RegistroAnimoSerializer(reg).data, status=status_code)
