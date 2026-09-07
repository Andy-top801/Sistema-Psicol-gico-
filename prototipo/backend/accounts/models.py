import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from datetime import timedelta

class Rol(models.Model):
    ADMIN_CENTRO = "Admin Centro"
    RECEPCIONISTA = "Recepcionista"
    COORDINADOR = "Coordinador Clínico"
    PSICOLOGO = "Psicólogo"
    PACIENTE = "Paciente"
    SUPERADMIN = "SuperAdmin"

    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Rol")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['id']

    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Permiso")
    codigo = models.CharField(max_length=100, unique=True, verbose_name="Código Identificador")
    modulo = models.CharField(max_length=50, verbose_name="Módulo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
        ordering = ['modulo', 'codigo']

    def __str__(self):
        return f"{self.modulo}: {self.nombre} ({self.codigo})"


class RolPermiso(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name="permisos_asignados")
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE, related_name="roles_con_permiso")

    class Meta:
        verbose_name = "Asignación Rol-Permiso"
        verbose_name_plural = "Asignaciones Rol-Permisos"
        unique_together = ('rol', 'permiso')

    def __str__(self):
        return f"{self.rol.nombre} -> {self.permiso.codigo}"


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('activo', True)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=150, unique=True, verbose_name="Correo Electrónico")
    nombre = models.CharField(max_length=100, verbose_name="Nombres")
    apellido = models.CharField(max_length=100, blank=True, default="", verbose_name="Apellidos")
    telefono = models.CharField(max_length=30, blank=True, null=True, verbose_name="Teléfono")
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name="usuarios")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-fecha_creacion']

    def __str__(self):
        rol_name = self.rol.nombre if self.rol else "Sin Rol"
        return f"{self.nombre} {self.apellido} <{self.email}> [{rol_name}]"

    def tiene_permiso(self, codigo_permiso):
        """Verifica si el usuario tiene un permiso a través de su rol o si es superusuario."""
        if self.is_superuser:
            return True
        if not self.rol:
            return False
        return RolPermiso.objects.filter(rol=self.rol, permiso__codigo=codigo_permiso).exists()


class TokenRecuperacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="tokens_recuperacion")
    token = models.CharField(max_length=128, unique=True, verbose_name="Token Temporal")
    fecha_expiracion = models.DateTimeField(verbose_name="Fecha de Expiración")
    usado = models.BooleanField(default=False, verbose_name="Usado")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Token de Recuperación"
        verbose_name_plural = "Tokens de Recuperación"

    def __str__(self):
        return f"Token para {self.usuario.email} (Usado: {self.usado})"

    def es_valido(self):
        return (not self.usado) and (timezone.now() <= self.fecha_expiracion)

    @classmethod
    def generar_para_usuario(cls, usuario, horas_validez=24):
        token_str = uuid.uuid4().hex + uuid.uuid4().hex
        expiracion = timezone.now() + timedelta(hours=horas_validez)
        return cls.objects.create(
            usuario=usuario,
            token=token_str,
            fecha_expiracion=expiracion,
            usado=False
        )
