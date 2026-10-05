import win32com.client
import uuid
import os
import requests

eap_path = os.path.abspath(r"diagramas\DIAGRAMAS.eapx")
img_dir = os.path.abspath(r"documentacion\imagenes")
sprint2_path = os.path.abspath(r"documentacion\sprint2.md")
os.makedirs(img_dir, exist_ok=True)

conn = win32com.client.Dispatch('ADODB.Connection')
conn.Open(f'Provider=Microsoft.ACE.OLEDB.16.0;Data Source={eap_path};')

def guid():
    return '{' + str(uuid.uuid4()).upper() + '}'

# Clean up any existing package 12 under Sprint 2 (Package_ID = 89)
print("Cleaning up any existing Analysis Class packages in EAPX...")
rs, _ = conn.Execute("SELECT Package_ID FROM t_package WHERE Parent_ID = 89 AND (Name LIKE '%Clases de An%' OR Name LIKE '%12.%')")
old_pkg_ids = []
while not rs.EOF:
    old_pkg_ids.append(rs.Fields(0).Value)
    rs.MoveNext()

for pid in old_pkg_ids:
    rs_sub, _ = conn.Execute(f"SELECT Package_ID FROM t_package WHERE Parent_ID = {pid}")
    sub_ids = []
    while not rs_sub.EOF:
        sub_ids.append(rs_sub.Fields(0).Value)
        rs_sub.MoveNext()
    for sid in sub_ids:
        conn.Execute(f"DELETE FROM t_diagramobjects WHERE Diagram_ID IN (SELECT Diagram_ID FROM t_diagram WHERE Package_ID = {sid})")
        conn.Execute(f"DELETE FROM t_diagramlinks WHERE DiagramID IN (SELECT Diagram_ID FROM t_diagram WHERE Package_ID = {sid})")
        conn.Execute(f"DELETE FROM t_diagram WHERE Package_ID = {sid}")
        conn.Execute(f"DELETE FROM t_operation WHERE Object_ID IN (SELECT Object_ID FROM t_object WHERE Package_ID = {sid})")
        conn.Execute(f"DELETE FROM t_attribute WHERE Object_ID IN (SELECT Object_ID FROM t_object WHERE Package_ID = {sid})")
        conn.Execute(f"DELETE FROM t_connector WHERE Start_Object_ID IN (SELECT Object_ID FROM t_object WHERE Package_ID = {sid}) OR End_Object_ID IN (SELECT Object_ID FROM t_object WHERE Package_ID = {sid})")
        conn.Execute(f"DELETE FROM t_object WHERE Package_ID = {sid}")
        conn.Execute(f"DELETE FROM t_package WHERE Package_ID = {sid}")
    conn.Execute(f"DELETE FROM t_object WHERE Package_ID = 89 AND PDATA1 = '{pid}'")
    conn.Execute(f"DELETE FROM t_package WHERE Package_ID = {pid}")

print(f"Deleted old packages: {old_pkg_ids}")

# Create main package 12
sp2_id = 89
main_pkg_name = "12. Diagramas de Clases de Análisis (BCE) - Sprint 2"
g_main = guid()
conn.Execute(f"INSERT INTO t_package (Name, Parent_ID, ea_guid, Version) VALUES ('{main_pkg_name}', {sp2_id}, '{g_main}', '1.0')")
rs, _ = conn.Execute(f"SELECT Package_ID FROM t_package WHERE ea_guid = '{g_main}'")
main_pkg_id = rs.Fields(0).Value
conn.Execute(f"INSERT INTO t_object (Object_Type, Name, Package_ID, PDATA1, ea_guid, Scope, Status, Complexity, Author, Version) VALUES ('Package', '{main_pkg_name}', {sp2_id}, '{main_pkg_id}', '{guid()}', 'Public', 'Proposed', '1', 'User', '1.0')")
print(f"Created main package: {main_pkg_name} (ID {main_pkg_id})")

