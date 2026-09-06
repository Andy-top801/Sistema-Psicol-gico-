import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { apiUrl } from '../core/api';

/** CU1 / HU-04 — configuración institucional del centro (uno por tenant). */
export interface CentroConfig {
  id?: string;
  nombre: string;
  nif_rif: string;
  registro_sanitario: string;
  direccion: string;
  telefono: string;
  email: string;
  modalidad: string;
  linea_crisis: string;
  horarios_atencion: { [key: string]: string };
  especialidades: string[];
  logo_url?: string;
  primary_color?: string;
  updated_at?: string;
}

@Injectable({ providedIn: 'root' })
export class CentroService {
  private url = apiUrl('users/centro-config/');

  constructor(private http: HttpClient) {}

  getConfig(): Observable<CentroConfig> {
    return this.http.get<CentroConfig>(this.url);
  }

  saveConfig(config: Partial<CentroConfig>): Observable<CentroConfig> {
    return this.http.put<CentroConfig>(this.url, config);
  }
}
