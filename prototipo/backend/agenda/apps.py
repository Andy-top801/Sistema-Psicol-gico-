import os
import sys
import threading
import time
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


def _ciclo_recordatorios(intervalo):
    """Cron embebido para desarrollo: CU12-paso 1 cada `intervalo` segundos."""
    from agenda.management.commands.despachar_recordatorios_push import despachar_en_todos_los_centros
    time.sleep(10)  # deja que el servidor termine de arrancar
    while True:
        try:
            r = despachar_en_todos_los_centros()
            if r["total_evaluadas"]:
                logger.warning(f"[CU12-Cron] enviadas={r['total_enviadas']} fallidas={r['total_fallidas']}")
        except Exception as e:
            logger.error(f"[CU12-Cron] {e}")
        time.sleep(intervalo)


class AgendaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agenda'
    verbose_name = 'Agenda, Teleconsulta y Alertas'

    def ready(self):
        # Solo con `runserver` (proceso hijo del autoreload) y si está habilitado en .env.
        # ponytail: hilo en proceso, sustituir por Celery Beat / cron real en producción.
        activo = os.environ.get('RECORDATORIOS_AUTOMATICOS', 'False').lower() in ('true', '1', 'yes')
        proceso_servidor = os.environ.get('RUN_MAIN') == 'true' or '--noreload' in sys.argv
        if activo and 'runserver' in sys.argv and proceso_servidor:
            intervalo = int(os.environ.get('RECORDATORIOS_INTERVALO_SEG', '60'))
            threading.Thread(target=_ciclo_recordatorios, args=(intervalo,), daemon=True).start()