CASES = [
    {
        "cu_id": "CU14",
        "title": "CU14: Ficha Previa de Intake Digital",
        "subpkg_name": "CU14 - Clases de Análisis: Intake Digital",
        "cu_short": "CU14 Intake Digital",
        "actor": "Paciente",
        "ui_name": "UI_FormularioPreConsulta",
        "ctrl_name": "IntakeController",
        "entity_name": "RespuestaPreConsulta",
        "entity_attrs": [
            ("sintomas", "string"),
            ("escala_malestar", "int"),
            ("antecedentes", "string"),
            ("prioridad", "string"),
        ],
        "img_file": "diagrama_clases_analisis_cu14.png"
    },
    {
        "cu_id": "CU15",
        "title": "CU15: Historia Clínica y Control RBAC",
        "subpkg_name": "CU15 - Clases de Análisis: Historia Clínica y RBAC",
        "cu_short": "CU15 Historia Clinica",
        "actor": "Psicologo Tratante",
        "ui_name": "UI_HistoriaClinica",
        "ctrl_name": "HistoriaClinicaController",
        "entity_name": "HistoriaClinica",
        "entity_attrs": [
            ("diagnostico_cie10", "string"),
            ("motivo_consulta", "string"),
            ("estado", "string"),
            ("fecha_apertura", "string"),
        ],
        "img_file": "diagrama_clases_analisis_cu15.png"
    },
    {
        "cu_id": "CU16",
        "title": "CU16: Notas SOAP y Autoguardado Reactivo",
        "subpkg_name": "CU16 - Clases de Análisis: Notas SOAP",
        "cu_short": "CU16 Notas SOAP",
        "actor": "Psicologo Tratante",
        "ui_name": "UI_EditorNotasSOAP",
        "ctrl_name": "NotaSOAPController",
        "entity_name": "NotaSOAP",
        "entity_attrs": [
            ("subjetivo", "string"),
            ("objetivo", "string"),
            ("analisis", "string"),
            ("plan", "string"),
        ],
        "img_file": "diagrama_clases_analisis_cu16.png"
    },
    {
        "cu_id": "CU17",
        "title": "CU17: Tareas Terapéuticas y Feedback",
        "subpkg_name": "CU17 - Clases de Análisis: Tareas Terapéuticas",
        "cu_short": "CU17 Tareas Terapeuticas",
        "actor": "Paciente",
        "ui_name": "UI_GestionTareas",
        "ctrl_name": "TareaTerapeuticaController",
        "entity_name": "TareaTerapeutica",
        "entity_attrs": [
            ("titulo", "string"),
            ("descripcion", "string"),
            ("estado", "string"),
            ("fecha_limite", "string"),
        ],
        "img_file": "diagrama_clases_analisis_cu17.png"
    },
    {
        "cu_id": "CU18",
        "title": "CU18: Consentimiento Informado y Firma Digital",
        "subpkg_name": "CU18 - Clases de Análisis: Consentimiento Informado",
        "cu_short": "CU18 Consentimiento Informado",
        "actor": "Paciente",
        "ui_name": "UI_Consentimiento",
        "ctrl_name": "ConsentimientoController",
        "entity_name": "ConsentimientoInformado",
        "entity_attrs": [
            ("hash_sha256", "string"),
            ("firmado", "boolean"),
            ("ip_firmante", "string"),
            ("timestamp", "string"),
        ],
        "img_file": "diagrama_clases_analisis_cu18.png"
    },
    {
        "cu_id": "CU19",
        "title": "CU19: Cierre de Caso y Derivación Psiquiátrica",
        "subpkg_name": "CU19 - Clases de Análisis: Derivación Psiquiátrica",
        "cu_short": "CU19 Derivacion Psiquiatrica",
        "actor": "Psicologo Tratante",
        "ui_name": "UI_DerivacionPsiquiatrica",
        "ctrl_name": "DerivacionController",
        "entity_name": "DerivacionPsiquiatrica",
        "entity_attrs": [
            ("motivo_derivacion", "string"),
            ("nivel_urgencia", "string"),
            ("estado", "string"),
            ("medico_receptor", "string"),
        ],
        "img_file": "diagrama_clases_analisis_cu19.png"
    },
    {
        "cu_id": "CU20",
        "title": "CU20: Chatbot de Orientación Clínica",
        "subpkg_name": "CU20 - Clases de Análisis: Chatbot y Escalamiento",
        "cu_short": "CU20 Chatbot Orientacion",
        "actor": "Paciente",
        "ui_name": "UI_ChatbotClinico",
        "ctrl_name": "ChatbotController",
        "entity_name": "MensajeChat",
        "entity_attrs": [
            ("contenido", "string"),
            ("remitente", "string"),
            ("riesgo_detectado", "boolean"),
            ("timestamp", "string"),
        ],
        "img_file": "diagrama_clases_analisis_cu20.png"
    },
    {
        "cu_id": "HU-35",
        "title": "HU-35: Pasarela Ética de IA y Filtro de Seguridad",
        "subpkg_name": "HU-35 - Clases de Análisis: Pasarela Ética de IA",
        "cu_short": "HU35 Pasarela IA",
        "actor": "Psicologo Tratante",
        "ui_name": "UI_AsistenteIA",
        "ctrl_name": "PasarelaIAController",
        "entity_name": "PeticionIA",
        "entity_attrs": [
            ("prompt_sanitizado", "string"),
            ("respuesta_validada", "string"),
            ("filtro_etico_ok", "boolean"),
            ("tokens_usados", "int"),
        ],
        "img_file": "diagrama_clases_analisis_hu35.png"
    },
    {
        "cu_id": "CU5",
        "title": "CU5: Bitácora Confidencial en Disco Cifrado",
        "subpkg_name": "CU5 - Clases de Análisis: Bitácora Confidencial",
        "cu_short": "CU5 Bitacora Confidencial",
        "actor": "Administrador de Seguridad",
        "ui_name": "UI_BitacoraSeguridad",
        "ctrl_name": "BitacoraController",
        "entity_name": "RegistroBitacora",
        "entity_attrs": [
            ("evento", "string"),
            ("usuario_id", "string"),
            ("payload_cifrado", "string"),
            ("hash_integridad", "string"),
        ],
        "img_file": "diagrama_clases_analisis_cu5.png"
    },
    {
        "cu_id": "CU25",
        "title": "CU25: Reportes Personalizados QBE y Voz",
        "subpkg_name": "CU25 - Clases de Análisis: Reportes Personalizados QBE y Voz",
        "cu_short": "CU25 Reportes QBE",
        "actor": "Psicologo Tratante",
        "ui_name": "UI_GeneradorReportes",
        "ctrl_name": "ReporteController",
        "entity_name": "ReporteClinico",
        "entity_attrs": [
            ("formato", "string"),
            ("parametros_filtro", "string"),
            ("ruta_archivo", "string"),
            ("estado", "string"),
        ],
        "img_file": "diagrama_clases_analisis_cu25.png"
    },
    {
        "cu_id": "CU28",
        "title": "CU28: Copias de Seguridad Cifradas y Restauración",
        "subpkg_name": "CU28 - Clases de Análisis: Copias de Seguridad y Restauración",
        "cu_short": "CU28 Copias Seguridad",
        "actor": "Administrador del Sistema",
        "ui_name": "UI_GestionBackups",
        "ctrl_name": "BackupController",
        "entity_name": "CopiaSeguridad",
        "entity_attrs": [
            ("checksum_sha256", "string"),
            ("estado_cifrado", "string"),
            ("tamano_mb", "int"),
            ("timestamp", "string"),
        ],
        "img_file": "diagrama_clases_analisis_cu28.png"
    },
]

