from django.contrib import admin

from .models import Especialidad, Psicologo, DisponibilidadPsicologo, Paciente, Cita


admin.site.register(Especialidad)
admin.site.register(Psicologo)
admin.site.register(DisponibilidadPsicologo)
admin.site.register(Paciente)
admin.site.register(Cita)
