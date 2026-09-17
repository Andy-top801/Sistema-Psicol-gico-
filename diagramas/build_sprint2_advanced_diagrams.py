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

def add_connector(source_elem, target_elem, conn_type, name="", stereotype="", seq_no=0):
    conn = source_elem.Connectors.AddNew(name, conn_type)
    conn.SupplierID = target_elem.ElementID
    if stereotype:
        conn.Stereotype = stereotype
    if seq_no:
        conn.SequenceNo = int(seq_no)
    conn.Update()
    source_elem.Connectors.Refresh()
    return conn

# ==============================================================================
# 1. BUILD COMMUNICATION DIAGRAMS (BCE)
# ==============================================================================
def build_communication_diagrams(sp2_pkg, ea_repo):
    print("Building 6. Diagramas de Comunicación - Sprint 2...")
    root_comm = add_or_get_package(sp2_pkg, "6. Diagramas de Comunicación - Sprint 2")

    comm_configs = [
        ("CU14 - Ficha Previa de Intake Digital", "Diagrama de Comunicación – CU14: Intake Digital",
         "Paciente / Psicólogo", "IU_FormularioPreConsulta\n(Web / Móvil)", "CTR_IntakeService\n(Django REST)", "CE_RespuestaPreConsulta\n(PostgreSQL Tenant)",
         [
             (1, 2, "1: Enviar respuestas pre-consulta()"),
             (2, 3, "2: POST /api/v1/intake/respuestas/"),
             (3, 3, "3: Validar JSON schema y urgencia()"),
             (3, 4, "4: INSERT clinica_respuestapreconsulta"),
             (4, 3, "5: Retorna UUID y timestamp"),
             (3, 2, "6: HTTP 201 Created"),
             (2, 1, "7: Muestra confirmación de entrega")
         ]),
        ("CU15 - Historia Clínica y Control RBAC", "Diagrama de Comunicación – CU15: Historia Clínica",
         "Psicólogo Tratante", "IU_HistoriaClinica\n(Angular 17)", "CTR_HistoriaClinicaService\n(Django REST)", "CE_HistoriaClinica\n(PostgreSQL Tenant)",
         [
             (1, 2, "1: Solicitar apertura de expediente()"),
             (2, 3, "2: POST /api/v1/historias-clinicas/"),
             (3, 3, "3: Validar asignación terapeuta (RBAC)"),
             (3, 4, "4: INSERT clinica_historiaclinica"),
             (4, 3, "5: Registro creado con código único"),
             (3, 2, "6: HTTP 201 Retorna expediente clínico"),
             (2, 1, "7: Despliega pestañas de historia clínica")
         ]),
        ("CU16 - Notas SOAP y Autoguardado Reactivo", "Diagrama de Comunicación – CU16: Notas SOAP",
         "Psicólogo Tratante", "IU_EditorNotasSOAP\n(Angular 17)", "CTR_NotaSesionService\n(Django REST)", "CE_NotaSesion\n(PostgreSQL Tenant)",
         [
             (1, 2, "1: Redactar campos SOAP y firmar()"),
             (2, 3, "2: POST /api/v1/notas-sesion/"),
             (3, 3, "3: Verificar estado cita = REALIZADA"),
             (3, 4, "4: INSERT clinica_notasesion (S, O, A, P)"),
             (4, 3, "5: Nota consolidada inmutable"),
             (3, 2, "6: HTTP 201 Nota Firmada Inmutable"),
             (2, 1, "7: Agrega nota firmada a línea de tiempo")
         ]),
        ("CU17 - Tareas Terapéuticas y Feedback", "Diagrama de Comunicación – CU17: Tareas Terapéuticas",
         "Paciente Móvil /\nPsicólogo Web", "IU_GestionTareas\n(Flutter / Angular)", "CTR_TareasService\n(Django REST)", "CE_TareaTerapeutica\n(PostgreSQL Tenant)",
         [
             (1, 2, "1: Reportar cumplimiento de tarea()"),
             (2, 3, "2: POST /api/v1/tareas/{id}/evidencia/"),
             (3, 3, "3: Validar plazo y archivo adjunto()"),
             (3, 4, "4: INSERT clinica_evidenciatarea & UPDATE"),
             (4, 3, "5: Tarea actualizada a COMPLETADA"),
             (3, 2, "6: HTTP 200 OK"),
             (2, 1, "7: Actualiza barra de progreso terapéutico")
         ]),
        ("CU18 - Consentimiento Informado y Firma Digital", "Diagrama de Comunicación – CU18: Consentimiento Informado",
         "Paciente / Tutor", "IU_FirmaConsentimiento\n(Flutter Móvil)", "CTR_ConsentimientoService\n(Django REST)", "CE_FirmaConsentimiento\n(PostgreSQL Tenant)",
         [
             (1, 2, "1: Aceptar cláusulas y firmar en canvas()"),
             (2, 2, "2: Calcular SHA-256(texto_legal + datos)"),
             (2, 3, "3: POST /api/v1/consentimientos/firmar/"),
             (3, 3, "4: Extraer IP remota y User-Agent()"),
             (3, 4, "5: INSERT clinica_firmaconsentimiento"),
             (4, 3, "6: Firma inmutable con sellado SHA-256"),
             (3, 2, "7: HTTP 201 Consentimiento Aceptado"),
             (2, 1, "8: Habilita acceso completo a la atención")
         ]),
        ("CU19 - Cierre de Caso y Derivación Psiquiátrica", "Diagrama de Comunicación – CU19: Derivación Psiquiátrica",
         "Psicólogo Tratante", "IU_DerivacionCierre\n(Angular 17)", "CTR_DerivacionService\n(Django REST)", "CE_DerivacionCaso\n(PostgreSQL Tenant)",
         [
             (1, 2, "1: Emitir orden de interconsulta()"),
             (2, 3, "2: POST /api/v1/derivaciones/"),
             (3, 3, "3: Generar PDF de interconsulta médica()"),
             (3, 4, "4: INSERT clinica_derivacioncaso"),
             (4, 3, "5: Registro guardado y caso derivado"),
             (3, 2, "6: Descarga orden y notifica coordinador"),
             (2, 1, "7: Muestra comprobante de derivación emitido")
         ]),
        ("HU-35 - Consentimiento y Pasarela Ética de IA", "Diagrama de Comunicación – HU-35: Pasarela IA Asistiva",
         "Psicólogo Tratante", "IU_PanelAsistenteIA\n(Angular 17)", "CTR_PasarelaIAService\n(Django / Celery)", "CE_AuditoriaIA\n(PostgreSQL Tenant)",
         [
             (1, 2, "1: Solicitar pre-análisis asistivo()"),
             (2, 3, "2: POST /api/v1/ia/preconsulta/analizar/"),
             (3, 3, "3: Sanitizar datos PII y verificar consentimiento()"),
             (3, 4, "4: INSERT auditoria_registro_ia (prompt, hash)"),
             (4, 3, "5: Registro de auditoría guardado"),
             (3, 2, "6: Retorna borrador explicativo neutral"),
             (2, 1, "7: Despliega borrador con reglas transparentes")
         ])
    ]

    for sub_name, diag_name, act_name, iu_name, ctr_name, ce_name, msgs in comm_configs:
        sub_pkg = add_or_get_package(root_comm, sub_name)
        diag = add_or_get_diagram(sub_pkg, diag_name, "Communication")

        # Elements BCE
        e_actor = add_element(sub_pkg, act_name, "Actor")
        e_iu = add_element(sub_pkg, iu_name, "Class", stereotype="boundary")
        e_ctr = add_element(sub_pkg, ctr_name, "Class", stereotype="control")
        e_ce = add_element(sub_pkg, ce_name, "Class", stereotype="entity")

        nodes = [None, e_actor, e_iu, e_ctr, e_ce]

        # Layout BCE (Horizontal line layout standard for EA Communication diagrams)
        add_to_diagram(diag, e_actor, 60, -80, 160, -180)
        add_to_diagram(diag, e_iu, 420, -80, 580, -182)
        add_to_diagram(diag, e_ctr, 840, -80, 1000, -182)
        add_to_diagram(diag, e_ce, 1260, -80, 1420, -180)

        for src_idx, tgt_idx, msg_text in msgs:
            add_connector(nodes[src_idx], nodes[tgt_idx], "ControlFlow", name=msg_text)

        diag.Update()
        ea_repo.ReloadDiagram(diag.DiagramID)
    print("Communication diagrams completed successfully.")