# Standard operations across all cases (matching teacher's exact image):
UI_METHODS = [("crear()", "void"), ("editar()", "void"), ("eliminar()", "void"), ("mostrar()", "void")]
CTRL_METHODS = [("destroy()", "void"), ("index()", "void"), ("store()", "void"), ("update()", "void")]
ENTITY_METHODS = [("create()", "void"), ("delete()", "void"), ("get()", "void"), ("update()", "void")]

style_ex_str = "ExcludeRTF=0;DocAll=0;HideQuals=0;AttPkg=1;ShowTests=0;ShowMaint=0;SuppressFOC=1;MatrixActive=0;SwimlanesActive=1;KanbanActive=0;MatrixLineWidth=1;MatrixLineClr=0;MatrixLocked=0;TConnectorNotation=UML 2.1;TExplicitNavigability=0;AdvancedElementProps=1;AdvancedFeatureProps=1;AdvancedConnectorProps=1;m_bElementClassifier=1;SPT=1;MDGDgm=;STBLDgm=;ShowNotes=0;VisibleAttributeDetail=0;ShowOpRetType=1;SuppressBrackets=0;SuppConnectorLabels=0;PrintPageHeadFoot=0;ShowAsList=0;SuppressedCompartments=;Theme=:119;"

ea_diag_map = {}

