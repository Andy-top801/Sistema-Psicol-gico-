from django.contrib import admin
from .models import (
    CuentaPaciente,
    PagoConsulta,
    MovimientoFinanciero,
    LiquidacionHonorario,
    DetalleLiquidacionCita,
)


@admin.register(CuentaPaciente)
class CuentaPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'moneda', 'total_cargado', 'total_pagado', 'saldo_pendiente', 'ultima_actualizacion')
    search_fields = ('paciente__codigo_expediente', 'paciente__usuario__nombre', 'paciente__usuario__apellido')


@admin.register(PagoConsulta)
class PagoConsultaAdmin(admin.ModelAdmin):
    list_display = ('numero_recibo', 'cuenta', 'monto', 'metodo_pago', 'anulado', 'fecha_pago')
    list_filter = ('metodo_pago', 'anulado')
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
