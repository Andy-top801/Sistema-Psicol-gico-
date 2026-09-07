import re
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from accounts.models import Usuario, Rol, Permiso, RolPermiso, TokenRecuperacion

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ['id', 'nombre', 'codigo', 'modulo', 'descripcion']


class RolSerializer(serializers.ModelSerializer):
    permisos = PermisoSerializer(source='permisos_asignados.permiso', many=True, read_only=True)
    permiso_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion', 'permisos', 'permiso_ids']

    def create(self, validated_data):
        permiso_ids = validated_data.pop('permiso_ids', [])
        rol = Rol.objects.create(**validated_data)
        for p_id in permiso_ids:
            try:
                p = Permiso.objects.get(id=p_id)
                RolPermiso.objects.create(rol=rol, permiso=p)
            except Permiso.DoesNotExist:
                pass
        return rol

    def update(self, instance, validated_data):
        """
        CU4: Gestionar Roles y Permisos (HU-06)
        Diagrama de Comunicación – Pasos en Base de Datos (PostgreSQL):
          Paso 5: SELECT * FROM accounts_permiso WHERE id IN (?)
          Paso 6: Permisos validados
          Paso 7: DELETE FROM accounts_rol_permiso WHERE rol_id = ?
          Paso 8: Permisos anteriores desvinculados
          Paso 9: INSERT INTO accounts_rol_permiso (rol_id, permiso_id)
          Paso 10: Nuevos permisos registrados en esquema
        """
        permiso_ids = validated_data.pop('permiso_ids', None)
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
        instance.save()

        if permiso_ids is not None:
            # --- Paso 7: DELETE FROM accounts_rol_permiso WHERE rol_id = ? ---
            # --- Paso 8: Permisos anteriores desvinculados ---
            RolPermiso.objects.filter(rol=instance).delete()
            for p_id in permiso_ids:
                try:
                    # --- Paso 5: SELECT * FROM accounts_permiso WHERE id IN (?) ---
                    p = Permiso.objects.get(id=p_id)
                    # --- Paso 6: Permisos validados ---
                    # --- Paso 9: INSERT INTO accounts_rol_permiso (rol_id, permiso_id) ---
                    # --- Paso 10: Nuevos permisos registrados en esquema ---
                    RolPermiso.objects.create(rol=instance, permiso=p)
                except Permiso.DoesNotExist:
                    pass
        return instance


