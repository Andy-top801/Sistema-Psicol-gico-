from django.contrib import admin
from agenda.models import Cita, Teleconsulta, Alerta

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora_inicio', 'hora_fin', 'paciente', 'psicologo', 'modalidad', 'estado', 'costo')
    list_filter = ('estado', 'modalidad', 'fecha')
    search_fields = ('paciente__usuario__nombre', 'psicologo__usuario__nombre')

@admin.register(Teleconsulta)
class TeleconsultaAdmin(admin.ModelAdmin):
    list_display = ('sala_id', 'cita', 'hora_inicio_real', 'duracion_segundos')
    search_fields = ('sala_id',)

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'tipo', 'severidad', 'resuelta', 'fecha_creacion')
    list_filter = ('tipo', 'severidad', 'resuelta')
    search_fields = ('paciente__usuario__nombre', 'descripcion')
