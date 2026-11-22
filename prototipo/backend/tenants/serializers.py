import re
from rest_framework import serializers
from django.db import transaction
from django_tenants.utils import schema_context
from tenants.models import Tenant, Dominio
from accounts.models import Usuario, Rol

class DominioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dominio
        fields = ['id', 'domain', 'is_primary']


class TenantSerializer(serializers.ModelSerializer):
    dominios = DominioSerializer(many=True, read_only=True)
    admin_email = serializers.EmailField(write_only=True, required=False)
    admin_password = serializers.CharField(write_only=True, required=False, min_length=8)
    admin_nombre = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Tenant
        fields = [
            'id', 'nombre', 'slug', 'schema_name', 'direccion', 'telefono',
            'email_contacto', 'plan', 'activo', 'fecha_creacion', 'dominios',
            'admin_email', 'admin_password', 'admin_nombre'
        ]
        read_only_fields = ['id', 'schema_name', 'fecha_creacion']

    def validate_slug(self, value):
        """
        CU1: Gestionar Centros Psicológicos (HU-03, HU-04)
        --- Paso 3: Valida disponibilidad Dominio ---
        """
        slug = value.lower().strip()
        if not re.match(r'^[a-z0-9_]+$', slug):
            raise serializers.ValidationError("El identificador debe contener únicamente letras minúsculas, números y guiones bajos.")
        if slug in ['public', 'schema', 'admin', 'api', 'root', 'system']:
            raise serializers.ValidationError("Este identificador está reservado por el sistema.")
        # --- Paso 4: Dominio disponible ---
        return slug

    def create(self, validated_data):
        """
        CU1: Gestionar Centros Psicológicos (HU-03, HU-04, HU-07, HU-08)
        Diagrama de Comunicación – Pasos en Base de Datos (PostgreSQL):
          Paso 3: Valida disponibilidad Dominio
          Paso 4: Dominio disponible
          Paso 5: insert(Tenant, Dominio)
          Paso 6: Registros creados
          Paso 7: CREATE SCHEMA y Migraciones
          Paso 8: Esquema creado
        """
        admin_email = validated_data.pop('admin_email', None)
        admin_password = validated_data.pop('admin_password', None)
        admin_nombre = validated_data.pop('admin_nombre', 'Administrador')
        
        slug = validated_data.get('slug')
        if not validated_data.get('schema_name'):
            validated_data['schema_name'] = slug

        # --- Asegurar que la creación del tenant se ejecute en el esquema public ---
        with schema_context('public'):
            with transaction.atomic():
                # --- Paso 5: insert(Tenant, Dominio) ---
                # --- Paso 7: CREATE SCHEMA y Migraciones (auto_create_schema=True) ---
                tenant = Tenant.objects.create(**validated_data)
                
                # Crear dominio asociado
                dominio_str = f"{slug}.localhost"
                Dominio.objects.create(
                    domain=dominio_str,
                    tenant=tenant,
                    is_primary=True
                )
                # --- Paso 6: Registros creados ---
                # --- Paso 8: Esquema creado y listo para poblar ---

        # Inicializar datos en el nuevo esquema del tenant aprovisionado
        with schema_context(tenant.schema_name):
            from core.models import Centro
            from accounts.utils import seed_tenant_roles_and_permissions
            from clinica.models import Especialidad

            Centro.objects.create(
                nombre=tenant.nombre,
                direccion=tenant.direccion or "",
                telefono=tenant.telefono or "",
                email=tenant.email_contacto or "",
                horarios_atencion={"lunes_viernes": "08:00 - 18:00", "sabado": "08:00 - 13:00"},
                configuracion={"cancelacion_horas_anticipacion": 24, "duracion_sesion_minutos": 50}
            )

            # Sembrar catálogo estándar de especialidades clínicas para este tenant (CU6 / HU-11)
            especialidades_data = [
                ("Terapia Cognitivo-Conductual (TCC)", "Reestructuración cognitiva y abordaje de esquemas desadaptativos y ansiedad."),
                ("Psicología Clínica y de la Salud", "Evaluación, diagnóstico y tratamiento de trastornos emocionales y del estado de ánimo."),
                ("Terapia Familiar y Sistémica", "Intervención sistémica orientada a la resolución de conflictos vinculares y de pareja."),
                ("Neuropsicología y Rehabilitación", "Evaluación de funciones cognitivas, memoria, atención y estimulación neurocognitiva."),
                ("Psicología Infantil y del Desarrollo", "Abordaje de trastornos del neurodesarrollo, conducta y apego en infancia y adolescencia."),
                ("Terapia de Aceptación y Compromiso (ACT)", "Intervenciones contextuales de tercera generación para flexibilidad psicológica."),
                ("Psicooncología y Cuidados Paliativos", "Acompañamiento psicológico en enfermedades crónicas, duelo y trauma vital."),
                ("Adicciones y Conductas Compulsivas", "Prevención de recaídas y modificación conductual en dependencias.")
            ]
            for nom, desc in especialidades_data:
                Especialidad.objects.get_or_create(nombre=nom, defaults={'descripcion': desc})

            # Sembrar TODOS los permisos y roles del sistema
            roles_map = seed_tenant_roles_and_permissions()
            rol_admin = roles_map[Rol.ADMIN_CENTRO]

            # Si se proveyó correo para el admin del centro
            target_email = admin_email or tenant.email_contacto or f"admin@{slug}.com"
            target_pass = admin_password or "Admin1234*"
            
            admin_user = Usuario.objects.create_user(
                email=target_email,
                password=target_pass,
                nombre=admin_nombre,
                apellido="Centro",
                rol=rol_admin,
                activo=True
            )

        return tenant
