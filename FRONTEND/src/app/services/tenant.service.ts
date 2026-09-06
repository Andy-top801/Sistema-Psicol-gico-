import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class TenantService {
  private apiUrl = 'http://localhost:8000/api/tenants/';

  constructor(private http: HttpClient, private authService: AuthService) { }

  getTenants(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl, { headers: this.authService.getAuthHeaders() });
  }

  getTenant(id: number | string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}${id}/`, { headers: this.authService.getAuthHeaders() });
  }

  createTenant(data: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, data, { headers: this.authService.getAuthHeaders() });
  }

  updateTenant(id: number | string, data: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}${id}/`, data, { headers: this.authService.getAuthHeaders() });
  }

  patchTenant(id: number | string, data: any): Observable<any> {
    return this.http.patch<any>(`${this.apiUrl}${id}/`, data, { headers: this.authService.getAuthHeaders() });
  }

  deleteTenant(id: number | string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}${id}/`, { headers: this.authService.getAuthHeaders() });
  }
}
