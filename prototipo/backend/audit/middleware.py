import logging

from .services import write_event


logger = logging.getLogger(__name__)


class AuditLogMiddleware:
    """Registra cada solicitud HTTP sin persistir eventos en la base de datos."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = None
        error = None
        try:
            response = self.get_response(request)
            return response
        except Exception as exc:
            error = exc
            raise
        finally:
            try:
                user = getattr(request, "user", None)
                tenant = getattr(request, "tenant", None)
                write_event(
                    {
                        "ip": self._client_ip(request),
                        "user_id": str(user.id) if getattr(user, "is_authenticated", False) else None,
                        "user": getattr(user, "email", None) if getattr(user, "is_authenticated", False) else "anonymous",
                        "tenant": getattr(tenant, "schema_name", None),
                        "method": request.method,
                        "path": request.path,
                        "action": f"{request.method} {request.path}",
                        "status_code": response.status_code if response else 500,
                        "error": error.__class__.__name__ if error else None,
                    }
                )
            except Exception:
                # A logging failure must not change the response or hide the original error.
                logger.exception("No se pudo escribir la bitacora cifrada")

    @staticmethod
    def _client_ip(request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