# ==============================================================================
# 2. BUILD SEQUENCE DIAGRAMS (3 LAYERS ARCHITECTURE)
# ==============================================================================
def build_sequence_diagrams(sp2_pkg, ea_repo):
    print("Building 7. Diagramas de Secuencia - Sprint 2...")
    root_seq = add_or_get_package(sp2_pkg, "7. Diagramas de Secuencia - Sprint 2")

    seq_configs = [
        ("CU14 - Secuencia Intake Digital", "Diagrama de Secuencia – CU14: Intake Digital",
         "Paciente / Psicólogo", "IU_FormularioPreConsulta (Web/Móvil)", "CTR_IntakeController (Django REST)", "CE_RespuestaPreConsulta (PostgreSQL)",
         [
             (1, 2, "1: ingresar_respuestas(sintomas, malestar)"),
             (2, 3, "2: POST /api/v1/intake/respuestas/"),
             (3, 3, "3: validar_esquema_json_y_urgencia()"),
             (3, 4, "4: INSERT INTO clinica_respuestapreconsulta"),
             (4, 3, "5: 201 Created (uuid, timestamp)"),
             (3, 2, "6: HTTP 201 Created"),
             (2, 1, "7: confirmacion_envio_exitosa()")
         ]),
        ("CU15 - Secuencia Historia Clínica y RBAC", "Diagrama de Secuencia – CU15: Historia Clínica y RBAC",
         "Psicólogo Tratante", "IU_HistoriaClinica (Angular 17)", "CTR_HistoriaClinicaController (DRF)", "CE_HistoriaClinica (PostgreSQL)",
         [
             (1, 2, "1: solicitar_apertura_historia(paciente_id)"),
             (2, 3, "2: POST /api/v1/historias-clinicas/"),
             (3, 3, "3: verificar_permisos_rbac_y_asignacion()"),
             (3, 4, "4: INSERT INTO clinica_historiaclinica"),
             (4, 3, "5: expediente_creado(codigo_historia)"),
             (3, 2, "6: HTTP 201 Created (expediente)"),
             (2, 1, "7: renderizar_historia_clinica()")
         ]),
        ("CU16 - Secuencia Notas SOAP", "Diagrama de Secuencia – CU16: Notas SOAP",
         "Psicólogo Tratante", "IU_EditorNotasSOAP (Angular 17)", "CTR_NotaSesionController (DRF)", "CE_NotaSesion (PostgreSQL)",
         [
             (1, 2, "1: guardar_y_firmar_nota(S, O, A, P)"),
             (2, 3, "2: POST /api/v1/notas-sesion/"),
             (3, 3, "3: validar_cita_realizada_y_terapeuta()"),
             (3, 4, "4: INSERT INTO clinica_notasesion (firmada=true)"),
             (4, 3, "5: nota_inmutable_persistida()"),
             (3, 2, "6: HTTP 201 Nota Firmada Inmutable"),
             (2, 1, "7: actualizar_timeline_sesiones()")
         ]),
        ("CU17 - Secuencia Tareas Terapéuticas", "Diagrama de Secuencia – CU17: Tareas Terapéuticas",
         "Paciente (Flutter Móvil)", "IU_GestionTareas (Flutter 3.x)", "CTR_TareasController (DRF)", "CE_TareaTerapeutica (PostgreSQL)",
         [
             (1, 2, "1: reportar_cumplimiento(reflexion, archivo)"),
             (2, 3, "2: POST /api/v1/tareas/{id}/evidencia/"),
             (3, 3, "3: validar_fecha_limite_y_formato()"),
             (3, 4, "4: INSERT evidencia & UPDATE tarea(COMPLETADA)"),
             (4, 3, "5: estado_actualizado_ok()"),
             (3, 2, "6: HTTP 200 OK"),
             (2, 1, "7: mostrar_progreso_actualizado()")
         ]),
        ("CU18 - Secuencia Consentimiento SHA-256", "Diagrama de Secuencia – CU18: Consentimiento SHA-256",
         "Paciente / Tutor", "IU_FirmaConsentimiento (Flutter)", "CTR_ConsentimientoController (DRF)", "CE_FirmaConsentimiento (PostgreSQL)",
         [
             (1, 2, "1: firmar_en_canvas_y_aceptar()"),
             (2, 2, "2: calcular_hash_sha256(texto, canvas)"),
             (2, 3, "3: POST /api/v1/consentimientos/firmar/"),
             (3, 3, "4: capturar_ip_useragent_y_timestamp()"),
             (3, 4, "5: INSERT INTO clinica_firmaconsentimiento"),
             (4, 3, "6: registro_criptografico_sellado()"),
             (3, 2, "7: HTTP 201 Consentimiento Aceptado"),
             (2, 1, "8: habilitar_citas_en_sistema()")
         ]),
        ("CU19 - Secuencia Derivación Psiquiátrica", "Diagrama de Secuencia – CU19: Derivación Psiquiátrica",
         "Psicólogo Tratante", "IU_DerivacionCierre (Angular 17)", "CTR_DerivacionController (DRF)", "CE_DerivacionCaso (PostgreSQL)",
         [
             (1, 2, "1: emitir_orden_interconsulta(motivo, riesgo)"),
             (2, 3, "2: POST /api/v1/derivaciones/"),
             (3, 3, "3: compilar_pdf_oficial_con_hash()"),
             (3, 4, "4: INSERT INTO clinica_derivacioncaso"),
             (4, 3, "5: orden_registrada(id, hash)"),
             (3, 2, "6: HTTP 201 (pdf_url, notificacion_coordinador)"),
             (2, 1, "7: descargar_orden_y_confirmar()")
         ]),
        ("HU-35 - Secuencia Pasarela IA Asistiva", "Diagrama de Secuencia – HU-35: Pasarela IA Asistiva",
         "Psicólogo Tratante", "IU_PanelAsistenteIA (Angular)", "CTR_PasarelaIAService (DRF/Celery)", "CE_AuditoriaIA (PostgreSQL)",
         [
             (1, 2, "1: solicitar_revision_asistiva(formulario_id)"),
             (2, 3, "2: POST /api/v1/ia/preconsulta/analizar/"),
             (3, 3, "3: validar_consentimiento_y_anonimizar_pii()"),
             (3, 4, "4: INSERT INTO auditoria_ia_request (hash, pii_clean)"),
             (4, 3, "5: auditoria_inmutable_iniciada()"),
             (3, 2, "6: HTTP 200 (borrador_neutral, explicacion_reglas)"),
             (2, 1, "7: mostrar_borrador_ia_requiere_revision_humana()")
         ])
    ]

    for sub_name, diag_name, act_name, iu_name, ctr_name, ce_name, msgs in seq_configs:
        sub_pkg = add_or_get_package(root_seq, sub_name)
        diag = add_or_get_diagram(sub_pkg, diag_name, "Sequence")

        # Elements for Sequence Diagram (Actor + Sequence Lifelines with stereotypes)
        e_actor = add_element(sub_pkg, act_name, "Actor")
        e_iu = add_element(sub_pkg, iu_name, "Sequence", stereotype="boundary")
        e_ctr = add_element(sub_pkg, ctr_name, "Sequence", stereotype="control")
        e_ce = add_element(sub_pkg, ce_name, "Sequence", stereotype="entity")

        nodes = [None, e_actor, e_iu, e_ctr, e_ce]

        # Lifeline positions (left, top=-40, right, bottom=-600)
        add_to_diagram(diag, e_actor, 60, -40, 150, -600)
        add_to_diagram(diag, e_iu, 280, -40, 440, -600)
        add_to_diagram(diag, e_ctr, 580, -40, 760, -600)
        add_to_diagram(diag, e_ce, 900, -40, 1080, -600)

        for seq_idx, (src_idx, tgt_idx, msg_text) in enumerate(msgs, start=1):
            add_connector(nodes[src_idx], nodes[tgt_idx], "Sequence", name=msg_text, seq_no=seq_idx)

        diag.Update()
        ea_repo.ReloadDiagram(diag.DiagramID)
    print("Sequence diagrams completed successfully.")

