# ==============================================================================
# MÓDULO: clinica/ia_resumen_service.py
# CASO DE USO: CU23 (HU-49) Generación asistida de resúmenes clínicos
#              longitudinales por IA (Híbrido Hugging Face + Fallback + HITL)
# ==============================================================================
import hashlib
import io
import json
import logging
import os
import re
import urllib.request
import urllib.error
from django.db import connection
from django.http import HttpResponse
from django.utils import timezone

from audit.services import log_event
from clinica.ia_rules_engine import PreconsultaRulesEngine
from clinica.models import (
    Paciente,
    HistoriaClinica,
    NotaSesion,
    EvolucionClinica,
    RegistroAnimo,
    TareaTerapeutica,
    RespuestaPreConsulta,
    ResumenClinicoIA,
)

logger = logging.getLogger(__name__)

HF_RESUMEN_URL = os.environ.get(
    'IA_RESUMEN_API_URL',
    'https://antidino-iacupficct.hf.space/api/v1/clinica/resumen-longitudinal/',
)
HF_TIMEOUT_SECONDS = 15
ETIQUETA_OBLIGATORIA = 'Borrador IA — Requiere Revisión Profesional'


def psicologo_asignado_al_paciente(user, paciente: Paciente) -> bool:
    """
    HU-49 (b): Verifica que solo el psicólogo tratante asignado, Coordinador,
    Admin Centro o SuperAdmin puedan leer o generar resúmenes IA del paciente.
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    rol = (user.rol.nombre or '').lower() if getattr(user, 'rol', None) else ''
    if 'admin' in rol or 'coordinador' in rol:
        return True
    if 'psic' in rol and hasattr(user, 'perfil_psicologo'):
        psico = user.perfil_psicologo
        if paciente.citas.filter(psicologo=psico).exists():
            return True
        if HistoriaClinica.objects.filter(paciente=paciente, psicologo_apertura=psico).exists():
            return True
        if NotaSesion.objects.filter(historia_clinica__paciente=paciente, psicologo=psico).exists():
            return True
    return False


def _sanitizar_narrativa_paciente(texto: str, paciente: Paciente) -> str:
    """Anonimiza CI, teléfonos, correos y nombres propios del paciente antes de IA."""
    limpio = PreconsultaRulesEngine.sanitizar_pii(texto or '')
    tokens_nombre = [
        (paciente.usuario.nombre or '').strip(),
        (paciente.usuario.apellido or '').strip(),
        (paciente.ci or '').strip(),
        (paciente.usuario.email or '').strip(),
        (paciente.usuario.telefono or '').strip(),
    ]
    for tok in tokens_nombre:
        if tok and len(tok) >= 3:
            limpio = re.sub(re.escape(tok), '[ANONIMIZADO]', limpio, flags=re.IGNORECASE)
    return limpio


def _llamar_hf_resumen(payload_anonimizado: dict) -> str | None:
    """Invoca Hugging Face Space con timeout estricto de 15s; retorna None en fallo."""
    if os.environ.get('IA_RESUMEN_OFFLINE', '0') == '1':
        return None
    try:
        req = urllib.request.Request(
            HF_RESUMEN_URL,
            data=json.dumps(payload_anonimizado).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=HF_TIMEOUT_SECONDS) as resp:
            if resp.status == 200:
                body = json.loads(resp.read().decode('utf-8'))
                resumen = body.get('resumen') or body.get('summary') or body.get('texto')
                if resumen and isinstance(resumen, str) and len(resumen.strip()) > 20:
                    return resumen.strip()
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        logger.warning('Fallback determinístico activado para Resumen IA (HF no disponible): %s', exc)
    return None


class ResumenIAService:
    """Servicio longitudinal híbrido (HF + Fallback determinístico + HITL)."""

    @classmethod
    def generar_resumen(cls, paciente: Paciente, usuario=None, usar_hf: bool = True) -> ResumenClinicoIA:
        hc = HistoriaClinica.objects.filter(paciente=paciente).order_by('-fecha_apertura').first()
        notas = list(
            NotaSesion.objects.filter(historia_clinica__paciente=paciente)
            .order_by('fecha_sesion')[:30]
        )
        evoluciones = list(
            EvolucionClinica.objects.filter(historia_clinica__paciente=paciente)
            .order_by('fecha_registro')[:30]
        )
        total_insumos = len(notas) + len(evoluciones)
        if total_insumos < 2:
            raise ValueError(
                'El paciente debe contar con al menos 2 notas SOAP o evoluciones clínicas para generar un resumen longitudinal.'
            )

        # 1. Motivo Inicial sanitizado
        motivo_raw = ''
        if hc and hc.motivo_consulta_inicial:
            motivo_raw = hc.motivo_consulta_inicial
        else:
            resp_intake = RespuestaPreConsulta.objects.filter(paciente=paciente).order_by('-fecha_respuesta').first()
            if resp_intake:
                motivo_raw = resp_intake.motivo_consulta or ''
        motivo_sanitizado = _sanitizar_narrativa_paciente(motivo_raw or 'No registrado en historia clínica.', paciente)

        # 2. Síntesis de notas SOAP sanitizadas
        soap_extractos = []
        for n in notas[-6:]:
            s_clean = _sanitizar_narrativa_paciente(n.subjetivo, paciente)[:180]
            a_clean = _sanitizar_narrativa_paciente(n.analisis, paciente)[:180]
            p_clean = _sanitizar_narrativa_paciente(n.plan, paciente)[:160]
            soap_extractos.append(
                f"Sesión #{n.numero_sesion} ({n.fecha_sesion.strftime('%Y-%m-%d')}): "
                f"S: {s_clean} | A: {a_clean} | P: {p_clean}"
            )
        for ev in evoluciones[-4:]:
            j_clean = _sanitizar_narrativa_paciente(ev.justificacion, paciente)[:180]
            soap_extractos.append(
                f"Evolución ({ev.fecha_registro.strftime('%Y-%m-%d')} — {ev.estado_avance}): {j_clean}"
            )

        # 3. Tendencia Mood Tracker
        animo_qs = list(RegistroAnimo.objects.filter(paciente=paciente).order_by('-fecha_registro')[:14])
        if animo_qs:
            promedio_animo = round(sum(a.escala_valor for a in animo_qs) / len(animo_qs), 2)
            ultimo_animo = animo_qs[0]
            tendencia_mood = (
                f"Promedio últimos {len(animo_qs)} registros: {promedio_animo}/5. "
                f"Último estado: {ultimo_animo.estado_animo} ({ultimo_animo.escala_valor}/5 el {ultimo_animo.fecha_registro.isoformat()})."
            )
        else:
            tendencia_mood = 'Sin registros recientes en Mood Tracker.'

        # 4. Adherencia a tareas terapéuticas
        tareas = list(TareaTerapeutica.objects.filter(historia_clinica__paciente=paciente))
        if tareas:
            completadas = sum(1 for t in tareas if t.estado in ('COMPLETADA', 'COMPLETADA_CON_RETRASO'))
            vencidas = sum(1 for t in tareas if t.estado in ('VENCIDA', 'NO_REALIZADA'))
            pct_adh = round((completadas / len(tareas)) * 100.0, 1)
            adherencia_str = (
                f"Adherencia terapéutica: {pct_adh}% ({completadas}/{len(tareas)} completadas, {vencidas} vencidas/no realizadas)."
            )
        else:
            adherencia_str = 'Sin tareas terapéuticas asignadas.'

        secciones = {
            'motivo_inicial': motivo_sanitizado,
            'sintesis_soap': soap_extractos,
            'tendencia_mood_tracker': tendencia_mood,
            'adherencia_tareas': adherencia_str,
        }

        # Intentar Hugging Face Space (solo con datos sanitizados)
        texto_hf = _llamar_hf_resumen({
            'expediente': paciente.codigo_expediente,
            'secciones': secciones,
        }) if usar_hf else None

        if texto_hf:
            fuente = 'HUGGINGFACE'
            texto_final = texto_hf
        else:
            fuente = 'FALLBACK_LOCAL'
            bloques_soap = '\n'.join(f"- {line}" for line in soap_extractos)
            texto_final = (
                f"[{ETIQUETA_OBLIGATORIA}]\n\n"
                f"1. MOTIVO INICIAL:\n{motivo_sanitizado}\n\n"
                f"2. SÍNTESIS LONGITUDINAL DE NOTAS SOAP Y EVOLUCIONES ({total_insumos} registros):\n{bloques_soap}\n\n"
                f"3. TENDENCIA MOOD TRACKER:\n{tendencia_mood}\n\n"
                f"4. ADHERENCIA A TAREAS TERAPÉUTICAS:\n{adherencia_str}\n\n"
                f"Nota clínica: Este borrador es un apoyo de preparación de sesión y no emite diagnósticos CIE automáticos."
            )

        hash_input = json.dumps({
            'paciente_id': str(paciente.id),
            'fuente': fuente,
            'texto': texto_final,
        }, sort_keys=True, ensure_ascii=False).encode('utf-8')
        hash_sha256 = hashlib.sha256(hash_input).hexdigest()

        resumen = ResumenClinicoIA.objects.create(
            paciente=paciente,
            historia_clinica=hc,
            estado='BORRADOR_IA',
            fuente_modelo=fuente,
            etiqueta_cumplimiento=ETIQUETA_OBLIGATORIA,
            contenido_estructurado=secciones,
            texto_resumen=texto_final,
            hash_sha256=hash_sha256,
            total_notas_analizadas=total_insumos,
            generado_por=usuario,
        )

        log_event(
            action='RESUMEN_IA_GENERADO',
            modulo='CU23_IA_LONGITUDINAL',
            tenant=getattr(connection, 'schema_name', None),
            user=getattr(usuario, 'email', None),
            user_id=str(usuario.id) if usuario else None,
            paciente_id=str(paciente.id),
            resumen_id=str(resumen.id),
            fuente_modelo=fuente,
            hash_sha256=hash_sha256,
        )
        return resumen

    @classmethod
    def aprobar_hitl(
        cls,
        resumen: ResumenClinicoIA,
        usuario,
        texto_editado: str | None = None,
        contenido_editado: dict | None = None,
    ) -> ResumenClinicoIA:
        """HU-49 (c): Aprobación explícita Human-in-the-Loop sin diagnósticos automáticos."""
        if texto_editado is not None and texto_editado.strip():
            resumen.texto_resumen = texto_editado.strip()
        if contenido_editado is not None and isinstance(contenido_editado, dict):
            resumen.contenido_estructurado = contenido_editado

        resumen.estado = 'APROBADO_HITL'
        resumen.aprobado_por = usuario
        resumen.fecha_aprobacion = timezone.now()
        resumen.hash_sha256 = hashlib.sha256(
            f"{resumen.id}|{resumen.texto_resumen}|{resumen.fecha_aprobacion.isoformat()}".encode('utf-8')
        ).hexdigest()
        resumen.save(update_fields=[
            'texto_resumen', 'contenido_estructurado', 'estado',
            'aprobado_por', 'fecha_aprobacion', 'hash_sha256',
        ])

        log_event(
            action='RESUMEN_IA_APROBADO_HITL',
            modulo='CU23_IA_LONGITUDINAL',
            tenant=getattr(connection, 'schema_name', None),
            user=getattr(usuario, 'email', None),
            user_id=str(usuario.id) if usuario else None,
            paciente_id=str(resumen.paciente_id),
            resumen_id=str(resumen.id),
            hash_sha256=resumen.hash_sha256,
        )
        return resumen


def generar_resumen_ia_pdf(resumen: ResumenClinicoIA, tenant_name: str = 'Centro Psicológico') -> HttpResponse:
    """Exporta el resumen clínico longitudinal a PDF oficial con marca de estado HITL."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from finanzas.pdf_utils import NumberedCanvas

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    title_st = ParagraphStyle('AITitle', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor('#0F2922'))
    banner_color = colors.HexColor('#B45309') if resumen.estado == 'BORRADOR_IA' else colors.HexColor('#047857')
    banner_st = ParagraphStyle('AIBanner', parent=styles['Normal'], fontSize=10, textColor=banner_color, fontName='Helvetica-Bold', spaceAfter=10)
    body_st = ParagraphStyle('AIBody', parent=styles['Normal'], fontSize=9.5, leading=13.5, spaceAfter=8)

    story = [
        Paragraph(f"RESUMEN CLÍNICO LONGITUDINAL IA — {tenant_name.upper()}", title_st),
        Paragraph(f"Estado: {resumen.estado} | {resumen.etiqueta_cumplimiento}", banner_st),
        Paragraph(
            f"<b>Expediente:</b> {resumen.paciente.codigo_expediente} &nbsp;|&nbsp; "
            f"<b>Modelo:</b> {resumen.fuente_modelo} &nbsp;|&nbsp; "
            f"<b>Hash SHA-256:</b> {resumen.hash_sha256[:24]}...",
            styles['Normal'],
        ),
        Spacer(1, 12),
    ]
    for linea in (resumen.texto_resumen or '').split('\n'):
        if linea.strip():
            safe_line = linea.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(safe_line, body_st))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    resp = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="resumen_ia_{resumen.paciente.codigo_expediente}.pdf"'
    return resp
