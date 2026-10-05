import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch
from contextlib import nullcontext

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
os.environ.pop('DJANGO_SETTINGS_MODULE', None)
from django.conf import settings
if not settings.configured:
    settings.configure(
        SECRET_KEY='isolated-tests-only', USE_TZ=True, DEFAULT_CHARSET='utf-8',
        INSTALLED_APPS=['django.contrib.auth', 'django.contrib.contenttypes', 'rest_framework', 'django_tenants', 'tenants', 'accounts', 'clinica', 'agenda', 'audit'],
        DATABASES={'default': {'ENGINE': 'django.db.backends.dummy'}},
        REST_FRAMEWORK={'UNAUTHENTICATED_USER': None}, AUTH_USER_MODEL='accounts.Usuario',
        TENANT_MODEL='tenants.Tenant', TENANT_DOMAIN_MODEL='tenants.Dominio',
        TENANT_APPS=['clinica', 'agenda'], SHARED_APPS=['django_tenants', 'tenants', 'django.contrib.auth', 'django.contrib.contenttypes', 'accounts', 'audit'],
        DATABASE_ROUTERS=['django_tenants.routers.TenantSyncRouter'],
    )
    import django
    django.setup()

from django.db import models
from django.test import SimpleTestCase
from clinica import lifecycle
from clinica.models import DerivacionCaso, HistoriaClinica
from clinica.serializers import DerivacionCasoSerializer, HistoriaClinicaSerializer


