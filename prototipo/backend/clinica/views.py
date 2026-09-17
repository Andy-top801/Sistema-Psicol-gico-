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
# ==============================================================================
from io import BytesIO
from django.utils import timezone
from django.http import HttpResponse
from clinica.permissions import IsTreatingPsychologistOrAdmin
from clinica.cie_catalog import search_cie10
from clinica.ia_rules_engine import PreconsultaRulesEngine
from clinica.models import (
    FormularioPreConsulta, RespuestaPreConsulta,
    HistoriaClinica, DiagnosticoCIE,
    NotaSesion, EvolucionClinica,
    TareaTerapeutica, EvidenciaTarea,
    ConsentimientoInformado, FirmaConsentimiento,
    DerivacionCaso, AuditoriaIA
)
from clinica.serializers import (
    FormularioPreConsultaSerializer, RespuestaPreConsultaSerializer,
    HistoriaClinicaSerializer, DiagnosticoCIESerializer,
    NotaSesionSerializer, EvolucionClinicaSerializer,
    TareaTerapeuticaSerializer, EvidenciaTareaSerializer,
    ConsentimientoInformadoSerializer, FirmaConsentimientoSerializer,
    DerivacionCasoSerializer, AuditoriaIASerializer
)


# ──────────────────────────────────────────────────────────────────────────────
# CU14: Formulario Pre-Consulta e Intake Digital
# ──────────────────────────────────────────────────────────────────────────────
class FormularioPreConsultaViewSet(viewsets.ModelViewSet):
    queryset = FormularioPreConsulta.objects.all().order_by('-fecha_creacion')
    serializer_class = FormularioPreConsultaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        activo = self.request.query_params.get('activo')
        if activo is not None:
            qs = qs.filter(activo=activo.lower() in ('true', '1'))
        return qs


class RespuestaPreConsultaViewSet(viewsets.ModelViewSet):
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

        # Filtro por estado
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado.upper())

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        # Si el usuario es un paciente autenticado y no se indicó paciente, asignar el suyo
        if hasattr(user, 'perfil_paciente') and not serializer.validated_data.get('paciente'):
            serializer.save(paciente=user.perfil_paciente)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], url_path='marcar-revisado')
    def marcar_revisado(self, request, pk=None):
        respuesta = self.get_object()
        respuesta.estado = 'REVISADO'
        respuesta.save()
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


# ──────────────────────────────────────────────────────────────────────────────
# CU15: Historia Clínica Psicológica Electrónica (RBAC Clínico)
# ──────────────────────────────────────────────────────────────────────────────
class HistoriaClinicaViewSet(viewsets.ModelViewSet):
    queryset = HistoriaClinica.objects.select_related('paciente__usuario', 'psicologo_apertura__usuario').prefetch_related('diagnosticos').all().order_by('-fecha_apertura')
    serializer_class = HistoriaClinicaSerializer
    permission_classes = [IsTreatingPsychologistOrAdmin]

    def get_queryset(self):
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
        user = self.request.user
        psico = getattr(user, 'perfil_psicologo', None)
        if not psico and not serializer.validated_data.get('psicologo_apertura'):
            # Si es admin creando en nombre del centro, asignar primer psicólogo activo
            psico = Psicologo.objects.filter(activo=True).first()
        serializer.save(psicologo_apertura=serializer.validated_data.get('psicologo_apertura') or psico)

    @action(detail=True, methods=['get', 'post'], url_path='diagnosticos')
    def diagnosticos(self, request, pk=None):
        historia = self.get_object()
        if request.method == 'GET':
            serializer = DiagnosticoCIESerializer(historia.diagnosticos.all(), many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            data = request.data.copy()
            data['historia_clinica'] = str(historia.id)
            serializer = DiagnosticoCIESerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

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
                "justificacion": e.justificacion,
                "acuerdos": e.acuerdos_pactados
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
                "dificultad": t.evidencia.dificultad_percibida if hasattr(t, 'evidencia') else None
            })

        timeline_items.sort(key=lambda x: str(x["fecha"]), reverse=True)
        return Response(timeline_items)


class DiagnosticoCIEViewSet(viewsets.ModelViewSet):
    queryset = DiagnosticoCIE.objects.all().order_by('-fecha_diagnostico')
    serializer_class = DiagnosticoCIESerializer
    permission_classes = [IsAuthenticated]


