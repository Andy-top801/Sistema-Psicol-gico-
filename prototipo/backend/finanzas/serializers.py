# ==============================================================================
# MÓDULO: finanzas/serializers.py
# DESCRIPCIÓN: Serializers DRF con validación estricta para Caja Clínica (HU-52)
#              y Liquidación de Honorarios (HU-54).
# ==============================================================================
from decimal import Decimal
from rest_framework import serializers
from .models import (
    CuentaPaciente,
    PagoConsulta,
    LiquidacionHonorario,
    DetalleLiquidacionCita,
)


class CuentaPacienteSerializer(serializers.ModelSerializer):
    paciente_id = serializers.UUIDField(source='paciente.id', read_only=True)
    paciente_nombre = serializers.SerializerMethodField()
    codigo_expediente = serializers.CharField(source='paciente.codigo_expediente', read_only=True)

    class Meta:
        model = CuentaPaciente
        fields = [
            'id', 'paciente_id', 'paciente_nombre', 'codigo_expediente',
            'moneda', 'total_cargado', 'total_pagado', 'saldo_pendiente',
            'ultima_actualizacion',
        ]

    def get_paciente_nombre(self, obj):
        u = obj.paciente.usuario
        return f"{u.nombre} {u.apellido}".strip()


class PagoConsultaSerializer(serializers.ModelSerializer):
    paciente_id = serializers.UUIDField(source='cuenta.paciente.id', read_only=True)
    paciente_nombre = serializers.SerializerMethodField()
    codigo_expediente = serializers.CharField(source='cuenta.paciente.codigo_expediente', read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    registrado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = PagoConsulta
        fields = [
            'id', 'cuenta', 'cita', 'paciente_id', 'paciente_nombre', 'codigo_expediente',
            'monto', 'metodo_pago', 'metodo_pago_display', 'numero_recibo',
            'codigo_verificacion', 'referencia_externa', 'observaciones',
            'registrado_por_nombre', 'anulado', 'fecha_pago',
        ]

    def get_paciente_nombre(self, obj):
        u = obj.cuenta.paciente.usuario
        return f"{u.nombre} {u.apellido}".strip()

    def get_registrado_por_nombre(self, obj):
        if not obj.registrado_por:
            return 'Sistema'
        return f"{obj.registrado_por.nombre} {obj.registrado_por.apellido}".strip()


class RegistrarPagoInputSerializer(serializers.Serializer):
    paciente_id = serializers.UUIDField()
    cita_id = serializers.UUIDField(required=False, allow_null=True)
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = serializers.ChoiceField(choices=PagoConsulta.METODO_PAGO_CHOICES)
    referencia_externa = serializers.CharField(max_length=120, required=False, allow_blank=True, default='')
    observaciones = serializers.CharField(max_length=500, required=False, allow_blank=True, default='')
    permitir_abono_adelantado = serializers.BooleanField(required=False, default=False)


class DetalleLiquidacionCitaSerializer(serializers.ModelSerializer):
    cita_id = serializers.UUIDField(source='cita.id', read_only=True)
    fecha_cita = serializers.DateField(source='cita.fecha', read_only=True)
    hora_inicio = serializers.TimeField(source='cita.hora_inicio', read_only=True)
    modalidad = serializers.CharField(source='cita.modalidad', read_only=True)
    paciente_nombre = serializers.SerializerMethodField()

    class Meta:
        model = DetalleLiquidacionCita
        fields = [
            'id', 'cita_id', 'fecha_cita', 'hora_inicio', 'modalidad',
            'paciente_nombre', 'monto_sesion', 'comision_sesion', 'neto_sesion', 'activo',
        ]

    def get_paciente_nombre(self, obj):
        u = obj.cita.paciente.usuario
        return f"{u.nombre} {u.apellido}".strip()


class LiquidacionHonorarioSerializer(serializers.ModelSerializer):
    psicologo_id = serializers.UUIDField(source='psicologo.id', read_only=True)
    psicologo_nombre = serializers.SerializerMethodField()
    numero_colegiado = serializers.CharField(source='psicologo.numero_colegiado', read_only=True)
    detalles = DetalleLiquidacionCitaSerializer(many=True, read_only=True)

    class Meta:
        model = LiquidacionHonorario
        fields = [
            'id', 'codigo_liquidacion', 'psicologo_id', 'psicologo_nombre', 'numero_colegiado',
            'fecha_inicio', 'fecha_fin', 'total_sesiones', 'monto_bruto',
            'porcentaje_comision_centro', 'comision_centro', 'monto_neto_psicologo',
            'estado', 'referencia_bancaria', 'observaciones', 'fecha_emision', 'fecha_pago',
            'detalles',
        ]

    def get_psicologo_nombre(self, obj):
        u = obj.psicologo.usuario
        return f"Lic. {u.nombre} {u.apellido}".strip()


class GenerarLiquidacionInputSerializer(serializers.Serializer):
    psicologo_id = serializers.UUIDField()
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    porcentaje_comision_centro = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, default=Decimal('30.00'),
        min_value=Decimal('0.00'), max_value=Decimal('100.00'),
    )
    observaciones = serializers.CharField(max_length=500, required=False, allow_blank=True, default='')


class PagarLiquidacionInputSerializer(serializers.Serializer):
    referencia_bancaria = serializers.CharField(max_length=120)
