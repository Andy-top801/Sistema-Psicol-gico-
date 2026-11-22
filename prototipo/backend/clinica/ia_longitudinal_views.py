# ==============================================================================
# MÓDULO: clinica/ia_longitudinal_views.py
# CASOS DE USO: CU23 (HU-49 Resumen Clínico IA HITL) y
#               CU24 (HU-50 / HU-51 Motor y Consola de Alertas de Riesgo IA)
# ==============================================================================
from datetime import date
from django.db import connection
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.services import log_event
from clinica.models import Paciente, ResumenClinicoIA, AlertaRiesgoIA
from clinica.ia_resumen_service import (
    ResumenIAService,
    psicologo_asignado_al_paciente,
    generar_resumen_ia_pdf,
)
from clinica.ia_riesgo_service import RiesgoLongitudinalService


def _is_coordinador_o_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    rol = (user.rol.nombre or '').lower() if getattr(user, 'rol', None) else ''
    return 'admin' in rol or 'coordinador' in rol or 'psic' in rol


def _serialize_resumen(r: ResumenClinicoIA) -> dict:
    return {
        'id': str(r.id),
        'resumen_id': str(r.id),
        'paciente_id': str(r.paciente_id),
        'expediente': r.paciente.codigo_expediente,
        'paciente_nombre': f"{r.paciente.usuario.nombre} {r.paciente.usuario.apellido}".strip(),
        'estado': r.estado,
        'fuente_modelo': r.fuente_modelo,
        'etiqueta_cumplimiento': r.etiqueta_cumplimiento,
        'contenido_estructurado': r.contenido_estructurado,
        'texto_resumen': r.texto_resumen,
        'borrador_ia': r.texto_resumen,
        'exportable_pdf': r.estado == 'APROBADO_HITL',
        'hash_sha256': r.hash_sha256,
        'total_notas_analizadas': r.total_notas_analizadas,
        'generado_por': f"{r.generado_por.nombre} {r.generado_por.apellido}".strip() if r.generado_por else None,
        'aprobado_por': f"{r.aprobado_por.nombre} {r.aprobado_por.apellido}".strip() if r.aprobado_por else None,
        'fecha_generacion': timezone.localtime(r.fecha_generacion).isoformat(),
        'fecha_aprobacion': timezone.localtime(r.fecha_aprobacion).isoformat() if r.fecha_aprobacion else None,
    }


def _serialize_alerta(a: AlertaRiesgoIA) -> dict:
    return {
        'id': str(a.id),
        'paciente_id': str(a.paciente_id),
        'expediente': a.paciente.codigo_expediente,
        'paciente_nombre': f"{a.paciente.usuario.nombre} {a.paciente.usuario.apellido}".strip(),
        'tipo': a.tipo,
        'score_riesgo': a.score_riesgo,
        'indice_riesgo': round(a.score_riesgo / 100.0, 3),
        'severidad': a.severidad,
        'estado': a.estado,
        'factores_detectados': a.factores_detectados,
        'factores_contribuyentes': a.factores_detectados,
        'explicacion': a.explicacion,
        'nota_intervencion': a.nota_intervencion,
        'atendido_por': f"{a.atendido_por.nombre} {a.atendido_por.apellido}".strip() if a.atendido_por else None,
        'fecha_deteccion': timezone.localtime(a.fecha_deteccion).isoformat(),
        'ultima_evaluacion': timezone.localtime(a.ultima_evaluacion).isoformat(),
        'fecha_resolucion': timezone.localtime(a.fecha_resolucion).isoformat() if a.fecha_resolucion else None,
    }


def _parse_optional_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw).strip()[:10])
    except ValueError:
        return None


