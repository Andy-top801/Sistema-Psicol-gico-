import uuid
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Tenant(TenantMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre del Centro")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Identificador Slug")
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=30, blank=True, null=True, verbose_name="Teléfono")
    email_contacto = models.EmailField(max_length=150, blank=True, null=True, verbose_name="Email de Contacto")
    plan = models.CharField(max_length=50, default="PRO", verbose_name="Plan de Suscripción")
    activo = models.BooleanField(default=True, verbose_name="Estado Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    # default_schema_name can be auto-generated or slug
    auto_create_schema = True
    auto_drop_schema = True

    class Meta:
        verbose_name = "Centro Psicológico (Tenant)"
        verbose_name_plural = "Centros Psicológicos (Tenants)"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} ({self.schema_name})"

    def suspender(self):
        self.activo = False
        self.save()

    def activar(self):
        self.activo = True
        self.save()


class Dominio(DomainMixin):
    id = models.AutoField(primary_key=True)
    
    class Meta:
        verbose_name = "Dominio de Centro"
        verbose_name_plural = "Dominios de Centros"

    def __str__(self):
        return self.domain


class BackupRegistro(models.Model):
    """
    CE_BackupLogRegistro: Almacena los metadatos y checksum SHA-256 de volcados en la tabla backups_registro.
    Cumple con el diagrama de comunicación y secuencia de HU-39 (CU28).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    archivo = models.CharField(max_length=255, verbose_name="Nombre de Archivo")
    sha256 = models.CharField(max_length=64, verbose_name="Checksum SHA-256")
    tamano = models.BigIntegerField(default=0, verbose_name="Tamaño en Bytes")
    tamano_mb = models.FloatField(default=0.0, verbose_name="Tamaño en MB")
    ambito = models.CharField(max_length=50, default="TENANT", verbose_name="Ámbito (GLOBAL o TENANT)")
    schema_name = models.CharField(max_length=100, default="public", verbose_name="Esquema de BD")
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True, related_name="backups")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Generación")
    origen = models.CharField(max_length=50, default="MANUAL", verbose_name="Origen (MANUAL o CRON)")
    estado = models.CharField(max_length=50, default="COMPLETADO", verbose_name="Estado")
    url_descarga = models.CharField(max_length=255, blank=True, null=True, verbose_name="URL de Descarga")

    class Meta:
        db_table = 'backups_registro'
        verbose_name = "Registro de Copia de Seguridad"
        verbose_name_plural = "Registros de Copias de Seguridad"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.archivo} ({self.sha256[:8]}...) - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
