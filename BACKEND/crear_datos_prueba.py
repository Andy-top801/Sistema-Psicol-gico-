"""
Script para crear datos de prueba del Sprint 0 de SIGEPSI.
Ejecutar con: python manage.py shell < crear_datos_prueba.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')
django.setup()

from apps.users.models import Usuario, Rol, Permiso

# ============================================================
# 1. Crear permisos base
# ============================================================
permisos_data = [
    ('Gestionar Usuarios', 'gestionar_usuarios'),
    ('Gestionar Roles', 'gestionar_roles'),
    ('Gestionar Centros', 'gestionar_centros'),
    ('Ver Dashboard', 'ver_dashboard'),
    ('Gestionar Pacientes', 'gestionar_pacientes'),
    ('Gestionar Citas', 'gestionar_citas'),
]

permisos_creados = []
for name, codename in permisos_data:
    p, created = Permiso.objects.get_or_create(codename=codename, defaults={'name': name})
    permisos_creados.append(p)
    status = 'CREADO' if created else 'YA EXISTE'
    print(f"  [{status}] Permiso: {name} ({codename})")

# ============================================================
# 2. Crear roles
# ============================================================
# SuperAdmin
rol_superadmin, created = Rol.objects.get_or_create(
    name='SuperAdmin',
    defaults={'description': 'Administrador global del sistema SIGEPSI. Acceso total.'}
)
if created:
    rol_superadmin.permisos.set(permisos_creados)
    print(f"  [CREADO] Rol: SuperAdmin (todos los permisos)")
else:
    print(f"  [YA EXISTE] Rol: SuperAdmin")

# AdminCentro
rol_admin_centro, created = Rol.objects.get_or_create(
    name='AdminCentro',
    defaults={'description': 'Administrador de un centro psicologico especifico.'}
)
if created:
    permisos_admin = Permiso.objects.filter(codename__in=['gestionar_usuarios', 'ver_dashboard', 'gestionar_pacientes', 'gestionar_citas'])
    rol_admin_centro.permisos.set(permisos_admin)
    print(f"  [CREADO] Rol: AdminCentro")
else:
    print(f"  [YA EXISTE] Rol: AdminCentro")

# Psicologo
rol_psicologo, created = Rol.objects.get_or_create(
    name='Psicologo',
    defaults={'description': 'Profesional psicologo que atiende pacientes.'}
)
if created:
    permisos_psico = Permiso.objects.filter(codename__in=['ver_dashboard', 'gestionar_pacientes', 'gestionar_citas'])
    rol_psicologo.permisos.set(permisos_psico)
    print(f"  [CREADO] Rol: Psicologo")
else:
    print(f"  [YA EXISTE] Rol: Psicologo")

# ============================================================
# 3. Crear usuario SuperAdmin de prueba
# ============================================================
email_admin = 'admin@sigepsi.com'
password_admin = 'Sigepsi2026!'

user, created = Usuario.objects.get_or_create(
    email=email_admin,
    defaults={
        'username': 'admin',
        'first_name': 'Administrador',
        'last_name': 'SIGEPSI',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
    }
)

if created:
    user.set_password(password_admin)
    user.save()
    user.roles.add(rol_superadmin)
    print(f"\n  [CREADO] Usuario SuperAdmin:")
    print(f"    Email:      {email_admin}")
    print(f"    Password:   {password_admin}")
else:
    print(f"\n  [YA EXISTE] Usuario SuperAdmin: {email_admin}")

print("\n============================================================")
print("  DATOS DE PRUEBA SPRINT 0 — COMPLETADOS")
print("============================================================")
print(f"\n  CREDENCIALES DE ACCESO:")
print(f"    Email:      {email_admin}")
print(f"    Password:   {password_admin}")
print(f"\n  ROLES DISPONIBLES:")
for r in Rol.objects.all():
    print(f"    - {r.name}: {r.description}")
print(f"\n  PERMISOS DISPONIBLES:")
for p in Permiso.objects.all():
    print(f"    - {p.name} ({p.codename})")
print("============================================================")
