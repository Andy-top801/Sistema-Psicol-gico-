import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

export interface Paciente {
  id: string;
  usuario: {
    id: number;
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
  citas_count?: number;
}

@Injectable({
  providedIn: 'root'
})
export class PacienteService {
  private apiUrl = 'http://localhost:8000/api/users/pacientes/';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  getPacientes(): Observable<Paciente[]> {
    return this.http.get<Paciente[]>(this.apiUrl, {
      headers: this.authService.getAuthHeaders()
    });
  }

  getPaciente(id: string): Observable<Paciente> {
    return this.http.get<Paciente>(`${this.apiUrl}${id}/`, {
      headers: this.authService.getAuthHeaders()
    });
  }

  createPaciente(data: any): Observable<Paciente> {
    return this.http.post<Paciente>(this.apiUrl, data, {
      headers: this.authService.getAuthHeaders()
    });
  }

  updatePaciente(id: string, data: any): Observable<Paciente> {
    return this.http.put<Paciente>(`${this.apiUrl}${id}/`, data, {
      headers: this.authService.getAuthHeaders()
    });
  }

  deletePaciente(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}${id}/`, {
      headers: this.authService.getAuthHeaders()
    });
  }
}
