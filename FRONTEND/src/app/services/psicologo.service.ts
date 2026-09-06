import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

export interface Especialidad {
  id: number;
  nombre: string;
  descripcion?: string;
}

export interface DisponibilidadSlot {
  id?: number;
  psicologo?: number;
  dia_semana: number; // 1 = Lunes, 7 = Domingo
  hora_inicio: string; // HH:MM:SS
  hora_fin: string; // HH:MM:SS
  activo?: boolean;
}

export interface Psicologo {
  id: number;
  usuario: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    phone?: string;
  };
  numero_colegiado: string;
  biografia?: string;
  activo: boolean;
  especialidades?: Especialidad[];
  disponibilidades?: DisponibilidadSlot[];
  cargas_trabajo?: number;
}

@Injectable({
  providedIn: 'root'
})
export class PsicologoService {
  private apiUrl = 'http://localhost:8000/api/users';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  getPsicologos(): Observable<Psicologo[]> {
    return this.http.get<Psicologo[]>(`${this.apiUrl}/psicologos/`, {
      headers: this.authService.getAuthHeaders()
    });
  }

  getPsicologo(id: number): Observable<Psicologo> {
    return this.http.get<Psicologo>(`${this.apiUrl}/psicologos/${id}/`, {
      headers: this.authService.getAuthHeaders()
    });
  }

  createPsicologo(data: any): Observable<Psicologo> {
    return this.http.post<Psicologo>(`${this.apiUrl}/psicologos/`, data, {
      headers: this.authService.getAuthHeaders()
    });
  }

  updatePsicologo(id: number, data: any): Observable<Psicologo> {
    return this.http.put<Psicologo>(`${this.apiUrl}/psicologos/${id}/`, data, {
      headers: this.authService.getAuthHeaders()
    });
  }

  patchPsicologo(id: number, data: any): Observable<Psicologo> {
    return this.http.patch<Psicologo>(`${this.apiUrl}/psicologos/${id}/`, data, {
      headers: this.authService.getAuthHeaders()
    });
  }

  // Especialidades
  getEspecialidades(): Observable<Especialidad[]> {
    return this.http.get<Especialidad[]>(`${this.apiUrl}/especialidades/`, {
      headers: this.authService.getAuthHeaders()
    });
  }

  // Disponibilidad Slots (CU8)
  getDisponibilidades(psicologoId?: number): Observable<DisponibilidadSlot[]> {
    const url = psicologoId 
      ? `${this.apiUrl}/disponibilidades-psicologo/?psicologo=${psicologoId}`
      : `${this.apiUrl}/disponibilidades-psicologo/`;
    return this.http.get<DisponibilidadSlot[]>(url, {
      headers: this.authService.getAuthHeaders()
    });
  }

  createDisponibilidad(slot: DisponibilidadSlot): Observable<DisponibilidadSlot> {
    return this.http.post<DisponibilidadSlot>(`${this.apiUrl}/disponibilidades-psicologo/`, slot, {
      headers: this.authService.getAuthHeaders()
    });
  }

  deleteDisponibilidad(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/disponibilidades-psicologo/${id}/`, {
      headers: this.authService.getAuthHeaders()
    });
  }
}