for c in CASES:
    print(f"\nProcessing {c['cu_id']} in EA...")
    g_sub = guid()
    conn.Execute(f"INSERT INTO t_package (Name, Parent_ID, ea_guid, Version) VALUES ('{c['subpkg_name']}', {main_pkg_id}, '{g_sub}', '1.0')")
    rs, _ = conn.Execute(f"SELECT Package_ID FROM t_package WHERE ea_guid = '{g_sub}'")
    subpkg_id = rs.Fields(0).Value
    conn.Execute(f"INSERT INTO t_object (Object_Type, Name, Package_ID, PDATA1, ea_guid, Scope, Status, Complexity, Author, Version) VALUES ('Package', '{c['subpkg_name']}', {main_pkg_id}, '{subpkg_id}', '{guid()}', 'Public', 'Proposed', '1', 'User', '1.0')")

    # Diagram: Logical (Class Diagram) with ShowBorder=True and Name='diagrama de clase nalisis'
    g_diag = guid()
    diag_title = "diagrama de clase nalisis"
    conn.Execute(f"""
        INSERT INTO t_diagram (Package_ID, Name, Diagram_Type, Orientation, cx, cy, Scale, ShowBorder, StyleEx, ea_guid)
        VALUES ({subpkg_id}, '{diag_title}', 'Logical', 'L', 1200, 800, 100, True, '{style_ex_str}', '{g_diag}')
    """)
    rs, _ = conn.Execute(f"SELECT Diagram_ID FROM t_diagram WHERE ea_guid = '{g_diag}'")
    diag_id = rs.Fields(0).Value
    ea_diag_map[c['cu_id']] = diag_id

    # 1. Actor
    g_act = guid()
    conn.Execute(f"""
        INSERT INTO t_object (Object_Type, Name, Package_ID, Scope, Status, Complexity, Author, Version, ea_guid)
        VALUES ('Actor', '{c['actor']}', {subpkg_id}, 'Public', 'Proposed', '1', 'User', '1.0', '{g_act}')
    """)
    rs, _ = conn.Execute(f"SELECT Object_ID FROM t_object WHERE ea_guid = '{g_act}'")
    act_id = rs.Fields(0).Value

    # 2. Boundary Class: No attributes, only methods
    b_name = f"{c['cu_short']}::{c['ui_name']}"
    g_b = guid()
    conn.Execute(f"""
        INSERT INTO t_object (Object_Type, Name, Package_ID, Scope, Status, Complexity, Author, Version, ea_guid)
        VALUES ('Class', '{b_name}', {subpkg_id}, 'Public', 'Proposed', '1', 'User', '1.0', '{g_b}')
    """)
    rs, _ = conn.Execute(f"SELECT Object_ID FROM t_object WHERE ea_guid = '{g_b}'")
    b_id = rs.Fields(0).Value
    for m_name, m_ret in UI_METHODS:
        conn.Execute(f"""
            INSERT INTO t_operation (Object_ID, Name, Type, Scope, ea_guid)
            VALUES ({b_id}, '{m_name}', '{m_ret}', 'Public', '{guid()}')
        """)

    # 3. Control Class: No attributes, only methods
    ctrl_name = f"{c['cu_short']}::{c['ctrl_name']}"
    g_ctrl = guid()
    conn.Execute(f"""
        INSERT INTO t_object (Object_Type, Name, Package_ID, Scope, Status, Complexity, Author, Version, ea_guid)
        VALUES ('Class', '{ctrl_name}', {subpkg_id}, 'Public', 'Proposed', '1', 'User', '1.0', '{g_ctrl}')
    """)
    rs, _ = conn.Execute(f"SELECT Object_ID FROM t_object WHERE ea_guid = '{g_ctrl}'")
    ctrl_id = rs.Fields(0).Value
    for m_name, m_ret in CTRL_METHODS:
        conn.Execute(f"""
            INSERT INTO t_operation (Object_ID, Name, Type, Scope, ea_guid)
            VALUES ({ctrl_id}, '{m_name}', '{m_ret}', 'Public', '{guid()}')
        """)

    # 4. Entity Class: Attributes + Methods
    e_name = f"{c['cu_short']}::{c['entity_name']}"
    g_e = guid()
    conn.Execute(f"""
        INSERT INTO t_object (Object_Type, Name, Package_ID, Scope, Status, Complexity, Author, Version, ea_guid)
        VALUES ('Class', '{e_name}', {subpkg_id}, 'Public', 'Proposed', '1', 'User', '1.0', '{g_e}')
    """)
    rs, _ = conn.Execute(f"SELECT Object_ID FROM t_object WHERE ea_guid = '{g_e}'")
    e_id = rs.Fields(0).Value
    for a_name, a_type in c['entity_attrs']:
        conn.Execute(f"""
            INSERT INTO t_attribute (Object_ID, Name, Type, Scope, ea_guid)
            VALUES ({e_id}, '{a_name}', '{a_type}', 'Private', '{guid()}')
        """)
    for m_name, m_ret in ENTITY_METHODS:
        conn.Execute(f"""
            INSERT INTO t_operation (Object_ID, Name, Type, Scope, ea_guid)
            VALUES ({e_id}, '{m_name}', '{m_ret}', 'Public', '{guid()}')
        """)

    # Connectors: Association lines Actor -> UI -> Controller -> Entity
    g_conn1 = guid()
    conn.Execute(f"INSERT INTO t_connector (Connector_Type, Start_Object_ID, End_Object_ID, Direction, ea_guid) VALUES ('Association', {act_id}, {b_id}, 'Unspecified', '{g_conn1}')")
    rs, _ = conn.Execute(f"SELECT Connector_ID FROM t_connector WHERE ea_guid = '{g_conn1}'")
    conn1_id = rs.Fields(0).Value

    g_conn2 = guid()
    conn.Execute(f"INSERT INTO t_connector (Connector_Type, Start_Object_ID, End_Object_ID, Direction, ea_guid) VALUES ('Association', {b_id}, {ctrl_id}, 'Unspecified', '{g_conn2}')")
    rs, _ = conn.Execute(f"SELECT Connector_ID FROM t_connector WHERE ea_guid = '{g_conn2}'")
    conn2_id = rs.Fields(0).Value

    g_conn3 = guid()
    conn.Execute(f"INSERT INTO t_connector (Connector_Type, Start_Object_ID, End_Object_ID, Direction, ea_guid) VALUES ('Association', {ctrl_id}, {e_id}, 'Unspecified', '{g_conn3}')")
    rs, _ = conn.Execute(f"SELECT Connector_ID FROM t_connector WHERE ea_guid = '{g_conn3}'")
    conn3_id = rs.Fields(0).Value

    # Diagram Objects (horizontal layout)
    conn.Execute(f"INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectRight, RectTop, RectBottom, Sequence, ObjectStyle) VALUES ({diag_id}, {act_id}, 40, 160, -90, -210, 1, 'DUID={guid()[:8]};')")
    conn.Execute(f"INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectRight, RectTop, RectBottom, Sequence, ObjectStyle) VALUES ({diag_id}, {b_id}, 240, 480, -50, -260, 2, 'DUID={guid()[:8]};')")
    conn.Execute(f"INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectRight, RectTop, RectBottom, Sequence, ObjectStyle) VALUES ({diag_id}, {ctrl_id}, 560, 800, -50, -260, 3, 'DUID={guid()[:8]};')")
    conn.Execute(f"INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectRight, RectTop, RectBottom, Sequence, ObjectStyle) VALUES ({diag_id}, {e_id}, 880, 1140, -50, -320, 4, 'DUID={guid()[:8]};')")

    # Diagram Links
    conn.Execute(f"INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Geometry, Style, Hidden) VALUES ({diag_id}, {conn1_id}, 'EDGE=2;', 'Mode=2;', False)")
    conn.Execute(f"INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Geometry, Style, Hidden) VALUES ({diag_id}, {conn2_id}, 'EDGE=2;', 'Mode=2;', False)")
    conn.Execute(f"INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Geometry, Style, Hidden) VALUES ({diag_id}, {conn3_id}, 'EDGE=2;', 'Mode=2;', False)")

