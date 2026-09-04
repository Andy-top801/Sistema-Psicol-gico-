from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context, get_public_schema_name
from tenants.models import Tenant, Dominio
from accounts.models import Usuario, Rol, Permiso, RolPermiso
from core.models import Centro

class Command(BaseCommand):
    help = 'Siembra datos iniciales (SuperAdmin, Roles, Permisos y Centros Demo) para SIGEPSI.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("==> Iniciando siembra de datos SIGEPSI Sprint 0..."))

        # 1. En esquema public: Crear Tenant Public y SuperAdmin
        with schema_context(get_public_schema_name()):
            # Crear o verificar Tenant Public
            public_tenant, created = Tenant.objects.get_or_create(
                schema_name=get_public_schema_name(),
                defaults={
                    'nombre': 'Plataforma Global SIGEPSI',
                    'slug': 'public',
                    'plan': 'ENTERPRISE',
                    'activo': True
                }
            )
            if created:
                Dominio.objects.get_or_create(
                    domain='localhost',
                    tenant=public_tenant,
                    is_primary=True
                )
                self.stdout.write(self.style.SUCCESS("[OK] Tenant 'public' creado con dominio 'localhost'"))

            # Crear SuperAdmin en public
            if not Usuario.objects.filter(email='admin@sigepsi.com').exists():
                superadmin = Usuario.objects.create_superuser(
                    email='admin@sigepsi.com',
                    password='Admin1234*',
                    nombre='SuperAdmin',
                    apellido='Global'
                )
                self.stdout.write(self.style.WARNING("! SuperAdmin ya existe (admin@sigepsi.com)"))

            # Sembrar roles y permisos en esquema public
            from accounts.utils import seed_tenant_roles_and_permissions
            seed_tenant_roles_and_permissions()
            self.stdout.write(self.style.SUCCESS("[OK] Roles y permisos sembrados en esquema 'public'"))

        # 2. Función auxiliar para sembrar datos dentro de un tenant
        def seed_tenant_data(tenant_obj):
            with schema_context(tenant_obj.schema_name):
                from accounts.utils import seed_tenant_roles_and_permissions

                # A. Permisos y Roles del sistema (usando utilidad compartida)
                roles_map = seed_tenant_roles_and_permissions()

                # B. Configuración del Centro
                Centro.objects.get_or_create(
                    defaults={
                        "nombre": tenant_obj.nombre,
                        "direccion": tenant_obj.direccion or "Av. Las Américas #450, Santa Cruz",
                        "telefono": tenant_obj.telefono or "+591 3 3456789",
                        "email": tenant_obj.email_contacto or f"contacto@{tenant_obj.slug}.com",
                        "horarios_atencion": {
                            "lunes_viernes": "08:00 - 19:00",
                            "sabado": "08:00 - 14:00"
                        },
                        "configuracion": {
                            "cancelacion_horas_anticipacion": 24,
                            "duracion_sesion_minutos": 50,
                            "modalidad_predeterminada": "Mixta (Presencial / Virtual)"
                        }
                    }
                )

                # C. Usuarios Demo del Centro
                domain_clean = tenant_obj.slug.replace('_', '')
                usuarios_demo = [
                    (f"admin@{domain_clean}.com", "Admin1234*", "Admin", f"{tenant_obj.nombre}", Rol.ADMIN_CENTRO, "+591 70011111"),
                    (f"psicologo@{domain_clean}.com", "Psico1234*", "Lic. Carlos", "Mendoza", Rol.PSICOLOGO, "+591 70022222"),
                    (f"recepcion@{domain_clean}.com", "Recep1234*", "María", "González", Rol.RECEPCIONISTA, "+591 70033333"),
                    (f"coordinador@{domain_clean}.com", "Coord1234*", "Dr. Roberto", "Paz", Rol.COORDINADOR, "+591 70044444"),
                ]

                for email, pwd, nom, ape, r_nom, tel in usuarios_demo:
                    if not Usuario.objects.filter(email=email).exists():
                        u = Usuario.objects.create_user(
                            email=email,
                            password=pwd,
                            nombre=nom,
                            apellido=ape,
                            telefono=tel,
                            rol=roles_map[r_nom],
                            activo=True
                        )
                        self.stdout.write(self.style.SUCCESS(f"  [OK] Usuario creado en '{tenant_obj.slug}': {email} [{r_nom}]"))

        # 3. Crear Centro Demo 1: Centro Psicológico Esperanza
        with schema_context(get_public_schema_name()):
            c1, created = Tenant.objects.get_or_create(
                slug='centro_esperanza',
                defaults={
                    'nombre': 'Centro Psicológico Esperanza',
                    'schema_name': 'centro_esperanza',
                    'direccion': 'Av. Principal #321, Santa Cruz',
                    'telefono': '+591 3 3450000',
                    'email_contacto': 'info@esperanza.com',
                    'plan': 'PREMIUM',
                    'activo': True
                }
            )
            if created:
                Dominio.objects.create(domain='esperanza.localhost', tenant=c1, is_primary=True)
                self.stdout.write(self.style.SUCCESS(f"[OK] Tenant '{c1.nombre}' creado."))

        seed_tenant_data(c1)

        # 4. Crear Centro Demo 2: Gabinete MenteSana
        with schema_context(get_public_schema_name()):
            c2, created = Tenant.objects.get_or_create(
                slug='mentesana',
                defaults={
                    'nombre': 'Gabinete Integral MenteSana',
                    'schema_name': 'mentesana',
                    'direccion': 'Calle Sucre #500, Cochabamba',
                    'telefono': '+591 4 4567890',
                    'email_contacto': 'contacto@mentesana.com',
                    'plan': 'PRO',
                    'activo': True
                }
            )
            if created:
                Dominio.objects.create(domain='mentesana.localhost', tenant=c2, is_primary=True)
                self.stdout.write(self.style.SUCCESS(f"[OK] Tenant '{c2.nombre}' creado."))

        seed_tenant_data(c2)

        self.stdout.write(self.style.SUCCESS("\n==> ¡Siembra de datos completada exitosamente! <==\n"))
