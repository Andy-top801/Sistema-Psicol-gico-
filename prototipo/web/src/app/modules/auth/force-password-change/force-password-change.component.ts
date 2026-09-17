// ==============================================================================
// MÓDULO: force-password-change.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_ForcePasswordChange
// PUNTO 7+8: Web/Móvil + Modelo SaaS en la nube
// DESCRIPCIÓN: Componente de cambio obligatorio de contraseña para usuarios
//              creados vía suscripción Stripe. Se muestra tras el primer login
//              cuando must_change_password = true.
// ==============================================================================
import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { SubscriptionService } from '../../../core/services/subscription.service';

@Component({
  selector: 'app-force-password-change',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="fpc-container">
      <div class="fpc-bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
      </div>

      <div class="fpc-card glass-panel">
        <div class="fpc-icon">
          <i class="fa-solid fa-shield-halved"></i>
        </div>
        <h2>Cambio de Contraseña Obligatorio</h2>
        <p class="fpc-subtitle">
          Tu cuenta fue creada con una contraseña temporal. Por seguridad, debes establecer una nueva contraseña antes de continuar.
        </p>

        <!-- Success Message -->
        <div *ngIf="successMessage()" class="alert-box alert-success">
          <i class="fa-solid fa-check-circle"></i>
          <span>{{ successMessage() }}</span>
        </div>

        <!-- Error Message -->
        <div *ngIf="errorMessage()" class="alert-box alert-error">
          <i class="fa-solid fa-triangle-exclamation"></i>
          <span>{{ errorMessage() }}</span>
        </div>

        <form (ngSubmit)="onSubmit()" *ngIf="!successMessage()">
          <!-- Current Password -->
          <div class="form-group">
            <label class="form-label">Contraseña Temporal Actual</label>
            <div class="input-wrapper">
              <i class="fa-solid fa-lock input-icon"></i>
              <input
                [type]="showCurrentPwd() ? 'text' : 'password'"
                class="form-control with-icon"
                [(ngModel)]="currentPassword"
                name="currentPassword"
                placeholder="Ingresa tu contraseña temporal"
                required
              >
              <button type="button" class="btn-eye" (click)="showCurrentPwd.set(!showCurrentPwd())">
                <i class="fa-solid" [class.fa-eye]="!showCurrentPwd()" [class.fa-eye-slash]="showCurrentPwd()"></i>
              </button>
            </div>
          </div>

          <!-- New Password -->
          <div class="form-group">
            <label class="form-label">Nueva Contraseña</label>
            <div class="input-wrapper">
              <i class="fa-solid fa-key input-icon"></i>
              <input
                [type]="showNewPwd() ? 'text' : 'password'"
                class="form-control with-icon"
                [(ngModel)]="newPassword"
                name="newPassword"
                placeholder="Mínimo 8 caracteres"
                required
                minlength="8"
              >
              <button type="button" class="btn-eye" (click)="showNewPwd.set(!showNewPwd())">
                <i class="fa-solid" [class.fa-eye]="!showNewPwd()" [class.fa-eye-slash]="showNewPwd()"></i>
              </button>
            </div>
            <!-- Password strength hints -->
            <div class="pwd-hints" *ngIf="newPassword">
              <span class="pwd-hint" [class.valid]="newPassword.length >= 8">
                <i class="fa-solid" [class.fa-check]="newPassword.length >= 8" [class.fa-xmark]="newPassword.length < 8"></i>
                Mínimo 8 caracteres
              </span>
              <span class="pwd-hint" [class.valid]="hasUppercase()">
                <i class="fa-solid" [class.fa-check]="hasUppercase()" [class.fa-xmark]="!hasUppercase()"></i>
                Una mayúscula
              </span>
              <span class="pwd-hint" [class.valid]="hasNumber()">
                <i class="fa-solid" [class.fa-check]="hasNumber()" [class.fa-xmark]="!hasNumber()"></i>
                Un número
              </span>
              <span class="pwd-hint" [class.valid]="hasSpecial()">
                <i class="fa-solid" [class.fa-check]="hasSpecial()" [class.fa-xmark]="!hasSpecial()"></i>
                Un carácter especial
              </span>
            </div>
          </div>

          <!-- Confirm Password -->
          <div class="form-group">
            <label class="form-label">Confirmar Nueva Contraseña</label>
            <div class="input-wrapper">
              <i class="fa-solid fa-key input-icon"></i>
              <input
                [type]="showConfirmPwd() ? 'text' : 'password'"
                class="form-control with-icon"
                [(ngModel)]="confirmPassword"
                name="confirmPassword"
                placeholder="Repite tu nueva contraseña"
                required
              >
              <button type="button" class="btn-eye" (click)="showConfirmPwd.set(!showConfirmPwd())">
                <i class="fa-solid" [class.fa-eye]="!showConfirmPwd()" [class.fa-eye-slash]="showConfirmPwd()"></i>
              </button>
            </div>
            <div class="pwd-hints" *ngIf="confirmPassword && newPassword !== confirmPassword">
              <span class="pwd-hint">
                <i class="fa-solid fa-xmark"></i>
                Las contraseñas no coinciden
              </span>
            </div>
          </div>

          <button type="submit" class="btn btn-primary btn-block" [disabled]="loading() || !isFormValid()">
            <i *ngIf="loading()" class="fa-solid fa-circle-notch fa-spin"></i>
            <span *ngIf="!loading()">
              <i class="fa-solid fa-check"></i> Cambiar Contraseña y Continuar
            </span>
            <span *ngIf="loading()">Actualizando...</span>
          </button>
        </form>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      --primary: #19734e;
      --primary-light: #22a06b;
      --primary-glow: rgba(25, 115, 78, 0.25);
      --bg-dark: #0a1628;
      --text-muted: #94a3b8;
      --border-glass: rgba(255,255,255,0.08);
    }

    .fpc-container {
      min-height: 100vh;
      display: flex; align-items: center; justify-content: center;
      background: var(--bg-dark);
      position: relative; overflow: hidden;
      padding: 24px;
    }
    .fpc-bg-shapes { position: absolute; inset: 0; pointer-events: none; }
    .shape { position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.3; }
    .shape-1 {
      width: 500px; height: 500px;
      background: var(--primary);
      top: -200px; left: -100px;
    }
    .shape-2 {
      width: 350px; height: 350px;
      background: #8b5cf6;
      bottom: -150px; right: -80px;
    }

    .fpc-card {
      max-width: 480px; width: 100%;
      background: rgba(15,26,48,0.9);
      border: 1px solid var(--border-glass);
      border-radius: 20px;
      padding: 40px 32px;
      text-align: center;
      position: relative; z-index: 2;
      animation: slideUp 0.5s ease-out;
    }
    .fpc-icon {
      width: 68px; height: 68px; border-radius: 18px;
      background: linear-gradient(135deg, #eab308, #f59e0b);
      display: flex; align-items: center; justify-content: center;
      font-size: 1.8rem; color: white;
      margin: 0 auto 20px;
      box-shadow: 0 4px 24px rgba(234,179,8,0.25);
    }
    .fpc-card h2 {
      font-size: 1.4rem; font-weight: 800; color: white; margin-bottom: 10px;
    }
    .fpc-subtitle {
      font-size: 0.9rem; color: var(--text-muted); line-height: 1.6;
      margin-bottom: 28px;
    }

    .form-group { margin-bottom: 20px; text-align: left; }
    .form-label {
      display: block; font-size: 0.85rem; font-weight: 600;
      color: var(--text-muted); margin-bottom: 6px;
    }
    .input-wrapper { position: relative; display: flex; align-items: center; }
    .input-icon {
      position: absolute; left: 14px; color: rgba(255,255,255,0.3); font-size: 0.9rem;
    }
    .form-control {
      width: 100%; padding: 12px 44px 12px 42px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 10px; color: white; font-size: 0.92rem;
      transition: all 0.3s ease; outline: none;
    }
    .form-control.with-icon { padding-left: 42px; }
    .form-control::placeholder { color: rgba(255,255,255,0.3); }
    .form-control:focus {
      border-color: var(--primary-light);
      box-shadow: 0 0 0 3px var(--primary-glow);
    }
    .btn-eye {
      position: absolute; right: 12px;
      background: transparent; border: none; color: rgba(255,255,255,0.4);
      cursor: pointer; padding: 4px;
    }
    .btn-eye:hover { color: white; }

    .pwd-hints {
      display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;
    }
    .pwd-hint {
      display: inline-flex; align-items: center; gap: 4px;
      font-size: 0.75rem; color: rgba(239,68,68,0.8);
      background: rgba(239,68,68,0.08);
      padding: 3px 8px; border-radius: 6px;
    }
    .pwd-hint.valid {
      color: var(--primary-light);
      background: rgba(34,160,107,0.1);
    }

    .btn { border: none; cursor: pointer; font-family: inherit; }
    .btn-primary {
      background: linear-gradient(135deg, var(--primary), var(--primary-light));
      color: white; font-weight: 700; font-size: 0.95rem;
      border-radius: 12px; transition: all 0.3s ease;
      display: flex; align-items: center; justify-content: center; gap: 8px;
      box-shadow: 0 4px 16px var(--primary-glow);
    }
    .btn-primary:hover:not(:disabled) {
      transform: translateY(-1px); box-shadow: 0 6px 24px var(--primary-glow);
    }
    .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
    .btn-block { width: 100%; padding: 14px; margin-top: 8px; }

    .alert-box {
      padding: 12px 16px; border-radius: 10px; font-size: 0.88rem;
      display: flex; align-items: center; gap: 10px; margin-bottom: 18px;
      text-align: left;
    }
    .alert-error {
      background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.3);
      color: #fca5a5;
    }
    .alert-success {
      background: rgba(34,160,107,0.12); border: 1px solid rgba(34,160,107,0.3);
      color: #86efac;
    }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `]
})
export class ForcePasswordChangeComponent {
  currentPassword = '';
  newPassword = '';
  confirmPassword = '';
  loading = signal(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);
  showCurrentPwd = signal(false);
  showNewPwd = signal(false);
  showConfirmPwd = signal(false);

  constructor(
    private subscriptionService: SubscriptionService,
    private router: Router,
  ) {}

  hasUppercase(): boolean { return /[A-Z]/.test(this.newPassword); }
  hasNumber(): boolean { return /[0-9]/.test(this.newPassword); }
  hasSpecial(): boolean { return /[^A-Za-z0-9]/.test(this.newPassword); }

  isFormValid(): boolean {
    return (
      this.currentPassword.length > 0 &&
      this.newPassword.length >= 8 &&
      this.hasUppercase() &&
      this.hasNumber() &&
      this.hasSpecial() &&
      this.newPassword === this.confirmPassword
    );
  }

  onSubmit() {
    this.errorMessage.set(null);

    if (!this.isFormValid()) {
      this.errorMessage.set('Por favor, completa todos los campos y cumple los requisitos de la contraseña.');
      return;
    }

    this.loading.set(true);

    this.subscriptionService.forceChangePassword({
      current_password: this.currentPassword,
      new_password: this.newPassword,
      new_password_confirm: this.confirmPassword,
    }).subscribe({
      next: () => {
        this.loading.set(false);
        this.successMessage.set('¡Contraseña actualizada exitosamente! Redirigiendo al dashboard...');
        setTimeout(() => {
          this.router.navigate(['/dashboard']);
        }, 2000);
      },
      error: (err) => {
        this.loading.set(false);
        const msg = err.error?.error || err.error?.detail || 'Error al cambiar la contraseña. Verifica tu contraseña actual.';
        this.errorMessage.set(msg);
      }
    });
  }
}
