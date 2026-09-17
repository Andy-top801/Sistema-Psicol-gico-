# ==============================================================================
# MÓDULO: subscriptions/serializers.py
# DESCRIPCIÓN: Serializadores para validar datos de checkout y retornar planes.
# PUNTO 7+8: Modelo SaaS en la nube — Web/Móvil con pasarela de pagos Stripe
# ==============================================================================
import re
from rest_framework import serializers
from subscriptions.plans import get_plan, get_all_plans


class PlanSerializer(serializers.Serializer):
    """Serializa un plan para su presentación en la landing page."""
    id = serializers.CharField()
    nombre = serializers.CharField()
    precio_mensual = serializers.IntegerField()
    moneda = serializers.CharField()
    max_psicologos = serializers.IntegerField()
    max_pacientes = serializers.IntegerField()
    recomendado = serializers.BooleanField(default=False)
    features = serializers.ListField(child=serializers.CharField())


class CreateCheckoutSerializer(serializers.Serializer):
    """Valida los datos necesarios para crear una sesión de Stripe Checkout."""
    plan = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    nombre_centro = serializers.CharField(max_length=150)
    nombre_admin = serializers.CharField(max_length=100, default='Administrador')

    def validate_plan(self, value):
        plan = get_plan(value)
        if not plan:
            raise serializers.ValidationError(
                'Plan no válido. Opciones: basico, profesional, empresarial.'
            )
        return value

    def validate_nombre_centro(self, value):
        """Genera un slug seguro a partir del nombre del centro."""
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                'El nombre del centro debe tener al menos 3 caracteres.'
            )
        return value


class VerifySessionSerializer(serializers.Serializer):
    """Valida el session_id recibido de Stripe Checkout."""
    session_id = serializers.CharField(max_length=255)