# ==============================================================================
# HU-49 / CU23: RESÚMENES CLÍNICOS LONGITUDINALES POR IA (HITL)
# ==============================================================================
class PacienteResumenIAListCreateView(APIView):
    """CTR_ResumenLongitudinalIA — Pasos 1..16 y 23..26 de CU23."""
    permission_classes = [IsAuthenticated]

    def _verificar_acceso(self, request, paciente):
        # CU23-paso 3-4: verificar_asignacion_tratante
        if not psicologo_asignado_al_paciente(request.user, paciente):
            # CU23-paso 23-24: CTR -> AUD : registrar_evento('ACCESO_DENEGADO_CU23', ip) -> ok
            log_event(
                action='ACCESO_DENEGADO_CU23',
                modulo='CU23_IA_LONGITUDINAL',
                tenant=getattr(connection, 'schema_name', None),
                user=getattr(request.user, 'email', None),
                user_id=str(request.user.id),
                paciente_id=str(paciente.id),
                ip=request.META.get('REMOTE_ADDR'),
                motivo='Psicólogo no asignado o rol sin permiso intentó acceder a resumen IA.',
            )
            return False
        return True

    def get(self, request, paciente_id):
        paciente = get_object_or_404(Paciente.objects.select_related('usuario'), pk=paciente_id)
        if not self._verificar_acceso(request, paciente):
            # CU23-paso 25: HTTP 403 Forbidden
            return Response(
                {'detail': 'Acceso restringido al tratante.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = ResumenClinicoIA.objects.filter(paciente=paciente).select_related('paciente__usuario', 'generado_por', 'aprobado_por')
        return Response([_serialize_resumen(r) for r in qs[:20]])

    def post(self, request, paciente_id):
        # CU23-paso 2: POST /api/v1/clinica/ia/resumen-longitudinal/ (o /pacientes/<id>/resumenes-ia/)
        paciente = get_object_or_404(Paciente.objects.select_related('usuario'), pk=paciente_id)
        if not self._verificar_acceso(request, paciente):
            # CU23-paso 25: HTTP 403 Forbidden
            return Response(
                {'detail': 'Acceso restringido al tratante.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        usar_hf = bool(request.data.get('usar_hf', True))
        fecha_ini = _parse_optional_date(request.data.get('fecha_ini'))
        fecha_fin = _parse_optional_date(request.data.get('fecha_fin'))
        try:
            resumen = ResumenIAService.generar_resumen(
                paciente=paciente,
                usuario=request.user,
                usar_hf=usar_hf,
                fecha_ini=fecha_ini,
                fecha_fin=fecha_fin,
            )
            # CU23-paso 15: HTTP 201 Created {resumen_id, borrador_ia}
            return Response(_serialize_resumen(resumen), status=status.HTTP_201_CREATED)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class ResumenLongitudinalIASequenceView(APIView):
    """Ruta exacta Diagrama de Secuencia CU23 Paso 2: /api/v1/clinica/ia/resumen-longitudinal/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        paciente_id = request.query_params.get('paciente_id')
        if not paciente_id:
            return Response({'detail': 'paciente_id es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        return PacienteResumenIAListCreateView().get(request, paciente_id=paciente_id)

    def post(self, request):
        paciente_id = request.data.get('paciente_id')
        if not paciente_id:
            return Response({'detail': 'paciente_id es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        return PacienteResumenIAListCreateView().post(request, paciente_id=paciente_id)


class ResumenIAAprobarHITLView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, resumen_id):
        # CU23-paso 18: PATCH /api/v1/clinica/ia/resumen-longitudinal/{id}/aprobar/
        resumen = get_object_or_404(ResumenClinicoIA.objects.select_related('paciente__usuario'), pk=resumen_id)
        if not psicologo_asignado_al_paciente(request.user, resumen.paciente):
            return Response({'detail': 'Acceso denegado para aprobar este resumen.'}, status=status.HTTP_403_FORBIDDEN)

        resumen = ResumenIAService.aprobar_hitl(
            resumen=resumen,
            usuario=request.user,
            texto_editado=request.data.get('texto_resumen') or request.data.get('texto_final'),
            contenido_editado=request.data.get('contenido_estructurado'),
        )
        # CU23-paso 21: HTTP 200 OK {exportable_pdf=true}
        return Response(_serialize_resumen(resumen))


class ResumenIAPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, resumen_id):
        resumen = get_object_or_404(ResumenClinicoIA.objects.select_related('paciente__usuario'), pk=resumen_id)
        if not psicologo_asignado_al_paciente(request.user, resumen.paciente):
            return Response({'detail': 'Acceso denegado para exportar este resumen.'}, status=status.HTTP_403_FORBIDDEN)
        tenant = getattr(connection, 'tenant', None)
        tenant_name = tenant.nombre if (tenant and getattr(tenant, 'nombre', None)) else 'SIGEPSI'
        return generar_resumen_ia_pdf(resumen, tenant_name=tenant_name)


# ==============================================================================
# HU-50 & HU-51: MOTOR Y CONSOLA DE ALERTAS PRIORITARIAS DE RIESGO IA
# ==============================================================================
class AlertasRiesgoIAListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_coordinador_o_admin(request.user):
            return Response({'detail': 'Acceso restringido al equipo clínico y coordinación.'}, status=status.HTTP_403_FORBIDDEN)
        estado = request.query_params.get('estado')
        severidad = request.query_params.get('severidad')
        qs = RiesgoLongitudinalService.listar_consola_priorizada(estado=estado, severidad=severidad)

        resumen_estados = {
            'abiertas': AlertaRiesgoIA.objects.filter(estado='ABIERTA').count(),
            'en_atencion': AlertaRiesgoIA.objects.filter(estado='EN_ATENCION').count(),
            'resueltas': AlertaRiesgoIA.objects.filter(estado='RESUELTA').count(),
            'criticas_abiertas': AlertaRiesgoIA.objects.filter(estado__in=['ABIERTA', 'EN_ATENCION'], severidad='CRITICO').count(),
        }
        return Response({
            'resumen': resumen_estados,
            'alertas': [_serialize_alerta(a) for a in qs[:200]],
        })


class AlertasRiesgoIAEvaluarView(APIView):
    """CTR_DetectorRiesgoML — CU24-paso 2: POST /api/v1/clinica/ml/evaluar-riesgo/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not _is_coordinador_o_admin(request.user):
            return Response({'detail': 'Acceso restringido al equipo clínico y coordinación.'}, status=status.HTTP_403_FORBIDDEN)
        paciente_id = request.data.get('paciente_id')
        if paciente_id:
            paciente = get_object_or_404(Paciente.objects.select_related('usuario'), pk=paciente_id)
            alertas = RiesgoLongitudinalService.evaluar_paciente(paciente)
            # CU24-paso 14: HTTP 200 OK {alertas_generadas[], resumen_cohorte}
            return Response({
                'pacientes_evaluados': 1,
                'alertas_activas_actualizadas': len(alertas),
                'alertas_generadas': [_serialize_alerta(a) for a in alertas],
                'alertas': [_serialize_alerta(a) for a in alertas],
                'resumen_cohorte': {'pacientes': 1, 'alertas': len(alertas)},
            })
        res = RiesgoLongitudinalService.evaluar_todos_pacientes()
        return Response(res)


class AlertaRiesgoIATransicionView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, alerta_id):
        if not _is_coordinador_o_admin(request.user):
            return Response({'detail': 'Acceso restringido al equipo clínico y coordinación.'}, status=status.HTTP_403_FORBIDDEN)
        alerta = get_object_or_404(AlertaRiesgoIA.objects.select_related('paciente__usuario'), pk=alerta_id)
        try:
            alerta = RiesgoLongitudinalService.transicionar_alerta(
                alerta=alerta,
                nuevo_estado=request.data.get('estado', 'RESUELTA'),
                nota_intervencion=request.data.get('nota_intervencion') or request.data.get('accion_clinica', ''),
                usuario=request.user,
            )
            return Response(_serialize_alerta(alerta))
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
