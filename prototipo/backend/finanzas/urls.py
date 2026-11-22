from django.urls import path
from .views import (
    CuentaPacienteListView,
    CuentaPacienteDetailView,
    PagoConsultaListCreateView,
    PagoReciboPDFView,
    ExtractoBancarioView,
    LiquidacionHonorarioListCreateView,
    LiquidacionPreviewView,
    LiquidacionPagarView,
    LiquidacionAnularView,
    LiquidacionBoletaPDFView,
    DashboardFinancieroView,
)

urlpatterns = [
    # HU-53: Dashboard Financiero y Gerencial Integral (>= 2 años + todos los reportes)
    path('dashboard/', DashboardFinancieroView.as_view(), name='finanzas-dashboard-gerencial'),

    # HU-52: Caja Clínica, Estado de Cuenta y Cobros en Bs.
    path('cuentas/', CuentaPacienteListView.as_view(), name='finanzas-cuentas-list'),
    path('cuentas/<uuid:paciente_id>/', CuentaPacienteDetailView.as_view(), name='finanzas-cuenta-detail'),
    path('pagos/', PagoConsultaListCreateView.as_view(), name='finanzas-pagos-list-create'),
    path('pagos/<uuid:pago_id>/recibo-pdf/', PagoReciboPDFView.as_view(), name='finanzas-pago-recibo-pdf'),

    # HU-52 (Ampliado): Extracto Histórico de Pagos Tipo Bancario (hasta 20 años)
    path('extracto/', ExtractoBancarioView.as_view(), name='finanzas-extracto-bancario'),

    # HU-54: Liquidación Periódica de Honorarios a Psicólogos (Bs.)
    path('liquidaciones/', LiquidacionHonorarioListCreateView.as_view(), name='finanzas-liquidaciones-list-create'),
    path('liquidaciones/preview/', LiquidacionPreviewView.as_view(), name='finanzas-liquidaciones-preview'),
    path('liquidaciones/<uuid:liquidacion_id>/pagar/', LiquidacionPagarView.as_view(), name='finanzas-liquidacion-pagar'),
    path('liquidaciones/<uuid:liquidacion_id>/anular/', LiquidacionAnularView.as_view(), name='finanzas-liquidacion-anular'),
    path('liquidaciones/<uuid:liquidacion_id>/boleta-pdf/', LiquidacionBoletaPDFView.as_view(), name='finanzas-liquidacion-boleta-pdf'),
]
