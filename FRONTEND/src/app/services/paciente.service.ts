import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { apiUrl, API } from '../core/api';
import { Paged, unwrap } from '../core/models/paged.model';

export interface Paciente {
  id: string;
  usuario: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    phone?: string;
  };
  fecha_nacimiento?: string;
  direccion?: string;
  documento_identidad?: string;
  genero?: string;
  created_at?: string;
  updated_at?: string;
  citas_count?: number;
}

@Injectable({ providedIn: 'root' })
export class PacienteService {
  private base = apiUrl(API.pacientes);

  constructor(private http: HttpClient) {}

  getPacientes(): Observable<Paciente[]> {
    return this.http
      .get<Paciente[] | Paged<Paciente>>(this.base)
      .pipe(unwrap<Paciente>());
  }

  getPaciente(id: string): Observable<Paciente> {
    return this.http.get<Paciente>(`${this.base}${id}/`);
  }

  createPaciente(data: any): Observable<Paciente> {
    return this.http.post<Paciente>(this.base, data);
  }

  updatePaciente(id: string, data: any): Observable<Paciente> {
    return this.http.put<Paciente>(`${this.base}${id}/`, data);
  }

  patchPaciente(id: string, data: any): Observable<Paciente> {
    return this.http.patch<Paciente>(`${this.base}${id}/`, data);
  }

  deletePaciente(id: string): Observable<any> {
    return this.http.delete(`${this.base}${id}/`);
  }
}
