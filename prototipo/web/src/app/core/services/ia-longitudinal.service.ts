import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class IaLongitudinalService {
  private readonly apiUrl = `${environment.apiUrl}/clinica`;
  private readonly v1Url = `${environment.apiUrl}/v1/clinica`;

  constructor(private http: HttpClient) {}

  // CU23 / HU-49: Resumen Clínico Longitudinal IA (HITL)
  listarResumenesIA(pacienteId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/pacientes/${pacienteId}/resumenes-ia/`);
  }

  // CU23-paso 2: UI envía POST /api/v1/clinica/ia/resumen-longitudinal/ con filtro de fechas
  generarResumenIA(pacienteId: string, usarHf = true, fechaIni?: string, fechaFin?: string): Observable<any> {
    const payload: any = { paciente_id: pacienteId, usar_hf: usarHf };
    if (fechaIni) payload.fecha_ini = fechaIni;
    if (fechaFin) payload.fecha_fin = fechaFin;
    return this.http.post<any>(`${this.v1Url}/ia/resumen-longitudinal/`, payload);
  }

  // CU23-paso 18: Especialista edita y aprueba el borrador IA (HITL)
  aprobarResumenHITL(resumenId: string, texto_resumen: string): Observable<any> {
    return this.http.patch<any>(`${this.apiUrl}/resumenes-ia/${resumenId}/aprobar/`, { texto_resumen });
  }

  // CU23-paso 23: Descarga PDF firmado con hash SHA-256
  descargarResumenPdf(resumenId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/resumenes-ia/${resumenId}/pdf/`, { responseType: 'blob' });
  }

  // CU24 / HU-50 & HU-51: Motor y Consola de Alertas Prioritarias de Riesgo IA
  listarAlertasRiesgo(estado?: string, severidad?: string): Observable<{ resumen: any; alertas: any[] }> {
    let hp = new HttpParams();
    if (estado) hp = hp.set('estado', estado);
    if (severidad) hp = hp.set('severidad', severidad);
    return this.http.get<{ resumen: any; alertas: any[] }>(`${this.apiUrl}/alertas-riesgo/`, { params: hp });
  }

  // CU24-paso 2: Dispara el motor predictivo sobre historias activas
  evaluarAlertasRiesgo(pacienteId?: string, ventanaMeses = 3): Observable<any> {
    const body: any = { ventana_meses: ventanaMeses };
    if (pacienteId) body.paciente_id = pacienteId;
    return this.http.post<any>(`${this.v1Url}/ml/evaluar-riesgo/`, body);
  }

  // CU24-paso 14: Registra intervención o resolución clínica sobre alerta
  transicionarAlerta(alertaId: string, estado: string, nota_intervencion: string): Observable<any> {
    return this.http.patch<any>(`${this.v1Url}/ml/alertas/${alertaId}/intervenir/`, {
      estado,
      nota_intervencion,
    });
  }
}
