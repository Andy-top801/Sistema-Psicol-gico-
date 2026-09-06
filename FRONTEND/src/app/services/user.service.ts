import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = 'http://localhost:8000/api/users/usuarios/';

  constructor(private http: HttpClient, private authService: AuthService) { }

  getUsers(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl, { headers: this.authService.getAuthHeaders() });
  }

  getUser(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}${id}/`, { headers: this.authService.getAuthHeaders() });
  }

  createUser(user: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, user, { headers: this.authService.getAuthHeaders() });
  }

  updateUser(id: number, user: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}${id}/`, user, { headers: this.authService.getAuthHeaders() });
  }

  deleteUser(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}${id}/`, { headers: this.authService.getAuthHeaders() });
  }
}
