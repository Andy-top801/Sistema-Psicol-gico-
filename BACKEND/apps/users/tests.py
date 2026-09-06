import json

from django.core import mail
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from apps.tenants.models import Dominio
from apps.users.models import Usuario, Especialidad, Psicologo, DisponibilidadPsicologo
from apps.users.tokens import make_reset_code

REGISTER_URL = '/api/users/auth/register/'
LOGIN_URL = '/api/users/auth/login/'
ME_URL = '/api/users/me/'
PASSWORD_RESET_URL = '/api/users/auth/password-reset/'
PASSWORD_RESET_VERIFY_URL = '/api/users/auth/password-reset-verify/'
PASSWORD_RESET_CONFIRM_URL = '/api/users/auth/password-reset-confirm/'
PSICOLOGOS_URL = '/api/users/psicologos/'
ESPECIALIDADES_URL = '/api/users/especialidades/'
DISPONIBILIDADES_URL = '/api/users/disponibilidades-psicologo/'


class RegisterAndAuthTests(TenantTestCase):
    """Registro, autenticación e inicio de sesión (parte móvil, HU-02).

    Corre dentro de un schema de tenant aislado (TenantTestCase), como
    corresponde a que `apps.users` es un TENANT_APP: cada centro tiene su
    propia tabla de usuarios.
    """

    def setUp(self):
        super().setUp()
        Dominio.objects.get_or_create(
            tenant=self.tenant,
            defaults={'domain': f'{self.tenant.schema_name}.test.com', 'is_primary': True},
        )
        self.client = TenantClient(self.tenant)

    def _post(self, url, payload):
        return self.client.post(
            url, data=json.dumps(payload), content_type='application/json'
        )

    def _register_payload(self, **overrides):
        payload = {
            'email': 'paciente.nuevo@test.com',
            'password': 'ClaveSegura123@',
            'first_name': 'Nuevo',
            'last_name': 'Paciente',
            'phone': '999999999',
        }
        payload.update(overrides)
        return payload

    def test_register_assigns_paciente_role_and_returns_tokens(self):
        response = self._post(REGISTER_URL, self._register_payload())

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertIn('access', body)
        self.assertIn('refresh', body)
        self.assertEqual(body['user']['roles'], ['Paciente'])

        user = Usuario.objects.get(email='paciente.nuevo@test.com')
        self.assertTrue(user.roles.filter(name='Paciente').exists())

    def test_duplicate_email_returns_clean_400(self):
        self._post(REGISTER_URL, self._register_payload())
        response = self._post(REGISTER_URL, self._register_payload())

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json())

    def test_me_requires_authentication(self):
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, 401)

    def test_me_returns_correct_profile(self):
        register_response = self._post(REGISTER_URL, self._register_payload())
        access_token = register_response.json()['access']

        response = self.client.get(
            ME_URL, HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['email'], 'paciente.nuevo@test.com')
        self.assertEqual(body['first_name'], 'Nuevo')
        self.assertEqual(body['roles'], ['Paciente'])

    def test_full_register_login_me_chain(self):
        self._post(REGISTER_URL, self._register_payload(email='paciente.chain@test.com'))

        login_response = self._post(
            LOGIN_URL,
            {'email': 'paciente.chain@test.com', 'password': 'ClaveSegura123@'},
        )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()['access']

        me_response = self.client.get(
            ME_URL, HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json()['email'], 'paciente.chain@test.com')


