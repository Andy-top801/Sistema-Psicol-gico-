# ==============================================================================
# MÓDULO: finanzas/views.py
# CASOS DE USO: CU26 (HU-52 Caja Clínica y Extracto Tipo Banco 20 Años,
#                     HU-54 Liquidación de Honorarios a Psicólogos)
# ==============================================================================
from datetime import date
from django.db import connection
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from agenda.models import Cita
from clinica.models import Paciente, Psicologo
from .models import CuentaPaciente, PagoConsulta, LiquidacionHonorario
from .permissions import (
    IsCajaStaff,
    IsAdminFinanciero,
    IsAdminOrOwnerPsychologist,
    IsCajaOrOwnerPaciente,
    is_admin_financiero,
    is_caja_staff,
)
from .serializers import (
    CuentaPacienteSerializer,
    PagoConsultaSerializer,
    RegistrarPagoInputSerializer,
    LiquidacionHonorarioSerializer,
    GenerarLiquidacionInputSerializer,
    PagarLiquidacionInputSerializer,
)
from .services import FinanzasService
from .dashboard_service import DashboardFinancieroService
from .pdf_utils import (
    generar_recibo_pago_pdf,
    generar_extracto_bancario_pdf,
    generar_extracto_bancario_excel,
    generar_extracto_bancario_csv,
    generar_boleta_liquidacion_pdf,
)


def _tenant_display_name() -> str:
    tenant = getattr(connection, 'tenant', None)
    if tenant and getattr(tenant, 'nombre', None):
        return tenant.nombre
    return getattr(connection, 'schema_name', 'SIGEPSI')


def _parse_iso_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(raw.strip()[:10])
    except ValueError:
        raise ValueError(f"Formato de fecha inválido '{raw}'. Use YYYY-MM-DD.")


# ==============================================================================
# HU-52: CUENTAS DE PACIENTES, REGISTRO DE COBROS Y RECIBO PDF
# ==============================================================================
class CuentaPacienteListView(APIView):
    permission_classes = [IsAuthenticated, IsCajaOrOwnerPaciente]

    def get(self, request):
        if is_caja_staff(request.user):
            # Asegurar sincronización opcional si se solicita (?sync=true)
            if request.query_params.get('sync') == 'true':
                for pac in Paciente.objects.select_related('usuario').all()[:200]:
                    FinanzasService.sincronizar_cargos_paciente(pac)
            qs = CuentaPaciente.objects.select_related('paciente__usuario').order_by('-saldo_pendiente')
            solo_deudores = request.query_params.get('solo_deudores')
            if solo_deudores in ('true', '1'):
                qs = qs.filter(saldo_pendiente__gt=0)
            q = (request.query_params.get('q') or '').strip()
            if q:
                qs = qs.filter(paciente__codigo_expediente__icontains=q) | qs.filter(
                    paciente__usuario__nombre__icontains=q
                ) | qs.filter(paciente__usuario__apellido__icontains=q)
            serializer = CuentaPacienteSerializer(qs, many=True)
            return Response(serializer.data)

        # Paciente autenticado: solo su propia cuenta
        pac = request.user.perfil_paciente
        cuenta = FinanzasService.sincronizar_cargos_paciente(pac)
        return Response([CuentaPacienteSerializer(cuenta).data])


