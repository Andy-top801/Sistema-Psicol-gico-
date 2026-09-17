import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  FormularioPreConsulta,
  RespuestaPreConsulta,
  HistoriaClinica,
  DiagnosticoCIE,
  NotaSesion,
  EvolucionClinica,
  TareaTerapeutica,
  ConsentimientoInformado,
  FirmaConsentimiento,
  DerivacionCaso,
  CieItem,
  AnalisisIAResponse,
  DecisionIARequest
} from '../models/clinica-sprint2.model';

@Injectable({
  providedIn: 'root'
})
export class ClinicaSprint2Service {
  private apiUrl = `${environment.apiUrl}/clinica`;

  constructor(private http: HttpClient) {}

  // --------------------------------------------------------------------------
  // CU14: INTAKE DIGITAL Y FORMULARIOS PRE-CONSULTA
  // --------------------------------------------------------------------------
  getFormulariosPreconsulta(): Observable<FormularioPreConsulta[]> {
    return this.http.get<FormularioPreConsulta[]>(`${this.apiUrl}/formularios-preconsulta/`);
  }

  getFormularioPreconsultaById(id: string): Observable<FormularioPreConsulta> {
    return this.http.get<FormularioPreConsulta>(`${this.apiUrl}/formularios-preconsulta/${id}/`);
  }

  crearFormularioPreconsulta(data: Partial<FormularioPreConsulta>): Observable<FormularioPreConsulta> {
    return this.http.post<FormularioPreConsulta>(`${this.apiUrl}/formularios-preconsulta/`, data);
  }

  actualizarFormularioPreconsulta(id: string, data: Partial<FormularioPreConsulta>): Observable<FormularioPreConsulta> {
    return this.http.patch<FormularioPreConsulta>(`${this.apiUrl}/formularios-preconsulta/${id}/`, data);
  }

  getRespuestasPreconsulta(citaId?: string, pacienteId?: string): Observable<RespuestaPreConsulta[]> {
    let params = new HttpParams();
    if (citaId) params = params.set('cita', citaId);
    if (pacienteId) params = params.set('paciente', pacienteId);
    return this.http.get<RespuestaPreConsulta[]>(`${this.apiUrl}/respuestas-preconsulta/`, { params });
  }

  getRespuestaPreconsultaById(id: string): Observable<RespuestaPreConsulta> {
    return this.http.get<RespuestaPreConsulta>(`${this.apiUrl}/respuestas-preconsulta/${id}/`);
  }

  enviarRespuestaPreconsulta(data: {
    formulario: string;
    cita: string;
    paciente: string;
    respuestas_json: Record<string, any>;
    consentimiento_ia_procesamiento?: boolean;
  }): Observable<RespuestaPreConsulta> {
    return this.http.post<RespuestaPreConsulta>(`${this.apiUrl}/respuestas-preconsulta/`, data);
  }

  analizarRespuestaConIA(respuestaId: string): Observable<AnalisisIAResponse> {
    return this.http.post<AnalisisIAResponse>(`${this.apiUrl}/respuestas-preconsulta/${respuestaId}/analizar_ia/`, {});
  }

  // --------------------------------------------------------------------------
  // CU15: HISTORIAS CLÍNICAS Y CATÁLOGO CIE-10
  // --------------------------------------------------------------------------
  getHistoriasClinicas(search?: string): Observable<HistoriaClinica[]> {
    let params = new HttpParams();
    if (search) params = params.set('search', search);
    return this.http.get<HistoriaClinica[]>(`${this.apiUrl}/historias-clinicas/`, { params });
  }

  getHistoriaClinicaById(id: string): Observable<HistoriaClinica> {
    return this.http.get<HistoriaClinica>(`${this.apiUrl}/historias-clinicas/${id}/`);
  }

  crearHistoriaClinica(data: {
    paciente: string;
    psicologo_cabecera?: string;
    motivo_consulta_inicial?: string;
    anamnesis?: string;
    antecedentes_personales?: string;
    antecedentes_familiares?: string;
    examen_estado_mental?: string;
    plan_terapeutico?: string;
    objetivos_terapeuticos?: string[];
  }): Observable<HistoriaClinica> {
    return this.http.post<HistoriaClinica>(`${this.apiUrl}/historias-clinicas/`, data);
  }

  actualizarHistoriaClinica(id: string, data: Partial<HistoriaClinica>): Observable<HistoriaClinica> {
    return this.http.patch<HistoriaClinica>(`${this.apiUrl}/historias-clinicas/${id}/`, data);
  }

