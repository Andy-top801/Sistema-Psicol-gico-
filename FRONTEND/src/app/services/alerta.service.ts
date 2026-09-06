import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { apiUrl, API } from '../core/api';
import { Paged, unwrap } from '../core/models/paged.model';

export interface AlertaPriorizacion {
  id: string;
  paciente: string;
  paciente_details?: {
    id: string;
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

@Injectable({ providedIn: 'root' })
export class AlertaService {
  private base = apiUrl(API.alertas);

  constructor(private http: HttpClient) {}

  getAlertas(): Observable<AlertaPriorizacion[]> {
    return this.http
      .get<AlertaPriorizacion[] | Paged<AlertaPriorizacion>>(this.base)
      .pipe(unwrap<AlertaPriorizacion>());
  }

  getAlerta(id: string): Observable<AlertaPriorizacion> {
    return this.http.get<AlertaPriorizacion>(`${this.base}${id}/`);
  }

  createAlerta(data: Partial<AlertaPriorizacion>): Observable<AlertaPriorizacion> {
    return this.http.post<AlertaPriorizacion>(this.base, data);
  }

  patchAlerta(
    id: string,
    data: Partial<AlertaPriorizacion>
  ): Observable<AlertaPriorizacion> {
    return this.http.patch<AlertaPriorizacion>(`${this.base}${id}/`, data);
  }

  /** Acción del backend: pasa la alerta a "en revisión". */
  revisarAlerta(id: string): Observable<AlertaPriorizacion> {
    return this.http.post<AlertaPriorizacion>(`${this.base}${id}/revisar/`, {});
  }

  /** Acción del backend: marca la alerta como resuelta con la acción tomada. */
  resolverAlerta(id: string, accionTomada: string): Observable<AlertaPriorizacion> {
    return this.http.post<AlertaPriorizacion>(`${this.base}${id}/resolver/`, {
      accion_tomada: accionTomada,
    });
  }
}
