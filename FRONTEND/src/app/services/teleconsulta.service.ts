import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { apiUrl, API } from '../core/api';
import { Paged, unwrap } from '../core/models/paged.model';

export interface Teleconsulta {
  id: string;
  cita: string;
  room_name: string;
  enlace_psicologo: string;
  enlace_paciente: string;
  estado: 'programada' | 'en_curso' | 'finalizada' | 'cancelada';
  estado_display?: string;
  iniciada_at?: string;
  finalizada_at?: string;
  created_at: string;
  updated_at: string;
}

@Injectable({ providedIn: 'root' })
export class TeleconsultaService {
  private base = apiUrl(API.teleconsultas);

  constructor(private http: HttpClient) {}

  getTeleconsultas(): Observable<Teleconsulta[]> {
    return this.http
      .get<Teleconsulta[] | Paged<Teleconsulta>>(this.base)
      .pipe(unwrap<Teleconsulta>());
  }

  getTeleconsulta(id: string): Observable<Teleconsulta> {
    return this.http.get<Teleconsulta>(`${this.base}${id}/`);
  }

  createTeleconsulta(data: { cita: string }): Observable<Teleconsulta> {
    return this.http.post<Teleconsulta>(this.base, data);
  }

  iniciarTeleconsulta(id: string): Observable<Teleconsulta> {
    return this.http.post<Teleconsulta>(`${this.base}${id}/iniciar/`, {});
  }

  finalizarTeleconsulta(id: string): Observable<Teleconsulta> {
    return this.http.post<Teleconsulta>(`${this.base}${id}/finalizar/`, {});
  }

  cancelarTeleconsulta(id: string): Observable<Teleconsulta> {
    return this.http.post<Teleconsulta>(`${this.base}${id}/cancelar/`, {});
  }
}
