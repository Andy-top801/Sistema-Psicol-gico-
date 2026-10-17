import win32com.client
import uuid
import os
import sys

# Ensure UTF-8 output in Windows console
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

eap_path = os.path.abspath(r"diagramas\DIAGRAMAS.eapx")

conn = win32com.client.Dispatch('ADODB.Connection')
conn.Open(f'Provider=Microsoft.ACE.OLEDB.16.0;Data Source={eap_path};')

def guid():
    return '{' + str(uuid.uuid4()).upper() + '}'

# Helper functions
def create_package(name, parent_id):
    g = guid()
    safe_name = name.replace("'", "''")
    conn.Execute(f"INSERT INTO t_package (Name, Parent_ID, ea_guid, [Version]) VALUES ('{safe_name}', {parent_id}, '{g}', '1.0')")
    rs, _ = conn.Execute(f"SELECT Package_ID FROM t_package WHERE ea_guid = '{g}'")
    pkg_id = rs.Fields(0).Value
    conn.Execute(f"INSERT INTO t_object (Object_Type, Name, Package_ID, PDATA1, ea_guid, [Scope], [Status], Complexity, Author, [Version]) VALUES ('Package', '{safe_name}', {parent_id}, '{pkg_id}', '{guid()}', 'Public', 'Proposed', '1', 'Grupo 9', '1.0')")
    return pkg_id

def create_diagram(pkg_id, name, diag_type, cx=1400, cy=900):
    g = guid()
    safe_name = name.replace("'", "''")
    style_ex = "ExcludeRTF=0;DocAll=0;HideQuals=0;AttPkg=1;ShowTests=0;ShowMaint=0;SuppressFOC=1;MatrixActive=0;SwimlanesActive=1;KanbanActive=0;MatrixLineWidth=1;MatrixLineClr=0;MatrixLocked=0;TConnectorNotation=UML 2.1;TExplicitNavigability=0;AdvancedElementProps=1;AdvancedFeatureProps=1;AdvancedConnectorProps=1;m_bElementClassifier=1;SPT=1;MDGDgm=;STBLDgm=;ShowNotes=0;VisibleAttributeDetail=0;ShowOpRetType=1;SuppressBrackets=0;SuppConnectorLabels=0;PrintPageHeadFoot=0;ShowAsList=0;SuppressedCompartments=;Theme=:119;"
    conn.Execute(f"""
        INSERT INTO t_diagram (Package_ID, Name, Diagram_Type, Orientation, cx, cy, Scale, ShowBorder, StyleEx, ea_guid)
        VALUES ({pkg_id}, '{safe_name}', '{diag_type}', 'L', {cx}, {cy}, 100, True, '{style_ex}', '{g}')
    """)
    rs, _ = conn.Execute(f"SELECT Diagram_ID FROM t_diagram WHERE ea_guid = '{g}'")
    return rs.Fields(0).Value

def create_object(pkg_id, name, obj_type, stereotype='', note=''):
    g = guid()
    st_val = f"'{stereotype}'" if stereotype else "NULL"
    safe_note = note.replace("'", "''")
    safe_name = name.replace("'", "''")
    conn.Execute(f"""
        INSERT INTO t_object (Object_Type, Name, Package_ID, Stereotype, [Note], [Scope], [Status], Complexity, Author, [Version], ea_guid)
        VALUES ('{obj_type}', '{safe_name}', {pkg_id}, {st_val}, '{safe_note}', 'Public', 'Proposed', '1', 'Grupo 9', '1.0', '{g}')
    """)
    rs, _ = conn.Execute(f"SELECT Object_ID FROM t_object WHERE ea_guid = '{g}'")
    return rs.Fields(0).Value

def add_attribute(obj_id, name, attr_type, scope='Public'):
    g = guid()
    safe_name = name.replace("'", "''")
    conn.Execute(f"""
        INSERT INTO t_attribute (Object_ID, Name, [Type], [Scope], ea_guid)
        VALUES ({obj_id}, '{safe_name}', '{attr_type}', '{scope}', '{g}')
    """)

def add_operation(obj_id, name, ret_type='void', scope='Public'):
    g = guid()
    safe_name = name.replace("'", "''")
    conn.Execute(f"""
        INSERT INTO t_operation (Object_ID, Name, [Type], [Scope], ea_guid)
        VALUES ({obj_id}, '{safe_name}', '{ret_type}', '{scope}', '{g}')
    """)

def create_connector(start_id, end_id, conn_type, name='', direction='Source -> Destination', stereotype='', diag_id=0):
    g = guid()
    st_val = f"'{stereotype}'" if stereotype else "NULL"
    safe_name = name.replace("'", "''")
    conn.Execute(f"""
        INSERT INTO t_connector (Start_Object_ID, End_Object_ID, Connector_Type, Name, [Direction], Stereotype, ea_guid, DiagramID)
        VALUES ({start_id}, {end_id}, '{conn_type}', '{safe_name}', '{direction}', {st_val}, '{g}', {diag_id})
    """)
    rs, _ = conn.Execute(f"SELECT Connector_ID FROM t_connector WHERE ea_guid = '{g}'")
    return rs.Fields(0).Value

def place_object(diag_id, obj_id, top, left, right, bottom):
    conn.Execute(f"""
        INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectTop, RectLeft, RectRight, RectBottom, Sequence)
        VALUES ({diag_id}, {obj_id}, {top}, {left}, {right}, {bottom}, 1)
    """)

def link_connector(diag_id, conn_id):
    conn.Execute(f"""
        INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Geometry)
        VALUES ({diag_id}, {conn_id}, '$SPLT=;')
    """)

print("--- Starting Full Sprint 3 Modeling in DIAGRAMAS.eapx ---")

# Check and clean up existing Sprint 3 packages if any
rs_clean, _ = conn.Execute("SELECT Package_ID FROM t_package WHERE Parent_ID = 1 AND Name LIKE '%Sprint 3%'")
old_pids = []
while not rs_clean.EOF:
    old_pids.append(rs_clean.Fields(0).Value)
    rs_clean.MoveNext()

for opid in old_pids:
    print(f"Cleaning up previous Sprint 3 package ID: {opid}")
    def clean_pkg(pid):
        rs_sub, _ = conn.Execute(f"SELECT Package_ID FROM t_package WHERE Parent_ID = {pid}")
        s_ids = []
        while not rs_sub.EOF:
            s_ids.append(rs_sub.Fields(0).Value)
            rs_sub.MoveNext()
        for s in s_ids:
            clean_pkg(s)
        conn.Execute(f"DELETE FROM t_diagramobjects WHERE Diagram_ID IN (SELECT Diagram_ID FROM t_diagram WHERE Package_ID = {pid})")
        conn.Execute(f"DELETE FROM t_diagramlinks WHERE DiagramID IN (SELECT Diagram_ID FROM t_diagram WHERE Package_ID = {pid})")
        conn.Execute(f"DELETE FROM t_diagram WHERE Package_ID = {pid}")
        conn.Execute(f"DELETE FROM t_operation WHERE Object_ID IN (SELECT Object_ID FROM t_object WHERE Package_ID = {pid})")
        conn.Execute(f"DELETE FROM t_attribute WHERE Object_ID IN (SELECT Object_ID FROM t_object WHERE Package_ID = {pid})")
        conn.Execute(f"DELETE FROM t_connector WHERE Start_Object_ID IN (SELECT Object_ID FROM t_object WHERE Package_ID = {pid}) OR End_Object_ID IN (SELECT Object_ID FROM t_object WHERE Package_ID = {pid})")
        conn.Execute(f"DELETE FROM t_object WHERE Package_ID = {pid}")
        conn.Execute(f"DELETE FROM t_package WHERE Package_ID = {pid}")
    clean_pkg(opid)
    conn.Execute(f"DELETE FROM t_object WHERE Package_ID = 1 AND PDATA1 = '{opid}'")

# Create Main Root Package for Sprint 3
sp3_root_name = "Sprint 3 - Experiencia Móvil de Pacientes y Asistencia de IA"
sp3_id = create_package(sp3_root_name, 1)
print(f"Created Root Package for Sprint 3: ID [{sp3_id}] '{sp3_root_name}'")

# ==============================================================================
# 1. CASOS DE USO - SPRINT 3 (INCREMENTAL ACUMULADO)
# ==============================================================================
pkg_cu_id = create_package("1. Casos de Uso - Sprint 3", sp3_id)
diag_cu_id = create_diagram(pkg_cu_id, "Diagrama de Casos de Uso - Sprint 3 Incremental Acumulado", "Use Case", 1600, 1000)
print(f"  [1] Casos de Uso Pkg [{pkg_cu_id}], Diag [{diag_cu_id}]")

act_paciente = create_object(pkg_cu_id, "Paciente\n(App Móvil Flutter / Web)", "Actor")
act_coord = create_object(pkg_cu_id, "Coordinador Clínico\n(Web Angular)", "Actor")
act_psico = create_object(pkg_cu_id, "Psicólogo Tratante\n(Web Angular)", "Actor")
act_recep = create_object(pkg_cu_id, "Recepcionista\n(Web Angular)", "Actor")
act_admin = create_object(pkg_cu_id, "Administrador del Centro\n(Clínica)", "Actor")
act_superadmin = create_object(pkg_cu_id, "SuperAdministrador SaaS\n(Plataforma)", "Actor")

place_object(diag_cu_id, act_paciente, -80, 50, 160, -180)
place_object(diag_cu_id, act_coord, -300, 50, 160, -400)
place_object(diag_cu_id, act_psico, -520, 50, 160, -620)
place_object(diag_cu_id, act_recep, -80, 1400, 1510, -180)
place_object(diag_cu_id, act_admin, -300, 1400, 1510, -400)
place_object(diag_cu_id, act_superadmin, -520, 1400, 1510, -620)

