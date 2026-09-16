# ==============================================================================
# MÓDULO: reportes/serializers.py
# DESCRIPCIÓN: Serializers para validación y estructuración de peticiones de reportes.
# ==============================================================================
from rest_framework import serializers


class ReporteFiltrosSerializer(serializers.Serializer):
    """Filtros opcionales dinámicos."""
    fecha_desde = serializers.DateField(required=False, allow_null=True)
    fecha_hasta = serializers.DateField(required=False, allow_null=True)
    estado = serializers.CharField(required=False, allow_blank=True)
    modalidad = serializers.CharField(required=False, allow_blank=True)
    psicologo_id = serializers.CharField(required=False, allow_blank=True)
    paciente_id = serializers.CharField(required=False, allow_blank=True)
    genero = serializers.CharField(required=False, allow_blank=True)
    tipo = serializers.CharField(required=False, allow_blank=True)
    severidad = serializers.CharField(required=False, allow_blank=True)
    resuelta = serializers.CharField(required=False, allow_blank=True)
    activo = serializers.CharField(required=False, allow_blank=True)
    especialidad = serializers.CharField(required=False, allow_blank=True)


class ReporteOrdenSerializer(serializers.Serializer):
    columna = serializers.CharField(required=True)
    direccion = serializers.ChoiceField(choices=['ASC', 'DESC'], default='ASC')


class ReportePersonalizadoRequestSerializer(serializers.Serializer):
    """Validador de petición para el constructor visual de reportes."""
    fuente = serializers.CharField(required=True)
    columnas = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    filtros = serializers.DictField(required=False, default=dict)
    orden = ReporteOrdenSerializer(required=False, allow_null=True)


class EnviarReporteEmailSerializer(serializers.Serializer):
    """Validador para envío de reporte por correo."""
    email = serializers.EmailField(required=True)
    asunto = serializers.CharField(required=False, default="Reporte Clínico SIGEPSI")
    fuente = serializers.CharField(required=True)
    filtros = serializers.DictField(required=False, default=dict)
    columnas = serializers.ListField(child=serializers.CharField(), required=False)
