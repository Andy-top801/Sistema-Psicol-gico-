import win32com.client
import os
import sys

def add_or_get_package(parent, name):
    for i in range(parent.Packages.Count):
        p = parent.Packages.GetAt(i)
        if p.Name.strip().lower() == name.strip().lower():
            return p
    pkg = parent.Packages.AddNew(name, "")
    pkg.Update()
    parent.Packages.Refresh()
    return pkg

def add_or_get_diagram(package, name, diag_type):
    for i in range(package.Diagrams.Count):
        d = package.Diagrams.GetAt(i)
        if d.Name.strip().lower() == name.strip().lower():
            return d
    diag = package.Diagrams.AddNew(name, diag_type)
    diag.Update()
    package.Diagrams.Refresh()
    return diag

def add_element(package, name, elem_type, stereotype="", subtype=0):
    elem = package.Elements.AddNew(name, elem_type)
    if stereotype:
        elem.Stereotype = stereotype
    if subtype:
        elem.Subtype = subtype
    elem.Update()
    package.Elements.Refresh()
    return elem

def add_to_diagram(diagram, elem, left, top, right, bottom):
    pos_str = f"l={left};r={right};t={top};b={bottom};"
    do = diagram.DiagramObjects.AddNew(pos_str, "")
    do.ElementID = elem.ElementID
    do.left = int(left)
    do.top = int(top)
    do.right = int(right)
    do.bottom = int(bottom)
    do.Update()
    diagram.DiagramObjects.Refresh()
    return do

def add_connector(source_elem, target_elem, conn_type, name="", stereotype="", client_card="", supplier_card="", supplier_agg=0):
    conn = source_elem.Connectors.AddNew(name, conn_type)
    conn.SupplierID = target_elem.ElementID
    if stereotype:
        conn.Stereotype = stereotype
    if client_card:
        conn.ClientEnd.Cardinality = client_card
    if supplier_card:
        conn.SupplierEnd.Cardinality = supplier_card
    if supplier_agg:
        conn.SupplierEnd.Aggregation = supplier_agg
    conn.Update()
    source_elem.Connectors.Refresh()
    return conn

def add_attributes_and_methods(elem, attributes, methods=None):
    for attr_name, attr_type in attributes:
        attr = elem.Attributes.AddNew(attr_name, attr_type)
        attr.Update()
    elem.Attributes.Refresh()
    if methods:
        for m_name, m_ret in methods:
            m = elem.Methods.AddNew(m_name, m_ret)
            m.Update()
        elem.Methods.Refresh()

