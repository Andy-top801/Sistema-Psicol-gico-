from django.contrib import admin
from clinica.models import Especialidad, Psicologo, PsicologoEspecialidad, Disponibilidad, Paciente

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Psicologo)
class PsicologoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'numero_colegiado', 'modalidad', 'tarifa_base', 'activo', 'fecha_ingreso')
    search_fields = ('usuario__nombre', 'usuario__apellido', 'numero_colegiado')
    list_filter = ('modalidad', 'activo')

@admin.register(Disponibilidad)
class DisponibilidadAdmin(admin.ModelAdmin):
    list_display = ('psicologo', 'dia_semana', 'hora_inicio', 'hora_fin', 'duracion_bloque_min', 'activo')
    list_filter = ('dia_semana', 'activo')

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('codigo_expediente', 'usuario', 'ci', 'fecha_nacimiento', 'genero', 'fecha_registro')
    search_fields = ('codigo_expediente', 'ci', 'usuario__nombre', 'usuario__apellido')
