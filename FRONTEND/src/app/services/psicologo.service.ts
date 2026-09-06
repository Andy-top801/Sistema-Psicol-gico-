import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { apiUrl, API } from '../core/api';
import { Paged, unwrap } from '../core/models/paged.model';

export interface Especialidad {
  id: string;
  name: string;
  description?: string;
}

export interface DisponibilidadSlot {
  id?: string;
  psicologo?: string;
  dia_semana: number; // 1 = Lunes … 7 = Domingo
  hora_inicio: string; // HH:MM:SS
  hora_fin: string; // HH:MM:SS
  activo?: boolean;
}

export interface Psicologo {
  id: string;
  usuario: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    phone?: string;
  };
  modalidad_atencion: 'presencial' | 'virtual' | 'mixta';
  activo: boolean;
  especialidades?: string[];
  especialidades_details?: Especialidad[];
  disponibilidades?: DisponibilidadSlot[];
  cargas_trabajo?: number;
}

@Injectable({ providedIn: 'root' })
export class PsicologoService {
  private psicologos = apiUrl(API.psicologos);
  private especialidadesUrl = apiUrl(API.especialidades);
  private disponibilidadesUrl = apiUrl(API.disponibilidades);

  constructor(private http: HttpClient) {}

  getPsicologos(): Observable<Psicologo[]> {
    return this.http
      .get<Psicologo[] | Paged<Psicologo>>(this.psicologos)
      .pipe(unwrap<Psicologo>());
  }

  getPsicologo(id: string): Observable<Psicologo> {
    return this.http.get<Psicologo>(`${this.psicologos}${id}/`);
  }

  createPsicologo(data: any): Observable<Psicologo> {
    return this.http.post<Psicologo>(this.psicologos, data);
  }

  updatePsicologo(id: string, data: any): Observable<Psicologo> {
    return this.http.put<Psicologo>(`${this.psicologos}${id}/`, data);
  }

  patchPsicologo(id: string, data: any): Observable<Psicologo> {
    return this.http.patch<Psicologo>(`${this.psicologos}${id}/`, data);
  }

  getEspecialidades(): Observable<Especialidad[]> {
    return this.http
      .get<Especialidad[] | Paged<Especialidad>>(this.especialidadesUrl)
      .pipe(unwrap<Especialidad>());
  }

  getDisponibilidades(psicologoId?: string): Observable<DisponibilidadSlot[]> {
    const url = psicologoId
      ? `${this.disponibilidadesUrl}?psicologo=${psicologoId}`
      : this.disponibilidadesUrl;
    return this.http
      .get<DisponibilidadSlot[] | Paged<DisponibilidadSlot>>(url)
      .pipe(unwrap<DisponibilidadSlot>());
  }

  createDisponibilidad(slot: DisponibilidadSlot): Observable<DisponibilidadSlot> {
    return this.http.post<DisponibilidadSlot>(this.disponibilidadesUrl, slot);
  }

  deleteDisponibilidad(id: string): Observable<any> {
    return this.http.delete(`${this.disponibilidadesUrl}${id}/`);
  }
}
