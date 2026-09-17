import win32com.client
import os
import sys

def rebuild_all_communication():
    eap_path = os.path.abspath(r"c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\diagramas\DIAGRAMAS.eapx")
    print(f"Opening {eap_path}...")
    ea_repo = win32com.client.Dispatch("EA.Repository")
    opened = ea_repo.OpenFile(eap_path)
    if not opened:
        print("Failed to open repository!")
        sys.exit(1)

    model = ea_repo.Models.GetAt(0)
    sp2_pkg = None
    for i in range(model.Packages.Count):
        p = model.Packages.GetAt(i)
        if "sprint 2" in p.Name.lower():
            sp2_pkg = p
            break

    if not sp2_pkg:
        print("Sprint 2 package not found!")
        sys.exit(1)

    # Find or recreate package '6. Diagramas de Comunicación - Sprint 2'
    comm_pkg = None
    for i in range(sp2_pkg.Packages.Count):
        p = sp2_pkg.Packages.GetAt(i)
        if "6. diagramas de comunicaci" in p.Name.lower():
            comm_pkg = p
            break

    if comm_pkg:
        # Delete existing subpackages so we can recreate them cleanly
        for i in range(sp2_pkg.Packages.Count - 1, -1, -1):
            if sp2_pkg.Packages.GetAt(i).PackageID == comm_pkg.PackageID:
                sp2_pkg.Packages.Delete(i)
                break
        sp2_pkg.Packages.Refresh()

    comm_pkg = sp2_pkg.Packages.AddNew("6. Diagramas de Comunicación - Sprint 2", "")
    comm_pkg.Update()
    sp2_pkg.Packages.Refresh()

    comm_specs = [
        {
            "sub_name": "CU14 - Ficha Previa de Intake Digital",
            "diag_name": "Diagrama de Comunicación – CU14: Intake Digital",
            "img_name": "diagrama_comunicacion_cu14.png",
            "actor_name": "Paciente / Psicólogo",
            "iu_name": "IU_FormularioPreConsulta\n(Web / Móvil)",
            "ctr_name": "CTR_IntakeController\n(Django REST)",
            "ce_name": "CE_RespuestaPreConsulta\n(PostgreSQL)",
            "msgs": [
                (1, 2, "1: Ingresar datos de síntomas y malestar", "SX=0;SY=18;EX=0;EY=18;"),
                (2, 1, "8: Mostrar 'Formulario enviado con éxito'", "SX=0;SY=-18;EX=0;EY=-18;"),
                (2, 3, "2: POST /api/v1/intake/respuestas/", "SX=0;SY=18;EX=0;EY=18;"),
                (3, 2, "7: 201 Created {id, prioridad: ALTA}", "SX=0;SY=-18;EX=0;EY=-18;"),
                (3, 4, "3: Validar esquema JSONB y nivel urgencia", "SX=0;SY=28;EX=0;EY=28;"),
                (4, 3, "4: Esquema válido y prioridad calculada", "SX=0;SY=12;EX=0;EY=12;"),
                (3, 4, "5: INSERT INTO clinica_respuestapreconsulta", "SX=0;SY=-12;EX=0;EY=-12;"),
                (4, 3, "6: Respuesta persistida con UUID único", "SX=0;SY=-28;EX=0;EY=-28;"),
            ]
        },
        {
            "sub_name": "CU15 - Historia Clínica y Control RBAC",
            "diag_name": "Diagrama de Comunicación – CU15: Historia Clínica",
            "img_name": "diagrama_comunicacion_cu15.png",
            "actor_name": "Psicólogo Tratante",
            "iu_name": "IU_HistoriaClinica\n(Angular 17)",
            "ctr_name": "CTR_HistoriaClinica\n(Django REST)",
            "ce_name": "CE_HistoriaClinica\n(PostgreSQL)",
            "msgs": [
                (1, 2, "1: Solicitar apertura formal de expediente", "SX=0;SY=18;EX=0;EY=18;"),
                (2, 1, "8: Desplegar historia clínica en pestañas", "SX=0;SY=-18;EX=0;EY=-18;"),
                (2, 3, "2: POST /api/v1/historias-clinicas/", "SX=0;SY=18;EX=0;EY=18;"),
                (3, 2, "7: 201 Created {codigo_historia, anamnesis}", "SX=0;SY=-18;EX=0;EY=-18;"),
                (3, 4, "3: Verificar rol PSICOLOGO y asignación", "SX=0;SY=28;EX=0;EY=28;"),
                (4, 3, "4: Permiso concedido y paciente sin historia", "SX=0;SY=12;EX=0;EY=12;"),
                (3, 4, "5: INSERT INTO clinica_historiaclinica", "SX=0;SY=-12;EX=0;EY=-12;"),
                (4, 3, "6: Expediente creado e indexado con CIE", "SX=0;SY=-28;EX=0;EY=-28;"),
            ]
        },
        {
            "sub_name": "CU16 - Notas SOAP y Autoguardado Reactivo",
            "diag_name": "Diagrama de Comunicación – CU16: Notas SOAP",
            "img_name": "diagrama_comunicacion_cu16.png",
            "actor_name": "Psicólogo Tratante",
            "iu_name": "IU_EditorNotasSOAP\n(Angular 17)",
            "ctr_name": "CTR_NotaSesion\n(Django REST)",
            "ce_name": "CE_NotaSesion\n(PostgreSQL)",
            "msgs": [
                (1, 2, "1: Redactar campos SOAP (S, O, A, P) y firmar", "SX=0;SY=18;EX=0;EY=18;"),
                (2, 1, "8: Bloquear edición y mostrar nota inmutable", "SX=0;SY=-18;EX=0;EY=-18;"),
                (2, 3, "2: POST /api/v1/notas-sesion/firmar/", "SX=0;SY=18;EX=0;EY=18;"),
                (3, 2, "7: 201 Created {nota_id, firmada: true}", "SX=0;SY=-18;EX=0;EY=-18;"),
                (3, 4, "3: Verificar cita = REALIZADA y terapeuta", "SX=0;SY=28;EX=0;EY=28;"),
                (4, 3, "4: Cita completada válida para cierre", "SX=0;SY=12;EX=0;EY=12;"),
                (3, 4, "5: INSERT INTO clinica_notasesion (inmutable)", "SX=0;SY=-12;EX=0;EY=-12;"),
                (4, 3, "6: Nota médica sellada en esquema tenant", "SX=0;SY=-28;EX=0;EY=-28;"),
            ]
        },
        {
            "sub_name": "CU17 - Tareas Terapéuticas y Feedback",
            "diag_name": "Diagrama de Comunicación – CU17: Tareas Terapéuticas",
            "img_name": "diagrama_comunicacion_cu17.png",
            "actor_name": "Paciente Móvil /\nPsicólogo Web",
            "iu_name": "IU_GestionTareas\n(Flutter / Angular)",
            "ctr_name": "CTR_TareasService\n(Django REST)",
            "ce_name": "CE_TareaTerapeutica\n(PostgreSQL)",
            "msgs": [
                (1, 2, "1: Reportar reflexión y evidencia de tarea", "SX=0;SY=18;EX=0;EY=18;"),
                (2, 1, "8: Actualizar indicador 'Completada 100%'", "SX=0;SY=-18;EX=0;EY=-18;"),
                (2, 3, "2: POST /api/v1/tareas/{id}/evidencia/", "SX=0;SY=18;EX=0;EY=18;"),
                (3, 2, "7: 200 OK {estado: 'COMPLETADA'}", "SX=0;SY=-18;EX=0;EY=-18;"),
                (3, 4, "3: Validar plazo de entrega y tipo archivo", "SX=0;SY=28;EX=0;EY=28;"),
                (4, 3, "4: Tarea activa en tiempo y plazo válido", "SX=0;SY=12;EX=0;EY=12;"),
                (3, 4, "5: INSERT evidencia & UPDATE clinica_tareaterapeutica", "SX=0;SY=-12;EX=0;EY=-12;"),
                (4, 3, "6: Evidencia guardada y tarea completada", "SX=0;SY=-28;EX=0;EY=-28;"),
            ]
        },
        {
            "sub_name": "CU18 - Consentimiento Informado y Firma Digital",
            "diag_name": "Diagrama de Comunicación – CU18: Consentimiento Informado",
            "img_name": "diagrama_comunicacion_cu18.png",
            "actor_name": "Paciente / Tutor",
            "iu_name": "IU_FirmaConsentimiento\n(Flutter Móvil)",
            "ctr_name": "CTR_Consentimiento\n(Django REST)",
            "ce_name": "CE_FirmaConsentimiento\n(PostgreSQL)",
            "msgs": [
                (1, 2, "1: Aceptar cláusulas y firmar en canvas", "SX=0;SY=18;EX=0;EY=18;"),
                (2, 1, "8: Confirmar consentimiento y habilitar citas", "SX=0;SY=-18;EX=0;EY=-18;"),
                (2, 3, "2: POST /api/v1/consentimientos/firmar/ (SHA-256)", "SX=0;SY=18;EX=0;EY=18;"),
                (3, 2, "7: 201 Created {hash_verificado, activo}", "SX=0;SY=-18;EX=0;EY=-18;"),
                (3, 4, "3: Capturar IP remota, User-Agent y timestamp", "SX=0;SY=28;EX=0;EY=28;"),
                (4, 3, "4: Metadatos y plantilla legal validados", "SX=0;SY=12;EX=0;EY=12;"),
                (3, 4, "5: INSERT INTO clinica_firmaconsentimiento", "SX=0;SY=-12;EX=0;EY=-12;"),
                (4, 3, "6: Firma sellada criptográficamente inmutable", "SX=0;SY=-28;EX=0;EY=-28;"),
            ]
        },
        {
            "sub_name": "CU19 - Cierre de Caso y Derivación Psiquiátrica",
            "diag_name": "Diagrama de Comunicación – CU19: Derivación Psiquiátrica",
            "img_name": "diagrama_comunicacion_cu19.png",
            "actor_name": "Psicólogo Tratante",
            "iu_name": "IU_DerivacionCierre\n(Angular 17)",
            "ctr_name": "CTR_DerivacionService\n(Django REST)",
            "ce_name": "CE_DerivacionCaso\n(PostgreSQL)",
            "msgs": [
                (1, 2, "1: Emitir orden clínica de interconsulta médica", "SX=0;SY=18;EX=0;EY=18;"),
                (2, 1, "8: Descargar PDF oficial y confirmar envío", "SX=0;SY=-18;EX=0;EY=-18;"),
                (2, 3, "2: POST /api/v1/derivaciones/ + datos orden", "SX=0;SY=18;EX=0;EY=18;"),
                (3, 2, "7: 201 Created {pdf_url, notif_coordinador}", "SX=0;SY=-18;EX=0;EY=-18;"),
                (3, 4, "3: Compilar PDF con sello profesional y hash", "SX=0;SY=28;EX=0;EY=28;"),
                (4, 3, "4: Expediente activo y validación completada", "SX=0;SY=12;EX=0;EY=12;"),
                (3, 4, "5: INSERT INTO clinica_derivacioncaso (DERIVADO)", "SX=0;SY=-12;EX=0;EY=-12;"),
                (4, 3, "6: Orden de interconsulta registrada en tenant", "SX=0;SY=-28;EX=0;EY=-28;"),
            ]
        },
        {
            "sub_name": "HU-35 - Consentimiento y Pasarela Ética de IA",
            "diag_name": "Diagrama de Comunicación – HU-35: Pasarela IA Asistiva",
            "img_name": "diagrama_comunicacion_hu35.png",
            "actor_name": "Psicólogo Tratante",
            "iu_name": "IU_PanelAsistenteIA\n(Angular 17)",
            "ctr_name": "CTR_PasarelaIAService\n(Django / Celery)",
            "ce_name": "CE_AuditoriaIA\n(PostgreSQL)",
            "msgs": [
                (1, 2, "1: Solicitar análisis asistivo de intake", "SX=0;SY=18;EX=0;EY=18;"),
                (2, 1, "8: Renderizar borrador con aviso de revisión humana", "SX=0;SY=-18;EX=0;EY=-18;"),
                (2, 3, "2: POST /api/v1/ia/preconsulta/analizar/", "SX=0;SY=18;EX=0;EY=18;"),
                (3, 2, "7: 200 OK {borrador_neutral, reglas_explicadas}", "SX=0;SY=-18;EX=0;EY=-18;"),
                (3, 4, "3: Verificar consentimiento activo y filtrar PII", "SX=0;SY=28;EX=0;EY=28;"),
                (4, 3, "4: Consentimiento validado y datos anonimizados", "SX=0;SY=12;EX=0;EY=12;"),
                (3, 4, "5: INSERT INTO auditoria_registro_ia (hash, prompt)", "SX=0;SY=-12;EX=0;EY=-12;"),
                (4, 3, "6: Auditoría inmutable guardada para supervisión", "SX=0;SY=-28;EX=0;EY=-28;"),
            ]
        }
    ]

    img_dir = os.path.abspath(r"c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\documentacion\imagenes")
    pi = ea_repo.GetProjectInterface()

    for spec in comm_specs:
        print(f"Building communication diagram: {spec['sub_name']}...")
        sub_pkg = comm_pkg.Packages.AddNew(spec["sub_name"], "")
        sub_pkg.Update()
        comm_pkg.Packages.Refresh()

        diag = sub_pkg.Diagrams.AddNew(spec["diag_name"], "Communication")
        diag.Update()
        sub_pkg.Diagrams.Refresh()

        # Elements BCE with exact positions and stereotypes
        # Actor
        e_actor = sub_pkg.Elements.AddNew(spec["actor_name"], "Actor")
        e_actor.Update()
        # Boundary
        e_iu = sub_pkg.Elements.AddNew(spec["iu_name"], "Class")
        e_iu.Stereotype = "boundary"
        e_iu.Update()
        # Control
        e_ctr = sub_pkg.Elements.AddNew(spec["ctr_name"], "Class")
        e_ctr.Stereotype = "control"
        e_ctr.Update()
        # Entity
        e_ce = sub_pkg.Elements.AddNew(spec["ce_name"], "Class")
        e_ce.Stereotype = "entity"
        e_ce.Update()

        sub_pkg.Elements.Refresh()

        # Exact layout positions from CU6:
        # Actor: (60, -80, 150, -180)
        # IU: (420, -80, 510, -180)
        # CTR: (920, -80, 1010, -180)
        # CE: (1460, -80, 1550, -180)
        elems = [None, e_actor, e_iu, e_ctr, e_ce]
        rects = [None, (60, -80, 150, -180), (420, -80, 510, -180), (920, -80, 1010, -180), (1460, -80, 1550, -180)]

        for idx in range(1, 5):
            el = elems[idx]
            l, t, r, b = rects[idx]
            pos_str = f"l={l};r={r};t={t};b={b};"
            do = diag.DiagramObjects.AddNew(pos_str, "")
            do.ElementID = el.ElementID
            do.left = l
            do.top = t
            do.right = r
            do.bottom = b
            do.Update()

        diag.DiagramObjects.Refresh()

        # Connectors with Direction="Source -> Destination"
        connectors_map = []
        for src_idx, tgt_idx, msg_name, geom in spec["msgs"]:
            src_el = elems[src_idx]
            tgt_el = elems[tgt_idx]
            c = src_el.Connectors.AddNew(msg_name, "ControlFlow")
            c.SupplierID = tgt_el.ElementID
            c.Direction = "Source -> Destination"
            c.Update()
            src_el.Connectors.Refresh()
            connectors_map.append((c.ConnectorID, geom))

        diag.Update()
        ea_repo.ReloadDiagram(diag.DiagramID)

        # Set DiagramLink Geometry
        for dl in diag.DiagramLinks:
            conn_id = dl.ConnectorID
            for c_id, geom in connectors_map:
                if conn_id == c_id:
                    dl.Geometry = geom
                    dl.Update()
                    break

        diag.DiagramLinks.Refresh()
        diag.Update()
        ea_repo.ReloadDiagram(diag.DiagramID)

        # Export image
        out_path = os.path.join(img_dir, spec["img_name"])
        try:
            pi.PutDiagramImageToFile(diag.DiagramGUID, out_path, 1)
            print(f"Exported: {spec['diag_name']} -> {out_path}")
        except Exception as e:
            print(f"Error exporting {spec['diag_name']}: {e}")

    ea_repo.CloseFile()
    ea_repo.Exit()
    print("ALL BCE COMMUNICATION DIAGRAMS SUCCESSFULLY REBUILT WITH PERFECT GEOMETRY!")

if __name__ == "__main__":
    rebuild_all_communication()
