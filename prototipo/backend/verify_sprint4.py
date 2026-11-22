# ==============================================================================
# SCRIPT DE CERTIFICACIÓN: verify_sprint4.py
# DESCRIPCIÓN: Ejecuta todas las suites automatizadas del Sprint 4 (HU-49 a HU-56)
#              y genera el reporte consolidado de aprobación.
# ==============================================================================
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PYTHON = sys.executable

SUITES = [
    ('Fase 1 — HU-52 / HU-54 (Caja, Extracto 20 años y Honorarios)', BASE_DIR / 'tests' / 'test_sprint4_fase1_finanzas.py'),
    ('Fase 2 — HU-53 (Dashboard 24m, Reportes Unificados y PDFExporter)', BASE_DIR / 'tests' / 'test_sprint4_fase2_dashboard_reportes.py'),
    ('Fase 3 — HU-55 (Suscripciones SaaS USD, Stripe Idempotente y Cupos)', BASE_DIR / 'tests' / 'test_sprint4_fase3_saas.py'),
    ('Fase 4 — HU-49 / HU-50 / HU-51 (IA Longitudinal HITL y Alertas Riesgo)', BASE_DIR / 'tests' / 'test_sprint4_fase4_ia_longitudinal.py'),
    ('Fase 6 — HU-56 (Estrés 32 reqs, Aislamiento JWT Multi-Tenant y Benchmark)', BASE_DIR / 'tests' / 'test_sprint4_fase6_estres_multitenant.py'),
]


def main():
    print('=' * 78)
    print('CERTIFICACIÓN INTEGRAL SPRINT 4 — SIGEPSI (HU-49 a HU-56)')
    print('=' * 78)

    passed = 0
    for titulo, script in SUITES:
        print(f'\n>>> Ejecutando: {titulo}')
        proc = subprocess.run([PYTHON, str(script)], capture_output=True, text=True)
        if proc.stdout:
            print(proc.stdout.strip())
        if proc.returncode != 0:
            if proc.stderr:
                print(proc.stderr.strip())
            print(f'[FALLO] {titulo}')
            sys.exit(1)
        passed += 1

    print('\n' + '=' * 78)
    print(f'[CERTIFICADO] {passed}/{len(SUITES)} SUITES DEL SPRINT 4 APROBADAS AL 100%.')
    print('=' * 78)


if __name__ == '__main__':
    main()