  buscarCIE10(query: string): Observable<CieItem[]> {
    const params = new HttpParams().set('q', query);
    return this.http.get<CieItem[]>(`${this.apiUrl}/historias-clinicas/buscar_cie10/`, { params });
  }

  agregarDiagnostico(historiaId: string, data: {
    codigo_cie10: string;
    descripcion: string;
    tipo: 'PRINCIPAL' | 'SECUNDARIO' | 'PRESUNTIVO' | 'DESCARTADO';
    notas_criterio?: string;
  }): Observable<{ mensaje: string; diagnosticos: DiagnosticoCIE[] }> {
    return this.http.post<{ mensaje: string; diagnosticos: DiagnosticoCIE[] }>(
      `${this.apiUrl}/historias-clinicas/${historiaId}/agregar_diagnostico/`,
      data
    );
  }

  removerDiagnostico(historiaId: string, diagnosticoId: string): Observable<{ mensaje: string; diagnosticos: DiagnosticoCIE[] }> {
    const params = new HttpParams().set('diagnostico_id', diagnosticoId);
    return this.http.delete<{ mensaje: string; diagnosticos: DiagnosticoCIE[] }>(
      `${this.apiUrl}/historias-clinicas/${historiaId}/remover_diagnostico/`,
      { params }
    );
  }

  getTimeline(historiaId: string): Observable<{
    historia: { id: string; numero: string; paciente: string };
    total_eventos: number;
    timeline: Array<{
      id: string;
      tipo: 'SESION' | 'EVOLUCION' | 'TAREA' | 'CONSENTIMIENTO' | 'DERIVACION';
      fecha: string;
      titulo: string;
      detalle: string;
      alerta: boolean;
      estado?: string;
      profesional?: string;
      metadata: Record<string, any>;
    }>;
  }> {
    return this.http.get<any>(`${this.apiUrl}/historias-clinicas/${historiaId}/timeline/`);
  }

  // --------------------------------------------------------------------------
  // CU16: NOTAS DE SESIÓN CLÍNICA (MODELO SOAP)
  // --------------------------------------------------------------------------
  getNotasSesion(historiaId?: string): Observable<NotaSesion[]> {
    let params = new HttpParams();
    if (historiaId) params = params.set('historia_clinica', historiaId);
    return this.http.get<NotaSesion[]>(`${this.apiUrl}/notas-sesion/`, { params });
  }

  getNotaSesionById(id: string): Observable<NotaSesion> {
    return this.http.get<NotaSesion>(`${this.apiUrl}/notas-sesion/${id}/`);
  }

  guardarBorrador(data: {
    id?: string;
    historia_clinica: string;
    cita?: string;
    subjetivo: string;
    objetivo: string;
    analisis: string;
    plan: string;
    intervenciones_aplicadas?: string;
    nivel_riesgo: string;
    duracion_minutos?: number;
  }): Observable<NotaSesion> {
    return this.http.post<NotaSesion>(`${this.apiUrl}/notas-sesion/guardar_borrador/`, data);
  }

  firmarNotaSesion(notaId: string, data: {
    subjetivo: string;
    objetivo: string;
    analisis: string;
    plan: string;
    intervenciones_aplicadas?: string;
    nivel_riesgo: string;
  }): Observable<{ mensaje: string; nota: NotaSesion; sha256: string }> {
    return this.http.post<{ mensaje: string; nota: NotaSesion; sha256: string }>(
      `${this.apiUrl}/notas-sesion/${notaId}/firmar_nota/`,
      data
    );
  }

  // --------------------------------------------------------------------------
  // CU17: EVOLUCIÓN CLÍNICA Y ALERTAS DE RECAÍDA
  // --------------------------------------------------------------------------
  getEvoluciones(historiaId?: string): Observable<EvolucionClinica[]> {
    let params = new HttpParams();
    if (historiaId) params = params.set('historia_clinica', historiaId);
    return this.http.get<EvolucionClinica[]>(`${this.apiUrl}/evoluciones/`, { params });
  }

  registrarEvolucion(data: {
    historia_clinica: string;
    nota_sesion?: string;
    puntuacion_escala: number;
    indicador_progreso: string;
    alerta_crisis_recaida?: boolean;
    descripcion_crisis?: string;
    recomendacion_inmediata?: string;
  }): Observable<EvolucionClinica> {
    return this.http.post<EvolucionClinica>(`${this.apiUrl}/evoluciones/`, data);
  }

  // --------------------------------------------------------------------------
  // CU17: TAREAS TERAPÉUTICAS INTER-SESIÓN
  // --------------------------------------------------------------------------
  getTareas(historiaId?: string): Observable<TareaTerapeutica[]> {
    let params = new HttpParams();
    if (historiaId) params = params.set('historia_clinica', historiaId);
    return this.http.get<TareaTerapeutica[]>(`${this.apiUrl}/tareas/`, { params });
  }