# ──────────────────────────────────────────────────────────────────────────────
# CU16: Notas Clínicas SOAP (Autoguardado y Firma Inmutable)
# ──────────────────────────────────────────────────────────────────────────────
class NotaSesionViewSet(viewsets.ModelViewSet):
    queryset = NotaSesion.objects.select_related('historia_clinica__paciente__usuario', 'psicologo__usuario', 'cita').all().order_by('-fecha_sesion')
    serializer_class = NotaSesionSerializer
    permission_classes = [IsTreatingPsychologistOrAdmin]

    def perform_create(self, serializer):
        user = self.request.user
        psico = getattr(user, 'perfil_psicologo', None)
        if not psico and not serializer.validated_data.get('psicologo'):
            psico = Psicologo.objects.filter(activo=True).first()
        serializer.save(psicologo=serializer.validated_data.get('psicologo') or psico)

    @action(detail=True, methods=['patch'], url_path='borrador')
    def guardar_borrador(self, request, pk=None):
        """Autoguardado reactivo cada 30 segundos (CU16 Criterio b)."""
        nota = self.get_object()
        if nota.estado_guardado == 'FIRMADA':
            return Response({"error": "La nota ya se encuentra consolidada y firmada de manera inmutable."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(nota, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(estado_guardado='BORRADOR')
        return Response({
            "mensaje": "Borrador de nota SOAP autoguardado exitosamente.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='firmar')
    def firmar_nota(self, request, pk=None):
        """Firma legal e inmutabilidad de la nota vinculada a cita atendida (CU16 Criterio c)."""
        nota = self.get_object()
        nota.estado_guardado = 'FIRMADA'
        nota.fecha_firma = timezone.now()
        nota.save()

        # Si tiene cita asociada, actualizar su estado a REALIZADA
        if nota.cita:
            nota.cita.estado = 'REALIZADA'
            nota.cita.save()

        return Response({
            "mensaje": "Nota SOAP firmada y consolidada inmutablemente.",
            "id": str(nota.id),
            "estado": nota.estado_guardado,
            "fecha_firma": nota.fecha_firma.isoformat()
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────────────────────
# CU17: Evolución Longitudinal, Tareas y Evidencias
# ──────────────────────────────────────────────────────────────────────────────
class EvolucionClinicaViewSet(viewsets.ModelViewSet):
    queryset = EvolucionClinica.objects.select_related('historia_clinica__paciente__usuario').all().order_by('-fecha_registro')
    serializer_class = EvolucionClinicaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        evolucion = serializer.save()
        # Si se detecta retroceso o crisis, generar alerta clínica de prioridad alta (CU17 / HU-28)
        if evolucion.estado_avance == 'RETROCESO_CRISIS':
            try:
                from agenda.models import Alerta
                paciente = evolucion.historia_clinica.paciente
                psico = evolucion.historia_clinica.psicologo_apertura
                Alerta.objects.create(
                    paciente=paciente,
                    psicologo=psico,
                    tipo='CRISIS_RETROCESO',
                    severidad='ALTA',
                    mensaje=f"Alerta de Retroceso/Crisis reportada para {paciente.usuario.nombre}: {evolucion.justificacion[:100]}"
                )
            except Exception:
                pass


class TareaTerapeuticaViewSet(viewsets.ModelViewSet):
    queryset = TareaTerapeutica.objects.select_related('historia_clinica', 'psicologo__usuario', 'paciente__usuario').prefetch_related('evidencia').all().order_by('fecha_limite')
    serializer_class = TareaTerapeuticaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        rol_nombre = user.rol.nombre.lower() if user.rol else ""

        if 'paciente' in rol_nombre and hasattr(user, 'perfil_paciente'):
            return qs.filter(paciente=user.perfil_paciente)

        paciente_id = self.request.query_params.get('paciente')
        if paciente_id:
            qs = qs.filter(paciente_id=paciente_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        psico = getattr(user, 'perfil_psicologo', None)
        if not psico and not serializer.validated_data.get('psicologo'):
            psico = Psicologo.objects.filter(activo=True).first()
        serializer.save(psicologo=serializer.validated_data.get('psicologo') or psico)

    @action(detail=True, methods=['post'], url_path='evidencia')
    def registrar_evidencia(self, request, pk=None):
        tarea = self.get_object()
        data = request.data.copy()
        data['tarea'] = str(tarea.id)
        serializer = EvidenciaTareaSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Actualizar estado de la tarea a COMPLETADA
        tarea.estado = 'COMPLETADA'
        tarea.save()
        return Response({
            "mensaje": "Evidencia de tarea terapéutica enviada con éxito.",
            "tarea_estado": tarea.estado,
            "evidencia": serializer.data
        }, status=status.HTTP_201_CREATED)


class EvidenciaTareaViewSet(viewsets.ModelViewSet):
    queryset = EvidenciaTarea.objects.select_related('tarea').all()
    serializer_class = EvidenciaTareaSerializer
    permission_classes = [IsAuthenticated]


# ──────────────────────────────────────────────────────────────────────────────
# CU18: Consentimiento Informado y Firma Digital
# ──────────────────────────────────────────────────────────────────────────────
class ConsentimientoInformadoViewSet(viewsets.ModelViewSet):
    queryset = ConsentimientoInformado.objects.all().order_by('titulo')
    serializer_class = ConsentimientoInformadoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='render-preview')
    def render_preview(self, request, pk=None):
        plantilla = self.get_object()
        paciente_id = request.query_params.get('paciente')
        paciente_nombre = "[Nombre del Paciente]"
        paciente_ci = "[CI del Paciente]"

        if paciente_id:
            try:
                p = Paciente.objects.select_related('usuario').get(id=paciente_id)
                paciente_nombre = f"{p.usuario.nombre} {p.usuario.apellido}"
                paciente_ci = p.ci
            except Paciente.DoesNotExist:
                pass

        contenido = plantilla.contenido_legal
        contenido = contenido.replace('{nombre_paciente}', paciente_nombre)
        contenido = contenido.replace('{ci}', paciente_ci)
        contenido = contenido.replace('{fecha}', timezone.localdate().strftime('%d/%m/%Y'))
        return Response({
            "titulo": plantilla.titulo,
            "version": plantilla.version,
            "contenido_renderizado": contenido
        })


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


# ──────────────────────────────────────────────────────────────────────────────
# CU19: Derivación y Cierre de Caso
# ──────────────────────────────────────────────────────────────────────────────
class DerivacionCasoViewSet(viewsets.ModelViewSet):
    queryset = DerivacionCaso.objects.select_related('historia_clinica__paciente__usuario', 'psicologo_emisor__usuario').all().order_by('-fecha_derivacion')
    serializer_class = DerivacionCasoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        psico = getattr(user, 'perfil_psicologo', None)
        if not psico and not serializer.validated_data.get('psicologo_emisor'):
            psico = Psicologo.objects.filter(activo=True).first()
        derivacion = serializer.save(psicologo_emisor=serializer.validated_data.get('psicologo_emisor') or psico)

        # Si es cierre de caso o alta, marcar historia clínica como cerrada (CU19 Criterio b)
        if derivacion.tipo_derivacion in ('CIERRE_ALTA', 'DESERCION'):
            hc = derivacion.historia_clinica
            hc.cerrada = True
            hc.fecha_cierre = timezone.now()
            hc.save()

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


# ──────────────────────────────────────────────────────────────────────────────
# HU-35: Asistente Ético de Preconsulta (Piloto IA)
# ──────────────────────────────────────────────────────────────────────────────
class IAPreconsultaViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='analizar')
    def analizar(self, request):
        """
        HU-35: Genera un borrador asistivo de preconsulta con reglas transparentes.
        Verifica consentimiento previo y prohíbe escrituras automáticas en historia clínica.
        """
        respuesta_id = request.data.get('respuesta_id')
        if not respuesta_id:
            return Response({"error": "Debe proporcionar 'respuesta_id'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            respuesta = RespuestaPreConsulta.objects.select_related('paciente__usuario').get(id=respuesta_id)
        except RespuestaPreConsulta.DoesNotExist:
            return Response({"error": "Respuesta pre-consulta no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # Criterio d: Verificar consentimiento informado activo
        tiene_consentimiento = FirmaConsentimiento.objects.filter(paciente=respuesta.paciente).exists()
        if not tiene_consentimiento:
            return Response({
                "error": "Procesamiento asistivo bloqueado: El paciente no cuenta con un consentimiento informado activo registrado en la plataforma.",
                "modo_manual_requerido": True
            }, status=status.HTTP_403_FORBIDDEN)

        # Ejecutar motor de reglas clínicas SP2-54
        resultado = PreconsultaRulesEngine.evaluar_preconsulta(respuesta)

        # Registrar bitácora inmutable de auditoría
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

        resultado["auditoria_id"] = str(auditoria.id)
        return Response(resultado, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='decision')
    def registrar_decision(self, request):
        """Registra la decisión profesional (Aceptar, Editar o Descartar) sobre la sugerencia de IA."""
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

