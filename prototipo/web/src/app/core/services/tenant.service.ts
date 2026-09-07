import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Tenant } from '../models';
import { environment } from '../../../environments/environment';

/**
 * ═══════════════════════════════════════════════════════════════════════════
 * CU1: Gestionar Centros Psicológicos y Configuración Multi-Tenant
 *      (HU-03, HU-04, HU-07, HU-08)
 * Servicio Angular para comunicación con CTR_TenantService (Django)
 * Implementa los pasos 2 y 9 del diagrama de comunicación:
 *   Paso 2: POST /api/tenants/ (enviar datos del nuevo centro)
 *   Paso 9: 201 Created (respuesta de creación exitosa)
 * ═══════════════════════════════════════════════════════════════════════════
 */
@Injectable({
  providedIn: 'root'
})
export class TenantService {
  private apiUrl = `${environment.apiUrl}/tenants`;

  constructor(private http: HttpClient) {}

  getPublicList(): Observable<Tenant[]> {
    return this.http.get<Tenant[]>(`${this.apiUrl}/public/`);
  }

  getAll(): Observable<Tenant[]> {
    return this.http.get<Tenant[]>(`${this.apiUrl}/`);
  }

  getById(id: string): Observable<Tenant> {
    return this.http.get<Tenant>(`${this.apiUrl}/${id}/`);
  }

  // --- CU1 Paso 2: POST /api/tenants/ ---
  // --- CU1 Paso 9: 201 Created ---
  create(data: any): Observable<Tenant> {
    return this.http.post<Tenant>(`${this.apiUrl}/`, data);
  }

  update(id: string, data: any): Observable<Tenant> {
    return this.http.put<Tenant>(`${this.apiUrl}/${id}/`, data);
  }

  suspender(id: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/${id}/suspender/`, {});
  }

  activar(id: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/${id}/activar/`, {});
  }

  delete(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}/`);
  }
}
