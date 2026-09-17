// ==============================================================================
// MÓDULO: login.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_Login
// CASOS DE USO: CU2: Gestionar Inicio de Sesión y Autenticación (HU-01, HU-02)
// DESCRIPCIÓN: Componente Angular interactivo para captura de credenciales y selección de centro.
//              Envía petición de autenticación JWT y conmuta dinámicamente el tenant activo.
//              Implementa los pasos 1, 2, 9 y 10 del Diagrama de Comunicación BCE.
// ==============================================================================
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
    <div class="login-wrapper">
      <!-- Fondo decorativo con luces y atmósfera clínica moderna -->
      <div class="login-bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape-grid"></div>
      </div>

      <div class="login-split-card glass-panel">
        <!-- ════════ PANEL IZQUIERDO: Marca y Nuevas Suscripciones ════════ -->
        <div class="brand-panel">
          <div class="brand-panel-content">
            <div class="brand-header-area">
              <div class="brand-logo-badge">
                <i class="fa-solid fa-brain"></i>
              </div>
              <h1 class="brand-heading">SIGEPSI</h1>
              <p class="brand-subheading">Plataforma Clínica Multi-Tenant para Centros Psicológicos</p>
            </div>

            <!-- Viñetas de valor clínico -->
            <div class="brand-features-list">
              <div class="feature-item">
                <div class="feature-bullet"><i class="fa-solid fa-shield-halved"></i></div>
                <div class="feature-text">
                  <strong>Aislamiento Seguro</strong>
                  <span>Esquema PostgreSQL independiente por cada centro</span>
                </div>
              </div>
              <div class="feature-item">
                <div class="feature-bullet"><i class="fa-solid fa-notes-medical"></i></div>
                <div class="feature-text">
                  <strong>Expedientes Clínicos</strong>
                  <span>Historias clínicas digitales, notas SOAP y consentimientos</span>
                </div>
              </div>
              <div class="feature-item">
                <div class="feature-bullet"><i class="fa-solid fa-video"></i></div>
                <div class="feature-text">
                  <strong>Teleconsulta Integrada</strong>
                  <span>Videollamadas clínicas encriptadas con Jitsi Meet</span>
                </div>
              </div>
            </div>

            <!-- Bloque Destacado Lateral: Crea tu Cuenta -->
            <div class="subscribe-card-side">
              <div class="subscribe-card-header">
                <span class="subscribe-tag"><i class="fa-solid fa-sparkles"></i> NUEVOS CENTROS</span>
              </div>
              <h3 class="subscribe-card-title">¿Aún no tienes cuenta para tu centro?</h3>
              <p class="subscribe-card-text">
                Comienza a digitalizar tu consulta hoy mismo con nuestros planes SaaS flexibles.
              </p>
              <a routerLink="/landing" class="btn-side-subscribe">
                <i class="fa-solid fa-rocket"></i> Crea tu Cuenta — Elige tu Plan
              </a>
              <div class="subscribe-side-footer">
                <a routerLink="/landing" class="side-link-presentation">
                  <i class="fa-solid fa-globe"></i> Conoce más sobre la plataforma SIGEPSI
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- ════════ PANEL DERECHO: Formulario de Acceso ════════ -->
        <div class="form-panel">
          <div class="form-panel-header">
            <div class="login-access-badge">
              <i class="fa-solid fa-right-to-bracket"></i>
              <span>Accede ahora a la plataforma</span>
            </div>
            <h2 class="form-panel-title">Iniciar Sesión</h2>
            <p class="form-panel-subtitle">Ingresa tus credenciales para acceder a tu centro</p>
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
          <div class="demo-box mt-3">
            <p class="demo-title"><i class="fa-solid fa-key"></i> Cuentas de Demostración:</p>
            <div class="demo-chips">
              <button class="demo-chip" (click)="fillDemo('beto.caleb.delgado.rojas@gmail.com', 'Admin1234*', true, '')">
                SuperAdmin (Beto)
              </button>
              <button class="demo-chip" (click)="fillDemo('admin@centroesperanza.com', 'Admin1234*', false, 'centro_esperanza')">
                Admin Esperanza
              </button>
              <button class="demo-chip" (click)="fillDemo('carlos.mendoza@centroesperanza.com', 'Psicologo123*', false, 'centro_esperanza')">
                Psicólogo (Carlos)
              </button>
              <button class="demo-chip" (click)="fillDemo('recepcion@centroesperanza.com', 'Recep1234*', false, 'centro_esperanza')">
                Recepcionista
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    /* ═══════════ WRAPPER & BACKGROUND ═══════════ */
    .login-wrapper {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 32px 20px;
      background: radial-gradient(circle at 10% 20%, #eaf4ee 0%, #f4f7f5 45%, #e5ede8 100%);
      position: relative;
      overflow: hidden;
    }
    .login-bg-shapes {
      position: absolute;
      inset: 0;
      pointer-events: none;
    }
    .shape {
      position: absolute;
      border-radius: 50%;
      filter: blur(100px);
      opacity: 0.5;
    }
    .shape-1 {
      width: 450px;
      height: 450px;
      background: rgba(34, 160, 107, 0.22);
      top: -120px;
      left: -80px;
    }
    .shape-2 {
      width: 420px;
      height: 420px;
      background: rgba(25, 115, 78, 0.16);
      bottom: -100px;
      right: -80px;
    }
    .shape-grid {
      position: absolute;
      inset: 0;
      background-image: radial-gradient(rgba(25, 115, 78, 0.08) 1px, transparent 1px);
      background-size: 28px 28px;
      opacity: 0.6;
    }

    /* ═══════════ SPLIT CARD ═══════════ */
    .login-split-card {
      width: 100%;
      max-width: 1040px;
      background: #ffffff;
      border: 1px solid rgba(25, 115, 78, 0.15);
      border-radius: 24px;
      box-shadow: 0 20px 60px rgba(15, 41, 34, 0.08), 0 2px 10px rgba(15, 41, 34, 0.03);
      display: flex;
      overflow: hidden;
      position: relative;
      z-index: 2;
    }

    /* ═══════════ LEFT BRAND PANEL ═══════════ */
    .brand-panel {
      flex: 1.1;
      background: linear-gradient(150deg, #0e2921 0%, #153e32 55%, #0b221b 100%);
      color: #ffffff;
      padding: 44px 40px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      overflow: hidden;
    }
    .brand-panel::before {
      content: '';
      position: absolute;
      top: -100px;
      right: -100px;
      width: 260px;
      height: 260px;
      background: radial-gradient(circle, rgba(46, 196, 134, 0.25) 0%, transparent 70%);
      pointer-events: none;
    }
    .brand-panel-content {
      position: relative;
      z-index: 2;
      display: flex;
      flex-direction: column;
      height: 100%;
      justify-content: space-between;
    }
    .brand-header-area {
      margin-bottom: 28px;
    }
    .brand-logo-badge {
      width: 58px;
      height: 58px;
      background: linear-gradient(135deg, #19734e, #22a06b);
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.7rem;
      color: #ffffff;
      margin-bottom: 16px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }
    .brand-heading {
      font-size: 2.1rem;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: -0.5px;
      margin-bottom: 6px;
    }
    .brand-subheading {
      font-size: 0.92rem;
      color: #9cbab0;
      line-height: 1.5;
    }

    /* Features List */
    .brand-features-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin-bottom: 32px;
    }
    .feature-item {
      display: flex;
      align-items: flex-start;
      gap: 14px;
    }
    .feature-bullet {
      width: 32px;
      height: 32px;
      border-radius: 9px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #34d399;
      font-size: 0.85rem;
      flex-shrink: 0;
      margin-top: 2px;
    }
    .feature-text strong {
      display: block;
      font-size: 0.88rem;
      color: #ffffff;
      font-weight: 700;
    }
    .feature-text span {
      font-size: 0.80rem;
      color: #8dafa3;
      line-height: 1.4;
    }

    /* Side Subscription Card */
    .subscribe-card-side {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 16px;
      padding: 22px 20px;
      backdrop-filter: blur(8px);
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
    }
    .subscribe-tag {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.8px;
      color: #34d399;
      background: rgba(34, 160, 107, 0.2);
      padding: 3px 10px;
      border-radius: 20px;
      margin-bottom: 10px;
    }
    .subscribe-card-title {
      font-size: 1.02rem;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 6px;
    }
    .subscribe-card-text {
      font-size: 0.82rem;
      color: #9cbab0;
      line-height: 1.45;
      margin-bottom: 14px;
    }
    .btn-side-subscribe {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      width: 100%;
      padding: 12px 18px;
      background: linear-gradient(135deg, #19734e, #22a06b);
      color: #ffffff;
      font-weight: 700;
      font-size: 0.88rem;
      border-radius: 10px;
      text-decoration: none;
      box-shadow: 0 4px 16px rgba(25, 115, 78, 0.4);
      transition: all 0.25s ease;
    }
    .btn-side-subscribe:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 22px rgba(34, 160, 107, 0.5);
      color: #ffffff;
    }
    .subscribe-side-footer {
      margin-top: 10px;
      text-align: center;
    }
    .side-link-presentation {
      font-size: 0.77rem;
      color: #7ee7be;
      font-weight: 600;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: color 0.2s;
    }
    .side-link-presentation:hover {
      color: #ffffff;
      text-decoration: underline;
    }

    /* ═══════════ RIGHT FORM PANEL ═══════════ */
    .form-panel {
      flex: 1;
      padding: 44px 38px;
      background: #ffffff;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    .form-panel-header {
      margin-bottom: 20px;
    }
    .login-access-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      border-radius: 20px;
      background: rgba(25, 115, 78, 0.08);
      color: #19734e;
      font-size: 0.78rem;
      font-weight: 700;
      margin-bottom: 12px;
      border: 1px solid rgba(25, 115, 78, 0.16);
    }
    .form-panel-title {
      font-size: 1.55rem;
      font-weight: 800;
      color: #12271f;
      letter-spacing: -0.5px;
      margin-bottom: 4px;
    }
    .form-panel-subtitle {
      font-size: 0.85rem;
      color: #64748b;
    }

    .mode-toggle {
      display: flex;
      background: #f1f5f3;
      border: 1px solid #e2ece6;
      border-radius: 12px;
      padding: 4px;
      margin-bottom: 18px;
    }
    .toggle-btn {
      flex: 1;
      padding: 8px 12px;
      font-size: 0.84rem;
      font-weight: 600;
      color: #557164;
      background: transparent;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    .toggle-btn.active {
      background: #ffffff;
      color: #12271f;
      font-weight: 700;
      box-shadow: 0 2px 6px rgba(15, 41, 34, 0.08);
    }

    .form-group {
      margin-bottom: 16px;
    }
    .form-label {
      display: block;
      font-size: 0.82rem;
      font-weight: 600;
      color: #283e35;
      margin-bottom: 6px;
    }
    .form-select {
      width: 100%;
      padding: 10px 14px;
      border: 1px solid #d1ded6;
      border-radius: 10px;
      background: #ffffff;
      color: #12271f;
      font-size: 0.88rem;
      outline: none;
      transition: border-color 0.2s ease;
    }
    .form-select:focus {
      border-color: #19734e;
      box-shadow: 0 0 0 3px rgba(25, 115, 78, 0.12);
    }
    .input-icon-wrapper {
      position: relative;
      display: flex;
      align-items: center;
    }
    .input-icon {
      position: absolute;
      left: 14px;
      color: #7e998d;
      font-size: 0.95rem;
    }
    .form-control.with-icon {
      padding-left: 40px;
    }
    .form-control {
      width: 100%;
      padding: 10px 14px;
      border: 1px solid #d1ded6;
      border-radius: 10px;
      font-size: 0.88rem;
      color: #12271f;
      outline: none;
      transition: all 0.2s ease;
    }
    .form-control:focus {
      border-color: #19734e;
      box-shadow: 0 0 0 3px rgba(25, 115, 78, 0.12);
    }
    .btn-toggle-eye {
      position: absolute;
      right: 12px;
      background: transparent;
      border: none;
      color: #7e998d;
      cursor: pointer;
      padding: 4px;
    }

    .btn {
      border: none;
      cursor: pointer;
      font-family: inherit;
    }
    .btn-primary {
      background: linear-gradient(135deg, #19734e, #22a06b);
      color: white;
      font-weight: 700;
      font-size: 0.92rem;
      border-radius: 10px;
      transition: all 0.25s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 4px 14px rgba(25, 115, 78, 0.25);
    }
    .btn-primary:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(25, 115, 78, 0.35);
    }
    .btn-primary:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    .btn-block {
      width: 100%;
      padding: 12px;
      margin-top: 6px;
    }

    .link-small {
      font-size: 0.78rem;
      color: #19734e;
      text-decoration: none;
      font-weight: 500;
    }
    .link-small:hover {
      text-decoration: underline;
    }

    .alert-box {
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 0.84rem;
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 14px;
    }
    .alert-error {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #991b1b;
    }

    /* Demo Box */
    .demo-box {
      background: #f8faf9;
      border: 1px dashed #d1ded6;
      border-radius: 10px;
      padding: 12px;
      margin-top: 14px;
    }
    .demo-title {
      font-size: 0.74rem;
      font-weight: 700;
      color: #557164;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
    }
    .demo-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }
    .demo-chip {
      background: #ffffff;
      border: 1px solid #d1ded6;
      color: #3b564a;
      font-weight: 600;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 0.74rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .demo-chip:hover {
      background: #e6f5ed;
      color: #19734e;
      border-color: #c7e6d7;
    }

    .d-flex { display: flex; }
    .justify-content-between { justify-content: space-between; }
    .align-items-center { align-items: center; }
    .mb-0 { margin-bottom: 0; }
    .mb-1 { margin-bottom: 4px; }
    .mt-3 { margin-top: 14px; }

    /* ═══════════ RESPONSIVE ═══════════ */
    @media (max-width: 960px) {
      .login-split-card {
        flex-direction: column;
        max-width: 520px;
      }
      .brand-panel {
        padding: 32px 24px;
      }
      .brand-features-list {
        display: none;
      }
      .form-panel {
        padding: 32px 24px;
      }
    }
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

    // Validaciones síncronas en frontend (HU-01, HU-02)
    if (!this.isSuperAdminMode() && !this.selectedTenantSlug) {
      this.errorMessage.set('Debe seleccionar su centro psicológico para iniciar sesión.');
      return;
    }

    const emailTrim = this.email?.trim();
    if (!emailTrim || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailTrim)) {
      this.errorMessage.set('Ingrese un correo electrónico válido.');
      return;
    }

    if (!this.password) {
      this.errorMessage.set('Ingrese su contraseña.');
      return;
    }

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
        // --- Punto 7+8: Verificar si debe cambiar contraseña ---
        if (res.must_change_password) {
          this.router.navigate(['/force-password-change']);
          return;
        }
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
