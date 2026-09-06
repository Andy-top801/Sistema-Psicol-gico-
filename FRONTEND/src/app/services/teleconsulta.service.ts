import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

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

@Injectable({
  providedIn: 'root'
})
export class TeleconsultaService {
  private apiUrl = 'http://localhost:8000/api/users/teleconsultas/';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  getTeleconsultas(): Observable<Teleconsulta[]> {
    return this.http.get<Teleconsulta[]>(this.apiUrl, {
      headers: this.authService.getAuthHeaders()
    });
  }

  getTeleconsulta(id: string): Observable<Teleconsulta> {
    return this.http.get<Teleconsulta>(`${this.apiUrl}${id}/`, {
      headers: this.authService.getAuthHeaders()
    });
  }

  createTeleconsulta(data: { cita: string }): Observable<Teleconsulta> {
    return this.http.post<Teleconsulta>(this.apiUrl, data, {
      headers: this.authService.getAuthHeaders()
    });
  }

  iniciarTeleconsulta(id: string): Observable<Teleconsulta> {
    return this.http.post<Teleconsulta>(`${this.apiUrl}${id}/iniciar/`, {}, {
      headers: this.authService.getAuthHeaders()
    });
  }

  finalizarTeleconsulta(id: string): Observable<Teleconsulta> {
    return this.http.post<Teleconsulta>(`${this.apiUrl}${id}/finalizar/`, {}, {
      headers: this.authService.getAuthHeaders()
    });
  }
}
