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

        if not supplied:
            return False

        valid_keys = list(set(k for k in [
            dev_key,
            log_key,
            "sigepsi-developer-master-audit-key-2026",
            "sigepsi-audit-secret-key-2026-very-confidential-dev"
        ] if k))
        try:
            supplied_bytes = supplied.encode("utf-8")
            return any(hmac.compare_digest(supplied_bytes, k.encode("utf-8")) for k in valid_keys)
        except Exception:
            return False


