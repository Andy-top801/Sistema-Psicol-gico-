from django.contrib import admin
from .models import (
    CuentaPaciente,
    PagoConsulta,
    MovimientoFinanciero,
    LiquidacionHonorario,
    DetalleLiquidacionCita,
    PlanPagoTerapeutico,
    CuotaAmortizacion,
    GastoFijoMensual,
    CalificacionCRM,
)


@admin.register(CuentaPaciente)
class CuentaPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'moneda', 'total_cargado', 'total_pagado', 'saldo_pendiente', 'ultima_actualizacion')
    search_fields = ('paciente__codigo_expediente', 'paciente__usuario__nombre', 'paciente__usuario__apellido')


@admin.register(PagoConsulta)
class PagoConsultaAdmin(admin.ModelAdmin):
    list_display = ('numero_recibo', 'cuenta', 'moneda_origen', 'monto_origen', 'monto', 'metodo_pago', 'anulado', 'fecha_pago')
    list_filter = ('metodo_pago', 'moneda_origen', 'anulado')
    search_fields = ('numero_recibo', 'codigo_verificacion')


@admin.register(MovimientoFinanciero)
class MovimientoFinancieroAdmin(admin.ModelAdmin):
    list_display = ('fecha_movimiento', 'cuenta', 'tipo', 'numero_documento', 'debe', 'haber')
    list_filter = ('tipo', 'metodo_pago')


@admin.register(LiquidacionHonorario)
class LiquidacionHonorarioAdmin(admin.ModelAdmin):
    list_display = ('codigo_liquidacion', 'psicologo', 'fecha_inicio', 'fecha_fin', 'monto_bruto', 'monto_neto_psicologo', 'estado')
    list_filter = ('estado',)
    search_fields = ('codigo_liquidacion', 'psicologo__usuario__nombre', 'psicologo__usuario__apellido')


@admin.register(DetalleLiquidacionCita)
class DetalleLiquidacionCitaAdmin(admin.ModelAdmin):
    list_display = ('liquidacion', 'cita', 'monto_sesion', 'neto_sesion', 'activo')
    list_filter = ('activo',)


@admin.register(PlanPagoTerapeutico)
class PlanPagoTerapeuticoAdmin(admin.ModelAdmin):
    list_display = ('nombre_plan', 'paciente', 'monto_total', 'numero_cuotas', 'saldo_insoluto', 'estado')
    list_filter = ('estado', 'moneda')


@admin.register(CuotaAmortizacion)
class CuotaAmortizacionAdmin(admin.ModelAdmin):
    list_display = ('plan', 'numero_cuota', 'fecha_vencimiento', 'capital_amortizado', 'interes_o_comision', 'seguro_asistencial', 'monto_total_cuota', 'estado')
    list_filter = ('estado',)


@admin.register(GastoFijoMensual)
class GastoFijoMensualAdmin(admin.ModelAdmin):
    list_display = ('periodo_mes', 'categoria', 'descripcion', 'monto_bob', 'fecha_gasto')
    list_filter = ('categoria', 'periodo_mes')


@admin.register(CalificacionCRM)
class CalificacionCRMAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'puntuacion_estrellas', 'requiere_seguimiento', 'estado_seguimiento', 'fecha_calificacion')
    list_filter = ('puntuacion_estrellas', 'requiere_seguimiento', 'estado_seguimiento')
