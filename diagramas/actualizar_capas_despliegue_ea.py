import win32com.client
import sys

def update_diagrams():
    eapx_path = r'c:\Users\User\Documents\2-2026\SI2\proyecto_grupal\diagramas\DIAGRAMAS.eapx'
    
    print("Iniciando Enterprise Architect para actualizar diagramas de Capas y Despliegue...")
    ea = win32com.client.Dispatch('EA.App')
    repo = ea.Repository
    
    if not repo.OpenFile(eapx_path):
        print("Error: No se pudo abrir el archivo .eapx")
        return
        
    root_model = repo.Models.GetAt(0)
    
    # Buscar el paquete principal
    sprint0_pkg = None
    for pkg in root_model.Packages:
        if pkg.Name == "Sprint 0 - Arquitectura y Contexto":
            sprint0_pkg = pkg
            break
            
    if sprint0_pkg is None:
        print("Error: No se encontró el paquete principal.")
        repo.CloseFile()
        repo.Exit()
        return

    def add_diag_obj(diag, elem, left, top, right, bottom, zorder=0):
        diag_obj = diag.DiagramObjects.AddNew(f"l={left};r={right};t={top};b={bottom};", "")
        diag_obj.ElementID = elem.ElementID
        diag_obj.left = left
        diag_obj.top = top
        diag_obj.right = right
        diag_obj.bottom = bottom
        diag_obj.Sequence = zorder
        diag_obj.Update()
        return diag_obj

    def add_connector(source_elem, target_elem, conn_type, name="", stereotype=""):
        conn = source_elem.Connectors.AddNew(name, conn_type)
        conn.SupplierID = target_elem.ElementID
        if stereotype:
            conn.Stereotype = stereotype
        conn.Update()
        source_elem.Connectors.Refresh()
        return conn

    # =========================================================================
    # ACTUALIZAR 5. ARQUITECTURA DE 3 CAPAS
    # =========================================================================
    print("\n--- Actualizando 5. Diagrama de Arquitectura de 3 Capas ---")
    # Eliminar paquete previo si existe
    for i in range(sprint0_pkg.Packages.Count - 1, -1, -1):
        p = sprint0_pkg.Packages.GetAt(i)
        if p.Name == "5. Arquitectura 3 Capas":
            sprint0_pkg.Packages.Delete(i)
            print("Subpaquete previo de arquitectura eliminado.")
            
    sprint0_pkg.Packages.Refresh()
    arq_pkg = sprint0_pkg.Packages.AddNew("5. Arquitectura 3 Capas", "Package")
    arq_pkg.Update()
    
    arq_diag = arq_pkg.Diagrams.AddNew("Diagrama de Arquitectura de 3 Capas", "Component")
    arq_diag.Update()
    
    # Capas (Boundaries / Packages visuales)
    capa1 = arq_pkg.Elements.AddNew("Capa 1: Presentación (Frontend)", "Boundary")
    capa1.Stereotype = "layer"
    capa1.Notes = "Contiene los clientes de usuario web y móvil desarrollados en Angular 17 y Flutter 3."
    capa1.Update()
    
    capa2 = arq_pkg.Elements.AddNew("Capa 2: Lógica de Negocio (Backend REST)", "Boundary")
    capa2.Stereotype = "layer"
    capa2.Notes = "Contiene la API REST en Django, middlewares de seguridad, servicios de negocio y ORM."
    capa2.Update()
    
    capa3 = arq_pkg.Elements.AddNew("Capa 3: Datos (PostgreSQL 16 Multi-Tenant)", "Boundary")
    capa3.Stereotype = "layer"
    capa3.Notes = "Contiene la base de datos relacional con esquema compartido public y esquemas aislados por tenant."
    capa3.Update()
    
    # Componentes de Capa 1
    c1_ang = arq_pkg.Elements.AddNew("Single Page Application (SPA)\n[Angular 17 / TypeScript]", "Component")
    c1_ang.Notes = "Módulos: Autenticación, Gestión de Usuarios/Roles, Configuración Institucional, Interceptor JWT."
    c1_ang.Update()
    
    c1_flt = arq_pkg.Elements.AddNew("App Móvil Nativa\n[Flutter 3.x / Dart]", "Component")
    c1_flt.Notes = "Módulos: Login, Registro, Almacenamiento seguro de tokens JWT, Consumo API REST."
    c1_flt.Update()
    
    # Componentes de Capa 2
    c2_api = arq_pkg.Elements.AddNew("API Gateway & Endpoints REST\n[Django REST Framework]", "Component")
    c2_api.Notes = "Rutas: /api/auth/, /api/tenants/, /api/users/, /api/roles/."
    c2_api.Update()
    
    c2_mid = arq_pkg.Elements.AddNew("Capa Middleware & Seguridad\n[TenantMiddleware / SimpleJWT / RBAC]", "Component")
    c2_mid.Notes = "Intercepta tenant_id por subdominio/header, valida JWT y verifica permisos RBAC."
    c2_mid.Update()
    
    c2_apps = arq_pkg.Elements.AddNew("Apps de Lógica de Negocio\n[Django Apps: core, accounts, tenants]", "Component")
    c2_apps.Notes = "Implementa la lógica del Sprint 0: autenticación, usuarios, centros y seguridad."
    c2_apps.Update()
    
    c2_orm = arq_pkg.Elements.AddNew("Django ORM & Router Multi-Tenant\n[django-tenants / psycopg2]", "Component")
    c2_orm.Notes = "Mapea modelos a esquemas PostgreSQL dinámicamente según el search_path."
    c2_orm.Update()
    
    # Componentes de Capa 3
    c3_db_pub = arq_pkg.Elements.AddNew("Esquema Public (Compartido)\n[tenants_tenant, tenants_dominio, superadmin]", "Component")
    c3_db_pub.Stereotype = "database schema"
    c3_db_pub.Update()
    
    c3_db_t1 = arq_pkg.Elements.AddNew("Esquema Tenant: Centro Esperanza\n[accounts_usuario, roles, permisos, core_centro]", "Component")
    c3_db_t1.Stereotype = "database schema"
    c3_db_t1.Update()
    
    c3_db_t2 = arq_pkg.Elements.AddNew("Esquema Tenant: Centro San Martín\n[accounts_usuario, roles, permisos, core_centro]", "Component")
    c3_db_t2.Stereotype = "database schema"
    c3_db_t2.Update()
    
    # Relaciones y Flujos de Datos entre Capas y Componentes
    add_connector(c1_ang, c2_api, "InformationFlow", "HTTPS :443 / JSON REST")
    add_connector(c1_flt, c2_api, "InformationFlow", "HTTPS :443 / JSON REST")
    
    add_connector(c2_api, c2_mid, "Dependency", "intercepta petición")
    add_connector(c2_mid, c2_apps, "Dependency", "activa contexto tenant")
    add_connector(c2_apps, c2_orm, "Dependency", "consulta ORM")
    
    add_connector(c2_orm, c3_db_pub, "Dependency", "search_path public")
    add_connector(c2_orm, c3_db_t1, "Dependency", "search_path tenant_esperanza")
    add_connector(c2_orm, c3_db_t2, "Dependency", "search_path tenant_sanmartin")
    
    # Posicionar Capas y Componentes en el diagrama
    # Capa 1 Boundary
    add_diag_obj(arq_diag, capa1, 40, -40, 780, -200, zorder=1)
    add_diag_obj(arq_diag, c1_ang, 70, -80, 390, -170, zorder=2)
    add_diag_obj(arq_diag, c1_flt, 430, -80, 750, -170, zorder=2)
    
    # Capa 2 Boundary
    add_diag_obj(arq_diag, capa2, 40, -240, 780, -680, zorder=1)
    add_diag_obj(arq_diag, c2_api, 180, -270, 640, -350, zorder=2)
    add_diag_obj(arq_diag, c2_mid, 180, -370, 640, -450, zorder=2)
    add_diag_obj(arq_diag, c2_apps, 180, -470, 640, -550, zorder=2)
    add_diag_obj(arq_diag, c2_orm, 180, -570, 640, -650, zorder=2)
    
    # Capa 3 Boundary
    add_diag_obj(arq_diag, capa3, 40, -720, 780, -890, zorder=1)
    add_diag_obj(arq_diag, c3_db_pub, 60, -760, 280, -860, zorder=2)
    add_diag_obj(arq_diag, c3_db_t1, 300, -760, 520, -860, zorder=2)
    add_diag_obj(arq_diag, c3_db_t2, 540, -760, 760, -860, zorder=2)
    
    arq_diag.Update()
    print("5. Diagrama de Arquitectura de 3 Capas actualizado con capas y componentes.")

    # =========================================================================
    # ACTUALIZAR 6. DIAGRAMA DE DESPLIEGUE
    # =========================================================================
    print("\n--- Actualizando 6. Diagrama de Despliegue ---")
    for i in range(sprint0_pkg.Packages.Count - 1, -1, -1):
        p = sprint0_pkg.Packages.GetAt(i)
        if p.Name == "6. Despliegue":
            sprint0_pkg.Packages.Delete(i)
            print("Subpaquete previo de despliegue eliminado.")
            
    sprint0_pkg.Packages.Refresh()
    dep_pkg = sprint0_pkg.Packages.AddNew("6. Despliegue", "Package")
    dep_pkg.Update()
    
    dep_diag = dep_pkg.Diagrams.AddNew("Diagrama de Despliegue", "Deployment")
    dep_diag.Update()
    
    # Nodos Físicos / Ambientes
    n_client_pc = dep_pkg.Elements.AddNew("Dispositivo del Usuario\n<<device>> (PC / Laptop)", "Node")
    n_client_pc.Update()
    
    art_browser = dep_pkg.Elements.AddNew("Navegador Web (Chrome / Firefox / Edge)\n<<executionEnvironment>>", "ExecutionEnvironment")
    art_browser.Update()
    
    art_ang_spa = dep_pkg.Elements.AddNew("Frontend Web SPA\n<<artifact>> [Angular 17 Build]", "Artifact")
    art_ang_spa.Update()
    
    n_client_mob = dep_pkg.Elements.AddNew("Dispositivo Móvil\n<<device>> (Smartphone)", "Node")
    n_client_mob.Update()
    
    art_mob_os = dep_pkg.Elements.AddNew("Sistema Operativo Móvil\n<<executionEnvironment>> [Android / iOS]", "ExecutionEnvironment")
    art_mob_os.Update()
    
    art_flt_app = dep_pkg.Elements.AddNew("App Móvil Compilada\n<<artifact>> [Flutter APK / IPA]", "Artifact")
    art_flt_app.Update()
    
    # Servidor Cloud
    n_server_cloud = dep_pkg.Elements.AddNew("Servidor Cloud de Producción\n<<executionEnvironment>> [Linux Ubuntu 22.04 LTS]", "Node")
    n_server_cloud.Update()
    
    n_nginx = dep_pkg.Elements.AddNew("Servidor Web & Proxy Inverso\n<<executionEnvironment>> [Nginx 1.24]", "ExecutionEnvironment")
    n_nginx.Notes = "Terminación SSL, Balanceo, Servir estáticos Angular, Rate Limiting."
    n_nginx.Update()
    
    n_gunicorn = dep_pkg.Elements.AddNew("Servidor de Aplicación WSGI\n<<executionEnvironment>> [Gunicorn WSGI]", "ExecutionEnvironment")
    n_gunicorn.Notes = "Gestor de procesos WSGI para Django application."
    n_gunicorn.Update()
    
    art_backend = dep_pkg.Elements.AddNew("Backend REST Application\n<<artifact>> [Django 5.x + DRF + Python 3.12]", "Artifact")
    art_backend.Update()
    
    n_postgres = dep_pkg.Elements.AddNew("Servidor de Base de Datos\n<<database>> [PostgreSQL 16 SGBD]", "ExecutionEnvironment")
    n_postgres.Notes = "Motor relacional con esquemas Multi-Tenant: public + tenant_schemas."
    n_postgres.Update()
    
    # Conexiones de red y comunicación
    add_connector(n_client_pc, n_server_cloud, "CommunicationPath", "HTTPS :443 (TLS v1.3)")
    add_connector(n_client_mob, n_server_cloud, "CommunicationPath", "HTTPS :443 (TLS v1.3)")
    add_connector(n_nginx, n_gunicorn, "CommunicationPath", "Unix Socket / HTTP :8000")
    add_connector(n_gunicorn, n_postgres, "CommunicationPath", "TCP/IP :5432 (psycopg2)")
    
    # Layout del diagrama de Despliegue con anidación visual
    # Dispositivo PC
    add_diag_obj(dep_diag, n_client_pc, 40, -40, 360, -280, zorder=1)
    add_diag_obj(dep_diag, art_browser, 65, -85, 335, -170, zorder=2)
    add_diag_obj(dep_diag, art_ang_spa, 90, -185, 310, -255, zorder=3)
    
    # Dispositivo Móvil
    add_diag_obj(dep_diag, n_client_mob, 420, -40, 740, -280, zorder=1)
    add_diag_obj(dep_diag, art_mob_os, 445, -85, 715, -170, zorder=2)
    add_diag_obj(dep_diag, art_flt_app, 470, -185, 690, -255, zorder=3)
    
    # Servidor Cloud
    add_diag_obj(dep_diag, n_server_cloud, 40, -330, 740, -850, zorder=1)
    add_diag_obj(dep_diag, n_nginx, 80, -380, 700, -480, zorder=2)
    add_diag_obj(dep_diag, n_gunicorn, 80, -510, 700, -640, zorder=2)
    add_diag_obj(dep_diag, art_backend, 110, -560, 670, -625, zorder=3)
    add_diag_obj(dep_diag, n_postgres, 80, -670, 700, -810, zorder=2)
    
    dep_diag.Update()
    print("6. Diagrama de Despliegue actualizado con nodos, entornos y componentes anidados.")
    
    # Refrescar y guardar
    sprint0_pkg.Packages.Refresh()
    repo.RefreshModelView(0)
    
    repo.CloseFile()
    repo.Exit()
    print("\n¡Ambos diagramas fueron actualizados y enriquecidos con éxito en DIAGRAMAS.eapx!")

if __name__ == '__main__':
    update_diagrams()
