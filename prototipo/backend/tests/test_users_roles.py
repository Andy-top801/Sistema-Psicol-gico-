from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework import status
from accounts.models import Usuario, Rol, Permiso, RolPermiso

class UsersRolesTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.client = TenantClient(self.tenant)

        # Crear rol Admin Centro con permiso
        self.permiso_users = Permiso.objects.create(
            nombre="Gestionar Usuarios",
            codigo="gestionar_usuarios",
            modulo="Usuarios"
        )
        self.rol_admin = Rol.objects.create(nombre=Rol.ADMIN_CENTRO, descripcion="Admin")
        RolPermiso.objects.create(rol=self.rol_admin, permiso=self.permiso_users)

        self.rol_psicologo = Rol.objects.create(nombre=Rol.PSICOLOGO, descripcion="Psicólogo Clínico")

        # Admin user
        self.admin_user = Usuario.objects.create_user(
            email="admin_tenant@test.com",
            password="Admin1234*",
            nombre="Admin",
            rol=self.rol_admin
        )

        login_res = self.client.post('/api/auth/login/', {"email": "admin_tenant@test.com", "password": "Admin1234*"}, content_type='application/json')
        self.access_token = login_res.data['access']
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}

    def test_tp10_crear_usuario_dentro_del_centro(self):
        """TP-10: Registrar usuario dentro del centro"""
        data = {
            "email": "psico_nuevo@test.com",
            "password": "Password123*",
            "nombre": "Lic. Pedro",
            "apellido": "Vargas",
            "rol_id": self.rol_psicologo.id
        }
        res = self.client.post('/api/users/', data, content_type='application/json', **self.auth_headers)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Usuario.objects.filter(email="psico_nuevo@test.com").exists())

    def test_tp11_crear_usuario_correo_duplicado_en_centro(self):
        """TP-11: Registrar usuario con correo duplicado en el centro"""
        Usuario.objects.create_user(
            email="repetido@test.com",
            password="Password123*",
            nombre="Repetido",
            rol=self.rol_psicologo
        )
        data = {
            "email": "repetido@test.com",
            "password": "Password123*",
            "nombre": "Otro"
        }
        res = self.client.post('/api/users/', data, content_type='application/json', **self.auth_headers)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tp12_asignar_rol_a_usuario(self):
        """TP-12: Asignar rol a usuario y verificar permisos"""
        u = Usuario.objects.create_user(
            email="con_rol@test.com",
            password="Password123*",
            nombre="Con Rol",
            rol=self.rol_psicologo
        )
        self.assertEqual(u.rol.nombre, Rol.PSICOLOGO)

    def test_tp13_cambiar_rol_de_usuario(self):
        """TP-13: Cambiar rol de usuario"""
        u = Usuario.objects.create_user(
            email="cambio_rol@test.com",
            password="Password123*",
            nombre="Cambio",
            rol=self.rol_psicologo
        )
        res = self.client.patch(
            f'/api/users/{u.id}/',
            {"rol_id": self.rol_admin.id},
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        u.refresh_from_db()
        self.assertEqual(u.rol.id, self.rol_admin.id)
