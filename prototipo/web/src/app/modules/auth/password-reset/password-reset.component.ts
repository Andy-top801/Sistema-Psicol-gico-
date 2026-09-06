import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-password-reset',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="login-container">
      <div class="login-card glass-panel">
        <div class="brand-header text-center">
          <div class="brand-icon">
            <i class="fa-solid fa-key"></i>
          </div>
          <h1 class="brand-title">Recuperar Acceso</h1>
          <p class="brand-subtitle">Restablece tu contraseña mediante correo electrónico</p>
        </div>

        <!-- Step 1: Request Token -->
        <div *ngIf="step() === 1">
          <div *ngIf="message()" class="alert-box alert-success">
            <i class="fa-solid fa-circle-check"></i>
            <span>{{ message() }}</span>
          </div>
          <div *ngIf="errorMessage()" class="alert-box alert-error">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <span>{{ errorMessage() }}</span>
          </div>

          <form (ngSubmit)="onRequestToken()">
            <div class="form-group">
              <label class="form-label">Correo Electrónico Registrado</label>
              <input 
                type="email" 
                class="form-control" 
                [(ngModel)]="email" 
                name="email" 
                placeholder="ejemplo@centro.com" 
                required>
            </div>

            <button type="submit" class="btn btn-primary btn-block" [disabled]="loading()">
              <i *ngIf="loading()" class="fa-solid fa-circle-notch fa-spin"></i>
              <span *ngIf="!loading()">Enviar Enlace de Recuperación</span>
            </button>
          </form>

          <div *ngIf="tokenSent()" class="mt-3 text-center">
            <p class="text-muted text-sm">¿Ya recibiste el token por correo?</p>
            <button class="btn btn-secondary btn-block" (click)="goToStep2()">
              <i class="fa-solid fa-arrow-right"></i> Ingresar Token y Nueva Contraseña
            </button>
          </div>
        </div>

        <!-- Step 2: Confirm New Password -->
        <div *ngIf="step() === 2">
          <div *ngIf="successMessage()" class="alert-box alert-success">
            <i class="fa-solid fa-circle-check"></i>
            <span>{{ successMessage() }}</span>
          </div>
          <div *ngIf="errorMessage()" class="alert-box alert-error">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <span>{{ errorMessage() }}</span>
          </div>

          <form *ngIf="!successMessage()" (ngSubmit)="onConfirmReset()">
            <div class="form-group">
              <label class="form-label">Token de Recuperación (recibido por correo)</label>
              <input 
                type="text" 
                class="form-control font-mono" 
                [(ngModel)]="token" 
                name="token" 
                placeholder="Pega aquí el token que recibiste por correo"
                required>
            </div>

            <div class="form-group">
              <label class="form-label">Nueva Contraseña</label>
              <input 
                type="password" 
                class="form-control" 
                [(ngModel)]="newPassword" 
                name="newPassword" 
                placeholder="Mínimo 8 caracteres" 
                required>
              <div class="password-hints" *ngIf="newPassword">
                <span [class.hint-ok]="newPassword.length >= 8" [class.hint-fail]="newPassword.length < 8">
                  <i class="fa-solid" [class.fa-check]="newPassword.length >= 8" [class.fa-xmark]="newPassword.length < 8"></i> Mínimo 8 caracteres
                </span>
                <span [class.hint-ok]="hasUppercase(newPassword)" [class.hint-fail]="!hasUppercase(newPassword)">
                  <i class="fa-solid" [class.fa-check]="hasUppercase(newPassword)" [class.fa-xmark]="!hasUppercase(newPassword)"></i> Al menos una mayúscula
                </span>
                <span [class.hint-ok]="hasLowercase(newPassword)" [class.hint-fail]="!hasLowercase(newPassword)">
                  <i class="fa-solid" [class.fa-check]="hasLowercase(newPassword)" [class.fa-xmark]="!hasLowercase(newPassword)"></i> Al menos una minúscula
                </span>
                <span [class.hint-ok]="hasNumber(newPassword)" [class.hint-fail]="!hasNumber(newPassword)">
                  <i class="fa-solid" [class.fa-check]="hasNumber(newPassword)" [class.fa-xmark]="!hasNumber(newPassword)"></i> Al menos un número
                </span>
                <span [class.hint-ok]="hasSpecial(newPassword)" [class.hint-fail]="!hasSpecial(newPassword)">
                  <i class="fa-solid" [class.fa-check]="hasSpecial(newPassword)" [class.fa-xmark]="!hasSpecial(newPassword)"></i> Al menos un carácter especial
                </span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Confirmar Contraseña</label>
              <input 
                type="password" 
                class="form-control" 
                [(ngModel)]="confirmPassword" 
                name="confirmPassword" 
                placeholder="Repetir nueva contraseña" 
                required>
              <div *ngIf="confirmPassword && newPassword !== confirmPassword" class="password-hints">
                <span class="hint-fail">
                  <i class="fa-solid fa-xmark"></i> Las contraseñas no coinciden
                </span>
              </div>
              <div *ngIf="confirmPassword && newPassword === confirmPassword && confirmPassword.length > 0" class="password-hints">
                <span class="hint-ok">
                  <i class="fa-solid fa-check"></i> Las contraseñas coinciden
                </span>
              </div>
            </div>

            <button type="submit" class="btn btn-primary btn-block" [disabled]="loading()">
              <i *ngIf="loading()" class="fa-solid fa-circle-notch fa-spin"></i>
              <span *ngIf="!loading()">Actualizar Contraseña</span>
            </button>
          </form>

          <div *ngIf="successMessage()" class="mt-3 text-center">
            <a routerLink="/login" class="btn btn-primary btn-block">Ir a Iniciar Sesión</a>
          </div>
        </div>

        <div class="text-center mt-4">
          <a routerLink="/login" class="link-small">
            <i class="fa-solid fa-arrow-left"></i> Volver a Iniciar Sesión
          </a>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .login-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
    .login-card { width: 100%; max-width: 480px; padding: 36px 32px; }
    .brand-icon { width: 56px; height: 56px; background: linear-gradient(135deg, var(--accent) 0%, var(--primary) 100%); border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; color: white; margin: 0 auto 16px; }
    .brand-title { font-size: 1.6rem; font-weight: 800; margin-bottom: 4px; }
    .brand-subtitle { font-size: 0.88rem; color: var(--text-muted); margin-bottom: 24px; }
    .alert-box { padding: 12px 16px; border-radius: 10px; font-size: 0.88rem; display: flex; align-items: center; gap: 10px; margin-bottom: 18px; }
    .alert-success { background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #6ee7b7; }
    .alert-error { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; }
    .btn-block { width: 100%; padding: 12px; }
    .link-small { font-size: 0.85rem; color: var(--primary); text-decoration: none; }
    .text-center { text-align: center; }
    .text-sm { font-size: 0.85rem; }
    .mt-3 { margin-top: 14px; }
    .mt-4 { margin-top: 20px; }
    .mb-1 { margin-bottom: 4px; }
    .text-xs { font-size: 0.75rem; }
    .font-bold { font-weight: 700; }
    .font-mono { font-family: var(--font-mono); }
    .password-hints { display: flex; flex-direction: column; gap: 3px; margin-top: 8px; font-size: 0.78rem; }
    .hint-ok { color: #6ee7b7; }
    .hint-fail { color: #fca5a5; }
    .password-hints i { font-size: 0.7rem; margin-right: 4px; }
  `]
})
export class PasswordResetComponent {
  step = signal<number>(1);
  email = '';
  token = '';
  newPassword = '';
  confirmPassword = '';
  loading = signal<boolean>(false);
  message = signal<string | null>(null);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);
  tokenSent = signal<boolean>(false);

  constructor(private authService: AuthService) {}

  // Password validation helpers
  hasUppercase(pwd: string): boolean { return /[A-Z]/.test(pwd); }
  hasLowercase(pwd: string): boolean { return /[a-z]/.test(pwd); }
  hasNumber(pwd: string): boolean { return /[0-9]/.test(pwd); }
  hasSpecial(pwd: string): boolean { return /[^A-Za-z0-9]/.test(pwd); }

  isPasswordValid(pwd: string): boolean {
    return pwd.length >= 8 && this.hasUppercase(pwd) && this.hasLowercase(pwd) && this.hasNumber(pwd) && this.hasSpecial(pwd);
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU27: Recuperar Contraseña y Credenciales (HU-10)
   * Diagrama de Comunicación – Solicitud de Token de Recuperación
   * Participantes:
   *   Actor  → Usuario (Todos los roles)
   *   IU     → IU_RecuperarPassword (Angular)
   *   CTR    → CTR_PasswordReset (Django REST)
   *   CE     → CE_Usuario_y_Token (PostgreSQL)
   *   SRV    → SRV_ServicioCorreo (SMTP / SendGrid)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  onRequestToken() {
    // --- Paso 1: Solicitar recuperación (email) ---
    // El Actor ingresa su correo electrónico registrado
    this.loading.set(true);
    this.errorMessage.set(null);
    this.message.set(null);

    // --- Paso 2: POST /api/auth/password-reset/ {email} ---
    // IU_RecuperarPassword envía el email al CTR_PasswordReset
    this.authService.requestPasswordReset(this.email).subscribe({
      next: (res: any) => {
        this.loading.set(false);
        // --- Paso 7: 200 OK (Enlace enviado si existe) ---
        // CTR_PasswordReset confirma el envío del enlace
        // --- Paso 8: Mostrar confirmación envío de correo ---
        // IU_RecuperarPassword muestra el mensaje de confirmación al Actor
        this.message.set(res.mensaje);
        this.tokenSent.set(true);
        // Seguridad: NO mostramos token_debug — el token solo se recibe por email
      },
      error: (err: any) => {
        this.loading.set(false);
        this.errorMessage.set(err.error?.email?.[0] || 'Error al solicitar recuperación.');
      }
    });
    // NOTA: Los pasos 3-6 y 5.1-5.2 ocurren en el backend:
    //   Paso 3: SELECT usuario WHERE email = ? AND activo = true
    //   Paso 4: Usuario encontrado
    //   Paso 5: INSERT INTO accounts_tokenrecuperacion (token, exp=24h)
    //   Paso 5.1: send_mail(email, reset_link)
    //   Paso 5.2: Correo enviado
    //   Paso 6: Token generado
  }

  goToStep2() {
    this.step.set(2);
    this.errorMessage.set(null);
    this.message.set(null);
  }

  /**
   * CU27: Recuperar Contraseña y Credenciales (HU-10)
   * Diagrama de Comunicación – Confirmación de Nueva Contraseña
   */
  onConfirmReset() {
    // --- Paso 9: Ingresar nueva password con token ---
    // El Actor ingresa el token recibido por correo y su nueva contraseña

    // Validación frontend de contraseña
    if (!this.isPasswordValid(this.newPassword)) {
      this.errorMessage.set('La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial.');
      return;
    }
    if (this.newPassword !== this.confirmPassword) {
      this.errorMessage.set('Las contraseñas no coinciden.');
      return;
    }

    this.loading.set(true);
    this.errorMessage.set(null);

    // --- Paso 10: POST /api/auth/password-reset-confirm/ {token, password} ---
    // IU_RecuperarPassword envía el token y nueva password al CTR_PasswordReset
    this.authService.confirmPasswordReset({
      token: this.token,
      password: this.newPassword,
      password_confirm: this.confirmPassword
    }).subscribe({
      next: (res: any) => {
        this.loading.set(false);
        // --- Paso 15: 200 OK (Contraseña actualizada) ---
        // CTR_PasswordReset confirma la actualización
        // --- Paso 16: Notificar éxito y redirigir a Login ---
        // IU_RecuperarPassword muestra el éxito y ofrece redirigir
        this.successMessage.set(res.mensaje);
      },
      error: (err: any) => {
        this.loading.set(false);
        const detail = err.error?.non_field_errors?.[0] || err.error?.password?.[0] || err.error?.token?.[0] || err.error?.detail || 'Error al restablecer contraseña.';
        this.errorMessage.set(detail);
      }
    });
    // NOTA: Los pasos 11-14 ocurren en el backend (CTR_PasswordReset ↔ CE_Usuario_y_Token):
    //   Paso 11: Validar token (vigente y usado = false)
    //   Paso 12: Token verificado
    //   Paso 13: UPDATE usuario SET password = ? ; token.usado = true
    //   Paso 14: Credenciales actualizadas
  }
}
