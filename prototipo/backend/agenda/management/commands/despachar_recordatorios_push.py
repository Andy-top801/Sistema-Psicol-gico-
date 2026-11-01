# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from tenants.models import Tenant
from agenda.services import FCMNotificationService

class Command(BaseCommand):
    help = "Despacha recordatorios preventivos de citas (24h y 1h antes) y avisos push para pacientes en todos los centros (CU12 / HU-43)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando despacho de recordatorios push FCM..."))
        tenants = Tenant.objects.exclude(schema_name='public')
        total_despachadas = 0

        for t in tenants:
            with schema_context(t.schema_name):
                num = FCMNotificationService.procesar_recordatorios_programados()
                total_despachadas += num
                if num > 0:
                    self.stdout.write(self.style.SUCCESS(f"  [{t.schema_name}] {num} notificaciones push procesadas."))

        self.stdout.write(self.style.SUCCESS(f"Finalizado. Total despachos ejecutados: {total_despachadas}"))
