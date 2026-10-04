import hmac

from django.conf import settings
from rest_framework.permissions import BasePermission

from accounts.permissions import EsSuperAdmin


class AuditDeveloperPermission(BasePermission):
    """Require SuperAdmin and a separately configured developer key for audit data."""

    message = "Acceso denegado a la bitácora."

    def has_permission(self, request, view):
        if not EsSuperAdmin().has_permission(request, view):
            return False

        expected = getattr(settings, "AUDIT_DEVELOPER_KEY", "")
        encryption_key = getattr(settings, "AUDIT_LOG_KEY", "")
        supplied = request.headers.get("X-Developer-Key", "")
        if not isinstance(expected, str) or not isinstance(supplied, str):
            return False
        if not expected or not supplied or expected == encryption_key:
            return False
        try:
            supplied_bytes = supplied.encode("utf-8")
            expected_bytes = expected.encode("utf-8")
        except UnicodeEncodeError:
            return False
        return hmac.compare_digest(supplied_bytes, expected_bytes)