class CuentaPacienteDetailView(APIView):
    permission_classes = [IsAuthenticated, IsCajaOrOwnerPaciente]

    def get(self, request, paciente_id):
        paciente = get_object_or_404(Paciente.objects.select_related('usuario'), pk=paciente_id)
        if not is_caja_staff(request.user):
            if not hasattr(request.user, 'perfil_paciente') or request.user.perfil_paciente.id != paciente.id:
                return Response({'detail': 'Acceso denegado a la cuenta de otro paciente.'}, status=status.HTTP_403_FORBIDDEN)

        cuenta = FinanzasService.sincronizar_cargos_paciente(paciente)
        pagos = PagoConsulta.objects.filter(cuenta=cuenta, anulado=False).select_related('registrado_por', 'cita')[:50]
        citas_pendientes = Cita.objects.filter(paciente=paciente, costo__gt=0).exclude(estado='CANCELADA').order_by('-fecha')[:30]

        return Response({
            'cuenta': CuentaPacienteSerializer(cuenta).data,
            'pagos_recientes': PagoConsultaSerializer(pagos, many=True).data,
            'citas_facturables': [
                {
                    'id': str(c.id),
                    'fecha': c.fecha.isoformat(),
                    'hora_inicio': c.hora_inicio.strftime('%H:%M'),
                    'modalidad': c.modalidad,
                    'estado': c.estado,
                    'costo': float(c.costo),
                }
                for c in citas_pendientes
            ],
        })


class PagoConsultaListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCajaStaff]

    def get(self, request):
        qs = PagoConsulta.objects.filter(anulado=False).select_related(
            'cuenta__paciente__usuario', 'registrado_por', 'cita'
        )
        paciente_id = request.query_params.get('paciente_id')
        metodo = request.query_params.get('metodo_pago')
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')

        try:
            d_desde = _parse_iso_date(fecha_desde)
            d_hasta = _parse_iso_date(fecha_hasta)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if paciente_id:
            qs = qs.filter(cuenta__paciente_id=paciente_id)
        if metodo:
            qs = qs.filter(metodo_pago=metodo.upper().strip())
        if d_desde:
            qs = qs.filter(fecha_pago__date__gte=d_desde)
        if d_hasta:
            qs = qs.filter(fecha_pago__date__lte=d_hasta)

        limit = min(500, max(1, int(request.query_params.get('limit', 100))))
        return Response(PagoConsultaSerializer(qs[:limit], many=True).data)

    def post(self, request):
        inp = RegistrarPagoInputSerializer(data=request.data)
        if not inp.is_valid():
            return Response(inp.errors, status=status.HTTP_400_BAD_REQUEST)

        data = inp.validated_data
        paciente = get_object_or_404(Paciente, pk=data['paciente_id'])
        cita = None
        if data.get('cita_id'):
            cita = get_object_or_404(Cita, pk=data['cita_id'])

        try:
            pago = FinanzasService.registrar_pago(
                paciente=paciente,
                monto=data['monto'],
                metodo_pago=data['metodo_pago'],
                usuario=request.user,
                cita=cita,
                referencia_externa=data.get('referencia_externa', ''),
                observaciones=data.get('observaciones', ''),
                permitir_abono_adelantado=data.get('permitir_abono_adelantado', False),
            )
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PagoConsultaSerializer(pago).data, status=status.HTTP_201_CREATED)


class PagoReciboPDFView(APIView):
    permission_classes = [IsAuthenticated, IsCajaOrOwnerPaciente]

    def get(self, request, pago_id):
        pago = get_object_or_404(
            PagoConsulta.objects.select_related(
                'cuenta__paciente__usuario', 'cita__psicologo__usuario', 'registrado_por'
            ),
            pk=pago_id,
        )
        if not is_caja_staff(request.user):
            if not hasattr(request.user, 'perfil_paciente') or request.user.perfil_paciente.id != pago.cuenta.paciente_id:
                return Response({'detail': 'Acceso denegado a este comprobante.'}, status=status.HTTP_403_FORBIDDEN)

        return generar_recibo_pago_pdf(pago, tenant_name=_tenant_display_name())


