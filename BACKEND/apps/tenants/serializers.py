import re

from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from rest_framework import serializers

from .models import Centro, Dominio

RESERVED_SCHEMAS = {'public', 'information_schema', 'pg_catalog', 'pg_toast'}
SCHEMA_RE = re.compile(r'^[a-z][a-z0-9_]{2,62}$')


class DominioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dominio
        fields = ['id', 'domain', 'is_primary']


class CentroSerializer(serializers.ModelSerializer):
    """CU1 / HU-03 — alta de un centro (schema aislado) + su primer AdminCentro."""

    domains = DominioSerializer(many=True, read_only=True)
    domain_url = serializers.CharField(write_only=True, required=False)

    # Primer administrador del centro (se crea dentro del schema nuevo)
    admin_email = serializers.EmailField(write_only=True, required=False)
    admin_password = serializers.CharField(
        write_only=True, required=False, style={'input_type': 'password'}
    )
    admin_first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    admin_last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Centro
        fields = [
            'id', 'name', 'schema_name', 'is_active', 'created_at', 'domains',
            'domain_url', 'admin_email', 'admin_password',
            'admin_first_name', 'admin_last_name',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_schema_name(self, value):
        value = value.strip().lower()
        if value in RESERVED_SCHEMAS or value.startswith('pg_'):
            raise serializers.ValidationError('Ese nombre de esquema está reservado.')
        if not SCHEMA_RE.match(value):
            raise serializers.ValidationError(
                'Solo minúsculas, números y guion bajo; empieza por letra; 3–63 caracteres.'
            )
        if Centro.objects.filter(schema_name=value).exists():
            raise serializers.ValidationError('Ya existe un centro con ese esquema.')
        return value

    def validate(self, attrs):
        if attrs.get('admin_email') and not attrs.get('admin_password'):
            raise serializers.ValidationError(
                {'admin_password': 'Indica una contraseña para el administrador inicial.'}
            )
        return attrs

    def create(self, validated_data):
        domain_url = validated_data.pop('domain_url', None)
        admin_email = validated_data.pop('admin_email', None)
        admin_password = validated_data.pop('admin_password', None)
        admin_first = validated_data.pop('admin_first_name', '') or 'Admin'
        admin_last = validated_data.pop('admin_last_name', '') or 'Centro'

        # El tenant SIEMPRE se crea desde el schema public (django-tenants).
        with schema_context('public'):
            tenant = Centro.objects.create(**validated_data)
            if domain_url:
                Dominio.objects.create(
                    domain=domain_url.strip().lower(), tenant=tenant, is_primary=True
                )

        # El primer AdminCentro vive dentro del schema recién creado.
        if admin_email and admin_password:
            User = get_user_model()
            from apps.users.models import Rol

            with schema_context(tenant.schema_name):
                rol_admin, _ = Rol.objects.get_or_create(
                    name='AdminCentro',
                    defaults={'description': 'Administrador del centro'},
                )
                if not User.objects.filter(email__iexact=admin_email).exists():
                    user = User.objects.create_user(
                        username=admin_email,
                        email=admin_email,
                        password=admin_password,
                        first_name=admin_first,
                        last_name=admin_last,
                        is_staff=True,
                    )
                    user.roles.add(rol_admin)

        return tenant
