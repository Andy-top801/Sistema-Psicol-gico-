import win32com.client
import sys
import os
from PIL import Image

def crear_diagramas_comunicacion_sprint1():
    eapx_path = r'c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\diagramas\DIAGRAMAS.eapx'
    out_dir = r'c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\diagramas'
    
    print("Iniciando Enterprise Architect...")
    ea = win32com.client.Dispatch('EA.App')
    repo = ea.Repository
    
    if not repo.OpenFile(eapx_path):
        print(f"Error: No se pudo abrir {eapx_path}")
        return False
        
    print("DIAGRAMAS.eapx abierto exitosamente.")
    root_model = repo.Models.GetAt(0)
    
    # Buscar el paquete 'sprint 1'
    sprint1_pkg = None
    for pkg in root_model.Packages:
        if pkg.Name.lower() == "sprint 1":
            sprint1_pkg = pkg
            break
            
    if sprint1_pkg is None:
        print("Error: No se encontró el paquete 'sprint 1'")
        repo.CloseFile()
        repo.Exit()
        return False

    # Eliminar subpaquete previo "7. Diagramas de Comunicación - Sprint 1" si existe
    pkg_name = "7. Diagramas de Comunicación - Sprint 1"
    for i in range(sprint1_pkg.Packages.Count - 1, -1, -1):
        p = sprint1_pkg.Packages.GetAt(i)
        if p.Name == pkg_name or p.Name == "7. Diagramas de Comunicación":
            sprint1_pkg.Packages.Delete(i)
            print(f"Subpaquete previo '{p.Name}' eliminado.")
            break
            
    sprint1_pkg.Packages.Refresh()
    comm_root_pkg = sprint1_pkg.Packages.AddNew(pkg_name, "Package")
    comm_root_pkg.Update()
    sprint1_pkg.Packages.Refresh()
    print(f"Subpaquete '{pkg_name}' creado en sprint 1.")
    
    def add_diag_obj(diag, elem, left, top, right, bottom):
        do = diag.DiagramObjects.AddNew(f"l={left};r={right};t={top};b={bottom};", "")
        do.ElementID = elem.ElementID
        do.left = left
        do.top = top
        do.right = right
        do.bottom = bottom
        do.Update()
        return do
        
    def add_parallel_connectors(diag, conns_data):
        conn_objs = []
        for item in conns_data:
            src = item[0]
            tgt = item[1]
            name = item[2]
            y_off = item[3]
            x_off = item[4] if len(item) > 4 else 0
            
            c = src.Connectors.AddNew(name, "ControlFlow")
            c.SupplierID = tgt.ElementID
            c.Update()
            src.Connectors.Refresh()
            tgt.Connectors.Refresh()
            conn_objs.append((c, y_off, x_off))
            
        diag.Update()
        diag.DiagramLinks.Refresh()
        
        for i in range(diag.DiagramLinks.Count):
            dl = diag.DiagramLinks.GetAt(i)
            for c, y_off, x_off in conn_objs:
                if c.ConnectorID == dl.ConnectorID:
                    if x_off != 0:
                        dl.Geometry = f"SX={x_off};SY={y_off};EX={x_off};EY={y_off};"
                    else:
                        dl.Geometry = f"SX=0;SY={y_off};EX=0;EY={y_off};"
                    dl.Update()
                    break
        diag.Update()

    project = repo.GetProjectInterface()

    # Coordenadas estándar para la distribución BCE
    X_ACT = 60
    X_BND = 420
    X_CTR = 920
    X_ENT = 1460
    Y_TOP = -80
    Y_BOT = -180

    casos_de_uso = [
        {
            "id": "CU6",
            "title": "CU6 - Gestión de Psicólogos y Perfiles",
            "diag_name": "Diagrama de Comunicación – CU6: Gestión de Psicólogos",
            "file_name": "Diagrama de Comunicación - CU6 Gestion de Psicologos",
            "actor": "Administrador\ndel Centro",
            "boundary": "IU_GestionPsicologos\n(Angular)",
            "control": "CTR_Psicologo\n(Django)",
            "entity": "CE_Usuario_y_Psicologo\n(PostgreSQL)",
            "conns": [
                ("act", "bnd", "1: Ingresar datos de Psicólogo", 18),
                ("bnd", "act", "8: Mostrar confirmación", -18),
                ("bnd", "ctr", "2: POST /api/clinica/psicologos/", 18),
                ("ctr", "bnd", "7: 201 Created", -18),
                ("ctr", "ent", "3: Validar datos (email y colegiatura únicos)", 28),
                ("ent", "ctr", "4: Datos válidos", 12),
                ("ctr", "ent", "5: Crear Usuario y Psicólogo en esquema tenant", -12),
                ("ent", "ctr", "6: Registros creados exitosamente", -28),
            ]
        },
        {
            "id": "CU7",
            "title": "CU7 - Gestión de Pacientes Web y Móvil",
            "diag_name": "Diagrama de Comunicación – CU7: Gestión de Pacientes",
            "file_name": "Diagrama de Comunicación - CU7 Gestion de Pacientes",
            "actor": "Recepcionista /\nPaciente",
            "boundary": "IU_RegistroPacientes\n(Angular / Móvil)",
            "control": "CTR_Paciente\n(Django REST)",
            "entity": "CE_Paciente_y_Expediente\n(PostgreSQL)",
            "conns": [
                ("act", "bnd", "1: Ingresar datos (CI, fecha nac, tutor si menor)", 18),
                ("bnd", "act", "8: Mostrar 'Expediente clínico generado'", -18),
                ("bnd", "ctr", "2: POST /api/clinica/pacientes/ + Header Tenant", 18),
                ("ctr", "bnd", "7: 201 Created {paciente_id, expediente}", -18),
                ("ctr", "ent", "3: Validar unicidad de CI en tenant activo", 28),
                ("ent", "ctr", "4: Documento no duplicado y tutor válido", 12),
                ("ctr", "ent", "5: INSERT INTO clinica_paciente con código único", -12),
                ("ent", "ctr", "6: Paciente registrado en esquema tenant", -28),
            ]
        },
        {
            "id": "CU8",
            "title": "CU8 - Gestión de Disponibilidad y Horarios",
            "diag_name": "Diagrama de Comunicación – CU8: Disponibilidad Horaria",
            "file_name": "Diagrama de Comunicación - CU8 Gestion de Disponibilidad",
            "actor": "Psicólogo /\nAdministrador",
            "boundary": "IU_DisponibilidadHoraria\n(Angular)",
            "control": "CTR_Disponibilidad\n(Django REST)",
            "entity": "CE_Disponibilidad_y_Horario\n(PostgreSQL)",
            "conns": [
                ("act", "bnd", "1: Configurar franjas semanales y duración bloque", 18),
                ("bnd", "act", "8: Mostrar 'Horario laboral actualizado'", -18),
                ("bnd", "ctr", "2: POST /api/clinica/disponibilidad/ + JWT", 18),
                ("ctr", "bnd", "7: 200 OK {franjas_configuradas, slots_generados}", -18),
                ("ctr", "ent", "3: Validar coherencia (inicio < fin) sin traslapes", 28),
                ("ent", "ctr", "4: Franjas válidas y terapeuta activo", 12),
                ("ctr", "ent", "5: Guardar franjas y particionar bloques en DB", -12),
                ("ent", "ctr", "6: Disponibilidad persistida en esquema", -28),
            ]
        },
        {
            "id": "CU9",
            "title": "CU9 - Dashboard Clínico e Indicadores",
            "diag_name": "Diagrama de Comunicación – CU9: Dashboard Clínico",
            "file_name": "Diagrama de Comunicación - CU9 Dashboard Clinico",
            "actor": "Coordinador /\nAdministrador",
            "boundary": "IU_DashboardClinico\n(Angular 17)",
            "control": "CTR_Dashboard\n(Django REST)",
            "entity": "CE_Metricas_y_Citas\n(PostgreSQL)",
            "conns": [
                ("act", "bnd", "1: Acceder al Dashboard y seleccionar período", 18),
                ("bnd", "act", "8: Renderizar KPIs, gráficos de tasa y métricas", -18),
                ("bnd", "ctr", "2: GET /api/agenda/dashboard/kpis/?periodo=mes", 18),
                ("ctr", "bnd", "7: 200 OK {total_citas, ausentismo, ocupacion}", -18),
                ("ctr", "ent", "3: Validar permisos y esquema tenant", 28),
                ("ent", "ctr", "4: Contexto administrativo autorizado", 12),
                ("ctr", "ent", "5: SELECT COUNT, AVG(tasa_ausentismo) GROUP BY terapeuta", -12),
                ("ent", "ctr", "6: Agregaciones estadísticas calculadas", -28),
            ]
        },
        {
            "id": "CU10",
            "title": "CU10 - Alertas Tempranas y Priorización",
            "diag_name": "Diagrama de Comunicación – CU10: Alertas Tempranas",
            "file_name": "Diagrama de Comunicación - CU10 Alertas Tempranas",
            "actor": "Coordinador /\nPsicólogo",
            "boundary": "IU_AlertasClinicas\n(Angular)",
            "control": "CTR_AlertaService\n(Django REST)",
            "entity": "CE_Alerta_y_Asistencia\n(PostgreSQL)",
            "conns": [
                ("act", "bnd", "1: Consultar bandeja de alertas prioritarias", 18),
                ("bnd", "act", "8: Desplegar lista de pacientes en riesgo de abandono", -18),
                ("bnd", "ctr", "2: GET /api/agenda/alertas/?resuelta=false", 18),
                ("ctr", "bnd", "7: 200 OK {alertas_activas, nivel_riesgo: ALTO}", -18),
                ("ctr", "ent", "3: Evaluar historial de inasistencias consecutivas (2+)", 28),
                ("ent", "ctr", "4: Pacientes con ausentismo crítico identificados", 12),
                ("ctr", "ent", "5: INSERT / UPDATE agenda_alerta (prioridad='ALTA')", -12),
                ("ent", "ctr", "6: Alertas clínicas registradas en esquema", -28),
            ]
        },
        {
            "id": "CU11",
            "title": "CU11 - Gestión de Citas y Agenda",
            "diag_name": "Diagrama de Comunicación – CU11: Gestión de Citas",
            "file_name": "Diagrama de Comunicación - CU11 Gestion de Citas y Agenda",
            "actor": "Recepcionista /\nPaciente",
            "boundary": "IU_AgendaCitas\n(Angular / Móvil)",
            "control": "CTR_CitaService\n(Django REST)",
            "entity": "CE_Cita_y_Disponibilidad\n(PostgreSQL)",
            "conns": [
                ("act", "bnd", "1: Seleccionar paciente, terapeuta, fecha y slot", 18),
                ("bnd", "act", "8: Desplegar comprobante de cita confirmada", -18),
                ("bnd", "ctr", "2: POST /api/agenda/citas/ {fecha, hora, modalidad}", 18),
                ("ctr", "bnd", "7: 201 Created {cita_id, estado: 'PROGRAMADA'}", -18),
                ("ctr", "ent", "3: Iniciar tx y SELECT FOR UPDATE sobre slot", 28),
                ("ent", "ctr", "4: Bloqueo pesimista concedido (slot libre)", 12),
                ("ctr", "ent", "5: INSERT INTO agenda_cita y marcar slot ocupado", -12),
                ("ent", "ctr", "6: Cita registrada sin colisión horaria", -28),
            ]
        },
        {
            "id": "CU13",
            "title": "CU13 - Teleconsulta y Videoconferencias Jitsi Meet",
            "diag_name": "Diagrama de Comunicación – CU13: Teleconsulta Jitsi",
            "file_name": "Diagrama de Comunicación - CU13 Teleconsulta Jitsi Meet",
            "actor": "Terapeuta /\nPaciente",
            "boundary": "IU_Teleconsulta\n(Angular / Móvil)",
            "control": "CTR_Teleconsulta\n(Django REST)",
            "entity": "CE_Sala_y_Cita\n(PostgreSQL)",
            "conns": [
                ("act", "bnd", "1: Clic en 'Unirse a Teleconsulta'", 18),
                ("bnd", "act", "8: Embeber sala Jitsi Meet con controles de llamada", -18),
                ("bnd", "ctr", "2: GET /api/agenda/teleconsulta/{id}/access/ + JWT", 18),
                ("ctr", "bnd", "7: 200 OK {room_name, jwt_token, rol_moderador}", -18),
                ("ctr", "ent", "3: Validar ventana horaria activa (cita +/- 15 min)", 28),
                ("ent", "ctr", "4: Cita virtual vigente y usuario participante", 12),
                ("ctr", "ent", "5: INSERT INTO agenda_teleconsulta (room, fecha_inicio)", -12),
                ("ent", "ctr", "6: Sala registrada y credenciales generadas", -28),
            ]
        }
    ]

    for cu in casos_de_uso:
        print(f"Generando {cu['id']}: {cu['title']}...")
        pkg_cu = comm_root_pkg.Packages.AddNew(cu["title"], "Package")
        pkg_cu.Update()
        
        diag = pkg_cu.Diagrams.AddNew(cu["diag_name"], "Communication")
        diag.Update()
        
        act = pkg_cu.Elements.AddNew(cu["actor"], "Actor")
        act.Update()
        
        bnd = pkg_cu.Elements.AddNew(cu["boundary"], "Class")
        bnd.Stereotype = "boundary"
        bnd.Update()
        
        ctr = pkg_cu.Elements.AddNew(cu["control"], "Class")
        ctr.Stereotype = "control"
        ctr.Update()
        
        ent = pkg_cu.Elements.AddNew(cu["entity"], "Class")
        ent.Stereotype = "entity"
        ent.Update()
        
        add_diag_obj(diag, act, X_ACT, Y_TOP, X_ACT + 90, Y_BOT)
        add_diag_obj(diag, bnd, X_BND, Y_TOP, X_BND + 90, Y_BOT)
        add_diag_obj(diag, ctr, X_CTR, Y_TOP, X_CTR + 90, Y_BOT)
        add_diag_obj(diag, ent, X_ENT, Y_TOP, X_ENT + 90, Y_BOT)
        diag.Update()
        
        elem_map = {"act": act, "bnd": bnd, "ctr": ctr, "ent": ent}
        conns_data = []
        for c_item in cu["conns"]:
            s_elem = elem_map[c_item[0]]
            t_elem = elem_map[c_item[1]]
            msg_name = c_item[2]
            y_offset = c_item[3]
            conns_data.append((s_elem, t_elem, msg_name, y_offset))
            
        add_parallel_connectors(diag, conns_data)
        
        bmp_path = os.path.join(out_dir, f"{cu['file_name']}.bmp")
        png_path = os.path.join(out_dir, f"{cu['file_name']}.png")
        
        project.PutDiagramImageToFile(diag.DiagramGUID, bmp_path, 1)
        try:
            Image.open(bmp_path).save(png_path)
            print(f"  Exportado: {cu['file_name']}.png")
        except Exception as ex:
            print(f"  Error convirtiendo a PNG: {ex}")
            
    sprint1_pkg.Packages.Refresh()
    repo.CloseFile()
    repo.Exit()
    print("¡Todos los diagramas de comunicación del Sprint 1 generados exitosamente en EA!")
    return True

if __name__ == "__main__":
    crear_diagramas_comunicacion_sprint1()