# ==============================================================================
# HU-52: EXTRACTO HISTÓRICO DE PAGOS TIPO BANCARIO (HASTA 20 AÑOS)
# ==============================================================================
class ExtractoBancarioView(APIView):
    permission_classes = [IsAuthenticated, IsCajaOrOwnerPaciente]

    def get(self, request):
        paciente_id = request.query_params.get('paciente_id')
        if not is_caja_staff(request.user):
            # Paciente solo puede ver su propio extracto
            paciente_id = str(request.user.perfil_paciente.id)

        try:
            fecha_desde = _parse_iso_date(request.query_params.get('fecha_desde'))
            fecha_hasta = _parse_iso_date(request.query_params.get('fecha_hasta'))
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        metodo_pago = request.query_params.get('metodo_pago')
        tipo = request.query_params.get('tipo')
        formato = (request.query_params.get('formato') or 'json').lower().strip()

        try:
            if formato in ('pdf', 'excel', 'xlsx', 'csv'):
                meta, rows_iter = FinanzasService.iterar_extracto_bancario(
                    paciente_id=paciente_id,
                    fecha_desde=fecha_desde,
                    fecha_hasta=fecha_hasta,
                    metodo_pago=metodo_pago,
                    tipo=tipo,
                )
                tenant_name = _tenant_display_name()
                if formato == 'pdf':
                    return generar_extracto_bancario_pdf(meta, rows_iter, tenant_name=tenant_name)
                if formato in ('excel', 'xlsx'):
                    return generar_extracto_bancario_excel(meta, rows_iter, tenant_name=tenant_name)
                return generar_extracto_bancario_csv(meta, rows_iter)

            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 50))
            resultado = FinanzasService.obtener_extracto_bancario(
                paciente_id=paciente_id,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                metodo_pago=metodo_pago,
                tipo=tipo,
                page=page,
                page_size=page_size,
            )
            return Response(resultado)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# HU-54: LIQUIDACIÓN PERIÓDICA DE HONORARIOS A PSICÓLOGOS (Bs.)
