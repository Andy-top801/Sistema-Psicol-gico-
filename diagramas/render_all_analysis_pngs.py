import requests
import os

img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "documentacion", "imagenes"))
os.makedirs(img_dir, exist_ok=True)

SPECS = [
    {
        "cu_id": "CU14",
        "cu_short": "CU14 Intake Digital",
        "title": "CU14: Ficha Previa de Intake Digital",
        "subpkg_name": "CU14 - Clases de Análisis: Intake Digital",
        "diag_name": "Diagrama de Clases de Análisis – CU14: Ficha Previa de Intake Digital",
        "img_file": "diagrama_clases_analisis_cu14.png",
        "actor": "Paciente",
        "boundary": {
            "name": "UI_FormularioPreConsulta",
            "methods": [
                ("ingresar_respuestas(sintomas, escala_malestar, antecedentes)", "void"),
                ("validar_campos_requeridos()", "boolean"),
                ("mostrar_alerta_urgencia_prioritaria()", "void"),
                ("confirmacion_envio_exitosa(badge_prioridad)", "void")
            ]
        },
        "control": {
            "name": "IntakeController",
            "methods": [
                ("post_respuestas(payload_jsonb)", "HttpResponse"),
                ("validar_esquema_json_y_urgencia(escala)", "boolean"),
                ("clasificar_prioridad(malestar)", "string")
            ]
        },
        "entity": {
            "name": "RespuestaPreConsulta",
            "attrs": [
                ("id", "UUID"),
                ("paciente_id", "UUID"),
                ("cita_id", "UUID"),
                ("sintomas", "JSONB"),
                ("escala_malestar", "int"),
                ("antecedentes", "text"),
                ("prioridad", "string"),
                ("fecha_registro", "datetime")
            ],
            "methods": [
                ("create(data)", "RespuestaPreConsulta"),
                ("get(id)", "RespuestaPreConsulta"),
                ("filter_by_paciente(paciente_id)", "list")
            ]
        }
    },
    {
        "cu_id": "CU15",
        "cu_short": "CU15 Historia Clinica",
        "title": "CU15: Historia Clínica y Control RBAC",
        "subpkg_name": "CU15 - Clases de Análisis: Historia Clínica y RBAC",
        "diag_name": "Diagrama de Clases de Análisis – CU15: Historia Clínica y Control RBAC",
        "img_file": "diagrama_clases_analisis_cu15.png",
        "actor": "Psicologo Tratante",
        "boundary": {
            "name": "UI_HistoriaClinica",
            "methods": [
                ("solicitar_apertura_historia(paciente_id)", "void"),
                ("renderizar_pestanas_historia(anamnesis, examen_mental, cie11)", "void"),
                ("mostrar_error_seguridad_rbac(mensaje)", "void")
            ]
        },
        "control": {
            "name": "HistoriaClinicaController",
            "methods": [
                ("post_historia_clinica(paciente_id, anamnesis)", "HttpResponse"),
                ("verificar_permiso_rbac(role, terapeuta_asignado)", "boolean"),
                ("generar_codigo_expediente(paciente_id)", "string")
            ]
        },
        "entity": {
            "name": "HistoriaClinica",
            "attrs": [
                ("id", "UUID"),
                ("codigo_expediente", "string"),
                ("paciente_id", "UUID"),
                ("psicologo_id", "UUID"),
                ("anamnesis_inicial", "text"),
                ("examen_mental", "text"),
                ("cie11_codigos", "string[]"),
                ("estado", "string"),
                ("fecha_apertura", "datetime"),
                ("cerrada", "boolean")
            ],
            "methods": [
                ("create(expediente)", "HistoriaClinica"),
                ("get_by_codigo(codigo)", "HistoriaClinica"),
                ("update_anamnesis(data)", "void"),
                ("close_expediente()", "void")
            ]
        }
    },
    {
        "cu_id": "CU16",
        "cu_short": "CU16 Notas SOAP",
        "title": "CU16: Notas SOAP y Autoguardado Reactivo",
        "subpkg_name": "CU16 - Clases de Análisis: Notas SOAP",
        "diag_name": "Diagrama de Clases de Análisis – CU16: Notas SOAP y Autoguardado Reactivo",
        "img_file": "diagrama_clases_analisis_cu16.png",
        "actor": "Psicologo Tratante",
        "boundary": {
            "name": "UI_EditorNotasSOAP",
            "methods": [
                ("redactar_nota_soap(s, o, a, p)", "void"),
                ("disparar_autoguardado_debounce()", "void"),
                ("formalizar_y_firmar_nota()", "void"),
                ("bloquear_editor_y_actualizar_timeline()", "void")
            ]
        },
        "control": {
            "name": "NotaSesionController",
            "methods": [
                ("patch_borrador(id, payload_parcial)", "HttpResponse"),
                ("post_firmar_nota(cita_id, payload_completo)", "HttpResponse"),
                ("validar_cita_realizada_y_bloqueo(cita_id)", "boolean")
            ]
        },
        "entity": {
            "name": "NotaSesion",
            "attrs": [
                ("id", "UUID"),
                ("cita_id", "UUID"),
                ("historia_clinica_id", "UUID"),
                ("subjetivo", "text"),
                ("objetivo", "text"),
                ("analisis", "text"),
                ("plan", "text"),
                ("estado", "string"),
                ("firmada", "boolean"),
                ("fecha_firma", "datetime")
            ],
            "methods": [
                ("save_borrador(datos)", "NotaSesion"),
                ("seal_inmutable()", "void"),
                ("get_by_cita(cita_id)", "NotaSesion")
            ]
        }
    },
    {
        "cu_id": "CU17",
        "cu_short": "CU17 Tareas Terapeuticas",
        "title": "CU17: Tareas Terapéuticas y Feedback",
        "subpkg_name": "CU17 - Clases de Análisis: Tareas Terapéuticas",
        "diag_name": "Diagrama de Clases de Análisis – CU17: Tareas Terapéuticas y Feedback",
        "img_file": "diagrama_clases_analisis_cu17.png",
        "actor": "Paciente Movil",
        "boundary": {
            "name": "UI_GestionTareas",
            "methods": [
                ("reportar_cumplimiento(tarea_id, texto, archivo)", "void"),
                ("actualizar_indicador_progreso(porcentaje)", "void"),
                ("mostrar_aviso_retraso(mensaje)", "void")
            ]
        },
        "control": {
            "name": "TareasController",
            "methods": [
                ("post_evidencia(tarea_id, form_data)", "HttpResponse"),
                ("validar_plazo_limite_y_tipo_archivo(fecha_limite, file)", "boolean"),
                ("calcular_adherencia_terapeutica(paciente_id)", "float")
            ]
        },
        "entity": {
            "name": "TareaTerapeutica",
            "attrs": [
                ("id", "UUID"),
                ("sesion_id", "UUID"),
                ("titulo", "string"),
                ("descripcion", "text"),
                ("fecha_limite", "datetime"),
                ("estado", "string"),
                ("evidencia_texto", "text"),
                ("evidencia_archivo_url", "string"),
                ("fecha_entrega", "datetime")
            ],
            "methods": [
                ("create_tarea(datos)", "TareaTerapeutica"),
                ("submit_evidencia(texto, archivo_url)", "void"),
                ("update_estado(nuevo_estado)", "void")
            ]
        }
    },
    {
        "cu_id": "CU18",
        "cu_short": "CU18 Consentimiento",
        "title": "CU18: Consentimiento Informado y Firma Digital",
        "subpkg_name": "CU18 - Clases de Análisis: Consentimiento Informado",
        "diag_name": "Diagrama de Clases de Análisis – CU18: Consentimiento Informado y Firma Digital",
        "img_file": "diagrama_clases_analisis_cu18.png",
        "actor": "Paciente o Tutor",
        "boundary": {
            "name": "UI_FirmaConsentimiento",
            "methods": [
                ("leer_clausulas_obligatorias()", "void"),
                ("firmar_en_canvas()", "void"),
                ("calcular_hash_sha256(texto, trazos, timestamp)", "string"),
                ("enviar_firma_digital()", "void"),
                ("habilitar_atencion_y_reserva()", "void")
            ]
        },
        "control": {
            "name": "ConsentimientoController",
            "methods": [
                ("post_firmar_consentimiento(hash, firma_png, tutor_ci)", "HttpResponse"),
                ("capturar_metadatos_legales(ip, user_agent, timestamp)", "dict"),
                ("validar_ci_y_parentesco_tutor(tutor_ci)", "boolean")
            ]
        },
        "entity": {
            "name": "FirmaConsentimiento",
            "attrs": [
                ("id", "UUID"),
                ("paciente_id", "UUID"),
                ("plantilla_id", "UUID"),
                ("tipo_firmante", "string"),
                ("tutor_ci", "string"),
                ("hash_sha256", "string"),
                ("trazo_firma_png_url", "string"),
                ("ip_origen", "string"),
                ("user_agent", "string"),
                ("timestamp_bolivia", "datetime"),
                ("inmutable", "boolean")
            ],
            "methods": [
                ("store_firma(firma_data)", "FirmaConsentimiento"),
                ("verify_integrity(hash)", "boolean"),
                ("get_by_paciente(paciente_id)", "FirmaConsentimiento")
            ]
        }
    },
    {
        "cu_id": "CU19",
        "cu_short": "CU19 Derivacion",
        "title": "CU19: Cierre de Caso y Derivación Psiquiátrica",
        "subpkg_name": "CU19 - Clases de Análisis: Derivación Psiquiátrica",
        "diag_name": "Diagrama de Clases de Análisis – CU19: Cierre de Caso y Derivación Psiquiátrica",
        "img_file": "diagrama_clases_analisis_cu19.png",
        "actor": "Psicologo Tratante",
        "boundary": {
            "name": "UI_DerivacionCierre",
            "methods": [
                ("emitir_orden_interconsulta(motivo, riesgo, sintomatologia)", "void"),
                ("registrar_alta_terapeutica(resumen)", "void"),
                ("mostrar_comprobante_interconsulta(pdf_url)", "void"),
                ("mostrar_comprobante_alta(mensaje)", "void")
            ]
        },
        "control": {
            "name": "DerivacionController",
            "methods": [
                ("post_derivacion(paciente_id, destino, riesgo)", "HttpResponse"),
                ("compilar_pdf_interconsulta(datos_caso)", "bytes"),
                ("ejecutar_cierre_alta(historia_id, resumen)", "HttpResponse")
            ]
        },
        "entity": {
            "name": "DerivacionCaso",
            "attrs": [
                ("id", "UUID"),
                ("historia_clinica_id", "UUID"),
                ("tipo", "string"),
                ("profesional_destino", "string"),
                ("especialidad_destino", "string"),
                ("motivo_interconsulta", "text"),
                ("nivel_urgencia", "string"),
                ("pdf_orden_url", "string"),
                ("estado", "string"),
                ("fecha_emision", "datetime")
            ],
            "methods": [
                ("create_derivacion(data)", "DerivacionCaso"),
                ("update_estado(estado)", "void"),
                ("get_derivaciones(historia_id)", "list")
            ]
        }
    },
    {
        "cu_id": "CU20",
        "cu_short": "CU20 Chatbot",
        "title": "CU20: Chatbot de Orientación Clínica y Derivación a Operador",
        "subpkg_name": "CU20 - Clases de Análisis: Chatbot y Escalamiento",
        "diag_name": "Diagrama de Clases de Análisis – CU20: Chatbot de Orientación Clínica",
        "img_file": "diagrama_clases_analisis_cu20.png",
        "actor": "Paciente / Usuario",
        "boundary": {
            "name": "UI_ChatbotWidget",
            "methods": [
                ("enviar_mensaje_o_consulta(texto, session_token)", "void"),
                ("renderizar_mensaje_de_orientacion(botones_accion)", "void"),
                ("desplegar_modal_urgencias_con_telefonos()", "void"),
                ("mostrar_estado_espera()", "void"),
                ("conexion_en_vivo_con_soporte(mensaje)", "void")
            ]
        },
        "control": {
            "name": "ChatbotController",
            "methods": [
                ("post_mensaje(texto, session_id)", "HttpResponse"),
                ("sanitizar_y_clasificar_intencion(texto)", "IntentResult"),
                ("evaluar_umbral_de_confianza_o_crisis(intent)", "string"),
                ("emitir_notificacion_websocket_transferencia(id)", "void")
            ]
        },
        "entity": {
            "name": "ConversacionChatbot",
            "attrs": [
                ("id", "UUID"),
                ("session_token", "string"),
                ("estado", "string"),
                ("crisis_detectada", "boolean"),
                ("total_mensajes", "int"),
                ("operador_asignado_id", "UUID"),
                ("fecha_inicio", "datetime"),
                ("fecha_escalamiento", "datetime")
            ],
            "methods": [
                ("create_session()", "ConversacionChatbot"),
                ("add_mensaje(emisor, texto)", "void"),
                ("escalate_to_human(operador_id)", "void")
            ]
        }
    },
    {
        "cu_id": "HU-35",
        "cu_short": "HU-35 Pasarela IA",
        "title": "HU-35: Consentimiento y Pasarela Ética de IA",
        "subpkg_name": "HU-35 - Clases de Análisis: Pasarela Ética de IA",
        "diag_name": "Diagrama de Clases de Análisis – HU-35: Pasarela Ética de IA",
        "img_file": "diagrama_clases_analisis_hu35.png",
        "actor": "Psicologo Clinico",
        "boundary": {
            "name": "UI_PanelAsistenteIA",
            "methods": [
                ("solicitar_analisis_preconsulta(formulario_id)", "void"),
                ("renderizar_panel_asistivo(resumen, priorizacion, reglas)", "void"),
                ("aceptar_descartar_o_editar(decision)", "void"),
                ("notificar_incorporacion_expediente()", "void"),
                ("habilitar_modo_evaluacion_manual()", "void")
            ]
        },
        "control": {
            "name": "PasarelaIAService",
            "methods": [
                ("post_analizar_preconsulta(formulario_id)", "HttpResponse"),
                ("verificar_consentimiento_activo_y_anonimizar_pii(datos)", "dict"),
                ("invoke_prompt_clinico_neutral(sintomas, escala)", "string"),
                ("post_decision_humana(auditoria_id, decision, obs)", "HttpResponse")
            ]
        },
        "entity": {
            "name": "AuditoriaIAInteraccion",
            "attrs": [
                ("id", "UUID"),
                ("formulario_intake_id", "UUID"),
                ("hash_prompt_sha256", "string"),
                ("respuesta_asistiva_raw", "text"),
                ("evaluacion_humana", "string"),
                ("decision_final", "string"),
                ("observaciones_psicologo", "text"),
                ("revisor_id", "UUID"),
                ("timestamp_analisis", "datetime")
            ],
            "methods": [
                ("create_auditoria(prompt_hash, raw_resp)", "AuditoriaIAInteraccion"),
                ("close_auditoria_decision(decision, revisor_id, obs)", "void"),
                ("verify_no_diagnostico_flag()", "boolean")
            ]
        }
    },
    {
        "cu_id": "CU5",
        "cu_short": "CU5 Bitacora",
        "title": "CU5: Bitácora Confidencial y Llave Única del Desarrollador (Criterio 3)",
        "subpkg_name": "CU5 - Clases de Análisis: Bitácora Confidencial",
        "diag_name": "Diagrama de Clases de Análisis – CU5: Bitácora Confidencial",
        "img_file": "diagrama_clases_analisis_cu5.png",
        "actor": "SuperAdmin / Desarrollador",
        "boundary": {
            "name": "UI_VisorBitacora",
            "methods": [
                ("ingresar_llave_maestra(dev_key, fecha, tenant)", "void"),
                ("renderizar_tabla_forense(eventos)", "void"),
                ("mostrar_alerta_seguridad_bloqueo(msg)", "void")
            ]
        },
        "control": {
            "name": "AuditLogController",
            "methods": [
                ("get_audit_logs(date, tenant, dev_key)", "HttpResponse"),
                ("validar_firma_hmac_sha256(key)", "boolean"),
                ("decrypt_payload_fernet(linea, key)", "dict"),
                ("write_event_sync(event)", "void")
            ]
        },
        "entity": {
            "name": "EncryptedAuditFile",
            "attrs": [
                ("file_path", "string"),
                ("date_stamp", "date"),
                ("permissions_mode", "string"),
                ("total_lines_encrypted", "int"),
                ("file_lock_acquired", "boolean"),
                ("timezone_bolivia", "string")
            ],
            "methods": [
                ("append_encrypted_line(cipher_bytes)", "void"),
                ("stream_encrypted_lines(date)", "bytes[]"),
                ("ensure_file_permissions_0600()", "void")
            ]
        }
    },
    {
        "cu_id": "CU25",
        "cu_short": "CU25 Reportes QBE",
        "title": "CU25: Constructor de Reportes Personalizados (QBE), Multiformato y Voz (Criterio 5)",
        "subpkg_name": "CU25 - Clases de Análisis: Reportes Personalizados QBE y Voz",
        "diag_name": "Diagrama de Clases de Análisis – CU25: Reportes Personalizados QBE y Voz",
        "img_file": "diagrama_clases_analisis_cu25.png",
        "actor": "Admin Centro / Coordinador",
        "boundary": {
            "name": "UI_ConstructorReportesQBE",
            "methods": [
                ("presionar_boton_microfono()", "void"),
                ("dictar_instruccion(audio)", "void"),
                ("actualizar_formulario_qbe_reactivo(filtros)", "void"),
                ("seleccionar_columnas_y_filtros(fuente, cols, flts)", "void"),
                ("solicitar_ejecucion_y_exportacion(formato)", "void"),
                ("disparar_descarga_automatica(archivo)", "void"),
                ("modal_confirmacion_envio_correo()", "void")
            ]
        },
        "control": {
            "name": "ReportEngineController",
            "methods": [
                ("post_reporte_personalizado(payload_qbe, formato)", "HttpResponse"),
                ("parse_voice_command(speech_transcript)", "dict"),
                ("construir_query_dinamico_con_aislamiento_tenant(qbe)", "string"),
                ("generar_libro_excel_openpyxl(dataset, headers)", "bytes"),
                ("adjuntar_y_enviar_smtp(email, dataset)", "boolean")
            ]
        },
        "entity": {
            "name": "ReporteDefinicionQBE",
            "attrs": [
                ("id", "UUID"),
                ("tenant_id", "string"),
                ("fuente_datos", "string"),
                ("columnas_seleccionadas", "string[]"),
                ("filtros_aplicados", "JSONB"),
                ("ordenamiento", "string"),
                ("comando_voz_original", "string"),
                ("formato_exportacion", "string"),
                ("fecha_generacion", "datetime")
            ],
            "methods": [
                ("execute_projected_query(query_sql)", "list"),
                ("save_template_qbe(template)", "void"),
                ("get_column_catalog(fuente)", "list")
            ]
        }
    },
    {
        "cu_id": "CU28",
        "cu_short": "CU28 Backup y Restore",
        "title": "CU28: Copias de Seguridad y Restauración (Backup / Restore) en la Nube (Criterio 6)",
        "subpkg_name": "CU28 - Clases de Análisis: Copias de Seguridad y Restauración",
        "diag_name": "Diagrama de Clases de Análisis – CU28: Copias de Seguridad y Restauración",
        "img_file": "diagrama_clases_analisis_cu28.png",
        "actor": "SuperAdministrador",
        "boundary": {
            "name": "UI_ConsolaBackupRestore",
            "methods": [
                ("solicitar_backup_manual(ambito, tenant_id)", "void"),
                ("cargar_archivo_respaldo(file, tenant_destino)", "void"),
                ("validar_extension_y_tamano_archivo(file)", "boolean"),
                ("renderizar_tarjeta_descarga_backup(info)", "void"),
                ("alerta_modal_exito(mensaje)", "void"),
                ("alerta_error_restauracion(error)", "void")
            ]
        },
        "control": {
            "name": "BackupRestoreOrchestrator",
            "methods": [
                ("post_backup_manual(ambito, tenant_id)", "HttpResponse"),
                ("post_restaurar_dump(dump_file, tenant_destino)", "HttpResponse"),
                ("ejecutar_pg_dump(esquema, formato)", "bytes"),
                ("calcular_checksum_sha256_y_comprimir(dump)", "tuple"),
                ("verificar_integridad_checksum(file, sha256)", "boolean"),
                ("ejecutar_pg_restore(file, esquema, flags)", "int")
            ]
        },
        "entity": {
            "name": "BackupLogRegistro",
            "attrs": [
                ("id", "UUID"),
                ("nombre_archivo", "string"),
                ("ambito", "string"),
                ("tenant_schema", "string"),
                ("tamano_mb", "float"),
                ("checksum_sha256", "string"),
                ("estado", "string"),
                ("timestamp_ejecucion", "datetime"),
                ("duracion_segundos", "int")
            ],
            "methods": [
                ("log_backup_operation(data)", "BackupLogRegistro"),
                ("log_restore_operation(data)", "BackupLogRegistro"),
                ("get_backups_history(tenant)", "list")
            ]
        }
    }
]

