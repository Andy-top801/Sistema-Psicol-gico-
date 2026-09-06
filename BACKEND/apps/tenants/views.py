from django.db import connection
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import HasAnyRole, user_roles

from .models import Centro
from .serializers import CentroSerializer


class CentroViewSet(viewsets.ModelViewSet):
    """CU1 — Gestionar centros psicológicos y configuración Multi-Tenant.

    - Alta / baja / suspensión: solo SuperAdmin (HU-03, HU-08).
    - Un AdminCentro solo ve (lectura) su propio centro (HU-07).
    """

    queryset = Centro.objects.all().prefetch_related('domains')
    serializer_class = CentroSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    read_roles = {'superadmin', 'admincentro'}
    write_roles = {'superadmin'}

    def get_queryset(self):
        qs = super().get_queryset()
        if 'superadmin' in user_roles(self.request.user):
            return qs
        # Aislamiento: cada centro solo se ve a sí mismo.
        return qs.filter(schema_name=connection.schema_name)
