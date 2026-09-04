import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Rol, Permiso } from '../models';

/**
 * ═══════════════════════════════════════════════════════════════════════════
 * CU4: Gestionar Roles y Permisos (HU-06)
 * Servicio Angular para comunicación con CTR_RolService (Django REST)
 * Implementa los pasos 2 y 11 del diagrama de comunicación:
 *   Paso 2: PUT /api/roles/{id}/ {permisos: [ids]} + JWT
 *   Paso 11: 200 OK {rol_actualizado}
 * ═══════════════════════════════════════════════════════════════════════════
 */
@Injectable({
  providedIn: 'root'
})
export class RoleService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  getRoles(): Observable<Rol[]> {
    return this.http.get<Rol[]>(`${this.apiUrl}/roles/`);
  }

  getPermisos(): Observable<Permiso[]> {
    return this.http.get<Permiso[]>(`${this.apiUrl}/permisos/`);
  }

  createRole(data: any): Observable<Rol> {
    return this.http.post<Rol>(`${this.apiUrl}/roles/`, data);
  }

  // --- CU4 Paso 2: PUT /api/roles/{id}/ {permisos: [ids]} + JWT ---
  // --- CU4 Paso 11: 200 OK {rol_actualizado} ---
  updateRole(id: number, data: any): Observable<Rol> {
    return this.http.put<Rol>(`${this.apiUrl}/roles/${id}/`, data);
  }

  deleteRole(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/roles/${id}/`);
  }
}
