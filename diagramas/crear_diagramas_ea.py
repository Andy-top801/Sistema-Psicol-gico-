import win32com.client
import sys
import os

def create_diagrams():
    eapx_path = r'c:\Users\User\Documents\2-2026\SI2\proyecto_grupal\diagramas\DIAGRAMAS.eapx'
    
    print("Iniciando Enterprise Architect...")
    ea = win32com.client.Dispatch('EA.App')
    repo = ea.Repository
    
    if not repo.OpenFile(eapx_path):
        print("Error: No se pudo abrir el archivo .eapx")
        return
        
    print("Archivo .eapx abierto exitosamente.")
    
    # Obtener el modelo raíz
    root_model = repo.Models.GetAt(0)
    print(f"Modelo raíz: {root_model.Name}")
    
    # Limpiar si ya existía para regenerar limpiamente
    for i in range(root_model.Packages.Count - 1, -1, -1):
        pkg = root_model.Packages.GetAt(i)
        if pkg.Name == "Sprint 0 - Arquitectura y Contexto":
            root_model.Packages.Delete(i)
            print("Paquete previo eliminado para regeneración limpia.")
            
    root_model.Packages.Refresh()
    sprint0_pkg = root_model.Packages.AddNew("Sprint 0 - Arquitectura y Contexto", "Package")
    sprint0_pkg.Update()
    root_model.Packages.Refresh()
    print("Paquete 'Sprint 0 - Arquitectura y Contexto' inicializado.")
        
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

    # Helper function to create connector
    def add_connector(source_elem, target_elem, conn_type, name="", stereotype=""):
        conn = source_elem.Connectors.AddNew(name, conn_type)
        conn.SupplierID = target_elem.ElementID
        if stereotype:
            conn.Stereotype = stereotype
        conn.Update()
        source_elem.Connectors.Refresh()
        return conn

    # =========================================================================
    # 1. DIAGRAMA DE CASOS DE USO DEL SPRINT 0
    # =========================================================================
    print("Creando 1. Diagrama de Casos de Uso...")
    cu_pkg = sprint0_pkg.Packages.AddNew("1. Casos de Uso - Sprint 0", "Package")
    cu_pkg.Update()
    
    cu_diag = cu_pkg.Diagrams.AddNew("Diagrama de Casos de Uso - Sprint 0", "Use Case")
    cu_diag.Update()
    
    # Actores
    act_superadmin = cu_pkg.Elements.AddNew("SuperAdministrador", "Actor")
    act_superadmin.Update()
    
    act_admin = cu_pkg.Elements.AddNew("Administrador del Centro", "Actor")
    act_admin.Update()
    
    act_user = cu_pkg.Elements.AddNew("Usuario General (Psicólogo / Recepcionista / Paciente)", "Actor")
    act_user.Update()
    
    # Casos de Uso
    cu1 = cu_pkg.Elements.AddNew("CU1: Gestionar centros psicológicos y configuración Multi-Tenant", "UseCase")
    cu1.Update()
    
    cu2 = cu_pkg.Elements.AddNew("CU2: Iniciar sesión y autenticar usuario", "UseCase")
    cu2.Update()
    
    cu3 = cu_pkg.Elements.AddNew("CU3: Gestionar usuarios del centro", "UseCase")
    cu3.Update()
    
    cu4 = cu_pkg.Elements.AddNew("CU4: Asignar roles y permisos (RBAC)", "UseCase")
    cu4.Update()
    
    cu27 = cu_pkg.Elements.AddNew("CU27: Recuperar contraseña y credenciales", "UseCase")
    cu27.Update()
    
    cu_logout = cu_pkg.Elements.AddNew("Cerrar sesión segura (JWT)", "UseCase")
    cu_logout.Update()
    
    cu_val = cu_pkg.Elements.AddNew("Validar Token JWT y Tenant", "UseCase")
    cu_val.Update()
    
    # Relaciones
    add_connector(act_superadmin, cu1, "Association")
    add_connector(act_superadmin, cu2, "Association")
    
    add_connector(act_admin, cu3, "Association")
    add_connector(act_admin, cu4, "Association")
    add_connector(act_admin, cu2, "Association")
    
    add_connector(act_user, cu2, "Association")
    add_connector(act_user, cu27, "Association")
    add_connector(act_user, cu_logout, "Association")
    
    add_connector(cu2, cu_val, "UseCase", "", "include")
    add_connector(cu3, cu_val, "UseCase", "", "include")
    add_connector(cu4, cu_val, "UseCase", "", "include")
    
    # Layout en el diagrama
    add_diag_obj(cu_diag, act_superadmin, 60, -80, 160, -180)
    add_diag_obj(cu_diag, act_admin, 60, -240, 160, -340)
    add_diag_obj(cu_diag, act_user, 60, -420, 160, -520)
    
    add_diag_obj(cu_diag, cu1, 300, -60, 520, -130)
    add_diag_obj(cu_diag, cu2, 300, -160, 520, -230)
    add_diag_obj(cu_diag, cu3, 300, -260, 520, -330)
    add_diag_obj(cu_diag, cu4, 300, -360, 520, -430)
    add_diag_obj(cu_diag, cu27, 300, -460, 520, -530)
    add_diag_obj(cu_diag, cu_logout, 300, -560, 520, -630)
    add_diag_obj(cu_diag, cu_val, 620, -260, 840, -330)
    
    cu_diag.Update()
    print("1. Diagrama de Casos de Uso creado.")

    # =========================================================================
    # 2. DIAGRAMA DE CLASES DEL SPRINT 0
    # =========================================================================
    print("Creando 2. Diagrama de Clases...")
    cl_pkg = sprint0_pkg.Packages.AddNew("2. Clases - Sprint 0", "Package")
    cl_pkg.Update()
    
    cl_diag = cl_pkg.Diagrams.AddNew("Diagrama de Clases - Sprint 0", "Class")
    cl_diag.Update()
    
    # Helper to add attributes and methods
    def add_attrs(elem, attrs):
        for name, typ in attrs:
            att = elem.Attributes.AddNew(name, typ)
            att.Update()
        elem.Attributes.Refresh()
        
    def add_methods(elem, methods):
        for name, ret in methods:
            m = elem.Methods.AddNew(name, ret)
            m.Update()
        elem.Methods.Refresh()
        
    # Clases
    c_tenant = cl_pkg.Elements.AddNew("Tenant", "Class")
    add_attrs(c_tenant, [("id", "UUID"), ("nombre", "String"), ("slug", "String"), 
                         ("schema_name", "String"), ("plan", "String"), ("activo", "Boolean"), 
                         ("fecha_creacion", "DateTime")])
    add_methods(c_tenant, [("crear_esquema", "void"), ("suspender", "void")])
    c_tenant.Update()
    
    c_dominio = cl_pkg.Elements.AddNew("Dominio", "Class")
    add_attrs(c_dominio, [("id", "Integer"), ("dominio", "String"), ("es_primario", "Boolean")])
    c_dominio.Update()
    
    c_superadmin = cl_pkg.Elements.AddNew("SuperAdmin", "Class")
    add_attrs(c_superadmin, [("id", "Integer"), ("email", "String"), ("password_hash", "String"), 
                             ("nombre", "String"), ("activo", "Boolean")])
    add_methods(c_superadmin, [("gestionar_tenants", "void")])
    c_superadmin.Update()
    
    c_centro = cl_pkg.Elements.AddNew("Centro", "Class")
    add_attrs(c_centro, [("id", "UUID"), ("nombre", "String"), ("direccion", "String"), 
                        ("telefono", "String"), ("email", "String"), ("logo", "String"), 
                        ("horarios_atencion", "JSON")])
    add_methods(c_centro, [("actualizar_config", "void")])
    c_centro.Update()
    
    c_usuario = cl_pkg.Elements.AddNew("Usuario", "Class")
    add_attrs(c_usuario, [("id", "UUID"), ("email", "String"), ("password_hash", "String"), 
                          ("nombre", "String"), ("apellido", "String"), ("telefono", "String"), 
                          ("activo", "Boolean"), ("fecha_creacion", "DateTime")])
    add_methods(c_usuario, [("autenticar", "Boolean"), ("cerrar_sesion", "void")])
    c_usuario.Update()
    
    c_rol = cl_pkg.Elements.AddNew("Rol", "Class")
    add_attrs(c_rol, [("id", "Integer"), ("nombre", "String"), ("descripcion", "String")])
    c_rol.Update()
    
    c_permiso = cl_pkg.Elements.AddNew("Permiso", "Class")
    add_attrs(c_permiso, [("id", "Integer"), ("nombre", "String"), ("codigo", "String"), ("modulo", "String")])
    c_permiso.Update()
    
    c_token_acc = cl_pkg.Elements.AddNew("TokenAcceso", "Class")
    add_attrs(c_token_acc, [("id", "UUID"), ("token_jwt", "String"), ("fecha_expiracion", "DateTime")])
    add_methods(c_token_acc, [("es_valido", "Boolean")])
    c_token_acc.Update()
    
    c_token_rec = cl_pkg.Elements.AddNew("TokenRecuperacion", "Class")
    add_attrs(c_token_rec, [("id", "UUID"), ("token", "String"), ("fecha_expiracion", "DateTime"), ("usado", "Boolean")])
    add_methods(c_token_rec, [("validar_token", "Boolean")])
    c_token_rec.Update()
    
    # Conectores de clases
    add_connector(c_tenant, c_dominio, "Aggregation", "posee")
    add_connector(c_tenant, c_centro, "Association", "define")
    add_connector(c_centro, c_usuario, "Aggregation", "contiene")
    add_connector(c_usuario, c_rol, "Association", "asignado")
    add_connector(c_rol, c_permiso, "Aggregation", "contiene")
    add_connector(c_usuario, c_token_acc, "Aggregation", "genera")
    add_connector(c_usuario, c_token_rec, "Aggregation", "solicita")
    add_connector(c_superadmin, c_tenant, "Dependency", "administra")
    
    # Posicionar en diagrama
    add_diag_obj(cl_diag, c_superadmin, 60, -60, 240, -180)
    add_diag_obj(cl_diag, c_tenant, 320, -60, 500, -220)
    add_diag_obj(cl_diag, c_dominio, 580, -60, 740, -160)
    
    add_diag_obj(cl_diag, c_centro, 320, -280, 500, -440)
    add_diag_obj(cl_diag, c_usuario, 320, -500, 520, -680)
    
    add_diag_obj(cl_diag, c_rol, 600, -500, 780, -620)
    add_diag_obj(cl_diag, c_permiso, 860, -500, 1020, -620)
    
    add_diag_obj(cl_diag, c_token_acc, 60, -500, 240, -620)
    add_diag_obj(cl_diag, c_token_rec, 60, -680, 240, -800)
    
    cl_diag.Update()
    print("2. Diagrama de Clases creado.")

    # =========================================================================
    # 3. DIAGRAMA DE ACTIVIDAD: AUTENTICACIÓN JWT
    # =========================================================================
    print("Creando 3. Diagrama de Actividad (Autenticación)...")
    act1_pkg = sprint0_pkg.Packages.AddNew("3. Actividad - Autenticación", "Package")
    act1_pkg.Update()
    
    act1_diag = act1_pkg.Diagrams.AddNew("Diagrama de Actividad - Autenticación JWT", "Activity")
    act1_diag.Update()
    
    init1 = act1_pkg.Elements.AddNew("", "StateNode")
    init1.Subtype = 100 # Initial Node
    init1.Update()
    
    a1_1 = act1_pkg.Elements.AddNew("Acceder a pantalla de inicio de sesión", "Activity")
    a1_1.Update()
    
    a1_2 = act1_pkg.Elements.AddNew("Ingresar correo, contraseña y seleccionar centro", "Activity")
    a1_2.Update()
    
    a1_3 = act1_pkg.Elements.AddNew("Validar formato y enviar POST /api/auth/login/", "Activity")
    a1_3.Update()
    
    d1_1 = act1_pkg.Elements.AddNew("¿Credenciales correctas?", "Decision")
    d1_1.Update()
    
    d1_2 = act1_pkg.Elements.AddNew("¿Cuenta activa?", "Decision")
    d1_2.Update()
    
    d1_3 = act1_pkg.Elements.AddNew("¿Centro activo?", "Decision")
    d1_3.Update()
    
    a1_4 = act1_pkg.Elements.AddNew("Identificar esquema PostgreSQL del tenant", "Activity")
    a1_4.Update()
    
    a1_5 = act1_pkg.Elements.AddNew("Generar Token JWT con claims (usuario, rol, tenant)", "Activity")
    a1_5.Update()
    
    a1_6 = act1_pkg.Elements.AddNew("Retornar HTTP 200 OK con JWT Access & Refresh Token", "Activity")
    a1_6.Update()
    
    a1_7 = act1_pkg.Elements.AddNew("Guardar token seguro y redirigir a Dashboard", "Activity")
    a1_7.Update()
    
    e1_1 = act1_pkg.Elements.AddNew("Error 401: Credenciales inválidas", "Activity")
    e1_1.Update()
    
    e1_2 = act1_pkg.Elements.AddNew("Error 403: Cuenta desactivada", "Activity")
    e1_2.Update()
    
    e1_3 = act1_pkg.Elements.AddNew("Error 403: Centro suspendido", "Activity")
    e1_3.Update()
    
    final1 = act1_pkg.Elements.AddNew("", "StateNode")
    final1.Subtype = 101 # Activity Final
    final1.Update()
    
    # Flujos
    add_connector(init1, a1_1, "ControlFlow")
    add_connector(a1_1, a1_2, "ControlFlow")
    add_connector(a1_2, a1_3, "ControlFlow")
    add_connector(a1_3, d1_1, "ControlFlow")
    
    add_connector(d1_1, d1_2, "ControlFlow", "Sí")
    add_connector(d1_1, e1_1, "ControlFlow", "No")
    
    add_connector(d1_2, d1_3, "ControlFlow", "Sí")
    add_connector(d1_2, e1_2, "ControlFlow", "No")
    
    add_connector(d1_3, a1_4, "ControlFlow", "Sí")
    add_connector(d1_3, e1_3, "ControlFlow", "No")
    
    add_connector(a1_4, a1_5, "ControlFlow")
    add_connector(a1_5, a1_6, "ControlFlow")
    add_connector(a1_6, a1_7, "ControlFlow")
    add_connector(a1_7, final1, "ControlFlow")
    
    add_connector(e1_1, final1, "ControlFlow")
    add_connector(e1_2, final1, "ControlFlow")
    add_connector(e1_3, final1, "ControlFlow")
    
    # Layout
    add_diag_obj(act1_diag, init1, 380, -40, 400, -60)
    add_diag_obj(act1_diag, a1_1, 280, -90, 500, -140)
    add_diag_obj(act1_diag, a1_2, 260, -170, 520, -220)
    add_diag_obj(act1_diag, a1_3, 260, -250, 520, -300)
    add_diag_obj(act1_diag, d1_1, 340, -340, 440, -390)
    
    add_diag_obj(act1_diag, d1_2, 340, -440, 440, -490)
    add_diag_obj(act1_diag, d1_3, 340, -540, 440, -590)
    
    add_diag_obj(act1_diag, a1_4, 270, -640, 510, -690)
    add_diag_obj(act1_diag, a1_5, 250, -720, 530, -770)
    add_diag_obj(act1_diag, a1_6, 250, -800, 530, -850)
    add_diag_obj(act1_diag, a1_7, 260, -880, 520, -930)
    add_diag_obj(act1_diag, final1, 380, -970, 400, -990)
    
    add_diag_obj(act1_diag, e1_1, 600, -340, 800, -390)
    add_diag_obj(act1_diag, e1_2, 600, -440, 800, -490)
    add_diag_obj(act1_diag, e1_3, 600, -540, 800, -590)
    
    act1_diag.Update()
    print("3. Diagrama de Actividad (Autenticación) creado.")

    # =========================================================================
    # 4. DIAGRAMA DE ACTIVIDAD: AISLAMIENTO MULTI-TENANT
    # =========================================================================
    print("Creando 4. Diagrama de Actividad (Multi-Tenant)...")
    act2_pkg = sprint0_pkg.Packages.AddNew("4. Actividad - Multi-Tenant", "Package")
    act2_pkg.Update()
    
    act2_diag = act2_pkg.Diagrams.AddNew("Diagrama de Actividad - Aislamiento Multi-Tenant", "Activity")
    act2_diag.Update()
    
    init2 = act2_pkg.Elements.AddNew("", "StateNode")
    init2.Subtype = 100
    init2.Update()
    
    b2_1 = act2_pkg.Elements.AddNew("Cliente realiza solicitud HTTP (GET /api/users/)", "Activity")
    b2_1.Update()
    
    b2_2 = act2_pkg.Elements.AddNew("TenantMiddleware intercepta la solicitud", "Activity")
    b2_2.Update()
    
    b2_3 = act2_pkg.Elements.AddNew("Extraer subdominio de cabecera Host o Header", "Activity")
    b2_3.Update()
    
    d2_1 = act2_pkg.Elements.AddNew("¿Tenant existe?", "Decision")
    d2_1.Update()
    
    d2_2 = act2_pkg.Elements.AddNew("¿Tenant activo?", "Decision")
    d2_2.Update()
    
    b2_4 = act2_pkg.Elements.AddNew("Configurar search_path al esquema del tenant", "Activity")
    b2_4.Update()
    
    b2_5 = act2_pkg.Elements.AddNew("Verificar token JWT y permisos de usuario", "Activity")
    b2_5.Update()
    
    d2_3 = act2_pkg.Elements.AddNew("¿Permiso concedido?", "Decision")
    d2_3.Update()
    
    b2_6 = act2_pkg.Elements.AddNew("Ejecutar consulta ORM en esquema PostgreSQL aislado", "Activity")
    b2_6.Update()
    
    b2_7 = act2_pkg.Elements.AddNew("Serializar y retornar respuesta HTTP 200 OK", "Activity")
    b2_7.Update()
    
    eb2_1 = act2_pkg.Elements.AddNew("Error 404: Subdominio no encontrado", "Activity")
    eb2_1.Update()
    
    eb2_2 = act2_pkg.Elements.AddNew("Error 403: Tenant suspendido", "Activity")
    eb2_2.Update()
    
    eb2_3 = act2_pkg.Elements.AddNew("Error 403: Permiso denegado", "Activity")
    eb2_3.Update()
    
    final2 = act2_pkg.Elements.AddNew("", "StateNode")
    final2.Subtype = 101
    final2.Update()
    
    add_connector(init2, b2_1, "ControlFlow")
    add_connector(b2_1, b2_2, "ControlFlow")
    add_connector(b2_2, b2_3, "ControlFlow")
    add_connector(b2_3, d2_1, "ControlFlow")
    
    add_connector(d2_1, d2_2, "ControlFlow", "Sí")
    add_connector(d2_1, eb2_1, "ControlFlow", "No")
    
    add_connector(d2_2, b2_4, "ControlFlow", "Sí")
    add_connector(d2_2, eb2_2, "ControlFlow", "No")
    
    add_connector(b2_4, b2_5, "ControlFlow")
    add_connector(b2_5, d2_3, "ControlFlow")
    
    add_connector(d2_3, b2_6, "ControlFlow", "Sí")
    add_connector(d2_3, eb2_3, "ControlFlow", "No")
    
    add_connector(b2_6, b2_7, "ControlFlow")
    add_connector(b2_7, final2, "ControlFlow")
    
    add_connector(eb2_1, final2, "ControlFlow")
    add_connector(eb2_2, final2, "ControlFlow")
    add_connector(eb2_3, final2, "ControlFlow")
    
    # Layout
    add_diag_obj(act2_diag, init2, 380, -40, 400, -60)
    add_diag_obj(act2_diag, b2_1, 260, -90, 520, -140)
    add_diag_obj(act2_diag, b2_2, 260, -170, 520, -220)
    add_diag_obj(act2_diag, b2_3, 250, -250, 530, -300)
    add_diag_obj(act2_diag, d2_1, 340, -340, 440, -390)
    
    add_diag_obj(act2_diag, d2_2, 340, -440, 440, -490)
    add_diag_obj(act2_diag, b2_4, 250, -530, 530, -580)
    add_diag_obj(act2_diag, b2_5, 250, -610, 530, -660)
    add_diag_obj(act2_diag, d2_3, 340, -700, 440, -750)
    
    add_diag_obj(act2_diag, b2_6, 240, -790, 540, -840)
    add_diag_obj(act2_diag, b2_7, 250, -870, 530, -920)
    add_diag_obj(act2_diag, final2, 380, -960, 400, -980)
    
    add_diag_obj(act2_diag, eb2_1, 600, -340, 820, -390)
    add_diag_obj(act2_diag, eb2_2, 600, -440, 820, -490)
    add_diag_obj(act2_diag, eb2_3, 600, -700, 820, -750)
    
    act2_diag.Update()
    print("4. Diagrama de Actividad (Multi-Tenant) creado.")

    # =========================================================================
    # 5. DIAGRAMA DE ARQUITECTURA DE 3 CAPAS
    # =========================================================================
    print("Creando 5. Diagrama de Arquitectura de 3 Capas...")
    arq_pkg = sprint0_pkg.Packages.AddNew("5. Arquitectura 3 Capas", "Package")
    arq_pkg.Update()
    
    arq_diag = arq_pkg.Diagrams.AddNew("Diagrama de Arquitectura de 3 Capas", "Component")
    arq_diag.Update()
    
    # Capa 1 Presentación
    comp_web = arq_pkg.Elements.AddNew("Angular 17 Web SPA (Módulo Auth, Usuarios, Tenant)", "Component")
    comp_web.Update()
    
    comp_mob = arq_pkg.Elements.AddNew("Flutter 3 App Móvil (Login, Sesión Segura)", "Component")
    comp_mob.Update()
    
    # Capa 2 Lógica
    comp_api = arq_pkg.Elements.AddNew("API Gateway & REST Endpoints (Django REST Framework)", "Component")
    comp_api.Update()
    
    comp_mid = arq_pkg.Elements.AddNew("Middleware & Seguridad (TenantMiddleware, JWT, RBAC)", "Component")
    comp_mid.Update()
    
    comp_apps = arq_pkg.Elements.AddNew("Lógica de Negocio (Apps: core, accounts, tenants)", "Component")
    comp_apps.Update()
    
    comp_orm = arq_pkg.Elements.AddNew("Django ORM (Migraciones y Conexión Multi-Tenant)", "Component")
    comp_orm.Update()
    
    # Capa 3 Datos
    comp_db_pub = arq_pkg.Elements.AddNew("PostgreSQL 16 - Esquema Public (Tenants, Dominios, SuperAdmin)", "Component")
    comp_db_pub.Update()
    
    comp_db_ten = arq_pkg.Elements.AddNew("PostgreSQL 16 - Esquemas Tenants (Usuarios, Roles, Permisos por Centro)", "Component")
    comp_db_ten.Update()
    
    # Conexiones
    add_connector(comp_web, comp_api, "InformationFlow", "HTTPS / JSON")
    add_connector(comp_mob, comp_api, "InformationFlow", "HTTPS / JSON")
    add_connector(comp_api, comp_mid, "Dependency", "intercepta")
    add_connector(comp_mid, comp_apps, "Dependency", "ejecuta")
    add_connector(comp_apps, comp_orm, "Dependency", "consulta")
    add_connector(comp_orm, comp_db_pub, "Dependency", "search_path public")
    add_connector(comp_orm, comp_db_ten, "Dependency", "search_path tenant")
    
    # Layout
    add_diag_obj(arq_diag, comp_web, 60, -80, 320, -180)
    add_diag_obj(arq_diag, comp_mob, 360, -80, 620, -180)
    
    add_diag_obj(arq_diag, comp_api, 180, -250, 500, -340)
    add_diag_obj(arq_diag, comp_mid, 180, -380, 500, -470)
    add_diag_obj(arq_diag, comp_apps, 180, -510, 500, -600)
    add_diag_obj(arq_diag, comp_orm, 180, -640, 500, -730)
    
    add_diag_obj(arq_diag, comp_db_pub, 60, -810, 320, -920)
    add_diag_obj(arq_diag, comp_db_ten, 360, -810, 640, -920)
    
    arq_diag.Update()
    print("5. Diagrama de Arquitectura de 3 Capas creado.")

    # =========================================================================
    # 6. DIAGRAMA DE DESPLIEGUE
    # =========================================================================
    print("Creando 6. Diagrama de Despliegue...")
    dep_pkg = sprint0_pkg.Packages.AddNew("6. Despliegue", "Package")
    dep_pkg.Update()
    
    dep_diag = dep_pkg.Diagrams.AddNew("Diagrama de Despliegue", "Deployment")
    dep_diag.Update()
    
    node_pc = dep_pkg.Elements.AddNew("Dispositivo del Usuario (PC / Laptop)", "Node")
    node_pc.Update()
    
    node_mob = dep_pkg.Elements.AddNew("Dispositivo Móvil (Smartphone Android / iOS)", "Node")
    node_mob.Update()
    
    node_server = dep_pkg.Elements.AddNew("Servidor Cloud (Linux Ubuntu 22.04 LTS)", "Node")
    node_server.Update()
    
    node_nginx = dep_pkg.Elements.AddNew("Servidor Web & Proxy Inverso (Nginx 1.24)", "Node")
    node_nginx.Update()
    
    node_app = dep_pkg.Elements.AddNew("Servidor de Aplicación WSGI (Gunicorn + Django 5.x)", "Node")
    node_app.Update()
    
    node_pg = dep_pkg.Elements.AddNew("Servidor de Base de Datos (PostgreSQL 16 SGBD)", "Node")
    node_pg.Update()
    
    add_connector(node_pc, node_nginx, "CommunicationPath", "HTTPS :443")
    add_connector(node_mob, node_nginx, "CommunicationPath", "HTTPS :443")
    add_connector(node_nginx, node_app, "CommunicationPath", "Unix Socket")
    add_connector(node_app, node_pg, "CommunicationPath", "TCP/IP :5432")
    
    # Layout
    add_diag_obj(dep_diag, node_pc, 60, -80, 300, -220)
    add_diag_obj(dep_diag, node_mob, 360, -80, 600, -220)
    
    add_diag_obj(dep_diag, node_nginx, 210, -280, 450, -400)
    add_diag_obj(dep_diag, node_app, 210, -460, 450, -580)
    add_diag_obj(dep_diag, node_pg, 210, -640, 450, -760)
    
    dep_diag.Update()
    print("6. Diagrama de Despliegue creado.")
    
    # Guardar cambios y refrescar
    sprint0_pkg.Packages.Refresh()
    repo.RefreshModelView(0)
    
    repo.CloseFile()
    repo.Exit()
    print("\n¡Todos los 6 diagramas fueron creados exitosamente en DIAGRAMAS.eapx!")

if __name__ == '__main__':
    create_diagrams()
