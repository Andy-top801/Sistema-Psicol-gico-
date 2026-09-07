import win32com.client
import sys
import os

def create_sprint1_incremental_diagrams():
    eapx_path = r'c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\diagramas\DIAGRAMAS.eapx'
    
    print("Iniciando Enterprise Architect...")
    ea = win32com.client.Dispatch('EA.App')
    repo = ea.Repository
    
    if not repo.OpenFile(eapx_path):
        print(f"Error: No se pudo abrir el archivo {eapx_path}")
        return False
        
    print("Archivo DIAGRAMAS.eapx abierto exitosamente.")
    
    # Obtener el modelo raíz
    root_model = repo.Models.GetAt(0)
    print(f"Modelo raíz: {root_model.Name}")
    
    # Limpiar cualquier versión previa de 'sprint 1' o 'Sprint 1'
    for i in range(root_model.Packages.Count - 1, -1, -1):
        pkg = root_model.Packages.GetAt(i)
        if pkg.Name.lower() == "sprint 1" or pkg.Name == "temp_test":
            print(f"Eliminando paquete existente '{pkg.Name}' para recrear limpiamente con modelo incremental...")
            root_model.Packages.Delete(i)
            
    root_model.Packages.Refresh()
    
    # Crear nueva carpeta / paquete llamada 'sprint 1'
    sprint1_pkg = root_model.Packages.AddNew("sprint 1", "Package")
    sprint1_pkg.Update()
    root_model.Packages.Refresh()
    print("Carpeta 'sprint 1' creada exitosamente.")
    
    # Helper function to add diagram object
    def add_diag_obj(diag, elem, left, top, right, bottom):
        diag_obj = diag.DiagramObjects.AddNew(f"l={left};r={right};t={top};b={bottom};", "")
        diag_obj.ElementID = elem.ElementID
        diag_obj.left = left
        diag_obj.top = top
        diag_obj.right = right
        diag_obj.bottom = bottom
        diag_obj.Update()
        return diag_obj

    # Helper function to create connector with cardinalities and aggregation
    def add_connector(source_elem, target_elem, conn_type, name="", stereotype="", 
                      client_card="", supplier_card="", aggregation=0):
        conn = source_elem.Connectors.AddNew(name, conn_type)
        conn.SupplierID = target_elem.ElementID
        if stereotype:
            conn.Stereotype = stereotype
        if client_card:
            conn.ClientEnd.Cardinality = client_card
        if supplier_card:
            conn.SupplierEnd.Cardinality = supplier_card
        if aggregation:
            conn.ClientEnd.Aggregation = aggregation  # 1 = shared, 2 = composite
        conn.Update()
        source_elem.Connectors.Refresh()
        return conn

    # Helper function to add attributes
    def add_attrs(elem, attrs):
        for name, typ in attrs:
            att = elem.Attributes.AddNew(name, typ)
            att.Update()
        elem.Attributes.Refresh()
        
    # Helper function to add methods
    def add_methods(elem, methods):
        for name, ret in methods:
            m = elem.Methods.AddNew(name, ret)
            m.Update()
        elem.Methods.Refresh()

    # =========================================================================
    # 1. DIAGRAMA DE CASOS DE USO DEL SPRINT 1 (INCREMENTAL SPRINT 0 + SPRINT 1)
    # =========================================================================
    print("\n--- 1. Creando Diagrama de Casos de Uso Incremental (Sprint 0 + Sprint 1) ---")
    cu_pkg = sprint1_pkg.Packages.AddNew("1. Casos de Uso - Sprint 1", "Package")
    cu_pkg.Update()
    
    cu_diag = cu_pkg.Diagrams.AddNew("Diagrama de Casos de Uso - Sprint 1 Incremental", "Use Case")
    cu_diag.Update()
    
    # Actores (6 actores completos)
    act_super = cu_pkg.Elements.AddNew("SuperAdministrador\n(Plataforma)", "Actor")
    act_super.Update()
    
    act_admin = cu_pkg.Elements.AddNew("Administrador del Centro", "Actor")
    act_admin.Update()
    
    act_coord = cu_pkg.Elements.AddNew("Coordinador Clínico", "Actor")
    act_coord.Update()
    
    act_psyc = cu_pkg.Elements.AddNew("Psicólogo", "Actor")
    act_psyc.Update()
    
    act_recep = cu_pkg.Elements.AddNew("Recepcionista", "Actor")
    act_recep.Update()
    
    act_patient = cu_pkg.Elements.AddNew("Paciente\n(Web / Móvil)", "Actor")
    act_patient.Update()
    
    # Casos de Uso Base Sprint 0
    cu1 = cu_pkg.Elements.AddNew("CU1: Gestionar centros psicológicos y Multi-Tenant", "UseCase")
    cu1.Update()
    
    cu2 = cu_pkg.Elements.AddNew("CU2: Autenticar e iniciar sesión (JWT)", "UseCase")
    cu2.Update()
    
    cu3 = cu_pkg.Elements.AddNew("CU3: Gestionar usuarios institucionales", "UseCase")
    cu3.Update()
    
    cu4 = cu_pkg.Elements.AddNew("CU4: Gestionar roles y permisos (RBAC)", "UseCase")
    cu4.Update()
    
    cu27 = cu_pkg.Elements.AddNew("CU27: Recuperar credenciales y contraseña", "UseCase")
    cu27.Update()
    
    # Casos de Uso Incremento Sprint 1
    cu6 = cu_pkg.Elements.AddNew("CU6: Gestionar psicólogos y perfiles profesionales", "UseCase")
    cu6.Update()
    
    cu8 = cu_pkg.Elements.AddNew("CU8: Configurar disponibilidad horaria y carga de trabajo", "UseCase")
    cu8.Update()
    
    cu7 = cu_pkg.Elements.AddNew("CU7: Gestionar expediente y datos de pacientes", "UseCase")
    cu7.Update()
    
    cu11 = cu_pkg.Elements.AddNew("CU11: Gestionar citas y agenda psicológica", "UseCase")
    cu11.Update()
    
    cu13 = cu_pkg.Elements.AddNew("CU13: Realizar teleconsulta y videoconferencia (Jitsi)", "UseCase")
    cu13.Update()
    
    cu9 = cu_pkg.Elements.AddNew("CU9: Consultar Dashboard e indicadores del centro", "UseCase")
    cu9.Update()
    
    cu10 = cu_pkg.Elements.AddNew("CU10: Gestionar alertas de priorización y seguimiento", "UseCase")
    cu10.Update()
    
    val_overlap = cu_pkg.Elements.AddNew("Validar colisión de horarios", "UseCase")
    val_overlap.Update()
    
    # Conectores de Actores
    # SuperAdmin
    add_connector(act_super, cu1, "Association")
    
    # Admin
    add_connector(act_admin, cu2, "Association")
    add_connector(act_admin, cu3, "Association")
    add_connector(act_admin, cu4, "Association")
    add_connector(act_admin, cu6, "Association")
    add_connector(act_admin, cu7, "Association")
    add_connector(act_admin, cu9, "Association")
    
    # Coord
    add_connector(act_coord, cu2, "Association")
    add_connector(act_coord, cu6, "Association")
    add_connector(act_coord, cu9, "Association")
    add_connector(act_coord, cu10, "Association")
    add_connector(act_coord, cu11, "Association")
    
    # Psicólogo
    add_connector(act_psyc, cu2, "Association")
    add_connector(act_psyc, cu8, "Association")
    add_connector(act_psyc, cu11, "Association")
    add_connector(act_psyc, cu13, "Association")
    add_connector(act_psyc, cu10, "Association")
    
    # Recepcionista
    add_connector(act_recep, cu2, "Association")
    add_connector(act_recep, cu7, "Association")
    add_connector(act_recep, cu11, "Association")
    
    # Paciente
    add_connector(act_patient, cu2, "Association")
    add_connector(act_patient, cu27, "Association")
    add_connector(act_patient, cu7, "Association")
    add_connector(act_patient, cu11, "Association")
    add_connector(act_patient, cu13, "Association")
    
    # Inclusiones
    add_connector(cu11, val_overlap, "UseCase", "", "include")
    add_connector(cu6, cu2, "UseCase", "", "include")
    add_connector(cu7, cu2, "UseCase", "", "include")
    add_connector(cu11, cu2, "UseCase", "", "include")
    add_connector(cu13, cu2, "UseCase", "", "include")
    add_connector(cu9, cu2, "UseCase", "", "include")
    add_connector(cu3, cu2, "UseCase", "", "include")
    add_connector(cu4, cu2, "UseCase", "", "include")
    
    # Layout en Diagrama de Casos de Uso
    # Columna 1: Actores
    add_diag_obj(cu_diag, act_super, 40, -40, 160, -140)
    add_diag_obj(cu_diag, act_admin, 40, -160, 160, -260)
    add_diag_obj(cu_diag, act_coord, 40, -280, 160, -380)
    add_diag_obj(cu_diag, act_psyc, 40, -400, 160, -500)
    add_diag_obj(cu_diag, act_recep, 40, -520, 160, -620)
    add_diag_obj(cu_diag, act_patient, 40, -640, 160, -740)
    
    # Columna 2: Casos de Uso Sprint 0 (arriba) y Sprint 1 (abajo)
    add_diag_obj(cu_diag, cu1, 260, -40, 520, -100)
    add_diag_obj(cu_diag, cu3, 260, -120, 520, -180)
    add_diag_obj(cu_diag, cu4, 260, -200, 520, -260)
    add_diag_obj(cu_diag, cu27, 260, -280, 520, -340)
    
    add_diag_obj(cu_diag, cu6, 260, -370, 520, -430)
    add_diag_obj(cu_diag, cu8, 260, -450, 520, -510)
    add_diag_obj(cu_diag, cu7, 260, -530, 520, -590)
    add_diag_obj(cu_diag, cu11, 260, -610, 520, -670)
    add_diag_obj(cu_diag, cu13, 260, -690, 520, -750)
    add_diag_obj(cu_diag, cu9, 260, -770, 520, -830)
    add_diag_obj(cu_diag, cu10, 260, -850, 520, -910)
    
    # Columna 3: Includes
    add_diag_obj(cu_diag, cu2, 600, -200, 840, -270)
    add_diag_obj(cu_diag, val_overlap, 600, -610, 840, -680)
    
    cu_diag.Update()
    print("1. Diagrama de Casos de Uso Incremental creado.")

    # =========================================================================
    # 2. DIAGRAMA DE CLASES DEL SPRINT 1 (MODELO INCREMENTAL SPRINT 0 + SPRINT 1)
    # =========================================================================
    print("\n--- 2. Creando Diagrama de Clases Incremental (Sprint 0 + Sprint 1) ---")
    cl_pkg = sprint1_pkg.Packages.AddNew("2. Clases - Sprint 1", "Package")
    cl_pkg.Update()
    
    cl_diag = cl_pkg.Diagrams.AddNew("Diagrama de Clases - Sprint 1 Incremental", "Class")
    cl_diag.Update()
    
    # --- CLASES DEL SPRINT 0 (ESQUEMA PUBLIC) ---
    c_tenant = cl_pkg.Elements.AddNew("Tenant", "Class")
    add_attrs(c_tenant, [
        ("id", "UUID"),
        ("nombre", "String"),
        ("slug", "String"),
        ("schema_name", "String"),
        ("plan", "String"),
        ("activo", "Boolean"),
        ("fecha_creacion", "DateTime")
    ])
    add_methods(c_tenant, [("crear_esquema", "void"), ("suspender", "void")])
    c_tenant.Update()
    
    c_dom = cl_pkg.Elements.AddNew("Dominio", "Class")
    add_attrs(c_dom, [("id", "Integer"), ("dominio", "String"), ("es_primario", "Boolean")])
    c_dom.Update()
    
    c_super = cl_pkg.Elements.AddNew("SuperAdmin", "Class")
    add_attrs(c_super, [
        ("id", "Integer"),
        ("email", "String"),
        ("password_hash", "String"),
        ("nombre", "String"),
        ("activo", "Boolean")
    ])
    add_methods(c_super, [("gestionar_tenants", "void")])
    c_super.Update()
    
    # --- CLASES DEL SPRINT 0 (ESQUEMA TENANT) ---
    c_centro = cl_pkg.Elements.AddNew("Centro", "Class")
    add_attrs(c_centro, [
        ("id", "UUID"),
        ("nombre", "String"),
        ("direccion", "String"),
        ("telefono", "String"),
        ("email", "String"),
        ("logo", "String"),
        ("horarios_atencion", "JSON")
    ])
    add_methods(c_centro, [("actualizar_config", "void")])
    c_centro.Update()
    
    c_user = cl_pkg.Elements.AddNew("Usuario", "Class")
    add_attrs(c_user, [
        ("id", "UUID"),
        ("email", "String"),
        ("password_hash", "String"),
        ("nombre", "String"),
        ("apellido", "String"),
        ("telefono", "String"),
        ("activo", "Boolean"),
        ("fecha_creacion", "DateTime")
    ])
    add_methods(c_user, [("autenticar", "Boolean"), ("cerrar_sesion", "void")])
    c_user.Update()
    
    c_rol = cl_pkg.Elements.AddNew("Rol", "Class")
    add_attrs(c_rol, [("id", "Integer"), ("nombre", "String"), ("descripcion", "String")])
    c_rol.Update()
    
    c_perm = cl_pkg.Elements.AddNew("Permiso", "Class")
    add_attrs(c_perm, [("id", "Integer"), ("nombre", "String"), ("codigo", "String"), ("modulo", "String")])
    c_perm.Update()
    
    c_tok_acc = cl_pkg.Elements.AddNew("TokenAcceso", "Class")
    add_attrs(c_tok_acc, [("id", "UUID"), ("token_jwt", "String"), ("fecha_expiracion", "DateTime")])
    add_methods(c_tok_acc, [("es_valido", "Boolean")])
    c_tok_acc.Update()
    
    c_tok_rec = cl_pkg.Elements.AddNew("TokenRecuperacion", "Class")
    add_attrs(c_tok_rec, [("id", "UUID"), ("token", "String"), ("fecha_expiracion", "DateTime"), ("usado", "Boolean")])
    add_methods(c_tok_rec, [("validar_token", "Boolean")])
    c_tok_rec.Update()
    
    # --- CLASES DEL SPRINT 1 (ESQUEMA TENANT - INCREMENTO CLÍNICO & AGENDA) ---
    c_psyc = cl_pkg.Elements.AddNew("Psicologo", "Class")
    add_attrs(c_psyc, [
        ("id", "UUID"),
        ("numero_colegiado", "String"),
        ("biografia", "Text"),
        ("modalidad", "String"),
        ("tarifa_base", "Decimal"),
        ("activo", "Boolean")
    ])
    add_methods(c_psyc, [("obtener_carga_semanal", "Integer")])
    c_psyc.Update()
    
    c_esp = cl_pkg.Elements.AddNew("Especialidad", "Class")
    add_attrs(c_esp, [("id", "Integer"), ("nombre", "String"), ("descripcion", "String")])
    c_esp.Update()
    
    c_disp = cl_pkg.Elements.AddNew("DisponibilidadHoraria", "Class")
    add_attrs(c_disp, [
        ("id", "UUID"),
        ("dia_semana", "Integer"),
        ("hora_inicio", "Time"),
        ("hora_fin", "Time"),
        ("duracion_bloque_min", "Integer"),
        ("activo", "Boolean")
    ])
    add_methods(c_disp, [("es_bloque_valido", "Boolean")])
    c_disp.Update()
    
    c_pac = cl_pkg.Elements.AddNew("Paciente", "Class")
    add_attrs(c_pac, [
        ("id", "UUID"),
        ("codigo_expediente", "String"),
        ("ci", "String"),
        ("fecha_nacimiento", "Date"),
        ("genero", "String"),
        ("contacto_emergencia_nombre", "String"),
        ("contacto_emergencia_telf", "String")
    ])
    add_methods(c_pac, [("es_menor_edad", "Boolean")])
    c_pac.Update()
    
    c_cita = cl_pkg.Elements.AddNew("Cita", "Class")
    add_attrs(c_cita, [
        ("id", "UUID"),
        ("fecha", "Date"),
        ("hora_inicio", "Time"),
        ("hora_fin", "Time"),
        ("modalidad", "String"),
        ("estado", "String"),
        ("motivo_consulta", "Text"),
        ("costo", "Decimal")
    ])
    add_methods(c_cita, [("reprogramar", "void"), ("cancelar", "void")])
    c_cita.Update()
    
    c_tele = cl_pkg.Elements.AddNew("Teleconsulta", "Class")
    add_attrs(c_tele, [
        ("id", "UUID"),
        ("sala_id", "String"),
        ("jwt_room_token", "String"),
        ("duracion_segundos", "Integer"),
        ("estado_conexion", "String")
    ])
    add_methods(c_tele, [("iniciar_sala", "String"), ("finalizar_sala", "void")])
    c_tele.Update()
    
    c_alerta = cl_pkg.Elements.AddNew("AlertaPriorizacion", "Class")
    add_attrs(c_alerta, [
        ("id", "UUID"),
        ("tipo", "String"),
        ("severidad", "String"),
        ("descripcion", "Text"),
        ("resuelta", "Boolean"),
        ("fecha_creacion", "DateTime")
    ])
    add_methods(c_alerta, [("resolver", "void")])
    c_alerta.Update()
    
    # --- RELACIONES CON CARDINALIDADES EXPLÍCITAS ---
    # Globales Sprint 0
    add_connector(c_tenant, c_dom, "Aggregation", "posee", client_card="1", supplier_card="1..*", aggregation=2)
    add_connector(c_tenant, c_centro, "Association", "aprovisiona", client_card="1", supplier_card="1")
    add_connector(c_super, c_tenant, "Dependency", "administra")
    
    # Base Tenant Sprint 0
    add_connector(c_centro, c_user, "Aggregation", "agrupa", client_card="1", supplier_card="0..*", aggregation=2)
    add_connector(c_centro, c_cita, "Aggregation", "registra", client_card="1", supplier_card="0..*", aggregation=2)
    add_connector(c_user, c_rol, "Aggregation", "asignado", client_card="0..*", supplier_card="1", aggregation=1)
    add_connector(c_rol, c_perm, "Aggregation", "concede", client_card="0..*", supplier_card="1..*", aggregation=1)
    add_connector(c_user, c_tok_acc, "Aggregation", "genera", client_card="1", supplier_card="0..*", aggregation=2)
    add_connector(c_user, c_tok_rec, "Aggregation", "solicita", client_card="1", supplier_card="0..*", aggregation=2)
    
    # Incrementales Sprint 1
    add_connector(c_user, c_psyc, "Association", "perfil profesional", client_card="1", supplier_card="0..1")
    add_connector(c_user, c_pac, "Association", "perfil clínico", client_card="1", supplier_card="0..1")
    add_connector(c_psyc, c_disp, "Aggregation", "programa", client_card="1", supplier_card="1..*", aggregation=2)
    add_connector(c_psyc, c_esp, "Association", "acredita", client_card="0..*", supplier_card="1..*")
    add_connector(c_psyc, c_cita, "Association", "atiende", client_card="1", supplier_card="0..*")
    add_connector(c_pac, c_cita, "Association", "agenda", client_card="1", supplier_card="0..*")
    add_connector(c_cita, c_tele, "Aggregation", "genera", client_card="1", supplier_card="0..1", aggregation=2)
    add_connector(c_pac, c_alerta, "Association", "origina", client_card="1", supplier_card="0..*")
    
    # --- LAYOUT LIMPIO EN EL DIAGRAMA DE CLASES ---
    # Nivel 0 (Esquema Public - Superior):
    add_diag_obj(cl_diag, c_super, 80, -40, 260, -170)
    add_diag_obj(cl_diag, c_tenant, 340, -40, 560, -210)
    add_diag_obj(cl_diag, c_dom, 640, -40, 820, -140)
    
    # Nivel 1 (Centro y Autenticación):
    add_diag_obj(cl_diag, c_centro, 340, -270, 560, -430)
    add_diag_obj(cl_diag, c_tok_acc, 80, -270, 260, -380)
    add_diag_obj(cl_diag, c_tok_rec, 80, -420, 260, -540)
    add_diag_obj(cl_diag, c_user, 640, -270, 860, -470)
    add_diag_obj(cl_diag, c_rol, 940, -270, 1120, -380)
    add_diag_obj(cl_diag, c_perm, 940, -420, 1120, -540)
    
    # Nivel 2 (Perfiles Sprint 1: Psicólogo y Paciente):
    add_diag_obj(cl_diag, c_esp, 80, -600, 260, -710)
    add_diag_obj(cl_diag, c_psyc, 340, -600, 560, -780)
    add_diag_obj(cl_diag, c_pac, 640, -600, 860, -780)
    add_diag_obj(cl_diag, c_alerta, 940, -600, 1140, -780)
    
    # Nivel 3 (Agenda, Disponibilidad y Teleconsulta):
    add_diag_obj(cl_diag, c_disp, 340, -840, 560, -1020)
    add_diag_obj(cl_diag, c_cita, 640, -840, 860, -1040)
    add_diag_obj(cl_diag, c_tele, 940, -840, 1160, -1000)
    
    cl_diag.Update()
    print("2. Diagrama de Clases Incremental creado exitosamente con las 16 clases.")

    # =========================================================================
    # 3. DIAGRAMA DE ACTIVIDAD: RESERVA Y PROGRAMACIÓN DE CITA
    # =========================================================================
    print("\n--- 3. Creando Diagrama de Actividad (Reserva de Cita) ---")
    act_pkg = sprint1_pkg.Packages.AddNew("3. Actividad - Reserva de Cita", "Package")
    act_pkg.Update()
    
    act_diag = act_pkg.Diagrams.AddNew("Diagrama de Actividad - Reserva de Cita", "Activity")
    act_diag.Update()
    
    a_init = act_pkg.Elements.AddNew("", "StateNode")
    a_init.Subtype = 100
    a_init.Update()
    
    a1 = act_pkg.Elements.AddNew("Usuario abre formulario de agendamiento y selecciona especialidad", "Activity")
    a1.Update()
    
    a2 = act_pkg.Elements.AddNew("Sistema consulta disponibilidad y despliega bloques libres", "Activity")
    a2.Update()
    
    a3 = act_pkg.Elements.AddNew("Usuario selecciona fecha, hora y envía solicitud de reserva", "Activity")
    a3.Update()
    
    a_dec_ov = act_pkg.Elements.AddNew("¿Existe solapamiento de horario?", "Decision")
    a_dec_ov.Update()
    
    a_err_ov = act_pkg.Elements.AddNew("Rollback y retornar HTTP 409: Horario previamente reservado", "Activity")
    a_err_ov.Update()
    
    a_crear_cita = act_pkg.Elements.AddNew("Crear registro agenda_cita (estado = Programada)", "Activity")
    a_crear_cita.Update()
    
    a_dec_mod = act_pkg.Elements.AddNew("¿Modalidad es Virtual?", "Decision")
    a_dec_mod.Update()
    
    a_crear_tele = act_pkg.Elements.AddNew("Generar sala única Jitsi y registrar en agenda_teleconsulta", "Activity")
    a_crear_tele.Update()
    
    a_consul = act_pkg.Elements.AddNew("Asignar consultorio físico según configuración del centro", "Activity")
    a_consul.Update()
    
    a_commit = act_pkg.Elements.AddNew("Commit transacción, emitir notificación y retornar HTTP 201", "Activity")
    a_commit.Update()
    
    a_final = act_pkg.Elements.AddNew("", "StateNode")
    a_final.Subtype = 101
    a_final.Update()
    
    # Conectores de flujo
    add_connector(a_init, a1, "ControlFlow")
    add_connector(a1, a2, "ControlFlow")
    add_connector(a2, a3, "ControlFlow")
    add_connector(a3, a_dec_ov, "ControlFlow")
    add_connector(a_dec_ov, a_err_ov, "ControlFlow", "Sí [Colisión]")
    add_connector(a_err_ov, a_final, "ControlFlow")
    add_connector(a_dec_ov, a_crear_cita, "ControlFlow", "No [Disponible]")
    add_connector(a_crear_cita, a_dec_mod, "ControlFlow")
    add_connector(a_dec_mod, a_crear_tele, "ControlFlow", "Sí [Virtual]")
    add_connector(a_dec_mod, a_consul, "ControlFlow", "No [Presencial]")
    add_connector(a_crear_tele, a_commit, "ControlFlow")
    add_connector(a_consul, a_commit, "ControlFlow")
    add_connector(a_commit, a_final, "ControlFlow")
    
    add_diag_obj(act_diag, a_init, 200, -20, 220, -40)
    add_diag_obj(act_diag, a1, 100, -70, 320, -120)
    add_diag_obj(act_diag, a2, 100, -150, 320, -200)
    add_diag_obj(act_diag, a3, 100, -230, 320, -280)
    add_diag_obj(act_diag, a_dec_ov, 180, -320, 240, -360)
    add_diag_obj(act_diag, a_err_ov, 380, -315, 600, -365)
    add_diag_obj(act_diag, a_crear_cita, 100, -400, 320, -450)
    add_diag_obj(act_diag, a_dec_mod, 180, -490, 240, -530)
    add_diag_obj(act_diag, a_crear_tele, 40, -570, 220, -620)
    add_diag_obj(act_diag, a_consul, 260, -570, 440, -620)
    add_diag_obj(act_diag, a_commit, 120, -660, 340, -710)
    add_diag_obj(act_diag, a_final, 220, -750, 240, -770)
    
    act_diag.Update()
    print("3. Diagrama de Actividad (Reserva de Cita) creado correctamente.")

    # =========================================================================
    # 4. DIAGRAMA DE ACTIVIDAD: TELECONSULTA JITSI MEET
    # =========================================================================
    print("\n--- 4. Creando Diagrama de Actividad (Teleconsulta Jitsi Meet) ---")
    tele_pkg = sprint1_pkg.Packages.AddNew("4. Actividad - Teleconsulta Jitsi Meet", "Package")
    tele_pkg.Update()
    
    tele_diag = tele_pkg.Diagrams.AddNew("Diagrama de Actividad - Teleconsulta Jitsi", "Activity")
    tele_diag.Update()
    
    t_init = tele_pkg.Elements.AddNew("", "StateNode")
    t_init.Subtype = 100
    t_init.Update()
    
    t1 = tele_pkg.Elements.AddNew("Usuario accede a cita virtual y solicita acceso GET /teleconsulta/access/", "Activity")
    t1.Update()
    
    t_dec_time = tele_pkg.Elements.AddNew("¿Ventana horaria válida (±15 min)?", "Decision")
    t_dec_time.Update()
    
    t_err_time = tele_pkg.Elements.AddNew("Retornar HTTP 403: Sala disponible únicamente en horario pactado", "Activity")
    t_err_time.Update()
    
    t2 = tele_pkg.Elements.AddNew("Generar JWT Room Token, claims de moderador e instanciar WebRTC (Angular/Flutter)", "Activity")
    t2.Update()
    
    t3 = tele_pkg.Elements.AddNew("Sesión terapéutica en curso: transmisión de audio/video y chat cifrado", "Activity")
    t3.Update()
    
    t4 = tele_pkg.Elements.AddNew("Psicólogo presiona 'Finalizar Consulta': desconectar WebRTC y enviar POST /finish/", "Activity")
    t4.Update()
    
    t5 = tele_pkg.Elements.AddNew("Guardar duración real en agenda_teleconsulta y marcar cita como 'Realizada'", "Activity")
    t5.Update()
    
    t_final = tele_pkg.Elements.AddNew("", "StateNode")
    t_final.Subtype = 101
    t_final.Update()
    
    add_connector(t_init, t1, "ControlFlow")
    add_connector(t1, t_dec_time, "ControlFlow")
    add_connector(t_dec_time, t_err_time, "ControlFlow", "No")
    add_connector(t_err_time, t_final, "ControlFlow")
    add_connector(t_dec_time, t2, "ControlFlow", "Sí")
    add_connector(t2, t3, "ControlFlow")
    add_connector(t3, t4, "ControlFlow")
    add_connector(t4, t5, "ControlFlow")
    add_connector(t5, t_final, "ControlFlow")
    
    add_diag_obj(tele_diag, t_init, 200, -20, 220, -40)
    add_diag_obj(tele_diag, t1, 80, -70, 340, -120)
    add_diag_obj(tele_diag, t_dec_time, 180, -160, 240, -200)
    add_diag_obj(tele_diag, t_err_time, 380, -155, 620, -205)
    add_diag_obj(tele_diag, t2, 80, -240, 340, -300)
    add_diag_obj(tele_diag, t3, 80, -340, 340, -390)
    add_diag_obj(tele_diag, t4, 80, -430, 340, -490)
    add_diag_obj(tele_diag, t5, 80, -530, 340, -580)
    add_diag_obj(tele_diag, t_final, 200, -620, 220, -640)
    
    tele_diag.Update()
    print("4. Diagrama de Actividad (Teleconsulta Jitsi) creado correctamente.")
    
    # Guardar y cerrar repositorio
    print("\nGuardando cambios en Enterprise Architect...", flush=True)
    sprint1_pkg.Packages.Refresh()
    repo.RefreshModelView(0)
    repo.CloseFile()
    repo.Exit()
    print("\n¡Todos los diagramas del Sprint 1 (Modelo Incremental) se han generado y guardado exitosamente en DIAGRAMAS.eapx!", flush=True)
    return True

if __name__ == '__main__':
    create_sprint1_incremental_diagrams()

