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
        SECRET_KEY="isolated-tests-only",
        USE_TZ=True,
        DEFAULT_CHARSET="utf-8",
        INSTALLED_APPS=[
            "django.contrib.auth", "django.contrib.contenttypes", "rest_framework",
            "django_tenants", "tenants", "accounts", "clinica", "agenda",
            "audit", "reportes",
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.dummy"}},
        REST_FRAMEWORK={"UNAUTHENTICATED_USER": None},
        AUDIT_DEVELOPER_KEY="right-secret",
        AUDIT_LOG_KEY="different-encryption-secret",
        TENANT_MODEL="tenants.Tenant",
        TENANT_DOMAIN_MODEL="tenants.Dominio",
        TENANT_APPS=["clinica", "agenda"],
        SHARED_APPS=[
            "django_tenants", "tenants", "django.contrib.auth",
            "django.contrib.contenttypes", "accounts", "audit", "reportes",
        ],
        DATABASE_ROUTERS=["django_tenants.routers.TenantSyncRouter"],
        AUTH_USER_MODEL="accounts.Usuario",
    )
    import django
    django.setup()

from django.http import HttpResponse
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from audit.views import AuditLogView
from reportes import exporters, views as report_views


RESULT = {
    "total": 0,
    "registros": [],
    "columnas": [{"label": "Evento", "key": "evento"}],
    "datos": [],
}

HANDLERS = {
    "direct": (AuditLogView, "get", {}),
    "generic": (report_views.ReporteGenericoView, "get", {"fuente": "bitacora"}),
    "custom": (report_views.ReportePersonalizadoView, "post", {}),
    "csv": (report_views.ReporteExportCSVView, "get", {"fuente": "bitacora"}),
    "excel": (report_views.ReporteExportExcelView, "get", {"fuente": "bitacora"}),
    "html": (report_views.ReporteExportHTMLView, "get", {"fuente": "bitacora"}),
    "email": (report_views.ReporteEmailView, "post", {}),
}
EXPORTERS = (exporters.CSVExporter, exporters.ExcelExporter, exporters.HTMLExporter)