def build_usecase_diagram(sp2_pkg, ea_repo):
    print("Building 1. Casos de Uso - Sprint 2...")
    pkg = add_or_get_package(sp2_pkg, "1. Casos de Uso - Sprint 2")
    diag = add_or_get_diagram(pkg, "Diagrama de Casos de Uso - Sprint 2 Incremental Acumulado", "Use Case")
    
    # 1. Actors
    actors = {}
    actor_defs = [
        ("SuperAdministrador\n(Plataforma)", 40, -40, 150, -140),
        ("Administrador del Centro", 40, -180, 150, -280),
        ("Coordinador Clínico", 40, -320, 150, -420),
        ("Recepcionista", 40, -460, 150, -560),
        ("Psicólogo", 1250, -200, 1360, -300),
        ("Paciente\n(Web / Móvil)", 1250, -480, 1360, -580),
    ]
    for name, l, t, r, b in actor_defs:
        elem = add_element(pkg, name, "Actor")
        add_to_diagram(diag, elem, l, t, r, b)
        actors[name.split("\n")[0].strip()] = elem

    # 2. Boundaries for visual grouping
    b_sp0 = add_element(pkg, "Incremento Sprint 0: Multi-Tenant & Acceso", "Boundary", stereotype="rectangle")
    add_to_diagram(diag, b_sp0, 200, -30, 690, -320)
    
    b_sp1 = add_element(pkg, "Incremento Sprint 1: Atención Clínica, Agenda & Teleconsulta", "Boundary", stereotype="rectangle")
    add_to_diagram(diag, b_sp1, 200, -340, 690, -710)
    
    b_sp2 = add_element(pkg, "Incremento Sprint 2: Historia Clínica, Intake, Notas & Consentimientos", "Boundary", stereotype="rectangle")
    add_to_diagram(diag, b_sp2, 730, -30, 1210, -710)

    # 3. Use Cases
    ucs = {}
    uc_defs = [
        # Sprint 0
        ("CU1", "CU1: Gestionar centros psicológicos\ny configuración Multi-Tenant", 230, -70, 430, -140),
        ("CU2", "CU2: Autenticar e iniciar sesión (JWT)", 470, -70, 660, -140),
        ("CU3", "CU3: Gestionar usuarios institucionales", 230, -160, 430, -220),
        ("CU4", "CU4: Gestionar roles y permisos (RBAC)", 470, -160, 660, -220),
        ("CU27", "CU27: Recuperar credenciales y contraseña", 350, -240, 550, -300),
        # Sprint 1
        ("CU6", "CU6: Gestionar psicólogos y perfiles", 230, -380, 430, -440),
        ("CU8", "CU8: Configurar disponibilidad horaria", 470, -380, 660, -440),
        ("CU7", "CU7: Gestionar expediente de pacientes", 230, -460, 430, -520),
        ("CU11", "CU11: Gestionar citas y agenda", 470, -460, 660, -520),
        ("CU13", "CU13: Realizar teleconsulta (Jitsi Meet)", 230, -540, 430, -600),
        ("CU9", "CU9: Consultar Dashboard e indicadores", 470, -540, 660, -600),
        ("CU10", "CU10: Gestionar alertas de priorización", 350, -620, 550, -680),
        # Sprint 2
        ("CU14", "CU14: Gestionar formulario previo\na la consulta (Intake Digital)", 760, -70, 960, -140),
        ("CU15", "CU15: Gestionar historia clínica\npsicológica electrónica", 990, -70, 1190, -140),
        ("CU16", "CU16: Registrar y gestionar\nnotas de sesión (Modelo SOAP)", 760, -180, 960, -250),
        ("CU17", "CU17: Gestionar evolución, tareas\ny seguimiento terapéutico", 990, -180, 1190, -250),
        ("CU18", "CU18: Gestionar consentimientos\ninformados y autorizaciones", 760, -290, 960, -360),
        ("CU19", "CU19: Gestionar cierre y\nderivación médica a Psiquiatría", 990, -290, 1190, -360),
        ("val_rbac", "Validar acceso confidencial RBAC", 990, -410, 1190, -470),
        ("val_hash", "Sellado de tiempo criptográfico SHA-256", 760, -410, 960, -470),
    ]
    for key, name, l, t, r, b in uc_defs:
        elem = add_element(pkg, name, "UseCase")
        add_to_diagram(diag, elem, l, t, r, b)
        ucs[key] = elem

    # 4. Actor Associations
    assocs = [
        ("SuperAdministrador", "CU1"),
        ("Administrador del Centro", "CU2"),
        ("Administrador del Centro", "CU3"),
        ("Administrador del Centro", "CU4"),
        ("Administrador del Centro", "CU6"),
        ("Administrador del Centro", "CU7"),
        ("Administrador del Centro", "CU9"),
        ("Administrador del Centro", "CU18"),
        ("Coordinador Clínico", "CU2"),
        ("Coordinador Clínico", "CU6"),
        ("Coordinador Clínico", "CU9"),
        ("Coordinador Clínico", "CU10"),
        ("Coordinador Clínico", "CU14"),
        ("Coordinador Clínico", "CU15"),
        ("Coordinador Clínico", "CU19"),
        ("Psicólogo", "CU2"),
        ("Psicólogo", "CU8"),
        ("Psicólogo", "CU11"),
        ("Psicólogo", "CU13"),
        ("Psicólogo", "CU14"),
        ("Psicólogo", "CU15"),
        ("Psicólogo", "CU16"),
        ("Psicólogo", "CU17"),
        ("Psicólogo", "CU19"),
        ("Recepcionista", "CU2"),
        ("Recepcionista", "CU7"),
        ("Recepcionista", "CU11"),
        ("Paciente", "CU2"),
        ("Paciente", "CU27"),
        ("Paciente", "CU7"),
        ("Paciente", "CU11"),
        ("Paciente", "CU13"),
        ("Paciente", "CU14"),
        ("Paciente", "CU17"),
        ("Paciente", "CU18"),
    ]
    for act_key, uc_key in assocs:
        if act_key in actors and uc_key in ucs:
            add_connector(actors[act_key], ucs[uc_key], "Association")

    # 5. Includes
    includes = [
        ("CU15", "val_rbac"),
        ("CU18", "val_hash"),
        ("CU14", "CU2"),
        ("CU15", "CU2"),
        ("CU16", "CU2"),
        ("CU17", "CU2"),
        ("CU18", "CU2"),
        ("CU19", "CU2"),
    ]
    for src, tgt in includes:
        if src in ucs and tgt in ucs:
            add_connector(ucs[src], ucs[tgt], "UseCase", name="", stereotype="include")

    diag.Update()
    ea_repo.ReloadDiagram(diag.DiagramID)
    print("Casos de Uso diagram completed successfully.")

