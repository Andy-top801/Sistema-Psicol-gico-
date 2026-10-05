import hmac

from django.conf import settings
from rest_framework.permissions import BasePermission

from accounts.permissions import EsSuperAdmin


class AuditDeveloperPermission(BasePermission):
    """Require SuperAdmin and a valid developer master key for audit data."""

    message = "Acceso denegado a la bitácora. Llave de Desarrollador inválida o no provista."

    def has_permission(self, request, view):
        if not EsSuperAdmin().has_permission(request, view):
            return False

        dev_key = (getattr(settings, "AUDIT_DEVELOPER_KEY", "") or "").strip()
        log_key = (getattr(settings, "AUDIT_LOG_KEY", "") or "").strip()
        supplied = request.headers.get("X-Developer-Key", "").strip()

        if not supplied or not dev_key or (log_key and dev_key == log_key):
            return False

        try:
            supplied_bytes = supplied.encode("utf-8")
            return hmac.compare_digest(supplied_bytes, dev_key.encode("utf-8"))
        except Exception:
            return False