# ==============================================================================
# 3. BUILD STATE MACHINE DIAGRAMS
# ==============================================================================
def build_state_machine_diagrams(sp2_pkg, ea_repo):
    print("Building 8. Máquinas de Estados - Sprint 2...")
    root_state = add_or_get_package(sp2_pkg, "8. Máquinas de Estados - Sprint 2")

    state_configs = [
        ("Máquina 1 - Intake y Triaje (CU14)", "Diagrama de Estados – CU14: Intake y Triaje Clínico",
         [
             ("init", "StateNode", 100, 220, -40, 240, -60),
             ("Borrador_Incompleto", "State", 0, 150, -100, 310, -150),
             ("Enviado_Pendiente_Triaje", "State", 0, 140, -200, 320, -250),
             ("Prioridad_Urgente_Nivel4", "State", 0, 40, -320, 220, -370),
             ("Prioridad_Ordinaria", "State", 0, 240, -320, 420, -370),
             ("Asociado_A_Historia_Clinica", "State", 0, 130, -440, 330, -490),
             ("Archivado", "State", 0, 150, -540, 310, -590),
             ("final", "StateNode", 101, 220, -630, 240, -650)
         ],
         [
             ("init", "Borrador_Incompleto", "iniciar_formulario()"),
             ("Borrador_Incompleto", "Enviado_Pendiente_Triaje", "enviar_formulario() [campos_validos]"),
             ("Enviado_Pendiente_Triaje", "Prioridad_Urgente_Nivel4", "calcular_prioridad() [malestar >= 4]"),
             ("Enviado_Pendiente_Triaje", "Prioridad_Ordinaria", "calcular_prioridad() [malestar < 4]"),
             ("Prioridad_Urgente_Nivel4", "Asociado_A_Historia_Clinica", "asociar_anamnesis()"),
             ("Prioridad_Ordinaria", "Asociado_A_Historia_Clinica", "asociar_anamnesis()"),
             ("Asociado_A_Historia_Clinica", "Archivado", "cerrar_caso()"),
             ("Archivado", "final", "")
         ]),
        ("Máquina 2 - Notas SOAP e Historia (CU15)", "Diagrama de Estados – CU15: Notas SOAP e Historia Clínica",
         [
             ("init", "StateNode", 100, 220, -40, 240, -60),
             ("Historia_Abierta_Activa", "State", 0, 140, -100, 320, -150),
             ("Nota_En_Edicion", "State", 0, 150, -200, 310, -250),
             ("Borrador_Autoguardado", "State", 0, 380, -200, 540, -250),
             ("Nota_Firmada_Inmutable", "State", 0, 140, -310, 320, -360),
             ("Historia_Cerrada_Alta", "State", 0, 140, -420, 320, -470),
             ("final", "StateNode", 101, 220, -510, 240, -530)
         ],
         [
             ("init", "Historia_Abierta_Activa", "crear_expediente()"),
             ("Historia_Abierta_Activa", "Nota_En_Edicion", "iniciar_sesion()"),
             ("Nota_En_Edicion", "Borrador_Autoguardado", "timer_autoguardado(30s)"),
             ("Borrador_Autoguardado", "Nota_En_Edicion", "reanudar_edicion()"),
             ("Nota_En_Edicion", "Nota_Firmada_Inmutable", "firmar_nota() [valida_cita_realizada]"),
             ("Nota_Firmada_Inmutable", "Historia_Abierta_Activa", "continuar_tratamiento()"),
             ("Historia_Abierta_Activa", "Historia_Cerrada_Alta", "formalizar_alta()"),
             ("Historia_Cerrada_Alta", "final", "")
         ]),
        ("Máquina 3 - Tareas Terapéuticas (CU16)", "Diagrama de Estados – CU16: Tareas Terapéuticas",
         [
             ("init", "StateNode", 100, 220, -40, 240, -60),
             ("Asignada", "State", 0, 150, -100, 310, -150),
             ("En_Progreso", "State", 0, 150, -200, 310, -250),
             ("Evidencia_Entregada", "State", 0, 140, -300, 320, -350),
             ("Completada_Con_Feedback", "State", 0, 130, -410, 330, -460),
             ("Vencida_Sin_Entrega", "State", 0, 380, -250, 540, -300),
             ("final", "StateNode", 101, 220, -500, 240, -520)
         ],
         [
             ("init", "Asignada", "asignar_post_sesion()"),
             ("Asignada", "En_Progreso", "abrir_tarea_en_app()"),
             ("En_Progreso", "Evidencia_Entregada", "enviar_reporte() [dentro_de_plazo]"),
             ("En_Progreso", "Vencida_Sin_Entrega", "timeout_fecha_limite()"),
             ("Evidencia_Entregada", "Completada_Con_Feedback", "retroalimentar_en_soap()"),
             ("Vencida_Sin_Entrega", "final", ""),
             ("Completada_Con_Feedback", "final", "")
         ]),
        ("Máquina 4 - Consentimiento y Pasarela IA (HU-35)", "Diagrama de Estados – HU-35: Consentimiento y Pasarela IA",
         [
             ("init", "StateNode", 100, 220, -40, 240, -60),
             ("Lectura_Obligatoria", "State", 0, 140, -100, 320, -150),
             ("Firmado_Activo_SHA256", "State", 0, 130, -200, 330, -250),
             ("Pasarela_IA_Habilitada", "State", 0, 130, -300, 330, -350),
             ("Borrador_Asistivo_Generado", "State", 0, 120, -400, 340, -450),
             ("Validacion_Humana_Cerrada", "State", 0, 120, -500, 340, -550),
             ("final", "StateNode", 101, 220, -580, 240, -600)
         ],
         [
             ("init", "Lectura_Obligatoria", "iniciar_intake()"),
             ("Lectura_Obligatoria", "Firmado_Activo_SHA256", "firmar_canvas_y_aceptar()"),
             ("Firmado_Activo_SHA256", "Pasarela_IA_Habilitada", "verificar_consentimiento()"),
             ("Pasarela_IA_Habilitada", "Borrador_Asistivo_Generado", "ejecutar_gemini_sanitizado()"),
             ("Borrador_Asistivo_Generado", "Validacion_Humana_Cerrada", "revisar_aceptar_o_descartar()"),
             ("Validacion_Humana_Cerrada", "final", "")
         ])
    ]

    for sub_name, diag_name, states, trans in state_configs:
        sub_pkg = add_or_get_package(root_state, sub_name)
        diag = add_or_get_diagram(sub_pkg, diag_name, "Statechart")

        state_elems = {}
        for s_id, s_type, s_subtype, l, t, r, b in states:
            s_name = "" if s_type == "StateNode" else s_id.replace("_", " ")
            el = add_element(sub_pkg, s_name, s_type, subtype=s_subtype)
            add_to_diagram(diag, el, l, t, r, b)
            state_elems[s_id] = el

        for src, tgt, t_name in trans:
            if src in state_elems and tgt in state_elems:
                add_connector(state_elems[src], state_elems[tgt], "StateFlow", name=t_name)

        diag.Update()
        ea_repo.ReloadDiagram(diag.DiagramID)
    print("State Machine diagrams completed successfully.")

