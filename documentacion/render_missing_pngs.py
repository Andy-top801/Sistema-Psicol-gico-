import os
import requests

img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "imagenes"))
os.makedirs(img_dir, exist_ok=True)

diagrams = {
    "diagrama_c4_nivel1_contexto.png": """@startuml
!include <C4/C4_Context>
LAYOUT_TOP_DOWN()
title Modelo C4 - Nivel 1: Diagrama de Contexto del Sistema (SIGEPSI)
Person(paciente, "Paciente", "Usuario de atención presencial o virtual")
Person(psicologo, "Psicólogo Clínico", "Apertura HC, SOAP, tareas, derivaciones")
Person(recepcionista, "Recepcionista en Turno", "Admisión, agenda y chat humano")
Person(admin_centro, "Admin Centro", "Gestión institucional y roles")
Person(superadmin, "SuperAdmin SaaS", "Multi-tenant global y esquemas")

System(sigepsi, "Plataforma SIGEPSI", "Gestión clínica y terapéutica SaaS Multi-Tenant")
System_Ext(jitsi, "Servidor Jitsi Meet", "Teleconsulta cifrada WebRTC")
System_Ext(hf_ia, "Hugging Face AI Space", "Chatbot y asistencia preconsulta")

Rel(paciente, sigepsi, "Usa app móvil y portal web", "HTTPS")
Rel(psicologo, sigepsi, "Gestiona historias clínicas y notas", "HTTPS")
Rel(recepcionista, sigepsi, "Gestiona citas y atiende chatbot", "HTTPS")
Rel(admin_centro, sigepsi, "Administra centro", "HTTPS")
Rel(superadmin, sigepsi, "Administra tenants", "HTTPS")
Rel(sigepsi, jitsi, "Inicia salas de teleconsulta", "WebRTC/HTTPS")
Rel(sigepsi, hf_ia, "Inferencia de lenguaje y chatbot", "REST HTTPS")
@enduml""",

    "diagrama_flujo_ia_sp2.png": """@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial

start
:Paciente completa Cuestionario Pre-Consulta;
:Consentimiento informado de IA verificado;
:Sanitización estricta de PII (anonimización de nombres, CI, teléfonos);
:Generación de Hash SHA-256 del Prompt;
:Evaluación con Motor de Reglas Clínicas Romero;
if (Detección de Riesgo Vital o Crisis?) then (Sí)
    :Disparar Alerta Roja Prioritaria;
    :Notificar a Recepción y Activar Protocolo de Crisis;
else (No)
    :Generar Borrador Asistivo Neutral;
endif
:Presentación al Psicólogo Tratante (Supervisión Humana Obligatoria);
if (Decisión del Profesional) then (Aprobar)
    :Incorporar a Historia Clínica;
elseif (Editar)
    :Ajustar observaciones y prioridad;
    :Guardar en Historia Clínica con trazabilidad;
else (Descartar)
    :Registrar motivo de descarte en Auditoría IA;
endif
:Registro Inmutable en AuditoriaIA (Hash, Decisión, Timestamp, IP);
stop
@enduml""",

    "diagrama_comunicacion_cu20.png": """@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
actor "Paciente / Usuario" as actor
boundary "IU_ChatbotWidget" as view
control "CTR_ChatbotController" as ctrl
entity "CE_ConversacionChatbot" as entity
actor "Recepcionista Humano" as human

actor -> view : 1. Enviar mensaje o consulta()
view -> ctrl : 2. POST /api/v1/chatbot/mensaje/
ctrl -> ctrl : 3. Sanitizar y clasificar intención (HF API)
ctrl -> entity : 4. INSERT clinica_mensajechatbot
ctrl -> ctrl : 5. Evaluar umbral de confianza o crisis vital
alt Intención Clara Normal
    ctrl --> view : 6a. Respuesta estructurada con botones
    view --> actor : 7a. Renderizar mensaje
else Alerta de Crisis o Solicitud de Operador
    ctrl -> entity : 6b. UPDATE conversacion (estado='ESCALADA_HUMANO')
    ctrl -> human : 7b. Emitir notificación de urgencia prioritaria
    human -> view : 8b. Operador humano asume el chat
    view --> actor : 9b. Asistencia humana en vivo
end
@enduml""",

    "diagrama_comunicacion_cu5.png": """@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
actor "SuperAdmin / Desarrollador" as act #LightYellow
boundary "IU_VisorBitacora" as iu #EBF5FB
control "CTR_AuditController" as ctr #E8F8F5
entity "CE_EncryptedAuditFile" as file #FADBD8
entity "CE_Usuario" as usr #FEF9E7

act -> iu : 1: Ingresar Llave Maestra y fecha/tenant()
iu -> ctr : 2: GET /api/v1/audit/log/ (X-Developer-Key)
ctr -> ctr : 3: Validar HMAC-SHA256 Llave Maestra
ctr -> file : 4: Leer líneas cifradas (.log.enc modo 0600)
file --> ctr : 5: Stream binario Fernet
ctr -> ctr : 6: Descifrar en memoria con AES-256
ctr -> usr : 7: Consultar usuario y rol
usr --> ctr : 8: Metadatos usuario
ctr --> iu : 9: HTTP 200 OK [eventos_desencriptados]
iu --> act : 10: Renderizar grilla forense interactiva
@enduml""",

    "diagrama_comunicacion_cu25.png": """@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
actor "Admin Centro / Coordinador" as act #LightYellow
boundary "IU_ConstructorReportes" as iu #EBF5FB
control "CTR_SpeechParserService" as voice #E8F8F5
control "CTR_ReportEngine" as ctr #E8F8F5
entity "CE_DatosClinicosTenant" as ce #FEF9E7

act -> iu : 1: Dictar por voz o seleccionar columnas QBE()
iu -> voice : 2: Parsear audio y extraer filtros
voice --> iu : 3: Parámetros estructurados
iu -> ctr : 4: POST /api/v1/reportes/personalizado/
ctr -> ctr : 5: Construir query relacional con aislamiento tenant
ctr -> ce : 6: SELECT proyectado con JOINs dinámicos
ce --> ctr : 7: Dataset relacional de registros
ctr -> ctr : 8: Generar Excel OpenPyXL / CSV
ctr --> iu : 9: HTTP 200 Stream binario
iu --> act : 10: Descarga automática de reporte
@enduml""",

    "diagrama_comunicacion_cu28.png": """@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
actor "SuperAdministrador" as act #LightYellow
boundary "IU_ConsolaBackupRestore" as iu #EBF5FB
control "CTR_BackupRestoreService" as ctr #E8F8F5
entity "CE_TenantDatabaseSchema" as db #FEF9E7
entity "CE_BackupLogRegistro" as log #FEF9E7

act -> iu : 1: Solicitar generación de Backup Manual()
iu -> ctr : 2: POST /api/tenants/{id}/backup/
ctr -> db : 3: Ejecutar pg_dump por esquema (gzip)
db --> ctr : 4: Stream binario de dump generado
ctr -> ctr : 5: Calcular Checksum criptográfico SHA-256
ctr -> log : 6: INSERT INTO backups_registro
log --> ctr : 7: Metadatos persistidos
ctr --> iu : 8: HTTP 201 Created (url_descarga, sha256)
iu --> act : 9: Habilitar tarjeta con hash verificado
@enduml"""
}

for name, puml in diagrams.items():
    print(f"Rendering {name}...", flush=True)
    resp = requests.post("https://kroki.io/plantuml/png", json={"diagram_source": puml, "diagram_type": "plantuml", "output_format": "png"}, timeout=25)
    if resp.status_code == 200:
        out = os.path.join(img_dir, name)
        with open(out, "wb") as f:
            f.write(resp.content)
        print(f"  [OK] Generated {name} ({len(resp.content)} bytes)")
    else:
        print(f"  [ERROR] {resp.status_code}: {resp.text[:100]}")

print("=== ALL DIAGRAMS PROCESSED ===")
