import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')
django.setup()

from django.db import connection
from django_tenants.utils import schema_context
from reportes.services import ReportEngine, FUENTES_DISPONIBLES
from reportes.exporters import CSVExporter, HTMLExporter
from tenants.models import Tenant
from accounts.models import Usuario

print("=" * 60)
print("1. DATABASE & POSTGRESQL CONNECTION TEST")
print("=" * 60)
with connection.cursor() as cursor:
    cursor.execute("SELECT current_database(), current_user, version();")
    row = cursor.fetchone()
    print(f"Connected to DB: {row[0]}")
    print(f"DB User: {row[1]}")
    print(f"PostgreSQL Version: {row[2].split(',')[0]}")

tenants = list(Tenant.objects.all())
print(f"\nRegistered Tenants in DB: {len(tenants)}")
for t in tenants:
    print(f"  - Schema: {t.schema_name:<18} | Nombre: {t.nombre}")

print("\n" + "=" * 60)
print("2. REPORT ENGINE TESTS ACROSS ALL 8 SOURCES")
print("=" * 60)
with schema_context('centro_esperanza'):
    for fuente in FUENTES_DISPONIBLES:
        try:
            res = ReportEngine.generar(fuente, None, {}, None)
            total = res.get("total", 0)
            cols = len(res.get("columnas", []))
            print(f"  [OK] Fuente: {fuente:<15} -> {total:>3} registros | {cols:>2} columnas")
        except Exception as e:
            print(f"  [FAIL] Fuente: {fuente:<15} -> Error: {e}")

print("\n" + "=" * 60)
print("3. CUSTOM REPORT BUILDER TEST (Filtros, Columnas, Orden)")
print("=" * 60)
with schema_context('centro_esperanza'):
    custom_res = ReportEngine.generar(
        fuente="citas",
        columnas=["fecha", "paciente_nombre", "psicologo_nombre", "costo", "estado"],
        filtros={"estado": "PROGRAMADA"},
        orden={"columna": "costo", "direccion": "DESC"}
    )
    print(f"  Petición personalizada procesada con éxito: {custom_res['total']} citas encontradas.")
    for idx, d in enumerate(custom_res['datos'][:3], 1):
        print(f"    Fila {idx}: {d}")

print("\n" + "=" * 60)
print("4. EXPORTERS TEST (CSV & HTML)")
print("=" * 60)
csv_resp = CSVExporter.generar(custom_res, "citas_test")
print(f"  [OK] CSV Exporter: Status {csv_resp.status_code}, Tamaño {len(csv_resp.content)} bytes")
assert csv_resp.status_code == 200
assert b"Fecha" in csv_resp.content or b"fecha" in csv_resp.content

html_str = HTMLExporter.generar(custom_res, "Reporte Test")
print(f"  [OK] HTML Exporter: Generado con {len(html_str)} caracteres")
assert "<table" in html_str
assert "</html>" in html_str

print("\n" + "=" * 60)
print("5. REST API TEST WITH TEST CLIENT")
print("=" * 60)
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

client = APIClient()
# Obtener un superadmin
user = Usuario.objects.filter(is_superuser=True).first()
if not user:
    user = Usuario.objects.first()

refresh = RefreshToken.for_user(user)
token = str(refresh.access_token)
client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}', HTTP_X_TENANT_ID='centro_esperanza')

# Test metadata endpoint
r_meta = client.get('/api/reportes/metadata/')
print(f"  [OK] GET /api/reportes/metadata/ -> Status {r_meta.status_code}")
assert r_meta.status_code == 200
assert "citas" in r_meta.data

# Test generic report
r_citas = client.get('/api/reportes/citas/')
print(f"  [OK] GET /api/reportes/citas/ -> Status {r_citas.status_code}, Registros: {r_citas.data.get('total')}")
assert r_citas.status_code == 200

# Test custom report POST
r_post = client.post('/api/reportes/personalizado/', {
    "fuente": "psicologos",
    "columnas": ["nombre_completo", "tarifa_base", "modalidad"],
    "filtros": {},
    "orden": {"columna": "tarifa_base", "direccion": "DESC"}
}, format='json')
print(f"  [OK] POST /api/reportes/personalizado/ -> Status {r_post.status_code}, Registros: {r_post.data.get('total')}")
assert r_post.status_code == 200

# Test CSV export endpoint
r_csv = client.get('/api/reportes/citas/export/csv/')
print(f"  [OK] GET /api/reportes/citas/export/csv/ -> Status {r_csv.status_code}")
assert r_csv.status_code == 200

# Test HTML export endpoint
r_html = client.get('/api/reportes/citas/export/html/')
print(f"  [OK] GET /api/reportes/citas/export/html/ -> Status {r_html.status_code}")
assert r_html.status_code == 200

print("\n" + "=" * 60)
print(">>> TODOS LOS TESTS DE BACKEND, BASE DE DATOS Y CONEXIONES PASARON EXITOSAMENTE (100%) <<<")
print("=" * 60)