# ==============================================================================
class LiquidacionHonorarioListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwnerPsychologist]

    def get(self, request):
        qs = LiquidacionHonorario.objects.select_related('psicologo__usuario').prefetch_related(
            'detalles__cita__paciente__usuario'
        )
        if not is_admin_financiero(request.user):
            qs = qs.filter(psicologo=request.user.perfil_psicologo)
        else:
            psico_id = request.query_params.get('psicologo_id')
            if psico_id:
                qs = qs.filter(psicologo_id=psico_id)

        estado = request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado.upper().strip())

        return Response(LiquidacionHonorarioSerializer(qs[:200], many=True).data)

    def post(self, request):
        if not is_admin_financiero(request.user):
            return Response(
                {'detail': 'Solo administradores del centro pueden generar liquidaciones.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        inp = GenerarLiquidacionInputSerializer(data=request.data)
        if not inp.is_valid():
            return Response(inp.errors, status=status.HTTP_400_BAD_REQUEST)

        data = inp.validated_data
        psicologo = get_object_or_404(Psicologo.objects.select_related('usuario'), pk=data['psicologo_id'])

        try:
            liq = FinanzasService.generar_liquidacion(
                psicologo=psicologo,
                fecha_inicio=data['fecha_inicio'],
                fecha_fin=data['fecha_fin'],
                usuario=request.user,
                porcentaje_comision_centro=data['porcentaje_comision_centro'],
                observaciones=data.get('observaciones', ''),
            )
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(LiquidacionHonorarioSerializer(liq).data, status=status.HTTP_201_CREATED)


class LiquidacionPreviewView(APIView):
    """Previsualiza sesiones REALIZADAS pendientes de liquidar para un psicólogo y rango."""
    permission_classes = [IsAuthenticated, IsAdminFinanciero]

    def get(self, request):
        psico_id = request.query_params.get('psicologo_id')
        if not psico_id:
            return Response({'detail': 'psicologo_id es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            f_ini = _parse_iso_date(request.query_params.get('fecha_inicio'))
            f_fin = _parse_iso_date(request.query_params.get('fecha_fin'))
            pct = float(request.query_params.get('porcentaje_comision_centro', 30))
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if not f_ini or not f_fin:
            return Response({'detail': 'fecha_inicio y fecha_fin son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)

        psicologo = get_object_or_404(Psicologo.objects.select_related('usuario'), pk=psico_id)
        citas = list(FinanzasService.citas_pendientes_liquidacion(psicologo, f_ini, f_fin))
        bruto = sum(float(c.costo) for c in citas)
        comision = round(bruto * pct / 100.0, 2)
        neto = round(bruto - comision, 2)

        return Response({
            'psicologo_id': str(psicologo.id),
            'psicologo_nombre': f"Lic. {psicologo.usuario.nombre} {psicologo.usuario.apellido}".strip(),
            'total_sesiones': len(citas),
            'monto_bruto': round(bruto, 2),
            'porcentaje_comision_centro': pct,
            'comision_centro': comision,
            'monto_neto_psicologo': neto,
            'sesiones': [
                {
                    'cita_id': str(c.id),
                    'fecha': c.fecha.isoformat(),
                    'hora_inicio': c.hora_inicio.strftime('%H:%M'),
                    'paciente': f"{c.paciente.usuario.nombre} {c.paciente.usuario.apellido}".strip(),
                    'modalidad': c.modalidad,
                    'costo': float(c.costo),
                }
                for c in citas
            ],
        })


class LiquidacionPagarView(APIView):
    permission_classes = [IsAuthenticated, IsAdminFinanciero]

    def patch(self, request, liquidacion_id):
        inp = PagarLiquidacionInputSerializer(data=request.data)
        if not inp.is_valid():
            return Response(inp.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            liq = FinanzasService.marcar_liquidacion_pagada(
                liquidacion_id=liquidacion_id,
                referencia_bancaria=inp.validated_data['referencia_bancaria'],
                usuario=request.user,
            )
        except LiquidacionHonorario.DoesNotExist:
            return Response({'detail': 'Liquidación no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(LiquidacionHonorarioSerializer(liq).data)


class LiquidacionAnularView(APIView):
    permission_classes = [IsAuthenticated, IsAdminFinanciero]

    def patch(self, request, liquidacion_id):
        motivo = (request.data.get('motivo') or '').strip()
        try:
            liq = FinanzasService.anular_liquidacion(liquidacion_id=liquidacion_id, motivo=motivo, usuario=request.user)
        except LiquidacionHonorario.DoesNotExist:
            return Response({'detail': 'Liquidación no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(LiquidacionHonorarioSerializer(liq).data)


class LiquidacionBoletaPDFView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwnerPsychologist]

    def get(self, request, liquidacion_id):
        liq = get_object_or_404(
            LiquidacionHonorario.objects.select_related('psicologo__usuario').prefetch_related(
                'detalles__cita__paciente__usuario'
            ),
            pk=liquidacion_id,
        )
        self.check_object_permissions(request, liq)
        return generar_boleta_liquidacion_pdf(liq, tenant_name=_tenant_display_name())


# ==============================================================================
# HU-53: DASHBOARD FINANCIERO Y GERENCIAL INTEGRAL (>= 2 AÑOS + TODOS REPORTES)
# ==============================================================================
class DashboardFinancieroView(APIView):
    permission_classes = [IsAuthenticated, IsAdminFinanciero]

    def get(self, request):
        horizonte = request.query_params.get('horizonte', '24m')
        psicologo_id = request.query_params.get('psicologo_id')
        especialidad_id = request.query_params.get('especialidad_id')
        try:
            fecha_desde = _parse_iso_date(request.query_params.get('fecha_desde'))
            fecha_hasta = _parse_iso_date(request.query_params.get('fecha_hasta'))
            data = DashboardFinancieroService.obtener_dashboard(
                horizonte=horizonte,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                psicologo_id=psicologo_id,
                especialidad_id=especialidad_id,
                incluir_superadmin_reportes=bool(request.user.is_superuser),
            )
            return Response(data)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

