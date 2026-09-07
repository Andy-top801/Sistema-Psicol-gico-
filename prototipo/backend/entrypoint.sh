#!/bin/bash
set -e

echo "=========================================================="
echo "🚀 SIGEPSI Backend Container Starting..."
echo "=========================================================="

# Esperar a que la base de datos PostgreSQL responda
echo "==> Verificando conexión con PostgreSQL..."
python << 'EOF'
import os
import sys
import time
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')
django.setup()

from django.db import connections
from django.db.utils import OperationalError

max_retries = 30
retry_interval = 2

for i in range(1, max_retries + 1):
    try:
        connection = connections['default']
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        print(f"✅ Conexión con PostgreSQL establecida exitosamente (intento {i})")
        sys.exit(0)
    except OperationalError as e:
        print(f"⏳ Esperando a PostgreSQL... ({i}/{max_retries}): {e}")
        time.sleep(retry_interval)

print("❌ Error: No fue posible conectar con PostgreSQL tras múltiples intentos.")
sys.exit(1)
EOF

echo "==> Ejecutando migraciones de django-tenants (public + tenants)..."
python manage.py migrate_schemas --shared --noinput
python manage.py migrate_schemas --tenant --noinput

echo "==> Sembrando datos base (Tenant public, SuperAdmin, roles y permisos)..."
python manage.py seed_data || echo "Nota: seed_data ya fue ejecutado previamente."

echo "==> Sembrando datos clínicos Sprint 1 (Especialidades, psicólogos, pacientes)..."
python manage.py seed_sprint1 || echo "Nota: seed_sprint1 ya fue ejecutado previamente."

echo "==> Recopilando archivos estáticos para WhiteNoise..."
python manage.py collectstatic --noinput

PORT="${PORT:-8000}"
echo "=========================================================="
echo "🔥 Arrancando Gunicorn en el puerto $PORT..."
echo "=========================================================="

exec gunicorn sigepsi.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
