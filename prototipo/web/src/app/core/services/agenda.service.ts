import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Cita, SlotDisponible, TeleconsultaAccess, DashboardKPIs, AlertaClinica } from '../models';
import { environment } from '../../../environments/environment';

/**
 * ═══════════════════════════════════════════════════════════════════════════
 * SERVICIO DE AGENDA Y TELECONSULTA - FRONTEND ANGULAR 17
 * Comunicación con el Backend Multi-Tenant para:
 *   - Programación y Reserva Concurrente de Citas (CU11 - HU-15, HU-16, HU-17, HU-22)
 *   - Videoconferencias y Teleconsulta WebRTC Jitsi (CU13 - HU-18, HU-19)
 *   - Tablero Clínico y Alertas Tempranas (CU9 / CU10 - HU-20, HU-21)
 * ═══════════════════════════════════════════════════════════════════════════
 */
@Injectable({
  providedIn: 'root'
})
export class AgendaService {
  private apiUrl = `${environment.apiUrl}/agenda`;

  constructor(private http: HttpClient) {}

  // --------------------------------------------------------------------------
  // CITAS Y CALENDARIO
  // --------------------------------------------------------------------------
  getCitas(filtros?: { psicologo_id?: string; paciente_id?: string; fecha?: string; estado?: string }): Observable<Cita[]> {
    let params = new HttpParams();
    if (filtros?.psicologo_id) params = params.set('psicologo_id', filtros.psicologo_id);
    if (filtros?.paciente_id) params = params.set('paciente_id', filtros.paciente_id);
    if (filtros?.fecha) params = params.set('fecha', filtros.fecha);
    if (filtros?.estado) params = params.set('estado', filtros.estado);
    return this.http.get<Cita[]>(`${this.apiUrl}/citas/`, { params });
  }

  getCitaById(id: string): Observable<Cita> {
    return this.http.get<Cita>(`${this.apiUrl}/citas/${id}/`);
  }

  getSlotsDisponibles(psicologoId: string, fecha: string): Observable<SlotDisponible[]> {
    const params = new HttpParams()
      .set('psicologo_id', psicologoId)
      .set('fecha', fecha);
    return this.http.get<any>(`${this.apiUrl}/citas/slots-disponibles/`, { params }).pipe(
      map(res => Array.isArray(res) ? res : (res?.slots || []))
    );
  }

