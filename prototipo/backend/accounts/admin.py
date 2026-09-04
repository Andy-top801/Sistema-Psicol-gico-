from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import Usuario, Rol, Permiso, RolPermiso, TokenRecuperacion

class RolPermisoInline(admin.TabularInline):
    model = RolPermiso
    extra = 1

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    inlines = [RolPermisoInline]

@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'codigo', 'modulo')
    list_filter = ('modulo',)
    search_fields = ('nombre', 'codigo')

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nombre', 'apellido', 'rol', 'activo', 'is_staff')
    list_filter = ('activo', 'rol', 'is_staff')
    search_fields = ('email', 'nombre', 'apellido')
    ordering = ('-fecha_creacion',)

@admin.register(TokenRecuperacion)
class TokenRecuperacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'token', 'fecha_expiracion', 'usado', 'fecha_creacion')
    list_filter = ('usado',)
