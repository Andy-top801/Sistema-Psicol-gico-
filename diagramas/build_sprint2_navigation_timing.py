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

def add_connector(source_elem, target_elem, conn_type, name="", stereotype=""):
    conn = source_elem.Connectors.AddNew(name, conn_type)
    conn.SupplierID = target_elem.ElementID
    if stereotype:
        conn.Stereotype = stereotype
    conn.Update()
    source_elem.Connectors.Refresh()
    return conn

# ==============================================================================
# 1. BUILD NAVIGATION DIAGRAMS (DISEÑO DE LA NAVEGACIÓN DE VISTAS)
# ==============================================================================
def build_navigation_diagrams(sp2_pkg, ea_repo):
    print("Building 9. Navegación de Vistas - Sprint 2...")
    root_nav = add_or_get_package(sp2_pkg, "9. Navegación de Vistas - Sprint 2")

    nav_specs = [
        {
            "sub_name": "Mapa de Navegación Global",
            "diag_name": "Mapa de Navegación Global - Sprint 2",
            "img_name": "diagrama_navegacion_global_sp2.png",
            "views": [
                ("init", "StateNode", 100, "", 50, -40, 70, -60),
                ("Dashboard_Principal", "State", 0, "GUI: Dashboard Clínico (Web)", 120, -30, 320, -90),
                ("Bandeja_Pacientes", "State", 0, "GUI: Expedientes Pacientes", 400, -30, 600, -90),
                ("Historia_Clinica", "State", 0, "GUI: Historia Clínica Modular", 680, -30, 900, -100),
                ("Editor_SOAP", "State", 0, "GUI: Editor Notas SOAP", 680, -150, 900, -220),
                ("Gestion_Tareas_Web", "State", 0, "GUI: Asignación de Tareas", 680, -260, 900, -330),
                ("Derivacion_Psiquiatria", "State", 0, "GUI: Hoja Derivación Psiquiatría", 680, -370, 920, -440),
                ("Panel_IA_Preconsulta", "State", 0, "GUI: Asistente IA Preconsulta", 400, -150, 620, -220),
                ("App_Home_Movil", "State", 0, "GUI: Home Paciente (Flutter)", 120, -240, 320, -300),
                ("Stepper_Intake", "State", 0, "GUI: Stepper Formulario Previo", 120, -340, 340, -410),
                ("Firma_Consentimiento", "State", 0, "GUI: Canvas Firma Digital", 400, -340, 620, -410),
                ("Mis_Tareas_Movil", "State", 0, "GUI: Mis Tareas Inter-Sesión", 120, -450, 340, -520),
            ],
            "links": [
                ("init", "Dashboard_Principal", "Login OK"),
                ("Dashboard_Principal", "Bandeja_Pacientes", "Seleccionar Pacientes"),
                ("Bandeja_Pacientes", "Historia_Clinica", "Abrir Historia"),
                ("Historia_Clinica", "Editor_SOAP", "Redactar SOAP"),
                ("Historia_Clinica", "Gestion_Tareas_Web", "Asignar Tarea"),
                ("Historia_Clinica", "Derivacion_Psiquiatria", "Derivar Psiquiatría"),
                ("Bandeja_Pacientes", "Panel_IA_Preconsulta", "Pre-análisis IA"),
                ("init", "App_Home_Movil", "Login Paciente"),
                ("App_Home_Movil", "Stepper_Intake", "Completar Intake"),
                ("Stepper_Intake", "Firma_Consentimiento", "Firmar Consentimiento"),
                ("App_Home_Movil", "Mis_Tareas_Movil", "Ver Tareas Asignadas"),
            ]
        },
        {
            "sub_name": "Navegación CU14 - Intake Digital",
            "diag_name": "Diagrama de Navegación – CU14: Formulario Previo",
            "img_name": "diagrama_navegacion_cu14.png",
            "views": [
                ("init", "StateNode", 100, "", 60, -40, 80, -60),
                ("Home_Movil", "State", 0, "Screen: Home Paciente (Flutter)", 140, -30, 360, -90),
                ("Paso1_Motivo", "State", 0, "Screen: Intake Paso 1 (Motivo)", 420, -30, 640, -90),
                ("Paso2_Escala", "State", 0, "Screen: Intake Paso 2 (Malestar)", 420, -140, 640, -200),
                ("Paso3_Antecedentes", "State", 0, "Screen: Intake Paso 3 (Historial)", 420, -250, 640, -310),
                ("Modal_Confirmacion", "State", 0, "Modal: Envío Exitoso (Badge Urgencia)", 140, -250, 360, -310),
                ("Vista_SoloLectura", "State", 0, "Screen: Resumen Preconsulta", 140, -360, 360, -420),
                ("final", "StateNode", 101, "", 230, -470, 250, -490),
            ],
            "links": [
                ("init", "Home_Movil", ""),
                ("Home_Movil", "Paso1_Motivo", "Click 'Completar Formulario'"),
                ("Paso1_Motivo", "Paso2_Escala", "Botón 'Siguiente'"),
                ("Paso2_Escala", "Paso3_Antecedentes", "Botón 'Siguiente'"),
                ("Paso3_Antecedentes", "Modal_Confirmacion", "Botón 'Enviar'"),
                ("Modal_Confirmacion", "Vista_SoloLectura", "Cerrar Modal"),
                ("Vista_SoloLectura", "final", ""),
            ]
        },
        {
            "sub_name": "Navegación CU15 - Historia Clínica",
            "diag_name": "Diagrama de Navegación – CU15: Historia Clínica y RBAC",
            "img_name": "diagrama_navegacion_cu15.png",
            "views": [
                ("init", "StateNode", 100, "", 60, -40, 80, -60),
                ("Bandeja_Expedientes", "State", 0, "View: Expedientes Pacientes (Web)", 140, -30, 370, -90),
                ("Tab_Anamnesis", "State", 0, "Tab: Anamnesis Inicial", 430, -30, 650, -90),
                ("Tab_ExamenMental", "State", 0, "Tab: Examen del Estado Mental", 430, -130, 650, -190),
                ("Tab_DiagnosticoCIE", "State", 0, "Tab: Diagnósticos CIE-10/11", 430, -230, 650, -290),
                ("Tab_PlanTratamiento", "State", 0, "Tab: Plan de Tratamiento", 430, -330, 650, -390),
                ("Toast_Guardado", "State", 0, "Toast: Historia Clínica Guardada", 140, -330, 370, -390),
                ("final", "StateNode", 101, "", 240, -450, 260, -470),
            ],
            "links": [
                ("init", "Bandeja_Expedientes", ""),
                ("Bandeja_Expedientes", "Tab_Anamnesis", "Click 'Abrir Historia' [RBAC OK]"),
                ("Tab_Anamnesis", "Tab_ExamenMental", "Pestaña 'Examen Mental'"),
                ("Tab_ExamenMental", "Tab_DiagnosticoCIE", "Pestaña 'Diagnóstico CIE'"),
                ("Tab_DiagnosticoCIE", "Tab_PlanTratamiento", "Pestaña 'Plan Tratamiento'"),
                ("Tab_PlanTratamiento", "Toast_Guardado", "Botón 'Guardar Historia'"),
                ("Toast_Guardado", "final", ""),
            ]
        },
        {
            "sub_name": "Navegación CU16 - Notas SOAP",
            "diag_name": "Diagrama de Navegación – CU16: Notas SOAP",
            "img_name": "diagrama_navegacion_cu16.png",
            "views": [
                ("init", "StateNode", 100, "", 60, -40, 80, -60),
                ("Agenda_Citas", "State", 0, "View: Agenda Semanal / Citas", 140, -30, 360, -90),
                ("Editor_SOAP_View", "State", 0, "View: Editor de Notas SOAP", 430, -30, 660, -100),
                ("Borrador_Toast", "State", 0, "Badge: Autoguardado Reactivo (30s)", 430, -150, 660, -210),
                ("Modal_Firma_Legal", "State", 0, "Modal: Firma Inmutable de Sesión", 430, -260, 660, -320),
                ("Timeline_Notas", "State", 0, "View: Línea de Tiempo de Sesiones", 140, -260, 370, -330),
                ("final", "StateNode", 101, "", 240, -400, 260, -420),
            ],
            "links": [
                ("init", "Agenda_Citas", ""),
                ("Agenda_Citas", "Editor_SOAP_View", "Click 'Documentar Sesión'"),
                ("Editor_SOAP_View", "Borrador_Toast", "Timer 30s sin teclear"),
                ("Borrador_Toast", "Editor_SOAP_View", "Continuar escribiendo"),
                ("Editor_SOAP_View", "Modal_Firma_Legal", "Click 'Firmar y Cerrar Nota'"),
                ("Modal_Firma_Legal", "Timeline_Notas", "Confirmar Firma Legal"),
                ("Timeline_Notas", "final", ""),
            ]
        },
        {
            "sub_name": "Navegación CU17 - Tareas Terapéuticas",
            "diag_name": "Diagrama de Navegación – CU17: Tareas Terapéuticas",
            "img_name": "diagrama_navegacion_cu17.png",
            "views": [
                ("init", "StateNode", 100, "", 60, -40, 80, -60),
                ("Modal_Asignar_Web", "State", 0, "Modal: Asignar Tarea (Web Psicólogo)", 140, -30, 380, -100),
                ("Screen_Tareas_Movil", "State", 0, "Screen: Mis Tareas (Flutter)", 440, -30, 670, -100),
                ("Detalle_Tarea", "State", 0, "Screen: Detalle y Guía Adjunta", 440, -160, 670, -220),
                ("Modal_Evidencia", "State", 0, "Modal: Subir Evidencia y Reflexión", 440, -280, 670, -350),
                ("Card_Completada", "State", 0, "Card: Tarea Marcada 'Completada'", 140, -280, 380, -350),
                ("final", "StateNode", 101, "", 250, -420, 270, -440),
            ],
            "links": [
                ("init", "Modal_Asignar_Web", "Terapeuta asigna tarea"),
                ("Modal_Asignar_Web", "Screen_Tareas_Movil", "Push Notification"),
                ("Screen_Tareas_Movil", "Detalle_Tarea", "Tap en Tarea"),
                ("Detalle_Tarea", "Modal_Evidencia", "Tap 'Reportar Cumplimiento'"),
                ("Modal_Evidencia", "Card_Completada", "Botón 'Enviar Reporte'"),
                ("Card_Completada", "final", ""),
            ]
        },
        {
            "sub_name": "Navegación CU18 - Consentimiento SHA-256",
            "diag_name": "Diagrama de Navegación – CU18: Consentimiento SHA-256",
            "img_name": "diagrama_navegacion_cu18.png",
            "views": [
                ("init", "StateNode", 100, "", 60, -40, 80, -60),
                ("Aviso_Consentimiento", "State", 0, "Banner: Consentimiento Obligatorio", 140, -30, 380, -90),
                ("Visor_Clausulas", "State", 0, "Screen: Lectura de Cláusulas Legales", 440, -30, 680, -100),
                ("Canvas_Firma", "State", 0, "Screen: Canvas Táctil de Firma", 440, -160, 680, -230),
                ("Modal_Hash", "State", 0, "Modal: Generando Hash SHA-256...", 440, -280, 680, -340),
                ("Screen_Exito", "State", 0, "Screen: Consentimiento Registrado", 140, -280, 380, -340),
                ("final", "StateNode", 101, "", 250, -410, 270, -430),
            ],
            "links": [
                ("init", "Aviso_Consentimiento", "Login sin consentimiento"),
                ("Aviso_Consentimiento", "Visor_Clausulas", "Tap 'Firmar Documento'"),
                ("Visor_Clausulas", "Canvas_Firma", "Scroll completo + Checkboxes"),
                ("Canvas_Firma", "Modal_Hash", "Tap 'Aceptar y Firmar'"),
                ("Modal_Hash", "Screen_Exito", "HTTP 201 Created"),
                ("Screen_Exito", "final", "Habilitar Agenda de Citas"),
            ]
        },
        {
            "sub_name": "Navegación CU19 - Derivación a Psiquiatría",
            "diag_name": "Diagrama de Navegación – CU19: Derivación a Psiquiatría",
            "img_name": "diagrama_navegacion_cu19.png",
            "views": [
                ("init", "StateNode", 100, "", 60, -40, 80, -60),
                ("Ficha_Expediente", "State", 0, "View: Ficha Paciente (Web)", 140, -30, 370, -90),
                ("Modal_TipoCierre", "State", 0, "Modal: Seleccionar Protocolo de Cierre", 430, -30, 680, -100),
                ("Form_Derivacion", "State", 0, "View: Orden Derivación Psiquiátrica", 430, -160, 680, -230),
                ("Visor_PDF_Interconsulta", "State", 0, "Modal: Descarga PDF Interconsulta", 430, -280, 680, -350),
                ("Form_Alta_Terapeutica", "State", 0, "View: Protocolo Alta Terapéutica", 140, -160, 370, -230),
                ("Expediente_Cerrado", "State", 0, "View: Expediente Egresado (Solo Lectura)", 140, -280, 370, -350),
                ("final", "StateNode", 101, "", 250, -420, 270, -440),
            ],
            "links": [
                ("init", "Ficha_Expediente", ""),
                ("Ficha_Expediente", "Modal_TipoCierre", "Click 'Cerrar / Derivar Caso'"),
                ("Modal_TipoCierre", "Form_Derivacion", "Opción 'Derivar a Psiquiatría'"),
                ("Form_Derivacion", "Visor_PDF_Interconsulta", "Botón 'Emitir Orden Médica'"),
                ("Modal_TipoCierre", "Form_Alta_Terapeutica", "Opción 'Alta por Objetivos'"),
                ("Form_Alta_Terapeutica", "Expediente_Cerrado", "Botón 'Formalizar Egreso'"),
                ("Visor_PDF_Interconsulta", "final", ""),
                ("Expediente_Cerrado", "final", ""),
            ]
        }
    ]

    for spec in nav_specs:
        sub_pkg = add_or_get_package(root_nav, spec["sub_name"])
        diag = add_or_get_diagram(sub_pkg, spec["diag_name"], "Statechart")

        state_nodes = {}
        for s_id, s_type, s_subtype, s_title, l, t, r, b in spec["views"]:
            if s_type == "StateNode":
                el = add_element(sub_pkg, "", "StateNode", subtype=s_subtype)
            else:
                el = add_element(sub_pkg, s_title, "State")
            add_to_diagram(diag, el, l, t, r, b)
            state_nodes[s_id] = el

        for src, tgt, trans_name in spec["links"]:
            if src in state_nodes and tgt in state_nodes:
                add_connector(state_nodes[src], state_nodes[tgt], "StateFlow", name=trans_name)

        diag.Update()
        ea_repo.ReloadDiagram(diag.DiagramID)
    print("Navigation diagrams completed successfully.")