CU_LIST = [
    ("CU1", "Gestionar centros y multi-tenant", "Sprint 0"),
    ("CU2", "Inicio de sesión y autenticación (Web y Móvil)", "Sprint 0 / SP3"),
    ("CU3", "Gestionar usuarios y credenciales", "Sprint 0"),
    ("CU4", "Gestionar roles y permisos RBAC", "Sprint 0"),
    ("CU27", "Recuperar contraseña por correo", "Sprint 0"),
    ("CU6", "Gestionar perfiles de psicólogos", "Sprint 1"),
    ("CU7", "Gestionar catálogo de pacientes", "Sprint 1"),
    ("CU8", "Gestionar disponibilidad horaria", "Sprint 1"),
    ("CU9", "Visualizar dashboard administrativo", "Sprint 1"),
    ("CU10", "Gestionar alertas tempranas de citas", "Sprint 1"),
    ("CU11", "Gestionar citas y agenda (Web y Móvil)", "Sprint 1 / SP3"),
    ("CU13", "Gestionar teleconsultas WebRTC (Web y Móvil)", "Sprint 1 / SP3"),
    ("CU5", "Bitácora confidencial cifrada con llave única", "Sprint 2"),
    ("CU14", "Llenar formulario previo e intake digital", "Sprint 2"),
    ("CU15", "Gestionar historia clínica electrónica", "Sprint 2"),
    ("CU16", "Registrar notas SOAP de evolución", "Sprint 2"),
    ("CU17", "Asignar y entregar tareas terapéuticas y Mood", "Sprint 2 / SP3"),
    ("CU18", "Formalizar consentimientos informados SHA-256", "Sprint 2"),
    ("CU19", "Cierre de caso y derivación a psiquiatría", "Sprint 2"),
    ("CU20", "Interactuar con chatbot de orientación", "Sprint 2"),
    ("CU25", "Generar reportes personalizados QBE y voz", "Sprint 2"),
    ("CU28", "Gestionar copias de seguridad y restauración", "Sprint 2"),
    ("CU12", "Gestionar recordatorios y notificaciones automáticas (Push FCM)", "Sprint 3 [NUEVO]"),
    ("CU21", "Clasificar motivo de consulta mediante IA (NLP/Triaje)", "Sprint 3 [NUEVO]"),
    ("CU22", "Sugerir asignación de paciente a psicólogo mediante IA", "Sprint 3 [NUEVO]"),
]

cu_objects = {}
col1_top = -60
col2_top = -60

for idx, (cuid, name, sprint_tag) in enumerate(CU_LIST):
    cu_name = f"{cuid}: {name}\n[{sprint_tag}]"
    o_cu = create_object(pkg_cu_id, cu_name, "UseCase")
    cu_objects[cuid] = o_cu
    if idx < 13:
        place_object(diag_cu_id, o_cu, col1_top, 280, 680, col1_top - 50)
        col1_top -= 68
    else:
        place_object(diag_cu_id, o_cu, col2_top, 740, 1180, col2_top - 50)
        col2_top -= 68

CONNECTIONS_CU = [
    (act_paciente, "CU2"), (act_paciente, "CU11"), (act_paciente, "CU12"), (act_paciente, "CU13"),
    (act_paciente, "CU14"), (act_paciente, "CU17"), (act_paciente, "CU18"), (act_paciente, "CU20"),
    (act_coord, "CU2"), (act_coord, "CU8"), (act_coord, "CU11"), (act_coord, "CU21"), (act_coord, "CU22"),
    (act_psico, "CU2"), (act_psico, "CU8"), (act_psico, "CU11"), (act_psico, "CU13"), (act_psico, "CU15"),
    (act_psico, "CU16"), (act_psico, "CU17"), (act_psico, "CU19"), (act_recep, "CU2"), (act_recep, "CU7"),
    (act_recep, "CU11"), (act_admin, "CU1"), (act_admin, "CU3"), (act_admin, "CU4"), (act_admin, "CU9"),
    (act_admin, "CU10"), (act_admin, "CU25"), (act_superadmin, "CU1"), (act_superadmin, "CU5"), (act_superadmin, "CU28")
]

for act_obj, cuid in CONNECTIONS_CU:
    conn_id = create_connector(act_obj, cu_objects[cuid], "Association")
    link_connector(diag_cu_id, conn_id)

# ==============================================================================
# 2. CLASES DEL DOMINIO CLÍNICO - SPRINT 3
# ==============================================================================
pkg_clases_id = create_package("2. Clases - Sprint 3", sp3_id)
diag_clases_id = create_diagram(pkg_clases_id, "Diagrama de Clases - Sprint 3 Dominio Clínico", "Logical", 1600, 1100)
print(f"  [2] Clases de Dominio Pkg [{pkg_clases_id}], Diag [{diag_clases_id}]")

cls_tenant = create_object(pkg_clases_id, "Tenant", "Class")
for a, t in [("id", "UUID"), ("nombre", "String"), ("slug", "String"), ("schema_name", "String"), ("plan", "String"), ("activo", "Boolean")]:
    add_attribute(cls_tenant, a, t)
add_operation(cls_tenant, "crear_esquema", "void")

cls_usuario = create_object(pkg_clases_id, "Usuario", "Class")
for a, t in [("id", "UUID"), ("email", "String"), ("rol", "String"), ("is_active", "Boolean")]:
    add_attribute(cls_usuario, a, t)
add_operation(cls_usuario, "verificar_credenciales", "Boolean")

cls_psicologo = create_object(pkg_clases_id, "Psicologo", "Class")
for a, t in [("id", "UUID"), ("numero_colegiado", "String"), ("especialidades", "Array[String]"), ("modalidad", "String"), ("tarifa_base", "Decimal"), ("cupo_maximo_pacientes", "Integer")]:
    add_attribute(cls_psicologo, a, t)
add_operation(cls_psicologo, "obtener_carga_actual", "Integer")

cls_paciente = create_object(pkg_clases_id, "Paciente", "Class")
for a, t in [("id", "UUID"), ("codigo_expediente", "String"), ("ci", "String"), ("fecha_nacimiento", "Date"), ("contacto_emergencia", "String")]:
    add_attribute(cls_paciente, a, t)

cls_cita = create_object(pkg_clases_id, "Cita", "Class")
for a, t in [("id", "UUID"), ("fecha", "Date"), ("hora_inicio", "Time"), ("hora_fin", "Time"), ("modalidad", "String"), ("estado", "String")]:
    add_attribute(cls_cita, a, t)
add_operation(cls_cita, "permite_cancelacion", "Boolean")

cls_token_fcm = create_object(pkg_clases_id, "TokenFCM", "Class")
for a, t in [("id", "UUID"), ("token", "String"), ("dispositivo_tipo", "String"), ("activo", "Boolean"), ("fecha_registro", "DateTime"), ("ultimo_uso", "DateTime")]:
    add_attribute(cls_token_fcm, a, t)
add_operation(cls_token_fcm, "registrar_token", "void")
add_operation(cls_token_fcm, "desactivar_token", "void")

cls_notif = create_object(pkg_clases_id, "NotificacionCita", "Class")
for a, t in [("id", "UUID"), ("tipo_evento", "String"), ("canal", "String"), ("titulo", "String"), ("cuerpo", "String"), ("enviado", "Boolean"), ("fecha_programada", "DateTime"), ("fecha_envio", "DateTime")]:
    add_attribute(cls_notif, a, t)
add_operation(cls_notif, "despachar_push", "void")

cls_mood = create_object(pkg_clases_id, "RegistroAnimo", "Class")
for a, t in [("id", "UUID"), ("puntuacion_animo", "Integer"), ("emocion_dominante", "String"), ("factores_contextuales", "Array[String]"), ("notas_reflexion", "Text"), ("fecha_registro", "Date")]:
    add_attribute(cls_mood, a, t)
add_operation(cls_mood, "registrar_animo", "void")
add_operation(cls_mood, "calcular_promedio_semanal", "Decimal")

cls_clasia = create_object(pkg_clases_id, "ClasificacionIA", "Class")
for a, t in [("id", "UUID"), ("area_tematica_principal", "String"), ("confianza_clasificacion", "Decimal"), ("nivel_severidad", "String"), ("alerta_crisis", "Boolean"), ("justificacion_clinica", "JSONB")]:
    add_attribute(cls_clasia, a, t)
add_operation(cls_clasia, "sanitizar_pii", "String")
add_operation(cls_clasia, "clasificar_motivo", "ClasificacionResultado")
add_operation(cls_clasia, "evaluar_crisis", "Boolean")

cls_match = create_object(pkg_clases_id, "SugerenciaMatching", "Class")
for a, t in [("id", "UUID"), ("score_total", "Decimal"), ("score_especialidad", "Decimal"), ("score_disponibilidad", "Decimal"), ("score_carga_trabajo", "Decimal"), ("score_modalidad", "Decimal"), ("ranking", "Integer"), ("estado_aprobacion", "String")]:
    add_attribute(cls_match, a, t)
add_operation(cls_match, "calcular_score_multivariable", "void")
add_operation(cls_match, "confirmar_asignacion", "void")
add_operation(cls_match, "rechazar_sugerencia", "void")

place_object(diag_clases_id, cls_tenant, -50, 50, 230, -210)
place_object(diag_clases_id, cls_usuario, -50, 320, 500, -210)
place_object(diag_clases_id, cls_psicologo, -50, 590, 830, -240)
place_object(diag_clases_id, cls_paciente, -50, 920, 1160, -220)
place_object(diag_clases_id, cls_cita, -350, 590, 830, -530)
place_object(diag_clases_id, cls_token_fcm, -350, 920, 1160, -520)
place_object(diag_clases_id, cls_notif, -620, 920, 1160, -800)
place_object(diag_clases_id, cls_mood, -350, 50, 290, -530)
place_object(diag_clases_id, cls_clasia, -620, 50, 320, -810)
place_object(diag_clases_id, cls_match, -620, 480, 780, -830)

