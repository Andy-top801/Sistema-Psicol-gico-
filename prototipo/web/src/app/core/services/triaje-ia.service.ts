// ==============================================================================
// MÓDULO: triaje-ia.service.ts
// CAPA BCE: CONTROL (Client Service) — CTR_TriajeIAService
// CASOS DE USO: CU21 (Clasificación Asistida por IA), CU22 (Matching de Psicólogos)
// HISTORIAS DE USUARIO: HU-47, HU-48
// DESCRIPCIÓN: Servicio Angular 17 para consumo de endpoints REST de triaje clínico,
//              detección de crisis y sugerencias con validación humana obligatoria (HITL).
// ==============================================================================
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface FactoresMatching {
  afinidad_especialidad: number;
  disponibilidad_horaria: number;
  balance_carga: number;
  preferencia_modalidad: number;
}

export interface SugerenciaMatching {
  id: string;
  paciente: string;
  paciente_nombre?: string;
  psicologo_sugerido: string;
  psicologo_nombre?: string;
  numero_colegiado?: string;
  ranking_posicion: number;
  score_afinidad: number;
  factores_ponderacion: FactoresMatching;
  estado_decision: 'PENDIENTE_VALIDACION' | 'APROBADO' | 'DESCARTADO';
  justificacion_clinica?: string;
  fecha_decision?: string;
}

export interface ClasificacionIA {
  id: string;
  respuestapreconsulta: string;
  paciente_nombre?: string;
  categoria_principal: 'ANSIEDAD_FOBIAS' | 'DEPRESION_ANIMO' | 'PAREJA_FAMILIA' | 'INFANTO_JUVENIL' | 'DUELO_PERDIDA';
  confianza_score: number;
  nivel_severidad: 'LEVE' | 'MODERADO' | 'SEVERO' | 'CRITICA';
  alerta_crisis: boolean;
  palabras_clave_detectadas: string[];
  explicacion_heuristica: string;
  hash_trazabilidad_sha256: string;
  fecha_analisis: string;
}

@Injectable({
  providedIn: 'root'
})
export class TriajeIAService {
  private apiUrl = `${environment.apiUrl}/clinica`;

  constructor(private http: HttpClient) {}

  /**
   * Obtiene la lista de alertas prioritarias de riesgo vital y crisis autolítica (CU21 / HU-47).
   */
  getAlertasCrisis(): Observable<ClasificacionIA[]> {
    return this.http.get<ClasificacionIA[]>(`${this.apiUrl}/triaje/alertas/`);
  }

  /**
   * Obtiene el historial de clasificaciones emitidas por el motor de IA.
   */
  getClasificaciones(): Observable<ClasificacionIA[]> {
    return this.http.get<ClasificacionIA[]>(`${this.apiUrl}/clasificacion-ia/`);
  }

  /**
   * Ejecuta el pipeline de sanitización PII e inferencia de motivos sobre una respuesta de preconsulta.
   */
  clasificarIntake(intakeId: string): Observable<ClasificacionIA> {
    return this.http.post<ClasificacionIA>(`${this.apiUrl}/intake/${intakeId}/clasificar/`, {});
  }

  /**
   * Genera el Top 3 de sugerencias de emparejamiento asistido mediante fórmula multivariable (CU22 / HU-48).
   */
  generarMatching(pacienteId: string, especialidad?: string, modalidad?: string): Observable<SugerenciaMatching[]> {
    return this.http.post<SugerenciaMatching[]>(`${this.apiUrl}/triaje/${pacienteId}/sugerir-matching/`, {
      especialidad,
      modalidad
    });
  }

  /**
   * Aplica la decisión y validación humana obligatoria (HITL) para consolidar asignación de terapeuta.
   */
  asignarPsicologoHITL(
    sugerenciaId: string,
    pacienteId: string,
    psicologoId: string,
    justificacion: string
  ): Observable<{ mensaje: string; paciente_id: string; psicologo_asignado: string; estado_decision: string }> {
    return this.http.post<{ mensaje: string; paciente_id: string; psicologo_asignado: string; estado_decision: string }>(
      `${this.apiUrl}/triaje/asignar/`,
      {
        sugerencia_id: sugerenciaId,
        paciente_id: pacienteId,
        psicologo_id: psicologoId,
        justificacion_clinica: justificacion
      }
    );
  }
}
