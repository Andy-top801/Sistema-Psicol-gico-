from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Centro(TenantMixin):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True
    auto_drop_schema = True

class Dominio(DomainMixin):
    pass
