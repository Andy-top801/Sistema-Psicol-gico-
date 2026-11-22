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
from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from clinica.models import Psicologo, Paciente
from clinica.lifecycle import ensure_history_open, lock_history
from agenda.models import Cita, Teleconsulta, Alerta
from agenda.serializers import (
    CitaSerializer,
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
        cita = self.get_object()
        history = getattr(cita.paciente, 'historia_clinica', None)
        if history:
            ensure_history_open(lock_history(history.pk))
        if request.data.get('paciente'):
            target = Paciente.objects.get(pk=request.data['paciente'])
            target_history = getattr(target, 'historia_clinica', None)
            if target_history:
                ensure_history_open(lock_history(target_history.pk))
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        cita = self.get_object()
        history = getattr(cita.paciente, 'historia_clinica', None)
        if history:
            ensure_history_open(lock_history(history.pk))
        return super().destroy(request, *args, **kwargs)

    # ================================================================
    # CU11 Móvil / HU-42: Cancelación con política > 24 h
    #   POST /api/v1/citas/{id}/cancelar/  (alias: /api/agenda/citas/{id}/cancelar/)
    #   Mensajes 2 → 16 / 18 del Diagrama de Secuencia → CTR_CitaMobileController
    #   El paciente solo puede cancelar SUS citas (get_object aplica el filtro RBAC).
    #   La política de 24 h aplica al Paciente; el personal del centro cancela sin ella.
    # ================================================================
    @action(detail=True, methods=['post'], url_path='cancelar')
    @transaction.atomic
    def cancelar(self, request, pk=None):
        from agenda.services.cita_mobile import CitaMobileController, CancelacionError
        cita = self.get_object()
        history = getattr(cita.paciente, 'historia_clinica', None)
        if history:
            ensure_history_open(lock_history(history.pk))
        es_paciente = bool(request.user.rol and request.user.rol.nombre == "Paciente") and not request.user.is_superuser
        ip = (request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
              or request.META.get('REMOTE_ADDR', 'unknown'))
        # CU11-paso 2: POST /api/v1/citas/{id}/cancelar/ (motivo) → CTR_CitaMovilController
        try:
            data = CitaMobileController.cancelar_cita(
                cita.id, request.data.get('motivo'), request.user, ip, aplicar_politica=es_paciente
            )
        except CancelacionError as e:
            # CU11-paso 18: HTTP 400 Bad Request {'Plazo expirado: cancelaciones requieren > 24h'} [retorno]
            return Response(e.body, status=e.status_code)
        # CU11-paso 16: HTTP 200 OK {'Cita cancelada y bloque liberado'} [retorno]
        data["cita"] = CitaSerializer(Cita.objects.get(id=cita.id)).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='completar')
    def completar(self, request, pk=None):
        """Concluye la cita marcándola como REALIZADA (Paso previo para HU-27 Nota SOAP)."""
        cita = self.get_object()
        cita.estado = 'REALIZADA'
        cita.save(update_fields=['estado', 'fecha_modificacion'])
        return Response({
            "mensaje": "Cita concluida exitosamente como REALIZADA. Ahora puede registrar la Nota SOAP.",
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

        # Si consulta un paciente, ocultar los horarios que chocan con sus propias citas
        # (misma regla que CitaConcurrencyService: no puede tener dos citas a la vez).
        paciente = Paciente.objects.filter(usuario=request.user).first()
        if paciente:
            ocupados = list(Cita.objects.filter(
                paciente=paciente, fecha=fecha_obj, estado__in=['PROGRAMADA', 'CONFIRMADA']
            ).values_list('hora_inicio', 'hora_fin'))
            slots = [s for s in slots if not any(
                str(ini) < str(s['hora_fin']) and str(fin) > str(s['hora_inicio']) for ini, fin in ocupados
            )]

        return Response({
            "psicologo": f"{psicologo.usuario.nombre} {psicologo.usuario.apellido}",
            "fecha": fecha_str,
            "tarifa_base": float(psicologo.tarifa_base),
            "slots": slots
        })

    @action(detail=False, methods=['get'], url_path='mis-citas')
    def mis_citas(self, request):
        """
        HU-41 / CU11 Móvil — listar_citas_paciente()
        GET /api/v1/citas/mis-citas/ → {'proximas': [...], 'historial': [...]} del paciente autenticado.
        """
        from agenda.services.cita_mobile import CitaMobileController
        paciente = Paciente.objects.filter(usuario=request.user).first()
        if not paciente:
            return Response({"error": "Solo los pacientes tienen agenda personal de citas."},
                            status=status.HTTP_403_FORBIDDEN)
        return Response(CitaMobileController.listar_citas_paciente(paciente), status=status.HTTP_200_OK)

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

    @transaction.atomic
    def get(self, request, cita_id):
        # CU13-paso 5: consultar_cita_virtual() → CE_Cita (trae también paciente y psicólogo para CU13-paso 7 y CU13-paso 9)
        try:
            cita = Cita.objects.select_for_update().select_related('psicologo__usuario', 'paciente__usuario').get(id=cita_id)
        except Cita.DoesNotExist:
            return Response({"error": "Cita no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        history = getattr(cita.paciente, 'historia_clinica', None)
        if history:
            ensure_history_open(lock_history(history.pk))
        if cita.modalidad != 'VIRTUAL':
            cita.modalidad = 'VIRTUAL'
            cita.save(update_fields=['modalidad'])

        # CU13-paso 6: cita_confirmada(hora, estado='CONFIRMADA') [retorno] — solo se acepta PROGRAMADA o CONFIRMADA
        if cita.estado not in ['PROGRAMADA', 'CONFIRMADA']:
            return Response({
                "error": f"Esta sesión de teleconsulta ya ha concluido o fue cancelada (Estado: {cita.estado}).",
                "codigo": "SESSION_CLOSED"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validar ventana de teleconsulta (10 min antes - 45 min después)
        from datetime import timedelta
        ahora = timezone.localtime()
        cita_dt = timezone.make_aware(
            datetime.combine(cita.fecha, cita.hora_inicio),
            timezone.get_current_timezone()
        )
        inicio_ventana = cita_dt - timedelta(minutes=10)
        fin_ventana = cita_dt + timedelta(minutes=45)

        es_admin = bool(request.user.rol and ('admin' in request.user.rol.nombre.lower() or 'coord' in request.user.rol.nombre.lower())) or request.user.is_superuser
        # CU13-paso 3: validar_ventana_acceso() — se calcula aquí en el CTR: 10 min antes a 45 min después (HU-44 a);
        #              el diagrama indica 15 min antes.
        # CU13-paso 4: resultado_ventana(en_ventana) [retorno]
        # else [en_ventana_acceso == false]
        # CU13-paso 21: HTTP 403 Forbidden {'Sala disponible solo ... antes de cita'} [retorno]
        if not es_admin and not (inicio_ventana <= ahora <= fin_ventana):
            return Response({
                "error": "La sala de teleconsulta solo está disponible desde 10 minutos antes y hasta 45 minutos después del horario programado.",
                "codigo": "OUTSIDE_TELECONSULTA_WINDOW"
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            # alt [en_ventana_acceso == true]
            # CU13-paso 7 a CU13-paso 12 y CU13-paso 15-16 ocurren en JitsiTokenGenerator.generar_acceso():
            #   datos del paciente y del psicólogo, iniciar_sala() y generar_token_jitsi_jwt()
            datos_acceso = JitsiTokenGenerator.generar_acceso(cita, request.user)
            # CU13-paso 13: registrar_entrada() → CE_Teleconsulta (hora de inicio real si aún no se había registrado)
            # CU13-paso 14: entrada_registrada() [retorno]
            tele = cita.teleconsulta
            if not tele.hora_inicio_real:
                tele.hora_inicio_real = timezone.now()
                tele.save(update_fields=['hora_inicio_real'])

            # CU13-paso 17: registrar_acceso(evento='INGRESO_SALA_TELECONSULTA', ip) → CE_AuditLog
            # CU13-paso 18: acceso_auditado() [retorno]
            from audit.services import AuditLog
            AuditLog.registrar_acceso(
                'INGRESO_SALA_TELECONSULTA',
                request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', 'unknown'),
                cita_id=str(cita.id), usuario=request.user.email, sala=datos_acceso.get('room_name'),
            )

            # CU13-paso 19: HTTP 200 OK {jitsi_jwt, room_name, server_url} [retorno]
            datos_acceso['jitsi_jwt'] = datos_acceso.get('jwt_token')
            datos_acceso['server_url'] = f"https://{datos_acceso.get('domain')}"
            return Response(datos_acceso, status=status.HTTP_200_OK)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    @transaction.atomic
    def post(self, request, cita_id):
        """CU13-paso 2: POST /api/v1/teleconsulta/{id}/unirse/ (dispositivo) → CTR_TeleconsultaController."""
        return self.get(request, cita_id)


class TeleconsultaFinishView(APIView):
    """
    POST /api/agenda/teleconsulta/{cita_id}/finish/
    Cierra la videollamada, guarda la duración real en segundos y marca la cita como 'REALIZADA' (HU-18).
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, cita_id):
        try:
            cita = Cita.objects.select_for_update(of=('self',)).select_related('teleconsulta', 'psicologo__usuario', 'paciente__usuario').get(id=cita_id)
        except Cita.DoesNotExist:
            return Response({"error": "Cita no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        history = getattr(cita.paciente, 'historia_clinica', None)
        if history:
            ensure_history_open(lock_history(history.pk))
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
            "sesion_concluida": True,
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


# ──────────────────────────────────────────────────────────────────────────────
# CONTROLADOR: FCMTokenEnrollView — CTR_FCMNotificationController (CU12 / HU-43)
# ──────────────────────────────────────────────────────────────────────────────
class FCMTokenEnrollView(APIView):
    """
    POST /api/agenda/fcm-token/
    Registra o actualiza el token FCM del dispositivo móvil para el paciente autenticado.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Criterio (a): al iniciar sesión, el token FCM se registra en comunicacion_tokenfcm."""
        token = (request.data.get('token') or '').strip()
        plataforma = (request.data.get('plataforma') or 'ANDROID').upper()

        if not token:
            return Response({"error": "El campo 'token' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        # Solo un paciente puede asociar dispositivos a SU propio expediente.
        paciente = Paciente.objects.filter(usuario=request.user).first()
        if not paciente:
            return Response(
                {"error": "Solo los pacientes pueden registrar dispositivos para recordatorios."},
                status=status.HTTP_403_FORBIDDEN
            )

        from clinica.models import TokenFCM
        plat_valida = plataforma if plataforma in ['ANDROID', 'IOS', 'WEB'] else 'ANDROID'
        token_obj, created = TokenFCM.objects.update_or_create(
            paciente=paciente,
            token=token,
            defaults={
                'plataforma': plat_valida,
                'activo': True
            }
        )

        return Response({
            "mensaje": "Token FCM registrado exitosamente.",
            "token_id": str(token_obj.id),
            "activo": token_obj.activo,
            "plataforma": token_obj.plataforma
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request):
        """Al cerrar sesión el dispositivo deja de recibir pushes de este paciente."""
        from clinica.models import TokenFCM
        token = (request.data.get('token') or request.query_params.get('token') or '').strip()
        n = TokenFCM.objects.filter(paciente__usuario=request.user, token=token, activo=True).update(activo=False)
        return Response({"desactivados": n}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────────────────────
# CU12 / HU-43: Centro de Notificaciones (IU_CentroNotificaciones web + móvil)
#   GET  /api/agenda/notificaciones/             → Paciente: sus avisos recibidos
#                                                  Personal: bitácora de despachos
#   POST /api/agenda/notificaciones/{id}/leer/   → marca como leída (Paciente)
#   POST /api/agenda/notificaciones/leer-todas/  → marca todas (Paciente)
#   POST /api/agenda/notificaciones/despachar/   → dispara CU12-paso 1 manualmente (Personal)
# ──────────────────────────────────────────────────────────────────────────────
from datetime import timedelta
from agenda.models import NotificacionCita
from agenda.serializers import NotificacionCitaSerializer
from agenda.services.notifications import FCMNotificationController


def _es_paciente(user):
    return bool(user.rol and user.rol.nombre == "Paciente") and not user.is_superuser


class NotificacionCitaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificacionCitaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = NotificacionCita.objects.select_related(
            'cita__paciente__usuario', 'cita__psicologo__usuario'
        )
        if _es_paciente(user):
            return qs.filter(cita__paciente__usuario=user, estado='ENVIADO').order_by('-fecha_envio')
        rol = user.rol.nombre if user.rol else ""
        if rol in ["Psicólogo", "Psicologo / Terapeuta"] and not user.is_superuser:
            qs = qs.filter(cita__psicologo__usuario=user)
        return qs.order_by('-fecha_programada')

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = NotificacionCitaSerializer(qs[:40], many=True).data
        if _es_paciente(request.user):
            resumen = {"no_leidas": qs.filter(leida=False).count()}
        else:
            hace_24h = timezone.now() - timedelta(hours=24)
            resumen = {
                "enviadas_24h": qs.filter(estado='ENVIADO', fecha_envio__gte=hace_24h).count(),
                "pendientes": qs.filter(estado='PENDIENTE').count(),
                "fallidas": qs.filter(estado='FALLIDO').count(),
            }
        return Response({"es_paciente": _es_paciente(request.user), "resumen": resumen, "resultados": data})

    @action(detail=True, methods=['post'], url_path='leer')
    def leer(self, request, pk=None):
        notif = self.get_object()
        if _es_paciente(request.user) and not notif.leida:
            notif.leida = True
            notif.save(update_fields=['leida'])
        return Response(NotificacionCitaSerializer(notif).data)

    @action(detail=False, methods=['post'], url_path='leer-todas')
    def leer_todas(self, request):
        n = self.get_queryset().filter(leida=False).update(leida=True) if _es_paciente(request.user) else 0
        return Response({"marcadas": n})

    @action(detail=False, methods=['post'], url_path='despachar')
    def despachar(self, request):
        """Ejecución manual del CU12-paso 1 (el Cron lo hace automáticamente)."""
        if _es_paciente(request.user):
            return Response({"error": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)
        return Response(FCMNotificationController.ejecutar_despacho_recordatorios())