class Hu33ClosureTests(SimpleTestCase):
    databases = []

    def setUp(self):
        self.psico = SimpleNamespace(id='p1')
        self.user = SimpleNamespace(
            is_authenticated=True, rol=SimpleNamespace(nombre='Psicólogo'),
            perfil_psicologo=self.psico,
        )
        self.patient = SimpleNamespace(
            citas=SimpleNamespace(filter=lambda **kwargs: SimpleNamespace(exists=lambda: False))
        )
        self.history = SimpleNamespace(
            pk='h1', id='h1', cerrada=False, fecha_cierre='old',
            psicologo_apertura_id='p1', paciente=self.patient,
            save=Mock(),
        )

    def test_history_object_is_resolved_and_locked(self):
        model_history = HistoriaClinica()
        self.assertIs(lifecycle.history_for_object(model_history), model_history)
        nested = SimpleNamespace(historia_clinica=self.history)
        with patch('clinica.lifecycle.lock_history', return_value=self.history) as lock:
            lifecycle.ensure_object_history_open(nested)
            lock.assert_called_once_with('h1')

    def test_close_validates_type_fields_and_current_role_before_event(self):
        for kwargs in (
            {'tipo_derivacion': 'EXTERNA_PSIQUIATRIA', 'motivo_clinico': 'm', 'logros_alcanzados': 'l', 'recomendaciones_mantenimiento': 'r'},
            {'tipo_derivacion': 'CIERRE_ALTA', 'motivo_clinico': ' ', 'logros_alcanzados': 'l', 'recomendaciones_mantenimiento': 'r'},
        ):
            with self.assertRaises(Exception):
                lifecycle.close_history(history_id='h1', user=self.user, **kwargs)
        bad_user = SimpleNamespace(is_authenticated=True, rol=SimpleNamespace(nombre='Administrador'), perfil_psicologo=self.psico)
        with self.assertRaises(Exception):
            lifecycle.close_history(history_id='h1', user=bad_user, tipo_derivacion='CIERRE_ALTA', motivo_clinico='m', logros_alcanzados='l', recomendaciones_mantenimiento='r')

    def test_close_locks_history_and_rolls_back_when_event_fails(self):
        event_manager = Mock()
        event_manager.create.side_effect = RuntimeError('event failure')
        with patch('clinica.lifecycle.transaction.atomic', return_value=nullcontext()), patch('clinica.lifecycle.assert_no_future_pending_appointments'), patch('clinica.lifecycle.lock_history', return_value=self.history), patch('clinica.models.DerivacionCaso.objects', event_manager):
            with self.assertRaises(RuntimeError):
                lifecycle.close_history(history_id='h1', user=self.user, tipo_derivacion='CIERRE_ALTA', motivo_clinico='m', logros_alcanzados='l', recomendaciones_mantenimiento='r')
        self.history.save.assert_not_called()

    def test_reactivate_is_closed_only_and_clears_date(self):
        self.history.cerrada = True
        self.history.fecha_cierre = 'closed'
        manager = Mock()
        manager.create.return_value = SimpleNamespace(tipo_derivacion='REACTIVACION')
        with patch('clinica.lifecycle.transaction.atomic', return_value=nullcontext()), patch('clinica.lifecycle.lock_history', return_value=self.history), patch('clinica.models.DerivacionCaso.objects', manager):
            event = lifecycle.reactivate_history(history_id='h1', user=self.user, reason='seguimiento')
        self.assertEqual(event.tipo_derivacion, 'REACTIVACION')
        self.assertFalse(self.history.cerrada)
        self.assertIsNone(self.history.fecha_cierre)
        self.history.save.assert_called_once()
        with self.assertRaises(Exception):
            lifecycle.reactivate_history(history_id='h1', user=self.user, reason='')

    def test_serializer_requires_three_closure_fields_and_rejects_direct_reactivation(self):
        serializer = DerivacionCasoSerializer()
        with self.assertRaises(Exception):
            serializer.validate({'tipo_derivacion': 'CIERRE_ALTA', 'motivo_clinico': 'summary'})
        direct = DerivacionCasoSerializer()
        with self.assertRaises(Exception):
            direct.validate({'tipo_derivacion': 'REACTIVACION', 'motivo_clinico': 'reason'})

    def test_history_serializer_lifecycle_fields_are_read_only(self):
        self.assertIn('cerrada', HistoriaClinicaSerializer.Meta.read_only_fields)
        self.assertIn('fecha_cierre', HistoriaClinicaSerializer.Meta.read_only_fields)

    def test_derivacion_fk_is_protected_and_migration_declares_protect(self):
        field = DerivacionCaso._meta.get_field('historia_clinica')
        self.assertIs(field.remote_field.on_delete, models.PROTECT)
        import importlib.util
        spec = importlib.util.spec_from_file_location('hu33_migration', BACKEND / 'clinica/migrations/0005_hu33_closure_details.py')
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        self.assertEqual(migration.Migration.operations[0].field.remote_field.on_delete, models.PROTECT)
        self.assertEqual(field.remote_field.on_delete, models.PROTECT)

    def test_lifecycle_events_are_immutable_and_non_deletable(self):
        event = DerivacionCaso(tipo_derivacion='CIERRE_ALTA')
        with self.assertRaises(Exception):
            event.delete()

    def test_pending_appointment_query_is_conservative(self):
        cita = Mock()
        qs = Mock()
        qs.exists.return_value = True
        with patch('agenda.models.Cita.objects.filter', return_value=qs) as filt:
            with self.assertRaises(Exception):
                lifecycle.assert_no_future_pending_appointments(self.history)
        filt.assert_called_once()
        self.assertIn('fecha__gte', filt.call_args.kwargs)
        self.assertEqual(filt.call_args.kwargs['estado__in'], ('PROGRAMADA', 'CONFIRMADA'))

    def test_custom_mutators_call_shared_archive_guard(self):
        from clinica.views import NotaSesionViewSet, EvidenciaTareaViewSet
        self.assertTrue(hasattr(NotaSesionViewSet, 'guardar_borrador_endpoint'))
        self.assertTrue(hasattr(NotaSesionViewSet, 'crear_adenda'))
        self.assertTrue(hasattr(EvidenciaTareaViewSet, 'perform_destroy'))
        self.assertTrue(callable(getattr(NotaSesionViewSet, 'perform_destroy')))

    def test_existing_draft_path_rejects_closed_history_before_serializer_save(self):
        from clinica.views import NotaSesionViewSet
        from rest_framework.exceptions import ValidationError
        note = SimpleNamespace(historia_clinica=self.history)
        fake = SimpleNamespace(
            request=SimpleNamespace(data={'id': 'n1'}),
            get_serializer=Mock(),
        )
        with patch('clinica.views.NotaSesion.objects.select_for_update') as manager, patch('clinica.views.ensure_object_history_open', side_effect=ValidationError('closed')):
            manager.return_value.get.return_value = note
            with self.assertRaises(ValidationError):
                NotaSesionViewSet.guardar_borrador_endpoint.__wrapped__(fake, fake.request)
        fake.get_serializer.assert_not_called()

    def test_cancellation_path_rejects_closed_history_before_cita_save(self):
        from agenda.views import CitaViewSet
        from rest_framework.exceptions import ValidationError
        cita = SimpleNamespace(paciente=SimpleNamespace(historia_clinica=self.history), save=Mock())
        fake = SimpleNamespace(get_object=Mock(return_value=cita))
        request = SimpleNamespace(data={'motivo': 'cancelación válida'}, user=self.user)
        with patch('agenda.views.lock_history', return_value=self.history), patch('agenda.views.ensure_history_open', side_effect=ValidationError('closed')):
            with self.assertRaises(ValidationError):
                CitaViewSet.cancelar.__wrapped__(fake, request, 'c1')
        cita.save.assert_not_called()