  crearTarea(data: {
    historia_clinica: string;
    cita_origen?: string;
    titulo: string;
    instrucciones: string;
    categoria: string;
    fecha_limite: string;
  }): Observable<TareaTerapeutica> {
    return this.http.post<TareaTerapeutica>(`${this.apiUrl}/tareas/`, data);
  }

  subirEvidenciaTarea(tareaId: string, data: {
    reflexion_paciente: string;
    nivel_dificultad_percibido: number;
    archivo_adjunto?: string;
  }): Observable<{ mensaje: string; tarea: TareaTerapeutica }> {
    return this.http.post<{ mensaje: string; tarea: TareaTerapeutica }>(
      `${this.apiUrl}/tareas/${tareaId}/subir_evidencia/`,
      data
    );
  }

  revisarTarea(tareaId: string, feedback: string): Observable<{ mensaje: string; tarea: TareaTerapeutica }> {
    return this.http.post<{ mensaje: string; tarea: TareaTerapeutica }>(
      `${this.apiUrl}/tareas/${tareaId}/revisar_tarea/`,
      { feedback }
    );
  }

  // --------------------------------------------------------------------------
  // CU18: CONSENTIMIENTOS INFORMADOS
  // --------------------------------------------------------------------------
  getPlantillasConsentimiento(): Observable<ConsentimientoInformado[]> {
    return this.http.get<ConsentimientoInformado[]>(`${this.apiUrl}/consentimientos-plantillas/`);
  }

  crearPlantillaConsentimiento(data: Partial<ConsentimientoInformado>): Observable<ConsentimientoInformado> {
    return this.http.post<ConsentimientoInformado>(`${this.apiUrl}/consentimientos-plantillas/`, data);
  }

  getFirmasConsentimiento(pacienteId?: string): Observable<FirmaConsentimiento[]> {
    let params = new HttpParams();
    if (pacienteId) params = params.set('paciente', pacienteId);
    return this.http.get<FirmaConsentimiento[]>(`${this.apiUrl}/consentimientos-firmas/`, { params });
  }

  firmarConsentimiento(data: {
    plantilla: string;
    paciente: string;
    contenido_final_renderizado: string;
    firma_imagen?: string;
  }): Observable<FirmaConsentimiento> {
    return this.http.post<FirmaConsentimiento>(`${this.apiUrl}/consentimientos-firmas/`, data);
  }

  descargarConsentimientoPdf(firmaId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/consentimientos-firmas/${firmaId}/descargar_pdf/`, {
      responseType: 'blob'
    });
  }

  revocarConsentimiento(firmaId: string, motivo: string): Observable<{ mensaje: string; firma: FirmaConsentimiento }> {
    return this.http.post<{ mensaje: string; firma: FirmaConsentimiento }>(
      `${this.apiUrl}/consentimientos-firmas/${firmaId}/revocar/`,
      { motivo }
    );
  }

  // --------------------------------------------------------------------------
  // CU19: CIERRE DE CASO Y DERIVACIONES
  // --------------------------------------------------------------------------
  getDerivaciones(historiaId?: string): Observable<DerivacionCaso[]> {
    let params = new HttpParams();
    if (historiaId) params = params.set('historia_clinica', historiaId);
    return this.http.get<DerivacionCaso[]>(`${this.apiUrl}/derivaciones/`, { params });
  }

  crearDerivacion(data: {
    historia_clinica: string;
    tipo_cierre: string;
    especialidad_destino?: string;
    profesional_o_institucion_destino?: string;
    motivo_derivacion: string;
    resumen_evolucion: string;
    recomendaciones_tratamiento?: string;
    bloquear_citas_subsecuentes?: boolean;
  }): Observable<DerivacionCaso> {
    return this.http.post<DerivacionCaso>(`${this.apiUrl}/derivaciones/`, data);
  }

  descargarOrdenDerivacionPdf(derivacionId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/derivaciones/${derivacionId}/descargar_orden_pdf/`, {
      responseType: 'blob'
    });
  }

  // --------------------------------------------------------------------------
  // HU-35: AUDITORÍA Y DECISIÓN HUMANA DE IA
  // --------------------------------------------------------------------------
  registrarDecisionIA(data: DecisionIARequest): Observable<{ mensaje: string; auditoria: any }> {
    return this.http.post<{ mensaje: string; auditoria: any }>(
      `${this.apiUrl}/auditorias-ia/registrar_decision/`,
      data
    );
  }
}
