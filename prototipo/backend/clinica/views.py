from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from clinica.models import Especialidad, Psicologo, Disponibilidad, Paciente
from clinica.serializers import (
    EspecialidadSerializer,
    PsicologoSerializer,
    DisponibilidadSerializer,
    PacienteSerializer
)
from accounts.permissions import EsAdminCentro

class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all().order_by('nombre')
    serializer_class = EspecialidadSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


class PsicologoViewSet(viewsets.ModelViewSet):
    queryset = Psicologo.objects.select_related('usuario').prefetch_related('especialidades', 'disponibilidades').all()
    serializer_class = PsicologoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'disponibilidad']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        # Filtro de búsqueda textual
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(
                    usuario__nombre__icontains=search,
                    usuario__apellido__icontains=search,
                    usuario__email__icontains=search,
                    numero_colegiado__icontains=search,
                    _connector=Q.OR
                )
            )

        # Filtro por especialidad
        esp_id = self.request.query_params.get('especialidad')
        if esp_id:
            qs = qs.filter(especialidades__id=esp_id)

        # Filtro por modalidad
        modalidad = self.request.query_params.get('modalidad')
        if modalidad:
            qs = qs.filter(modalidad__iexact=modalidad)

        # Filtro por estado activo
        activo = self.request.query_params.get('activo')
        if activo is not None:
            es_activo = activo.lower() in ('true', '1', 'yes')
            qs = qs.filter(activo=es_activo)

        return qs.distinct()

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['get', 'post'], url_path='disponibilidad')
    def disponibilidad(self, request, pk=None):
        psicologo = self.get_object()

        if request.method == 'GET':
            disps = psicologo.disponibilidades.filter(activo=True).order_by('dia_semana', 'hora_inicio')
            serializer = DisponibilidadSerializer(disps, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            data = request.data
            if isinstance(data, dict) and 'franjas' in data:
                data = data['franjas']

            if isinstance(data, list):
                # Al guardar el horario semanal completo, reemplazar las franjas anteriores
                psicologo.disponibilidades.all().delete()
                creados = []
                for item in data:
                    item_copy = dict(item)
                    item_copy['psicologo'] = str(psicologo.id)
                    ser = DisponibilidadSerializer(data=item_copy)
                    ser.is_valid(raise_exception=True)
                    ser.save()
                    creados.append(ser.data)
                return Response({
                    "mensaje": f"{len(creados)} franja(s) horaria(s) configurada(s) exitosamente.",
                    "count": len(creados),
                    "horarios": creados,
                    "disponibilidades": creados
                }, status=status.HTTP_200_OK)
            else:
                data_dict = dict(data)
                data_dict['psicologo'] = str(psicologo.id)
                ser = DisponibilidadSerializer(data=data_dict)
                ser.is_valid(raise_exception=True)
                ser.save()
                return Response(ser.data, status=status.HTTP_201_CREATED)



class DisponibilidadViewSet(viewsets.ModelViewSet):
    queryset = Disponibilidad.objects.all()
    serializer_class = DisponibilidadSerializer
    permission_classes = [IsAuthenticated]


class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.select_related('usuario').all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Si es un paciente autenticado, sólo ve su propio perfil salvo que sea admin/recepcionista
        rol_nombre = user.rol.nombre if user.rol else ""
        if rol_nombre == "Paciente" and not user.is_superuser:
            return qs.filter(usuario=user)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(
                    usuario__nombre__icontains=search,
                    usuario__apellido__icontains=search,
                    usuario__email__icontains=search,
                    ci__icontains=search,
                    codigo_expediente__icontains=search,
                    _connector=Q.OR
                )
            )

        return qs

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Retorna el expediente del paciente autenticado."""
        try:
            paciente = Paciente.objects.select_related('usuario').get(usuario=request.user)
            serializer = self.get_serializer(paciente)
            return Response(serializer.data)
        except Paciente.DoesNotExist:
            return Response(
                {"error": "El usuario actual no cuenta con un expediente de paciente asignado."},
                status=status.HTTP_404_NOT_FOUND
            )