conn.Close()
print("\n=== ENTERPRISE ARCHITECT DATABASE POPULATED SUCCESSFULLY ===")

# 2. Render all 11 PNGs using hide empty fields + frame syntax matching exact image
print("\n=== RENDERING ALL 11 PNGs MATCHING EXACT IMAGE FORMAT ===")
for c in CASES:
    puml = f"""@startuml
allowmixing
left to right direction
skinparam shadowing false
skinparam roundcorner 6
skinparam defaultFontName Arial
skinparam classAttributeIconSize 0
hide circle
hide empty fields

skinparam class {{
    BackgroundColor #FFFDF0
    BorderColor #9C6500
    ArrowColor #2C3E50
}}
skinparam frame {{
    BorderColor #2C3E50
    BackgroundColor white
}}

frame "sd diagrama de clase nalisis" {{
    actor "{c['actor']}" as act
    class "{c['cu_short']}::{c['ui_name']}" as UI {{
"""
    for m, r in UI_METHODS:
        puml += f"        + {m}: {r}\n"
    puml += f"""    }}
    class "{c['cu_short']}::{c['ctrl_name']}" as Ctrl {{
"""
    for m, r in CTRL_METHODS:
        puml += f"        + {m}: {r}\n"
    puml += f"""    }}
    class "{c['cu_short']}::{c['entity_name']}" as Ent {{
"""
    for a, t in c['entity_attrs']:
        puml += f"        - {a}: {t}\n"
    for m, r in ENTITY_METHODS:
        puml += f"        + {m}: {r}\n"
    puml += f"""    }}

    act -- UI
    UI -- Ctrl
    Ctrl -- Ent
}}
@enduml"""

    c['puml_styled'] = puml
    payload = {
        "diagram_source": puml,
        "diagram_type": "plantuml",
        "output_format": "png"
    }
    r = requests.post("https://kroki.io/plantuml/png", json=payload, timeout=25)
    if r.status_code == 200:
        out_path = os.path.join(img_dir, c['img_file'])
        with open(out_path, "wb") as f_out:
            f_out.write(r.content)
        print(f"  -> Generated {c['img_file']} ({len(r.content)} bytes)")
    else:
        print(f"  -> Error {r.status_code}: {r.text[:100]}")

