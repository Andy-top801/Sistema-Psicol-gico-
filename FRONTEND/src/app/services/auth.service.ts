import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://sanamente.localhost:8000/api/users/auth';
  private tokenKey = 'sigepsi_token';

  constructor(private http: HttpClient) { }

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/login/`, { email, password }).pipe(
      tap((res: any) => {
        if (res.access) {
          localStorage.setItem(this.tokenKey, res.access);
        }
      })
    );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  requestPasswordReset(email: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/password-reset/request/`, { email });
  }

  confirmPasswordReset(token: string, newPassword: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/password-reset/confirm/`, {
      token,
      new_password: newPassword
    });
  }

  verifyPasswordResetCode(code: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/password-reset-verify/`, { code });
  }

  getAuthHeaders(): HttpHeaders {
    const token = this.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }
}
