import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class FinanzasService {
  private readonly apiUrl = `${environment.apiUrl}/finanzas`;
  private readonly reportesUrl = `${environment.apiUrl}/reportes`;

  constructor(private http: HttpClient) {}

  // HU-52: Cuentas y Cobros en Bs.
  getCuentas(params?: { solo_deudores?: boolean; q?: string; sync?: boolean }): Observable<any[]> {
    let hp = new HttpParams();
    if (params?.solo_deudores) hp = hp.set('solo_deudores', 'true');
    if (params?.q) hp = hp.set('q', params.q);
    if (params?.sync) hp = hp.set('sync', 'true');
    return this.http.get<any[]>(`${this.apiUrl}/cuentas/`, { params: hp });
  }

  getCuentaDetalle(pacienteId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/cuentas/${pacienteId}/`);
  }

  getPagos(params?: { paciente_id?: string; metodo_pago?: string; fecha_desde?: string; fecha_hasta?: string }): Observable<any[]> {
    let hp = new HttpParams();
    if (params?.paciente_id) hp = hp.set('paciente_id', params.paciente_id);
    if (params?.metodo_pago) hp = hp.set('metodo_pago', params.metodo_pago);
    if (params?.fecha_desde) hp = hp.set('fecha_desde', params.fecha_desde);
    if (params?.fecha_hasta) hp = hp.set('fecha_hasta', params.fecha_hasta);
    return this.http.get<any[]>(`${this.apiUrl}/pagos/`, { params: hp });
  }

  registrarPago(payload: {
    paciente_id: string;
    cita_id?: string | null;
    monto: number;
    metodo_pago: string;
    referencia_externa?: string;
    observaciones?: string;
    permitir_abono_adelantado?: boolean;
  }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/pagos/`, payload);
  }

  descargarReciboPdf(pagoId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/pagos/${pagoId}/recibo-pdf/`, { responseType: 'blob' });
  }

  // HU-52 (Ampliado): Extracto Histórico Tipo Banco (hasta 20 años)
  getExtractoBancario(params: {
    paciente_id?: string;
    fecha_desde?: string;
    fecha_hasta?: string;
    metodo_pago?: string;
    tipo?: string;
    page?: number;
    page_size?: number;
  }): Observable<any> {
    let hp = new HttpParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') hp = hp.set(k, String(v));
    });
    return this.http.get<any>(`${this.apiUrl}/extracto/`, { params: hp });
  }

  descargarExtracto(formato: 'pdf' | 'excel' | 'csv', params: Record<string, any>): Observable<Blob> {
    let hp = new HttpParams().set('formato', formato);
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') hp = hp.set(k, String(v));
    });
    return this.http.get(`${this.apiUrl}/extracto/`, { params: hp, responseType: 'blob' });
  }

  // HU-53: Dashboard Financiero y Gerencial Integral (>= 2 años)
  getDashboardFinanciero(params: {
    horizonte?: string;
    fecha_desde?: string;
    fecha_hasta?: string;
    psicologo_id?: string;
  } = {}): Observable<any> {
    let hp = new HttpParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') hp = hp.set(k, String(v));
    });
    return this.http.get<any>(`${this.apiUrl}/dashboard/`, { params: hp });
  }

  descargarReporte(fuente: string, formato: 'pdf' | 'excel' | 'csv'): Observable<Blob> {
    return this.http.get(`${this.reportesUrl}/${fuente}/export/${formato}/`, { responseType: 'blob' });
  }

  // HU-54: Liquidaciones de Honorarios a Psicólogos (Bs.)
  getLiquidaciones(params?: { psicologo_id?: string; estado?: string }): Observable<any[]> {
    let hp = new HttpParams();
    if (params?.psicologo_id) hp = hp.set('psicologo_id', params.psicologo_id);
    if (params?.estado) hp = hp.set('estado', params.estado);
    return this.http.get<any[]>(`${this.apiUrl}/liquidaciones/`, { params: hp });
  }

  previewLiquidacion(psicologo_id: string, fecha_inicio: string, fecha_fin: string, porcentaje_comision_centro = 30): Observable<any> {
    const hp = new HttpParams()
      .set('psicologo_id', psicologo_id)
      .set('fecha_inicio', fecha_inicio)
      .set('fecha_fin', fecha_fin)
      .set('porcentaje_comision_centro', String(porcentaje_comision_centro));
    return this.http.get<any>(`${this.apiUrl}/liquidaciones/preview/`, { params: hp });
  }

  generarLiquidacion(payload: {
    psicologo_id: string;
    fecha_inicio: string;
    fecha_fin: string;
    porcentaje_comision_centro: number;
    observaciones?: string;
  }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/liquidaciones/`, payload);
  }

  pagarLiquidacion(liquidacionId: string, referencia_bancaria: string): Observable<any> {
    return this.http.patch<any>(`${this.apiUrl}/liquidaciones/${liquidacionId}/pagar/`, { referencia_bancaria });
  }

  anularLiquidacion(liquidacionId: string, motivo: string): Observable<any> {
    return this.http.patch<any>(`${this.apiUrl}/liquidaciones/${liquidacionId}/anular/`, { motivo });
  }

  descargarBoletaPdf(liquidacionId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/liquidaciones/${liquidacionId}/boleta-pdf/`, { responseType: 'blob' });
  }

  triggerBlobDownload(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }
}