# 3. Update sprint2.md
print("\n=== UPDATING sprint2.md ===")
with open(sprint2_path, "r", encoding="utf-8") as f:
    doc = f.read()

target_marker = "#### 6.2.1.4 Diseño de la Navegación de Vistas (Modelo WAE Conallen por Paquetes y Global)"
if "#### 6.2.1.3.2 Modelado Estático de Análisis (Diagramas de Clases de Análisis / Robustez BCE)" in doc:
    before_part = doc.split("#### 6.2.1.3.2 Modelado Estático de Análisis (Diagramas de Clases de Análisis / Robustez BCE)")[0]
    after_part = target_marker + doc.split(target_marker)[1]
else:
    before_part = doc.split(target_marker)[0]
    after_part = target_marker + doc.split(target_marker)[1]

sec_lines = []
sec_lines.append("#### 6.2.1.3.2 Modelado Estático de Análisis (Diagramas de Clases de Análisis / Robustez BCE)\n\n")
sec_lines.append("En estricta conformidad con el marco metodológico del Análisis y Diseño Orientado a Objetos (metodología RUP / Jacobson y directrices de la cátedra de Sistemas de Información II bajo el estándar **UML 2.5+**), los **Diagramas de Clases de Análisis** formalizan la vista estática de clases participantes en la realización de cada caso de uso clínico y de soporte técnico. Siguiendo el estándar de entrega académica requerido:\n\n")
sec_lines.append("* **Marco de Interacción (`sd diagrama de clase nalisis`):** Cada caso de uso delimita su contexto mediante un marco formal de interacción UML 2.5+.\n")
sec_lines.append("* **Actor (Monigote / Stick Figure):** Representa el actor humano o rol institucional iniciador de la interacción a la izquierda.\n")
sec_lines.append("* **Clase de Interfaz (`CU...::UI_...`):** Representada como clase rectangular con prefijo del caso de uso. Al modelar la vista de presentación, no expone atributos de persistencia, sino exclusivamente los métodos de interacción con el usuario (`crear(): void`, `editar(): void`, `eliminar(): void`, `mostrar(): void`).\n")
sec_lines.append("* **Clase Controladora (`CU...::...Controller`):** Representada como clase rectangular con prefijo del caso de uso. Al modelar la lógica de control del caso de uso, no posee atributos de estado interno de dominio, sino los métodos de control y despacho de acciones (`destroy(): void`, `index(): void`, `store(): void`, `update(): void`).\n")
sec_lines.append("* **Clase Entidad (`CU...::...`):** Representada como clase rectangular con dos compartimentos: el compartimento superior con sus atributos privados de persistencia (`- atributo: tipo`) y el compartimento inferior con las operaciones básicas de persistencia (`create(): void`, `delete(): void`, `get(): void`, `update(): void`).\n")
sec_lines.append("* **Relaciones:** Líneas de asociación simples horizontales (`Actor -- UI -- Controller -- Entidad`).\n\n")

