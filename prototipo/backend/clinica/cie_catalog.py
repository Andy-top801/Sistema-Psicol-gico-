# ==============================================================================
# MÓDULO: clinica/cie_catalog.py
# DESCRIPCIÓN: Catálogo estructurado de diagnósticos CIE-10 para salud mental
#              con buscador por código y descripción con ranking de relevancia.
# ==============================================================================

CIE10_MENTAL_HEALTH_CATALOG = [
    {"codigo": "F00", "descripcion": "Demencia en la enfermedad de Alzheimer"},
    {"codigo": "F01", "descripcion": "Demencia vascular"},
    {"codigo": "F03", "descripcion": "Demencia no especificada"},
    {"codigo": "F06.0", "descripcion": "Alucinosis orgánica"},
    {"codigo": "F06.4", "descripcion": "Trastorno de ansiedad orgánico"},
    {"codigo": "F10.0", "descripcion": "Intoxicación aguda por alcohol"},
    {"codigo": "F10.2", "descripcion": "Síndrome de dependencia del alcohol"},
    {"codigo": "F11.2", "descripcion": "Trastornos mentales y del comportamiento debidos al consumo de opioides"},
    {"codigo": "F12.2", "descripcion": "Trastornos mentales y del comportamiento debidos al consumo de cannabinoides"},
    {"codigo": "F19.2", "descripcion": "Trastornos debidos al consumo de múltiples sustancias psicotrópicas"},
    {"codigo": "F20.0", "descripcion": "Esquizofrenia paranoide"},
    {"codigo": "F20.1", "descripcion": "Esquizofrenia hebefrénica"},
    {"codigo": "F20.3", "descripcion": "Esquizofrenia indiferenciada"},
    {"codigo": "F22.0", "descripcion": "Trastorno delirante persistente"},
    {"codigo": "F25.0", "descripcion": "Trastorno esquizoafectivo de tipo maníaco"},
    {"codigo": "F25.1", "descripcion": "Trastorno esquizoafectivo de tipo depresivo"},
    {"codigo": "F30.0", "descripcion": "Hipomanía"},
    {"codigo": "F31.0", "descripcion": "Trastorno bipolar, episodio actual hipomaníaco"},
    {"codigo": "F31.1", "descripcion": "Trastorno bipolar, episodio actual maníaco sin síntomas psicóticos"},
    {"codigo": "F31.3", "descripcion": "Trastorno bipolar, episodio actual depresivo leve o moderado"},
    {"codigo": "F31.4", "descripcion": "Trastorno bipolar, episodio actual depresivo grave sin síntomas psicóticos"},
    {"codigo": "F32.0", "descripcion": "Episodio depresivo leve"},
    {"codigo": "F32.1", "descripcion": "Episodio depresivo moderado"},
    {"codigo": "F32.2", "descripcion": "Episodio depresivo grave sin síntomas psicóticos"},
    {"codigo": "F32.3", "descripcion": "Episodio depresivo grave con síntomas psicóticos"},
    {"codigo": "F33.0", "descripcion": "Trastorno depresivo recurrente, episodio actual leve"},
    {"codigo": "F33.1", "descripcion": "Trastorno depresivo recurrente, episodio actual moderado"},
    {"codigo": "F33.2", "descripcion": "Trastorno depresivo recurrente, episodio actual grave"},
    {"codigo": "F34.1", "descripcion": "Distimia (Trastorno depresivo persistente)"},
    {"codigo": "F40.0", "descripcion": "Agorafobia"},
    {"codigo": "F40.1", "descripcion": "Fobias sociales (Trastorno de ansiedad social)"},
    {"codigo": "F40.2", "descripcion": "Fobias específicas (aisladas)"},
    {"codigo": "F41.0", "descripcion": "Trastorno de pánico (ansiedad paroxística episódica)"},
    {"codigo": "F41.1", "descripcion": "Trastorno de ansiedad generalizada (TAG)"},
    {"codigo": "F41.2", "descripcion": "Trastorno mixto ansioso-depresivo"},
    {"codigo": "F42.0", "descripcion": "Trastorno obsesivo-compulsivo con predominio de pensamientos obsesivos"},
    {"codigo": "F42.1", "descripcion": "Trastorno obsesivo-compulsivo con predominio de actos compulsivos"},
    {"codigo": "F42.2", "descripcion": "Trastorno obsesivo-compulsivo con actos y pensamientos obsesivos mixtos"},
    {"codigo": "F43.0", "descripcion": "Reacción a estrés agudo"},
    {"codigo": "F43.1", "descripcion": "Trastorno de estrés postraumático (TEPT)"},
    {"codigo": "F43.2", "descripcion": "Trastornos de adaptación (con reacción depresiva o ansiosa)"},
    {"codigo": "F45.0", "descripcion": "Trastorno de somatización"},
    {"codigo": "F48.0", "descripcion": "Neurastenia / Fatiga crónica psicológica"},
    {"codigo": "F50.0", "descripcion": "Anorexia nerviosa"},
    {"codigo": "F50.2", "descripcion": "Bulimia nerviosa"},
    {"codigo": "F50.8", "descripcion": "Trastorno por atracón y otros trastornos de la conducta alimentaria"},
    {"codigo": "F51.0", "descripcion": "Insomnio no orgánico"},
    {"codigo": "F51.1", "descripcion": "Hipersomnio no orgánico"},
    {"codigo": "F52.0", "descripcion": "Falta o pérdida del deseo sexual"},
    {"codigo": "F60.0", "descripcion": "Trastorno paranoide de la personalidad"},
    {"codigo": "F60.1", "descripcion": "Trastorno esquizoide de la personalidad"},
    {"codigo": "F60.2", "descripcion": "Trastorno disocial de la personalidad"},
    {"codigo": "F60.3", "descripcion": "Trastorno de inestabilidad emocional de la personalidad (tipo límite / borderline)"},
    {"codigo": "F60.4", "descripcion": "Trastorno histriónico de la personalidad"},
    {"codigo": "F60.5", "descripcion": "Trastorno anancástico (obsesivo) de la personalidad"},
    {"codigo": "F60.6", "descripcion": "Trastorno ansioso (con conducta de evitación) de la personalidad"},
    {"codigo": "F60.7", "descripcion": "Trastorno dependiente de la personalidad"},
    {"codigo": "F84.0", "descripcion": "Autismo en la niñez (Trastorno del espectro autista)"},
    {"codigo": "F84.5", "descripcion": "Síndrome de Asperger"},
    {"codigo": "F90.0", "descripcion": "Perturbación de la actividad y de la atención (TDAH combinado)"},
    {"codigo": "F90.1", "descripcion": "Trastorno hipercinético de la conducta"},
    {"codigo": "F91.0", "descripcion": "Trastorno disocial limitado al contexto familiar"},
    {"codigo": "F91.3", "descripcion": "Trastorno de oposición desafiante (TOD)"},
    {"codigo": "F93.0", "descripcion": "Trastorno de ansiedad por separación en la infancia"},
    {"codigo": "F94.0", "descripcion": "Mutismo selectivo"},
    {"codigo": "F98.0", "descripcion": "Enuresis no orgánica"},
    {"codigo": "Z63.0", "descripcion": "Problemas en la relación con el cónyuge o pareja"},
    {"codigo": "Z63.4", "descripcion": "Desaparición y defunción de un miembro de la familia (Duelo no complicado)"},
    {"codigo": "Z73.0", "descripcion": "Síndrome de agotamiento profesional (Burnout)"},
    {"codigo": "R45.8", "descripcion": "Ideación suicida / Otros síntomas que involucran el estado emocional"}
]

def search_cie10(query: str, limit: int = 20):
    """Busca en el catálogo por código o texto, priorizando coincidencias exactas."""
    if not query:
        return CIE10_MENTAL_HEALTH_CATALOG[:limit]
    
    q = query.strip().lower()
    exact_matches = []
    starts_matches = []
    contains_matches = []

    for item in CIE10_MENTAL_HEALTH_CATALOG:
        cod = item["codigo"].lower()
        desc = item["descripcion"].lower()

        if cod == q:
            exact_matches.append(item)
        elif cod.startswith(q) or desc.startswith(q):
            starts_matches.append(item)
        elif q in cod or q in desc:
            contains_matches.append(item)

    results = exact_matches + starts_matches + contains_matches
    # Deduplicar preservando orden
    seen = set()
    deduped = []
    for r in results:
        if r["codigo"] not in seen:
            seen.add(r["codigo"])
            deduped.append(r)
            if len(deduped) >= limit:
                break
    return deduped
