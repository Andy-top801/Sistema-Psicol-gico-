# -*- coding: utf-8 -*-
# CU21 / HU-47: descarga (si hace falta), carga y prueba el modelo de IA de Hugging Face.
#   python manage.py precargar_modelo_ia
import time

from django.core.management.base import BaseCommand, CommandError

from clinica import ia_nlp


class Command(BaseCommand):
    help = "Descarga/carga el modelo zero-shot de Hugging Face (CU21) y clasifica un texto de prueba."

    def handle(self, *args, **options):
        self.stdout.write(f"Modelo configurado: {ia_nlp.modelo_configurado()}")
        t0 = time.perf_counter()
        try:
            ia_nlp._pipeline()
        except Exception as exc:
            raise CommandError(f"No se pudo cargar el modelo: {exc}. El sistema usará REGLAS-FALLBACK.")
        self.stdout.write(f"Modelo cargado en {time.perf_counter() - t0:.1f} s")

        texto = "no puedo dormir, tengo ataques de pánico y taquicardia al salir de casa"
        t0 = time.perf_counter()
        inf = ia_nlp.consultar_inferencia_nlp(texto)
        self.stdout.write(f"Prueba: {inf} ({time.perf_counter() - t0:.2f} s)")
        if inf['modelo_ia'] != ia_nlp.modelo_configurado():
            raise CommandError("La inferencia no usó el modelo de Hugging Face.")
        self.stdout.write(self.style.SUCCESS("Modelo de IA listo."))
