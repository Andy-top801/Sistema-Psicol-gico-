from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import EsSuperAdmin

from .serializers import AuditEventSerializer
from .services import parse_date, read_events


class AuditLogView(APIView):
    permission_classes = [EsSuperAdmin]

    def get(self, request):
        dev_key = request.headers.get("X-Developer-Key") or request.query_params.get("developer_key")
        expected_key = getattr(settings, "AUDIT_LOG_KEY", "")
        if dev_key and expected_key and dev_key != expected_key:
            return Response(
                {"error": "Llave de Desarrollador Inválida - Acceso Denegado a la Bitácora."},
                status=403,
            )

        try:
            events = read_events(parse_date(request.query_params.get("date")))
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        except Exception:
            return Response(
                {"error": "La bitacora no esta disponible o la llave es invalida."},
                status=503,
            )

        tenant = request.query_params.get("tenant")
        if tenant:
            events = [event for event in events if event.get("tenant") == tenant]
        return Response(AuditEventSerializer(events, many=True).data)
