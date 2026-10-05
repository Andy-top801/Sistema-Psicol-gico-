import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
os.environ.pop("DJANGO_SETTINGS_MODULE", None)

from django.conf import settings
if not settings.configured:
    settings.configure(
        SECRET_KEY="isolated-tests-only", USE_TZ=True, DEFAULT_CHARSET="utf-8",
        INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes", "rest_framework", "django_tenants", "tenants", "accounts", "clinica", "agenda", "audit"],
        DATABASES={"default": {"ENGINE": "django.db.backends.dummy"}},
        REST_FRAMEWORK={"UNAUTHENTICATED_USER": None}, AUTH_USER_MODEL="accounts.Usuario",
        TENANT_MODEL="tenants.Tenant", TENANT_DOMAIN_MODEL="tenants.Dominio",
        TENANT_APPS=["clinica", "agenda"], SHARED_APPS=["django_tenants", "tenants", "django.contrib.auth", "django.contrib.contenttypes", "accounts", "audit"],
        DATABASE_ROUTERS=["django_tenants.routers.TenantSyncRouter"],
    )
    import django
    django.setup()

from django.test import SimpleTestCase
from clinica.permissions import IsReferralParticipant
from clinica.serializers import DerivacionCasoSerializer
from clinica.models import DerivacionCaso, HistoriaClinica, Paciente, Psicologo
from accounts.models import Usuario


class ReferralCommonBaseTests(SimpleTestCase):
    databases = []

    def test_emitter_is_server_managed(self):
        self.assertIn("psicologo_emisor", DerivacionCasoSerializer.Meta.read_only_fields)

    def test_mutations_require_authenticated_psychologist_profile(self):
        permission = IsReferralParticipant()
        view = SimpleNamespace(action="create")
        psychologist = SimpleNamespace(is_authenticated=True, is_superuser=False, rol=SimpleNamespace(nombre="Psicólogo"), perfil_psicologo=object())
        patient = SimpleNamespace(is_authenticated=True, is_superuser=False, rol=SimpleNamespace(nombre="Paciente"), perfil_psicologo=None)
        admin = SimpleNamespace(is_authenticated=True, is_superuser=False, rol=SimpleNamespace(nombre="Administrador"), perfil_psicologo=None)
        no_profile = SimpleNamespace(is_authenticated=True, is_superuser=False, rol=SimpleNamespace(nombre="Psicólogo"), perfil_psicologo=None)
        self.assertTrue(permission.has_permission(SimpleNamespace(user=psychologist), view))
        self.assertFalse(permission.has_permission(SimpleNamespace(user=patient), view))
        self.assertFalse(permission.has_permission(SimpleNamespace(user=admin), view))
        self.assertFalse(permission.has_permission(SimpleNamespace(user=no_profile), view))

    def test_reads_do_not_grant_unauthenticated_access(self):
        permission = IsReferralParticipant()
        view = SimpleNamespace(action="list")
        anonymous = SimpleNamespace(is_authenticated=False, is_superuser=False, rol=None)
        self.assertFalse(permission.has_permission(SimpleNamespace(user=anonymous), view))

    def test_null_role_fails_closed_for_every_referral_action(self):
        permission = IsReferralParticipant()
        user = SimpleNamespace(is_authenticated=True, is_superuser=False, rol=None)
        for action in ('list', 'create', 'retrieve', 'partial_update'):
            self.assertFalse(permission.has_permission(SimpleNamespace(user=user), SimpleNamespace(action=action)))

    def test_unrelated_psychologist_is_denied_without_using_emitter_as_link(self):
        history = SimpleNamespace(
            paciente=SimpleNamespace(citas=SimpleNamespace(filter=lambda **kwargs: SimpleNamespace(exists=lambda: False))),
            psicologo_apertura=object(),
        )
        referral = SimpleNamespace(historia_clinica=history, psicologo_emisor=object(), id='ref-1')
        user = SimpleNamespace(is_authenticated=True, is_superuser=False, email='x@test.invalid', rol=SimpleNamespace(nombre='Psicólogo'), perfil_psicologo=object())
        with patch('clinica.permissions.write_event') as audit:
            self.assertFalse(IsReferralParticipant().has_object_permission(SimpleNamespace(user=user), SimpleNamespace(action='retrieve'), referral))
            audit.assert_called_once()

    def test_opening_psychologist_is_linked_without_appointments(self):
        patient = SimpleNamespace(citas=SimpleNamespace(filter=lambda **kwargs: SimpleNamespace(exists=lambda: False)))
        psico = object()
        history = SimpleNamespace(paciente=patient, psicologo_apertura=psico)
        referral = SimpleNamespace(historia_clinica=history, psicologo_emisor=object(), tipo_derivacion='CIERRE_ALTA')
        user = SimpleNamespace(is_authenticated=True, is_superuser=False, rol=SimpleNamespace(nombre='Psicólogo'), perfil_psicologo=psico)
        self.assertTrue(IsReferralParticipant().has_object_permission(SimpleNamespace(user=user), SimpleNamespace(action='retrieve'), referral))

    def test_history_and_type_are_immutable_and_alias_is_frontend_compatible(self):
        first = HistoriaClinica(paciente=Paciente(usuario=Usuario()), codigo_historia='HC-1')
        other = HistoriaClinica(paciente=Paciente(usuario=Usuario()), codigo_historia='HC-2')
        instance = DerivacionCaso(historia_clinica=first, psicologo_emisor=Psicologo(usuario=Usuario()), tipo_derivacion='EXTERNA_PSIQUIATRIA')
        serializer = DerivacionCasoSerializer(instance=instance)
        with self.assertRaises(Exception):
            serializer.validate({'historia_clinica': other})
        with self.assertRaises(Exception):
            serializer.validate({'tipo_derivacion': 'CIERRE_ALTA'})
        self.assertEqual(serializer.to_representation(instance)['tipo_cierre'], 'DERIVACION_PSIQUIATRIA')
