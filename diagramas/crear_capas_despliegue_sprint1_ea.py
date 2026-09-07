import win32com.client
import sys
import os
from PIL import Image

def add_capas_and_despliegue_sprint1():
    eapx_path = r'c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\diagramas\DIAGRAMAS.eapx'
    out_dir = r'c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\diagramas'
    
    print("Iniciando Enterprise Architect para agregar Arquitectura de 3 Capas y Despliegue en Sprint 1...")
    ea = win32com.client.Dispatch('EA.App')
    repo = ea.Repository
    
    if not repo.OpenFile(eapx_path):
        print(f"Error: No se pudo abrir el archivo {eapx_path}")
        return False
        
    print("Archivo DIAGRAMAS.eapx abierto exitosamente.")
    root_model = repo.Models.GetAt(0)
    
    # Buscar el paquete 'sprint 1'
    sprint1_pkg = None
    for pkg in root_model.Packages:
        if pkg.Name.lower() == "sprint 1":
            sprint1_pkg = pkg
            break
            
    if sprint1_pkg is None:
        print("Error: No se encontró la carpeta 'sprint 1'.")
        repo.CloseFile()
        repo.Exit()
        return False
        
    print(f"Carpeta '{sprint1_pkg.Name}' encontrada.")

    # Helper function to add diagram object
    def add_diag_obj(diag, elem, left, top, right, bottom, zorder=0):
        diag_obj = diag.DiagramObjects.AddNew(f"l={left};r={right};t={top};b={bottom};", "")
        diag_obj.ElementID = elem.ElementID
        diag_obj.left = left
        diag_obj.top = top
        diag_obj.right = right
        diag_obj.bottom = bottom
        if zorder:
            diag_obj.Sequence = zorder
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
        target_elem.Connectors.Refresh()
        return conn

    project = repo.GetProjectInterface()

    # =========================================================================
    # 5. DIAGRAMA DE ARQUITECTURA DE 3 CAPAS - SPRINT 1 (SISTEMA ACUMULADO)
    # =========================================================================
    print("\n--- Creando 5. Arquitectura 3 Capas - Sprint 1 ---")
    # Limpiar si ya existía para regeneración limpia
    for i in range(sprint1_pkg.Packages.Count - 1, -1, -1):
        p = sprint1_pkg.Packages.GetAt(i)
        if "5. arquitectura" in p.Name.lower():
            sprint1_pkg.Packages.Delete(i)
            print("Subpaquete previo de arquitectura eliminado.")
            
    sprint1_pkg.Packages.Refresh()
    arq_pkg = sprint1_pkg.Packages.AddNew("5. Arquitectura 3 Capas - Sprint 1", "Package")
    arq_pkg.Update()
    
    arq_diag = arq_pkg.Diagrams.AddNew("Diagrama de Arquitectura de 3 Capas - Sprint 1", "Component")
    arq_diag.Update()
    
    # Capas (Boundaries con estereotipo Layer)
    capa1 = arq_pkg.Elements.AddNew("Capa 1: Presentación (Clientes Web y Móvil - Sistema Acumulado)", "Boundary")
    capa1.Stereotype = "layer"
    capa1.Notes = "Clientes Angular 17 y Flutter 3.x con Auth, RBAC, Citas, Pacientes, Calendario y Teleconsulta."
    capa1.Update()
    
    capa2 = arq_pkg.Elements.AddNew("Capa 2: Lógica de Negocio (Servicios Backend Django / DRF y WebRTC)", "Boundary")
    capa2.Stereotype = "layer"
    capa2.Notes = "Servicios REST en Django 5.x, validadores de disponibilidad, control de colisiones y servidor Jitsi Meet."
    capa2.Update()
    
    capa3 = arq_pkg.Elements.AddNew("Capa 3: Datos (PostgreSQL 16 Multi-Tenant Acumulado)", "Boundary")
    capa3.Stereotype = "layer"
    capa3.Notes = "PostgreSQL 16 con esquema public global y esquemas aislados por centro con tablas clínicas y de agenda."
    capa3.Update()
    
    # Componentes de Capa 1
    c1_ang = arq_pkg.Elements.AddNew("Cliente Web: SPA Angular 17\n[Auth, Roles, Centro, Psicólogos, Pacientes, Calendario Citas, Métricas, Jitsi WebRTC Wrapper]", "Component")
    c1_ang.Notes = "Componentes standalone, Reactive Forms, FullCalendar, Chart.js y Jitsi Meet API Wrapper."
    c1_ang.Update()
    
    c1_flt = arq_pkg.Elements.AddNew("Cliente Móvil: App Nativa Flutter 3.x\n[Login & Tenant, Perfil Paciente, Mis Citas & Reservar, Jitsi Native SDK, Secure Storage]", "Component")
    c1_flt.Notes = "Dart con arquitectura limpia, manejo de estado, almacenamiento seguro y Jitsi Meet nativo."
    c1_flt.Update()
    
    # Componentes de Capa 2
    c2_api = arq_pkg.Elements.AddNew("API Gateway & Endpoints REST Acumulados\n[/api/auth/, /api/accounts/, /api/tenants/, /api/clinica/, /api/agenda/, /api/core/]", "Component")
    c2_api.Update()
    
    c2_mid = arq_pkg.Elements.AddNew("Capa de Middleware\n[TenantMiddleware (django-tenants), JWTAuthentication, RolePermissionGuard]", "Component")
    c2_mid.Update()
    
    c2_serv = arq_pkg.Elements.AddNew("Servicios de Dominio\n[TenantIsolation, AvailabilityValidator, ConflictResolution, JitsiTokenGenerator, MetricsAggregator]", "Component")
    c2_serv.Update()
    
    c2_orm = arq_pkg.Elements.AddNew("Django ORM & Router Multi-Tenant\n[django-tenants / psycopg2]", "Component")
    c2_orm.Update()
    
    c2_jitsi = arq_pkg.Elements.AddNew("Cluster Videoconferencia WebRTC\n[Servidor Jitsi Meet: VideoBridge JVB + Prosody XMPP Server]", "Component")
    c2_jitsi.Notes = "Servidor WebRTC externo para gestión de salas seguras y streaming de audio/video en tiempo real."
    c2_jitsi.Update()
    
    # Componentes de Capa 3
    c3_db_pub = arq_pkg.Elements.AddNew("Esquema Public (Global - Consolidado Sprint 0)\n[tenants_tenant, tenants_dominio, accounts_superadmin]", "Component")
    c3_db_pub.Stereotype = "database schema"
    c3_db_pub.Update()
    
    c3_db_base = arq_pkg.Elements.AddNew("Esquema Tenant: Tablas Base (Consolidado Sprint 0)\n[core_centro, accounts_usuario, accounts_rol, accounts_permiso, accounts_rol_permiso, accounts_token_recuperacion]", "Component")
    c3_db_base.Stereotype = "database schema"
    c3_db_base.Update()
    
    c3_db_clin = arq_pkg.Elements.AddNew("Esquema Tenant: Tablas Clínicas & Agenda (Incremento Sprint 1)\n[clinica_especialidad, clinica_psicologo, clinica_disponibilidad, clinica_paciente, agenda_cita, agenda_teleconsulta, agenda_alerta]", "Component")
    c3_db_clin.Stereotype = "database schema"
    c3_db_clin.Update()
    
    # Conectores y Flujos de Datos entre Capas
    add_connector(c1_ang, c2_api, "InformationFlow", "HTTPS / JSON REST API")
    add_connector(c1_flt, c2_api, "InformationFlow", "HTTPS / JSON REST API")
    add_connector(c1_ang, c2_jitsi, "InformationFlow", "WebRTC Audio/Video Stream")
    add_connector(c1_flt, c2_jitsi, "InformationFlow", "WebRTC Native Media Stream")
    
    add_connector(c2_api, c2_mid, "Dependency", "intercepta")
    add_connector(c2_mid, c2_serv, "Dependency", "ejecuta reglas")
    add_connector(c2_serv, c2_orm, "Dependency", "persiste datos")
    
    add_connector(c2_orm, c3_db_pub, "Dependency", "search_path = public")
    add_connector(c2_orm, c3_db_base, "Dependency", "search_path = tenant_schema")
    add_connector(c2_orm, c3_db_clin, "Dependency", "search_path = tenant_schema")
    
    # Posicionamiento en diagrama
    # Capa 1 Boundary
    add_diag_obj(arq_diag, capa1, 40, -40, 980, -220, zorder=1)
    add_diag_obj(arq_diag, c1_ang, 70, -80, 500, -180, zorder=2)
    add_diag_obj(arq_diag, c1_flt, 530, -80, 950, -180, zorder=2)
    
    # Capa 2 Boundary
    add_diag_obj(arq_diag, capa2, 40, -260, 980, -740, zorder=1)
    add_diag_obj(arq_diag, c2_api, 70, -300, 600, -380, zorder=2)
    add_diag_obj(arq_diag, c2_mid, 70, -410, 600, -490, zorder=2)
    add_diag_obj(arq_diag, c2_serv, 70, -520, 600, -600, zorder=2)
    add_diag_obj(arq_diag, c2_orm, 70, -630, 600, -710, zorder=2)
    add_diag_obj(arq_diag, c2_jitsi, 640, -300, 950, -710, zorder=2)
    
    # Capa 3 Boundary
    add_diag_obj(arq_diag, capa3, 40, -780, 980, -980, zorder=1)
    add_diag_obj(arq_diag, c3_db_pub, 70, -820, 330, -940, zorder=2)
    add_diag_obj(arq_diag, c3_db_base, 360, -820, 650, -940, zorder=2)
    add_diag_obj(arq_diag, c3_db_clin, 680, -820, 950, -940, zorder=2)
    
    arq_diag.Update()
    
    # Exportar imagen de Arquitectura
    bmp_arq = os.path.join(out_dir, "Diagrama de Arquitectura de 3 Capas - Sprint 1.bmp")
    png_arq = os.path.join(out_dir, "Diagrama de Arquitectura de 3 Capas - Sprint 1.png")
    try:
        project.PutDiagramImageToFile(arq_diag.DiagramGUID, bmp_arq, 1)
        Image.open(bmp_arq).save(png_arq)
        print(f"Imagen exportada: {png_arq}")
    except Exception as e:
        print(f"Aviso al exportar imagen de arquitectura: {e}")
        
    print("5. Diagrama de Arquitectura de 3 Capas (Sprint 1) creado exitosamente.")

    # =========================================================================
    # 6. DIAGRAMA DE DESPLIEGUE - SPRINT 1
    # =========================================================================
    print("\n--- Creando 6. Despliegue - Sprint 1 ---")
    # Limpiar si ya existía para regeneración limpia
    for i in range(sprint1_pkg.Packages.Count - 1, -1, -1):
        p = sprint1_pkg.Packages.GetAt(i)
        if "6. despliegue" in p.Name.lower():
            sprint1_pkg.Packages.Delete(i)
            print("Subpaquete previo de despliegue eliminado.")
            
    sprint1_pkg.Packages.Refresh()
    dep_pkg = sprint1_pkg.Packages.AddNew("6. Despliegue - Sprint 1", "Package")
    dep_pkg.Update()
    
    dep_diag = dep_pkg.Diagrams.AddNew("Diagrama de Despliegue - Sprint 1", "Deployment")
    dep_diag.Update()
    
    # Nodos de Dispositivos Cliente
    n_pc = dep_pkg.Elements.AddNew("Estación de Trabajo (PC / Laptop)", "Node")
    n_pc.Stereotype = "device"
    n_pc.Update()
    
    env_browser = dep_pkg.Elements.AddNew("Navegador Web (Chrome / Edge / Firefox)", "ExecutionEnvironment")
    env_browser.Update()
    
    art_spa = dep_pkg.Elements.AddNew("Angular 17 Build (SPA)", "Artifact")
    art_spa.Update()
    
    n_mob = dep_pkg.Elements.AddNew("Smartphone del Paciente", "Node")
    n_mob.Stereotype = "device"
    n_mob.Update()
    
    env_os = dep_pkg.Elements.AddNew("Android 14 / iOS 17", "ExecutionEnvironment")
    env_os.Update()
    
    art_apk = dep_pkg.Elements.AddNew("SIGEPSI Mobile App (Flutter APK / IPA)", "Artifact")
    art_apk.Update()
    
    # Servidor Cloud Principal
    n_cloud = dep_pkg.Elements.AddNew("Servidor Cloud (Ubuntu 22.04 LTS)", "Node")
    n_cloud.Stereotype = "cloud server"
    n_cloud.Update()
    
    env_nginx = dep_pkg.Elements.AddNew("Servidor Proxy Inverso & SSL\n[Nginx 1.24 :443 HTTPS / WSS]", "ExecutionEnvironment")
    env_nginx.Notes = "Terminación SSL/TLS, enrutamiento por subdominio tenant y balanceo de carga."
    env_nginx.Update()
    
    env_wsgi = dep_pkg.Elements.AddNew("Servidor de Aplicación WSGI\n[Gunicorn 21.x :8000 WSGI]", "ExecutionEnvironment")
    env_wsgi.Update()
    
    art_django = dep_pkg.Elements.AddNew("Django 5.x REST Backend", "Artifact")
    art_django.Update()
    
    env_psql = dep_pkg.Elements.AddNew("Servidor SGBD\n[PostgreSQL 16 Multi-Tenant SGBD]", "ExecutionEnvironment")
    env_psql.Stereotype = "database"
    env_psql.Notes = "Base de datos multi-tenant por esquemas (public + tenant_schemas)."
    env_psql.Update()
    
    # Cluster Videoconferencia WebRTC
    n_jitsi = dep_pkg.Elements.AddNew("Cluster Videoconferencia WebRTC\n[Jitsi Meet Server]", "Node")
    n_jitsi.Stereotype = "cloud server"
    n_jitsi.Update()
    
    env_jitsi_srv = dep_pkg.Elements.AddNew("Jitsi Meet Server\n[WebRTC Audio/Video :10000 UDP]", "ExecutionEnvironment")
    env_jitsi_srv.Notes = "Jitsi VideoBridge (JVB) y Prosody XMPP para teleconsultas en tiempo real."
    env_jitsi_srv.Update()
    
    # Conectores y Rutas de Comunicación
    add_connector(env_browser, env_nginx, "CommunicationPath", "HTTPS :443 (REST API)")
    add_connector(env_os, env_nginx, "CommunicationPath", "HTTPS :443 (REST API)")
    add_connector(env_browser, env_jitsi_srv, "CommunicationPath", "WebRTC Data/Media Stream")
    add_connector(env_os, env_jitsi_srv, "CommunicationPath", "WebRTC Media Stream (RTP/RTCP)")
    add_connector(env_nginx, env_wsgi, "CommunicationPath", "Unix Domain Socket")
    add_connector(env_wsgi, art_django, "Dependency", "WSGI Handler")
    add_connector(art_django, env_psql, "CommunicationPath", "TCP/IP :5432 (psycopg2)")
    
    # Layout visual anidado en el diagrama de despliegue
    # PC
    add_diag_obj(dep_diag, n_pc, 40, -40, 360, -280, zorder=1)
    add_diag_obj(dep_diag, env_browser, 65, -85, 335, -170, zorder=2)
    add_diag_obj(dep_diag, art_spa, 90, -185, 310, -255, zorder=3)
    
    # Smartphone
    add_diag_obj(dep_diag, n_mob, 420, -40, 740, -280, zorder=1)
    add_diag_obj(dep_diag, env_os, 445, -85, 715, -170, zorder=2)
    add_diag_obj(dep_diag, art_apk, 470, -185, 690, -255, zorder=3)
    
    # Servidor Cloud Principal
    add_diag_obj(dep_diag, n_cloud, 40, -330, 740, -850, zorder=1)
    add_diag_obj(dep_diag, env_nginx, 80, -380, 700, -470, zorder=2)
    add_diag_obj(dep_diag, env_wsgi, 80, -500, 700, -620, zorder=2)
    add_diag_obj(dep_diag, art_django, 110, -550, 670, -605, zorder=3)
    add_diag_obj(dep_diag, env_psql, 80, -650, 700, -780, zorder=2)
    
    # Cluster Jitsi
    add_diag_obj(dep_diag, n_jitsi, 800, -40, 1140, -450, zorder=1)
    add_diag_obj(dep_diag, env_jitsi_srv, 830, -100, 1110, -380, zorder=2)
    
    dep_diag.Update()
    
    # Exportar imagen de Despliegue
    bmp_dep = os.path.join(out_dir, "Diagrama de Despliegue - Sprint 1.bmp")
    png_dep = os.path.join(out_dir, "Diagrama de Despliegue - Sprint 1.png")
    try:
        project.PutDiagramImageToFile(dep_diag.DiagramGUID, bmp_dep, 1)
        Image.open(bmp_dep).save(png_dep)
        print(f"Imagen exportada: {png_dep}")
    except Exception as e:
        print(f"Aviso al exportar imagen de despliegue: {e}")

    print("6. Diagrama de Despliegue (Sprint 1) creado exitosamente.")
    
    # Guardar y cerrar repositorio
    print("\nGuardando cambios en Enterprise Architect...", flush=True)
    dep_pkg.Packages.Refresh()
    arq_pkg.Packages.Refresh()
    sprint1_pkg.Packages.Refresh()
    repo.RefreshModelView(0)
    repo.CloseFile()
    repo.Exit()
    print("\n¡Los diagramas de Arquitectura de 3 Capas y Despliegue del Sprint 1 se han guardado exitosamente en DIAGRAMAS.eapx!", flush=True)
    return True

if __name__ == '__main__':
    add_capas_and_despliegue_sprint1()
