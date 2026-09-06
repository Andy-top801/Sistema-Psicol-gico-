from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Centro, Dominio
from .serializers import CentroSerializer, DominioSerializer

class CentroViewSet(viewsets.ModelViewSet):
    queryset = Centro.objects.all()
    serializer_class = CentroSerializer
    permission_classes = [IsAuthenticated] # Adjust as needed (e.g. IsAdminUser)

    def get_queryset(self):
        # Depending on the user's role, they might only see their own tenant
        # or if they are SuperAdmin, they can see all
        user = self.request.user
        # Assuming we can check if user is a superadmin
        if user.is_superuser:
            return Centro.objects.all()
        # Otherwise, they only see the tenant they belong to
        # In django-tenants, the current tenant is accessible via request.tenant
        return Centro.objects.filter(id=self.request.tenant.id)
