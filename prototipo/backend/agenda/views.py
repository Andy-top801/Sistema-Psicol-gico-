# ==============================================================================
# MÓDULO: agenda/views.py
# CAPA BCE: CONTROL (Controller) — CTR_CitaService, CTR_Teleconsulta,
#           CTR_Dashboard, CTR_AlertaService
# CASOS DE USO: CU11 (Gestión de Citas), CU13 (Teleconsulta Jitsi Meet),
#               CU9 (Dashboard KPIs), CU10 (Alertas de Priorización)
# DESCRIPCIÓN: Endpoints REST que reciben las peticiones de la capa Boundary
#              (IU_AgendaCitas, IU_Teleconsulta, IU_DashboardClinico, IU_AlertasClinicas)
#              y coordinan la lógica de negocio con la capa Entity y los Services.
#              Implementan los pasos 2→7 de los Diagramas de Comunicación BCE.
# ==============================================================================
from datetime import datetime, date
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from clinica.models import Psicologo, Paciente
from agenda.models import Cita, Teleconsulta, Alerta
from agenda.serializers import (
    CitaSerializer,
    CancelarCitaSerializer,
    TeleconsultaSerializer,
    TeleconsultaFinishSerializer,
    AlertaSerializer
)
from agenda.services.availability import AvailabilityValidator
from agenda.services.jitsi import JitsiTokenGenerator
from agenda.services.dashboard import MetricsAggregator
from agenda.services.alerts import AlertService

