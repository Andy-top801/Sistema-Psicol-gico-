import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { switchMap, tap } from 'rxjs/operators';

import { apiUrl, API } from '../core/api';
import {
  AppRole,
  AppUser,
  ROLE_PRECEDENCE,
  normalizeRole,
} from '../core/models/user.model';

/** Nombres de rol conocidos (ya normalizados) + alias tolerantes. */
const ROLE_ALIASES: Record<string, AppRole> = {
  superadmin: 'superadmin',
  superadministrador: 'superadmin',
  adminplataforma: 'superadmin',
  admincentro: 'admincentro',
  administrador: 'admincentro',
  administradordelcentro: 'admincentro',
  admin: 'admincentro',
  coordinador: 'coordinador',
  coordinadorclinico: 'coordinador',
  psicologo: 'psicologo',
  psiquiatra: 'psicologo',
  recepcionista: 'recepcionista',
  paciente: 'paciente',
};

@Injectable({ providedIn: 'root' })
export class AuthService {
  private tokenKey = 'sigepsi_token';
  private refreshKey = 'sigepsi_refresh';
  private userKey = 'sigepsi_user';

  constructor(private http: HttpClient) {}

  // ── Autenticación ──────────────────────────────────────────────

  /** Login: guarda tokens y luego resuelve el perfil (`/me/`). */
  login(email: string, password: string): Observable<AppUser> {
    return this.http.post<any>(apiUrl(API.login), { email, password }).pipe(
      tap((res) => {
        if (res?.access) localStorage.setItem(this.tokenKey, res.access);
        if (res?.refresh) localStorage.setItem(this.refreshKey, res.refresh);
      }),
      switchMap(() => this.fetchMe())
    );
  }

  /** Obtiene el perfil del usuario autenticado y lo cachea. */
  fetchMe(): Observable<AppUser> {
    return this.http.get<AppUser>(apiUrl(API.me)).pipe(
      tap((user) => localStorage.setItem(this.userKey, JSON.stringify(user)))
    );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshKey);
    localStorage.removeItem(this.userKey);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  // ── Perfil / roles ─────────────────────────────────────────────

  currentUser(): AppUser | null {
    const raw = localStorage.getItem(this.userKey);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as AppUser;
    } catch {
      return null;
    }
  }

  /** Compat: algunas vistas viejas leen `getUser()`. */
  getUser(): AppUser | null {
    return this.currentUser();
  }

  displayName(): string {
    const u = this.currentUser();
    if (!u) return '';
    const full = `${u.first_name ?? ''} ${u.last_name ?? ''}`.trim();
    return full || u.email;
  }

  /** Roles del usuario, normalizados a `AppRole`. */
  roles(): AppRole[] {
    const u = this.currentUser();
    if (!u) return [];
    const set = new Set<AppRole>();
    for (const r of u.roles ?? []) {
      set.add(ROLE_ALIASES[normalizeRole(r)] ?? 'unknown');
    }
    if (u.is_superuser) set.add('superadmin');
    return [...set];
  }

  /** Rol de mayor precedencia que tiene el usuario. */
  primaryRole(): AppRole {
    const mine = this.roles();
    return ROLE_PRECEDENCE.find((r) => mine.includes(r)) ?? 'unknown';
  }

  hasAnyRole(roles: AppRole[]): boolean {
    const mine = this.roles();
    return roles.some((r) => mine.includes(r));
  }

  isPaciente(): boolean {
    return this.primaryRole() === 'paciente';
  }

  /** Ruta de inicio según el rol (paciente → portal, resto → panel). */
  homePathForRole(): string {
    return this.isPaciente() ? '/portal' : '/dashboard';
  }

  // ── Recuperación de contraseña ─────────────────────────────────

  requestPasswordReset(email: string): Observable<any> {
    return this.http.post(apiUrl(API.passwordResetRequest), { email });
  }

  confirmPasswordReset(token: string, newPassword: string): Observable<any> {
    return this.http.post(apiUrl(API.passwordResetConfirm), {
      token,
      new_password: newPassword,
    });
  }

  verifyPasswordResetCode(code: string): Observable<any> {
    return this.http.post(apiUrl(API.passwordResetVerify), { code });
  }

  // ── Compat (deprecado) ────────────────────────────────────────

  /**
   * @deprecated El `authInterceptor` adjunta el header automáticamente.
   * Se mantiene para no romper llamadas legacy que aún lo pasen.
   */
  getAuthHeaders(): HttpHeaders {
    const token = this.getToken();
    return new HttpHeaders(token ? { Authorization: `Bearer ${token}` } : {});
  }
}