conns_cls = [
    (cls_tenant, cls_usuario, "Composition", "1", "1..*"),
    (cls_usuario, cls_psicologo, "Generalization", "", ""),
    (cls_usuario, cls_paciente, "Generalization", "", ""),
    (cls_psicologo, cls_cita, "Association", "1", "0..*"),
    (cls_paciente, cls_cita, "Association", "1", "0..*"),
    (cls_paciente, cls_token_fcm, "Association", "1", "0..*"),
    (cls_token_fcm, cls_notif, "Association", "1", "0..*"),
    (cls_paciente, cls_mood, "Composition", "1", "0..*"),
    (cls_paciente, cls_clasia, "Association", "1", "0..*"),
    (cls_clasia, cls_match, "Association", "1", "0..*"),
    (cls_psicologo, cls_match, "Association", "1", "0..*")
]

for s, e, ct, sc, dc in conns_cls:
    cid = create_connector(s, e, ct, f"{sc}..{dc}".strip('.'))
    link_connector(diag_clases_id, cid)

# ==============================================================================
# 3. ACTIVIDADES DEL SISTEMA - SPRINT 3 (5 DIAGRAMAS)
# ==============================================================================
pkg_act_id = create_package("3. Actividades del Sistema - Sprint 3", sp3_id)
print(f"  [3] Actividades Pkg [{pkg_act_id}]")

# 3.1 Actividad Despacho Push FCM (CU12)
pkg_act1 = create_package("3.1 Actividad - Despacho Push FCM (CU12)", pkg_act_id)
diag_act1 = create_diagram(pkg_act1, "Diagrama de Actividad - Despacho Push FCM (CU12)", "Activity")
n_init1 = create_object(pkg_act1, "", "StateNode", "Initial")
a1_1 = create_object(pkg_act1, "Cron Job Celery Beat ejecuta tarea cada 15 min", "Activity")
a1_2 = create_object(pkg_act1, "Consultar citas programadas en ventanas T-24h y T-1h", "Activity")
a1_3 = create_object(pkg_act1, "Consultar tokens FCM activos del paciente", "Activity")
d1_1 = create_object(pkg_act1, "¿Existe token FCM registrado?", "Decision")
a1_4 = create_object(pkg_act1, "Armar payload y despachar a FCM API", "Activity")
a1_5 = create_object(pkg_act1, "Registrar fallback SMS/Correo", "Activity")
a1_6 = create_object(pkg_act1, "FCM enruta a APNs / Google Android", "Activity")
a1_7 = create_object(pkg_act1, "Mostrar notificación en smartphone (Banner / Bandeja)", "Activity")
a1_8 = create_object(pkg_act1, "Paciente presiona alerta y abre Detalle de Cita", "Activity")
n_final1 = create_object(pkg_act1, "", "StateNode", "Final")

place_object(diag_act1, n_init1, -40, 240, 260, -60)
place_object(diag_act1, a1_1, -80, 130, 370, -130)
place_object(diag_act1, a1_2, -150, 130, 370, -200)
place_object(diag_act1, a1_3, -220, 130, 370, -270)
place_object(diag_act1, d1_1, -290, 235, 265, -320)
place_object(diag_act1, a1_4, -340, 130, 370, -390)
place_object(diag_act1, a1_5, -340, 420, 640, -390)
place_object(diag_act1, a1_6, -410, 130, 370, -460)
place_object(diag_act1, a1_7, -480, 130, 370, -530)
place_object(diag_act1, a1_8, -550, 130, 370, -600)
place_object(diag_act1, n_final1, -620, 240, 260, -640)

c_a1 = create_connector(n_init1, a1_1, "ControlFlow")
c_a2 = create_connector(a1_1, a1_2, "ControlFlow")
c_a3 = create_connector(a1_2, a1_3, "ControlFlow")
c_a4 = create_connector(a1_3, d1_1, "ControlFlow")
c_a5 = create_connector(d1_1, a1_4, "ControlFlow", "[Sí]")
c_a6 = create_connector(d1_1, a1_5, "ControlFlow", "[No]")
c_a7 = create_connector(a1_4, a1_6, "ControlFlow")
c_a8 = create_connector(a1_6, a1_7, "ControlFlow")
c_a9 = create_connector(a1_7, a1_8, "ControlFlow")
c_a10 = create_connector(a1_8, n_final1, "ControlFlow")
for cid in [c_a1, c_a2, c_a3, c_a4, c_a5, c_a6, c_a7, c_a8, c_a9, c_a10]:
    link_connector(diag_act1, cid)

# 3.2 Actividad Pipeline IA Triage (CU21)
pkg_act2 = create_package("3.2 Actividad - Pipeline Clasificación IA y Crisis (CU21)", pkg_act_id)
diag_act2 = create_diagram(pkg_act2, "Diagrama de Actividad - Pipeline Clasificación IA y Crisis (CU21)", "Activity")
n_init2 = create_object(pkg_act2, "", "StateNode", "Initial")
a2_1 = create_object(pkg_act2, "Paciente envía Cuestionario de Pre-consulta", "Activity")
a2_2 = create_object(pkg_act2, "Sanitización estricta de PII sensible (CI, Telf, Email)", "Activity")
a2_3 = create_object(pkg_act2, "Análisis NLP temático (Ansiedad, Depresión, Pareja, etc.)", "Activity")
d2_1 = create_object(pkg_act2, "¿Detecta patrones de ideación autolítica o crisis?", "Decision")
a2_4 = create_object(pkg_act2, "Activar bandera ALERTA_CRISIS = TRUE y severidad Crítica", "Activity")
a2_5 = create_object(pkg_act2, "Calcular nivel de severidad ordinario (Leve/Moderado/Severo)", "Activity")
a2_6 = create_object(pkg_act2, "Persistir resultado en clinica_clasificacionia", "Activity")
a2_7 = create_object(pkg_act2, "Desplegar caso en Consola Web Coordinador (Banner Rojo si Crisis)", "Activity")
n_final2 = create_object(pkg_act2, "", "StateNode", "Final")

place_object(diag_act2, n_init2, -40, 240, 260, -60)
place_object(diag_act2, a2_1, -80, 130, 370, -130)
place_object(diag_act2, a2_2, -150, 130, 370, -200)
place_object(diag_act2, a2_3, -220, 130, 370, -270)
place_object(diag_act2, d2_1, -290, 235, 265, -320)
place_object(diag_act2, a2_4, -340, 400, 650, -390)
place_object(diag_act2, a2_5, -340, 130, 370, -390)
place_object(diag_act2, a2_6, -420, 130, 370, -470)
place_object(diag_act2, a2_7, -490, 130, 370, -540)
place_object(diag_act2, n_final2, -560, 240, 260, -580)

ca2_1 = create_connector(n_init2, a2_1, "ControlFlow")
ca2_2 = create_connector(a2_1, a2_2, "ControlFlow")
ca2_3 = create_connector(a2_2, a2_3, "ControlFlow")
ca2_4 = create_connector(a2_3, d2_1, "ControlFlow")
ca2_5 = create_connector(d2_1, a2_4, "ControlFlow", "[Sí: Riesgo Vital]")
ca2_6 = create_connector(d2_1, a2_5, "ControlFlow", "[No: Ordinario]")
ca2_7 = create_connector(a2_4, a2_6, "ControlFlow")
ca2_8 = create_connector(a2_5, a2_6, "ControlFlow")
ca2_9 = create_connector(a2_6, a2_7, "ControlFlow")
ca2_10 = create_connector(a2_7, n_final2, "ControlFlow")
for cid in [ca2_1, ca2_2, ca2_3, ca2_4, ca2_5, ca2_6, ca2_7, ca2_8, ca2_9, ca2_10]:
    link_connector(diag_act2, cid)

# 3.3 Actividad Matching IA (CU22)
pkg_act3 = create_package("3.3 Actividad - Matching IA y Validación Humana (CU22)", pkg_act_id)
diag_act3 = create_diagram(pkg_act3, "Diagrama de Actividad - Matching IA y Validación Humana (CU22)", "Activity")
n_init3 = create_object(pkg_act3, "", "StateNode", "Initial")
a3_1 = create_object(pkg_act3, "Coordinador solicita sugerencias de matching en consola web", "Activity")
a3_2 = create_object(pkg_act3, "Evaluar afinidad especialidad (40%), horario (30%), carga (20%), mod (10%)", "Activity")
a3_3 = create_object(pkg_act3, "Ordenar descendentemente y seleccionar candidatos Top 3", "Activity")
a3_4 = create_object(pkg_act3, "Renderizar Top 3 con desglose factorial en Angular 17", "Activity")
d3_1 = create_object(pkg_act3, "¿Coordinador aprueba candidato recomendado #1?", "Decision")
a3_5 = create_object(pkg_act3, "Aprobar asignación sugerida", "Activity")
a3_6 = create_object(pkg_act3, "Seleccionar terapeuta alternativo e ingresar justificación", "Activity")
a3_7 = create_object(pkg_act3, "Persistir asignación en BD y registrar decisión humana en bitácora", "Activity")
n_final3 = create_object(pkg_act3, "", "StateNode", "Final")

place_object(diag_act3, n_init3, -40, 240, 260, -60)
place_object(diag_act3, a3_1, -80, 130, 370, -130)
place_object(diag_act3, a3_2, -150, 130, 370, -200)
place_object(diag_act3, a3_3, -220, 130, 370, -270)
place_object(diag_act3, a3_4, -290, 130, 370, -340)
place_object(diag_act3, d3_1, -360, 235, 265, -390)
place_object(diag_act3, a3_5, -420, 130, 370, -470)
place_object(diag_act3, a3_6, -420, 420, 680, -470)
place_object(diag_act3, a3_7, -500, 130, 370, -550)
place_object(diag_act3, n_final3, -570, 240, 260, -590)