for c in CASES:
    d_id = ea_diag_map.get(c['cu_id'], 0)
    sec_lines.append(f"##### Diagrama de Clases de Análisis {c['cu_id']}: {c['title'].split(': ')[1]}\n\n")
    sec_lines.append(f"* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 2* → *12. Diagramas de Clases de Análisis (BCE) - Sprint 2* → *{c['subpkg_name']}* (**Diagrama: `diagrama de clase nalisis`, ID: {d_id}**).\n")
    sec_lines.append(f"* **Participantes:**\n")
    sec_lines.append(f"  * **Actor:** `{c['actor']}`\n")
    sec_lines.append(f"  * **Interfaz (`UI`):** `{c['cu_short']}::{c['ui_name']}` (solo métodos: `crear()`, `editar()`, `eliminar()`, `mostrar()`)\n")
    sec_lines.append(f"  * **Controlador (`Controller`):** `{c['cu_short']}::{c['ctrl_name']}` (solo métodos: `destroy()`, `index()`, `store()`, `update()`)\n")
    sec_lines.append(f"  * **Entidad (`Entity`):** `{c['cu_short']}::{c['entity_name']}` (atributos de dominio + métodos CRUD)\n\n")
    sec_lines.append(f"![Clases de Análisis {c['cu_id']}](./imagenes/{c['img_file']})\n\n")
    sec_lines.append("```plantuml\n")
    sec_lines.append(c['puml_styled'])
    sec_lines.append("\n```\n\n")

final_content = before_part + "".join(sec_lines) + after_part
with open(sprint2_path, "w", encoding="utf-8") as f:
    f.write(final_content)

print(f"Successfully updated {sprint2_path}!")
print("=== COMPLETED ALL TASKS ===")
