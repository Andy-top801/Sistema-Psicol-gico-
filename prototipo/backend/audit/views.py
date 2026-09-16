from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import EsSuperAdmin

from .serializers import AuditEventSerializer
from .services import parse_date, read_events


class AuditLogView(APIView):
    permission_classes = [EsSuperAdmin]

    def get(self, request):
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
