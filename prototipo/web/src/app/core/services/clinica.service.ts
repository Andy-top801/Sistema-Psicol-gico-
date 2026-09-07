import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Especialidad, Psicologo, Disponibilidad, Paciente, CrearPsicologoDTO, CrearPacienteDTO } from '../models';
import { environment } from '../../../environments/environment';

/**
 * ═══════════════════════════════════════════════════════════════════════════
 * SERVICIO CLÍNICO - FRONTEND ANGULAR 17
 * Comunicación con el Backend Multi-Tenant para las entidades del módulo clínico:
 *   - Especialidades
 *   - Psicólogos y Disponibilidad Horaria (CU6 / CU8 - HU-11, HU-12)
 *   - Pacientes y Expedientes (CU7 - HU-13, HU-14)
 * ═══════════════════════════════════════════════════════════════════════════
 */
@Injectable({
  providedIn: 'root'
})
export class ClinicaService {
  private apiUrl = `${environment.apiUrl}/clinica`;

  constructor(private http: HttpClient) {}

  // --------------------------------------------------------------------------
  // ESPECIALIDADES
  // --------------------------------------------------------------------------
  getEspecialidades(): Observable<Especialidad[]> {
    return this.http.get<Especialidad[]>(`${this.apiUrl}/especialidades/`);
  }

  createEspecialidad(data: { nombre: string; descripcion?: string }): Observable<Especialidad> {
    return this.http.post<Especialidad>(`${this.apiUrl}/especialidades/`, data);
  }

  // --------------------------------------------------------------------------
  // PSICÓLOGOS Y DIRECTORIO
  // --------------------------------------------------------------------------
  getPsicologos(filtros?: { especialidad?: string; modalidad?: string; search?: string }): Observable<Psicologo[]> {
    let params = new HttpParams();
    if (filtros?.especialidad) params = params.set('especialidad', filtros.especialidad);
    if (filtros?.modalidad) params = params.set('modalidad', filtros.modalidad);
    if (filtros?.search) params = params.set('search', filtros.search);
    return this.http.get<any[]>(`${this.apiUrl}/psicologos/`, { params }).pipe(
      map(list => (list || []).map(p => ({
        ...p,
        usuario: p.usuario || p.usuario_datos || { nombre: 'Profesional', apellido: '', email: '' }
      })))
    );
  }

  getPsicologoById(id: string): Observable<Psicologo> {
    return this.http.get<any>(`${this.apiUrl}/psicologos/${id}/`).pipe(
      map(p => ({
        ...p,
        usuario: p.usuario || p.usuario_datos || { nombre: 'Profesional', apellido: '', email: '' }
      }))
    );
  }

  createPsicologo(data: CrearPsicologoDTO): Observable<Psicologo> {
    return this.http.post<Psicologo>(`${this.apiUrl}/psicologos/`, data);
  }

