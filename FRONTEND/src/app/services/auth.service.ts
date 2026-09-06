import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, tap, catchError, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private tokenKey = 'sigepsi_token';
  private userKey = 'sigepsi_user';

  constructor(private http: HttpClient) { }

  private getApiUrl(): string {
    const host = window.location.hostname;
    if (host === '127.0.0.1') {
      return 'http://127.0.0.1:8000/api/users/auth';
    }
    return 'http://localhost:8000/api/users/auth';
  }

  login(email: string, password: string): Observable<any> {
    const url = this.getApiUrl();
    return this.http.post(`${url}/login/`, { email, password }).pipe(
      tap((res: any) => {
        if (res.access) {
          localStorage.setItem(this.tokenKey, res.access);
        }
        localStorage.setItem(this.userKey, JSON.stringify({ email }));
      })
    );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  getUser(): any {
    const raw = localStorage.getItem(this.userKey);
    return raw ? JSON.parse(raw) : null;
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  requestPasswordReset(email: string): Observable<any> {
    const url = this.getApiUrl();
    return this.http.post(`${url}/password-reset/request/`, { email });
  }

  confirmPasswordReset(token: string, newPassword: string): Observable<any> {
    const url = this.getApiUrl();
    return this.http.post(`${url}/password-reset/confirm/`, {
      token,
      new_password: newPassword
    });
  }

  verifyPasswordResetCode(code: string): Observable<any> {
    const url = this.getApiUrl();
    return this.http.post(`${url}/password-reset-verify/`, { code });
  }

  getAuthHeaders(): HttpHeaders {
    const token = this.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }
}
