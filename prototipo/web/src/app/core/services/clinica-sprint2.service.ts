import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
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
    return this.http.post<any>(`${this.apiUrl}/ia/preconsulta/analizar/`, { respuesta_id: respuestaId }).pipe(
      map((res: any) => ({
        analisis_id: res.auditoria_id,
        puntuacion_severidad: res.puntaje_severidad ?? res.puntuacion_severidad ?? 0,
        nivel_alerta: res.prioridad_sugerida || res.nivel_alerta || 'NORMAL',
        reglas_disparadas: (res.reglas_aplicadas || res.reglas_disparadas || []).map((r: any) => ({
          regla: r.codigo || r.regla || 'Regla Heurística',
          evidencia: r.criterio || r.evidencia || '',
          explicacion: r.explicacion || '',
          severidad: (r.codigo === 'REG-ALERTA-CRISIS' ? 'CRITICA' : (r.codigo === 'REG-MALESTAR-ALTO' ? 'ALTA' : (r.severidad || 'MEDIA'))),
          prioridad: r.prioridad || 1
        })),
        resumen_clinico_sugerido: res.resumen_generado || res.resumen_clinico_sugerido || '',
        preguntas_profundizacion_sugeridas: res.preguntas_profundizacion_sugeridas || [
          '¿Cuándo fue la primera vez que experimentó este nivel de malestar?',
          '¿Qué factores atenúan o intensifican los síntomas descritos?',
          '¿Cuenta con red de apoyo familiar o social inmediata?'
        ],
        disclaimer: res.etiqueta_obligatoria || 'Borrador IA — Requiere Revisión Profesional',
        sha256_verificacion: res.hash_prompt || res.sha256_verificacion || ''
      } as AnalisisIAResponse))
    );
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
    return this.http.get<CieItem[]>(`${this.apiUrl}/cie10/`, { params });
  }

  agregarDiagnostico(historiaId: string, data: {
    codigo_cie10: string;
    descripcion: string;
    tipo: 'PRINCIPAL' | 'SECUNDARIO' | 'PRESUNTIVO' | 'DESCARTADO';
    notas_criterio?: string;
  }): Observable<{ mensaje: string; diagnostico: any }> {
    const payload = {
      historia_clinica: historiaId,
      codigo_cie: data.codigo_cie10,
      descripcion: data.descripcion,
      tipo: data.tipo,
      observaciones: data.notas_criterio || ''
    };
    return this.http.post<any>(`${this.apiUrl}/diagnosticos-cie/`, payload);
  }

  removerDiagnostico(historiaId: string, diagnosticoId: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/diagnosticos-cie/${diagnosticoId}/`);
  }

  getTimeline(historiaId: string): Observable<{
    historia: { id: string; numero?: string; paciente?: string };
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
    return this.http.get<any>(`${this.apiUrl}/historias-clinicas/${historiaId}/timeline/`).pipe(
      map((res: any) => {
        if (Array.isArray(res)) {
          return {
            historia: { id: historiaId },
            total_eventos: res.length,
            timeline: res.map(item => ({
              id: item.id,
              tipo: item.tipo === 'NOTA_SOAP' ? 'SESION' : item.tipo,
              fecha: item.fecha,
              titulo: item.titulo,
              detalle: item.subjetivo || item.justificacion || item.titulo || '',
              alerta: item.estado_avance === 'RETROCESO_CRISIS' || item.alerta === true,
              estado: item.estado_avance || item.estado,
              profesional: item.profesional,
              metadata: item
            }))
          };
        }
        return res;
      })
    );
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
  }): Observable<{ mensaje: string; nota: NotaSesion; sha256: string; firmada?: boolean; nota_id?: string }> {
    return this.http.post<{ mensaje: string; nota: NotaSesion; sha256: string; firmada?: boolean; nota_id?: string }>(
      `${this.apiUrl}/notas-sesion/${notaId}/firmar/`,
      data
    );
  }

  agregarAdendaNotaSesion(notaId: string, textoAdenda: string): Observable<{ mensaje: string; nota: NotaSesion; adendas: string }> {
    return this.http.post<{ mensaje: string; nota: NotaSesion; adendas: string }>(
      `${this.apiUrl}/notas-sesion/${notaId}/adenda/`,
      { texto_adenda: textoAdenda }
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
    estado_avance?: string;
    justificacion?: string;
    acuerdos_pactados?: string;
    nota_sesion?: string;
    puntuacion_escala?: number;
    indicador_progreso?: string;
    alerta_crisis_recaida?: boolean;
    descripcion_crisis?: string;
    recomendacion_inmediata?: string;
    [key: string]: any;
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
  }): Observable<{ mensaje: string; estado: string; completada_porcentaje: number; tarea?: TareaTerapeutica }> {
    return this.http.post<{ mensaje: string; estado: string; completada_porcentaje: number; tarea?: TareaTerapeutica }>(
      `${this.apiUrl}/tareas/${tareaId}/evidencia/`,
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
    plantilla?: string;
    consentimiento?: string;
    paciente: string;
    contenido_final_renderizado?: string;
    firma_imagen?: string;
    firma_canvas_url?: string;
    hash_sha256?: string;
  }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/consentimientos/firmar/`, data);
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
    logros_alcanzados?: string;
    recomendaciones_mantenimiento?: string;
  }): Observable<DerivacionCaso> {
    const tipoMap: Record<string, string> = {
      DERIVACION_PSIQUIATRIA: 'EXTERNA_PSIQUIATRIA',
      DERIVACION_MEDICA: 'EXTERNA_NEUROLOGIA',
      ALTA_TERAPEUTICA: 'CIERRE_ALTA',
      ABANDONO: 'DESERCION',
      MUTUO_ACUERDO: 'MUTUO_ACUERDO'
    };
    const notas = [
      data.resumen_evolucion && `Evolución: ${data.resumen_evolucion}`,
      data.recomendaciones_tratamiento && `Recomendaciones: ${data.recomendaciones_tratamiento}`
    ].filter(Boolean).join('\n');
    const closure = ['ALTA_TERAPEUTICA', 'ABANDONO', 'MUTUO_ACUERDO'].includes(data.tipo_cierre);
    return this.http.post<DerivacionCaso>(`${this.apiUrl}/derivaciones/`, {
      historia_clinica: data.historia_clinica,
      tipo_derivacion: tipoMap[data.tipo_cierre] || data.tipo_cierre,
      motivo_clinico: closure ? data.motivo_derivacion : [data.motivo_derivacion, notas].filter(Boolean).join('\n\n'),
      logros_alcanzados: data.logros_alcanzados || '',
      recomendaciones_mantenimiento: data.recomendaciones_mantenimiento || '',
      sintomatologia_relevante: '',
      profesional_destino: data.especialidad_destino || '',
      institucion_destino: data.profesional_o_institucion_destino || ''
    });
  }

  reactivarHistoriaClinica(id: string, motivo_clinico: string): Observable<DerivacionCaso> {
    return this.http.post<DerivacionCaso>(`${this.apiUrl}/historias-clinicas/${id}/reactivar/`, { motivo_clinico });
  }

  descargarOrdenDerivacionPdf(derivacionId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/derivaciones/${derivacionId}/descargar-pdf/`, {
      responseType: 'blob'
    });
  }

  // --------------------------------------------------------------------------
  // HU-35: AUDITORÍA Y DECISIÓN HUMANA DE IA
  // --------------------------------------------------------------------------
  registrarDecisionIA(data: DecisionIARequest): Observable<{ mensaje: string; auditoria: any }> {
    const payload = {
      auditoria_id: data.analisis_id,
      decision: data.decision,
      observaciones: data.texto_final_utilizado || data.motivo_descarte || ''
    };
    return this.http.post<{ mensaje: string; auditoria: any }>(
      `${this.apiUrl}/ia/preconsulta/decision/`,
      payload
    );
  }
}