def build_class_diagram(sp2_pkg, ea_repo):
    print("Building 2. Clases - Sprint 2...")
    pkg = add_or_get_package(sp2_pkg, "2. Clases - Sprint 2")
    diag = add_or_get_diagram(pkg, "Diagrama de Clases - Sprint 2 Dominio Clínico", "Logical")

    # Visual Packages / Boundaries
    b_pub = add_element(pkg, "Esquema Public (Global - Consolidado Sprint 0)", "Boundary", stereotype="package")
    add_to_diagram(diag, b_pub, 50, -30, 660, -250)

    b_tenant_base = add_element(pkg, "Esquema Tenant (Entidades Base - Sprints 0 y 1)", "Boundary", stereotype="package")
    add_to_diagram(diag, b_tenant_base, 50, -280, 660, -820)

    b_tenant_sp2 = add_element(pkg, "Esquema Tenant (Incremento Clínico - Sprint 2)", "Boundary", stereotype="package")
    add_to_diagram(diag, b_tenant_sp2, 700, -30, 1500, -1530)

    classes = {}
    
    # 1. Public Schema
    c_tenant = add_element(pkg, "Tenant", "Class")
    add_attributes_and_methods(c_tenant, [
        ("id", "UUID"),
        ("nombre", "String"),
        ("slug", "String"),
        ("schema_name", "String"),
        ("plan", "String"),
        ("activo", "Boolean"),
        ("fecha_creacion", "DateTime")
    ], [
        ("crear_esquema", "void"),
        ("suspender", "void")
    ])
    add_to_diagram(diag, c_tenant, 80, -70, 330, -220)
    classes["Tenant"] = c_tenant

    c_dominio = add_element(pkg, "Dominio", "Class")
    add_attributes_and_methods(c_dominio, [
        ("id", "Integer"),
        ("dominio", "String"),
        ("es_primario", "Boolean")
    ])
    add_to_diagram(diag, c_dominio, 400, -90, 620, -190)
    classes["Dominio"] = c_dominio

    # 2. Base Tenant Schema
    c_usuario = add_element(pkg, "Usuario", "Class")
    add_attributes_and_methods(c_usuario, [
        ("id", "UUID"),
        ("email", "String"),
        ("rol", "String"),
        ("is_active", "Boolean")
    ], [
        ("verificar_credenciales", "void")
    ])
    add_to_diagram(diag, c_usuario, 80, -320, 320, -450)
    classes["Usuario"] = c_usuario

    c_psicologo = add_element(pkg, "Psicologo", "Class")
    add_attributes_and_methods(c_psicologo, [
        ("id", "UUID"),
        ("numero_colegiado", "String"),
        ("modalidad", "String"),
        ("tarifa_base", "Decimal"),
        ("activo", "Boolean")
    ])
    add_to_diagram(diag, c_psicologo, 400, -320, 620, -470)
    classes["Psicologo"] = c_psicologo

    c_paciente = add_element(pkg, "Paciente", "Class")
    add_attributes_and_methods(c_paciente, [
        ("id", "UUID"),
        ("codigo_expediente", "String"),
        ("ci", "String"),
        ("fecha_nacimiento", "Date"),
        ("contacto_emergencia_nombre", "String"),
        ("contacto_emergencia_telf", "String")
    ])
    add_to_diagram(diag, c_paciente, 80, -520, 340, -690)
    classes["Paciente"] = c_paciente

    c_cita = add_element(pkg, "Cita", "Class")
    add_attributes_and_methods(c_cita, [
        ("id", "UUID"),
        ("fecha", "Date"),
        ("hora_inicio", "Time"),
        ("hora_fin", "Time"),
        ("modalidad", "String"),
        ("estado", "String")
    ])
    add_to_diagram(diag, c_cita, 400, -530, 620, -680)
    classes["Cita"] = c_cita

    # 3. Sprint 2 Entities
    c_form = add_element(pkg, "FormularioPreConsulta", "Class")
    add_attributes_and_methods(c_form, [
        ("id", "UUID"),
        ("titulo", "String"),
        ("version", "String"),
        ("activo", "Boolean"),
        ("preguntas_schema", "JSONB")
    ])
    add_to_diagram(diag, c_form, 730, -70, 1020, -210)
    classes["FormularioPreConsulta"] = c_form

    c_resp = add_element(pkg, "RespuestaPreConsulta", "Class")
    add_attributes_and_methods(c_resp, [
        ("id", "UUID"),
        ("motivo_consulta", "Text"),
        ("nivel_urgencia", "Integer"),
        ("respuestas_detalle", "JSONB"),
        ("estado", "String"),
        ("fecha_envio", "DateTime")
    ])
    add_to_diagram(diag, c_resp, 1100, -70, 1400, -230)
    classes["RespuestaPreConsulta"] = c_resp

    c_hc = add_element(pkg, "HistoriaClinica", "Class")
    add_attributes_and_methods(c_hc, [
        ("id", "UUID"),
        ("codigo_historia", "String"),
        ("motivo_consulta_inicial", "Text"),
        ("antecedentes_personales", "Text"),
        ("antecedentes_familiares", "Text"),
        ("examen_mental", "Text"),
        ("plan_tratamiento", "Text"),
        ("fecha_apertura", "DateTime"),
        ("cerrada", "Boolean")
    ])
    add_to_diagram(diag, c_hc, 730, -280, 1040, -510)
    classes["HistoriaClinica"] = c_hc

    c_cie = add_element(pkg, "DiagnosticoCIE", "Class")
    add_attributes_and_methods(c_cie, [
        ("id", "Integer"),
        ("codigo_cie", "String"),
        ("descripcion", "String"),
        ("tipo", "String"),
        ("fecha_diagnostico", "Date")
    ])
    add_to_diagram(diag, c_cie, 1100, -290, 1380, -450)
    classes["DiagnosticoCIE"] = c_cie

    c_nota = add_element(pkg, "NotaSesion", "Class")
    add_attributes_and_methods(c_nota, [
        ("id", "UUID"),
        ("numero_sesion", "Integer"),
        ("fecha_sesion", "DateTime"),
        ("subjetivo", "Text"),
        ("objetivo", "Text"),
        ("analisis", "Text"),
        ("plan", "Text"),
        ("tecnicas_aplicadas", "String"),
        ("estado_guardado", "String")
    ])
    add_to_diagram(diag, c_nota, 730, -560, 1040, -780)
    classes["NotaSesion"] = c_nota

    c_evoc = add_element(pkg, "EvolucionClinica", "Class")
    add_attributes_and_methods(c_evoc, [
        ("id", "UUID"),
        ("estado_avance", "String"),
        ("justificacion", "Text"),
        ("acuerdos_pactados", "Text"),
        ("fecha_registro", "DateTime")
    ])
    add_to_diagram(diag, c_evoc, 1100, -560, 1380, -720)
    classes["EvolucionClinica"] = c_evoc

    c_deriv = add_element(pkg, "DerivacionCaso", "Class")
    add_attributes_and_methods(c_deriv, [
        ("id", "UUID"),
        ("tipo_derivacion", "String"),
        ("motivo_clinico", "Text"),
        ("sintomatologia_relevante", "Text"),
        ("profesional_destino", "String"),
        ("institucion_destino", "String"),
        ("nivel_riesgo", "String"),
        ("fecha_derivacion", "DateTime"),
        ("aceptada", "Boolean")
    ])
    add_to_diagram(diag, c_deriv, 1100, -760, 1420, -970)
    classes["DerivacionCaso"] = c_deriv

    c_tarea = add_element(pkg, "TareaTerapeutica", "Class")
    add_attributes_and_methods(c_tarea, [
        ("id", "UUID"),
        ("titulo", "String"),
        ("descripcion", "Text"),
        ("categoria", "String"),
        ("fecha_limite", "Date"),
        ("estado", "String"),
        ("archivo_adjunto_url", "String")
    ])
    add_to_diagram(diag, c_tarea, 730, -840, 1040, -1030)
    classes["TareaTerapeutica"] = c_tarea

    c_evid = add_element(pkg, "EvidenciaTarea", "Class")
    add_attributes_and_methods(c_evid, [
        ("id", "UUID"),
        ("texto_reflexion", "Text"),
        ("dificultad_percibida", "Integer"),
        ("archivo_evidencia_url", "String"),
        ("fecha_cumplimiento", "DateTime")
    ])
    add_to_diagram(diag, c_evid, 1100, -1020, 1400, -1190)
    classes["EvidenciaTarea"] = c_evid

    c_consent = add_element(pkg, "ConsentimientoInformado", "Class")
    add_attributes_and_methods(c_consent, [
        ("id", "UUID"),
        ("titulo", "String"),
        ("tipo", "String"),
        ("contenido_legal", "Text"),
        ("version", "String"),
        ("activo", "Boolean")
    ])
    add_to_diagram(diag, c_consent, 730, -1090, 1040, -1250)
    classes["ConsentimientoInformado"] = c_consent

    c_firma = add_element(pkg, "FirmaConsentimiento", "Class")
    add_attributes_and_methods(c_firma, [
        ("id", "UUID"),
        ("firmado_por", "String"),
        ("es_menor_edad", "Boolean"),
        ("tutor_nombre", "String"),
        ("tutor_ci", "String"),
        ("hash_sha256", "String"),
        ("ip_origen", "String"),
        ("user_agent", "String"),
        ("fecha_firma", "DateTime"),
        ("firma_canvas_url", "String")
    ])
    add_to_diagram(diag, c_firma, 1100, -1250, 1420, -1490)
    classes["FirmaConsentimiento"] = c_firma

    # Connectors
    # Tenant *-- Dominio (Composition: supplier_agg=2)
    add_connector(classes["Tenant"], classes["Dominio"], "Aggregation", client_card="1", supplier_card="*", supplier_agg=2)
    
    # Usuario <-- Psicologo / Paciente
    add_connector(classes["Psicologo"], classes["Usuario"], "Association", client_card="1", supplier_card="1")
    add_connector(classes["Paciente"], classes["Usuario"], "Association", client_card="1", supplier_card="1")

    # Paciente *-- HistoriaClinica
    add_connector(classes["Paciente"], classes["HistoriaClinica"], "Aggregation", client_card="1", supplier_card="1", supplier_agg=2)

    # HistoriaClinica *-- DiagnosticoCIE, NotaSesion, EvolucionClinica, DerivacionCaso
    add_connector(classes["HistoriaClinica"], classes["DiagnosticoCIE"], "Aggregation", client_card="1", supplier_card="*", supplier_agg=2)
    add_connector(classes["HistoriaClinica"], classes["NotaSesion"], "Aggregation", client_card="1", supplier_card="*", supplier_agg=2)
    add_connector(classes["HistoriaClinica"], classes["EvolucionClinica"], "Aggregation", client_card="1", supplier_card="*", supplier_agg=2)
    add_connector(classes["HistoriaClinica"], classes["DerivacionCaso"], "Aggregation", client_card="1", supplier_card="*", supplier_agg=2)

    # NotaSesion --> Cita (documenta)
    add_connector(classes["NotaSesion"], classes["Cita"], "Association", name="documenta", client_card="0..1", supplier_card="1")

    # Paciente *-- RespuestaPreConsulta
    add_connector(classes["Paciente"], classes["RespuestaPreConsulta"], "Aggregation", client_card="1", supplier_card="*", supplier_agg=2)

    # FormularioPreConsulta <-- RespuestaPreConsulta
    add_connector(classes["RespuestaPreConsulta"], classes["FormularioPreConsulta"], "Association", client_card="*", supplier_card="1")

    # Psicologo *-- TareaTerapeutica (asigna)
    add_connector(classes["Psicologo"], classes["TareaTerapeutica"], "Aggregation", name="asigna", client_card="1", supplier_card="*", supplier_agg=2)

    # Paciente *-- TareaTerapeutica (realiza)
    add_connector(classes["Paciente"], classes["TareaTerapeutica"], "Association", name="realiza", client_card="1", supplier_card="*")

    # TareaTerapeutica *-- EvidenciaTarea
    add_connector(classes["TareaTerapeutica"], classes["EvidenciaTarea"], "Aggregation", client_card="1", supplier_card="0..1", supplier_agg=2)

    # ConsentimientoInformado <-- FirmaConsentimiento
    add_connector(classes["FirmaConsentimiento"], classes["ConsentimientoInformado"], "Association", client_card="*", supplier_card="1")

    # Paciente *-- FirmaConsentimiento
    add_connector(classes["Paciente"], classes["FirmaConsentimiento"], "Aggregation", client_card="1", supplier_card="*", supplier_agg=2)

    diag.Update()
    ea_repo.ReloadDiagram(diag.DiagramID)
    print("Clases diagram completed successfully.")

