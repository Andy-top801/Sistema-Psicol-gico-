from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django_tenants.utils import schema_context, get_public_schema_name
from rest_framework import status
from tenants.models import Tenant, Dominio
from accounts.models import Usuario, Rol
from core.models import Centro

class MultiTenantTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.client = TenantClient(self.tenant)

        # Crear SuperAdmin en schema public
        with schema_context(get_public_schema_name()):
            self.superadmin = Usuario.objects.create_superuser(
                email="super_mt@sigepsi.com",
                password="Admin1234*",
                nombre="SuperAdmin"
            )

    def test_tp07_crear_tenant_y_esquema_aislado(self):
        """TP-07: Alta de centro con esquema PostgreSQL aislado"""
        with schema_context(get_public_schema_name()):
            t = Tenant.objects.create(
                nombre="Centro Test Aislamiento",
                slug="centro_test_aislado",
                schema_name="centro_test_aislado",
                activo=True
            )
            Dominio.objects.create(domain="test_aislado.localhost", tenant=t, is_primary=True)

            self.assertTrue(Tenant.objects.filter(slug="centro_test_aislado").exists())

        # Verificar que se puede ingresar al nuevo esquema
        with schema_context("centro_test_aislado"):
            u = Usuario.objects.create_user(
                email="user_aislado@test.com",
                password="Password123*",
                nombre="Usuario Aislado"
            )
            self.assertTrue(Usuario.objects.filter(email="user_aislado@test.com").exists())

        # Verificar que NO existe en el tenant principal
        self.assertFalse(Usuario.objects.filter(email="user_aislado@test.com").exists())

    def test_tp09_editar_configuracion_centro(self):
        """TP-09: Editar configuración institucional del centro"""
        centro = Centro.objects.first()
        if not centro:
            centro = Centro.objects.create(
                nombre=self.tenant.nombre,
                direccion="Calle Inicial #100",
                telefono="71111111",
                email="test@centro.com"
            )

        rol_admin, _ = Rol.objects.get_or_create(nombre=Rol.ADMIN_CENTRO)
        admin_u = Usuario.objects.create_user(
            email="admin_cfg@test.com",
            password="Admin1234*",
            nombre="Admin Config",
            rol=rol_admin
        )

        login_res = self.client.post('/api/auth/login/', {"email": "admin_cfg@test.com", "password": "Admin1234*"}, content_type='application/json')
        access_token = login_res.data['access']

        res = self.client.put(
            '/api/centro/config/',
            {
                "nombre": "Nombre Actualizado",
                "direccion": "Nueva Dirección #200"
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        centro.refresh_from_db()
        self.assertEqual(centro.nombre, "Nombre Actualizado")

    def test_tp19_suspender_reactivar_centro(self):
        """TP-19: Suspender y reactivar centro psicológico"""
        with schema_context(get_public_schema_name()):
            t = Tenant.objects.create(
                nombre="Centro a Suspender",
                slug="centro_suspender",
                schema_name="centro_suspender",
                activo=True
            )
            t.suspender()
            self.assertFalse(t.activo)
            t.activar()
            self.assertTrue(t.activo)
