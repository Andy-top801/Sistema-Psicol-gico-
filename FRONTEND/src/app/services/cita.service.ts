import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { apiUrl, API } from '../core/api';
import { Paged, unwrap } from '../core/models/paged.model';

export interface CitaPersona {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export interface Cita {
  id: string;
  paciente: string;
  paciente_details?: CitaPersona;
  psicologo: string;
  psicologo_details?: CitaPersona;
  fecha_hora: string;
  duracion_minutos: number;
  modalidad?: 'presencial' | 'virtual';
  estado: 'reservada' | 'confirmada' | 'cancelada' | 'reprogramada' | 'inasistencia';
  motivo?: string;
  created_at?: string;
  updated_at?: string;
}

@Injectable({ providedIn: 'root' })
export class CitaService {
  private base = apiUrl(API.citas);

  constructor(private http: HttpClient) {}

  getCitas(params?: Record<string, string | number | boolean>): Observable<Cita[]> {
    let httpParams = new HttpParams();
    for (const [k, v] of Object.entries(params ?? {})) {
      if (v !== undefined && v !== null && v !== '') {
        httpParams = httpParams.set(k, String(v));
      }
    }
    return this.http
      .get<Cita[] | Paged<Cita>>(this.base, { params: httpParams })
      .pipe(unwrap<Cita>());
  }

  getCita(id: string): Observable<Cita> {
    return this.http.get<Cita>(`${this.base}${id}/`);
  }

  createCita(data: Partial<Cita>): Observable<Cita> {
    return this.http.post<Cita>(this.base, data);
  }

  updateCita(id: string, data: Partial<Cita>): Observable<Cita> {
    return this.http.put<Cita>(`${this.base}${id}/`, data);
  }

  patchCita(id: string, data: Partial<Cita>): Observable<Cita> {
    return this.http.patch<Cita>(`${this.base}${id}/`, data);
  }

  /** Acción del backend: no dispara la validación de disponibilidad. */
  confirmarCita(id: string): Observable<Cita> {
    return this.http.post<Cita>(`${this.base}${id}/confirmar/`, {});
  }

  /** Acción del backend: no dispara la validación de disponibilidad. */
  cancelarCita(id: string): Observable<Cita> {
    return this.http.post<Cita>(`${this.base}${id}/cancelar/`, {});
  }

  reprogramarCita(id: string, nuevaFechaHora: string): Observable<Cita> {
    return this.http.post<Cita>(`${this.base}${id}/reprogramar/`, {
      nueva_fecha_hora: nuevaFechaHora,
    });
  }
}