def build_activity_intake(sp2_pkg, ea_repo):
    print("Building 3. Actividad - Formulario Previo e Historia Clínica...")
    pkg = add_or_get_package(sp2_pkg, "3. Actividad - Formulario Previo e Historia Clínica")
    diag = add_or_get_diagram(pkg, "Diagrama de Actividad - Intake y Apertura HC", "Activity")

    # 3 Lanes (Boundaries)
    lane1 = add_element(pkg, "Paciente (Móvil / Web)", "Boundary", stereotype="swimlane")
    add_to_diagram(diag, lane1, 40, -20, 420, -1000)

    lane2 = add_element(pkg, "Backend Django REST", "Boundary", stereotype="swimlane")
    add_to_diagram(diag, lane2, 440, -20, 820, -1000)

    lane3 = add_element(pkg, "Psicólogo (Web Angular)", "Boundary", stereotype="swimlane")
    add_to_diagram(diag, lane3, 840, -20, 1220, -1000)

    # Lane 1 Elements (Paciente)
    start_node = add_element(pkg, "", "StateNode", subtype=100)
    add_to_diagram(diag, start_node, 220, -50, 240, -70)

    a1 = add_element(pkg, "Selecciona 'Completar Formulario Previo'", "Activity")
    add_to_diagram(diag, a1, 80, -100, 380, -150)

    a2 = add_element(pkg, "Lee instrucciones y preguntas clínicas", "Activity")
    add_to_diagram(diag, a2, 80, -180, 380, -230)

    a3 = add_element(pkg, "Ingresa motivo de consulta y síntomas", "Activity")
    add_to_diagram(diag, a3, 80, -260, 380, -310)

    a4 = add_element(pkg, "Selecciona nivel de malestar (Escala 1-5)", "Activity")
    add_to_diagram(diag, a4, 80, -340, 380, -390)

    a5 = add_element(pkg, "Detalla antecedentes médicos y psicológicos", "Activity")
    add_to_diagram(diag, a5, 80, -420, 380, -470)

    dec1 = add_element(pkg, "¿Campos obligatorios válidos?", "Decision")
    add_to_diagram(diag, dec1, 190, -500, 270, -550)

    a6 = add_element(pkg, "Presiona 'Enviar Formulario'", "Activity")
    add_to_diagram(diag, a6, 80, -580, 380, -630)

    # Lane 2 Elements (Backend)
    a7 = add_element(pkg, "Valida esquema JSON y tipos de datos", "Activity")
    add_to_diagram(diag, a7, 480, -580, 780, -630)

    a8 = add_element(pkg, "Calcula bandera de atención prioritaria si Malestar >= 4", "Activity")
    add_to_diagram(diag, a8, 480, -660, 780, -720)

    a9 = add_element(pkg, "Persiste registro en tabla clinica_respuestapreconsulta", "Activity")
    add_to_diagram(diag, a9, 480, -750, 780, -800)

    a10 = add_element(pkg, "Notifica al Esquema Tenant del Centro", "Activity")
    add_to_diagram(diag, a10, 480, -830, 780, -880)

    # Lane 3 Elements (Psicólogo)
    a11 = add_element(pkg, "Abre expediente del paciente", "Activity")
    add_to_diagram(diag, a11, 880, -580, 1180, -630)

    a12 = add_element(pkg, "Visualiza datos de pre-consulta e intake", "Activity")
    add_to_diagram(diag, a12, 880, -660, 1180, -710)

    a13 = add_element(pkg, "Presiona 'Abrir Historia Clínica'", "Activity")
    add_to_diagram(diag, a13, 880, -740, 1180, -790)

    a14 = add_element(pkg, "Asocia respuestas iniciales a la anamnesis", "Activity")
    add_to_diagram(diag, a14, 880, -820, 1180, -870)

    a15 = add_element(pkg, "Registra diagnóstico presuntivo CIE y metas", "Activity")
    add_to_diagram(diag, a15, 880, -900, 1180, -950)

    a16 = add_element(pkg, "Guarda Historia Clínica Electrónica", "Activity")
    add_to_diagram(diag, a16, 880, -980, 1180, -1030)

    stop_node = add_element(pkg, "", "StateNode", subtype=101)
    add_to_diagram(diag, stop_node, 1020, -1060, 1040, -1080)

    # Adjust lane height
    lane1_do = diag.DiagramObjects.GetAt(0)
    lane1_do.bottom = -1120
    lane1_do.Update()
    lane2_do = diag.DiagramObjects.GetAt(1)
    lane2_do.bottom = -1120
    lane2_do.Update()
    lane3_do = diag.DiagramObjects.GetAt(2)
    lane3_do.bottom = -1120
    lane3_do.Update()

    # Connectors (ControlFlow)
    add_connector(start_node, a1, "ControlFlow")
    add_connector(a1, a2, "ControlFlow")
    add_connector(a2, a3, "ControlFlow")
    add_connector(a3, a4, "ControlFlow")
    add_connector(a4, a5, "ControlFlow")
    add_connector(a5, dec1, "ControlFlow")
    add_connector(dec1, a3, "ControlFlow", name="No")
    add_connector(dec1, a6, "ControlFlow", name="Sí")
    add_connector(a6, a7, "ControlFlow")
    add_connector(a7, a8, "ControlFlow")
    add_connector(a8, a9, "ControlFlow")
    add_connector(a9, a10, "ControlFlow")
    add_connector(a10, a11, "ControlFlow")
    add_connector(a11, a12, "ControlFlow")
    add_connector(a12, a13, "ControlFlow")
    add_connector(a13, a14, "ControlFlow")
    add_connector(a14, a15, "ControlFlow")
    add_connector(a15, a16, "ControlFlow")
    add_connector(a16, stop_node, "ControlFlow")

    diag.Update()
    ea_repo.ReloadDiagram(diag.DiagramID)
    print("Actividad Intake diagram completed successfully.")

