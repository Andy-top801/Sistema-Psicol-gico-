"""
Autenticación JWT personalizada para SIGEPSI Multi-Tenant.
Permite que el SuperAdmin (que vive en el esquema 'public') se autentique
en cualquier esquema de tenant, haciendo fallback al esquema público.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import connection
from django_tenants.utils import get_public_schema_name, schema_context


class TenantAwareJWTAuthentication(JWTAuthentication):
    """
    Extiende JWTAuthentication para soportar autenticación cross-schema.
    
    Flujo:
    1. Intenta autenticar al usuario en el esquema actual del tenant.
    2. Si falla (usuario no encontrado), intenta en el esquema 'public'.
    3. Si el usuario del esquema público es superuser, lo acepta.
    """

    def get_user(self, validated_token):
        # Primero intentar en el esquema actual
        try:
            return super().get_user(validated_token)
        except Exception:
            pass

        # Si estamos en un esquema de tenant (no public), intentar en public
        current_schema = connection.schema_name
        if current_schema != get_public_schema_name():
            try:
                with schema_context(get_public_schema_name()):
                    user = super().get_user(validated_token)
                    # Solo permitir fallback para superusuarios
                    if user and user.is_superuser:
                        return user
            except Exception:
                pass

        # Si nada funciona, dejar que SimpleJWT lance su error estándar
        return super().get_user(validated_token)
