from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context, get_public_schema_name
from tenants.models import Tenant, Dominio
from accounts.models import Usuario, Rol
from core.models import Centro

CENTROS_SAAS_CATALOGO = [
    {
        "slug": "centro_esperanza",
        "nombre": "Centro Psicológico Esperanza",
        "schema_name": "centro_esperanza",
        "dominio": "esperanza.localhost",
        "ciudad": "Santa Cruz",
        "direccion": "Av. Las Américas #321, Barrio Equipetrol",
        "telefono": "+591 3 3450000",
        "email": "contacto@esperanza.com",
        "plan": "ENTERPRISE",
        "activo": True
    },
    {
        "slug": "mentesana",
        "nombre": "Gabinete Integral MenteSana",
        "schema_name": "mentesana",
        "dominio": "mentesana.localhost",
        "ciudad": "Cochabamba",
        "direccion": "Calle Sucre #500, Zona Central",
        "telefono": "+591 4 4567890",
        "email": "contacto@mentesana.com",
        "plan": "PRO",
        "activo": True
    },
    {
        "slug": "equilibrio_mental",
        "nombre": "Centro de Salud Emocional Equilibrio",
        "schema_name": "equilibrio_mental",
        "dominio": "equilibrio.localhost",
        "ciudad": "La Paz",
        "direccion": "Av. 6 de Agosto #2435, San Jorge",
        "telefono": "+591 2 2431200",
        "email": "contacto@equilibrio.com",
        "plan": "ENTERPRISE",
        "activo": True
    },
    {
        "slug": "renacer_psicologia",
        "nombre": "Clínica de Psicoterapia Renacer",
        "schema_name": "renacer_psicologia",
        "dominio": "renacer.localhost",
        "ciudad": "Santa Cruz",
        "direccion": "Av. San Martín #800, Barrio Sirari",
        "telefono": "+591 3 3889010",
        "email": "info@renacerpsicologia.bo",
        "plan": "PRO",
        "activo": True
    },
    {
        "slug": "serenidad_sucre",
        "nombre": "Instituto Psicológico Serenidad",
        "schema_name": "serenidad_sucre",
        "dominio": "serenidad.localhost",
        "ciudad": "Sucre",
        "direccion": "Calle Calvo #124, Centro Histórico",
        "telefono": "+591 4 6451234",
        "email": "atencion@serenidadsucre.bo",
        "plan": "BASIC",
        "activo": True
    },
    {
        "slug": "vinculos_familiares",
        "nombre": "Centro Terapéutico Vínculos",
        "schema_name": "vinculos_familiares",
        "dominio": "vinculos.localhost",
        "ciudad": "Tarija",
        "direccion": "Calle Madrid #345, Barrio El Molino",
        "telefono": "+591 4 6649870",
        "email": "info@vinculosfamiliares.bo",
        "plan": "PRO",
        "activo": True
    },
    {
        "slug": "crecer_infantil",
        "nombre": "Gabinete Infanto-Juvenil Crecer",
        "schema_name": "crecer_infantil",
        "dominio": "crecer.localhost",
        "ciudad": "Santa Cruz",
        "direccion": "Av. Cristo Redentor #1400, 3er Anillo",
        "telefono": "+591 3 3421122",
        "email": "contacto@crecerinfantil.bo",
        "plan": "PRO",
        "activo": True
    },
    {
        "slug": "bienestar_pleno",
        "nombre": "Centro de Psicología Clínica Bienestar Pleno",
        "schema_name": "bienestar_pleno",
        "dominio": "bienestar.localhost",
        "ciudad": "La Paz",
        "direccion": "Calle Montenegro #880, San Miguel",
        "telefono": "+591 2 2794321",
        "email": "info@bienestarpleno.bo",
        "plan": "ENTERPRISE",
        "activo": True
    },
    {
        "slug": "armonia_cochabamba",
        "nombre": "Consultorios Psicológicos Armonía",
        "schema_name": "armonia_cochabamba",
        "dominio": "armonia.localhost",
        "ciudad": "Cochabamba",
        "direccion": "Av. Ballivián (El Prado) #720",
        "telefono": "+591 4 4256677",
        "email": "citas@armoniacocha.bo",
        "plan": "BASIC",
        "activo": True
    },
    {
        "slug": "resiliencia_oruro",
        "nombre": "Centro Integral de Salud Mental Resiliencia",
        "schema_name": "resiliencia_oruro",
        "dominio": "resiliencia.localhost",
        "ciudad": "Oruro",
        "direccion": "Calle Bolívar #450, Centro",
        "telefono": "+591 2 5253344",
        "email": "info@resilienciaoruro.bo",
        "plan": "BASIC",
        "activo": True
    },
    {
        "slug": "vida_salud",
        "nombre": "Centro Psicoterapéutico Vida & Salud",
        "schema_name": "vida_salud",
        "dominio": "vidasalud.localhost",
        "ciudad": "Potosí",
        "direccion": "Calle Hoyos #88, Plaza Principal",
        "telefono": "+591 2 6224455",
        "email": "contacto@vidasaludpotosi.bo",
        "plan": "BASIC",
        "activo": True
    },
    {
        "slug": "oasis_emocional",
        "nombre": "Consultorios Terapéuticos Oasis",
        "schema_name": "oasis_emocional",
        "dominio": "oasis.localhost",
        "ciudad": "Trinidad",
        "direccion": "Av. Cipriano Barace #210",
        "telefono": "+591 3 4629988",
        "email": "info@oasisemocional.bo",
        "plan": "BASIC",
        "activo": True
    }
]

