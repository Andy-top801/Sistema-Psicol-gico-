from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.models import Centro
from core.serializers import CentroSerializer
from accounts.permissions import EsAdminCentro

class CentroConfigView(APIView):
    """
    GET /api/centro/config/
    PUT /api/centro/config/
    Permite al Administrador del Centro consultar y personalizar datos institucionales,
    horarios y políticas de atención de su centro.
    """
    permission_classes = [IsAuthenticated, EsAdminCentro]

    def get_object(self):
        centro = Centro.objects.first()
        if not centro:
            centro = Centro.objects.create(
                nombre="Centro Psicológico",
                direccion="Calle Principal #123",
                telefono="70000000",
                email="contacto@centro.com",
                horarios_atencion={"lunes_viernes": "08:00 - 18:00"},
                configuracion={"duracion_sesion_minutos": 50}
            )
        return centro

    def get(self, request):
        centro = self.get_object()
        serializer = CentroSerializer(centro)
        return Response(serializer.data)

    def put(self, request):
        centro = self.get_object()
        serializer = CentroSerializer(centro, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "mensaje": "Configuración institucional actualizada exitosamente.",
            "centro": serializer.data
        }, status=status.HTTP_200_OK)
