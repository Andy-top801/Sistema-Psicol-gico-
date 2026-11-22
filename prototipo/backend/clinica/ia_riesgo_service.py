# ==============================================================================
# MÓDULO: clinica/ia_riesgo_service.py
# CASOS DE USO: CU24 (HU-50 Detección longitudinal de señales de riesgo y deserción,
#                     HU-51 Consola web de alertas prioritarias e intervención)
# ==============================================================================
import re
from datetime import timedelta
from django.db import connection
from django.db.models import Case, IntegerField, Value, When
from django.utils import timezone

from agenda.models import Cita
from audit.services import log_event
from clinica.chatbot_service import ChatbotEngine
from clinica.models import (
    Paciente,
    NotaSesion,
    EvolucionClinica,
    RegistroAnimo,
    TareaTerapeutica,
    AlertaRiesgoIA,
)


PATRONES_RIESGO_VITAL = [re.compile(pat, re.IGNORECASE) for pat in ChatbotEngine.PALABRAS_CRISIS]


def _clasificar_severidad(score: int) -> str:
    if score >= 80:
        return 'CRITICO'
    if score >= 60:
        return 'ALTO'
    if score >= 35:
        return 'MEDIO'
    return 'BAJO'


class RiesgoLongitudinalService:
    """
    HU-50: Evalúa 4 señales combinadas sobre el historial longitudinal del paciente:
      1. Léxico de riesgo vital en notas SOAP, evoluciones o check-ins de ánimo.
      2. 3+ registros consecutivos de ánimo MUY_BAJO/BAJO (<= 2/5).
      3. 2+ INASISTENCIA consecutivas o > 21 días sin cita realizada/programada.
      4. Caída de adherencia en tareas terapéuticas (vencidas/no realizadas).
    Evita duplicados manteniendo actualizada la alerta abierta del mismo tipo.
    """

    @classmethod
    def evaluar_paciente(cls, paciente: Paciente) -> list[AlertaRiesgoIA]:
        hoy = timezone.localdate()
        factores_vital = []
        factores_abandono = []
        score_vital = 0
        score_abandono = 0

        # Señal 1: Léxico de riesgo vital en notas SOAP, evoluciones o check-ins recientes
        notas_rec = list(
            NotaSesion.objects.filter(historia_clinica__paciente=paciente)
            .order_by('-fecha_sesion')[:5]
        )
        textos_clinicos = []
        for n in notas_rec:
            textos_clinicos.append(f"{n.subjetivo} {n.objetivo} {n.analisis} {n.plan}")

        animo_rec = list(RegistroAnimo.objects.filter(paciente=paciente).order_by('-fecha_registro', '-creado_en')[:10])
        for a in animo_rec[:5]:
            if a.nota_reflexiva:
                textos_clinicos.append(a.nota_reflexiva)

        hits_lexico = set()
        for txt in textos_clinicos:
            for rx in PATRONES_RIESGO_VITAL:
                m = rx.search(txt or '')
                if m:
                    hits_lexico.add(m.group(0).lower())

        if hits_lexico:
            score_vital += 65
            factores_vital.append({
                'codigo': 'LEXICO_RIESGO_VITAL',
                'etiqueta': f"Léxico de riesgo vital ({', '.join(sorted(hits_lexico)[:3])})",
                'peso': 65,
            })

        # Evolución reciente en RETROCESO_CRISIS
        ult_ev = EvolucionClinica.objects.filter(historia_clinica__paciente=paciente).order_by('-fecha_registro').first()
        if ult_ev and ult_ev.estado_avance == 'RETROCESO_CRISIS':
            score_vital += 25
            factores_vital.append({
                'codigo': 'RETROCESO_CRISIS_EVOLUCION',
                'etiqueta': 'Evolución marcada en Retroceso / Crisis',
                'peso': 25,
            })

        # Señal 2: 3+ registros consecutivos de ánimo <= 2/5
        consecutivos_bajos = 0
        for a in animo_rec:
            if a.escala_valor <= 2 or a.estado_animo in ('MUY_BAJO', 'BAJO'):
                consecutivos_bajos += 1
            else:
                break

        if consecutivos_bajos >= 3:
            peso_animo = 40 if not hits_lexico else 25
            score_vital += peso_animo
            factores_vital.append({
                'codigo': 'ANIMO_BAJO_SOSTENIDO',
                'etiqueta': f'{consecutivos_bajos} días consecutivos de ánimo <= 2/5',
                'peso': peso_animo,
            })

        # Señal 3: 2+ INASISTENCIA consecutivas o > 21 días sin cita
        ultimas_citas = list(
            Cita.objects.filter(paciente=paciente, estado__in=['REALIZADA', 'INASISTENCIA'])
            .order_by('-fecha', '-hora_inicio')[:5]
        )
        consecutivas_inasist = 0
        for c in ultimas_citas:
            if c.estado == 'INASISTENCIA':
                consecutivas_inasist += 1
            else:
                break

        if consecutivas_inasist >= 2:
            score_abandono += 50
            factores_abandono.append({
                'codigo': 'INASISTENCIAS_CONSECUTIVAS',
                'etiqueta': f'{consecutivas_inasist} inasistencias consecutivas',
                'peso': 50,
            })

        ult_realizada = Cita.objects.filter(paciente=paciente, estado='REALIZADA').order_by('-fecha').first()
        tiene_futura = Cita.objects.filter(paciente=paciente, estado__in=['PROGRAMADA', 'CONFIRMADA'], fecha__gte=hoy).exists()
        if ult_realizada and not tiene_futura:
            dias_sin_cita = (hoy - ult_realizada.fecha).days
            if dias_sin_cita > 21:
                score_abandono += 25
                factores_abandono.append({
                    'codigo': 'INACTIVIDAD_21_DIAS',
                    'etiqueta': f'{dias_sin_cita} días sin nueva sesión (>21 días)',
                    'peso': 25,
                })

        # Señal 4: Caída de adherencia en tareas terapéuticas
        tareas = list(TareaTerapeutica.objects.filter(historia_clinica__paciente=paciente))
        if tareas:
            vencidas = [t for t in tareas if t.estado in ('VENCIDA', 'NO_REALIZADA')]
            tasa_incumpl = len(vencidas) / len(tareas)
            if len(vencidas) >= 2 or (len(tareas) >= 2 and tasa_incumpl >= 0.5):
                score_abandono += 30
                factores_abandono.append({
                    'codigo': 'CAIDA_ADHERENCIA_TAREAS',
                    'etiqueta': f'{len(vencidas)}/{len(tareas)} tareas vencidas o no realizadas',
                    'peso': 30,
                })

        alertas_generadas = []

        # Persistir / actualizar alerta de riesgo vital o retroceso agudo sin duplicar
        if score_vital >= 35:
            score_v = min(100, score_vital)
            sev_v = _clasificar_severidad(score_v)
            if hits_lexico and score_v < 80:
                score_v = 85
                sev_v = 'CRITICO'
            elif consecutivos_bajos >= 3 and score_v < 60:
                score_v = 65
                sev_v = 'ALTO'
            tipo_v = 'RIESGO_VITAL' if hits_lexico else 'RETROCESO_AGUDO'
            explicacion_v = (
                f"Detección longitudinal (Score {score_v}/100 — {sev_v}): "
                + '; '.join(f['etiqueta'] for f in factores_vital) + '.'
            )
            alerta_v = cls._upsert_alerta_abierta(paciente, tipo_v, score_v, sev_v, factores_vital, explicacion_v)
            alertas_generadas.append(alerta_v)

        # Persistir / actualizar alerta de deserción / abandono sin duplicar
        if score_abandono >= 35:
            score_a = min(100, score_abandono)
            sev_a = _clasificar_severidad(score_a)
            tipo_a = 'RIESGO_ABANDONO' if consecutivas_inasist >= 2 or score_a >= 50 else 'CAIDA_ADHERENCIA'
            explicacion_a = (
                f"Riesgo de deserción terapéutica (Score {score_a}/100 — {sev_a}): "
                + '; '.join(f['etiqueta'] for f in factores_abandono) + '.'
            )
            alerta_a = cls._upsert_alerta_abierta(paciente, tipo_a, score_a, sev_a, factores_abandono, explicacion_a)
            alertas_generadas.append(alerta_a)

        return alertas_generadas

    @classmethod
    def _upsert_alerta_abierta(
        cls,
        paciente: Paciente,
        tipo: str,
        score: int,
        severidad: str,
        factores: list,
        explicacion: str,
    ) -> AlertaRiesgoIA:
        """HU-50 (c): Evita duplicados actualizando la alerta abierta existente para paciente + tipo."""
        existente = (
            AlertaRiesgoIA.objects.filter(
                paciente=paciente,
                tipo=tipo,
                estado__in=['ABIERTA', 'EN_ATENCION'],
            )
            .order_by('-fecha_deteccion')
            .first()
        )
        if existente:
            existente.score_riesgo = score
            existente.severidad = severidad
            existente.factores_detectados = factores
            existente.explicacion = explicacion
            existente.save(update_fields=['score_riesgo', 'severidad', 'factores_detectados', 'explicacion', 'ultima_evaluacion'])
            return existente

        alerta = AlertaRiesgoIA.objects.create(
            paciente=paciente,
            tipo=tipo,
            score_riesgo=score,
            severidad=severidad,
            estado='ABIERTA',
            factores_detectados=factores,
            explicacion=explicacion,
        )
        log_event(
            action='ALERTA_RIESGO_IA_CREADA',
            modulo='CU24_RIESGO_IA',
            tenant=getattr(connection, 'schema_name', None),
            paciente_id=str(paciente.id),
            alerta_id=str(alerta.id),
            tipo=tipo,
            severidad=severidad,
            score_riesgo=score,
        )
        return alerta

    @classmethod
    def evaluar_todos_pacientes(cls) -> dict:
        pacientes = list(Paciente.objects.select_related('usuario').all())
        total_alertas = []
        for p in pacientes:
            total_alertas.extend(cls.evaluar_paciente(p))
        return {
            'pacientes_evaluados': len(pacientes),
            'alertas_activas_actualizadas': len(total_alertas),
        }

    @classmethod
    def listar_consola_priorizada(cls, estado: str | None = None, severidad: str | None = None):
        """HU-51 (a): Ordena siempre CRITICO arriba y por score_riesgo descendente."""
        qs = AlertaRiesgoIA.objects.select_related('paciente__usuario', 'atendido_por').annotate(
            prioridad_ord=Case(
                When(severidad='CRITICO', then=Value(1)),
                When(severidad='ALTO', then=Value(2)),
                When(severidad='MEDIO', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        )
        if estado:
            qs = qs.filter(estado=estado.upper().strip())
        if severidad:
            qs = qs.filter(severidad=severidad.upper().strip())
        return qs.order_by('prioridad_ord', '-score_riesgo', '-fecha_deteccion')

    @classmethod
    def transicionar_alerta(
        cls,
        alerta: AlertaRiesgoIA,
        nuevo_estado: str,
        nota_intervencion: str,
        usuario,
    ) -> AlertaRiesgoIA:
        """
        HU-51 (b, c): Cambia estado (ABIERTA -> EN_ATENCION -> RESUELTA/DESCARTADA).
        Exige nota_intervencion obligatoria al resolver o descartar y registra en CE_AuditLog.
        """
        est = (nuevo_estado or '').upper().strip()
        estados_validos = {'ABIERTA', 'EN_ATENCION', 'RESUELTA', 'DESCARTADA'}
        if est not in estados_validos:
            raise ValueError(f"Estado inválido '{nuevo_estado}'. Permitidos: {', '.join(sorted(estados_validos))}.")

        nota_limpia = (nota_intervencion or '').strip()
        if est in ('RESUELTA', 'DESCARTADA') and len(nota_limpia) < 5:
            raise ValueError(
                'Debe registrar una nota de intervención clínica (mínimo 5 caracteres) para resolver o descartar la alerta.'
            )

        alerta.estado = est
        if nota_limpia:
            alerta.nota_intervencion = nota_limpia
        alerta.atendido_por = usuario
        if est in ('RESUELTA', 'DESCARTADA'):
            alerta.fecha_resolucion = timezone.now()
        alerta.save(update_fields=['estado', 'nota_intervencion', 'atendido_por', 'fecha_resolucion', 'ultima_evaluacion'])

        log_event(
            action='ALERTA_RIESGO_IA_INTERVENCION',
            modulo='CU24_RIESGO_IA',
            tenant=getattr(connection, 'schema_name', None),
            user=getattr(usuario, 'email', None),
            user_id=str(usuario.id) if usuario else None,
            alerta_id=str(alerta.id),
            paciente_id=str(alerta.paciente_id),
            nuevo_estado=est,
            nota_intervencion=alerta.nota_intervencion,
        )
        return alerta
