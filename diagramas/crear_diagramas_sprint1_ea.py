import win32com.client
import sys
import os

def create_sprint1_diagrams():
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
            print(f"Eliminando paquete existente '{pkg.Name}' para recrear limpiamente...")
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
    # 1. DIAGRAMA DE CASOS DE USO DEL SPRINT 1
    # =========================================================================
    print("\n--- 1. Creando Diagrama de Casos de Uso (Sprint 1) ---")
    cu_pkg = sprint1_pkg.Packages.AddNew("1. Casos de Uso - Sprint 1", "Package")
    cu_pkg.Update()
    
    cu_diag = cu_pkg.Diagrams.AddNew("Diagrama de Casos de Uso - Sprint 1", "Use Case")
    cu_diag.Update()
    
    # Actores
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
    
    # Casos de Uso
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
    
    auth = cu_pkg.Elements.AddNew("Autenticar sesión JWT y Tenant", "UseCase")
    auth.Update()
    
    # Asociaciones de Actores a Casos de Uso
    # Admin
    add_connector(act_admin, cu6, "Association")
    add_connector(act_admin, cu7, "Association")
    add_connector(act_admin, cu9, "Association")
    
    # Coordinador
    add_connector(act_coord, cu6, "Association")
    add_connector(act_coord, cu9, "Association")
    add_connector(act_coord, cu10, "Association")
    add_connector(act_coord, cu11, "Association")
    
    # Psicólogo
    add_connector(act_psyc, cu8, "Association")
    add_connector(act_psyc, cu11, "Association")
    add_connector(act_psyc, cu13, "Association")
    add_connector(act_psyc, cu10, "Association")
    
    # Recepcionista
    add_connector(act_recep, cu7, "Association")
    add_connector(act_recep, cu11, "Association")
    
    # Paciente
    add_connector(act_patient, cu7, "Association")
    add_connector(act_patient, cu11, "Association")
    add_connector(act_patient, cu13, "Association")
    
    # Relaciones <<include>>
    add_connector(cu11, val_overlap, "UseCase", "", "include")
    add_connector(cu6, auth, "UseCase", "", "include")
    add_connector(cu7, auth, "UseCase", "", "include")
    add_connector(cu11, auth, "UseCase", "", "include")
    add_connector(cu13, auth, "UseCase", "", "include")
    add_connector(cu9, auth, "UseCase", "", "include")
    
    # Posicionamiento en diagrama
    # Columna 1: Actores
    add_diag_obj(cu_diag, act_admin, 60, -60, 180, -160)
    add_diag_obj(cu_diag, act_coord, 60, -200, 180, -300)
    add_diag_obj(cu_diag, act_psyc, 60, -340, 180, -440)
    add_diag_obj(cu_diag, act_recep, 60, -480, 180, -580)
    add_diag_obj(cu_diag, act_patient, 60, -620, 180, -720)
    
    # Columna 2: Casos de Uso
    add_diag_obj(cu_diag, cu6, 300, -50, 560, -120)
    add_diag_obj(cu_diag, cu9, 300, -150, 560, -220)
    add_diag_obj(cu_diag, cu10, 300, -250, 560, -320)
    add_diag_obj(cu_diag, cu8, 300, -350, 560, -420)
    add_diag_obj(cu_diag, cu11, 300, -450, 560, -520)
    add_diag_obj(cu_diag, cu7, 300, -550, 560, -620)
    add_diag_obj(cu_diag, cu13, 300, -650, 560, -720)
    
    # Columna 3: Includes
    add_diag_obj(cu_diag, auth, 680, -220, 920, -290)
    add_diag_obj(cu_diag, val_overlap, 680, -450, 920, -520)
    
    cu_diag.Update()
    print("1. Diagrama de Casos de Uso creado correctamente.")

    # =========================================================================
    # 2. DIAGRAMA DE CLASES DEL SPRINT 1 (CON CARDINALIDADES Y TIPOS)
    # =========================================================================
    print("\n--- 2. Creando Diagrama de Clases (Sprint 1) con Cardinalidades ---")
    cl_pkg = sprint1_pkg.Packages.AddNew("2. Clases - Sprint 1", "Package")
    cl_pkg.Update()
    
    cl_diag = cl_pkg.Diagrams.AddNew("Diagrama de Clases - Sprint 1", "Class")
    cl_diag.Update()
    
    # 2.1 Usuario
    c_user = cl_pkg.Elements.AddNew("Usuario", "Class")
    add_attrs(c_user, [
        ("id", "UUID"),
        ("email", "String"),
        ("nombre", "String"),
        ("apellido", "String"),
        ("telefono", "String"),
        ("activo", "Boolean"),
        ("rol", "Rol")
    ])
    add_methods(c_user, [
        ("autenticar", "Boolean"),
        ("cerrar_sesion", "void")
    ])
    c_user.Update()
    
    # 2.2 Psicologo
    c_psyc = cl_pkg.Elements.AddNew("Psicologo", "Class")
    add_attrs(c_psyc, [
        ("id", "UUID"),
        ("numero_colegiado", "String"),
        ("biografia", "Text"),
        ("modalidad", "String"),
        ("tarifa_base", "Decimal"),
        ("activo", "Boolean")
    ])
    add_methods(c_psyc, [
        ("obtener_carga_semanal", "Integer")
    ])
    c_psyc.Update()
    
    # 2.3 Especialidad
    c_esp = cl_pkg.Elements.AddNew("Especialidad", "Class")
    add_attrs(c_esp, [
        ("id", "Integer"),
        ("nombre", "String"),
        ("descripcion", "String")
    ])
    c_esp.Update()
    
    # 2.4 DisponibilidadHoraria
    c_disp = cl_pkg.Elements.AddNew("DisponibilidadHoraria", "Class")
    add_attrs(c_disp, [
        ("id", "UUID"),
        ("dia_semana", "Integer"),
        ("hora_inicio", "Time"),
        ("hora_fin", "Time"),
        ("duracion_bloque_min", "Integer"),
        ("activo", "Boolean")
    ])
    add_methods(c_disp, [
        ("es_bloque_valido", "Boolean")
    ])
    c_disp.Update()
    
    # 2.5 Paciente
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
    add_methods(c_pac, [
        ("es_menor_edad", "Boolean")
    ])
    c_pac.Update()
    
    # 2.6 Cita
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
    add_methods(c_cita, [
        ("reprogramar", "void"),
        ("cancelar", "void")
    ])
    c_cita.Update()
    
    # 2.7 Teleconsulta
    c_tele = cl_pkg.Elements.AddNew("Teleconsulta", "Class")
    add_attrs(c_tele, [
        ("id", "UUID"),
        ("sala_id", "String"),
        ("jwt_room_token", "String"),
        ("duracion_segundos", "Integer"),
        ("estado_conexion", "String")
    ])
    add_methods(c_tele, [
        ("iniciar_sala", "String"),
        ("finalizar_sala", "void")
    ])
    c_tele.Update()
    
    # 2.8 AlertaPriorizacion
    c_alerta = cl_pkg.Elements.AddNew("AlertaPriorizacion", "Class")
    add_attrs(c_alerta, [
        ("id", "UUID"),
        ("tipo", "String"),
        ("severidad", "String"),
        ("descripcion", "Text"),
        ("resuelta", "Boolean"),
        ("fecha_creacion", "DateTime")
    ])
    add_methods(c_alerta, [
        ("resolver", "void")
    ])
    c_alerta.Update()
    
    # Relaciones con cardinalidades explícitas
    # Usuario "1" -- "0..1" Psicologo : extiende
    add_connector(c_user, c_psyc, "Association", "extiende", client_card="1", supplier_card="0..1")
    
    # Usuario "1" -- "0..1" Paciente : extiende
    add_connector(c_user, c_pac, "Association", "extiende", client_card="1", supplier_card="0..1")
    
    # Psicologo "1" *-- "1..*" DisponibilidadHoraria : posee (Composición)
    add_connector(c_psyc, c_disp, "Aggregation", "posee", client_card="1", supplier_card="1..*", aggregation=2)
    
    # Psicologo "0..*" -- "1..*" Especialidad : domina
    add_connector(c_psyc, c_esp, "Association", "domina", client_card="0..*", supplier_card="1..*")
    
    # Psicologo "1" -- "0..*" Cita : atiende
    add_connector(c_psyc, c_cita, "Association", "atiende", client_card="1", supplier_card="0..*")
    
    # Paciente "1" -- "0..*" Cita : agenda
    add_connector(c_pac, c_cita, "Association", "agenda", client_card="1", supplier_card="0..*")
    
    # Cita "1" *-- "0..1" Teleconsulta : genera (Composición)
    add_connector(c_cita, c_tele, "Aggregation", "genera", client_card="1", supplier_card="0..1", aggregation=2)
    
    # Paciente "1" -- "0..*" AlertaPriorizacion : origina
    add_connector(c_pac, c_alerta, "Association", "origina", client_card="1", supplier_card="0..*")
    
    # Layout limpio en el diagrama de clases
    # Fila 1: Usuario en el centro superior
    add_diag_obj(cl_diag, c_user, 460, -50, 680, -230)
    
    # Fila 2: Especialidad (izquierda), Psicólogo (centro-izq), Paciente (centro-der), Alerta (derecha)
    add_diag_obj(cl_diag, c_esp, 60, -320, 240, -440)
    add_diag_obj(cl_diag, c_psyc, 300, -320, 520, -500)
    add_diag_obj(cl_diag, c_pac, 620, -320, 850, -500)
    add_diag_obj(cl_diag, c_alerta, 920, -320, 1140, -500)
    
    # Fila 3: DisponibilidadHoraria (debajo de Psicólogo), Cita (en el centro entre Psicólogo y Paciente)
    add_diag_obj(cl_diag, c_disp, 280, -580, 520, -760)
    add_diag_obj(cl_diag, c_cita, 600, -580, 840, -780)
    
    # Fila 4: Teleconsulta (debajo de Cita)
    add_diag_obj(cl_diag, c_tele, 600, -840, 840, -1000)
    
    cl_diag.Update()
    print("2. Diagrama de Clases creado correctamente con cardinalidades.")

    # =========================================================================
    # 3. DIAGRAMA DE ACTIVIDAD: RESERVA Y PROGRAMACIÓN DE CITA
    # =========================================================================
    print("\n--- 3. Creando Diagrama de Actividad (Reserva de Cita) ---")
    act1_pkg = sprint1_pkg.Packages.AddNew("3. Actividad - Reserva de Cita", "Package")
    act1_pkg.Update()
    
    act1_diag = act1_pkg.Diagrams.AddNew("Diagrama de Actividad - Reserva de Cita", "Activity")
    act1_diag.Update()
    
    # Elementos
    init1 = act1_pkg.Elements.AddNew("", "StateNode")
    init1.Subtype = 100
    init1.Update()
    
    a1_1 = act1_pkg.Elements.AddNew("Usuario (Recepcionista o Paciente) abre formulario de agendamiento", "Activity")
    a1_1.Update()
    
    a1_2 = act1_pkg.Elements.AddNew("Selecciona Especialidad, Psicólogo y Modalidad (Presencial / Virtual)", "Activity")
    a1_2.Update()
    
    a1_3 = act1_pkg.Elements.AddNew("El sistema consulta la DisponibilidadHoraria del psicólogo", "Activity")
    a1_3.Update()
    
    a1_4 = act1_pkg.Elements.AddNew("Se despliegan en pantalla los bloques libres de la semana", "Activity")
    a1_4.Update()
    
    a1_5 = act1_pkg.Elements.AddNew("Usuario selecciona la fecha y hora de inicio deseada", "Activity")
    a1_5.Update()
    
    a1_6 = act1_pkg.Elements.AddNew("Ingresa motivo de consulta y envía solicitud de reserva", "Activity")
    a1_6.Update()
    
    a1_7 = act1_pkg.Elements.AddNew("Interceptar solicitud con TenantMiddleware y autenticar JWT", "Activity")
    a1_7.Update()
    
    a1_8 = act1_pkg.Elements.AddNew("Iniciar transacción de BD y ejecutar SELECT FOR UPDATE sobre citas activas", "Activity")
    a1_8.Update()
    
    d1_1 = act1_pkg.Elements.AddNew("¿Existe solapamiento con otra cita activa?", "Decision")
    d1_1.Update()
    
    e1_1 = act1_pkg.Elements.AddNew("Hacer Rollback de transacción y retornar HTTP 409 Conflict ('Horario reservado')", "Activity")
    e1_1.Update()
    
    e1_1_msg = act1_pkg.Elements.AddNew("Mostrar mensaje de colisión y recargar bloques en UI", "Activity")
    e1_1_msg.Update()
    
    fin_err1 = act1_pkg.Elements.AddNew("", "StateNode")
    fin_err1.Subtype = 101
    fin_err1.Update()
    
    d1_2 = act1_pkg.Elements.AddNew("¿El horario está dentro de la disponibilidad laboral?", "Decision")
    d1_2.Update()
    
    e1_2 = act1_pkg.Elements.AddNew("Retornar HTTP 400 Bad Request ('Fuera de disponibilidad laboral')", "Activity")
    e1_2.Update()
    
    fin_err2 = act1_pkg.Elements.AddNew("", "StateNode")
    fin_err2.Subtype = 101
    fin_err2.Update()
    
    a1_9 = act1_pkg.Elements.AddNew("Crear registro en tabla agenda_cita (estado = 'Programada')", "Activity")
    a1_9.Update()
    
    d1_3 = act1_pkg.Elements.AddNew("¿Modalidad es Virtual?", "Decision")
    d1_3.Update()
    
    a1_10_v = act1_pkg.Elements.AddNew("Generar sala única Jitsi Meet y crear registro en agenda_teleconsulta", "Activity")
    a1_10_v.Update()
    
    a1_10_p = act1_pkg.Elements.AddNew("Asignar consultorio físico según configuración del centro", "Activity")
    a1_10_p.Update()
    
    m1_1 = act1_pkg.Elements.AddNew("Sincronización Modalidad", "Decision")
    m1_1.Update()
    
    a1_11 = act1_pkg.Elements.AddNew("Hacer Commit de transacción de base de datos", "Activity")
    a1_11.Update()
    
    a1_12 = act1_pkg.Elements.AddNew("Emitir evento WebSocket / notificación de cita confirmada", "Activity")
    a1_12.Update()
    
    a1_13 = act1_pkg.Elements.AddNew("Retornar HTTP 201 Created con detalle de la cita", "Activity")
    a1_13.Update()
    
    a1_14 = act1_pkg.Elements.AddNew("Mostrar confirmación en pantalla y actualizar calendario", "Activity")
    a1_14.Update()
    
    fin_ok1 = act1_pkg.Elements.AddNew("", "StateNode")
    fin_ok1.Subtype = 101
    fin_ok1.Update()
    
    # Flujos de control
    add_connector(init1, a1_1, "ControlFlow")
    add_connector(a1_1, a1_2, "ControlFlow")
    add_connector(a1_2, a1_3, "ControlFlow")
    add_connector(a1_3, a1_4, "ControlFlow")
    add_connector(a1_4, a1_5, "ControlFlow")
    add_connector(a1_5, a1_6, "ControlFlow")
    add_connector(a1_6, a1_7, "ControlFlow")
    add_connector(a1_7, a1_8, "ControlFlow")
    add_connector(a1_8, d1_1, "ControlFlow")
    
    # Rama conflicto
    add_connector(d1_1, e1_1, "ControlFlow", "Sí")
    add_connector(e1_1, e1_1_msg, "ControlFlow")
    add_connector(e1_1_msg, fin_err1, "ControlFlow")
    
    # Rama sin conflicto -> disponibilidad
    add_connector(d1_1, d1_2, "ControlFlow", "No")
    
    # Fuera de disponibilidad
    add_connector(d1_2, e1_2, "ControlFlow", "No")
    add_connector(e1_2, fin_err2, "ControlFlow")
    
    # Dentro de disponibilidad
    add_connector(d1_2, a1_9, "ControlFlow", "Sí")
    add_connector(a1_9, d1_3, "ControlFlow")
    
    # Modalidad virtual vs presencial
    add_connector(d1_3, a1_10_v, "ControlFlow", "Sí")
    add_connector(d1_3, a1_10_p, "ControlFlow", "No")
    
    add_connector(a1_10_v, m1_1, "ControlFlow")
    add_connector(a1_10_p, m1_1, "ControlFlow")
    
    add_connector(m1_1, a1_11, "ControlFlow")
    add_connector(a1_11, a1_12, "ControlFlow")
    add_connector(a1_12, a1_13, "ControlFlow")
    add_connector(a1_13, a1_14, "ControlFlow")
    add_connector(a1_14, fin_ok1, "ControlFlow")
    
    # Layout en Diagrama de Actividad 1
    add_diag_obj(act1_diag, init1, 380, -30, 400, -50)
    add_diag_obj(act1_diag, a1_1, 250, -70, 530, -115)
    add_diag_obj(act1_diag, a1_2, 240, -135, 540, -180)
    add_diag_obj(act1_diag, a1_3, 240, -200, 540, -245)
    add_diag_obj(act1_diag, a1_4, 240, -265, 540, -310)
    add_diag_obj(act1_diag, a1_5, 240, -330, 540, -375)
    add_diag_obj(act1_diag, a1_6, 240, -395, 540, -440)
    add_diag_obj(act1_diag, a1_7, 240, -460, 540, -505)
    add_diag_obj(act1_diag, a1_8, 230, -525, 550, -570)
    
    # Decisión 1: Solapamiento
    add_diag_obj(act1_diag, d1_1, 330, -590, 450, -640)
    add_diag_obj(act1_diag, e1_1, 600, -590, 880, -640)
    add_diag_obj(act1_diag, e1_1_msg, 600, -660, 880, -710)
    add_diag_obj(act1_diag, fin_err1, 730, -730, 750, -750)
    
    # Decisión 2: Disponibilidad
    add_diag_obj(act1_diag, d1_2, 330, -680, 450, -730)
    add_diag_obj(act1_diag, e1_2, 600, -760, 880, -810)
    add_diag_obj(act1_diag, fin_err2, 730, -830, 750, -850)
    
    # Creación y Decisión 3: Modalidad
    add_diag_obj(act1_diag, a1_9, 240, -770, 540, -815)
    add_diag_obj(act1_diag, d1_3, 340, -845, 440, -895)
    
    # Ramas Virtual / Presencial
    add_diag_obj(act1_diag, a1_10_v, 80, -925, 340, -975)
    add_diag_obj(act1_diag, a1_10_p, 440, -925, 700, -975)
    
    add_diag_obj(act1_diag, m1_1, 370, -1005, 410, -1035)
    add_diag_obj(act1_diag, a1_11, 250, -1065, 530, -1110)
    add_diag_obj(act1_diag, a1_12, 240, -1130, 540, -1175)
    add_diag_obj(act1_diag, a1_13, 240, -1195, 540, -1240)
    add_diag_obj(act1_diag, a1_14, 240, -1260, 540, -1305)
    add_diag_obj(act1_diag, fin_ok1, 380, -1335, 400, -1355)
    
    act1_diag.Update()
    print("3. Diagrama de Actividad (Reserva de Cita) creado correctamente.")

    # =========================================================================
    # 4. DIAGRAMA DE ACTIVIDAD: TELECONSULTA JITSI MEET
    # =========================================================================
    print("\n--- 4. Creando Diagrama de Actividad (Teleconsulta Jitsi Meet) ---")
    act2_pkg = sprint1_pkg.Packages.AddNew("4. Actividad - Teleconsulta Jitsi Meet", "Package")
    act2_pkg.Update()
    
    act2_diag = act2_pkg.Diagrams.AddNew("Diagrama de Actividad - Teleconsulta Jitsi Meet", "Activity")
    act2_diag.Update()
    
    init2 = act2_pkg.Elements.AddNew("", "StateNode")
    init2.Subtype = 100
    init2.Update()
    
    b2_1 = act2_pkg.Elements.AddNew("Usuario accede al detalle de su cita virtual programada", "Activity")
    b2_1.Update()
    
    b2_2 = act2_pkg.Elements.AddNew("Cliente solicita acceso: GET /api/teleconsulta/{cita_id}/access/", "Activity")
    b2_2.Update()
    
    d2_1 = act2_pkg.Elements.AddNew("¿Fecha y hora coinciden con ventana de atención (±15 min)?", "Decision")
    d2_1.Update()
    
    b2_err = act2_pkg.Elements.AddNew("Retornar HTTP 403: 'Sala disponible únicamente durante el horario'", "Activity")
    b2_err.Update()
    
    b2_err_msg = act2_pkg.Elements.AddNew("Mostrar alerta con cuenta regresiva en el cliente", "Activity")
    b2_err_msg.Update()
    
    fin_err_tele = act2_pkg.Elements.AddNew("", "StateNode")
    fin_err_tele.Subtype = 101
    fin_err_tele.Update()
    
    b2_3 = act2_pkg.Elements.AddNew("Generar token seguro de sala JWT y claims de participante", "Activity")
    b2_3.Update()
    
    b2_4 = act2_pkg.Elements.AddNew("Retornar parámetros de conexión (nombre de sala, dominio Jitsi, token)", "Activity")
    b2_4.Update()
    
    d2_2 = act2_pkg.Elements.AddNew("¿Plataforma cliente es Web o Móvil?", "Decision")
    d2_2.Update()
    
    b2_web = act2_pkg.Elements.AddNew("Cargar script Jitsi Meet External API e instanciar en contenedor DOM", "Activity")
    b2_web.Update()
    
    b2_mov = act2_pkg.Elements.AddNew("Verificar permisos de Cámara/Micrófono y lanzar vista SDK nativo", "Activity")
    b2_mov.Update()
    
    m2_1 = act2_pkg.Elements.AddNew("Sincronización Cliente", "Decision")
    m2_1.Update()
    
    b2_5 = act2_pkg.Elements.AddNew("Establecer negociación WebRTC hacia servidor de videoconferencia", "Activity")
    b2_5.Update()
    
    b2_6 = act2_pkg.Elements.AddNew("Conectar streams de audio bidireccional y video HD", "Activity")
    b2_6.Update()
    
    b2_7 = act2_pkg.Elements.AddNew("Iniciar contador de tiempo transcurrido en pantalla", "Activity")
    b2_7.Update()
    
    b2_8 = act2_pkg.Elements.AddNew("Transmitir audio, video y chat durante sesión terapéutica", "Activity")
    b2_8.Update()
    
    b2_9 = act2_pkg.Elements.AddNew("Psicólogo presiona botón 'Finalizar Consulta'", "Activity")
    b2_9.Update()
    
    b2_10 = act2_pkg.Elements.AddNew("Desconectar participantes y destruir instancia WebRTC", "Activity")
    b2_10.Update()
    
    b2_11 = act2_pkg.Elements.AddNew("Enviar petición POST /api/teleconsulta/{cita_id}/finish/", "Activity")
    b2_11.Update()
    
    b2_12 = act2_pkg.Elements.AddNew("Guardar hora fin y duración total en agenda_teleconsulta", "Activity")
    b2_12.Update()
    
    b2_13 = act2_pkg.Elements.AddNew("Actualizar estado de cita a 'Realizada'", "Activity")
    b2_13.Update()
    
    b2_14 = act2_pkg.Elements.AddNew("Mostrar mensaje de sesión concluida exitosamente", "Activity")
    b2_14.Update()
    
    fin_ok_tele = act2_pkg.Elements.AddNew("", "StateNode")
    fin_ok_tele.Subtype = 101
    fin_ok_tele.Update()
    
    # Flujos
    add_connector(init2, b2_1, "ControlFlow")
    add_connector(b2_1, b2_2, "ControlFlow")
    add_connector(b2_2, d2_1, "ControlFlow")
    
    # Ventana inválida
    add_connector(d2_1, b2_err, "ControlFlow", "No")
    add_connector(b2_err, b2_err_msg, "ControlFlow")
    add_connector(b2_err_msg, fin_err_tele, "ControlFlow")
    
    # Ventana válida
    add_connector(d2_1, b2_3, "ControlFlow", "Sí")
    add_connector(b2_3, b2_4, "ControlFlow")
    add_connector(b2_4, d2_2, "ControlFlow")
    
    # Ramas Web vs Móvil
    add_connector(d2_2, b2_web, "ControlFlow", "Web Angular")
    add_connector(d2_2, b2_mov, "ControlFlow", "Móvil Flutter")
    
    add_connector(b2_web, m2_1, "ControlFlow")
    add_connector(b2_mov, m2_1, "ControlFlow")
    
    add_connector(m2_1, b2_5, "ControlFlow")
    add_connector(b2_5, b2_6, "ControlFlow")
    add_connector(b2_6, b2_7, "ControlFlow")
    add_connector(b2_7, b2_8, "ControlFlow")
    add_connector(b2_8, b2_9, "ControlFlow")
    add_connector(b2_9, b2_10, "ControlFlow")
    add_connector(b2_10, b2_11, "ControlFlow")
    add_connector(b2_11, b2_12, "ControlFlow")
    add_connector(b2_12, b2_13, "ControlFlow")
    add_connector(b2_13, b2_14, "ControlFlow")
    add_connector(b2_14, fin_ok_tele, "ControlFlow")
    
    # Layout en Diagrama de Actividad 2
    add_diag_obj(act2_diag, init2, 380, -30, 400, -50)
    add_diag_obj(act2_diag, b2_1, 240, -70, 540, -115)
    add_diag_obj(act2_diag, b2_2, 230, -135, 550, -180)
    
    # Decisión 1: Ventana horaria
    add_diag_obj(act2_diag, d2_1, 310, -200, 470, -255)
    add_diag_obj(act2_diag, b2_err, 590, -200, 870, -255)
    add_diag_obj(act2_diag, b2_err_msg, 590, -275, 870, -325)
    add_diag_obj(act2_diag, fin_err_tele, 720, -345, 740, -365)
    
    # Continuación flujo exitoso
    add_diag_obj(act2_diag, b2_3, 230, -280, 550, -325)
    add_diag_obj(act2_diag, b2_4, 220, -345, 560, -390)
    
    # Decisión 2: Web vs Móvil
    add_diag_obj(act2_diag, d2_2, 330, -410, 450, -460)
    add_diag_obj(act2_diag, b2_web, 80, -485, 340, -535)
    add_diag_obj(act2_diag, b2_mov, 440, -485, 700, -535)
    
    add_diag_obj(act2_diag, m2_1, 370, -560, 410, -590)
    add_diag_obj(act2_diag, b2_5, 220, -615, 560, -660)
    add_diag_obj(act2_diag, b2_6, 240, -680, 540, -725)
    add_diag_obj(act2_diag, b2_7, 240, -745, 540, -790)
    add_diag_obj(act2_diag, b2_8, 230, -810, 550, -855)
    add_diag_obj(act2_diag, b2_9, 250, -875, 530, -920)
    add_diag_obj(act2_diag, b2_10, 230, -940, 550, -985)
    add_diag_obj(act2_diag, b2_11, 230, -1005, 550, -1050)
    add_diag_obj(act2_diag, b2_12, 230, -1070, 550, -1115)
    add_diag_obj(act2_diag, b2_13, 250, -1135, 530, -1180)
    add_diag_obj(act2_diag, b2_14, 240, -1200, 540, -1245)
    add_diag_obj(act2_diag, fin_ok_tele, 380, -1275, 400, -1295)
    
    act2_diag.Update()
    print("4. Diagrama de Actividad (Teleconsulta Jitsi Meet) creado correctamente.")
    
    # Guardar cambios y cerrar repositorio
    print("\nGuardando cambios en Enterprise Architect...", flush=True)
    sprint1_pkg.Packages.Refresh()
    repo.RefreshModelView(0)
    repo.CloseFile()
    repo.Exit()
    print("¡PROCESO COMPLETADO EXITOSAMENTE! Carpeta 'sprint 1' generada con todos los diagramas.", flush=True)
    return True

if __name__ == "__main__":
    create_sprint1_diagrams()

