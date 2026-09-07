from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from tenants.models import Tenant, Dominio

class DominioInline(admin.TabularInline):
    model = Dominio
    max_num = 1

@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'schema_name', 'plan', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'plan')
    search_fields = ('nombre', 'slug', 'schema_name')
    inlines = [DominioInline]