class Command(BaseCommand):
    help = "Crea el catálogo exhaustivo de 12 Centros Psicológicos (Tenants) SaaS para la Defensa Docente (Criterio 8)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--populate-history',
            action='store_true',
            help='Ejecuta la siembra de datos clínicos e históricos (Sprint 1 y Sprint 2) en todos los centros creados.'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("\n========================================================================="))
        self.stdout.write(self.style.NOTICE("==> PROVISIONANDO CATÁLOGO MULTI-TENANT DE 12 CENTROS PSICOLÓGICOS (SAAS)"))
        self.stdout.write(self.style.NOTICE("=========================================================================\n"))

        with schema_context(get_public_schema_name()):
            from accounts.utils import seed_tenant_roles_and_permissions

            created_count = 0
            for item in CENTROS_SAAS_CATALOGO:
                t, created = Tenant.objects.get_or_create(
                    slug=item["slug"],
                    defaults={
                        "nombre": item["nombre"],
                        "schema_name": item["schema_name"],
                        "direccion": item["direccion"],
                        "telefono": item["telefono"],
                        "email_contacto": item["email"],
                        "plan": item["plan"],
                        "activo": item["activo"]
                    }
                )

                Dominio.objects.get_or_create(
                    domain=item["dominio"],
                    tenant=t,
                    defaults={"is_primary": True}
                )

                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"[OK] Creado nuevo Tenant: {item['nombre']} [{item['slug']}] -> Dominio: {item['dominio']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"[EXISTE] Tenant ya existente: {item['nombre']} [{item['slug']}]"))

                # Inicializar configuración del centro y usuarios demo en su esquema
                with schema_context(t.schema_name):
                    roles_map = seed_tenant_roles_and_permissions()
                    Centro.objects.get_or_create(
                        defaults={
                            "nombre": item["nombre"],
                            "direccion": item["direccion"],
                            "telefono": item["telefono"],
                            "email": item["email"],
                            "horarios_atencion": {
                                "lunes_viernes": "08:00 - 19:00",
                                "sabado": "08:00 - 13:00"
                            },
                            "configuracion": {
                                "cancelacion_horas_anticipacion": 24,
                                "duracion_sesion_minutos": 50,
                                "modalidad_predeterminada": "Mixta (Presencial / Telepsicología)"
                            }
                        }
                    )

                    clean_slug = item["slug"].replace("_", "")
                    demo_users = [
                        (f"admin@{clean_slug}.com", "Admin1234*", "Admin", f"{item['nombre']}", Rol.ADMIN_CENTRO, item["telefono"]),
                        (f"psicologo@{clean_slug}.com", "Psico1234*", "Lic. Principal", "Clínico", Rol.PSICOLOGO, "+591 71000000"),
                        (f"recepcion@{clean_slug}.com", "Recep1234*", "Recepción", "Admisión", Rol.RECEPCIONISTA, "+591 72000000"),
                        (f"coordinador@{clean_slug}.com", "Coord1234*", "Dr. Coordinador", "Médico", Rol.COORDINADOR, "+591 73000000"),
                    ]

                    for email, pwd, nom, ape, r_nom, tel in demo_users:
                        u, u_created = Usuario.objects.get_or_create(
                            email=email,
                            defaults={
                                "nombre": nom,
                                "apellido": ape,
                                "telefono": tel,
                                "rol": roles_map[r_nom],
                                "activo": True
                            }
                        )
                        if u_created:
                            u.set_password(pwd)
                            u.save()

        self.stdout.write(self.style.SUCCESS(f"\n[FINALIZADO] Catálogo SaaS de 12 Centros Psicológicos listo para la Defensa."))
        self.stdout.write(self.style.NOTICE("Cada centro cuenta con esquema PostgreSQL aislado, dominio y credenciales demo.\n"))