  getCalendarioEventos(filtros?: { psicologo_id?: string; start?: string; end?: string }): Observable<any[]> {
    let params = new HttpParams();
    if (filtros?.psicologo_id) params = params.set('psicologo_id', filtros.psicologo_id);
    if (filtros?.start) params = params.set('start', filtros.start);
    if (filtros?.end) params = params.set('end', filtros.end);
    return this.http.get<any[]>(`${this.apiUrl}/citas/calendario/`, { params });
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU11: Programación y Reserva de Citas (HU-15, HU-16, HU-17, HU-22)
   * Diagrama de Comunicación – Flujo de Reserva con Bloqueo Concurrente
   * Participantes:
   *   Actor  → Recepcionista / Paciente / Administrador
   *   IU     → IU_AgendaCitas (Angular 17)
   *   CTR    → CTR_CitaService (Django REST)
   *   CE     → CE_Cita_y_Disponibilidad (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  createCita(data: {
    paciente: string;
    psicologo: string;
    fecha: string;
    hora_inicio: string;
    hora_fin: string;
    modalidad: 'PRESENCIAL' | 'VIRTUAL';
    motivo_consulta?: string;
    costo?: number;
  }): Observable<Cita> {
    // --- Paso 1: Actor selecciona psicólogo, fecha, bloque y modalidad en IU_AgendaCitas ---
    // (Verificación visual previa de franjas horarias libres generadas por availability.py)

    // --- Paso 2: POST /api/agenda/citas/ {psicologo_id, fecha, bloque} + JWT + X-Tenant-ID ---
    // IU_AgendaCitas despacha la solicitud de agendamiento atómico
    return this.http.post<Cita>(`${this.apiUrl}/citas/`, data);

    // NOTA: Pasos 3 a 10 ocurren en el backend (CTR_CitaService ↔ CE_Cita_y_Disponibilidad):
    //   Paso 3: Iniciar transacción atómica y SELECT FOR UPDATE sobre la franja horaria
    //   Paso 4: Bloqueo pesimista concedido a la transacción concurrente
    //   Paso 5: Validar si horario está dentro de clinica_disponibilidad del psicólogo
    //   Paso 6: Horario dentro de jornada laboral acreditado
    //   Paso 7: SELECT COUNT(*) FROM agenda_cita WHERE solapada = true AND activa
    //   Paso 8: Cero colisiones detectadas (o rollback 409 si alguien ganó el slot)
    //   Paso 9: INSERT INTO agenda_cita (paciente_id, psicologo_id, fecha, hora...)
    //   Paso 10: Cita registrada y slot bloqueado exitosamente
    // --- Paso 11: 201 Created {cita_id, estado: "PROGRAMADA"} retornado a Angular ---
    // --- Paso 12: Desplegar comprobante de cita programada y refrescar calendario en IU ---
  }

  cancelarCita(citaId: string, motivo: string): Observable<{ mensaje: string; cita_id: string; estado: string }> {
    return this.http.post<{ mensaje: string; cita_id: string; estado: string }>(
      `${this.apiUrl}/citas/${citaId}/cancelar/`,
      { motivo }
    );
  }

  // --------------------------------------------------------------------------
  // TELECONSULTA JITSI MEET
  // --------------------------------------------------------------------------
  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU13: Teleconsulta y Videoconferencias Jitsi Meet (HU-18, HU-19)
   * Diagrama de Comunicación – Flujo de Acceso a Sala Virtual Segura
   * Participantes:
   *   Actor  → Paciente / Terapeuta
   *   IU     → IU_Teleconsulta (Angular 17)
   *   CTR    → CTR_TeleconsultaService (Django REST)
   *   CE     → CE_Teleconsulta_y_Cita (PostgreSQL)
   *   SRV    → SRV_JitsiServer (WebRTC Cluster meet.jit.si)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  getTeleconsultaAccess(citaId: string): Observable<TeleconsultaAccess> {
    // --- Paso 1: Actor hace clic en 'Iniciar / Unirse a Videoconsulta' en IU_Teleconsulta ---
    
    // --- Paso 2: GET /api/agenda/teleconsulta/{cita_id}/access/ + Bearer JWT + X-Tenant-ID ---
    // IU_Teleconsulta solicita las credenciales WebRTC seguras
    return this.http.get<TeleconsultaAccess>(`${this.apiUrl}/teleconsulta/${citaId}/access/`);

    // NOTA: Pasos 3 a 6 ocurren en el backend (CTR_TeleconsultaService ↔ CE_Teleconsulta_y_Cita):
    //   Paso 3: Validar que cita esté activa, en modalidad VIRTUAL y en ventana horaria válida
    //   Paso 4: Cita virtual vigente y participante autorizado
    //   Paso 5: Generar o recuperar sala_id en agenda_teleconsulta y emitir JWT con claims (moderador/invitado)
    //   Paso 6: Registro de sala listo en PostgreSQL
    // --- Paso 7: 200 OK {room_name, jwt_token, domain, is_moderator} retornado a Angular ---
    // --- Paso 8: IU_Teleconsulta inicializa JitsiMeetExternalAPI con WebRTC ---
    // --- Paso 9: Flujo bidireccional de audio y video activo (SRV_JitsiServer) ---
    // --- Paso 10: Cargar sala de video interactiva en pantalla con temporizador activo ---
  }

  finishTeleconsulta(citaId: string, duracionSegundos?: number): Observable<{ mensaje: string; duracion_segundos: number }> {
    return this.http.post<{ mensaje: string; duracion_segundos: number }>(
      `${this.apiUrl}/teleconsulta/${citaId}/finish/`,
      { duracion_segundos: duracionSegundos || 0 }
    );
  }

  // --------------------------------------------------------------------------
  // DASHBOARD CLÍNICO Y ALERTAS TEMPRANAS
  // --------------------------------------------------------------------------
  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU9 / CU10: Dashboard Clínico y Alertas Tempranas (HU-20, HU-21)
   * Diagrama de Comunicación – Consulta Agregada de Métricas y Alertas
   * Participantes:
   *   Actor  → Coordinador Clínico / Administrador
   *   IU     → IU_DashboardClinico (Angular 17)
   *   CTR    → CTR_DashboardService (Django REST)
   *   CE     → CE_Metricas_y_Alertas (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  getDashboardKPIs(periodo: string = 'mes'): Observable<DashboardKPIs> {
    // --- Paso 1: Actor accede al Dashboard Principal en IU_DashboardClinico ---

    // --- Paso 2: GET /api/agenda/dashboard/kpis/?periodo=mes + Bearer JWT + X-Tenant-ID ---
    // IU_DashboardClinico solicita agregaciones analíticas de la clínica
    const params = new HttpParams().set('periodo', periodo);
    return this.http.get<DashboardKPIs>(`${this.apiUrl}/dashboard/kpis/`, { params });

    // NOTA: Pasos 3 a 8 ocurren en el backend (CTR_DashboardService ↔ CE_Metricas_y_Alertas):
    //   Paso 3: Validar permisos de Coordinador / Administrador en tenant activo
    //   Paso 4: Acceso administrativo autorizado
    //   Paso 5: SELECT COUNT(citas), AVG(ocupacion) GROUP BY psicologo, estado
    //   Paso 6: Agregaciones estadísticas y cálculo de tasa de ausentismo calculadas
    //   Paso 7: SELECT * FROM agenda_alerta WHERE resuelta = false
    //   Paso 8: Listado de pacientes con 2+ inasistencias o riesgo de abandono
    // --- Paso 9: 200 OK {total_citas, ausentismo_pct, alertas_activas} retornado a Angular ---
    // --- Paso 10: Renderizar KPIs, gráficos de distribución y tabla de alertas en IU ---
  }

  getAlertas(): Observable<AlertaClinica[]> {
    return this.http.get<AlertaClinica[]>(`${this.apiUrl}/alertas/`);
  }

  resolverAlerta(alertaId: string): Observable<{ mensaje: string; id: string; resuelta: boolean }> {
    return this.http.post<{ mensaje: string; id: string; resuelta: boolean }>(
      `${this.apiUrl}/alertas/${alertaId}/resolver/`,
      {}
    );
  }
}