ca3_1 = create_connector(n_init3, a3_1, "ControlFlow")
ca3_2 = create_connector(a3_1, a3_2, "ControlFlow")
ca3_3 = create_connector(a3_2, a3_3, "ControlFlow")
ca3_4 = create_connector(a3_3, a3_4, "ControlFlow")
ca3_5 = create_connector(a3_4, d3_1, "ControlFlow")
ca3_6 = create_connector(d3_1, a3_5, "ControlFlow", "[Sí: Confirmar]")
ca3_7 = create_connector(d3_1, a3_6, "ControlFlow", "[No: Cambio Manual]")
ca3_8 = create_connector(a3_5, a3_7, "ControlFlow")
ca3_9 = create_connector(a3_6, a3_7, "ControlFlow")
ca3_10 = create_connector(a3_7, n_final3, "ControlFlow")
for cid in [ca3_1, ca3_2, ca3_3, ca3_4, ca3_5, ca3_6, ca3_7, ca3_8, ca3_9, ca3_10]:
    link_connector(diag_act3, cid)

# 3.4 Actividad Flujo Móvil Flutter (CU2, CU11, CU13)
pkg_act4 = create_package("3.4 Actividad - Flujo Móvil de Pacientes en Flutter (CU2, CU11, CU13)", pkg_act_id)
diag_act4 = create_diagram(pkg_act4, "Diagrama de Actividad - Flujo Móvil de Pacientes en Flutter", "Activity")
n_init4 = create_object(pkg_act4, "", "StateNode", "Initial")
a4_1 = create_object(pkg_act4, "Paciente abre app móvil Flutter", "Activity")
d4_1 = create_object(pkg_act4, "¿Existe Refresh Token válido?", "Decision")
a4_2 = create_object(pkg_act4, "Renovar Access Token transparente", "Activity")
a4_3 = create_object(pkg_act4, "Login con correo y contraseña", "Activity")
a4_4 = create_object(pkg_act4, "Renderizar Dashboard Móvil", "Activity")
d4_2 = create_object(pkg_act4, "¿Selecciona Mis Citas o Sala Virtual?", "Decision")
a4_5 = create_object(pkg_act4, "Navegar a Mis Citas (Próximas/Historial)", "Activity")
d4_3 = create_object(pkg_act4, "¿Cancelar cita > 24 horas?", "Decision")
a4_6 = create_object(pkg_act4, "Confirmar cancelación y liberar cupo", "Activity")
a4_7 = create_object(pkg_act4, "Bloquear y mostrar teléfono centro", "Activity")
a4_8 = create_object(pkg_act4, "Conectar Teleconsulta WebRTC Jitsi", "Activity")
n_final4 = create_object(pkg_act4, "", "StateNode", "Final")

place_object(diag_act4, n_init4, -40, 240, 260, -60)
place_object(diag_act4, a4_1, -80, 130, 370, -130)
place_object(diag_act4, d4_1, -150, 235, 265, -180)
place_object(diag_act4, a4_2, -210, 80, 270, -260)
place_object(diag_act4, a4_3, -210, 330, 520, -260)
place_object(diag_act4, a4_4, -290, 180, 420, -340)
place_object(diag_act4, d4_2, -370, 235, 265, -400)
place_object(diag_act4, a4_5, -430, 50, 270, -480)
place_object(diag_act4, d4_3, -500, 140, 170, -530)
place_object(diag_act4, a4_6, -560, 40, 220, -610)
place_object(diag_act4, a4_7, -560, 250, 430, -610)
place_object(diag_act4, a4_8, -430, 330, 550, -480)
place_object(diag_act4, n_final4, -640, 240, 260, -660)

ca4_1 = create_connector(n_init4, a4_1, "ControlFlow")
ca4_2 = create_connector(a4_1, d4_1, "ControlFlow")
ca4_3 = create_connector(d4_1, a4_2, "ControlFlow", "[Sí]")
ca4_4 = create_connector(d4_1, a4_3, "ControlFlow", "[No]")
ca4_5 = create_connector(a4_2, a4_4, "ControlFlow")
ca4_6 = create_connector(a4_3, a4_4, "ControlFlow")
ca4_7 = create_connector(a4_4, d4_2, "ControlFlow")
ca4_8 = create_connector(d4_2, a4_5, "ControlFlow", "[Mis Citas]")
ca4_9 = create_connector(d4_2, a4_8, "ControlFlow", "[Teleconsulta]")
ca4_10 = create_connector(a4_5, d4_3, "ControlFlow")
ca4_11 = create_connector(d4_3, a4_6, "ControlFlow", "[> 24h]")
ca4_12 = create_connector(d4_3, a4_7, "ControlFlow", "[< 24h]")
ca4_13 = create_connector(a4_6, n_final4, "ControlFlow")
ca4_14 = create_connector(a4_7, n_final4, "ControlFlow")
ca4_15 = create_connector(a4_8, n_final4, "ControlFlow")
for cid in [ca4_1, ca4_2, ca4_3, ca4_4, ca4_5, ca4_6, ca4_7, ca4_8, ca4_9, ca4_10, ca4_11, ca4_12, ca4_13, ca4_14, ca4_15]:
    link_connector(diag_act4, cid)

# 3.5 Actividad Tareas y Mood Tracker (CU17)
pkg_act5 = create_package("3.5 Actividad - Tareas Terapéuticas y Mood Tracker Móvil (CU17)", pkg_act_id)
diag_act5 = create_diagram(pkg_act5, "Diagrama de Actividad - Tareas Terapéuticas y Mood Tracker Móvil", "Activity")
n_init5 = create_object(pkg_act5, "", "StateNode", "Initial")
a5_1 = create_object(pkg_act5, "Paciente accede a Salud Mental en App Flutter", "Activity")
d5_1 = create_object(pkg_act5, "¿Selecciona Mood Tracker o Tareas?", "Decision")
a5_2 = create_object(pkg_act5, "Registrar ánimo 1-5, factores y notas", "Activity")
a5_3 = create_object(pkg_act5, "Persistir en BD y actualizar tendencia emocional", "Activity")
a5_4 = create_object(pkg_act5, "Abrir detalle de tarea e instrucciones", "Activity")
a5_5 = create_object(pkg_act5, "Llenar autorregistro, dificultad y reflexiones", "Activity")
a5_6 = create_object(pkg_act5, "Enviar entrega y marcar ENTREGADA", "Activity")
a5_7 = create_object(pkg_act5, "Psicólogo revisa en expediente clínico web", "Activity")
n_final5 = create_object(pkg_act5, "", "StateNode", "Final")

place_object(diag_act5, n_init5, -40, 240, 260, -60)
place_object(diag_act5, a5_1, -80, 130, 370, -130)
place_object(diag_act5, d5_1, -150, 235, 265, -180)
place_object(diag_act5, a5_2, -210, 50, 250, -260)
place_object(diag_act5, a5_3, -280, 50, 250, -330)
place_object(diag_act5, a5_4, -210, 300, 500, -260)
place_object(diag_act5, a5_5, -280, 300, 500, -330)
place_object(diag_act5, a5_6, -350, 300, 500, -400)
place_object(diag_act5, a5_7, -420, 180, 420, -470)
place_object(diag_act5, n_final5, -490, 240, 260, -510)

ca5_1 = create_connector(n_init5, a5_1, "ControlFlow")
ca5_2 = create_connector(a5_1, d5_1, "ControlFlow")
ca5_3 = create_connector(d5_1, a5_2, "ControlFlow", "[Mood Tracker]")
ca5_4 = create_connector(d5_1, a5_4, "ControlFlow", "[Tareas]")
ca5_5 = create_connector(a5_2, a5_3, "ControlFlow")
ca5_6 = create_connector(a5_4, a5_5, "ControlFlow")
ca5_7 = create_connector(a5_5, a5_6, "ControlFlow")
ca5_8 = create_connector(a5_3, a5_7, "ControlFlow")
ca5_9 = create_connector(a5_6, a5_7, "ControlFlow")
ca5_10 = create_connector(a5_7, n_final5, "ControlFlow")
for cid in [ca5_1, ca5_2, ca5_3, ca5_4, ca5_5, ca5_6, ca5_7, ca5_8, ca5_9, ca5_10]:
    link_connector(diag_act5, cid)

# ==============================================================================
# 6. DIAGRAMAS DE COMUNICACIÓN - SPRINT 3
# ==============================================================================
pkg_com_id = create_package("6. Diagramas de Comunicación - Sprint 3", sp3_id)
print(f"  [6] Diagramas de Comunicación Pkg [{pkg_com_id}]")