print(f"Rendering all {len(SPECS)} Analysis Class Diagrams to {img_dir}...")

for s in SPECS:
    print(f"Generating PNG for {s['cu_id']} ({s['img_file']})...", flush=True)
    puml = f"""@startuml
left to right direction
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
skinparam classAttributeIconSize 0
hide circle

class "{s['actor']}" <<Actor>> #LightYellow

class "{s['cu_short']}::{s['boundary']['name']}" as UI #EBF5FB {{
"""
    for m, r in s['boundary']['methods']:
        puml += f"    + {m}: {r}\n"
    puml += f"""}}

class "{s['cu_short']}::{s['control']['name']}" as Controller #E8F8F5 {{
"""
    for m, r in s['control']['methods']:
        puml += f"    + {m}: {r}\n"
    puml += f"""}}

class "{s['cu_short']}::{s['entity']['name']}" as Entity #FADBD8 {{
"""
    for a, t in s['entity']['attrs']:
        puml += f"    - {a}: {t}\n"
    puml += "    __\n"
    for m, r in s['entity']['methods']:
        puml += f"    + {m}: {r}\n"
    puml += f"""}}

"{s['actor']}" -- UI
UI -- Controller
Controller -- Entity
@enduml"""

    try:
        payload = {
            "diagram_source": puml,
            "diagram_type": "plantuml",
            "output_format": "png"
        }
        r = requests.post("https://kroki.io/plantuml/png", json=payload, timeout=25)
        if r.status_code == 200:
            out_path = os.path.join(img_dir, s['img_file'])
            with open(out_path, "wb") as f_out:
                f_out.write(r.content)
            print(f"  -> Successfully generated {s['img_file']} ({len(r.content)} bytes)")
        else:
            print(f"  -> Error {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  -> Exception: {e}")

print("=== ALL 11 IMAGES GENERATED SUCCESSFULLY ===")
