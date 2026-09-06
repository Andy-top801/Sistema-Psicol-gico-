from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework import status
from accounts.models import Usuario, Rol, TokenRecuperacion

class AutenticacionTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.client = TenantClient(self.tenant)

    def test_tp01_registro_superadmin_valido(self):
        """TP-01: Registrar SuperAdmin con datos válidos"""
        data = {
            "email": "nuevo_superadmin@sigepsi.com",
            "password": "Password123*",
            "nombre": "Admin",
            "apellido": "Principal"
        }
        response = self.client.post('/api/auth/register/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Usuario.objects.filter(email="nuevo_superadmin@sigepsi.com").exists())

    def test_tp02_registro_correo_duplicado(self):
        """TP-02: Registrar con correo duplicado"""
        Usuario.objects.create_user(
            email="duplicado@sigepsi.com",
            password="Password123*",
            nombre="User"
        )
        data = {
            "email": "duplicado@sigepsi.com",
            "password": "Password123*",
            "nombre": "User 2"
        }
        response = self.client.post('/api/auth/register/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tp03_registro_contrasena_debil(self):
        """TP-03: Registrar con contraseña débil (falla requisitos de seguridad)"""
        data = {
            "email": "debil@sigepsi.com",
            "password": "123",
            "nombre": "User"
        }
        response = self.client.post('/api/auth/register/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tp04_login_credenciales_correctas(self):
        """TP-04: Login con credenciales correctas -> genera JWT"""
        Usuario.objects.create_user(
            email="login_test@sigepsi.com",
            password="Password123*",
            nombre="Login User"
        )
        data = {
            "email": "login_test@sigepsi.com",
            "password": "Password123*"
        }
        response = self.client.post('/api/auth/login/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_tp05_login_credenciales_incorrectas(self):
        """TP-05: Login con credenciales incorrectas -> mensaje genérico"""
        data = {
            "email": "inexistente@sigepsi.com",
            "password": "WrongPassword123*"
        }
        response = self.client.post('/api/auth/login/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tp06_login_cuenta_suspendida(self):
        """TP-06: Login con cuenta desactivada"""
        Usuario.objects.create_user(
            email="suspendido@sigepsi.com",
            password="Password123*",
            nombre="Suspendido",
            activo=False
        )
        data = {
            "email": "suspendido@sigepsi.com",
            "password": "Password123*"
        }
        response = self.client.post('/api/auth/login/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tp21_logout_invalida_refresh_token(self):
        """TP-21: Cierre de sesión seguro con blacklist JWT"""
        Usuario.objects.create_user(
            email="logout_user@sigepsi.com",
            password="Password123*",
            nombre="Logout User"
        )
        login_res = self.client.post('/api/auth/login/', {"email": "logout_user@sigepsi.com", "password": "Password123*"}, content_type='application/json')
        access_token = login_res.data['access']
        refresh_token = login_res.data['refresh']

        logout_res = self.client.post(
            '/api/auth/logout/',
            {"refresh": refresh_token},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        self.assertEqual(logout_res.status_code, status.HTTP_200_OK)

    def test_tp23_solicitud_recuperacion_contrasena(self):
        """TP-23: Solicitar recuperación de contraseña"""
        Usuario.objects.create_user(
            email="recuperar@sigepsi.com",
            password="Password123*",
            nombre="Recuperar"
        )
        response = self.client.post('/api/auth/password-reset/', {"email": "recuperar@sigepsi.com"}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token_debug", response.data)

    def test_tp24_restablecer_contrasena_con_token(self):
        """TP-24: Restablecer contraseña con token válido"""
        user = Usuario.objects.create_user(
            email="reset_ok@sigepsi.com",
            password="OldPassword123*",
            nombre="Reset OK"
        )
        token_obj = TokenRecuperacion.generar_para_usuario(user)
        data = {
            "token": token_obj.token,
            "password": "NewPassword123*",
            "password_confirm": "NewPassword123*"
        }
        response = self.client.post('/api/auth/password-reset-confirm/', data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewPassword123*"))