COMMS = [
    {
        "pkg_name": "CU2 - Autenticación Móvil JWT",
        "diag_name": "Diagrama de Comunicación – CU2: Autenticación Móvil",
        "actor": "Paciente Móvil",
        "boundary": "IU_LoginMovil\n(Flutter)",
        "control": "CTR_AuthMovilController\n(Django REST)",
        "entity": "CE_UsuarioToken\n(PostgreSQL / Keystore)",
        "messages": [
            ("1: Ingresar email y password", 0, 1),
            ("2: POST /api/auth/login/", 1, 2),
            ("3: Validar hash credenciales y tenant", 2, 3),
            ("4: Generar access token y refresh JWT", 3, 2),
            ("5: 200 OK {tokens, user_profile}", 2, 1),
            ("6: Almacenar tokens en Keystore seguro", 1, 3),
            ("7: Redirigir a Dashboard Móvil", 1, 0),
        ]
    },
    {
        "pkg_name": "CU11 - Gestión y Cancelación de Cita Móvil",
        "diag_name": "Diagrama de Comunicación – CU11: Citas Móviles",
        "actor": "Paciente Móvil",
        "boundary": "IU_AgendaCitasMovil\n(Flutter)",
        "control": "CTR_CitasMovilController\n(Django REST)",
        "entity": "CE_Cita\n(PostgreSQL)",
        "messages": [
            ("1: Solicitar Mis Citas y Cancelación", 0, 1),
            ("2: GET /api/v1/agenda/citas/mis-citas/", 1, 2),
            ("3: SELECT * FROM agenda_cita WHERE pac_id", 2, 3),
            ("4: Retornar lista de citas", 3, 2),
            ("5: POST /api/v1/agenda/citas/{id}/cancelar/", 1, 2),
            ("6: Validar política anticipación > 24h", 2, 3),
            ("7: UPDATE estado='CANCELADA' y liberar horario", 2, 3),
            ("8: 200 OK {mensaje: 'Cita cancelada'}", 2, 1),
            ("9: Mostrar confirmación y refrescar lista", 1, 0),
        ]
    },
    {
        "pkg_name": "CU12 - Despacho de Recordatorio Push (FCM)",
        "diag_name": "Diagrama de Comunicación – CU12: Notificaciones Push FCM",
        "actor": "Cron Job Celery Beat",
        "boundary": "IU_FirebaseGateway\n(FCM API)",
        "control": "CTR_NotificacionPushController\n(Django)",
        "entity": "CE_TokenFCM\n(PostgreSQL)",
        "messages": [
            ("1: Trigger periódico cada 15 min", 0, 2),
            ("2: Consultar citas en ventana T-24h y T-1h", 2, 3),
            ("3: Obtener tokens FCM activos del paciente", 2, 3),
            ("4: Generar payload mensaje multicast", 2, 1),
            ("5: POST https://fcm.googleapis.com/v1/projects/.../messages:send", 1, 2),
            ("6: FCM responde 200 {name: 'projects/.../messages/123'}", 1, 2),
            ("7: INSERT INTO agenda_notificacioncita (enviado=True)", 2, 3),
            ("8: Despachar a smartphone receptor", 1, 0),
        ]
    },
    {
        "pkg_name": "CU21 - Clasificación Asistida del Motivo por IA",
        "diag_name": "Diagrama de Comunicación – CU21: Clasificación IA",
        "actor": "Paciente / Coordinador",
        "boundary": "IU_ConsolaTriajeWeb\n(Angular 17)",
        "control": "CTR_ClasificacionIAController\n(Django REST)",
        "entity": "CE_ClasificacionIA\n(PostgreSQL)",
        "messages": [
            ("1: Enviar formulario intake con motivo", 0, 1),
            ("2: POST /api/v1/ia/clasificar-motivo/", 1, 2),
            ("3: Sanitizar PII sensible por Regex", 2, 2),
            ("4: Inferencia NLP y evaluación de reglas crisis", 2, 3),
            ("5: INSERT INTO clinica_clasificacionia", 2, 3),
            ("6: 200 OK {area, severidad, alerta_crisis}", 2, 1),
            ("7: Mostrar tarjeta con banner rojo si crisis", 1, 0),
        ]
    },
    {
        "pkg_name": "CU22 - Emparejamiento y Asignación por IA",
        "diag_name": "Diagrama de Comunicación – CU22: Matching y Asignación IA",
        "actor": "Coordinador Clínico",
        "boundary": "IU_ConsolaMatchingWeb\n(Angular 17)",
        "control": "CTR_MatchingController\n(Django REST)",
        "entity": "CE_SugerenciaMatching\n(PostgreSQL)",
        "messages": [
            ("1: Solicitar matching para caso", 0, 1),
            ("2: GET /api/v1/ia/sugerir-psicologo/{pac_id}/", 1, 2),
            ("3: Calcular afinidad 40/30/20/10 terapeutas", 2, 3),
            ("4: Retornar Top 3 candidatos idóneos", 3, 2),
            ("5: 200 OK {candidatos_top3}", 2, 1),
            ("6: POST /api/v1/ia/confirmar-asignacion/", 1, 2),
            ("7: UPDATE paciente asignando terapeuta con log", 2, 3),
            ("8: 200 OK Asignación completada", 2, 1),
        ]
    }
]

for com in COMMS:
    pkg_c = create_package(com["pkg_name"], pkg_com_id)
    diag_c = create_diagram(pkg_c, com["diag_name"], "Communication")
    
    o_act = create_object(pkg_c, com["actor"], "Actor")
    o_b = create_object(pkg_c, com["boundary"], "Class", "boundary")
    o_ctrl = create_object(pkg_c, com["control"], "Class", "control")
    o_ent = create_object(pkg_c, com["entity"], "Class", "entity")
    
    place_object(diag_c, o_act, -80, 50, 140, -180)
    place_object(diag_c, o_b, -80, 300, 480, -180)
    place_object(diag_c, o_ctrl, -80, 680, 860, -180)
    place_object(diag_c, o_ent, -80, 1060, 1260, -180)
    
    objs = [o_act, o_b, o_ctrl, o_ent]
    for msg, s_idx, e_idx in com["messages"]:
        c = create_connector(objs[s_idx], objs[e_idx], "ControlFlow", msg)
        link_connector(diag_c, c)

# ==============================================================================
# 7. DIAGRAMAS DE SECUENCIA - SPRINT 3 (7 DIAGRAMAS)
# ==============================================================================
pkg_seq_id = create_package("7. Diagramas de Secuencia - Sprint 3", sp3_id)
print(f"  [7] Diagramas de Secuencia Pkg [{pkg_seq_id}]")

SEQS = [
    {
        "pkg_name": "CU2 - Secuencia Autenticación Móvil JWT",
        "diag_name": "Secuencia_CU2_Auth_Movil_JWT",
        "actor": "Paciente Móvil",
        "boundary": "IU_LoginMovil",
        "control": "CTR_AuthMovilController",
        "entity": "CE_UsuarioToken",
        "alt_name": "alt: Credenciales Válidas / Inválidas",
        "messages": [
            ("1: Ingresar credenciales (email, password)", 0, 1),
            ("2: POST /api/auth/login/", 1, 2),
            ("3: Validar hash y permisos tenant", 2, 3),
            ("4: Generar access token y refresh JWT", 3, 2),
            ("5: 200 OK {tokens, perfil}", 2, 1),
            ("6: Guardar tokens en Keystore seguro", 1, 3),
            ("7: Redirigir a Dashboard Móvil", 1, 0)
        ]
    },
    {
        "pkg_name": "CU11 - Secuencia Gestión y Cancelación de Cita Móvil",
        "diag_name": "Secuencia_CU11_Citas_Movil",
        "actor": "Paciente Móvil",
        "boundary": "IU_AgendaCitasMovil",
        "control": "CTR_CitasMovilController",
        "entity": "CE_Cita",
        "alt_name": "alt: Anticipación > 24h / Cancelación Tardía",
        "messages": [
            ("1: Solicitar Mis Citas", 0, 1),
            ("2: GET /api/v1/agenda/citas/mis-citas/", 1, 2),
            ("3: SELECT * FROM agenda_cita", 2, 3),
            ("4: Listado de citas", 3, 2),
            ("5: POST /api/v1/agenda/citas/{id}/cancelar/", 1, 2),
            ("6: Validar política anticipación > 24h", 2, 3),
            ("7: UPDATE estado='CANCELADA'", 2, 3),
            ("8: 200 OK Cita Cancelada", 2, 1),
            ("9: Confirmación en pantalla", 1, 0)
        ]
    },
    {
        "pkg_name": "CU12 - Secuencia Despacho de Recordatorio Push (FCM)",
        "diag_name": "Secuencia_CU12_Notificaciones_Push_FCM",
        "actor": "Cron Celery Beat",
        "boundary": "IU_FirebaseGateway",
        "control": "CTR_NotificacionPushController",
        "entity": "CE_TokenFCM",
        "alt_name": "loop: Cada 15 min [Ventanas T-24h y T-1h]",
        "messages": [
            ("1: Trigger periódico cron", 0, 2),
            ("2: Consultar citas en ventana T-24h / T-1h", 2, 3),
            ("3: Obtener tokens FCM activos", 2, 3),
            ("4: Armar payload y despachar a Firebase", 2, 1),
            ("5: POST /v1/projects/.../messages:send", 1, 2),
            ("6: 200 OK Message ID", 1, 2),
            ("7: INSERT INTO agenda_notificacioncita", 2, 3),
            ("8: Despacho a smartphone receptor", 1, 0)
        ]
    },
    {
        "pkg_name": "CU13 - Secuencia Teleconsulta Móvil Nativa WebRTC",
        "diag_name": "Secuencia_CU13_Teleconsulta_Movil_WebRTC",
        "actor": "Paciente Móvil",
        "boundary": "IU_TeleconsultaJitsi",
        "control": "CTR_TeleconsultaController",
        "entity": "CE_SesionTeleconsulta",
        "alt_name": "opt: Horario de Cita Vigente",
        "messages": [
            ("1: Presionar 'Entrar a Sala Virtual'", 0, 1),
            ("2: GET /api/v1/teleconsulta/sesion/{id}/token/", 1, 2),
            ("3: Validar horario y generar JWT Jitsi", 2, 3),
            ("4: Retornar token de sala cifrado", 3, 2),
            ("5: 200 OK {sala_uuid, jwt_token}", 2, 1),
            ("6: Conectar audio y video WebRTC", 1, 3),
            ("7: Finalizar teleconsulta y registrar duración", 1, 2)
        ]
    },
    {
        "pkg_name": "CU17 - Secuencia Seguimiento de Tareas y Mood Tracker Móvil",
        "diag_name": "Secuencia_CU17_Tareas_Mood_Movil",
        "actor": "Paciente Móvil",
        "boundary": "IU_TareasMoodScreen",
        "control": "CTR_TareasMoodController",
        "entity": "CE_TareaTerapeutica",
        "alt_name": "alt: Entrega Tarea / Registro Mood Tracker",
        "messages": [
            ("1: Abrir Tarea / Mood Tracker", 0, 1),
            ("2: POST /api/v1/clinica/tareas/{id}/entregar/", 1, 2),
            ("3: Persistir evidencia, dificultad y reflexión", 2, 3),
            ("4: Actualizar estado a 'ENTREGADA'", 3, 2),
            ("5: POST /api/v1/clinica/mood-tracker/", 1, 2),
            ("6: INSERT INTO clinica_registroanimo", 2, 3),
            ("7: 200 OK {mensaje: 'Registrado con éxito'}", 2, 1),
            ("8: Actualizar gráfica emocional en app", 1, 0)
        ]
    },
    {
        "pkg_name": "CU21 - Secuencia Clasificación Asistida del Motivo por IA",
        "diag_name": "Secuencia_CU21_Clasificacion_IA",
        "actor": "Paciente / Coordinador",
        "boundary": "IU_ConsolaTriajeWeb",
        "control": "CTR_ClasificacionIAController",
        "entity": "CE_ClasificacionIA",
        "alt_name": "alt: Alerta Crisis / Severidad Ordinaria",
        "messages": [
            ("1: Enviar cuestionario preconsulta", 0, 1),
            ("2: POST /api/v1/ia/clasificar-motivo/", 1, 2),
            ("3: Sanitizar PII sensible por Regex", 2, 2),
            ("4: Inferencia NLP y reglas heurísticas de severidad", 2, 3),
            ("5: INSERT INTO clinica_clasificacionia", 2, 3),
            ("6: 200 OK {area_tematica, severidad, alerta_crisis}", 2, 1),
            ("7: Renderizar tarjeta de triaje (Banner Rojo si Crisis)", 1, 0)
        ]
    },
    {
        "pkg_name": "CU22 - Secuencia Emparejamiento y Asignación por IA",
        "diag_name": "Secuencia_CU22_Matching_Asignacion_IA",
        "actor": "Coordinador Clínico",
        "boundary": "IU_ConsolaMatchingWeb",
        "control": "CTR_MatchingController",
        "entity": "CE_SugerenciaMatching",
        "alt_name": "alt: Aprobar Sugerencia #1 / Asignación Manual",
        "messages": [
            ("1: Solicitar matching para caso evaluado", 0, 1),
            ("2: GET /api/v1/ia/sugerir-psicologo/{pac_id}/", 1, 2),
            ("3: Calcular afinidad 40/30/20/10 terapeutas disponibles", 2, 3),
            ("4: Retornar candidatos Top 3 clasificados", 3, 2),
            ("5: 200 OK {top3_candidatos}", 2, 1),
            ("6: POST /api/v1/ia/confirmar-asignacion/", 1, 2),
            ("7: UPDATE paciente asignando terapeuta y registrar log", 2, 3),
            ("8: 200 OK Asignación completada", 2, 1),
            ("9: Actualizar expediente clínico asignado", 1, 0)
        ]
    }
]