def build_activity_tareas(sp2_pkg, ea_repo):
    print("Building 4. Actividad - Tareas Terapéuticas...")
    pkg = add_or_get_package(sp2_pkg, "4. Actividad - Tareas Terapéuticas")
    diag = add_or_get_diagram(pkg, "Diagrama de Actividad - Ciclo Tareas Terapéuticas", "Activity")

    # 3 Lanes
    lane1 = add_element(pkg, "Psicólogo (Web Angular)", "Boundary", stereotype="swimlane")
    add_to_diagram(diag, lane1, 40, -20, 420, -1100)

    lane2 = add_element(pkg, "Backend Django REST", "Boundary", stereotype="swimlane")
    add_to_diagram(diag, lane2, 440, -20, 820, -1100)

    lane3 = add_element(pkg, "Paciente (Móvil Flutter)", "Boundary", stereotype="swimlane")
    add_to_diagram(diag, lane3, 840, -20, 1220, -1100)

    # Lane 1 (Psicólogo inicial)
    start_node = add_element(pkg, "", "StateNode", subtype=100)
    add_to_diagram(diag, start_node, 220, -50, 240, -70)

    a1 = add_element(pkg, "Accede a la ficha del paciente post-sesión", "Activity")
    add_to_diagram(diag, a1, 80, -100, 380, -150)

    a2 = add_element(pkg, "Selecciona 'Asignar Tarea Terapéutica'", "Activity")
    add_to_diagram(diag, a2, 80, -180, 380, -230)

    a3 = add_element(pkg, "Define título, instrucciones y fecha límite", "Activity")
    add_to_diagram(diag, a3, 80, -260, 380, -310)

    a4 = add_element(pkg, "Adjunta guía en PDF o plantilla de autorregistro", "Activity")
    add_to_diagram(diag, a4, 80, -340, 380, -390)

    a5 = add_element(pkg, "Presiona 'Guardar Asignación'", "Activity")
    add_to_diagram(diag, a5, 80, -420, 380, -470)

    # Lane 2 (Backend 1)
    a6 = add_element(pkg, "Almacena tarea en clinica_tareaterapeutica", "Activity")
    add_to_diagram(diag, a6, 480, -420, 780, -470)

    a7 = add_element(pkg, "Emite evento de notificación WebSocket / Push", "Activity")
    add_to_diagram(diag, a7, 480, -500, 780, -550)

    # Lane 3 (Paciente)
    a8 = add_element(pkg, "Recibe notificación de nueva tarea", "Activity")
    add_to_diagram(diag, a8, 880, -500, 1180, -550)

    a9 = add_element(pkg, "Consulta detalle en 'Mis Tareas'", "Activity")
    add_to_diagram(diag, a9, 880, -580, 1180, -630)

    a10 = add_element(pkg, "Practica ejercicio (ej. Registro cognitivo)", "Activity")
    add_to_diagram(diag, a10, 880, -660, 1180, -710)

    a11 = add_element(pkg, "Presiona 'Reportar Cumplimiento'", "Activity")
    add_to_diagram(diag, a11, 880, -740, 1180, -790)

    a12 = add_element(pkg, "Ingresa notas de reflexión y nivel de dificultad", "Activity")
    add_to_diagram(diag, a12, 880, -820, 1180, -870)

    a13 = add_element(pkg, "Presiona 'Enviar Reporte'", "Activity")
    add_to_diagram(diag, a13, 880, -900, 1180, -950)

    # Lane 2 (Backend 2)
    a14 = add_element(pkg, "Registra evidencia en clinica_evidenciatarea", "Activity")
    add_to_diagram(diag, a14, 480, -900, 780, -950)

    a15 = add_element(pkg, "Actualiza estado de tarea a 'COMPLETADA'", "Activity")
    add_to_diagram(diag, a15, 480, -980, 780, -1030)

    # Lane 1 (Psicólogo cierre)
    a16 = add_element(pkg, "Visualiza reporte de tarea en la próxima sesión", "Activity")
    add_to_diagram(diag, a16, 80, -980, 380, -1030)

    a17 = add_element(pkg, "Brinda retroalimentación en la Nota SOAP", "Activity")
    add_to_diagram(diag, a17, 80, -1060, 380, -1110)

    stop_node = add_element(pkg, "", "StateNode", subtype=101)
    add_to_diagram(diag, stop_node, 220, -1140, 240, -1160)

    # Adjust lane height
    for i in range(3):
        lane_do = diag.DiagramObjects.GetAt(i)
        lane_do.bottom = -1200
        lane_do.Update()

    # Connectors
    add_connector(start_node, a1, "ControlFlow")
    add_connector(a1, a2, "ControlFlow")
    add_connector(a2, a3, "ControlFlow")
    add_connector(a3, a4, "ControlFlow")
    add_connector(a4, a5, "ControlFlow")
    add_connector(a5, a6, "ControlFlow")
    add_connector(a6, a7, "ControlFlow")
    add_connector(a7, a8, "ControlFlow")
    add_connector(a8, a9, "ControlFlow")
    add_connector(a9, a10, "ControlFlow")
    add_connector(a10, a11, "ControlFlow")
    add_connector(a11, a12, "ControlFlow")
    add_connector(a12, a13, "ControlFlow")
    add_connector(a13, a14, "ControlFlow")
    add_connector(a14, a15, "ControlFlow")
    add_connector(a15, a16, "ControlFlow")
    add_connector(a16, a17, "ControlFlow")
    add_connector(a17, stop_node, "ControlFlow")

    diag.Update()
    ea_repo.ReloadDiagram(diag.DiagramID)
    print("Actividad Tareas diagram completed successfully.")

