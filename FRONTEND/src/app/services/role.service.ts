import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class RoleService {
  private apiUrl = 'http://localhost:8000/api/users/roles/';
  private permisosUrl = 'http://localhost:8000/api/users/permisos/';

  constructor(private http: HttpClient, private authService: AuthService) { }

  getRoles(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl, { headers: this.authService.getAuthHeaders() });
  }

  getRole(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}${id}/`, { headers: this.authService.getAuthHeaders() });
  }

  createRole(role: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, role, { headers: this.authService.getAuthHeaders() });
  }

  getPermisos(): Observable<any[]> {
    return this.http.get<any[]>(this.permisosUrl, { headers: this.authService.getAuthHeaders() });
  }
}