# ──────────────────────────────────────────────────────────────────────────────
# CONTROLADOR: CitaViewSet — CTR_CitaService
# DIAGRAMA DE COMUNICACIÓN CU11 – Programación, Reserva y Gestión de Citas:
#   Paso 2: IU_AgendaCitas → CTR: POST /api/agenda/citas/ {fecha, hora, modalidad}
#   Pasos 3–6: CitaSerializer delega a ConflictResolutionService (SELECT FOR UPDATE)
#   Paso 7: CTR → IU: 201 Created {cita_id, estado: 'PROGRAMADA'}
# ──────────────────────────────────────────────────────────────────────────────
class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.select_related('paciente__usuario', 'psicologo__usuario', 'teleconsulta').all()
    serializer_class = CitaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        rol_nombre = user.rol.nombre if user.rol else ""

        # Filtrado RBAC automático
        if rol_nombre == "Paciente" and not user.is_superuser:
            qs = qs.filter(paciente__usuario=user)
        elif rol_nombre in ["Psicólogo", "Psicologo / Terapeuta"] and not user.is_superuser:
            qs = qs.filter(psicologo__usuario=user)

        # Filtros por parámetros URL
        psico_id = self.request.query_params.get('psicologo') or self.request.query_params.get('psicologo_id')
        if psico_id:
            qs = qs.filter(psicologo_id=psico_id)

        paciente_id = self.request.query_params.get('paciente') or self.request.query_params.get('paciente_id')
        if paciente_id:
            qs = qs.filter(paciente_id=paciente_id)

        fecha = self.request.query_params.get('fecha')
        if fecha:
            qs = qs.filter(fecha=fecha)

        fecha_inicio = self.request.query_params.get('fecha_inicio') or self.request.query_params.get('start')
        if fecha_inicio:
            # Si incluye timestamp (FullCalendar), cortar solo fecha
            f_ini = fecha_inicio.split('T')[0]
            qs = qs.filter(fecha__gte=f_ini)

        fecha_fin = self.request.query_params.get('fecha_fin') or self.request.query_params.get('end')
        if fecha_fin:
            f_fin = fecha_fin.split('T')[0]
            qs = qs.filter(fecha__lte=f_fin)

        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado.upper())

        modalidad = self.request.query_params.get('modalidad')
        if modalidad:
            qs = qs.filter(modalidad=modalidad.upper())

        return qs.order_by('fecha', 'hora_inicio')

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    # ================================================================
    # HU-17: Cancelación de citas con validación de anticipación
    # DIAGRAMA DE COMUNICACIÓN CU11 (variante cancelación):
    #   Paso 2: IU → CTR: POST /api/agenda/citas/{id}/cancelar/
    #   Paso 3: CancelarCitaSerializer valida motivo y anticipación (2h mínimo)
    #   Paso 5: estado = 'CANCELADA', cupo liberado en agenda
    #   Paso 7: CTR → IU: 200 OK con confirmación
    # ================================================================
    @action(detail=True, methods=['post'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        """Cancela la cita validando anticipación y registrando el motivo."""
        cita = self.get_object()
        serializer = CancelarCitaSerializer(data=request.data, context={'cita': cita, 'request': request})
        serializer.is_valid(raise_exception=True)

        motivo = serializer.validated_data['motivo']
        cita.estado = 'CANCELADA'
        cita.motivo_cancelacion = motivo
        cita.save(update_fields=['estado', 'motivo_cancelacion', 'fecha_modificacion'])

        return Response({
            "mensaje": "La cita fue cancelada exitosamente.",
            "cita": CitaSerializer(cita).data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='slots-disponibles')
    def slots_disponibles(self, request):
        """
        Retorna la matriz de slots libres para un psicólogo en una fecha dada (HU-15, HU-16).
        GET /api/agenda/citas/slots-disponibles/?psicologo_id=...&fecha=YYYY-MM-DD
        """
        psico_id = request.query_params.get('psicologo_id') or request.query_params.get('psicologo')
        fecha_str = request.query_params.get('fecha')


        if not psico_id or not fecha_str:
            return Response(
                {"error": "Los parámetros 'psicologo_id' y 'fecha' (YYYY-MM-DD) son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            psicologo = Psicologo.objects.get(id=psico_id)
        except Psicologo.DoesNotExist:
            return Response({"error": "Psicólogo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        try:
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Formato de fecha inválido. Utilice YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        slots = AvailabilityValidator.obtener_slots_disponibles(psicologo, fecha_obj)
        return Response({
            "psicologo": f"{psicologo.usuario.nombre} {psicologo.usuario.apellido}",
            "fecha": fecha_str,
            "tarifa_base": float(psicologo.tarifa_base),
            "slots": slots
        })

    @action(detail=False, methods=['get'], url_path='calendario')
    def calendario(self, request):
        """
        Retorna eventos con formato nativo para FullCalendar (HU-22).
        """
        citas = self.get_queryset()
        colores_estado = {
            'PROGRAMADA': '#3B82F6',   # Azul
            'CONFIRMADA': '#10B981',   # Verde
            'REALIZADA': '#6B7280',    # Gris
            'CANCELADA': '#EF4444',    # Rojo
            'INASISTENCIA': '#F59E0B'  # Ámbar
        }

        eventos = []
        for c in citas:
            color = colores_estado.get(c.estado, '#3B82F6')
            start_str = f"{c.fecha.strftime('%Y-%m-%d')}T{c.hora_inicio.strftime('%H:%M:%S')}"
            end_str = f"{c.fecha.strftime('%Y-%m-%d')}T{c.hora_fin.strftime('%H:%M:%S')}"

            titulo = f"{c.paciente.usuario.nombre} ({c.modalidad[0]})"
            eventos.append({
                "id": str(c.id),
                "title": titulo,
                "start": start_str,
                "end": end_str,
                "backgroundColor": color,
                "borderColor": color,
                "textColor": "#ffffff",
                "extendedProps": {
                    "paciente": f"{c.paciente.usuario.nombre} {c.paciente.usuario.apellido}",
                    "psicologo": f"{c.psicologo.usuario.nombre} {c.psicologo.usuario.apellido}",
                    "estado": c.estado,
                    "modalidad": c.modalidad,
                    "costo": float(c.costo),
                    "motivo": c.motivo_consulta
                }
            })

        return Response(eventos)


# ──────────────────────────────────────────────────────────────────────────────
# CONTROLADOR: TeleconsultaAccessView — CTR_Teleconsulta
# DIAGRAMA DE COMUNICACIÓN CU13 – Teleconsultas y Videoconferencias Jitsi Meet:
#   Paso 2: IU_Teleconsulta → CTR: GET /api/agenda/teleconsulta/{id}/access/ + JWT
#   Pasos 3–6: JitsiTokenGenerator valida participante y genera sala + token JWT
#   Paso 7: CTR → IU: 200 OK {room_name, jwt_token, rol_moderador}
# ──────────────────────────────────────────────────────────────────────────────
class TeleconsultaAccessView(APIView):
    """
    GET /api/agenda/teleconsulta/{cita_id}/access/
    Entrega tokens WebRTC y credenciales para la sala Jitsi Meet (HU-18, HU-19).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, cita_id):
        try:
            cita = Cita.objects.select_related('psicologo__usuario', 'paciente__usuario').get(id=cita_id)
        except Cita.DoesNotExist:
            return Response({"error": "Cita no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if cita.modalidad != 'VIRTUAL':
            cita.modalidad = 'VIRTUAL'
            cita.save(update_fields=['modalidad'])

        if cita.estado in ['CANCELADA', 'REALIZADA']:
            return Response({
                "error": f"Esta sesión de teleconsulta ya ha concluido o fue cancelada (Estado: {cita.estado}).",
                "codigo": "SESSION_CLOSED"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            datos_acceso = JitsiTokenGenerator.generar_acceso(cita, request.user)
            # Marcar hora de inicio real si aún no se había registrado
            tele = cita.teleconsulta
            if not tele.hora_inicio_real:
                tele.hora_inicio_real = timezone.now()
                tele.save(update_fields=['hora_inicio_real'])

            return Response(datos_acceso, status=status.HTTP_200_OK)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)


class TeleconsultaFinishView(APIView):
    """
    POST /api/agenda/teleconsulta/{cita_id}/finish/
    Cierra la videollamada, guarda la duración real en segundos y marca la cita como 'REALIZADA' (HU-18).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, cita_id):
        try:
            cita = Cita.objects.select_related('teleconsulta', 'psicologo__usuario').get(id=cita_id)
        except Cita.DoesNotExist:
            return Response({"error": "Cita no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TeleconsultaFinishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        duracion = serializer.validated_data.get('duracion_segundos', 0)
        ahora = timezone.now()

        tele = getattr(cita, 'teleconsulta', None)
        if tele:
            tele.hora_fin_real = ahora
            if duracion > 0:
                tele.duracion_segundos = duracion
            elif tele.hora_inicio_real:
                delta = int((ahora - tele.hora_inicio_real).total_seconds())
                tele.duracion_segundos = max(0, delta)
            tele.save()

        cita.estado = 'REALIZADA'
        cita.save(update_fields=['estado', 'fecha_modificacion'])

        return Response({
            "mensaje": "Sesión de teleconsulta finalizada exitosamente.",
            "cita_id": str(cita.id),
            "estado": cita.estado,
            "duracion_segundos": tele.duracion_segundos if tele else duracion
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────────────────────
# CONTROLADOR: DashboardKPIsView — CTR_Dashboard
# DIAGRAMA DE COMUNICACIÓN CU9 – Consultar Dashboard e Indicadores Clínicos:
#   Paso 2: IU_DashboardClinico → CTR: GET /api/agenda/dashboard/kpis/?periodo=mes
#   Pasos 3–6: MetricsAggregator ejecuta consultas agregadas sobre agenda_cita
#   Paso 7: CTR → IU: 200 OK {total_citas, ausentismo, ocupacion}
# ──────────────────────────────────────────────────────────────────────────────
class DashboardKPIsView(APIView):
    """
    GET /api/agenda/dashboard/kpis/
    Métricas e indicadores analíticos en tiempo real para Coordinadores y Admins (HU-20).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        anio = request.query_params.get('anio')
        mes = request.query_params.get('mes')

        try:
            anio_int = int(anio) if anio else None
            mes_int = int(mes) if mes else None
        except ValueError:
            return Response({"error": "Año o mes con formato numérico inválido."}, status=status.HTTP_400_BAD_REQUEST)

        kpis = MetricsAggregator.obtener_kpis(anio_int, mes_int)
        return Response(kpis, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────────────────────
# CONTROLADOR: AlertaViewSet — CTR_AlertaService
# DIAGRAMA DE COMUNICACIÓN CU10 – Gestión de Alertas Tempranas y Priorización:
#   Paso 2: IU_AlertasClinicas → CTR: GET /api/agenda/alertas/?resuelta=false
#   Pasos 3–6: AlertService evalúa inasistencias y genera/lista alertas en CE
#   Paso 7: CTR → IU: 200 OK {alertas_activas, nivel_riesgo: ALTO}
# ──────────────────────────────────────────────────────────────────────────────
class AlertaViewSet(viewsets.ModelViewSet):
    queryset = Alerta.objects.select_related('paciente__usuario').all()
    serializer_class = AlertaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        resuelta = self.request.query_params.get('resuelta')
        if resuelta is not None:
            es_resuelta = resuelta.lower() in ('true', '1', 'yes')
            qs = qs.filter(resuelta=es_resuelta)

        tipo = self.request.query_params.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo.upper())

        return qs

    @action(detail=True, methods=['post'], url_path='resolver')
    def resolver(self, request, pk=None):
        """Marca una alerta clínica como resuelta y registra notas de seguimiento (HU-21)."""
        alerta = self.get_object()
        nota = request.data.get('nota_resolucion', 'Alerta atendida por equipo clínico.')

        alerta.resuelta = True
        alerta.fecha_resolucion = timezone.now()
        alerta.nota_resolucion = nota
        alerta.save(update_fields=['resuelta', 'fecha_resolucion', 'nota_resolucion'])

        return Response({
            "mensaje": "Alerta clínica resuelta correctamente.",
            "alerta": AlertaSerializer(alerta).data
        }, status=status.HTTP_200_OK)
