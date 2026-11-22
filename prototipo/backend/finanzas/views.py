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
from .models import CuentaPaciente, PagoConsulta, LiquidacionHonorario, PlanPagoTerapeutico, CuotaAmortizacion, GastoFijoMensual, CalificacionCRM
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
    CrearPlanAmortizacionInputSerializer,
    RegistrarPagoCuotaInputSerializer,
    RegistrarGastoFijoInputSerializer,
    RegistrarCalificacionCRMInputSerializer,
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
            if data.get('cuota_id'):
                res = FinanzasService.registrar_pago_cuota(
                    cuota_id=data['cuota_id'],
                    monto=data['monto'],
                    moneda=data.get('moneda_origen', 'BOB'),
                    metodo_pago=data['metodo_pago'],
                    usuario=request.user,
                    referencia_externa=data.get('referencia_externa', ''),
                )
                return Response(PagoConsultaSerializer(res['pago']).data, status=status.HTTP_201_CREATED)

            pago = FinanzasService.registrar_pago(
                paciente=paciente,
                monto=data['monto'],
                metodo_pago=data['metodo_pago'],
                usuario=request.user,
                cita=cita,
                referencia_externa=data.get('referencia_externa', ''),
                observaciones=data.get('observaciones', ''),
                permitir_abono_adelantado=data.get('permitir_abono_adelantado', False),
                moneda_origen=data.get('moneda_origen', 'BOB'),
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


# ==============================================================================
# INCREMENTO CU26-A: PLANES DE AMORTIZACIÓN, EXTRACTO POR PACIENTE Y PAGO BOB/USD
# ==============================================================================
class PlanPagoAmortizacionListCreateView(APIView):
    """CTR_PagosAmortizacion — Crea y lista planes de pago con tabla de amortización."""
    permission_classes = [IsAuthenticated, IsCajaOrOwnerPaciente]

    def get(self, request):
        paciente_id = request.query_params.get('paciente_id')
        if not is_caja_staff(request.user):
            paciente_id = str(request.user.perfil_paciente.id)
        if not paciente_id:
            qs = PlanPagoTerapeutico.objects.select_related('paciente__usuario').prefetch_related('cuotas')[:50]
            return Response([
                {
                    'id': str(pl.id),
                    'paciente_id': str(pl.paciente_id),
                    'paciente_nombre': f"{pl.paciente.usuario.nombre} {pl.paciente.usuario.apellido}".strip(),
                    'nombre_plan': pl.nombre_plan,
                    'monto_total': float(pl.monto_total),
                    'numero_cuotas': pl.numero_cuotas,
                    'saldo_insoluto': float(pl.saldo_insoluto),
                    'estado': pl.estado,
                }
                for pl in qs
            ])
        return Response(FinanzasService.obtener_extracto_paciente_completo(paciente_id))

    def post(self, request):
        if not is_caja_staff(request.user):
            return Response({'detail': 'Solo personal de caja puede crear planes.'}, status=status.HTTP_403_FORBIDDEN)
        inp = CrearPlanAmortizacionInputSerializer(data=request.data)
        if not inp.is_valid():
            return Response(inp.errors, status=status.HTTP_400_BAD_REQUEST)
        d = inp.validated_data
        paciente = get_object_or_404(Paciente, pk=d['paciente_id'])
        try:
            plan = FinanzasService.crear_plan_amortizacion(
                paciente=paciente,
                nombre_plan=d['nombre_plan'],
                monto_total=d['monto_total'],
                numero_cuotas=d['numero_cuotas'],
                tasa_interes_anual=d['tasa_interes_anual'],
                porcentaje_seguro=d['porcentaje_seguro'],
                moneda=d['moneda'],
                sesiones_incluidas=d['sesiones_incluidas'],
                fecha_inicio=d.get('fecha_inicio'),
            )
            return Response(FinanzasService.obtener_extracto_paciente_completo(plan.paciente_id), status=status.HTTP_201_CREATED)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class ExtractoPacienteAmortizacionView(APIView):
    """Ruta CU26-A: GET /api/v1/finanzas/extracto-paciente/<paciente_id>/"""
    permission_classes = [IsAuthenticated, IsCajaOrOwnerPaciente]

    def get(self, request, paciente_id):
        paciente = get_object_or_404(Paciente, pk=paciente_id)
        if not is_caja_staff(request.user):
            if not hasattr(request.user, 'perfil_paciente') or request.user.perfil_paciente.id != paciente.id:
                return Response({'detail': 'Acceso denegado.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(FinanzasService.obtener_extracto_paciente_completo(paciente.id))


class PagoRegistrarMultimonedaView(APIView):
    """
    CU26A-paso 2: POST /api/v1/finanzas/pagos/registrar/
    Soporta pago de Cuota de Amortización (cuota_id) o cobro directo en BOB/USD.
    """
    permission_classes = [IsAuthenticated, IsCajaStaff]

    def post(self, request):
        inp = RegistrarPagoCuotaInputSerializer(data=request.data)
        if not inp.is_valid():
            return Response(inp.errors, status=status.HTTP_400_BAD_REQUEST)
        d = inp.validated_data
        try:
            if d.get('cuota_id'):
                res = FinanzasService.registrar_pago_cuota(
                    cuota_id=d['cuota_id'],
                    monto=d.get('monto'),
                    moneda=d.get('moneda', 'BOB'),
                    metodo_pago=d.get('metodo_pago', 'QR_BANCARIO'),
                    usuario=request.user,
                    referencia_externa=d.get('referencia_externa', ''),
                )
                # CU26A-paso 12: HTTP 201 Created {comprobante, extracto_actualizado}
                return Response({
                    'comprobante': PagoConsultaSerializer(res['pago']).data,
                    'extracto_actualizado': res['extracto_amortizacion'],
                }, status=status.HTTP_201_CREATED)

            if not d.get('paciente_id') or not d.get('monto'):
                return Response({'detail': 'Debe enviar cuota_id o paciente_id + monto.'}, status=status.HTTP_400_BAD_REQUEST)
            pac = get_object_or_404(Paciente, pk=d['paciente_id'])
            pago = FinanzasService.registrar_pago(
                paciente=pac,
                monto=d['monto'],
                metodo_pago=d.get('metodo_pago', 'QR_BANCARIO'),
                usuario=request.user,
                referencia_externa=d.get('referencia_externa', ''),
                observaciones=d.get('observaciones', ''),
                moneda_origen=d.get('moneda', 'BOB'),
            )
            return Response({
                'comprobante': PagoConsultaSerializer(pago).data,
                'extracto_actualizado': FinanzasService.obtener_extracto_paciente_completo(pac.id),
            }, status=status.HTTP_201_CREATED)
        except CuotaAmortizacion.DoesNotExist:
            return Response({'detail': 'Cuota de amortización no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            # CU26A-paso 14: HTTP 400 Bad Request
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# INCREMENTO CU26-B & CRM: GASTOS FIJOS, ESTADO DE RESULTADOS P&L Y CRM 1–5★
# ==============================================================================
class GastoFijoMensualListCreateView(APIView):
    """CRUD de Gastos Fijos Mensuales (Alquiler, Servicios, Personal, SaaS)."""
    permission_classes = [IsAuthenticated, IsAdminFinanciero]

    def get(self, request):
        qs = GastoFijoMensual.objects.all()
        periodo = request.query_params.get('periodo_mes')
        categoria = request.query_params.get('categoria')
        if periodo:
            qs = qs.filter(periodo_mes=periodo.strip())
        if categoria:
            qs = qs.filter(categoria=categoria.upper().strip())
        return Response([
            {
                'id': str(g.id),
                'periodo_mes': g.periodo_mes,
                'fecha_gasto': g.fecha_gasto.isoformat(),
                'categoria': g.categoria,
                'categoria_display': g.get_categoria_display(),
                'descripcion': g.descripcion,
                'moneda': g.moneda,
                'monto_bob': float(g.monto_bob),
                'comprobante_ref': g.comprobante_ref,
            }
            for g in qs[:200]
        ])

    def post(self, request):
        inp = RegistrarGastoFijoInputSerializer(data=request.data)
        if not inp.is_valid():
            return Response(inp.errors, status=status.HTTP_400_BAD_REQUEST)
        d = inp.validated_data
        try:
            gasto = DashboardFinancieroService.registrar_gasto_fijo(
                categoria=d['categoria'],
                descripcion=d['descripcion'],
                monto=d['monto'],
                moneda=d.get('moneda', 'BOB'),
                fecha_gasto=d.get('fecha_gasto'),
                periodo_mes=d.get('periodo_mes') or None,
                comprobante_ref=d.get('comprobante_ref', ''),
                usuario=request.user,
            )
            return Response({
                'id': str(gasto.id),
                'periodo_mes': gasto.periodo_mes,
                'categoria': gasto.categoria,
                'descripcion': gasto.descripcion,
                'monto_bob': float(gasto.monto_bob),
            }, status=status.HTTP_201_CREATED)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class EstadoResultadosContableView(APIView):
    """CU26B-paso 2: GET /api/v1/finanzas/estado-resultados/?ini=...&fin=..."""
    permission_classes = [IsAuthenticated, IsAdminFinanciero]

    def get(self, request):
        try:
            f_ini = _parse_iso_date(request.query_params.get('ini') or request.query_params.get('fecha_desde'))
            f_fin = _parse_iso_date(request.query_params.get('fin') or request.query_params.get('fecha_hasta'))
            res = DashboardFinancieroService.calcular_estado_resultados_y_crm(fecha_desde=f_ini, fecha_hasta=f_fin)
            return Response(res)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class CalificacionCRMListCreateView(APIView):
    """Registro y listado de calificaciones post-consulta CRM 1–5 estrellas."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = CalificacionCRM.objects.select_related('paciente__usuario', 'psicologo__usuario')
        if not is_caja_staff(request.user) and hasattr(request.user, 'perfil_paciente'):
            qs = qs.filter(paciente=request.user.perfil_paciente)
        return Response([
            {
                'id': str(c.id),
                'cita_id': str(c.cita_id) if c.cita_id else None,
                'paciente_id': str(c.paciente_id),
                'paciente_nombre': f"{c.paciente.usuario.nombre} {c.paciente.usuario.apellido}".strip(),
                'psicologo_nombre': f"Lic. {c.psicologo.usuario.nombre} {c.psicologo.usuario.apellido}".strip() if c.psicologo else '-',
                'puntuacion_estrellas': c.puntuacion_estrellas,
                'puntualidad': c.puntualidad,
                'empatia_profesional': c.empatia_profesional,
                'calidad_plataforma': c.calidad_plataforma,
                'comentario': c.comentario,
                'requiere_seguimiento': c.requiere_seguimiento,
                'estado_seguimiento': c.estado_seguimiento,
                'nota_seguimiento': c.nota_seguimiento,
                'fecha_calificacion': c.fecha_calificacion.isoformat(),
            }
            for c in qs[:100]
        ])

    def post(self, request):
        inp = RegistrarCalificacionCRMInputSerializer(data=request.data)
        if not inp.is_valid():
            return Response(inp.errors, status=status.HTTP_400_BAD_REQUEST)
        d = inp.validated_data
        cita = get_object_or_404(Cita, pk=d['cita_id']) if d.get('cita_id') else None
        paciente = None
        if hasattr(request.user, 'perfil_paciente') and not is_caja_staff(request.user):
            paciente = request.user.perfil_paciente
        elif d.get('paciente_id'):
            paciente = get_object_or_404(Paciente, pk=d['paciente_id'])
        elif cita is not None:
            paciente = cita.paciente
        else:
            paciente = Paciente.objects.first()
        if not paciente:
            return Response({'detail': 'No se pudo resolver el paciente para la calificación CRM.'}, status=status.HTTP_400_BAD_REQUEST)

        psicologo = get_object_or_404(Psicologo, pk=d['psicologo_id']) if d.get('psicologo_id') else None
        try:
            calif = DashboardFinancieroService.registrar_calificacion_crm(
                paciente=paciente,
                puntuacion_estrellas=d['puntuacion_estrellas'],
                cita=cita,
                psicologo=psicologo,
                puntualidad=d['puntualidad'],
                empatia_profesional=d['empatia_profesional'],
                calidad_plataforma=d['calidad_plataforma'],
                comentario=d.get('comentario', ''),
            )
            return Response({
                'id': str(calif.id),
                'puntuacion_estrellas': calif.puntuacion_estrellas,
                'requiere_seguimiento': calif.requiere_seguimiento,
                'estado_seguimiento': calif.estado_seguimiento,
            }, status=status.HTTP_201_CREATED)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class CalificacionCRMSeguimientoView(APIView):
    """Permite marcar como ATENDIDO un ticket CRM de baja puntuación (<= 2★)."""
    permission_classes = [IsAuthenticated, IsAdminFinanciero]

    def patch(self, request, calificacion_id):
        calif = get_object_or_404(CalificacionCRM, pk=calificacion_id)
        nota = (request.data.get('nota_seguimiento') or '').strip()
        calif.estado_seguimiento = 'ATENDIDO'
        if nota:
            calif.nota_seguimiento = nota
        calif.save(update_fields=['estado_seguimiento', 'nota_seguimiento'])
        return Response({'id': str(calif.id), 'estado_seguimiento': calif.estado_seguimiento, 'nota_seguimiento': calif.nota_seguimiento})


class EstadisticasCRMView(APIView):
    """Estadísticas consolidadas CSAT/NPS e histograma 1–5★."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            f_ini = _parse_iso_date(request.query_params.get('ini') or request.query_params.get('fecha_desde'))
            f_fin = _parse_iso_date(request.query_params.get('fin') or request.query_params.get('fecha_hasta'))
            return Response(DashboardFinancieroService.obtener_estadisticas_crm(fecha_desde=f_ini, fecha_hasta=f_fin))
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

