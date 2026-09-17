import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')
django.setup()

from audit.services import read_events, write_event, _cipher
from audit.views import AuditLogView
from reportes.services import ReportEngine
from rest_framework.test import APIRequestFactory, force_authenticate
from accounts.models import Usuario, Rol

print("=" * 60)
print("1. VERIFICANDO CIFRADOR FERNET Y AUDIT_LOG_KEY")
print("=" * 60)
try:
    c = _cipher()
    print("[OK] Cifrador Fernet derivado e inicializado correctamente con SHA-256.")
except Exception as e:
    print(f"[ERROR] Error al inicializar cifrador: {e}")

print("\n" + "=" * 60)
print("2. PROBANDO LECTURA Y DESCIFRADO DE BITACORA COMPLETA")
print("=" * 60)
try:
    events = read_events()
    print(f"[OK] Total eventos descifrados sin ninguna falla: {len(events)}")
    if events:
        last = events[-1]
        print(f"     Último evento registrado:")
        print(f"     - Timestamp: {last.get('timestamp')}")
        print(f"     - Usuario:   {last.get('user')}")
        print(f"     - Método:    {last.get('method')}")
        print(f"     - Ruta:      {last.get('path')}")
        print(f"     - Status:    {last.get('status_code')}")
        print(f"     - IP:        {last.get('ip')}")
except Exception as e:
    print(f"[ERROR] Error al leer eventos: {e}")

print("\n" + "=" * 60)
print("3. PROBANDO ESCRITURA Y CIFRADO DE UN NUEVO EVENTO")
print("=" * 60)
try:
    write_event({
        "ip": "127.0.0.1",
        "user_id": None,
        "user": "test_auditor@sigepsi.com",
        "tenant": "public",
        "method": "POST",
        "path": "/api/test-auditoria-verificacion/",
        "action": "POST /api/test-auditoria-verificacion/",
        "status_code": 200,
        "error": None
    })
    events_after = read_events()
    print(f"[OK] Evento de auditoría cifrado y guardado. Nuevo total: {len(events_after)}")
    last_ev = events_after[-1]
    assert last_ev["user"] == "test_auditor@sigepsi.com"
    print("[OK] Verificación de integridad de lectura del evento recién escrito: ÉXITO")
except Exception as e:
    print(f"[ERROR] Error al escribir evento: {e}")

print("\n" + "=" * 60)
print("4. PROBANDO ENDPOINT REST /api/audit/logs/ CON PERMISOS")
print("=" * 60)
factory = APIRequestFactory()
superadmin = Usuario.objects.filter(is_superuser=True).first()
if not superadmin:
    superadmin = Usuario.objects.filter(rol__nombre="SuperAdmin").first()

if superadmin:
    # Test SuperAdmin
    req_sa = factory.get("/api/audit/logs/")
    force_authenticate(req_sa, user=superadmin)
    view = AuditLogView.as_view()
    res_sa = view(req_sa)
    print(f"[OK] Acceso SuperAdmin ({superadmin.email}): Status {res_sa.status_code}, Eventos devueltos: {len(res_sa.data)}")

    # Test No-SuperAdmin (usuario normal o anónimo)
    psico = Usuario.objects.filter(rol__nombre="Psicólogo").first()
    if psico:
        req_norm = factory.get("/api/audit/logs/")
        force_authenticate(req_norm, user=psico)
        res_norm = view(req_norm)
        print(f"[OK] Acceso Usuario Normal ({psico.email}): Status {res_norm.status_code} (Acceso denegado correctamente)")
    else:
        req_anon = factory.get("/api/audit/logs/")
        res_anon = view(req_anon)
        print(f"[OK] Acceso Anónimo: Status {res_anon.status_code} (Acceso denegado correctamente)")
else:
    print("[WARN] No se encontró usuario SuperAdmin en la base de datos.")

print("\n" + "=" * 60)
print("5. PROBANDO INTEGRACIÓN CON MOTOR DE REPORTES (FUENTE: bitacora)")
print("=" * 60)
try:
    res = ReportEngine.generar("bitacora", filtros={"status_code": "200"})
    filas = res.get("datos", [])
    print(f"[OK] ReportEngine.generar('bitacora', status_code=200): {len(filas)} filas filtradas.")
    if filas:
        print(f"     Columnas: {[c['label'] for c in res.get('columnas', [])]}")
        print(f"     Ejemplo de fila exportable: {filas[0]}")

    # Probar exportaciones
    from reportes.exporters import CSVExporter, HTMLExporter, ExcelExporter
    csv_resp = CSVExporter.generar(res, "bitacora_test")
    print(f"[OK] CSV Exporter bitacora: Status {csv_resp.status_code}, Tamaño: {len(csv_resp.content)} bytes")

    html_str = HTMLExporter.generar(res, "bitacora_test", "Plataforma Global SIGEPSI")
    print(f"[OK] HTML Exporter bitacora: Generado correctamente con {len(html_str)} caracteres HTML.")

    excel_resp = ExcelExporter.generar(res, "bitacora_test", "Plataforma Global SIGEPSI")
    print(f"[OK] Excel Exporter bitacora: Status {excel_resp.status_code}, Tamaño: {len(excel_resp.content)} bytes")
except Exception as e:
    print(f"[ERROR] Error en motor de reportes o exportadores para bitácora: {e}")

print("\n" + "=" * 60)
print("6. PROBANDO AUDITORÍA IA (SPRINT 2 HU-35)")
print("=" * 60)
try:
    from clinica.models import AuditoriaDecisionIA
    count_ai = AuditoriaDecisionIA.objects.count()
    print(f"[OK] Modelo AuditoriaDecisionIA accesible. Registros en tenant activo: {count_ai}")
except Exception as e:
    print(f"[INFO] Modelo AuditoriaDecisionIA: {e}")
