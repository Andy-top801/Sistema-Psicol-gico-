import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { AuthService } from './auth.service';

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

@Injectable({
  providedIn: 'root'
})
export class CentroService {
  private storageKey = 'sigepsi_centro_config';
  private apiUrl = 'http://localhost:8000/api/tenants/';

  private defaultConfig: CentroConfig = {
    nombre: 'Centro Psicográfico MenteSana & Bienestar Integral',
    nif_rif: 'J-90182743-2',
    registro_sanitario: 'RES-MED-2024-8891',
    direccion: 'Av. El Poblado #43A-12, Edificio Médica Suite 502, Medellín',
    telefono: '+57 (604) 444-9621',
    email: 'contacto@mentesanapsicologia.com',
    modalidad: 'Híbrida (Presencial + Telepsicología)',
    linea_crisis: '+57 (300) 911-2233',
    horarios_atencion: {
      'lunes_viernes': '08:00 - 19:00',
      'sabado': '08:00 - 13:00'
    },
    especialidades: [
      'Terapia Cognitivo-Conductual',
      'Neuropsicología Clínica',
      'Psicología Infantil y del Adolescente',
      'Terapia de Pareja y Familiar'
    ]
  };

  constructor(private http: HttpClient, private authService: AuthService) {}

  getConfig(): Observable<CentroConfig> {
    const local = localStorage.getItem(this.storageKey);
    if (local) {
      try {
        return of(JSON.parse(local));
      } catch (e) {
        // fallback
      }
    }
    return of(this.defaultConfig);
  }

  saveConfig(config: CentroConfig): Observable<CentroConfig> {
    localStorage.setItem(this.storageKey, JSON.stringify(config));
    return of(config);
  }
}