def build_activity_derivacion(sp2_pkg, ea_repo):
    print("Building 5. Actividad - Derivación a Psiquiatría...")
    pkg = add_or_get_package(sp2_pkg, "5. Actividad - Derivación a Psiquiatría")
    diag = add_or_get_diagram(pkg, "Diagrama de Actividad - Protocolo Derivación Psiquiátrica", "Activity")

    # 3 Lanes
    lane1 = add_element(pkg, "Psicólogo Tratante (Web)", "Boundary", stereotype="swimlane")
    add_to_diagram(diag, lane1, 40, -20, 420, -900)

    lane2 = add_element(pkg, "Backend Django REST", "Boundary", stereotype="swimlane")
    add_to_diagram(diag, lane2, 440, -20, 820, -900)

    lane3 = add_element(pkg, "Coordinador Clínico (Web)", "Boundary", stereotype="swimlane")
    add_to_diagram(diag, lane3, 840, -20, 1220, -900)

    # Initial Node
    start_node = add_element(pkg, "", "StateNode", subtype=100)
    add_to_diagram(diag, start_node, 220, -50, 240, -70)

    a1 = add_element(pkg, "Evalúa sintomatología clínica en sesión", "Activity")
    add_to_diagram(diag, a1, 80, -100, 380, -150)

    dec1 = add_element(pkg, "¿Requiere farmacoterapia o evaluación médica?", "Decision")
    add_to_diagram(diag, dec1, 160, -180, 300, -240)

    # Branch Sí (Derivación)
    a2 = add_element(pkg, "Selecciona 'Derivación Médica a Psiquiatría'", "Activity")
    add_to_diagram(diag, a2, 80, -270, 380, -320)

    a3 = add_element(pkg, "Redacta motivo clínico de interconsulta", "Activity")
    add_to_diagram(diag, a3, 80, -350, 380, -400)

    a4 = add_element(pkg, "Detalla signos de riesgo psicopatológico", "Activity")
    add_to_diagram(diag, a4, 80, -430, 380, -480)

    a5 = add_element(pkg, "Genera orden de derivación oficial", "Activity")
    add_to_diagram(diag, a5, 80, -510, 380, -560)

    # Backend Django REST
    a6 = add_element(pkg, "Registra derivación en clinica_derivacioncaso", "Activity")
    add_to_diagram(diag, a6, 480, -510, 780, -560)

    a7 = add_element(pkg, "Calcula hash SHA-256 y compila PDF de referencia médica", "Activity")
    add_to_diagram(diag, a7, 480, -590, 780, -650)

    a8 = add_element(pkg, "Emite alerta de alta prioridad al Coordinador Clínico", "Activity")
    add_to_diagram(diag, a8, 480, -680, 780, -730)

    # Coordinador Clínico
    a9 = add_element(pkg, "Revisa resumen clínico y orden de derivación", "Activity")
    add_to_diagram(diag, a9, 880, -680, 1180, -730)

    a10 = add_element(pkg, "Coordina interconsulta con psiquiatra de enlace", "Activity")
    add_to_diagram(diag, a10, 880, -760, 1180, -810)

    a11 = add_element(pkg, "Confirma derivación en la plataforma", "Activity")
    add_to_diagram(diag, a11, 880, -840, 1180, -890)

    stop_deriv = add_element(pkg, "", "StateNode", subtype=101)
    add_to_diagram(diag, stop_deriv, 1020, -920, 1040, -940)

    # Branch No (Cierre ordinario) - In Lane 1 further right or separated
    a12 = add_element(pkg, "Aplica protocolo de Alta Terapéutica", "Activity")
    add_to_diagram(diag, a12, 80, -620, 380, -670)

    a13 = add_element(pkg, "Registra objetivos alcanzados y pautas de prevención", "Activity")
    add_to_diagram(diag, a13, 80, -700, 380, -750)

    a14 = add_element(pkg, "Cierra formalmente el caso en Historia Clínica", "Activity")
    add_to_diagram(diag, a14, 80, -780, 380, -830)

    stop_alta = add_element(pkg, "", "StateNode", subtype=101)
    add_to_diagram(diag, stop_alta, 220, -860, 240, -880)

    # Adjust lane height
    for i in range(3):
        lane_do = diag.DiagramObjects.GetAt(i)
        lane_do.bottom = -980
        lane_do.Update()

    # Connectors
    add_connector(start_node, a1, "ControlFlow")
    add_connector(a1, dec1, "ControlFlow")
    
    # Sí
    add_connector(dec1, a2, "ControlFlow", name="Sí")
    add_connector(a2, a3, "ControlFlow")
    add_connector(a3, a4, "ControlFlow")
    add_connector(a4, a5, "ControlFlow")
    add_connector(a5, a6, "ControlFlow")
    add_connector(a6, a7, "ControlFlow")
    add_connector(a7, a8, "ControlFlow")
    add_connector(a8, a9, "ControlFlow")
    add_connector(a9, a10, "ControlFlow")
    add_connector(a10, a11, "ControlFlow")
    add_connector(a11, stop_deriv, "ControlFlow")

    # No
    add_connector(dec1, a12, "ControlFlow", name="No - Cierre ordinario")
    add_connector(a12, a13, "ControlFlow")
    add_connector(a13, a14, "ControlFlow")
    add_connector(a14, stop_alta, "ControlFlow")

    diag.Update()
    ea_repo.ReloadDiagram(diag.DiagramID)
    print("Actividad Derivacion diagram completed successfully.")

