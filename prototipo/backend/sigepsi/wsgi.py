import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')
application = get_wsgi_application()

# CU21: precarga del modelo de IA en cada worker de Gunicorn (en segundo plano, sin bloquear
# el arranque). Solo si IA_PRECARGAR=True (lo exporta entrypoint.sh); runserver no lo activa.
if os.environ.get('IA_PRECARGAR', 'False').lower() in ('true', '1', 'yes'):
    import threading
    from clinica.ia_nlp import precargar_en_segundo_plano
    threading.Thread(target=precargar_en_segundo_plano, daemon=True).start()
