from django.contrib import admin
from core.models import Centro

@admin.register(Centro)
class CentroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'fecha_actualizacion')