# ==============================================================================
# 2. BUILD TIMING DIAGRAMS (DIAGRAMAS DE TIEMPO UML)
# ==============================================================================
def build_timing_diagrams(sp2_pkg, ea_repo):
    print("Building 10. Diagramas de Tiempo - Sprint 2...")
    root_time = add_or_get_package(sp2_pkg, "10. Diagramas de Tiempo - Sprint 2")

    timing_specs = [
        {
            "sub_name": "Diagrama de Tiempo 1 - Autoguardado SOAP",
            "diag_name": "Diagrama de Tiempo 1: Autoguardado Reactivo SOAP",
            "img_name": "diagrama_tiempo_autoguardado_soap.png",
            "lifelines": [
                ("Psicologo_UI", "Actor: Psicólogo Clínico (Teclado UI)", 60, -40, 200, -500),
                ("RxJS_Debounce", "Lifeline: RxJS Debounce Timer (30s)", 240, -40, 420, -500),
                ("Angular_State", "Lifeline: Angular 17 Reactive State", 460, -40, 640, -500),
                ("Backend_Postgres", "Lifeline: PostgreSQL Tenant Schema", 680, -40, 860, -500)
            ],
            "messages": [
                (0, 1, "t=0s: Evento Input(teclado)"),
                (1, 1, "t=15s: Reiniciar Debounce (30s)"),
                (1, 2, "t=45s: Timer Expira -> Trigger Save"),
                (2, 3, "t=45.1s: PATCH /api/v1/notas/{id}/borrador/"),
                (3, 2, "t=45.3s: 200 OK (Persistido)"),
                (2, 0, "t=45.4s: Mostrar Badge 'Borrador Guardado'")
            ]
        },
        {
            "sub_name": "Diagrama de Tiempo 2 - Pipeline IA",
            "diag_name": "Diagrama de Tiempo 2: Pipeline Asíncrono IA y Riesgo",
            "img_name": "diagrama_tiempo_seguridad_ia.png",
            "lifelines": [
                ("Psicologo_Web", "Actor: Psicólogo Tratante", 60, -40, 200, -500),
                ("DRF_Gateway", "Lifeline: Django API Gateway & Sanitizer", 240, -40, 440, -500),
                ("Celery_Worker", "Lifeline: Celery Task Worker", 480, -40, 660, -500),
                ("Gemini_AI", "Lifeline: Google Gemini 1.5 Pro", 700, -40, 880, -500),
                ("Auditoria_DB", "Lifeline: PostgreSQL Inmutable Audit", 920, -40, 1100, -500)
            ],
            "messages": [
                (0, 1, "t=0ms: POST /ia/preconsulta/analizar/"),
                (1, 1, "t=80ms: Sanitización PII & Consent Check"),
                (1, 2, "t=100ms: Encolar Task (Redis Broker)"),
                (2, 3, "t=120ms: Invocación API Gemini (TLS 1.3)"),
                (3, 2, "t=1800ms: Retorno Resumen y Reglas"),
                (2, 4, "t=1850ms: INSERT auditoria_ia_interaccion"),
                (2, 1, "t=1900ms: Task Completed Event"),
                (1, 0, "t=1950ms: Renderizar Borrador con Tag Humano")
            ]
        },
        {
            "sub_name": "Diagrama de Tiempo 3 - Tareas Terapéuticas",
            "diag_name": "Diagrama de Tiempo 3: Ciclo Tareas y Recordatorios",
            "img_name": "diagrama_tiempo_tareas_recordatorios.png",
            "lifelines": [
                ("Psicologo_Web", "Actor: Psicólogo Clínico", 60, -40, 200, -500),
                ("Celery_Beat", "Lifeline: Celery Beat Daily Cron", 240, -40, 420, -500),
                ("FCM_Push", "Lifeline: Firebase Cloud Messaging", 460, -40, 640, -500),
                ("Paciente_App", "Actor: Paciente (Flutter Móvil)", 680, -40, 860, -500),
                ("Tarea_Estado", "Lifeline: Estado Tarea (PostgreSQL)", 900, -40, 1080, -500)
            ],
            "messages": [
                (0, 4, "t=Día 0: Asignar Tarea (Estado=Asignada)"),
                (1, 2, "t=Día 3 (08:00 AM): Trigger Recordatorio Push"),
                (2, 3, "t=Día 3: Recibir Push 'Tienes una tarea pendiente'"),
                (3, 4, "t=Día 5: Enviar Evidencia (Estado=Completada)"),
                (4, 0, "t=Día 7: Sesión Presencial -> Feedback SOAP")
            ]
        }
    ]

    for spec in timing_specs:
        sub_pkg = add_or_get_package(root_time, spec["sub_name"])
        diag = add_or_get_diagram(sub_pkg, spec["diag_name"], "Sequence")

        nodes = []
        for l_id, l_name, l, t, r, b in spec["lifelines"]:
            if "actor" in l_name.lower():
                el = add_element(sub_pkg, l_name, "Actor")
            else:
                el = add_element(sub_pkg, l_name, "Sequence")
            add_to_diagram(diag, el, l, t, r, b)
            nodes.append(el)

        for seq_idx, (src_idx, tgt_idx, msg_text) in enumerate(spec["messages"], start=1):
            c = add_connector(nodes[src_idx], nodes[tgt_idx], "Sequence", name=msg_text)
            c.SequenceNo = seq_idx
            c.Update()

        diag.Update()
        ea_repo.ReloadDiagram(diag.DiagramID)
    print("Timing diagrams completed successfully.")

