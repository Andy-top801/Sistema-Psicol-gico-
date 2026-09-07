import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { AuthResponse, Usuario, Tenant } from '../models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;

  // Signals para estado reactivo moderno
  currentUser = signal<Usuario | null>(null);
  currentTenant = signal<Tenant | null>(null);
  accessToken = signal<string | null>(localStorage.getItem('sigepsi_access'));
  refreshToken = signal<string | null>(localStorage.getItem('sigepsi_refresh'));

  isAuthenticated = computed(() => !!this.accessToken());
  isSuperAdmin = computed(() => {
    const user = this.currentUser();
    return user?.is_superuser || user?.rol?.nombre === 'SuperAdmin' || localStorage.getItem('sigepsi_rol') === 'SuperAdmin';
  });
  isAdminCentro = computed(() => {
    const user = this.currentUser();
    const rolName = (user?.rol?.nombre || localStorage.getItem('sigepsi_rol') || '').toLowerCase();
    return rolName.includes('admin') || rolName.includes('coordinador') || !!user?.is_superuser;
  });

  constructor(private http: HttpClient) {
    const savedUser = localStorage.getItem('sigepsi_user');
    if (savedUser) {
      try {
        this.currentUser.set(JSON.parse(savedUser));
      } catch (e) {}
    }
    const savedTenant = localStorage.getItem('sigepsi_tenant');
    if (savedTenant) {
      try {
        this.currentTenant.set(JSON.parse(savedTenant));
      } catch (e) {}
    }
  }

  setTenant(tenant: Tenant | null) {
    this.currentTenant.set(tenant);
    if (tenant) {
      localStorage.setItem('sigepsi_tenant', JSON.stringify(tenant));
    } else {
      localStorage.removeItem('sigepsi_tenant');
    }
  }

  clearTenant() {
    this.currentTenant.set(null);
    localStorage.removeItem('sigepsi_tenant');
  }

  isInTenantContext = computed(() => {
    const tenant = this.currentTenant();
    return !!tenant && tenant.schema_name !== 'public';
  });

  getTenantId(): string | undefined {
    return this.currentTenant()?.slug || this.currentTenant()?.id || undefined;
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU2: Gestionar Inicio de Sesión y Autenticación (HU-01, HU-02)
   * Diagrama de Comunicación – Flujo de Login (Servicio Angular)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  login(credentials: { email: string; password: string; tenant?: string }): Observable<AuthResponse> {
    // --- Paso 2: POST /api/auth/login/ ---
    // IU_Login envía credenciales (email, password, tenant) al CTR_AuthService
    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/login/`, credentials).pipe(
      tap((res: AuthResponse) => {
        // --- Paso 9: 200 OK (access_token, refresh_token, usuario, rol) ---
        // Se reciben y almacenan los tokens JWT y datos del usuario autenticado
        this.accessToken.set(res.access);
        this.refreshToken.set(res.refresh);
        this.currentUser.set(res.usuario);

        if (res.tenant) {
          this.setTenant(res.tenant);
        }

        localStorage.setItem('sigepsi_access', res.access);
        localStorage.setItem('sigepsi_refresh', res.refresh);
        localStorage.setItem('sigepsi_user', JSON.stringify(res.usuario));
        localStorage.setItem('sigepsi_rol', res.rol);
      })
    );
  }

  register(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/register/`, data);
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU2 (Logout): Cierre de Sesión Seguro (HU-09)
   * Diagrama de Comunicación – Flujo de Logout
   * Participantes:
   *   Actor  → Usuario Autenticado (Todos los roles)
   *   IU     → IU_Navbar (Angular / Móvil)
   *   CTR    → CTR_AuthLogout (Django REST)
   *   CE     → CE_TokenBlacklist (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  logout(): Observable<any> {
    const refresh = this.refreshToken();
    // --- Paso 2: POST /api/auth/logout/ {refresh} + Bearer JWT ---
    // IU_Navbar envía el refresh token al CTR_AuthLogout para invalidarlo
    return this.http.post(`${this.apiUrl}/auth/logout/`, { refresh }).pipe(
      // --- Paso 7: 200 OK {"mensaje": "Sesión cerrada"} ---
      // CTR_AuthLogout confirma el cierre de sesión
      tap(() => this.clearSession())
    );
    // NOTA: Los pasos 3-6 ocurren en el backend (CTR_AuthLogout ↔ CE_TokenBlacklist):
    //   Paso 3: Validar token y autenticación de usuario
    //   Paso 4: Refresh token válido
    //   Paso 5: INSERT INTO token_blacklist (token, fecha)
    //   Paso 6: Token revocado en lista negra
  }

  clearSession() {
    this.accessToken.set(null);
    this.refreshToken.set(null);
    this.currentUser.set(null);
    localStorage.removeItem('sigepsi_access');
    localStorage.removeItem('sigepsi_refresh');
    localStorage.removeItem('sigepsi_user');
    localStorage.removeItem('sigepsi_rol');
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU27: Recuperar Contraseña y Credenciales (HU-10)
   * Diagrama de Comunicación – Flujo de Recuperación (Solicitud de Token)
   * Participantes:
   *   Actor  → Usuario (Todos los roles)
   *   IU     → IU_RecuperarPassword (Angular)
   *   CTR    → CTR_PasswordReset (Django REST)
   *   CE     → CE_Usuario_y_Token (PostgreSQL)
   *   SRV    → SRV_ServicioCorreo (SMTP / SendGrid)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  requestPasswordReset(email: string): Observable<any> {
    // --- Paso 2: POST /api/auth/password-reset/ {email} ---
    // IU_RecuperarPassword envía el email al CTR_PasswordReset
    return this.http.post(`${this.apiUrl}/auth/password-reset/`, { email });
    // --- Paso 7: 200 OK (Enlace enviado si existe) ---
    // NOTA: Los pasos 3-6 y 5.1-5.2 ocurren en el backend:
    //   Paso 3: SELECT usuario WHERE email = ? AND activo = true
    //   Paso 4: Usuario encontrado
    //   Paso 5: INSERT INTO accounts_tokenrecuperacion (token, exp=24h)
    //   Paso 5.1: send_mail(email, reset_link)
    //   Paso 5.2: Correo enviado
    //   Paso 6: Token generado
  }

  confirmPasswordReset(payload: { token: string; password: string; password_confirm: string }): Observable<any> {
    // --- Paso 10: POST /api/auth/password-reset-confirm/ {token, password} ---
    // IU_RecuperarPassword envía el token y nueva password al CTR_PasswordReset
    return this.http.post(`${this.apiUrl}/auth/password-reset-confirm/`, payload);
    // --- Paso 15: 200 OK (Contraseña actualizada) ---
    // NOTA: Los pasos 11-14 ocurren en el backend:
    //   Paso 11: Validar token (vigente y usado = false)
    //   Paso 12: Token verificado
    //   Paso 13: UPDATE usuario SET password = ? ; token.usado = true
    //   Paso 14: Credenciales actualizadas
  }

  getProfile(): Observable<any> {
    return this.http.get(`${this.apiUrl}/auth/me/`);
  }
}