class PasswordResetTests(TenantTestCase):
    """HU-10 / CU27 / RF-31: recuperación de contraseña por correo."""

    def setUp(self):
        super().setUp()
        Dominio.objects.get_or_create(
            tenant=self.tenant,
            defaults={'domain': f'{self.tenant.schema_name}.test.com', 'is_primary': True},
        )
        self.client = TenantClient(self.tenant)
        self.user = Usuario.objects.create_user(
            username='paciente@sanamente.com',
            email='paciente@sanamente.com',
            password='ClaveVieja123@',
            first_name='Ana',
        )

    def _post(self, url, payload):
        return self.client.post(
            url, data=json.dumps(payload), content_type='application/json'
        )

    def test_request_with_registered_email_sends_mail_with_code(self):
        response = self._post(PASSWORD_RESET_URL, {'email': 'paciente@sanamente.com'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('paciente@sanamente.com', mail.outbox[0].to)
        self.assertIn('código de verificación', mail.outbox[0].body.lower())

    def test_request_with_unknown_email_returns_generic_200_without_sending_mail(self):
        response = self._post(PASSWORD_RESET_URL, {'email': 'no.existe@test.com'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_verify_with_valid_code_returns_200_without_changing_password(self):
        code = make_reset_code(self.user)

        response = self._post(PASSWORD_RESET_VERIFY_URL, {'code': code})

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('ClaveVieja123@'))  # sin cambios

    def test_verify_with_invalid_code_returns_clean_400(self):
        response = self._post(PASSWORD_RESET_VERIFY_URL, {'code': 'codigo-invalido'})

        self.assertEqual(response.status_code, 400)
        self.assertIn('code', response.json())

    def test_verify_does_not_consume_the_code_confirm_still_works_after(self):
        code = make_reset_code(self.user)

        verify_response = self._post(PASSWORD_RESET_VERIFY_URL, {'code': code})
        self.assertEqual(verify_response.status_code, 200)

        confirm_response = self._post(
            PASSWORD_RESET_CONFIRM_URL,
            {'code': code, 'new_password': 'ClaveNueva456@'},
        )
        self.assertEqual(confirm_response.status_code, 200)

    def test_confirm_with_valid_code_updates_password(self):
        code = make_reset_code(self.user)

        response = self._post(
            PASSWORD_RESET_CONFIRM_URL,
            {'code': code, 'new_password': 'ClaveNueva456@'},
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('ClaveNueva456@'))

        login_response = self._post(
            LOGIN_URL,
            {'email': 'paciente@sanamente.com', 'password': 'ClaveNueva456@'},
        )
        self.assertEqual(login_response.status_code, 200)

    def test_confirm_with_invalid_code_returns_clean_400(self):
        response = self._post(
            PASSWORD_RESET_CONFIRM_URL,
            {'code': 'codigo-invalido', 'new_password': 'ClaveNueva456@'},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('code', response.json())

    def test_code_cannot_be_reused_after_password_already_changed(self):
        code = make_reset_code(self.user)
        self._post(PASSWORD_RESET_CONFIRM_URL, {'code': code, 'new_password': 'ClaveNueva456@'})

        reused_response = self._post(
            PASSWORD_RESET_CONFIRM_URL,
            {'code': code, 'new_password': 'OtraClave789@'},
        )

        self.assertEqual(reused_response.status_code, 400)


class PsicologoAdminTests(TenantTestCase):
    @classmethod
    def get_test_schema_name(cls):
        return 'users_psicologo_test'

    @classmethod
    def get_test_tenant_domain(cls):
        return 'users-psicologo.test.com'

    def setUp(self):
        super().setUp()
        Dominio.objects.get_or_create(
            tenant=self.tenant,
            defaults={'domain': f'{self.tenant.schema_name}.test.com', 'is_primary': True},
        )
        self.client = TenantClient(self.tenant)
        self.admin_user = Usuario.objects.create_superuser(
            username='admin@test.com',
            email='admin@test.com',
            password='Admin123@',
        )
        self.especialidad = Especialidad.objects.create(name='Terapia Cognitivo Conductual')

    def _post(self, url, payload, **extra):
        return self.client.post(
            url, data=json.dumps(payload), content_type='application/json', **extra
        )

    def _admin_token(self):
        response = self._post(LOGIN_URL, {'email': 'admin@test.com', 'password': 'Admin123@'})
        self.assertEqual(response.status_code, 200)
        return response.json()['access']

    def _create_psicologo(self):
        user = Usuario.objects.create_user(
            username='psicologo.base@test.com',
            email='psicologo.base@test.com',
            password='ClaveSegura123@',
        )
        psicologo = Psicologo.objects.create(usuario=user)
        return psicologo

    def test_admin_can_create_psicologo_with_role_and_specialty(self):
        response = self._post(
            PSICOLOGOS_URL,
            {
                'email': 'psicologo1@test.com',
                'password': 'ClaveSegura123@',
                'first_name': 'Carlos',
                'last_name': 'Lopez',
                'phone': '77777777',
                'modalidad_atencion': 'mixta',
                'especialidades': [str(self.especialidad.id)],
            },
            HTTP_AUTHORIZATION=f'Bearer {self._admin_token()}',
        )

        self.assertEqual(response.status_code, 201)
        psicologo = Psicologo.objects.get(usuario__email='psicologo1@test.com')
        self.assertTrue(psicologo.usuario.roles.filter(name='Psicólogo').exists())
        self.assertTrue(psicologo.especialidades.filter(pk=self.especialidad.pk).exists())

    def test_admin_can_create_especialidad(self):
        response = self._post(
            ESPECIALIDADES_URL,
            {'name': 'Psicoterapia Infantil', 'description': 'Atención a niños'},
            HTTP_AUTHORIZATION=f'Bearer {self._admin_token()}',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Especialidad.objects.filter(name='Psicoterapia Infantil').exists())

    def test_admin_can_create_disponibilidad(self):
        psicologo = self._create_psicologo()
        response = self._post(
            DISPONIBILIDADES_URL,
            {
                'psicologo': str(psicologo.id),
                'dia_semana': 1,
                'hora_inicio': '08:00:00',
                'hora_fin': '12:00:00',
                'activo': True,
            },
            HTTP_AUTHORIZATION=f'Bearer {self._admin_token()}',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(DisponibilidadPsicologo.objects.filter(psicologo=psicologo).exists())
