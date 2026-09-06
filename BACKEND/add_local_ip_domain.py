import os
import django
import sys
import socket

# Setup Django environment
sys.path.append(r"c:\Users\MARILYN\Documents\Carpeta Esther\Semestre 2-2026\Sistema-Psicol-gico-\BACKEND")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sigepsi.settings")
django.setup()

from apps.tenants.models import Centro, Dominio

# Get local IP address of the PC
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
except Exception:
    local_ip = "192.168.1.15"  # Fallback to standard local IP if offline

print(f"IP local detectada: {local_ip}")

# Get the tenant for clinica_demo
try:
    centro_demo = Centro.objects.get(schema_name='clinica_demo')
    
    # Register the IP as a valid domain for this tenant
    dominio, created = Dominio.objects.get_or_create(
        domain=local_ip,
        defaults={
            'tenant': centro_demo,
            'is_primary': False
        }
    )
    
    if created:
        print(f"¡Dominio '{local_ip}' registrado con éxito para la clínica 'clinica_demo'!")
    else:
        print(f"El dominio '{local_ip}' ya estaba registrado para la clínica.")
        
    print("\n--- INSTRUCCIONES PARA PROBAR DESDE TU CELULAR ---")
    print(f"1. Asegúrate de que tu celular y tu computadora estén conectados al mismo Wi-Fi.")
    print(f"2. En la terminal de la app móvil (MOBILE), ejecuta este comando:")
    print(f"   flutter run --dart-define=API_BASE_URL=http://{local_ip}:8000/api")
    print(f"3. ¡Listo! Tu celular se comunicará directamente con tu base de datos local.")
    
except Centro.DoesNotExist:
    print("Error: No se encontró la clínica 'clinica_demo'. Primero debes correr python manage.py init_system.")
