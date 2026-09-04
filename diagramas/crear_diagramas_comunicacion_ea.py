import win32com.client
import sys
import os
from PIL import Image

def crear_diagramas_comunicacion():
    eapx_path = r'c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\diagramas\DIAGRAMAS.eapx'
    
    print("Iniciando Enterprise Architect...")
    ea = win32com.client.Dispatch('EA.App')
    repo = ea.Repository
    
    if not repo.OpenFile(eapx_path):
        print("Error: No se pudo abrir el archivo .eapx")
        return
        
    print("Archivo .eapx abierto exitosamente.")
    root_model = repo.Models.GetAt(0)
    
    # Buscar el paquete principal "Sprint 0 - Arquitectura y Contexto"
    sprint0_pkg = None
    for pkg in root_model.Packages:
        if pkg.Name == "Sprint 0 - Arquitectura y Contexto":
            sprint0_pkg = pkg
            break
            
    if sprint0_pkg is None:
        print("Error: No se encontró el paquete 'Sprint 0 - Arquitectura y Contexto'")
        repo.CloseFile()
        repo.Exit()
        return
        
    # Eliminar subpaquete previo "7. Diagramas de Comunicación" si existe
    pkg_name = "7. Diagramas de Comunicación"
    for i in range(sprint0_pkg.Packages.Count - 1, -1, -1):
        p = sprint0_pkg.Packages.GetAt(i)
        if p.Name == pkg_name:
            sprint0_pkg.Packages.Delete(i)
            print(f"Paquete previo '{pkg_name}' eliminado para regeneración limpia.")
            break
            
    sprint0_pkg.Packages.Refresh()
    comm_root_pkg = sprint0_pkg.Packages.AddNew(pkg_name, "Package")
    comm_root_pkg.Update()
    sprint0_pkg.Packages.Refresh()
    print(f"Paquete '{pkg_name}' creado exitosamente.")
    
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
        """
        conns_data: list of tuples (source_elem, target_elem, message_name, y_offset, [x_offset])
        Creates individual directed ControlFlow connectors with specific vertical offsets.
        """
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
    out_dir = r'c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\diagramas'

    # Posiciones horizontales estándar para permitir flechas largas legibles
    X_ACT = 60
    X_BND = 420
    X_CTR = 920
    X_ENT = 1460
    
    Y_TOP = -80
    Y_BOT = -180

    # =========================================================================
    # 1. CU1: GESTIONAR CENTROS PSICOLÓGICOS Y CONFIGURACIÓN MULTI-TENANT
    # =========================================================================
    print("Creando Diagrama CU1: Multi-Tenant (Flechas individuales)...")
    pkg_cu1 = comm_root_pkg.Packages.AddNew("CU1 - Gestionar Centros y Multi-Tenant", "Package")
    pkg_cu1.Update()
    diag_cu1 = pkg_cu1.Diagrams.AddNew("Diagrama de Comunicación – CU1: Multi-Tenant", "Communication")
    diag_cu1.Update()
    
    act1 = pkg_cu1.Elements.AddNew("SuperAdministrador", "Actor")
    act1.Update()
    
    bnd1 = pkg_cu1.Elements.AddNew("IU_FormularioCentro\n(Angular)", "Class")
    bnd1.Stereotype = "boundary"
    bnd1.Update()
    
    ctr1 = pkg_cu1.Elements.AddNew("CTR_TenantService\n(Django)", "Class")
    ctr1.Stereotype = "control"
    ctr1.Update()
    
    ent1 = pkg_cu1.Elements.AddNew("CE_Tenant_y_Dominio\n(PostgreSQL)", "Class")
    ent1.Stereotype = "entity"
    ent1.Update()
    
    add_diag_obj(diag_cu1, act1, X_ACT, Y_TOP, X_ACT + 90, Y_BOT)
    add_diag_obj(diag_cu1, bnd1, X_BND, Y_TOP, X_BND + 90, Y_BOT)
    add_diag_obj(diag_cu1, ctr1, X_CTR, Y_TOP, X_CTR + 90, Y_BOT)
    add_diag_obj(diag_cu1, ent1, X_ENT, Y_TOP, X_ENT + 90, Y_BOT)
    diag_cu1.Update()
    
    conns_cu1 = [
        # Act <-> Bnd
        (act1, bnd1, "1: Ingresar datos de Centro", 18),
        (bnd1, act1, "10: Mostrar confirmación", -18),
        
        # Bnd <-> Ctr
        (bnd1, ctr1, "2: POST /api/tenants/", 18),
        (ctr1, bnd1, "9: 201 Created", -18),
        
        # Ctr <-> Ent (6 flechas individuales paralelas)
        (ctr1, ent1, "3: Valida disponibilidad Dominio", 36),
        (ent1, ctr1, "4: Dominio disponible", 22),
        (ctr1, ent1, "5: insert(Tenant, Dominio)", 7),
        (ent1, ctr1, "6: Registros creados", -7),
        (ctr1, ent1, "7: CREATE SCHEMA y Migraciones", -22),
        (ent1, ctr1, "8: Esquema creado", -36),
    ]
    add_parallel_connectors(diag_cu1, conns_cu1)
    
    bmp_cu1 = os.path.join(out_dir, "Diagrama de Comunicación - CU1 Multi-Tenant.bmp")
    png_cu1 = os.path.join(out_dir, "Diagrama de Comunicación - CU1 Multi-Tenant.png")
    project.PutDiagramImageToFile(diag_cu1.DiagramGUID, bmp_cu1, 1)
    try:
        Image.open(bmp_cu1).save(png_cu1)
    except Exception:
        pass
    print("CU1 completado.")

    # =========================================================================
    # 2. CU2: GESTIONAR INICIO DE SESIÓN Y AUTENTICACIÓN
    # =========================================================================
    print("Creando Diagrama CU2: Inicio de Sesión (Flechas individuales)...")
    pkg_cu2 = comm_root_pkg.Packages.AddNew("CU2 - Inicio de Sesión y Autenticación", "Package")
    pkg_cu2.Update()
    diag_cu2 = pkg_cu2.Diagrams.AddNew("Diagrama de Comunicación – CU2: Autenticación", "Communication")
    diag_cu2.Update()
    
    act2 = pkg_cu2.Elements.AddNew("Usuario\n(Todos los roles)", "Actor")
    act2.Update()
    
    bnd2 = pkg_cu2.Elements.AddNew("IU_Login\n(Angular / Móvil)", "Class")
    bnd2.Stereotype = "boundary"
    bnd2.Update()
    
    ctr2 = pkg_cu2.Elements.AddNew("CTR_AuthService\n(Django REST)", "Class")
    ctr2.Stereotype = "control"
    ctr2.Update()
    
    ent2 = pkg_cu2.Elements.AddNew("CE_Usuario_y_Tenant\n(PostgreSQL)", "Class")
    ent2.Stereotype = "entity"
    ent2.Update()
    
    add_diag_obj(diag_cu2, act2, X_ACT, Y_TOP, X_ACT + 90, Y_BOT)
    add_diag_obj(diag_cu2, bnd2, X_BND, Y_TOP, X_BND + 90, Y_BOT)
    add_diag_obj(diag_cu2, ctr2, X_CTR, Y_TOP, X_CTR + 90, Y_BOT)
    add_diag_obj(diag_cu2, ent2, X_ENT, Y_TOP, X_ENT + 90, Y_BOT)
    diag_cu2.Update()
    
    conns_cu2 = [
        # Act <-> Bnd
        (act2, bnd2, "1: Ingresar credenciales (email, password, tenant)", 18),
        (bnd2, act2, "10: Redirigir a Dashboard según rol", -18),
        
        # Bnd <-> Ctr
        (bnd2, ctr2, "2: POST /api/auth/login/", 18),
        (ctr2, bnd2, "9: 200 OK (access, refresh, usuario, rol)", -18),
        
        # Ctr <-> Ent
        (ctr2, ent2, "3: Validar tenant y conmutar schema", 36),
        (ent2, ctr2, "4: Esquema PostgreSQL activo", 22),
        (ctr2, ent2, "5: SELECT usuario WHERE email = ? AND activo = true", 7),
        (ent2, ctr2, "6: Retornar usuario y hash password", -7),
        (ctr2, ent2, "7: Verificar password (PBKDF2) y generar JWT", -22),
        (ent2, ctr2, "8: Tokens JWT generados (con claims)", -36),
    ]
    add_parallel_connectors(diag_cu2, conns_cu2)
    
    bmp_cu2 = os.path.join(out_dir, "Diagrama de Comunicación - CU2 Autenticación.bmp")
    png_cu2 = os.path.join(out_dir, "Diagrama de Comunicación - CU2 Autenticación.png")
    project.PutDiagramImageToFile(diag_cu2.DiagramGUID, bmp_cu2, 1)
    try:
        Image.open(bmp_cu2).save(png_cu2)
    except Exception:
        pass
    print("CU2 completado.")

    # =========================================================================
    # 3. CU2 (LOGOUT): CIERRE DE SESIÓN SEGURO
    # =========================================================================
    print("Creando Diagrama CU2: Logout (Flechas individuales)...")
    pkg_cu2_out = comm_root_pkg.Packages.AddNew("CU2 Logout - Cierre de Sesión Seguro", "Package")
    pkg_cu2_out.Update()
    diag_cu2_out = pkg_cu2_out.Diagrams.AddNew("Diagrama de Comunicación – CU2: Logout Seguro", "Communication")
    diag_cu2_out.Update()
    
    act2_out = pkg_cu2_out.Elements.AddNew("Usuario Autenticado\n(Todos los roles)", "Actor")
    act2_out.Update()
    
    bnd2_out = pkg_cu2_out.Elements.AddNew("IU_Navbar\n(Angular / Móvil)", "Class")
    bnd2_out.Stereotype = "boundary"
    bnd2_out.Update()
    
    ctr2_out = pkg_cu2_out.Elements.AddNew("CTR_AuthLogout\n(Django REST)", "Class")
    ctr2_out.Stereotype = "control"
    ctr2_out.Update()
    
    ent2_out = pkg_cu2_out.Elements.AddNew("CE_TokenBlacklist\n(PostgreSQL)", "Class")
    ent2_out.Stereotype = "entity"
    ent2_out.Update()
    
    add_diag_obj(diag_cu2_out, act2_out, X_ACT, Y_TOP, X_ACT + 90, Y_BOT)
    add_diag_obj(diag_cu2_out, bnd2_out, X_BND, Y_TOP, X_BND + 90, Y_BOT)
    add_diag_obj(diag_cu2_out, ctr2_out, X_CTR, Y_TOP, X_CTR + 90, Y_BOT)
    add_diag_obj(diag_cu2_out, ent2_out, X_ENT, Y_TOP, X_ENT + 90, Y_BOT)
    diag_cu2_out.Update()
    
    conns_cu2_out = [
        # Act <-> Bnd
        (act2_out, bnd2_out, "1: Click en 'Cerrar Sesión'", 18),
        (bnd2_out, act2_out, "8: Redirigir a pantalla de Login", -18),
        
        # Bnd <-> Ctr
        (bnd2_out, ctr2_out, "2: POST /api/auth/logout/ {refresh}", 18),
        (ctr2_out, bnd2_out, "7: 200 OK {'mensaje': 'Sesión cerrada'}", -18),
        
        # Ctr <-> Ent
        (ctr2_out, ent2_out, "3: Validar token y autenticación de usuario", 25),
        (ent2_out, ctr2_out, "4: Refresh token válido", 10),
        (ctr2_out, ent2_out, "5: INSERT INTO token_blacklist (token, fecha)", -10),
        (ent2_out, ctr2_out, "6: Token revocado en lista negra", -25),
    ]
    add_parallel_connectors(diag_cu2_out, conns_cu2_out)
    
    bmp_cu2_out = os.path.join(out_dir, "Diagrama de Comunicación - CU2 Logout Seguro.bmp")
    png_cu2_out = os.path.join(out_dir, "Diagrama de Comunicación - CU2 Logout Seguro.png")
    project.PutDiagramImageToFile(diag_cu2_out.DiagramGUID, bmp_cu2_out, 1)
    try:
        Image.open(bmp_cu2_out).save(png_cu2_out)
    except Exception:
        pass
    print("CU2 Logout completado.")

    # =========================================================================
    # 4. CU27: RECUPERAR CONTRASEÑA Y CREDENCIALES (COMO EN LA FOTO DEL USUARIO)
    # =========================================================================
    print("Creando Diagrama CU27: Recuperar Contraseña (Exacto a la foto)...")
    pkg_cu27 = comm_root_pkg.Packages.AddNew("CU27 - Recuperar Contraseña", "Package")
    pkg_cu27.Update()
    diag_cu27 = pkg_cu27.Diagrams.AddNew("Diagrama de Comunicación – CU27: Recuperar Contraseña", "Communication")
    diag_cu27.Update()
    
    act27 = pkg_cu27.Elements.AddNew("Usuario", "Actor")
    act27.Update()
    
    bnd27 = pkg_cu27.Elements.AddNew("IU_Recuperacion\n(Angular / Dart)", "Class")
    bnd27.Stereotype = "boundary"
    bnd27.Update()
    
    ctr27 = pkg_cu27.Elements.AddNew("CTR_PasswordReset\n(Django)", "Class")
    ctr27.Stereotype = "control"
    ctr27.Update()
    
    ent27 = pkg_cu27.Elements.AddNew("CE_Usuario\n(PostgreSQL)", "Class")
    ent27.Stereotype = "entity"
    ent27.Update()
    
    # Servidor_Email posicionado debajo del controlador CTR
    mail27 = pkg_cu27.Elements.AddNew("Servidor_Email", "Class")
    mail27.Stereotype = "boundary"
    mail27.Update()
    
    add_diag_obj(diag_cu27, act27, X_ACT, Y_TOP, X_ACT + 90, Y_BOT)
    add_diag_obj(diag_cu27, bnd27, X_BND, Y_TOP, X_BND + 90, Y_BOT)
    add_diag_obj(diag_cu27, ctr27, X_CTR, Y_TOP, X_CTR + 90, Y_BOT)
    add_diag_obj(diag_cu27, ent27, X_ENT, Y_TOP, X_ENT + 90, Y_BOT)
    add_diag_obj(diag_cu27, mail27, X_CTR, -280, X_CTR + 90, -370)
    diag_cu27.Update()
    
    conns_cu27 = [
        # Usuario <-> IU_Recuperacion (3 flechas como en la foto)
        (act27, bnd27, "1: Solicita recuperación", 25),
        (act27, bnd27, "7: Ingresa nueva contraseña", 0),
        (bnd27, act27, "12: Redirigir al Login", -25),
        
        # IU_Recuperacion <-> CTR_PasswordReset (4 flechas como en la foto)
        (bnd27, ctr27, "2: POST /password-reset/ (email)", 35),
        (ctr27, bnd27, "6: 200 OK (Confirmación)", 12),
        (bnd27, ctr27, "8: POST /password-reset/confirm/", -12),
        (ctr27, bnd27, "11: 200 OK (Contraseña cambiada)", -35),
        
        # CTR_PasswordReset <-> CE_Usuario (4 flechas como en la foto)
        (ctr27, ent27, "3: select_where(email)", 35),
        (ent27, ctr27, "4: Usuario validado", 12),
        (ctr27, ent27, "9: Actualiza(password)", -12),
        (ent27, ctr27, "10: Éxito en BD", -35),
        
        # CTR_PasswordReset -> Servidor_Email (1 flecha vertical hacia abajo)
        (ctr27, mail27, "5: Enviar correo con código", 0, 0),
    ]
    add_parallel_connectors(diag_cu27, conns_cu27)
    
    bmp_cu27 = os.path.join(out_dir, "Diagrama de Comunicación - CU27 Recuperar Contraseña.bmp")
    png_cu27 = os.path.join(out_dir, "Diagrama de Comunicación - CU27 Recuperar Contraseña.png")
    project.PutDiagramImageToFile(diag_cu27.DiagramGUID, bmp_cu27, 1)
    try:
        Image.open(bmp_cu27).save(png_cu27)
    except Exception:
        pass
    print("CU27 completado.")

    # =========================================================================
    # 5. CU3: GESTIONAR USUARIOS DEL CENTRO
    # =========================================================================
    print("Creando Diagrama CU3: Gestionar Usuarios (Flechas individuales)...")
    pkg_cu3 = comm_root_pkg.Packages.AddNew("CU3 - Gestionar Usuarios del Centro", "Package")
    pkg_cu3.Update()
    diag_cu3 = pkg_cu3.Diagrams.AddNew("Diagrama de Comunicación – CU3: Gestionar Usuarios", "Communication")
    diag_cu3.Update()
    
    act3 = pkg_cu3.Elements.AddNew("Administrador\ndel Centro", "Actor")
    act3.Update()
    
    bnd3 = pkg_cu3.Elements.AddNew("IU_GestionUsuarios\n(Angular)", "Class")
    bnd3.Stereotype = "boundary"
    bnd3.Update()
    
    ctr3 = pkg_cu3.Elements.AddNew("CTR_UsuarioService\n(Django REST)", "Class")
    ctr3.Stereotype = "control"
    ctr3.Update()
    
    ent3 = pkg_cu3.Elements.AddNew("CE_Usuario_y_Rol\n(PostgreSQL)", "Class")
    ent3.Stereotype = "entity"
    ent3.Update()
    
    add_diag_obj(diag_cu3, act3, X_ACT, Y_TOP, X_ACT + 90, Y_BOT)
    add_diag_obj(diag_cu3, bnd3, X_BND, Y_TOP, X_BND + 90, Y_BOT)
    add_diag_obj(diag_cu3, ctr3, X_CTR, Y_TOP, X_CTR + 90, Y_BOT)
    add_diag_obj(diag_cu3, ent3, X_ENT, Y_TOP, X_ENT + 90, Y_BOT)
    diag_cu3.Update()
    
    conns_cu3 = [
        # Act <-> Bnd
        (act3, bnd3, "1: Ingresar datos de nuevo usuario", 18),
        (bnd3, act3, "10: Mostrar confirmación 'Usuario creado'", -18),
        
        # Bnd <-> Ctr
        (bnd3, ctr3, "2: POST /api/users/ + JWT Header", 18),
        (ctr3, bnd3, "9: 201 Created {usuario_creado}", -18),
        
        # Ctr <-> Ent (6 flechas paralelas)
        (ctr3, ent3, "3: Validar JWT, TenantMiddleware y Admin Centro", 36),
        (ent3, ctr3, "4: Contexto tenant y permisos verificados", 22),
        (ctr3, ent3, "5: Validar unicidad de email", 7),
        (ent3, ctr3, "6: Email disponible en centro", -7),
        (ctr3, ent3, "7: INSERT INTO accounts_usuario", -22),
        (ent3, ctr3, "8: Usuario persistido en esquema tenant", -36),
    ]
    add_parallel_connectors(diag_cu3, conns_cu3)
    
    bmp_cu3 = os.path.join(out_dir, "Diagrama de Comunicación - CU3 Gestionar Usuarios.bmp")
    png_cu3 = os.path.join(out_dir, "Diagrama de Comunicación - CU3 Gestionar Usuarios.png")
    project.PutDiagramImageToFile(diag_cu3.DiagramGUID, bmp_cu3, 1)
    try:
        Image.open(bmp_cu3).save(png_cu3)
    except Exception:
        pass
    print("CU3 completado.")

    # =========================================================================
    # 6. CU4: ASIGNAR ROLES Y PERMISOS (RBAC)
    # =========================================================================
    print("Creando Diagrama CU4: Roles y Permisos (Flechas individuales)...")
    pkg_cu4 = comm_root_pkg.Packages.AddNew("CU4 - Asignar Roles y Permisos (RBAC)", "Package")
    pkg_cu4.Update()
    diag_cu4 = pkg_cu4.Diagrams.AddNew("Diagrama de Comunicación – CU4: Roles y Permisos", "Communication")
    diag_cu4.Update()
    
    act4 = pkg_cu4.Elements.AddNew("Administrador\ndel Centro", "Actor")
    act4.Update()
    
    bnd4 = pkg_cu4.Elements.AddNew("IU_GestionRoles\n(Angular)", "Class")
    bnd4.Stereotype = "boundary"
    bnd4.Update()
    
    ctr4 = pkg_cu4.Elements.AddNew("CTR_RolService\n(Django REST)", "Class")
    ctr4.Stereotype = "control"
    ctr4.Update()
    
    ent4 = pkg_cu4.Elements.AddNew("CE_Rol_y_Permiso\n(PostgreSQL)", "Class")
    ent4.Stereotype = "entity"
    ent4.Update()
    
    add_diag_obj(diag_cu4, act4, X_ACT, Y_TOP, X_ACT + 90, Y_BOT)
    add_diag_obj(diag_cu4, bnd4, X_BND, Y_TOP, X_BND + 90, Y_BOT)
    add_diag_obj(diag_cu4, ctr4, X_CTR, Y_TOP, X_CTR + 90, Y_BOT)
    add_diag_obj(diag_cu4, ent4, X_ENT, Y_TOP, X_ENT + 90, Y_BOT)
    diag_cu4.Update()
    
    conns_cu4 = [
        # Act <-> Bnd
        (act4, bnd4, "1: Seleccionar permisos para el rol", 18),
        (bnd4, act4, "10: Mostrar confirmación 'Permisos actualizados'", -18),
        
        # Bnd <-> Ctr
        (bnd4, ctr4, "2: PUT /api/roles/{id}/ {permisos: [ids]} + JWT", 18),
        (ctr4, bnd4, "9: 200 OK {rol_actualizado}", -18),
        
        # Ctr <-> Ent (6 flechas paralelas)
        (ctr4, ent4, "3: Validar JWT, permisos RBAC y esquema tenant", 36),
        (ent4, ctr4, "4: Permisos administrativos verificados", 22),
        (ctr4, ent4, "5: SELECT FROM accounts_permiso WHERE id IN (?)", 7),
        (ent4, ctr4, "6: Permisos validados", -7),
        (ctr4, ent4, "7: DELETE anteriores; INSERT accounts_rol_permiso", -22),
        (ent4, ctr4, "8: Nuevos permisos registrados en esquema", -36),
    ]
    add_parallel_connectors(diag_cu4, conns_cu4)
    
    bmp_cu4 = os.path.join(out_dir, "Diagrama de Comunicación - CU4 Roles y Permisos.bmp")
    png_cu4 = os.path.join(out_dir, "Diagrama de Comunicación - CU4 Roles y Permisos.png")
    project.PutDiagramImageToFile(diag_cu4.DiagramGUID, bmp_cu4, 1)
    try:
        Image.open(bmp_cu4).save(png_cu4)
    except Exception:
        pass
    print("CU4 completado.")

    # Guardar cambios en el repositorio
    comm_root_pkg.Packages.Refresh()
    sprint0_pkg.Packages.Refresh()
    repo.RefreshModelView(0)
    repo.CloseFile()
    repo.Exit()
    print("\n¡Todos los 6 diagramas de comunicación con flechas individuales fueron creados exitosamente en DIAGRAMAS.eapx!")

if __name__ == '__main__':
    crear_diagramas_comunicacion()