class UsuarioSerializer(serializers.ModelSerializer):
    rol_detalle = RolSerializer(source='rol', read_only=True)
    rol_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nombre', 'apellido', 'telefono',
            'rol', 'rol_detalle', 'rol_id', 'activo', 'is_staff',
            'is_superuser', 'fecha_creacion', 'password'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'is_staff', 'is_superuser', 'rol']

    def validate_password(self, value):
        if value:
            if len(value) < 8:
                raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
            if not re.search(r'[A-Z]', value):
                raise serializers.ValidationError("La contraseña debe contener al menos una letra mayúscula.")
            if not re.search(r'[0-9]', value):
                raise serializers.ValidationError("La contraseña debe contener al menos un número.")
            if not re.search(r'[^A-Za-z0-9]', value):
                raise serializers.ValidationError("La contraseña debe contener al menos un carácter especial.")
        return value

    def create(self, validated_data):
        """
        CU3: Gestionar Usuarios (HU-05)
        Diagrama de Comunicación – Pasos en Base de Datos (PostgreSQL):
          Paso 5: Validar datos y unicidad de email
          Paso 6: Email disponible
          Paso 7: SELECT rol WHERE id = ?
          Paso 8: Rol encontrado
          Paso 9: INSERT INTO accounts_usuario (email, password_hash, rol_id)
          Paso 10: Usuario guardado en esquema tenant
        """
        rol_id = validated_data.pop('rol_id', None)
        password = validated_data.pop('password', None)
        if rol_id:
            try:
                # --- Paso 7: SELECT rol WHERE id = ? ---
                # --- Paso 8: Rol encontrado ---
                validated_data['rol'] = Rol.objects.get(id=rol_id)
            except Rol.DoesNotExist:
                pass
        
        # --- Paso 9: INSERT INTO accounts_usuario (email, password_hash, rol_id) ---
        # --- Paso 10: Usuario guardado en esquema tenant ---
        user = Usuario.objects.create_user(password=password, **validated_data)

        # Sincronización automática de perfil profesional para rol Psicólogo
        if user.rol and 'psic' in user.rol.nombre.lower():
            try:
                import random
                from clinica.models import Psicologo
                from clinica.serializers import crear_disponibilidad_default
                if not Psicologo.objects.filter(usuario=user).exists():
                    num_col = f"COL-PSI-{random.randint(1000, 9999)}"
                    while Psicologo.objects.filter(numero_colegiado=num_col).exists():
                        num_col = f"COL-PSI-{random.randint(1000, 9999)}"
                    psico = Psicologo.objects.create(
                        usuario=user,
                        numero_colegiado=num_col,
                        tarifa_base=150.00,
                        modalidad='MIXTA',
                        activo=True
                    )
                    crear_disponibilidad_default(psico)
            except Exception:
                pass

        return user

    def update(self, instance, validated_data):
        rol_id = validated_data.pop('rol_id', None)
        password = validated_data.pop('password', None)
        if rol_id is not None:
            try:
                instance.rol = Rol.objects.get(id=rol_id) if rol_id else None
            except Rol.DoesNotExist:
                pass

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()

        # Sincronización automática si se asigna rol Psicólogo
        if instance.rol and 'psic' in instance.rol.nombre.lower():
            try:
                import random
                from clinica.models import Psicologo
                from clinica.serializers import crear_disponibilidad_default
                if not Psicologo.objects.filter(usuario=instance).exists():
                    num_col = f"COL-PSI-{random.randint(1000, 9999)}"
                    while Psicologo.objects.filter(numero_colegiado=num_col).exists():
                        num_col = f"COL-PSI-{random.randint(1000, 9999)}"
                    psico = Psicologo.objects.create(
                        usuario=instance,
                        numero_colegiado=num_col,
                        tarifa_base=150.00,
                        modalidad='MIXTA',
                        activo=True
                    )
                    crear_disponibilidad_default(psico)
            except Exception:
                pass

        return instance


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    rol_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'password', 'nombre', 'apellido', 'telefono', 'rol_id']

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos una mayúscula.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos un número.")
        if not re.search(r'[^A-Za-z0-9]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos un carácter especial.")
        return value

    def create(self, validated_data):
        rol_id = validated_data.pop('rol_id', None)
        password = validated_data.pop('password')
        if rol_id:
            try:
                validated_data['rol'] = Rol.objects.get(id=rol_id)
            except Rol.DoesNotExist:
                pass
        return Usuario.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    tenant = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        """
        CU2: Gestionar Inicio de Sesión y Autenticación (HU-01, HU-02)
        Diagrama de Comunicación – Pasos en Backend / Base de Datos:
          Paso 3: Validar tenant y conmutar schema
          Paso 4: Esquema PostgreSQL activo
          Paso 5: SELECT usuario WHERE email = ? AND activo = true
          Paso 6: Retornar usuario y hash password
          Paso 7: Verificar password (PBKDF2) y generar JWT
          Paso 8: Tokens JWT generados (con claims)
        """
        email = attrs.get('email', '').strip()
        password = attrs.get('password')
        tenant_param = attrs.get('tenant')

        if not email or not password:
            raise serializers.ValidationError("Debe ingresar correo y contraseña.")

        from django.db import connection
        from django_tenants.utils import schema_context
        from tenants.models import Tenant

        user = None
        target_tenant = None

        if tenant_param and str(tenant_param).strip().lower() != 'public':
            try:
                try:
                    tenant_obj = Tenant.objects.get(id=tenant_param)
                except Exception:
                    tenant_obj = Tenant.objects.get(slug=tenant_param)
                if not tenant_obj.activo:
                    raise serializers.ValidationError("El centro psicológico se encuentra inactivo o suspendido.")
                connection.set_tenant(tenant_obj)
                target_tenant = tenant_obj
            except Tenant.DoesNotExist:
                raise serializers.ValidationError("Centro psicológico no encontrado.")

            user = Usuario.objects.filter(email__iexact=email).first()
            if not user:
                raise serializers.ValidationError("Credenciales inválidas.")
        else:
            # Si no se pasó tenant o se pasó public, buscar en public primero
            user = Usuario.objects.filter(email__iexact=email).first()
            if not user:
                # Búsqueda automática en todos los esquemas de tenants activos
                for t in Tenant.objects.exclude(schema_name='public').filter(activo=True):
                    with schema_context(t.schema_name):
                        u_cand = Usuario.objects.filter(email__iexact=email).first()
                        if u_cand:
                            target_tenant = t
                            user = u_cand
                            break
                if target_tenant:
                    connection.set_tenant(target_tenant)
                else:
                    raise serializers.ValidationError("Credenciales inválidas.")

        # --- Paso 6: Retornar usuario y hash password ---
        # --- Paso 7: Verificar password (PBKDF2) y generar JWT ---
        if not user.check_password(password):
            raise serializers.ValidationError("Credenciales inválidas.")

        if not user.activo:
            raise serializers.ValidationError("La cuenta se encuentra desactivada.")

        # --- Paso 8: Tokens JWT generados (con claims) ---
        refresh = RefreshToken.for_user(user)
        rol_nombre = user.rol.nombre if user.rol else ("SuperAdmin" if user.is_superuser else "Usuario")
        
        # Claims personalizados
        refresh['email'] = user.email
        refresh['rol'] = rol_nombre
        refresh['nombre_completo'] = f"{user.nombre} {user.apellido}".strip()

        active_tenant = getattr(connection, 'tenant', None) or target_tenant
        tenant_data = None
        if active_tenant and getattr(active_tenant, 'schema_name', '') != 'public':
            refresh['tenant_id'] = str(active_tenant.id)
            refresh['tenant_slug'] = active_tenant.slug
            refresh['schema_name'] = active_tenant.schema_name
            tenant_data = {
                'id': str(active_tenant.id),
                'nombre': active_tenant.nombre,
                'slug': active_tenant.slug,
                'schema_name': active_tenant.schema_name,
                'plan': getattr(active_tenant, 'plan', 'PROFESIONAL'),
                'activo': active_tenant.activo
            }

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'rol': rol_nombre,
            'usuario': UsuarioSerializer(user).data,
            'tenant': tenant_data
        }



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
            return None
        except Exception:
            raise serializers.ValidationError("Token inválido o ya revocado.")


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            Usuario.objects.get(email=value, activo=True)
        except Usuario.DoesNotExist:
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)
    password_confirm = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        
        pwd = attrs['password']
        if not re.search(r'[A-Z]', pwd) or not re.search(r'[0-9]', pwd) or not re.search(r'[^A-Za-z0-9]', pwd):
            raise serializers.ValidationError("La contraseña debe incluir al menos una mayúscula, un número y un carácter especial.")

        token_obj = None
        found_tenant = None

        # 1. Intentar en el esquema actual
        try:
            token_obj = TokenRecuperacion.objects.select_related('usuario').get(token=attrs['token'])
        except TokenRecuperacion.DoesNotExist:
            # 2. Buscar en todos los esquemas de tenants activos
            from tenants.models import Tenant
            from django_tenants.utils import schema_context
            for t in Tenant.objects.exclude(slug='public').filter(activo=True):
                with schema_context(t.schema_name):
                    try:
                        token_obj = TokenRecuperacion.objects.select_related('usuario').get(token=attrs['token'])
                        found_tenant = t
                        break
                    except TokenRecuperacion.DoesNotExist:
                        continue

        if not token_obj:
            raise serializers.ValidationError("El token de recuperación no es válido o no existe.")

        if not token_obj.es_valido():
            raise serializers.ValidationError("El enlace o token de recuperación ha expirado o ya fue utilizado.")

        attrs['token_obj'] = token_obj
        attrs['tenant_obj'] = found_tenant
        return attrs