for seq in SEQS:
    pkg_s = create_package(seq["pkg_name"], pkg_seq_id)
    diag_s = create_diagram(pkg_s, seq["diag_name"], "Sequence")
    
    o_act = create_object(pkg_s, seq["actor"], "Sequence")
    o_b = create_object(pkg_s, seq["boundary"], "Sequence")
    o_ctrl = create_object(pkg_s, seq["control"], "Sequence")
    o_ent = create_object(pkg_s, seq["entity"], "Sequence")
    o_frag = create_object(pkg_s, seq["alt_name"], "InteractionFragment")
    
    place_object(diag_s, o_act, -50, 60, 200, -100)
    place_object(diag_s, o_b, -50, 260, 440, -100)
    place_object(diag_s, o_ctrl, -50, 500, 680, -100)
    place_object(diag_s, o_ent, -50, 740, 920, -100)
    place_object(diag_s, o_frag, -250, 40, 940, -580)
    
    objs = [o_act, o_b, o_ctrl, o_ent]
    for msg, s_idx, e_idx in seq["messages"]:
        c = create_connector(objs[s_idx], objs[e_idx], "Sequence", msg, diag_id=diag_s)
        link_connector(diag_s, c)

# ==============================================================================
# 8. MÁQUINAS DE ESTADOS - SPRINT 3
# ==============================================================================
pkg_sm_id = create_package("8. Máquinas de Estados - Sprint 3", sp3_id)
print(f"  [8] Máquinas de Estados Pkg [{pkg_sm_id}]")

SM_LIST = [
    {
        "pkg_name": "Máquina 1 - Cita Médica Móvil (CU11)",
        "diag_name": "Diagrama de Estados – CU11: Ciclo de Vida de Cita Móvil",
        "states": ["PROGRAMADA", "CONFIRMADA_MOVIL", "SOLICITUD_CANCELACION_OPORTUNA", "CANCELADA_SISTEMA", "EN_TELECONSULTA_WEBRTC", "FINALIZADA"],
        "transitions": [
            (0, 1, "Agendamiento exitoso"),
            (1, 2, "Paciente confirma asistencia en app"),
            (2, 3, "Cancelar [Anticipación > 24h]"),
            (3, 4, "Liberar cupo en agenda"),
            (2, 5, "Horario cumplido e ingreso a Jitsi"),
            (5, 6, "Sesión concluida")
        ]
    },
    {
        "pkg_name": "Máquina 2 - Tarea Terapéutica Móvil (CU17)",
        "diag_name": "Diagrama de Estados – CU17: Ciclo de Vida de Tarea Móvil",
        "states": ["ASIGNADA_POR_TERAPEUTA", "PENDIENTE_EN_APP_MOVIL", "EN_PROGRESO_AUTORREGISTRO", "ENTREGADA_CON_REFLEXION", "REVISADA_EN_CONSULTA"],
        "transitions": [
            (0, 1, "Psicólogo prescribe tarea"),
            (1, 2, "Paciente abre detalle en app"),
            (2, 3, "Llenado de autorregistro y reflexiones"),
            (3, 4, "Enviar entrega con dificultad 1-5"),
            (4, 5, "Psicólogo valida en siguiente sesión")
        ]
    },
    {
        "pkg_name": "Máquina 3 - Triaje y Matching IA (CU21 / CU22)",
        "diag_name": "Diagrama de Estados – CU21 / CU22: Triaje y Matching IA",
        "states": ["INTAKE_RECIBIDO", "EN_SANITIZACION_PII", "CLASIFICADO_TEMATICA", "CRISIS_DETECTADA_ALERTA_ROJA", "TOP3_GENERADO_MATCHING", "ASIGNACION_CONFIRMADA_COORDINADOR"],
        "transitions": [
            (0, 1, "Ingesta de respuestas intake"),
            (1, 2, "Regex elimina datos sensibles PII"),
            (2, 3, "Inferencia NLP determina severidad"),
            (3, 4, "[Ideación autolítica detectada]"),
            (3, 5, "Algoritmo calcula scores 40/30/20/10"),
            (5, 6, "Coordinador aprueba candidato en consola web")
        ]
    },
    {
        "pkg_name": "Máquina 4 - Token FCM y Despacho Push (CU12)",
        "diag_name": "Diagrama de Estados – CU12: Token FCM y Despacho Push",
        "states": ["TOKEN_REGISTRADO_DISPOSITIVO", "ACTIVO_MONITOREO_CITAS", "RECORDATORIO_24H_DESPACHADO", "RECORDATORIO_1H_DESPACHADO", "INVALIDADO_APP_DESINSTALADA"],
        "transitions": [
            (0, 1, "Login exitoso y registro en comunicacion_tokenfcm"),
            (1, 2, "Cron escanea ventana T-24h"),
            (2, 3, "Multicast a FCM API exitoso"),
            (3, 4, "Cron escanea ventana T-1h y despacha alerta final"),
            (2, 5, "[Token no registrado en Firebase: Desactivar]")
        ]
    }
]

for sm in SM_LIST:
    pkg_s = create_package(sm["pkg_name"], pkg_sm_id)
    diag_s = create_diagram(pkg_s, sm["diag_name"], "Activity")
    
    n_in = create_object(pkg_s, "", "StateNode", "Initial")
    place_object(diag_s, n_in, -40, 240, 260, -60)
    
    st_objs = [n_in]
    top_pos = -90
    for st_name in sm["states"]:
        o_st = create_object(pkg_s, st_name, "Activity")
        place_object(diag_s, o_st, top_pos, 130, 420, top_pos - 50)
        top_pos -= 80
        st_objs.append(o_st)
        
    n_fi = create_object(pkg_s, "", "StateNode", "Final")
    place_object(diag_s, n_fi, top_pos, 240, 260, top_pos - 20)
    st_objs.append(n_fi)
    
    for s_idx, e_idx, tr_name in sm["transitions"]:
        start_obj = st_objs[s_idx]
        end_obj = st_objs[e_idx] if e_idx < len(st_objs) else st_objs[-1]
        c = create_connector(start_obj, end_obj, "ControlFlow", tr_name)
        link_connector(diag_s, c)
    c_fin = create_connector(st_objs[-2], n_fi, "ControlFlow")
    link_connector(diag_s, c_fin)

# ==============================================================================
# 9. NAVEGACIÓN DE VISTAS - SPRINT 3 (WAE CONALLEN)
# ==============================================================================
pkg_nav_id = create_package("9. Navegación de Vistas - Sprint 3", sp3_id)
print(f"  [9] Navegación WAE Pkg [{pkg_nav_id}]")

pkg_nav_glob = create_package("Mapa de Navegación Global (Sprint 0 al Sprint 3 Acumulado)", pkg_nav_id)
diag_nav_glob = create_diagram(pkg_nav_glob, "Navegacion_Sistema_Global_SIGEPSI_Sprint3", "Logical")
p_home = create_object(pkg_nav_glob, "PortalWeb_Angular17", "Class", "ClientPage")
p_movil = create_object(pkg_nav_glob, "AppMovil_Flutter3", "Class", "ClientPage")
p_api = create_object(pkg_nav_glob, "Backend_DjangoREST", "Class", "ServerPage")
place_object(diag_nav_glob, p_home, -100, 100, 300, -220)
place_object(diag_nav_glob, p_movil, -100, 450, 650, -220)
place_object(diag_nav_glob, p_api, -350, 280, 480, -470)
c_ng1 = create_connector(p_home, p_api, "Dependency", "REST TLS 1.3")
c_ng2 = create_connector(p_movil, p_api, "Dependency", "REST JWT")
link_connector(diag_nav_glob, c_ng1)
link_connector(diag_nav_glob, c_ng2)