def export_all_new_images(sp2_pkg, ea_repo):
    pi = ea_repo.GetProjectInterface()
    img_dir = os.path.abspath(r"c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\documentacion\imagenes")
    os.makedirs(img_dir, exist_ok=True)

    def recurse_export(pkg):
        for d in pkg.Diagrams:
            filename_map = {
                "Mapa de Navegación Global - Sprint 2": "diagrama_navegacion_global_sp2.png",
                "Diagrama de Navegación – CU14: Formulario Previo": "diagrama_navegacion_cu14.png",
                "Diagrama de Navegación – CU15: Historia Clínica y RBAC": "diagrama_navegacion_cu15.png",
                "Diagrama de Navegación – CU16: Notas SOAP": "diagrama_navegacion_cu16.png",
                "Diagrama de Navegación – CU17: Tareas Terapéuticas": "diagrama_navegacion_cu17.png",
                "Diagrama de Navegación – CU18: Consentimiento SHA-256": "diagrama_navegacion_cu18.png",
                "Diagrama de Navegación – CU19: Derivación a Psiquiatría": "diagrama_navegacion_cu19.png",
                "Diagrama de Tiempo 1: Autoguardado Reactivo SOAP": "diagrama_tiempo_autoguardado_soap.png",
                "Diagrama de Tiempo 2: Pipeline Asíncrono IA y Riesgo": "diagrama_tiempo_seguridad_ia.png",
                "Diagrama de Tiempo 3: Ciclo Tareas y Recordatorios": "diagrama_tiempo_tareas_recordatorios.png",
            }
            if d.Name in filename_map:
                out_name = filename_map[d.Name]
                out_path = os.path.join(img_dir, out_name)
                try:
                    pi.PutDiagramImageToFile(d.DiagramGUID, out_path, 1)
                    print(f"Exported: {d.Name} -> {out_name}")
                except Exception as e:
                    print(f"Error exporting {d.Name}: {e}")
        for p in pkg.Packages:
            recurse_export(p)

    recurse_export(sp2_pkg)

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

    build_navigation_diagrams(sp2_pkg, ea_repo)
    build_timing_diagrams(sp2_pkg, ea_repo)
    export_all_new_images(sp2_pkg, ea_repo)

    ea_repo.CloseFile()
    ea_repo.Exit()
    print("ALL NAVIGATION AND TIMING DIAGRAMS SUCCESSFULLY BUILT AND EXPORTED!")

if __name__ == "__main__":
    main()