def main():
    eap_path = os.path.abspath(r"c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\diagramas\DIAGRAMAS.eapx")
    print(f"Opening Enterprise Architect with {eap_path}...")
    ea_repo = win32com.client.Dispatch("EA.Repository")
    opened = ea_repo.OpenFile(eap_path)
    if not opened:
        print("Failed to open DIAGRAMAS.eapx!")
        sys.exit(1)

    model = ea_repo.Models.GetAt(0)
    sp2_pkg = add_or_get_package(model, "Sprint 2 - Historia Clínica, Intake y Consentimientos")

    build_usecase_diagram(sp2_pkg, ea_repo)
    build_class_diagram(sp2_pkg, ea_repo)
    build_activity_intake(sp2_pkg, ea_repo)
    build_activity_tareas(sp2_pkg, ea_repo)
    build_activity_derivacion(sp2_pkg, ea_repo)

    # Save and export images if possible
    pi = ea_repo.GetProjectInterface()
    img_dir = os.path.abspath(r"c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\documentacion\imagenes")
    os.makedirs(img_dir, exist_ok=True)

    diagram_exports = [
        ("1. Casos de Uso - Sprint 2", "Diagrama de Casos de Uso - Sprint 2 Incremental Acumulado", "diagrama_casos_uso_sp2.png"),
        ("2. Clases - Sprint 2", "Diagrama de Clases - Sprint 2 Dominio Clínico", "diagrama_clases_sp2.png"),
        ("3. Actividad - Formulario Previo e Historia Clínica", "Diagrama de Actividad - Intake y Apertura HC", "diagrama_actividad_intake.png"),
        ("4. Actividad - Tareas Terapéuticas", "Diagrama de Actividad - Ciclo Tareas Terapéuticas", "diagrama_actividad_tareas.png"),
        ("5. Actividad - Derivación a Psiquiatría", "Diagrama de Actividad - Protocolo Derivación Psiquiátrica", "diagrama_actividad_derivacion.png"),
    ]

    for sub_pkg_name, diag_name, img_filename in diagram_exports:
        sub_pkg = add_or_get_package(sp2_pkg, sub_pkg_name)
        for i in range(sub_pkg.Diagrams.Count):
            d = sub_pkg.Diagrams.GetAt(i)
            if d.Name.strip().lower() == diag_name.strip().lower():
                out_path = os.path.join(img_dir, img_filename)
                try:
                    pi.PutDiagramImageToFile(d.DiagramGUID, out_path, 1)
                    print(f"Exported {diag_name} -> {out_path}")
                except Exception as e:
                    print(f"Could not export {diag_name} to image: {e}")

    ea_repo.CloseFile()
    ea_repo.Exit()
    print("ALL 5 DIAGRAMS GENERATED AND SAVED IN DIAGRAMAS.eapx!")

if __name__ == "__main__":
    main()
