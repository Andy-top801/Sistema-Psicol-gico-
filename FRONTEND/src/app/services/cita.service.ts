import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

export interface Cita {
  id: string;
  paciente: string;
  paciente_details?: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    phone?: string;
  };
  psicologo: number;
  psicologo_details?: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
  };
  fecha_hora: string;
  duracion_minutos: number;
  estado: 'reservada' | 'confirmada' | 'cancelada' | 'reprogramada' | 'inasistencia';
  motivo?: string;
  created_at?: string;
  updated_at?: string;
}

@Injectable({
  providedIn: 'root'
})
export class CitaService {
  private apiUrl = 'http://localhost:8000/api/users/citas/';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  getCitas(params?: any): Observable<Cita[]> {
    return this.http.get<Cita[]>(this.apiUrl, {
      headers: this.authService.getAuthHeaders(),
      params
    });
  }

  getCita(id: string): Observable<Cita> {
    return this.http.get<Cita>(`${this.apiUrl}${id}/`, {
      headers: this.authService.getAuthHeaders()
    });
  }

  createCita(data: any): Observable<Cita> {
    return this.http.post<Cita>(this.apiUrl, data, {
      headers: this.authService.getAuthHeaders()
    });
  }

  updateCita(id: string, data: any): Observable<Cita> {
    return this.http.put<Cita>(`${this.apiUrl}${id}/`, data, {
      headers: this.authService.getAuthHeaders()
    });
  }

  patchCita(id: string, data: any): Observable<Cita> {
    return this.http.patch<Cita>(`${this.apiUrl}${id}/`, data, {
      headers: this.authService.getAuthHeaders()
    });
  }

  reprogramarCita(id: string, nuevaFechaHora: string): Observable<Cita> {
    return this.http.post<Cita>(`${this.apiUrl}${id}/reprogramar/`, {
      nueva_fecha_hora: nuevaFechaHora
    }, {
      headers: this.authService.getAuthHeaders()
    });
  }

  cancelarCita(id: string, motivo?: string): Observable<Cita> {
    return this.http.post<Cita>(`${this.apiUrl}${id}/cancelar/`, { motivo }, {
      headers: this.authService.getAuthHeaders()
    });
  }
}