pkg_nav_mov = create_package("Navegación Subsistema Móvil de Pacientes (Flutter 3.x)", pkg_nav_id)
diag_nav_mov = create_diagram(pkg_nav_mov, "Navegacion_Subsistema_Movil_Pacientes_Flutter", "Logical")
m_login = create_object(pkg_nav_mov, "LoginScreen\n(Flutter UI)", "Class", "ClientPage")
m_dash = create_object(pkg_nav_mov, "DashboardScreen\n(Flutter UI)", "Class", "ClientPage")
m_citas = create_object(pkg_nav_mov, "MisCitasScreen\n(Tabs: Próximas / Historial)", "Class", "ClientPage")
m_jitsi = create_object(pkg_nav_mov, "TeleconsultaJitsiScreen\n(WebRTC Plugin)", "Class", "ClientPage")
m_tareas = create_object(pkg_nav_mov, "TareasScreen\n(Lista y Entrega)", "Class", "ClientPage")
m_mood = create_object(pkg_nav_mov, "MoodTrackerScreen\n(Escala 1-5 y Contexto)", "Class", "ClientPage")

place_object(diag_nav_mov, m_login, -100, 50, 250, -200)
place_object(diag_nav_mov, m_dash, -100, 350, 550, -200)
place_object(diag_nav_mov, m_citas, -280, 200, 400, -380)
place_object(diag_nav_mov, m_jitsi, -450, 200, 400, -550)
place_object(diag_nav_mov, m_tareas, -280, 500, 700, -380)
place_object(diag_nav_mov, m_mood, -450, 500, 700, -550)

cnm1 = create_connector(m_login, m_dash, "Dependency", "Autenticación JWT exitosa")
cnm2 = create_connector(m_dash, m_citas, "Dependency", "Navegar a Mis Citas")
cnm3 = create_connector(m_citas, m_jitsi, "Dependency", "Entrar a Sala Virtual")
cnm4 = create_connector(m_dash, m_tareas, "Dependency", "Navegar a Tareas")
cnm5 = create_connector(m_dash, m_mood, "Dependency", "Registrar Ánimo Hoy")
for c in [cnm1, cnm2, cnm3, cnm4, cnm5]:
    link_connector(diag_nav_mov, c)

# ==============================================================================
# 10. DIAGRAMAS DE TIEMPO - SPRINT 3 (TIMING)
# ==============================================================================
pkg_time_id = create_package("10. Diagramas de Tiempo - Sprint 3", sp3_id)
print(f"  [10] Diagramas de Tiempo Pkg [{pkg_time_id}]")

TIMES = [
    ("Tiempo 1 - Sesión de Teleconsulta Móvil WebRTC", "Diagrama_Tiempo_Teleconsulta_Movil_WebRTC", ["Paciente_App_Flutter", "Servidor_WebRTC_Jitsi", "Psicologo_Portal_Web"]),
    ("Tiempo 2 - Pipeline IA y Detección de Crisis", "Diagrama_Tiempo_Pipeline_Clasificacion_IA_Crisis", ["Gateway_Intake", "Sanitizador_PII_Regex", "Motor_Inferencia_NLP", "Consola_Coordinador_Web"]),
    ("Tiempo 3 - Ciclo Notificación Push FCM", "Diagrama_Tiempo_Ciclo_Notificacion_Push_FCM", ["Cron_Celery_Beat", "FCM_Push_Dispatcher", "Firebase_APNs_Cloud", "Terminal_Smartphone_OS"])
]

for t_sub, d_name, timelines in TIMES:
    pkg_t = create_package(t_sub, pkg_time_id)
    diag_t = create_diagram(pkg_t, d_name, "Timing")
    y_pos = -30
    for tl_name in timelines:
        o_tl = create_object(pkg_t, tl_name, "TimeLine")
        place_object(diag_t, o_tl, y_pos, 30, 850, y_pos - 120)
        y_pos -= 150

# ==============================================================================
# 11. MODELO C4 DE ARQUITECTURA (NIVELES 1 AL 4)
# ==============================================================================
pkg_c4_id = create_package("11. Arquitectura de Software - Modelo C4 (Niveles 1 al 4) - Sprint 3", sp3_id)
print(f"  [11] Modelo C4 Pkg [{pkg_c4_id}]")

# C4 Nivel 1
pkg_c4_1 = create_package("C4 Nivel 1 - Contexto del Sistema (Sprint 3 Final)", pkg_c4_id)
diag_c4_1 = create_diagram(pkg_c4_1, "Modelo C4 - Nivel 1: Contexto del Sistema (Sprint 3 Final)", "Component")
c4_p1 = create_object(pkg_c4_1, "Paciente", "Actor")
c4_p2 = create_object(pkg_c4_1, "Psicólogo Clínico", "Actor")
c4_p3 = create_object(pkg_c4_1, "Coordinador Clínico", "Actor")
c4_sys = create_object(pkg_c4_1, "Plataforma SIGEPSI\n(Core SaaS Multi-Tenant)", "Component", "system")
c4_fcm = create_object(pkg_c4_1, "Firebase Cloud Messaging\n(FCM Push Service)", "Component", "external_system")
c4_jitsi = create_object(pkg_c4_1, "Servidor Jitsi Meet\n(WebRTC Teleconsulta)", "Component", "external_system")

place_object(diag_c4_1, c4_p1, -50, 100, 280, -180)
place_object(diag_c4_1, c4_p2, -50, 450, 630, -180)
place_object(diag_c4_1, c4_p3, -50, 800, 980, -180)
place_object(diag_c4_1, c4_sys, -300, 350, 750, -450)
place_object(diag_c4_1, c4_fcm, -550, 200, 450, -700)
place_object(diag_c4_1, c4_jitsi, -550, 650, 900, -700)

rc1 = create_connector(c4_p1, c4_sys, "InformationFlow", "Usa App Móvil Flutter y Portal Web [HTTPS]")
rc2 = create_connector(c4_p2, c4_sys, "InformationFlow", "Atiende sesiones, evalúa tareas [HTTPS]")
rc3 = create_connector(c4_p3, c4_sys, "InformationFlow", "Supervisa triaje y aprueba matching [HTTPS]")
rc4 = create_connector(c4_sys, c4_fcm, "Dependency", "Despacha alertas push multicast [REST / HTTPS]")
rc5 = create_connector(c4_sys, c4_jitsi, "Dependency", "Instancia salas virtuales dinámicas [WebRTC]")
for c in [rc1, rc2, rc3, rc4, rc5]:
    link_connector(diag_c4_1, c)

# C4 Nivel 2
pkg_c4_2 = create_package("C4 Nivel 2 - Contenedores (Lógica y Física)", pkg_c4_id)
diag_c4_2 = create_diagram(pkg_c4_2, "Modelo C4 - Nivel 2: Contenedores (Sprint 3)", "Component")
cnt_flutter = create_object(pkg_c4_2, "App Móvil Paciente\n(Flutter 3.x / Dart)", "Component", "container")
cnt_angular = create_object(pkg_c4_2, "Portal Web Clínico\n(Angular 17 / TS)", "Component", "container")
cnt_django = create_object(pkg_c4_2, "Backend API Gateway\n(Django REST / Python 3.11)", "Component", "container")
cnt_db = create_object(pkg_c4_2, "Base de Datos Relacional\n(PostgreSQL 16 Multi-Tenant)", "Component", "database")
cnt_redis = create_object(pkg_c4_2, "Cola de Tareas y Caché\n(Redis & Celery Beat)", "Component", "container")

place_object(diag_c4_2, cnt_flutter, -100, 100, 320, -250)
place_object(diag_c4_2, cnt_angular, -100, 450, 670, -250)
place_object(diag_c4_2, cnt_django, -350, 280, 500, -500)
place_object(diag_c4_2, cnt_db, -600, 150, 370, -750)
place_object(diag_c4_2, cnt_redis, -600, 450, 670, -750)

rcn1 = create_connector(cnt_flutter, cnt_django, "Dependency", "REST API / JWT TLS 1.3")
rcn2 = create_connector(cnt_angular, cnt_django, "Dependency", "REST API / JWT TLS 1.3")
rcn3 = create_connector(cnt_django, cnt_db, "Dependency", "django-tenants SQL")
rcn4 = create_connector(cnt_django, cnt_redis, "Dependency", "Trigger recordatorios push")
for c in [rcn1, rcn2, rcn3, rcn4]:
    link_connector(diag_c4_2, c)

# C4 Nivel 3
pkg_c4_3 = create_package("C4 Nivel 3 - Componentes Backend API Core", pkg_c4_id)
diag_c4_3 = create_diagram(pkg_c4_3, "Modelo C4 - Nivel 3: Componentes Backend API Core (Sprint 3)", "Component")
cmp_citas = create_object(pkg_c4_3, "CitasController\n(views.py)", "Component", "component")
cmp_fcm = create_object(pkg_c4_3, "FCMNotificationService\n(services.py)", "Component", "component")
cmp_triage = create_object(pkg_c4_3, "TriageMatchingController\n(views.py)", "Component", "component")
cmp_engine = create_object(pkg_c4_3, "IARulesEngine\n(ia_rules_engine.py)", "Component", "component")

place_object(diag_c4_3, cmp_citas, -100, 100, 320, -250)
place_object(diag_c4_3, cmp_fcm, -100, 450, 670, -250)
place_object(diag_c4_3, cmp_triage, -350, 100, 320, -500)
place_object(diag_c4_3, cmp_engine, -350, 450, 670, -500)

rc3_1 = create_connector(cmp_citas, cmp_fcm, "Dependency", "Solicita push 24h/1h")
rc3_2 = create_connector(cmp_triage, cmp_engine, "Dependency", "Clasificación NLP y Matching")
link_connector(diag_c4_3, rc3_1)
link_connector(diag_c4_3, rc3_2)

