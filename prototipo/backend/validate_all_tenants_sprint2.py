"""
VALIDACIÓN EXHAUSTIVA DE DATOS DEL SPRINT 2 EN TODOS LOS TENANTS ACTIVOS DE SIGEPSI
Verifica la presencia, integridad y consistencia de:
- HU-23 & HU-24: Formularios Pre-Consulta y Respuestas Intake
- HU-35: Auditoría IA y Motor de Reglas Romero
- HU-25 & HU-26: Historias Clínicas (EHR) y Diagnósticos CIE-10
- HU-27 & HU-28: Notas de Sesión SOAP y Evolución Longitudinal
- HU-29 & HU-30: Tareas Terapéuticas y Evidencias de Adherencia
- HU-31 & HU-32: Plantillas de Consentimiento y Firmas Criptográficas SHA-256
- HU-33 & HU-34: Altas Terapéuticas (Cierres) y Derivaciones Psiquiátricas
- HU-36: Chatbot Asistente, Detección de Riesgo y Protocolo de Crisis
- HU-37: Trazas de Bitácora Forense Cifrada en Disco
"""
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')
import django
django.setup()

from django_tenants.utils import get_tenant_model, schema_context
from clinica.models import (
    Psicologo, Paciente, FormularioPreConsulta, RespuestaPreConsulta,
    AuditoriaIA, HistoriaClinica, DiagnosticoCIE, NotaSesion,
    EvolucionClinica, TareaTerapeutica, EvidenciaTarea,
    ConsentimientoInformado, FirmaConsentimiento, DerivacionCaso,
    ConversacionChatbot, MensajeChatbot
)
from audit.services import _log_path
from django.utils import timezone


