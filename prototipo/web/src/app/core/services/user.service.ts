import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Usuario } from '../models';
import { environment } from '../../../environments/environment';

/**
 * ═══════════════════════════════════════════════════════════════════════════
 * CU3: Gestionar Usuarios (HU-05)
 * Servicio Angular para comunicación con CTR_UsuarioService (Django REST)
 * Implementa los pasos 2 y 11 del diagrama de comunicación:
 *   Paso 2: POST /api/users/ + JWT Header (crear usuario)
 *   Paso 11: 201 Created {usuario_creado} (respuesta)
 * ═══════════════════════════════════════════════════════════════════════════
 */
@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = `${environment.apiUrl}/users`;

  constructor(private http: HttpClient) {}

  getAll(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(`${this.apiUrl}/`);
  }

  getById(id: string): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/${id}/`);
  }

  // --- CU3 Paso 2: POST /api/users/ + JWT Header ---
  create(data: any): Observable<Usuario> {
    return this.http.post<Usuario>(`${this.apiUrl}/`, data);
  }

  update(id: string, data: any): Observable<Usuario> {
    return this.http.patch<Usuario>(`${this.apiUrl}/${id}/`, data);
  }

  toggleStatus(id: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/${id}/alternar_estado/`, {});
  }

  delete(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}/`);
  }
}
