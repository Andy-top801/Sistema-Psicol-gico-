from django.contrib import admin

from .models import Especialidad, Psicologo, DisponibilidadPsicologo


admin.site.register(Especialidad)
admin.site.register(Psicologo)
admin.site.register(DisponibilidadPsicologo)