  updatePsicologo(id: string, data: Partial<CrearPsicologoDTO>): Observable<Psicologo> {
    return this.http.patch<Psicologo>(`${this.apiUrl}/psicologos/${id}/`, data);
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU6 / CU8: Gestión de Psicólogos y Disponibilidad (HU-11, HU-12)
   * Diagrama de Comunicación – Flujo de Disponibilidad Horaria Semanal
   * Participantes:
   *   Actor  → Administrador / Psicólogo
   *   IU     → IU_PerfilDisponibilidad (Angular 17)
   *   CTR    → CTR_PsicologoService (Django REST)
   *   CE     → CE_Psicologo_y_Horario (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  getDisponibilidad(psicologoId: string): Observable<Disponibilidad[]> {
    return this.http.get<Disponibilidad[]>(`${this.apiUrl}/psicologos/${psicologoId}/disponibilidad/`);
  }

  guardarDisponibilidad(psicologoId: string, franjas: Disponibilidad[]): Observable<{ mensaje: string; count: number; horarios: Disponibilidad[] }> {
    // --- Paso 1: Actor ingresa datos de perfil y horario semanal en IU_PerfilDisponibilidad ---
    // (Selección de días 0-6, hora_inicio, hora_fin y duración de bloque de 50 min)

    // --- Paso 2: POST /api/clinica/psicologos/{id}/disponibilidad/ + JWT (Bearer) + X-Tenant-ID ---
    // IU_PerfilDisponibilidad envía el arreglo de franjas horarias al controlador Django
    return this.http.post<{ mensaje: string; count: number; horarios: Disponibilidad[] }>(
      `${this.apiUrl}/psicologos/${psicologoId}/disponibilidad/`,
      { franjas }
    );

    // NOTA: Pasos 3 a 10 ocurren en el backend (CTR_PsicologoService ↔ CE_Psicologo_y_Horario):
    //   Paso 3: Validar JWT, TenantMiddleware y rol profesional
    //   Paso 4: Permisos y tenant verificados
    //   Paso 5: Validar consistencia de horas (inicio < fin) y no traslape en el mismo día
    //   Paso 6: Franjas horarias coherentes
    //   Paso 7: SELECT id FROM clinica_psicologo WHERE colegiado = ?
    //   Paso 8: Colegiatura no duplicada
    //   Paso 9: INSERT INTO clinica_disponibilidad (dia, inicio, fin, bloques)
    //   Paso 10: Registros de disponibilidad persistidos
    // --- Paso 11: 200 OK {mensaje, count, horarios} retornado a Angular ---
    // --- Paso 12: Notificar "Disponibilidad guardada correctamente" al Actor ---
  }

  // --------------------------------------------------------------------------
  // PACIENTES Y EXPEDIENTES CLÍNICOS
  // --------------------------------------------------------------------------
  getPacientes(search?: string): Observable<Paciente[]> {
    let params = new HttpParams();
    if (search) params = params.set('search', search);
    return this.http.get<any[]>(`${this.apiUrl}/pacientes/`, { params }).pipe(
      map(list => (list || []).map(p => ({
        ...p,
        usuario: p.usuario || p.usuario_datos || { nombre: 'Paciente', apellido: '', email: '' }
      })))
    );
  }

  getPacienteById(id: string): Observable<Paciente> {
    return this.http.get<any>(`${this.apiUrl}/pacientes/${id}/`).pipe(
      map(p => ({
        ...p,
        usuario: p.usuario || p.usuario_datos || { nombre: 'Paciente', apellido: '', email: '' }
      }))
    );
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU7: Gestión de Pacientes Web y Móvil (HU-13, HU-14)
   * Diagrama de Comunicación – Flujo de Alta de Expediente de Paciente
   * Participantes:
   *   Actor  → Paciente / Recepcionista / Administrador
   *   IU     → IU_RegistroPaciente (Angular / Flutter)
   *   CTR    → CTR_PacienteService (Django REST)
   *   CE     → CE_Paciente_y_Usuario (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  createPaciente(data: CrearPacienteDTO): Observable<Paciente> {
    // --- Paso 1: Actor ingresa datos personales en IU_RegistroPaciente ---
    // (CI, nombre, apellido, fecha de nacimiento, contacto emergencia y tutor legal si edad < 18)

    // --- Paso 2: POST /api/clinica/pacientes/ + Header X-Tenant-ID + Bearer JWT ---
    // IU_RegistroPaciente envía el payload estructurado a CTR_PacienteService
    return this.http.post<Paciente>(`${this.apiUrl}/pacientes/`, data);

    // NOTA: Pasos 3 a 8 ocurren en el backend (CTR_PacienteService ↔ CE_Paciente_y_Usuario):
    //   Paso 3: Validar unicidad de CI y correo en el tenant
    //   Paso 4: Documento no duplicado
    //   Paso 5: Validar minoría de edad (< 18 años) y presencia obligatoria de tutor responsable
    //   Paso 6: Datos de tutor correctos
    //   Paso 7: INSERT INTO clinica_paciente (expediente, ci, fecha_nac...)
    //   Paso 8: Expediente clínico registrado en esquema tenant
    // --- Paso 9: 201 Created {paciente_id, codigo_expediente} retornado a Angular ---
    // --- Paso 10: Confirmar "Expediente de paciente creado" en IU ---
  }

  updatePaciente(id: string, data: Partial<CrearPacienteDTO>): Observable<Paciente> {
    return this.http.patch<Paciente>(`${this.apiUrl}/pacientes/${id}/`, data);
  }
}