# C4 Nivel 4
pkg_c4_4 = create_package("C4 Nivel 4 - Código y Clases por Paquetes de Software", pkg_c4_id)
diag_c4_4 = create_diagram(pkg_c4_4, "Modelo C4 - Nivel 4: Código y Clases por Paquetes de Software", "Logical")
p4_1 = create_object(pkg_c4_4, "Paquete 1: Administración y Seguridad Multi-Tenant", "Package")
p4_2 = create_object(pkg_c4_4, "Paquete 2: Gestión Clínica y Expedientes", "Package")
p4_3 = create_object(pkg_c4_4, "Paquete 3: Agenda, Comunicación y FCM", "Package")
p4_5 = create_object(pkg_c4_4, "Paquete 5: Inteligencia Artificial y Triaje", "Package")

place_object(diag_c4_4, p4_1, -100, 100, 320, -250)
place_object(diag_c4_4, p4_2, -100, 450, 670, -250)
place_object(diag_c4_4, p4_3, -350, 100, 320, -500)
place_object(diag_c4_4, p4_5, -350, 450, 670, -500)

# ==============================================================================
# 12. DIAGRAMAS DE CLASES DE ANÁLISIS (BCE) - SPRINT 3 (REGLA DE ORO DOCENTE)
# ==============================================================================
pkg_bce_id = create_package("12. Diagramas de Clases de Análisis (BCE) - Sprint 3", sp3_id)
print(f"  [12] Clases de Análisis BCE Pkg [{pkg_bce_id}] (Regla de Oro)")

ANALYSIS_CASES = [
    {
        "cu_id": "CU2",
        "title": "CU2 - Clases de Análisis: Autenticación Móvil JWT",
        "actor": "Paciente Móvil",
        "boundary": "UI_LoginMovil",
        "control": "LoginMovilController",
        "primary_entity": "Usuario",
        "primary_attrs": [("id", "UUID"), ("email", "String"), ("rol", "String"), ("is_active", "Boolean")],
        "detail_entities": [
            ("TokenSesionJWT", [("access_token", "String"), ("refresh_token", "String"), ("expira_en", "DateTime")]),
            ("CredencialDispositivo", [("device_id", "String"), ("huella_digital", "String"), ("ultimo_login", "DateTime")])
        ]
    },
    {
        "cu_id": "CU11",
        "title": "CU11 - Clases de Análisis: Gestión de Citas Móviles",
        "actor": "Paciente Móvil",
        "boundary": "UI_GestionCitasMovil",
        "control": "CitaMovilController",
        "primary_entity": "Cita",
        "primary_attrs": [("id", "UUID"), ("fecha", "Date"), ("hora_inicio", "Time"), ("estado", "String"), ("modalidad", "String")],
        "detail_entities": [
            ("HorarioDisponible", [("dia_semana", "String"), ("rango_horario", "String"), ("cupo_libre", "Boolean")]),
            ("MotivoCancelacion", [("razon_cancelacion", "Text"), ("horas_anticipacion", "Integer"), ("reprogramable", "Boolean")])
        ]
    },
    {
        "cu_id": "CU12",
        "title": "CU12 - Clases de Análisis: Notificaciones Push FCM y Recordatorios",
        "actor": "Cron Job / Sistema",
        "boundary": "UI_PanelNotificacionesFCM",
        "control": "NotificacionFCMController",
        "primary_entity": "NotificacionCita",
        "primary_attrs": [("id", "UUID"), ("tipo_evento", "String"), ("titulo", "String"), ("cuerpo", "String"), ("enviado", "Boolean")],
        "detail_entities": [
            ("TokenFCM", [("token", "String"), ("dispositivo_tipo", "String"), ("activo", "Boolean")]),
            ("DispositivoMovil", [("modelo", "String"), ("sistema_operativo", "String"), ("version_app", "String")])
        ]
    },
    {
        "cu_id": "CU13",
        "title": "CU13 - Clases de Análisis: Teleconsulta WebRTC Móvil",
        "actor": "Paciente Móvil",
        "boundary": "UI_TeleconsultaWebRTC",
        "control": "TeleconsultaMovilController",
        "primary_entity": "SesionTeleconsulta",
        "primary_attrs": [("id", "UUID"), ("sala_uuid", "String"), ("jwt_token_jitsi", "String"), ("duracion_minutos", "Integer")],
        "detail_entities": [
            ("ConfiguracionJitsi", [("servidor_url", "String"), ("audio_mutado_inicio", "Boolean"), ("video_activo", "Boolean")])
        ]
    },
    {
        "cu_id": "CU17",
        "title": "CU17 - Clases de Análisis: Tareas y Mood Tracker Móvil",
        "actor": "Paciente Móvil",
        "boundary": "UI_SeguimientoTareasMood",
        "control": "TareasMoodController",
        "primary_entity": "TareaTerapeutica",
        "primary_attrs": [("id", "UUID"), ("titulo", "String"), ("descripcion", "Text"), ("estado", "String"), ("fecha_limite", "Date")],
        "detail_entities": [
            ("EvidenciaTarea", [("dificultad_percibida", "Integer"), ("reflexion_escrita", "Text"), ("fecha_entrega", "DateTime")]),
            ("RegistroAnimo", [("puntuacion_animo", "Integer"), ("emocion_dominante", "String"), ("factores_contexto", "String")])
        ]
    },
    {
        "cu_id": "CU21",
        "title": "CU21 - Clases de Análisis: Clasificación Asistida por IA",
        "actor": "Paciente / Coordinador",
        "boundary": "UI_ConsolaTriajeIA",
        "control": "ClasificacionIAController",
        "primary_entity": "ClasificacionIA",
        "primary_attrs": [("id", "UUID"), ("area_tematica", "String"), ("severidad", "String"), ("confianza", "Decimal"), ("alerta_crisis", "Boolean")],
        "detail_entities": [
            ("RespuestaPreConsulta", [("motivo_sanitizado", "Text"), ("escala_malestar", "Integer"), ("fecha_envio", "DateTime")]),
            ("AlertaCrisis", [("patron_detectado", "String"), ("nivel_urgencia", "String"), ("notificado_coordinador", "Boolean")])
        ]
    },
    {
        "cu_id": "CU22",
        "title": "CU22 - Clases de Análisis: Sugerencia y Asignación Asistida",
        "actor": "Coordinador Clínico",
        "boundary": "UI_ConsolaMatchingIA",
        "control": "MatchingController",
        "primary_entity": "SugerenciaMatching",
        "primary_attrs": [("id", "UUID"), ("score_total", "Decimal"), ("ranking", "Integer"), ("estado_aprobacion", "String"), ("fecha_resolucion", "DateTime")],
        "detail_entities": [
            ("CandidatoPsicologo", [("psicologo_id", "UUID"), ("nombre", "String"), ("especialidad_principal", "String"), ("pacientes_activos", "Integer")]),
            ("PuntuacionFactorial", [("score_esp", "Decimal"), ("score_disp", "Decimal"), ("score_carga", "Decimal"), ("score_mod", "Decimal")])
        ]
    }
]

UI_METHODS = [("crear()", "void"), ("editar()", "void"), ("eliminar()", "void"), ("mostrar()", "void")]
CTRL_METHODS = [("destroy()", "void"), ("index()", "void"), ("store()", "void"), ("update()", "void")]
ENTITY_METHODS = [("create()", "void"), ("delete()", "void"), ("get()", "void"), ("update()", "void")]

for ac in ANALYSIS_CASES:
    pkg_sub = create_package(ac["title"], pkg_bce_id)
    diag_bce = create_diagram(pkg_sub, "diagrama de clase nalisis", "Logical")
    
    # 1. Actor
    o_act = create_object(pkg_sub, ac["actor"], "Actor")
    place_object(diag_bce, o_act, -80, 50, 150, -180)
    
    # 2. Boundary Class (Methods only)
    b_name = f"{ac['cu_id']}::{ac['boundary']}"
    o_b = create_object(pkg_sub, b_name, "Class")
    for m, r in UI_METHODS:
        add_operation(o_b, m, r)
    place_object(diag_bce, o_b, -50, 240, 480, -260)
    
    # 3. Control Class (Methods only)
    ctrl_name = f"{ac['cu_id']}::{ac['control']}"
    o_ctrl = create_object(pkg_sub, ctrl_name, "Class")
    for m, r in CTRL_METHODS:
        add_operation(o_ctrl, m, r)
    place_object(diag_bce, o_ctrl, -50, 560, 800, -260)
    
    # 4. Primary Entity Class (Aggregate Root)
    prim_name = f"{ac['cu_id']}::{ac['primary_entity']}"
    o_prim = create_object(pkg_sub, prim_name, "Class")
    for a, t in ac["primary_attrs"]:
        add_attribute(o_prim, a, t)
    for m, r in ENTITY_METHODS:
        add_operation(o_prim, m, r)
    place_object(diag_bce, o_prim, -50, 880, 1140, -320)
    
    # Connect Actor -> Boundary -> Control -> Primary Entity
    c_ab = create_connector(o_act, o_b, "Association")
    c_bc = create_connector(o_b, o_ctrl, "Association")
    c_cp = create_connector(o_ctrl, o_prim, "Association")
    link_connector(diag_bce, c_ab)
    link_connector(diag_bce, c_bc)
    link_connector(diag_bce, c_cp)
    
    # 5. Detail Entities (Connected ONLY to Primary Entity - REGLA DE ORO)
    det_top = -50
    for det_name, det_attrs in ac["detail_entities"]:
        full_det_name = f"{ac['cu_id']}::{det_name}"
        o_det = create_object(pkg_sub, full_det_name, "Class")
        for a, t in det_attrs:
            add_attribute(o_det, a, t)
        for m, r in ENTITY_METHODS:
            add_operation(o_det, m, r)
        place_object(diag_bce, o_det, det_top, 1220, 1460, det_top - 200)
        det_top -= 240
        
        c_pd = create_connector(o_prim, o_det, "Composition", "1..*")
        link_connector(diag_bce, c_pd)

conn.Close()
print("\n=== All Sprint 3 Diagrams successfully created in DIAGRAMAS.eapx! ===")