class AuditDeveloperKeyTests(SimpleTestCase):
    databases = []
    factory = APIRequestFactory()
    admin = SimpleNamespace(is_authenticated=True, is_superuser=True, rol=None)
    denied_user = SimpleNamespace(is_authenticated=True, is_superuser=False, rol=None)

    def dispatch(self, handler, *, key=None, query=None, user=None, source="bitacora"):
        cls, method, kwargs = HANDLERS[handler]
        if handler == "generic":
            kwargs = {"fuente": source}
        path = "/api/reportes/bitacora/"
        headers = {"HTTP_X_DEVELOPER_KEY": key} if key is not None else {}
        if method == "post":
            query_string = "?developer_key=" + query if query is not None else ""
            request = self.factory.post(
                path + query_string,
                {"fuente": source, "email": "test@example.invalid"},
                format="json",
                **headers,
            )
        else:
            query_string = "?developer_key=" + query if query is not None else ""
            request = self.factory.get(path + query_string, **headers)
        if user is not None:
            force_authenticate(request, user=user)
        return cls.as_view(authentication_classes=[])(request, **kwargs)

    def side_effect_patches(self):
        return (
            patch("audit.views.read_events", return_value=[]),
            patch.object(report_views.ReportEngine, "generar", return_value=RESULT),
            patch.object(exporters.CSVExporter, "generar", return_value=HttpResponse("csv")),
            patch.object(exporters.ExcelExporter, "generar", return_value=HttpResponse("xlsx")),
            patch.object(exporters.HTMLExporter, "generar", return_value="<html></html>"),
            patch("django.core.mail.EmailMultiAlternatives"),
        )

    def test_all_handlers_allow_authorized_superadmin_and_run_expected_effect(self):
        with self.side_effect_patches()[0] as read_events, self.side_effect_patches()[1] as generate, \
                self.side_effect_patches()[2] as csv_export, self.side_effect_patches()[3] as excel_export, \
                self.side_effect_patches()[4] as html_export, self.side_effect_patches()[5] as email_class:
            for name in HANDLERS:
                with self.subTest(handler=name):
                    response = self.dispatch(name, key="right-secret", user=self.admin)
                    self.assertLess(response.status_code, 400)
            self.assertEqual(read_events.call_count, 1)
            self.assertEqual(generate.call_count, 6)
            csv_export.assert_called_once()
            excel_export.assert_called_once()
            self.assertEqual(html_export.call_count, 2)
            email_class.return_value.send.assert_called_once_with(fail_silently=False)

    def test_all_handlers_deny_before_any_data_or_export_side_effect(self):
        with self.side_effect_patches()[0] as read_events, self.side_effect_patches()[1] as generate, \
                self.side_effect_patches()[2] as csv_export, self.side_effect_patches()[3] as excel_export, \
                self.side_effect_patches()[4] as html_export, self.side_effect_patches()[5] as email_class:
            attempts = (
                (None, None, self.admin), ("wrong", None, self.admin),
                (None, "right-secret", self.admin),
                ("right-secret", None, self.denied_user), ("right-secret", None, None),
            )
            for name in HANDLERS:
                for key, query, user in attempts:
                    with self.subTest(handler=name, key=key, query=query, user=user):
                        response = self.dispatch(name, key=key, query=query, user=user)
                        self.assertGreaterEqual(response.status_code, 400)
            read_events.assert_not_called()
            generate.assert_not_called()
            csv_export.assert_not_called()
            excel_export.assert_not_called()
            html_export.assert_not_called()
            email_class.assert_not_called()

    def test_all_handlers_fail_closed_when_developer_key_missing_or_reuses_encryption_key(self):
        for developer_key, encryption_key, headers in (
            ("", "encryption-secret", (None, "", "wrong-key")),
            ("shared-secret", "shared-secret", ("shared-secret",)),
        ):
            with self.subTest(developer_key=developer_key), \
                    self.settings(AUDIT_DEVELOPER_KEY=developer_key, AUDIT_LOG_KEY=encryption_key), \
                    patch("audit.views.read_events") as read_events, \
                    patch.object(report_views.ReportEngine, "generar") as generate, \
                    patch.object(exporters.CSVExporter, "generar") as csv_export, \
                    patch.object(exporters.ExcelExporter, "generar") as excel_export, \
                    patch.object(exporters.HTMLExporter, "generar") as html_export, \
                    patch("django.core.mail.EmailMultiAlternatives") as email_class:
                for name in HANDLERS:
                    for supplied in headers:
                        response = self.dispatch(name, key=supplied, user=self.admin)
                        self.assertEqual(response.status_code, 403)
                read_events.assert_not_called()
                generate.assert_not_called()
                csv_export.assert_not_called()
                excel_export.assert_not_called()
                html_export.assert_not_called()
                email_class.assert_not_called()

    def test_unicode_wrong_and_invalid_utf8_headers_are_denied_without_exception(self):
        for supplied in ("clé-incorrecte", "\ud800"):
            with self.subTest(supplied=repr(supplied)):
                response = self.dispatch("direct", key=supplied, user=self.admin)
                self.assertEqual(response.status_code, 403)

    def test_query_string_never_supplies_or_overrides_header(self):
        with patch("audit.views.read_events", return_value=[]):
            denied = self.dispatch("direct", key="wrong", query="right-secret", user=self.admin)
            allowed = self.dispatch("direct", key="right-secret", query="wrong", user=self.admin)
        self.assertEqual(denied.status_code, 403)
        self.assertLess(allowed.status_code, 400)

    def test_non_audit_report_does_not_require_developer_key(self):
        with patch.object(report_views.ReportEngine, "generar", return_value=RESULT) as generate:
            response = self.dispatch("generic", user=self.admin, source="citas")
        self.assertLess(response.status_code, 400)
        generate.assert_called_once()


if __name__ == "__main__":
    import unittest
    unittest.main()
