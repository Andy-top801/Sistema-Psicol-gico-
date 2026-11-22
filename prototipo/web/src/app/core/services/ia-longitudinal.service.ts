import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class IaLongitudinalService {
  private readonly apiUrl = `${environment.apiUrl}/clinica`;

  constructor(private http: HttpClient) {}

  // HU-49: Resumen Clínico Longitudinal IA (HITL)
  listarResumenesIA(pacienteId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/pacientes/${pacienteId}/resumenes-ia/`);
  }

  generarResumenIA(pacienteId: string, usarHf = true): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/pacientes/${pacienteId}/resumenes-ia/`, { usar_hf: usarHf });
  }

  aprobarResumenHITL(resumenId: string, texto_resumen: string): Observable<any> {
    return this.http.patch<any>(`${this.apiUrl}/resumenes-ia/${resumenId}/aprobar/`, { texto_resumen });
  }

  descargarResumenPdf(resumenId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/resumenes-ia/${resumenId}/pdf/`, { responseType: 'blob' });
  }

  // HU-50 & HU-51: Motor y Consola de Alertas Prioritarias de Riesgo IA
  listarAlertasRiesgo(estado?: string, severidad?: string): Observable<{ resumen: any; alertas: any[] }> {
    let hp = new HttpParams();
    if (estado) hp = hp.set('estado', estado);
    if (severidad) hp = hp.set('severidad', severidad);
    return this.http.get<{ resumen: any; alertas: any[] }>(`${this.apiUrl}/alertas-riesgo/`, { params: hp });
  }

  evaluarAlertasRiesgo(pacienteId?: string): Observable<any> {
    const body = pacienteId ? { paciente_id: pacienteId } : {};
    return this.http.post<any>(`${this.apiUrl}/alertas-riesgo/evaluar/`, body);
  }

  transicionarAlerta(alertaId: string, estado: string, nota_intervencion: string): Observable<any> {
    return this.http.patch<any>(`${this.apiUrl}/alertas-riesgo/${alertaId}/transicion/`, {
      estado,
      nota_intervencion,
    });
  }
}
