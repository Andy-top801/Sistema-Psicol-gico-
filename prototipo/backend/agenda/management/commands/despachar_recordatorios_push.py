# -*- coding: utf-8 -*-
# Actor «tiempo» del Diagrama de Secuencia CU12 (Cron Celery Beat).
# CU12-paso 1: ejecutar_despacho_recordatorios() en cada centro (tenant) → CU12-paso 16: resumen_despacho.
# Programarlo cada 5-15 min (cron de Linux / Programador de tareas de Windows / Render Cron Job):
#     python manage.py despachar_recordatorios_push
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from tenants.models import Tenant
from agenda.services.notifications import FCMNotificationController


def despachar_en_todos_los_centros():
    total = {"total_evaluadas": 0, "total_enviadas": 0, "total_fallidas": 0, "por_centro": {}}
    for t in Tenant.objects.exclude(schema_name='public'):
        with schema_context(t.schema_name):
            # CU12-paso 1: ejecutar_despacho_recordatorios() → CTR_FCMNotificationController (devuelve CU12-paso 16)
            r = FCMNotificationController.ejecutar_despacho_recordatorios()
        for k in ("total_evaluadas", "total_enviadas", "total_fallidas"):
            total[k] += r[k]
        if r["total_evaluadas"]:
            total["por_centro"][t.schema_name] = r
    return total


class Command(BaseCommand):
    help = "CU12/HU-43: despacha recordatorios push (24h y 1h antes) de citas confirmadas en todos los centros."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("[CU12] Ejecutando despacho de recordatorios push FCM..."))
        r = despachar_en_todos_los_centros()
        for centro, res in r["por_centro"].items():
            self.stdout.write(
                f"  [{centro}] evaluadas={res['total_evaluadas']} enviadas={res['total_enviadas']} "
                f"fallidas={res['total_fallidas']} (modo {res['modo_fcm']})"
            )
        self.stdout.write(self.style.SUCCESS(
            f"resumen_despacho → total_enviadas: {r['total_enviadas']} | fallidas: {r['total_fallidas']}"
        ))