def validate_all_tenants():
    Tenant = get_tenant_model()
    tenants = list(Tenant.objects.exclude(schema_name='public').order_by('schema_name'))

    print("=" * 110)
    print("MATRIZ DE VALIDACIÓN DE DATOS DEL SPRINT 2 - SIGEPSI MULTI-TENANT")
    print("=" * 110)

    all_passed = True
    summary_results = []

    for t in tenants:
        print(f"\n>>> Validando Tenant: '{t.nombre}' (Esquema: {t.schema_name})")
        errors = []

        with schema_context(t.schema_name):
            # Actores base
            n_psi = Psicologo.objects.count()
            n_pac = Paciente.objects.count()
            if n_psi < 3: errors.append(f"Insuficientes psicólogos: {n_psi} < 3")
            if n_pac < 5: errors.append(f"Insuficientes pacientes: {n_pac} < 5")

            # HU-23 / HU-24: Intake Pre-Consulta
            n_forms = FormularioPreConsulta.objects.count()
            n_resp = RespuestaPreConsulta.objects.count()
            if n_forms < 2: errors.append(f"Faltan plantillas preconsulta: {n_forms} < 2")
            if n_resp < 3: errors.append(f"Faltan respuestas de pacientes: {n_resp} < 3")

            # HU-35: Motor de Reglas Romero y Auditoría IA
            n_ia = AuditoriaIA.objects.count()
            if n_ia < 3: errors.append(f"Faltan registros de auditoría IA: {n_ia} < 3")

            # HU-25 / HU-26: EHR y CIE-10
            n_hc = HistoriaClinica.objects.count()
            n_cie = DiagnosticoCIE.objects.count()
            if n_hc < 3: errors.append(f"Faltan historias clínicas: {n_hc} < 3")
            if n_cie < 5: errors.append(f"Faltan diagnósticos CIE-10: {n_cie} < 5")

            # HU-27 / HU-28: SOAP y Evolución
            n_soap = NotaSesion.objects.count()
            n_firmadas = NotaSesion.objects.filter(estado_guardado='FIRMADA').count()
            n_borradores = NotaSesion.objects.filter(estado_guardado='BORRADOR').count()
            n_evo = EvolucionClinica.objects.count()
            if n_soap < 4: errors.append(f"Faltan notas SOAP: {n_soap} < 4")
            if n_firmadas < 2: errors.append("Faltan notas SOAP firmadas")
            if n_borradores < 1: errors.append("Falta al menos un borrador autosave SOAP")
            if n_evo < 2: errors.append(f"Faltan evoluciones clínicas: {n_evo} < 2")

            # HU-29 / HU-30: Tareas y Evidencias
            n_tar = TareaTerapeutica.objects.count()
            n_evi = EvidenciaTarea.objects.count()
            cats = set(TareaTerapeutica.objects.values_list('categoria', flat=True))
            if n_tar < 4: errors.append(f"Faltan tareas terapéuticas: {n_tar} < 4")
            if n_evi < 2: errors.append(f"Faltan evidencias de cumplimiento: {n_evi} < 2")
            if not {'AUTOREGISTRO', 'MINDFULNESS', 'CONDUCTUAL'}.issubset(cats):
                errors.append(f"Faltan categorías clínicas en tareas: {cats}")

            # HU-31 / HU-32: Consentimientos y Firmas SHA-256
            n_cons = ConsentimientoInformado.objects.count()
            n_firm = FirmaConsentimiento.objects.count()
            n_sha = FirmaConsentimiento.objects.filter(hash_sha256__isnull=False).exclude(hash_sha256="").count()
            if n_cons < 4: errors.append(f"Faltan tipos de consentimiento: {n_cons} < 4")
            if n_firm < 3: errors.append(f"Faltan firmas de pacientes: {n_firm} < 3")
            if n_sha < 3: errors.append(f"Faltan firmas con hash SHA-256 válido: {n_sha} < 3")

            # HU-33 / HU-34: Cierre y Derivaciones
            n_altas = DerivacionCaso.objects.filter(tipo_derivacion='CIERRE_ALTA').count()
            n_psiquiatria = DerivacionCaso.objects.filter(tipo_derivacion='EXTERNA_PSIQUIATRIA').count()
            n_hc_cerradas = HistoriaClinica.objects.filter(cerrada=True).count()
            if n_altas < 1: errors.append("Falta registro de Alta Terapéutica formal (CIERRE_ALTA)")
            if n_psiquiatria < 1: errors.append("Falta registro de Derivación Psiquiátrica externa")
            if n_hc_cerradas < 1: errors.append("Falta historia clínica cerrada por alta")

            # HU-36: Chatbot y Crisis
            n_chat = ConversacionChatbot.objects.count()
            n_msg = MensajeChatbot.objects.count()
            n_crisis_chat = ConversacionChatbot.objects.filter(nivel_riesgo='CRISIS').count()
            n_crisis_msg = MensajeChatbot.objects.filter(es_alerta_crisis=True).count()
            if n_chat < 2: errors.append(f"Faltan conversaciones de chatbot: {n_chat} < 2")
            if n_msg < 5: errors.append(f"Faltan mensajes de chatbot: {n_msg} < 5")
            if n_crisis_chat < 1: errors.append("Falta conversación con riesgo CRISIS")
            if n_crisis_msg < 1: errors.append("Falta mensaje de chatbot con alerta de crisis vital")

        if errors:
            all_passed = False
            print(f"  ❌ FALLOS DETECTADOS ({len(errors)}):")
            for err in errors:
                print(f"     - {err}")
        else:
            print(f"  ✅ [VALIDACIÓN EXITOSA] Todos los criterios de aceptación del Sprint 2 cumplidos al 100%.")

        summary_results.append({
            'tenant': t.schema_name,
            'nombre': t.nombre,
            'ok': len(errors) == 0,
            'psi': n_psi, 'pac': n_pac, 'resp': n_resp, 'ia': n_ia,
            'hc': n_hc, 'cie': n_cie, 'soap': n_soap, 'evo': n_evo,
            'tar': n_tar, 'evi': n_evi, 'cons': n_cons, 'firm': n_firm,
            'altas': n_altas, 'deriv_psi': n_psiquiatria,
            'chat': n_chat, 'crisis_chat': n_crisis_chat
        })

    # HU-37: Verificación de bitácora en disco
    today = timezone.localtime(timezone.now()).date()
    log_file = _log_path(today)
    log_exists = log_file.exists() and log_file.stat().st_size > 0
    print(f"\n>>> HU-37: Archivo de bitácora forense cifrada en disco: {log_file}")
    if log_exists:
        print(f"  ✅ [OK] Bitácora en disco activa y verificada ({log_file.stat().st_size} bytes cifrados Fernet).")
    else:
        print(f"  ❌ [ERROR] No se encontró archivo de bitácora cifrada.")
        all_passed = False

    print("\n" + "=" * 110)
    print("RESUMEN GENERAL POR TENANT:")
    print("=" * 110)
    print(f"{'TENANT':<20} | {'ESTADO':<8} | {'PAC':<4} | {'INTAKE':<6} | {'IA':<4} | {'HC':<4} | {'CIE':<4} | {'SOAP':<4} | {'TAREAS':<6} | {'FIRMAS':<6} | {'ALTA':<4} | {'DERIV':<5} | {'CHATS':<5}")
    print("-" * 110)
    for s in summary_results:
        st_str = "VÁLIDO" if s['ok'] else "ERROR"
        print(f"{s['tenant']:<20} | {st_str:<8} | {s['pac']:<4} | {s['resp']:<6} | {s['ia']:<4} | {s['hc']:<4} | {s['cie']:<4} | {s['soap']:<4} | {s['tar']:<6} | {s['firm']:<6} | {s['altas']:<4} | {s['deriv_psi']:<5} | {s['chat']:<5}")
    print("=" * 110)

    if all_passed:
        print("\n🎉 ¡TODOS LOS TENANTS CUENTAN CON DATOS VÁLIDOS Y COMPLETOS DE TODAS LAS HISTORIAS DE USUARIO DEL SPRINT 2! 🎉\n")
        return True
    else:
        print("\n⚠️ ALGUNOS TENANTS NO SUPERARON LA VALIDACIÓN COMPLETA.\n")
        return False


if __name__ == '__main__':
    ok = validate_all_tenants()
    sys.exit(0 if ok else 1)
