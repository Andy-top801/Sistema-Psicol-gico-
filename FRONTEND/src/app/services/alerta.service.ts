import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

export interface AlertaPriorizacion {
  id: string;
  paciente: string;
  paciente_details?: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    phone?: string;
  };
  tipo: 'inasistencia' | 'riesgo_abandono' | 'senal_riesgo' | 'estancamiento';
  tipo_display?: string;
  descripcion: string;
  estado: 'pendiente' | 'en_revision' | 'resuelta';
  estado_display?: string;
  accion_tomada?: string;
  created_at: string;
  updated_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class AlertaService {
  private apiUrl = 'http://localhost:8000/api/users/alertas/';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  getAlertas(): Observable<AlertaPriorizacion[]> {
    return this.http.get<AlertaPriorizacion[]>(this.apiUrl, {
      headers: this.authService.getAuthHeaders()
    });
  }

  getAlerta(id: string): Observable<AlertaPriorizacion> {
    return this.http.get<AlertaPriorizacion>(`${this.apiUrl}${id}/`, {
      headers: this.authService.getAuthHeaders()
    });
  }

  patchAlerta(id: string, data: Partial<AlertaPriorizacion>): Observable<AlertaPriorizacion> {
    return this.http.patch<AlertaPriorizacion>(`${this.apiUrl}${id}/`, data, {
      headers: this.authService.getAuthHeaders()
    });
  }

  createAlerta(data: any): Observable<AlertaPriorizacion> {
    return this.http.post<AlertaPriorizacion>(this.apiUrl, data, {
      headers: this.authService.getAuthHeaders()
    });
  }
}
