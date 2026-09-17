// ==============================================================================
// MÓDULO: checkout-success.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_CheckoutSuccess
// PUNTO 7+8: Web/Móvil + Modelo SaaS en la nube
// DESCRIPCIÓN: Página de confirmación post-pago que verifica la sesión de Stripe,
//              dispara la creación del tenant y muestra las credenciales al usuario.
// ==============================================================================
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { SubscriptionService } from '../../core/services/subscription.service';

@Component({
  selector: 'app-checkout-success',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="success-container">
      <div class="success-bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
      </div>

      <!-- Loading State -->
      <div class="success-card glass-panel" *ngIf="loading()">
        <div class="loading-icon">
          <i class="fa-solid fa-circle-notch fa-spin"></i>
        </div>
        <h2>Verificando tu pago...</h2>
        <p class="text-muted">Estamos creando tu centro psicológico. Esto puede tomar unos segundos.</p>
        <div class="progress-bar">
          <div class="progress-fill"></div>
        </div>
      </div>

      <!-- Success State -->
      <div class="success-card glass-panel" *ngIf="!loading() && success()">
        <div class="success-icon">
          <i class="fa-solid fa-check"></i>
        </div>
        <h2>¡Tu centro está listo! 🎉</h2>
        <p class="text-muted">{{ mensaje() }}</p>

        <div class="credentials-box">
          <div class="cred-header">
            <i class="fa-solid fa-key"></i>
            <span>Credenciales de Acceso</span>
          </div>
          <div class="cred-item">
            <span class="cred-label">Centro:</span>
            <span class="cred-value">{{ centroNombre() }}</span>
          </div>
          <div class="cred-item">
            <span class="cred-label">Email:</span>
            <span class="cred-value">{{ email() }}</span>
          </div>
          <div class="cred-item" *ngIf="passwordTemporal()">
            <span class="cred-label">Contraseña temporal:</span>
            <div class="pass-wrapper">
              <code class="cred-pass-display">{{ showPassword() ? passwordTemporal() : '••••••••••••' }}</code>
              <div class="pass-actions">
                <button type="button" class="btn-icon-action" (click)="toggleShowPassword()" [title]="showPassword() ? 'Ocultar contraseña' : 'Ver contraseña'">
                  <i class="fa-solid" [class.fa-eye]="!showPassword()" [class.fa-eye-slash]="showPassword()"></i>
                </button>
                <button type="button" class="btn-icon-action" (click)="copyPassword()" [title]="copied() ? '¡Copiado!' : 'Copiar contraseña'">
                  <i class="fa-solid" [class.fa-copy]="!copied()" [class.fa-check]="copied()" [style.color]="copied() ? '#34d399' : ''"></i>
                </button>
              </div>
            </div>
          </div>
          <div class="cred-note">
            <i class="fa-solid fa-envelope"></i>
            Se enviaron las credenciales completas (incluida la contraseña temporal) a tu correo electrónico.
          </div>
        </div>

        <div class="info-box">
          <i class="fa-solid fa-info-circle"></i>
          <p>Al iniciar sesión por primera vez, el sistema te pedirá que cambies tu contraseña temporal por una nueva contraseña segura.</p>
        </div>

        <div class="success-actions">
          <a routerLink="/login" class="btn-go-login">
            <i class="fa-solid fa-arrow-right-to-bracket"></i>
            Ir a Iniciar Sesión
          </a>
          <a routerLink="/landing" class="btn-back">
            <i class="fa-solid fa-arrow-left"></i>
            Volver al Inicio
          </a>
        </div>
      </div>

      <!-- Error State -->
      <div class="success-card glass-panel" *ngIf="!loading() && !success()">
        <div class="error-icon">
          <i class="fa-solid fa-triangle-exclamation"></i>
        </div>
        <h2>Hubo un problema</h2>
        <p class="text-muted">{{ errorMessage() }}</p>

        <div class="success-actions">
          <a routerLink="/landing" class="btn-go-login">
            <i class="fa-solid fa-arrow-left"></i>
            Volver a Intentar
          </a>
        </div>
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

    .success-container {
      min-height: 100vh;
      display: flex; align-items: center; justify-content: center;
      background: var(--bg-dark);
      position: relative; overflow: hidden;
      padding: 24px;
    }
    .success-bg-shapes { position: absolute; inset: 0; pointer-events: none; }
    .shape {
      position: absolute; border-radius: 50%;
      filter: blur(120px); opacity: 0.3;
    }
    .shape-1 {
      width: 500px; height: 500px;
      background: var(--primary);
      top: -200px; right: -100px;
    }
    .shape-2 {
      width: 350px; height: 350px;
      background: #0ea5e9;
      bottom: -150px; left: -80px;
    }

    .success-card {
      max-width: 520px; width: 100%;
      background: rgba(15,26,48,0.9);
      border: 1px solid var(--border-glass);
      border-radius: 20px;
      padding: 48px 36px;
      text-align: center;
      position: relative; z-index: 2;
      animation: slideUp 0.5s ease-out;
    }
    .success-card h2 {
      font-size: 1.6rem; font-weight: 800; color: white; margin-bottom: 10px;
    }
    .text-muted { color: var(--text-muted); font-size: 0.95rem; line-height: 1.6; }

    .loading-icon {
      width: 72px; height: 72px; border-radius: 50%;
      background: rgba(34,160,107,0.12);
      display: flex; align-items: center; justify-content: center;
      font-size: 2rem; color: var(--primary-light);
      margin: 0 auto 24px;
    }

    .progress-bar {
      width: 100%; height: 4px; background: rgba(255,255,255,0.06);
      border-radius: 2px; margin-top: 28px; overflow: hidden;
    }
    .progress-fill {
      height: 100%; width: 0%;
      background: linear-gradient(90deg, var(--primary), var(--primary-light));
      border-radius: 2px;
      animation: progressAnim 3s ease-in-out forwards;
    }
    @keyframes progressAnim { 0%{width:0%} 30%{width:40%} 60%{width:65%} 80%{width:85%} 100%{width:95%} }

    .success-icon {
      width: 80px; height: 80px; border-radius: 50%;
      background: linear-gradient(135deg, var(--primary), var(--primary-light));
      display: flex; align-items: center; justify-content: center;
      font-size: 2.2rem; color: white;
      margin: 0 auto 24px;
      box-shadow: 0 8px 32px var(--primary-glow);
      animation: successPulse 1s ease-out;
    }
    @keyframes successPulse {
      0% { transform: scale(0.5); opacity: 0; }
      50% { transform: scale(1.15); }
      100% { transform: scale(1); opacity: 1; }
    }

    .error-icon {
      width: 80px; height: 80px; border-radius: 50%;
      background: rgba(239,68,68,0.15);
      display: flex; align-items: center; justify-content: center;
      font-size: 2.2rem; color: #ef4444;
      margin: 0 auto 24px;
    }

    .credentials-box {
      background: rgba(34,160,107,0.08);
      border: 1px solid rgba(34,160,107,0.2);
      border-radius: 14px;
      padding: 20px;
      margin: 28px 0 20px;
      text-align: left;
    }
    .cred-header {
      display: flex; align-items: center; gap: 8px;
      font-weight: 700; color: var(--primary-light); font-size: 0.88rem;
      margin-bottom: 14px; text-transform: uppercase; letter-spacing: 1px;
    }
    .cred-item {
      display: flex; justify-content: space-between; align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .cred-label { font-size: 0.85rem; color: var(--text-muted); }
    .cred-value { font-size: 0.9rem; color: white; font-weight: 600; }
    .cred-note {
      display: flex; align-items: flex-start; gap: 8px;
      margin-top: 14px;
      font-size: 0.82rem; color: var(--primary-light);
      line-height: 1.5;
    }
    .cred-note i { margin-top: 3px; flex-shrink: 0; }

    .pass-wrapper {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .cred-pass-display {
      font-family: 'Courier New', Courier, monospace;
      font-size: 0.95rem;
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid rgba(34, 160, 107, 0.35);
      padding: 4px 10px;
      border-radius: 8px;
      color: #34d399;
      font-weight: 700;
      letter-spacing: 0.5px;
    }
    .pass-actions {
      display: flex;
      gap: 5px;
    }
    .btn-icon-action {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #e2e8f0;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.85rem;
      transition: all 0.2s ease;
    }
    .btn-icon-action:hover {
      background: rgba(34, 160, 107, 0.25);
      border-color: rgba(34, 160, 107, 0.5);
      color: #34d399;
    }

    .info-box {
      display: flex; align-items: flex-start; gap: 10px;
      background: rgba(14,165,233,0.08);
      border: 1px solid rgba(14,165,233,0.2);
      border-radius: 12px;
      padding: 14px 16px;
      margin-bottom: 28px;
      text-align: left;
    }
    .info-box i { color: #0ea5e9; font-size: 1rem; margin-top: 2px; flex-shrink: 0; }
    .info-box p { font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; margin: 0; }

    .success-actions {
      display: flex; flex-direction: column; gap: 12px;
    }
    .btn-go-login {
      display: flex; align-items: center; justify-content: center; gap: 10px;
      background: linear-gradient(135deg, var(--primary), var(--primary-light));
      color: white; font-weight: 700; font-size: 1rem;
      padding: 14px 28px; border-radius: 12px; text-decoration: none;
      box-shadow: 0 4px 20px var(--primary-glow);
      transition: all 0.3s ease;
    }
    .btn-go-login:hover {
      transform: translateY(-2px); box-shadow: 0 6px 28px var(--primary-glow);
    }
    .btn-back {
      display: flex; align-items: center; justify-content: center; gap: 8px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.1);
      color: var(--text-muted); font-weight: 600; font-size: 0.9rem;
      padding: 12px 24px; border-radius: 12px; text-decoration: none;
      transition: all 0.3s ease;
    }
    .btn-back:hover { background: rgba(255,255,255,0.1); color: white; }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `]
})
export class CheckoutSuccessComponent implements OnInit {
  loading = signal(true);
  success = signal(false);
  centroNombre = signal('');
  email = signal('');
  mensaje = signal('');
  errorMessage = signal('');
  passwordTemporal = signal('');
  showPassword = signal(false);
  copied = signal(false);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private subscriptionService: SubscriptionService,
  ) {}

  ngOnInit() {
    const sessionId = this.route.snapshot.queryParamMap.get('session_id');
    if (!sessionId) {
      this.loading.set(false);
      this.success.set(false);
      this.errorMessage.set('No se encontró la sesión de pago. Verifica tu enlace o intenta de nuevo.');
      return;
    }
    this.verifySession(sessionId);
  }

  toggleShowPassword() {
    this.showPassword.update(v => !v);
  }

  copyPassword() {
    const pass = this.passwordTemporal();
    if (!pass) return;
    navigator.clipboard.writeText(pass).then(() => {
      this.copied.set(true);
      setTimeout(() => this.copied.set(false), 2500);
    });
  }

  verifySession(sessionId: string) {
    this.subscriptionService.verifySession(sessionId).subscribe({
      next: (res) => {
        this.loading.set(false);
        this.success.set(true);
        this.centroNombre.set(res.centro_nombre);
        this.email.set(res.email);
        this.mensaje.set(res.mensaje);
        if (res.password_temporal) {
          this.passwordTemporal.set(res.password_temporal);
        }
      },
      error: (err) => {
        this.loading.set(false);
        this.success.set(false);
        const msg = err.error?.error || err.error?.detail || 'Error al verificar el pago. Contacta soporte si el problema persiste.';
        this.errorMessage.set(msg);
      }
    });
  }
}
