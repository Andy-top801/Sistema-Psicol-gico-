import os

sprint2_path = os.path.abspath(r"documentacion\sprint2.md")

with open(sprint2_path, "r", encoding="utf-8") as f:
    content = f.read()

target_marker = "#### 6.2.1.4 Diseño de la Navegación de Vistas (Modelo WAE Conallen por Paquetes y Global)"
if target_marker not in content:
    print(f"Error: target marker not found!")
    exit(1)

# Check if section was already inserted
if "#### 6.2.1.3.2 Modelado Estático de Análisis (Diagramas de Clases de Análisis / Robustez BCE)" in content:
    print("Section already present, replacing old section...")
    before_part = content.split("#### 6.2.1.3.2 Modelado Estático de Análisis (Diagramas de Clases de Análisis / Robustez BCE)")[0]
    after_part = target_marker + content.split(target_marker)[1]
else:
    before_part = content.split(target_marker)[0]
    after_part = target_marker + content.split(target_marker)[1]

from build_analysis_class_diagrams import SPECS

ea_diag_ids = {
    "CU14": 169,
    "CU15": 170,
    "CU16": 171,
    "CU17": 172,
    "CU18": 173,
    "CU19": 174,
    "CU20": 175,
    "HU-35": 176,
    "CU5": 177,
    "CU25": 178,
    "CU28": 179,
}

lines = []
lines.append("#### 6.2.1.3.2 Modelado Estático de Análisis (Diagramas de Clases de Análisis / Robustez BCE)\n")
lines.append("En estricta conformidad con el marco metodológico del Análisis y Diseño Orientado a Objetos (metodología RUP / Jacobson y directrices de la cátedra de Sistemas de Información II), los **Diagramas de Clases de Análisis** (también denominados Diagramas de Robustez en formato de Clases Estereotipadas) formalizan la vista estática inicial de la lógica de negocio para cada caso de uso. En estos diagramas:\n")
lines.append("* **Actor:** Representa al rol o actor del sistema que dispara y consume la funcionalidad del caso de uso.\n")
lines.append("* **Clase Interfaz (`<<boundary>>` / `UI_...`):** Modela el objeto de frontera o vista que media entre el actor y el sistema, encapsulando las operaciones de captura de datos, validación sintáctica reactiva y despliegue de respuestas/alertas en pantalla.\n")
lines.append("* **Clase Control (`<<control>>` / `...Controller`):** Modela la lógica y orquestación del caso de uso (controlador de aplicación / servicio REST), implementando los métodos de negocio, verificación de seguridad/RBAC y despacho transaccional.\n")
lines.append("* **Clase Entidad (`<<entity>>` / `...`):** Modela los objetos del dominio persistente y sus atributos fundamentales, así como sus operaciones de acceso y manipulación de datos (`create`, `get`, `update`, etc.).\n")
lines.append("\nTodos los métodos, atributos e interfaces modelados a continuación guardan **estricta y absoluta coherencia con los Diagramas de Comunicación BCE (sección 6.2.1.3) y los Diagramas de Secuencia UML (sección 6.2.1.3.1)**, garantizando una trazabilidad metodológica del 100% sin discrepancias de nombres ni signaturas.\n\n")

for s in SPECS:
    diag_id = ea_diag_ids.get(s['cu_id'], 0)
    lines.append(f"##### Diagrama de Clases de Análisis {s['cu_id']}: {s['title'].split(': ')[1]}\n\n")
    lines.append(f"* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 2* → *12. Diagramas de Clases de Análisis (BCE) - Sprint 2* → *{s['subpkg_name']}* (**Diagrama ID: {diag_id}**).\n")
    lines.append(f"* **Participantes del Patrón BCE:**\n")
    lines.append(f"  * **Actor Principal:** `{s['actor']}`\n")
    lines.append(f"  * **Clase Interfaz (`<<boundary>>`):** `{s['cu_short']}::{s['boundary']['name']}`\n")
    lines.append(f"  * **Clase Control (`<<control>>`):** `{s['cu_short']}::{s['control']['name']}`\n")
    lines.append(f"  * **Clase Entidad (`<<entity>>`):** `{s['cu_short']}::{s['entity']['name']}`\n\n")
    lines.append(f"![Clases de Análisis {s['cu_id']}](./imagenes/{s['img_file']})\n\n")
    lines.append("```plantuml\n")
    lines.append("@startuml\n")
    lines.append("left to right direction\n")
    lines.append("skinparam shadowing false\n")
    lines.append("skinparam roundcorner 8\n")
    lines.append("skinparam defaultFontName Arial\n")
    lines.append("skinparam classAttributeIconSize 0\n")
    lines.append("hide circle\n\n")
    lines.append(f"class \"{s['actor']}\" <<Actor>> #LightYellow\n\n")
    lines.append(f"class \"{s['cu_short']}::{s['boundary']['name']}\" as UI #EBF5FB {{\n")
    for m, r in s['boundary']['methods']:
        lines.append(f"    + {m}: {r}\n")
    lines.append("}\n\n")
    lines.append(f"class \"{s['cu_short']}::{s['control']['name']}\" as Controller #E8F8F5 {{\n")
    for m, r in s['control']['methods']:
        lines.append(f"    + {m}: {r}\n")
    lines.append("}\n\n")
    lines.append(f"class \"{s['cu_short']}::{s['entity']['name']}\" as Entity #FADBD8 {{\n")
    for a, t in s['entity']['attrs']:
        lines.append(f"    - {a}: {t}\n")
    lines.append("    __\n")
    for m, r in s['entity']['methods']:
        lines.append(f"    + {m}: {r}\n")
    lines.append("}\n\n")
    lines.append(f"\"{s['actor']}\" -- UI\n")
    lines.append("UI -- Controller\n")
    lines.append("Controller -- Entity\n")
    lines.append("@enduml\n")
    lines.append("```\n\n")

new_section_text = "".join(lines)
updated_content = before_part + new_section_text + after_part

with open(sprint2_path, "w", encoding="utf-8") as f:
    f.write(updated_content)

print(f"Successfully inserted analysis class diagrams into {sprint2_path}!")
