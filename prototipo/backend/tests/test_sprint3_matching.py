# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_matching_psicologo_service_weights_and_hitl():
    from clinica.ia_rules_engine import MatchingPsicologoService

    # Mock psychologists queryset/objects
    class MockUsuario:
        def __init__(self, nombre, email, is_active=True):
            self.first_name = nombre
            self.email = email
            self.is_active = is_active
        def get_full_name(self):
            return self.first_name

    class MockEspecialidadRel:
        def __init__(self, codes):
            self.codes = codes
        def all(self):
            class EspObj:
                def __init__(self, nom):
                    self.nombre = nom
            return [EspObj(c) for c in self.codes]
        def filter(self, **kwargs):
            class FilterResult:
                def __init__(self, match):
                    self._match = match
                def exists(self):
                    return self._match
            code = kwargs.get('codigo') or kwargs.get('nombre__icontains')
            return FilterResult(any(code.lower() in c.lower() for c in self.codes))

    class MockCountRel:
        def __init__(self, count):
            self._count = count
        def filter(self, **kwargs):
            return self
        def count(self):
            return self._count

    class MockPsicologo:
        def __init__(self, id_str, nombre, especialidades, bloques_disp, pacientes_activos, max_cap, modalidad):
            self.id = id_str
            self.usuario = MockUsuario(nombre, f"{nombre.lower()}@sigepsi.bo")
            self.numero_colegiado = f"COL-{id_str}"
            self.especialidades = MockEspecialidadRel(especialidades)
            self.horarios_disponibilidad = MockCountRel(bloques_disp)
            self.pacientes_asignados = MockCountRel(pacientes_activos)
            self.carga_maxima_pacientes = max_cap
            self.modalidad = modalidad

    p1 = MockPsicologo("1", "Dra. Elena Ramos", ["ANSIEDAD_FOBIAS"], bloques_disp=8, pacientes_activos=5, max_cap=20, modalidad="MIXTA")
    p2 = MockPsicologo("2", "Dr. Carlos Mendez", ["DEPRESION_ANIMO"], bloques_disp=6, pacientes_activos=3, max_cap=20, modalidad="VIRTUAL")
    p3 = MockPsicologo("3", "Lic. Sofia Castro", ["ANSIEDAD_FOBIAS"], bloques_disp=2, pacientes_activos=19, max_cap=20, modalidad="PRESENCIAL") # casi saturada
    p4 = MockPsicologo("4", "Dr. Hugo Vaca (Saturado)", ["ANSIEDAD_FOBIAS"], bloques_disp=10, pacientes_activos=20, max_cap=20, modalidad="MIXTA") # 100% saturado

    candidatos = MatchingPsicologoService.sugerir_psicologos(
        especialidad_req="ANSIEDAD_FOBIAS",
        modalidad_req="VIRTUAL",
        psicologos_queryset=[p1, p2, p3, p4]
    )

    # Must return Top 3
    assert len(candidatos) <= 3
    # Top 1 should be Dra. Elena Ramos (has specialty, good availability, good capacity balance)
    assert candidatos[0]['psicologo_id'] == "1"
    assert candidatos[0]['score_compatibilidad'] >= 80.0
    assert candidatos[0]['factores']['afinidad_especialidad'] == 40.0

    # Hugo Vaca is 100% saturated (20/20), so his balance_carga must be 0.0
    saturated = [c for c in candidatos if c['psicologo_id'] == "4"]
    if saturated:
        assert saturated[0]['factores']['balance_carga'] == 0.0


if __name__ == "__main__":
    test_matching_psicologo_service_weights_and_hitl()
    print("ALL MATCHING TESTS PASSED [OK]")
