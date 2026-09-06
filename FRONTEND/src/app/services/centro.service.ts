import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';

export interface CentroConfig {
  id?: number;
  nombre: string;
  nif_rif: string;
  registro_sanitario: string;
  direccion: string;
  telefono: string;
  email: string;
  modalidad: string;
  linea_crisis: string;
  horarios_atencion?: { [key: string]: string };
  especialidades?: string[];
  branding?: {
    logo_url?: string;
    color_primario?: string;
  };
}

/**
 * Config del centro. Hoy persiste en localStorage (no hay endpoint dedicado de
 * config del tenant); cuando exista se migra a `apiUrl(API.tenants)`.
 */
@Injectable({ providedIn: 'root' })
export class CentroService {
  private storageKey = 'sigepsi_centro_config';

  private defaultConfig: CentroConfig = {
    nombre: 'Centro Psicológico',
    nif_rif: '',
    registro_sanitario: '',
    direccion: '',
    telefono: '',
    email: '',
    modalidad: 'Presencial',
    linea_crisis: '',
    horarios_atencion: {},
    especialidades: [],
  };

  getConfig(): Observable<CentroConfig> {
    try {
      const local = localStorage.getItem(this.storageKey);
      if (local) return of(JSON.parse(local) as CentroConfig);
    } catch {
      /* ignore */
    }
    return of(this.defaultConfig);
  }

  saveConfig(config: CentroConfig): Observable<CentroConfig> {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(config));
    } catch {
      /* ignore */
    }
    return of(config);
  }
}
