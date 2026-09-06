import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { TenantService } from '../../../core/services/tenant.service';
import { Tenant } from '../../../core/models';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="login-container">
      <div class="login-card glass-panel">
        <!-- Logo & Header -->
        <div class="brand-header text-center">
          <div class="brand-icon">
            <i class="fa-solid fa-brain"></i>
          </div>
          <h1 class="brand-title">SIGEPSI</h1>
          <p class="brand-subtitle">Plataforma Clínica Multi-Tenant para Centros Psicológicos</p>
        </div>

        <!-- Mode Toggle -->
        <div class="mode-toggle">
          <button 
            type="button" 
            class="toggle-btn" 
            [class.active]="!isSuperAdminMode()" 
            (click)="setSuperAdminMode(false)">
            <i class="fa-solid fa-hospital"></i> Centro Psicológico
          </button>
          <button 
            type="button" 
            class="toggle-btn" 
            [class.active]="isSuperAdminMode()" 
            (click)="setSuperAdminMode(true)">
            <i class="fa-solid fa-shield-halved"></i> SuperAdmin
          </button>
        </div>

        <!-- Error Message -->
        <div *ngIf="errorMessage()" class="alert-box alert-error">
          <i class="fa-solid fa-triangle-exclamation"></i>
          <span>{{ errorMessage() }}</span>
        </div>

        <!-- Login Form -->
        <form (ngSubmit)="onSubmit()">
          <!-- Tenant Selector (if Centro mode) -->
          <div *ngIf="!isSuperAdminMode()" class="form-group">
            <label class="form-label">Centro / Gabinete</label>
            <select class="form-select" [(ngModel)]="selectedTenantSlug" name="tenant" required>
              <option value="" disabled selected>Selecciona tu centro psicológico...</option>
              <option *ngFor="let t of tenants()" [value]="t.slug">
                {{ t.nombre }} ({{ t.slug }})
              </option>
            </select>
          </div>

          <!-- Email -->
          <div class="form-group">
            <label class="form-label">Correo Electrónico</label>
            <div class="input-icon-wrapper">
              <i class="fa-solid fa-envelope input-icon"></i>
              <input 
                type="email" 
                class="form-control with-icon" 
                [(ngModel)]="email" 
                name="email" 
                placeholder="ejemplo@centro.com" 
                required>
            </div>
          </div>

          <!-- Password -->
          <div class="form-group">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <label class="form-label mb-0">Contraseña</label>
              <a routerLink="/password-reset" class="link-small">¿Olvidaste tu contraseña?</a>
            </div>
            <div class="input-icon-wrapper">
              <i class="fa-solid fa-lock input-icon"></i>
              <input 
                [type]="showPassword() ? 'text' : 'password'" 
                class="form-control with-icon" 
                [(ngModel)]="password" 
                name="password" 
                placeholder="••••••••" 
                required>
              <button type="button" class="btn-toggle-eye" (click)="toggleShowPassword()">
                <i class="fa-solid" [class.fa-eye]="!showPassword()" [class.fa-eye-slash]="showPassword()"></i>
              </button>
            </div>
          </div>

          <!-- Submit Button -->
          <button type="submit" class="btn btn-primary btn-block" [disabled]="loading()">
            <i *ngIf="loading()" class="fa-solid fa-circle-notch fa-spin"></i>
            <span *ngIf="!loading()">Iniciar Sesión</span>
            <span *ngIf="loading()">Validando credenciales...</span>
          </button>
        </form>

        <!-- Quick Demo Credentials Box -->
        <div class="demo-box mt-4">
          <p class="demo-title"><i class="fa-solid fa-key"></i> Cuentas de Demostración:</p>
          <div class="demo-chips">
            <button class="demo-chip" (click)="fillDemo('admin@sigepsi.com', 'Admin1234*', true, '')">
              SuperAdmin
            </button>
            <button class="demo-chip" (click)="fillDemo('admin@centroesperanza.com', 'Admin1234*', false, 'centro_esperanza')">
              Admin Esperanza
            </button>
            <button class="demo-chip" (click)="fillDemo('psicologo@centroesperanza.com', 'Psico1234*', false, 'centro_esperanza')">
              Psicólogo
            </button>
            <button class="demo-chip" (click)="fillDemo('recepcion@centroesperanza.com', 'Recep1234*', false, 'centro_esperanza')">
              Recepcionista
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .login-container {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .login-card {
      width: 100%;
      max-width: 480px;
      padding: 36px 32px;
    }
    .brand-icon {
      width: 64px;
      height: 64px;
      background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
      border-radius: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2rem;
      color: white;
      margin: 0 auto 16px;
      box-shadow: 0 8px 25px var(--primary-glow);
    }
    .brand-title {
      font-size: 1.8rem;
      font-weight: 800;
      letter-spacing: -0.5px;
      background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 4px;
    }
    .brand-subtitle {
      font-size: 0.88rem;
      color: var(--text-muted);
      margin-bottom: 24px;
    }
    .mode-toggle {
      display: flex;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border-glass);
      border-radius: 12px;
      padding: 4px;
      margin-bottom: 20px;
    }
    .toggle-btn {
      flex: 1;
      padding: 8px 12px;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-muted);
      background: transparent;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: var(--transition);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    .toggle-btn.active {
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-main);
      box-shadow: var(--shadow-sm);
    }
    .input-icon-wrapper {
      position: relative;
      display: flex;
      align-items: center;
    }
    .input-icon {
      position: absolute;
      left: 14px;
      color: var(--text-dim);
      font-size: 1rem;
    }
    .form-control.with-icon {
      padding-left: 42px;
    }
    .btn-toggle-eye {
      position: absolute;
      right: 14px;
      background: transparent;
      border: none;
      color: var(--text-dim);
      cursor: pointer;
    }
    .btn-block {
      width: 100%;
      padding: 12px;
      margin-top: 10px;
    }
    .alert-box {
      padding: 12px 16px;
      border-radius: 10px;
      font-size: 0.88rem;
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 18px;
    }
    .alert-error {
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid rgba(239, 68, 68, 0.3);
      color: #fca5a5;
    }
    .link-small {
      font-size: 0.8rem;
      color: var(--primary);
      text-decoration: none;
    }
    .link-small:hover { text-decoration: underline; }
    .demo-box {
      background: rgba(15, 23, 42, 0.6);
      border: 1px dashed var(--border-glass);
      border-radius: 12px;
      padding: 14px;
    }
    .demo-title {
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      margin-bottom: 8px;
    }
    .demo-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .demo-chip {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-glass);
      color: var(--text-muted);
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.78rem;
      cursor: pointer;
      transition: var(--transition);
    }
    .demo-chip:hover {
      background: var(--primary);
      color: white;
      border-color: var(--primary);
    }
    .text-center { text-align: center; }
    .d-flex { display: flex; }
    .justify-content-between { justify-content: space-between; }
    .align-items-center { align-items: center; }
    .mb-0 { margin-bottom: 0; }
    .mb-1 { margin-bottom: 4px; }
    .mt-4 { margin-top: 18px; }
  `]
})
export class LoginComponent implements OnInit {
  email = '';
  password = '';
  selectedTenantSlug = '';
  isSuperAdminMode = signal<boolean>(false);
  showPassword = signal<boolean>(false);
  loading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  tenants = signal<Tenant[]>([]);

  constructor(
    private authService: AuthService,
    private tenantService: TenantService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadTenants();
  }

  loadTenants() {
    this.tenantService.getPublicList().subscribe({
      next: (list: Tenant[]) => {
        this.tenants.set(list);
        if (list.length > 0) {
          this.selectedTenantSlug = list[0].slug;
        }
      },
      error: () => {}
    });
  }

  setSuperAdminMode(mode: boolean) {
    this.isSuperAdminMode.set(mode);
    this.errorMessage.set(null);
  }

  toggleShowPassword() {
    this.showPassword.update((v: boolean) => !v);
  }

  fillDemo(email: string, pass: string, isSuper: boolean, tenantSlug: string) {
    this.email = email;
    this.password = pass;
    this.isSuperAdminMode.set(isSuper);
    if (!isSuper && tenantSlug) {
      this.selectedTenantSlug = tenantSlug;
    }
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU2: Gestionar Inicio de Sesión y Autenticación (HU-01, HU-02)
   * Diagrama de Comunicación – Flujo de Login
   * Participantes:
   *   Actor  → Usuario (Todos los roles)
   *   IU     → IU_Login (Angular / Móvil)
   *   CTR    → CTR_AuthService (Django REST)
   *   CE     → CE_Usuario_y_Tenant (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  onSubmit() {
    this.errorMessage.set(null);
    this.loading.set(true);

    // --- Paso 1: Ingresar credenciales (email, password, tenant) ---
    // El Actor (Usuario) ingresa sus credenciales en el formulario IU_Login
    const tenant = this.isSuperAdminMode() ? 'public' : this.selectedTenantSlug;

    // Guardar contexto de tenant en el frontend
    if (!this.isSuperAdminMode()) {
      const tenantObj = this.tenants().find((t: Tenant) => t.slug === this.selectedTenantSlug);
      this.authService.setTenant(tenantObj || null);
    } else {
      this.authService.setTenant(null);
    }

    // --- Paso 2: POST /api/auth/login/ ---
    // IU_Login envía las credenciales al CTR_AuthService (Django REST)
    this.authService.login({
      email: this.email,
      password: this.password,
      tenant: tenant
    }).subscribe({
      // --- Paso 9: 200 OK (access_token, refresh_token, usuario, rol) ---
      // CTR_AuthService responde con tokens JWT y datos del usuario autenticado
      next: (res: any) => {
        this.loading.set(false);
        // --- Paso 10: Redirigir a Dashboard según rol ---
        // IU_Login redirige al Actor al Dashboard correspondiente a su rol
        this.router.navigate(['/dashboard']);
      },
      error: (err: any) => {
        this.loading.set(false);
        const detail = err.error?.non_field_errors?.[0] || err.error?.detail || err.error?.error || 'Credenciales inválidas o centro suspendido.';
        this.errorMessage.set(detail);
      }
    });
    // NOTA: Los pasos 3-8 ocurren en el backend (CTR_AuthService ↔ CE_Usuario_y_Tenant):
    //   Paso 3: Validar tenant y conmutar schema
    //   Paso 4: Esquema PostgreSQL activo
    //   Paso 5: SELECT usuario WHERE email = ? AND activo = true
    //   Paso 6: Retornar usuario y hash password
    //   Paso 7: Verificar password (PBKDF2) y generar JWT
    //   Paso 8: Tokens JWT generados (con claims)
  }
}
