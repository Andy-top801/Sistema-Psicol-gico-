# -*- coding: utf-8 -*-
# CU21/CU22 — Task 1: campos de carga del psicólogo, asignación y modalidad del paciente.
#   python tests/test_cu21_cu22_modelos.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigepsi.settings')

import django
django.setup()

from django_tenants.utils import schema_context

TENANT = 'centro_esperanza'


def test_carga_psicologo_y_obtener_paciente():
    from clinica.models import Psicologo, Paciente
    psico = Psicologo.objects.filter(activo=True).first()
    pac = Paciente.objects.first()
    assert psico and pac, "El tenant necesita datos seed (seed_sprint1)"
    carga_orig, cupo_orig = psico.carga_actual, psico.cupo_maximo
    try:
        psico.carga_actual, psico.cupo_maximo = 0, 2
        psico.save(update_fields=['carga_actual', 'cupo_maximo'])
        assert psico.cupo_completo is False
        assert psico.incrementar_carga() == 1
        assert psico.incrementar_carga() == 2
        assert psico.carga_actual == 2
        assert psico.cupo_completo is True
        assert Psicologo.listar_candidatos_activos().filter(id=psico.id).exists()

        datos = Paciente.obtener_paciente(pac.id)
        assert datos['modalidad_preferencia'] in ('PRESENCIAL', 'VIRTUAL', 'MIXTA')
        assert datos['paciente_id'] == str(pac.id)
        assert hasattr(pac, 'psicologo_asignado')
    finally:
        psico.carga_actual, psico.cupo_maximo = carga_orig, cupo_orig
        psico.save(update_fields=['carga_actual', 'cupo_maximo'])


def test_severidades_hu47():
    from clinica.models import ClasificacionIA
    codigos = [c for c, _ in ClasificacionIA.SEVERIDAD_CHOICES]
    assert codigos == ['BAJA', 'MODERADA', 'ALTA', 'CRITICA']
    assert not ClasificacionIA.objects.filter(nivel_severidad__in=['LEVE', 'MODERADO', 'SEVERO']).exists()


if __name__ == "__main__":
    with schema_context(TENANT):
        test_carga_psicologo_y_obtener_paciente()
        test_severidades_hu47()
    print("ALL CU21-CU22 MODELOS TESTS PASSED [OK]")
