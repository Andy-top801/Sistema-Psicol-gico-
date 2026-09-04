import uuid
from django.db import models

class Centro(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150, verbose_name="Nombre Institucional")
    direccion = models.CharField(max_length=255, blank=True, default="", verbose_name="Dirección")
    telefono = models.CharField(max_length=50, blank=True, default="", verbose_name="Teléfono")
    email = models.EmailField(max_length=150, blank=True, default="", verbose_name="Email Institucional")
    logo = models.TextField(blank=True, null=True, verbose_name="URL o Base64 del Logo")
    horarios_atencion = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Horarios de Atención Semanal"
    )
    configuracion = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Configuración y Políticas del Gabinete"
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración del Centro Psicológico"
        verbose_name_plural = "Configuraciones del Centro"

    def __str__(self):
        return self.nombre

    def actualizar_config(self, datos):
        for key, value in datos.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        return self