def export_all_images(sp2_pkg, ea_repo):
    pi = ea_repo.GetProjectInterface()
    img_dir = os.path.abspath(r"c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\documentacion\imagenes")
    os.makedirs(img_dir, exist_ok=True)

    def export_pkg_diagrams(pkg):
        for d in pkg.Diagrams:
            clean_name = d.Name.replace("–", "-").replace(":", "").replace("/", "_").strip()
            # Map specific diagrams to standard markdown filenames
            filename_map = {
                "Diagrama de Comunicación – CU14: Intake Digital": "diagrama_comunicacion_cu14.png",
                "Diagrama de Comunicación – CU15: Historia Clínica": "diagrama_comunicacion_cu15.png",
                "Diagrama de Comunicación – CU16: Notas SOAP": "diagrama_comunicacion_cu16.png",
                "Diagrama de Comunicación – CU17: Tareas Terapéuticas": "diagrama_comunicacion_cu17.png",
                "Diagrama de Comunicación – CU18: Consentimiento Informado": "diagrama_comunicacion_cu18.png",
                "Diagrama de Comunicación – CU19: Derivación Psiquiátrica": "diagrama_comunicacion_cu19.png",
                "Diagrama de Comunicación – HU-35: Pasarela IA Asistiva": "diagrama_comunicacion_hu35.png",
                "Diagrama de Secuencia – CU14: Intake Digital": "diagrama_secuencia_cu14.png",
                "Diagrama de Secuencia – CU15: Historia Clínica y RBAC": "diagrama_secuencia_cu15.png",
                "Diagrama de Secuencia – CU16: Notas SOAP": "diagrama_secuencia_cu16.png",
                "Diagrama de Secuencia – CU17: Tareas Terapéuticas": "diagrama_secuencia_cu17.png",
                "Diagrama de Secuencia – CU18: Consentimiento SHA-256": "diagrama_secuencia_cu18.png",
                "Diagrama de Secuencia – CU19: Derivación Psiquiátrica": "diagrama_secuencia_cu19.png",
                "Diagrama de Secuencia – HU-35: Pasarela IA Asistiva": "diagrama_secuencia_hu35.png",
                "Diagrama de Estados – CU14: Intake y Triaje Clínico": "diagrama_estados_formulario_intake.png",
                "Diagrama de Estados – CU15: Notas SOAP e Historia Clínica": "diagrama_estados_historia_clinica.png",
                "Diagrama de Estados – CU16: Tareas Terapéuticas": "diagrama_estados_tareas_terapeuticas.png",
                "Diagrama de Estados – HU-35: Consentimiento y Pasarela IA": "diagrama_estados_consentimiento_y_piloto_ia.png",
            }
            out_name = filename_map.get(d.Name, f"{clean_name}.png")
            out_path = os.path.join(img_dir, out_name)
            try:
                pi.PutDiagramImageToFile(d.DiagramGUID, out_path, 1)
                print(f"Exported: {d.Name} -> {out_name}")
            except Exception as e:
                print(f"Error exporting {d.Name}: {e}")
        for p in pkg.Packages:
            export_pkg_diagrams(p)

    export_pkg_diagrams(sp2_pkg)

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

    build_communication_diagrams(sp2_pkg, ea_repo)
    build_sequence_diagrams(sp2_pkg, ea_repo)
    build_state_machine_diagrams(sp2_pkg, ea_repo)
    export_all_images(sp2_pkg, ea_repo)

    ea_repo.CloseFile()
    ea_repo.Exit()
    print("ALL ADVANCED SPRINT 2 DIAGRAMS SUCCESSFULLY BUILT AND EXPORTED!")

if __name__ == "__main__":
    main()
