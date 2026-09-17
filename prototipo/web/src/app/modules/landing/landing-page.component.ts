// ==============================================================================
// MÓDULO: landing-page.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_LandingPage
// PUNTO 7+8: Web/Móvil + Modelo SaaS en la nube
// DESCRIPCIÓN: Landing page pública con presentación del sistema, planes de
//              suscripción y flujo de checkout con Stripe. Diseño premium con
//              glassmorphism, gradientes, micro-animaciones y UX profesional.
// ==============================================================================
import { Component, OnInit, AfterViewInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { SubscriptionService } from '../../core/services/subscription.service';
import { Plan } from '../../core/models';

@Component({
  selector: 'app-landing-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <!-- ═══════════ NAVIGATION BAR ═══════════ -->
    <nav class="landing-nav" id="landing-nav">
      <div class="nav-container">
        <div class="nav-brand" (click)="scrollToTop($event)" role="button" tabindex="0">
          <div class="nav-logo">
            <i class="fa-solid fa-brain"></i>
          </div>
          <span class="nav-title">SIGEPSI</span>
        </div>
        <div class="nav-links">
          <a href="#features" (click)="scrollToSection('features', $event)" class="nav-link">Características</a>
          <a href="#planes" (click)="scrollToSection('planes', $event)" class="nav-link">Planes</a>
          <a routerLink="/login" class="nav-link">Iniciar Sesión</a>
          <a href="#planes" (click)="scrollToSection('planes', $event)" class="nav-cta-btn">Crear mi Centro</a>
        </div>
      </div>
    </nav>

    <!-- ═══════════ HERO SECTION ═══════════ -->
    <section class="hero-section" id="hero">
      <div class="hero-bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
      <div class="hero-content">
        <div class="hero-badge">
          <i class="fa-solid fa-sparkles"></i>
          Plataforma Clínica de Nueva Generación
        </div>
        <h1 class="hero-title">
          Gestiona tu Centro<br>
          Psicológico de forma<br>
          <span class="gradient-text">inteligente y segura</span>
        </h1>
        <p class="hero-subtitle">
          SIGEPSI es la plataforma SaaS multi-tenant diseñada para centros psicológicos.
          Agenda, historias clínicas, teleconsulta, reportes y más — todo en un solo lugar.
        </p>
        <div class="hero-actions">
          <a href="#planes" (click)="scrollToSection('planes', $event)" class="btn-hero-primary">
            <i class="fa-solid fa-rocket"></i>
            Comenzar Ahora
          </a>
          <a routerLink="/login" class="btn-hero-secondary">
            <i class="fa-solid fa-arrow-right-to-bracket"></i>
            Accede a la Plataforma
          </a>
        </div>
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-number">100%</span>
            <span class="stat-label">En la Nube</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-number">Multi-Tenant</span>
            <span class="stat-label">Aislamiento Total</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-number">24/7</span>
            <span class="stat-label">Disponibilidad</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════ FEATURES SECTION ═══════════ -->
    <section class="features-section" id="features">
      <div class="section-container">
        <div class="section-header">
          <span class="section-tag">CARACTERÍSTICAS</span>
          <h2 class="section-title">Todo lo que tu centro necesita</h2>
          <p class="section-subtitle">
            Una suite completa de herramientas clínicas y administrativas, diseñada por y para profesionales de la salud mental.
          </p>
        </div>
        <div class="features-grid">
          <div class="feature-card" *ngFor="let feat of features">
            <div class="feature-icon" [style.background]="feat.gradient">
              <i [class]="feat.icon"></i>
            </div>
            <h3 class="feature-title">{{ feat.title }}</h3>
            <p class="feature-desc">{{ feat.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════ PRICING SECTION ═══════════ -->
    <section class="pricing-section" id="planes">
      <div class="section-container">
        <div class="section-header">
          <span class="section-tag">PLANES</span>
          <h2 class="section-title">Elige el plan ideal para tu centro</h2>
          <p class="section-subtitle">
            Sin contratos a largo plazo. Cancela cuando quieras. Comienza hoy mismo.
          </p>
        </div>

        <div class="pricing-grid">
          <div
            class="pricing-card"
            *ngFor="let plan of plans()"
            [class.recommended]="plan.recomendado"
            [id]="'plan-' + plan.id"
          >
            <div class="pricing-badge" *ngIf="plan.recomendado">
              <i class="fa-solid fa-star"></i> Más Popular
            </div>
            <div class="pricing-header">
              <h3 class="pricing-name">{{ plan.nombre }}</h3>
              <div class="pricing-price">
                <span class="price-currency">$</span>
                <span class="price-amount">{{ plan.precio_mensual / 100 }}</span>
                <span class="price-period">/mes</span>
              </div>
              <p class="pricing-limits">
                <span *ngIf="plan.max_psicologos < 9999">Hasta {{ plan.max_psicologos }} psicólogos</span>
                <span *ngIf="plan.max_psicologos >= 9999">Psicólogos ilimitados</span>
                ·
                <span *ngIf="plan.max_pacientes < 99999">{{ plan.max_pacientes }} pacientes</span>
                <span *ngIf="plan.max_pacientes >= 99999">Pacientes ilimitados</span>
              </p>
            </div>
            <ul class="pricing-features">
              <li *ngFor="let f of plan.features">
                <i class="fa-solid fa-check"></i>
                {{ f }}
              </li>
            </ul>
            <button
              class="pricing-btn"
              [class.btn-recommended]="plan.recomendado"
              (click)="onSelectPlan(plan)"
              [disabled]="checkoutLoading()"
            >
              <i *ngIf="checkoutLoading() && selectedPlanId() === plan.id" class="fa-solid fa-circle-notch fa-spin"></i>
              <span *ngIf="!(checkoutLoading() && selectedPlanId() === plan.id)">
                <i class="fa-solid fa-credit-card"></i> Suscribirme
              </span>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════ CHECKOUT MODAL ═══════════ -->
    <div class="modal-overlay" *ngIf="showCheckoutModal()" (click)="closeModal()">
      <div class="modal-card glass-panel" (click)="$event.stopPropagation()">
        <button class="modal-close" (click)="closeModal()">
          <i class="fa-solid fa-xmark"></i>
        </button>
        <div class="modal-header">
          <div class="modal-icon">
            <i class="fa-solid fa-hospital"></i>
          </div>
          <h2>Crea tu Centro Psicológico</h2>
          <p>Completa los datos para crear tu cuenta en el plan <strong>{{ selectedPlanName() }}</strong></p>
        </div>

        <div *ngIf="checkoutError()" class="alert-box alert-error">
          <i class="fa-solid fa-triangle-exclamation"></i>
          <span>{{ checkoutError() }}</span>
        </div>

        <form (ngSubmit)="onCheckout()">
          <div class="form-group">
            <label class="form-label">Nombre del Centro / Gabinete</label>
            <input
              type="text"
              class="form-control"
              [(ngModel)]="checkoutData.nombre_centro"
              name="nombre_centro"
              placeholder="Ej: Centro Psicológico Esperanza"
              required
              minlength="3"
            >
          </div>
          <div class="form-group">
            <label class="form-label">Tu Nombre Completo</label>
            <input
              type="text"
              class="form-control"
              [(ngModel)]="checkoutData.nombre_admin"
              name="nombre_admin"
              placeholder="Ej: Juan Pérez"
              required
            >
          </div>
          <div class="form-group">
            <label class="form-label">Correo Electrónico</label>
            <input
              type="email"
              class="form-control"
              [(ngModel)]="checkoutData.email"
              name="email"
              placeholder="tu@correo.com"
              required
            >
            <small class="form-hint">Recibirás tus credenciales de acceso en este correo</small>
          </div>
          <button type="submit" class="btn btn-primary btn-block" [disabled]="checkoutLoading()">
            <i *ngIf="checkoutLoading()" class="fa-solid fa-circle-notch fa-spin"></i>
            <span *ngIf="!checkoutLoading()">
              <i class="fa-solid fa-lock"></i> Continuar al Pago Seguro
            </span>
            <span *ngIf="checkoutLoading()">Preparando pago...</span>
          </button>
          <p class="modal-secure-note">
            <i class="fa-solid fa-shield-halved"></i>
            Pago seguro procesado por Stripe. No almacenamos datos de tarjeta.
          </p>
        </form>
      </div>
    </div>

    <!-- ═══════════ CTA SECTION ═══════════ -->
    <section class="cta-section">
      <div class="section-container">
        <div class="cta-content">
          <h2 class="cta-title">¿Ya tienes una cuenta?</h2>
          <p class="cta-subtitle">
            Accede a tu centro psicológico ahora mismo e inicia tu jornada de trabajo.
          </p>
          <a routerLink="/login" class="btn-cta">
            <i class="fa-solid fa-arrow-right-to-bracket"></i>
            Accede a la Plataforma
          </a>
        </div>
      </div>
    </section>

    <!-- ═══════════ FOOTER ═══════════ -->
    <footer class="landing-footer">
      <div class="footer-container">
        <div class="footer-brand">
          <div class="footer-logo">
            <i class="fa-solid fa-brain"></i>
          </div>
          <span>SIGEPSI</span>
          <p class="footer-tagline">Plataforma Clínica Multi-Tenant para Centros Psicológicos</p>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2026 SIGEPSI — Sistema de Gestión Psicológica. Todos los derechos reservados.</p>
        </div>
      </div>
    </footer>
  `,
  styles: [`
    /* ═══════════ GLOBAL RESETS ═══════════ */
    :host {
      display: block;
      overflow-x: hidden;
      scrollbar-width: none !important;
      -ms-overflow-style: none !important;
      --primary: #19734e;
      --primary-light: #22a06b;
      --primary-dark: #0f3526;
      --primary-glow: rgba(34, 160, 107, 0.28);
      --accent: #2ec486;
      --bg-dark: #07131e;
      --bg-card: rgba(13, 24, 38, 0.75);
      --text-white: #f8fafc;
      --text-muted: #94a3b8;
      --border-glass: rgba(255,255,255,0.08);
      --radius-lg: 20px;
      --radius-md: 14px;
      --transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
    }
    :host::-webkit-scrollbar {
      display: none !important;
      width: 0 !important;
      height: 0 !important;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    #features, #planes {
      scroll-margin-top: 86px;
    }

    /* ═══════════ NAVIGATION ═══════════ */
    .landing-nav {
      position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
      background: rgba(7, 19, 30, 0.88);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      padding: 0 28px;
    }
    .nav-container {
      max-width: 1200px; margin: 0 auto;
      display: flex; align-items: center; justify-content: space-between;
      height: 68px;
    }
    .nav-brand {
      display: flex; align-items: center; gap: 10px;
      cursor: pointer;
      user-select: none;
      outline: none;
    }
    .nav-logo {
      width: 38px; height: 38px;
      background: linear-gradient(135deg, var(--primary), var(--primary-light));
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      color: white; font-size: 1.1rem;
      box-shadow: 0 2px 10px var(--primary-glow);
    }
    .nav-title {
      font-weight: 800; font-size: 1.3rem; color: white; letter-spacing: -0.5px;
    }
    .nav-links {
      display: flex; align-items: center; gap: 8px;
    }
    .nav-link {
      color: var(--text-muted); text-decoration: none; font-size: 0.9rem;
      font-weight: 500; padding: 8px 14px; border-radius: 8px;
      transition: var(--transition);
      cursor: pointer;
    }
    .nav-link:hover { color: white; background: rgba(255,255,255,0.06); }
    .nav-cta-btn {
      background: linear-gradient(135deg, var(--primary), var(--primary-light));
      color: white; text-decoration: none; font-weight: 700; font-size: 0.88rem;
      padding: 10px 22px; border-radius: 10px;
      transition: var(--transition);
      box-shadow: 0 2px 14px var(--primary-glow);
      cursor: pointer;
    }
    .nav-cta-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 22px rgba(34,160,107,0.45);
      color: white;
    }

    /* ═══════════ HERO ═══════════ */
    .hero-section {
      min-height: 100vh; display: flex; align-items: center; justify-content: center;
      background: radial-gradient(ellipse 90% 65% at 50% -10%, #0d2a3e 0%, #071522 55%, #050b12 100%);
      position: relative; overflow: hidden;
      padding: 120px 24px 80px;
    }
    .hero-bg-shapes { position: absolute; inset: 0; pointer-events: none; }
    .shape {
      position: absolute; border-radius: 50%;
      filter: blur(120px); opacity: 0.28;
    }
    .shape-1 {
      width: 550px; height: 550px;
      background: var(--primary);
      top: -180px; right: -80px;
      animation: float1 12s ease-in-out infinite;
    }
    .shape-2 {
      width: 400px; height: 400px;
      background: var(--accent);
      bottom: -150px; left: -100px;
      animation: float2 15s ease-in-out infinite;
    }
    .shape-3 {
      width: 280px; height: 280px;
      background: #0ea5e9;
      top: 40%; left: 50%;
      animation: float3 10s ease-in-out infinite;
    }
    @keyframes float1 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(-30px,25px)} }
    @keyframes float2 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(25px,-30px)} }
    @keyframes float3 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(-15px,15px)} }

    .hero-content {
      max-width: 820px; text-align: center; position: relative; z-index: 2;
    }
    .hero-badge {
      display: inline-flex; align-items: center; gap: 8px;
      background: rgba(25, 115, 78, 0.18); color: #34d399;
      border: 1px solid rgba(46, 196, 134, 0.35);
      box-shadow: 0 0 24px rgba(46, 196, 134, 0.12);
      padding: 7px 20px; border-radius: 40px;
      font-size: 0.82rem; font-weight: 600;
      letter-spacing: 0.3px;
      margin-bottom: 28px;
      animation: fadeInUp 0.6s ease-out;
    }
    .hero-title {
      font-size: clamp(2.3rem, 5.2vw, 3.8rem);
      font-weight: 800; line-height: 1.12; color: #ffffff;
      letter-spacing: -0.03em; margin-bottom: 22px;
      animation: fadeInUp 0.6s ease-out 0.1s both;
    }
    .gradient-text {
      background: linear-gradient(135deg, #34d399 0%, #2ec486 50%, #38bdf8 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .hero-subtitle {
      font-size: 1.12rem; color: #94a3b8;
      line-height: 1.75; max-width: 640px; margin: 0 auto 36px;
      font-weight: 400;
      animation: fadeInUp 0.6s ease-out 0.2s both;
    }
    .hero-actions {
      display: flex; gap: 14px; justify-content: center; flex-wrap: wrap;
      animation: fadeInUp 0.6s ease-out 0.3s both;
    }
    .btn-hero-primary {
      background: linear-gradient(135deg, #19734e, #22a06b);
      color: white; font-weight: 700; font-size: 0.98rem;
      padding: 15px 34px; border-radius: 12px; text-decoration: none;
      display: flex; align-items: center; gap: 10px;
      box-shadow: 0 6px 24px rgba(25, 115, 78, 0.35);
      transition: var(--transition);
      cursor: pointer;
    }
    .btn-hero-primary:hover {
      transform: translateY(-2px); box-shadow: 0 10px 32px rgba(34, 160, 107, 0.45);
      color: white;
    }
    .btn-hero-secondary {
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.16);
      color: #e2e8f0; font-weight: 600; font-size: 0.98rem;
      padding: 15px 34px; border-radius: 12px; text-decoration: none;
      display: flex; align-items: center; gap: 10px;
      backdrop-filter: blur(10px);
      transition: var(--transition);
    }
    .btn-hero-secondary:hover {
      background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.3);
      color: white;
    }
    .hero-stats {
      display: flex; align-items: center; justify-content: center; gap: 32px;
      margin-top: 56px; animation: fadeInUp 0.6s ease-out 0.4s both;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.07);
      border-radius: 16px;
      padding: 16px 36px;
      backdrop-filter: blur(10px);
    }
    .stat-item { text-align: center; }
    .stat-number { display: block; font-size: 1.35rem; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; }
    .stat-label { font-size: 0.78rem; color: #94a3b8; font-weight: 500; }
    .stat-divider { width: 1px; height: 36px; background: rgba(255,255,255,0.12); }

    @keyframes fadeInUp {
      from { opacity:0; transform:translateY(20px); }
      to { opacity:1; transform:translateY(0); }
    }

    /* ═══════════ FEATURES ═══════════ */
    .features-section {
      background: #050c16; padding: 110px 24px; position: relative;
    }
    .section-container { max-width: 1200px; margin: 0 auto; }
    .section-header { text-align: center; margin-bottom: 56px; }
    .section-tag {
      display: inline-block;
      font-size: 0.75rem; font-weight: 700; letter-spacing: 2px;
      color: var(--accent);
      background: rgba(46, 196, 134, 0.12);
      border: 1px solid rgba(46, 196, 134, 0.25);
      padding: 6px 18px; border-radius: 20px;
      margin-bottom: 16px;
    }
    .section-title {
      font-size: clamp(1.8rem, 3.2vw, 2.5rem); font-weight: 800;
      color: white; letter-spacing: -0.5px; margin-bottom: 14px;
    }
    .section-subtitle {
      font-size: 1.05rem; color: var(--text-muted);
      max-width: 620px; margin: 0 auto; line-height: 1.65;
    }
    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 22px;
    }
    .feature-card {
      background: rgba(13, 24, 38, 0.7);
      border: 1px solid var(--border-glass);
      border-radius: var(--radius-lg);
      padding: 34px 28px;
      backdrop-filter: blur(14px);
      transition: var(--transition);
    }
    .feature-card:hover {
      transform: translateY(-4px);
      background: rgba(18, 32, 50, 0.85);
      border-color: rgba(46, 196, 134, 0.35);
      box-shadow: 0 16px 40px rgba(0,0,0,0.4), 0 0 20px rgba(46, 196, 134, 0.08);
    }
    .feature-icon {
      width: 52px; height: 52px; border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.3rem; color: white; margin-bottom: 18px;
    }
    .feature-title {
      font-size: 1.15rem; font-weight: 700; color: white; margin-bottom: 10px;
    }
    .feature-desc {
      font-size: 0.92rem; color: var(--text-muted); line-height: 1.65;
    }

    /* ═══════════ PRICING ═══════════ */
    .pricing-section {
      background: #081320; padding: 110px 24px; position: relative;
    }
    .pricing-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 24px; max-width: 1050px; margin: 0 auto;
      align-items: start;
    }
    .pricing-card {
      background: rgba(13, 24, 38, 0.85);
      border: 1px solid var(--border-glass);
      border-radius: var(--radius-lg);
      padding: 38px 28px;
      transition: var(--transition);
      position: relative;
      backdrop-filter: blur(16px);
    }
    .pricing-card:hover {
      transform: translateY(-4px);
      border-color: rgba(255, 255, 255, 0.16);
      box-shadow: 0 16px 44px rgba(0,0,0,0.45);
    }
    .pricing-card.recommended {
      background: linear-gradient(180deg, rgba(20, 52, 42, 0.85) 0%, rgba(11, 22, 34, 0.98) 100%);
      border: 1px solid rgba(46, 196, 134, 0.5);
      box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 35px rgba(46, 196, 134, 0.16);
      transform: scale(1.04);
    }
    .pricing-card.recommended:hover { transform: scale(1.05) translateY(-4px); }
    .pricing-badge {
      position: absolute; top: -14px; left: 50%; transform: translateX(-50%);
      background: linear-gradient(135deg, var(--primary), var(--primary-light));
      color: white; font-weight: 700; font-size: 0.78rem;
      padding: 6px 18px; border-radius: 20px;
      display: flex; align-items: center; gap: 6px;
      box-shadow: 0 2px 10px rgba(25, 115, 78, 0.4);
    }
    .pricing-header { text-align: center; margin-bottom: 24px; }
    .pricing-name {
      font-size: 1.25rem; font-weight: 700; color: white; margin-bottom: 12px;
    }
    .pricing-price { display: flex; align-items: baseline; justify-content: center; gap: 2px; }
    .price-currency { font-size: 1.25rem; font-weight: 700; color: var(--accent); }
    .price-amount { font-size: 3.1rem; font-weight: 900; color: white; letter-spacing: -2px; }
    .price-period { font-size: 0.92rem; color: var(--text-muted); font-weight: 500; }
    .pricing-limits {
      font-size: 0.84rem; color: var(--text-muted); margin-top: 8px;
    }
    .pricing-features {
      list-style: none; padding: 0; margin-bottom: 28px;
    }
    .pricing-features li {
      display: flex; align-items: center; gap: 10px;
      font-size: 0.88rem; color: #cbd5e1;
      padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .pricing-features li i {
      color: var(--accent); font-size: 0.72rem; flex-shrink: 0;
    }
    .pricing-btn {
      width: 100%; padding: 14px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.12);
      color: #f1f5f9; font-weight: 700; font-size: 0.92rem;
      border-radius: 12px; cursor: pointer;
      transition: var(--transition);
      display: flex; align-items: center; justify-content: center; gap: 8px;
    }
    .pricing-btn:hover {
      background: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.25);
      color: white; transform: translateY(-1px);
    }
    .pricing-btn.btn-recommended {
      background: linear-gradient(135deg, var(--primary), var(--primary-light));
      border-color: transparent;
      box-shadow: 0 4px 20px rgba(25, 115, 78, 0.35);
      color: white;
    }
    .pricing-btn.btn-recommended:hover {
      box-shadow: 0 6px 28px rgba(34, 160, 107, 0.45);
      color: white;
    }
    .pricing-btn:disabled {
      opacity: 0.6; cursor: not-allowed;
    }

    /* ═══════════ MODAL ═══════════ */
    .modal-overlay {
      position: fixed; inset: 0; z-index: 2000;
      background: rgba(0,0,0,0.7);
      backdrop-filter: blur(8px);
      display: flex; align-items: center; justify-content: center;
      padding: 24px;
      animation: fadeIn 0.2s ease-out;
    }
    .modal-card {
      width: 100%; max-width: 480px;
      background: rgba(15,26,48,0.95);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: var(--radius-lg);
      padding: 36px 32px;
      position: relative;
      animation: slideUp 0.3s ease-out;
    }
    .modal-close {
      position: absolute; top: 16px; right: 16px;
      background: rgba(255,255,255,0.06); border: none;
      color: var(--text-muted); width: 36px; height: 36px;
      border-radius: 10px; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: var(--transition);
    }
    .modal-close:hover { background: rgba(255,255,255,0.12); color: white; }
    .modal-header { text-align: center; margin-bottom: 24px; }
    .modal-icon {
      width: 56px; height: 56px;
      background: linear-gradient(135deg, var(--primary), var(--primary-light));
      border-radius: 16px; margin: 0 auto 16px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.5rem; color: white;
    }
    .modal-header h2 { font-size: 1.4rem; font-weight: 800; color: white; margin-bottom: 8px; }
    .modal-header p { font-size: 0.9rem; color: var(--text-muted); }
    .form-group { margin-bottom: 18px; }
    .form-label {
      display: block; font-size: 0.85rem; font-weight: 600;
      color: var(--text-muted); margin-bottom: 6px;
    }
    .form-control {
      width: 100%; padding: 12px 16px;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 10px; color: white; font-size: 0.92rem;
      transition: var(--transition);
      outline: none;
    }
    .form-control::placeholder { color: rgba(255,255,255,0.3); }
    .form-control:focus {
      border-color: var(--primary-light);
      box-shadow: 0 0 0 3px var(--primary-glow);
    }
    .form-hint {
      display: block; font-size: 0.78rem; color: var(--text-muted); margin-top: 6px;
    }
    .btn { border: none; cursor: pointer; font-family: inherit; }
    .btn-primary {
      background: linear-gradient(135deg, var(--primary), var(--primary-light));
      color: white; font-weight: 700; font-size: 0.95rem;
      border-radius: 12px; transition: var(--transition);
      display: flex; align-items: center; justify-content: center; gap: 8px;
      box-shadow: 0 4px 16px var(--primary-glow);
    }
    .btn-primary:hover:not(:disabled) {
      transform: translateY(-1px); box-shadow: 0 6px 24px var(--primary-glow);
    }
    .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
    .btn-block { width: 100%; padding: 14px; margin-top: 8px; }
    .modal-secure-note {
      text-align: center; font-size: 0.78rem; color: var(--text-muted);
      margin-top: 14px; display: flex; align-items: center; justify-content: center; gap: 6px;
    }
    .alert-box {
      padding: 12px 16px; border-radius: 10px; font-size: 0.88rem;
      display: flex; align-items: center; gap: 10px; margin-bottom: 18px;
    }
    .alert-error {
      background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.3);
      color: #fca5a5;
    }
    @keyframes fadeIn { from{opacity:0} to{opacity:1} }
    @keyframes slideUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }

    /* ═══════════ CTA SECTION ═══════════ */
    .cta-section {
      background: linear-gradient(135deg, var(--primary-dark), var(--primary));
      padding: 80px 24px;
    }
    .cta-content { text-align: center; }
    .cta-title { font-size: 2rem; font-weight: 800; color: white; margin-bottom: 12px; }
    .cta-subtitle {
      font-size: 1.05rem; color: rgba(255,255,255,0.75);
      max-width: 500px; margin: 0 auto 28px;
    }
    .btn-cta {
      display: inline-flex; align-items: center; gap: 10px;
      background: white; color: var(--primary-dark);
      font-weight: 700; font-size: 1rem;
      padding: 14px 32px; border-radius: 12px; text-decoration: none;
      transition: var(--transition);
      box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .btn-cta:hover {
      transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.3);
    }

    /* ═══════════ FOOTER ═══════════ */
    .landing-footer {
      background: #050d18; padding: 40px 24px 24px; border-top: 1px solid var(--border-glass);
    }
    .footer-container {
      max-width: 1200px; margin: 0 auto; text-align: center;
    }
    .footer-brand {
      display: flex; align-items: center; justify-content: center; gap: 10px;
      font-size: 1.2rem; font-weight: 800; color: white; margin-bottom: 8px;
    }
    .footer-logo {
      width: 32px; height: 32px;
      background: linear-gradient(135deg, var(--primary), var(--primary-light));
      border-radius: 8px; display: flex; align-items: center; justify-content: center;
      color: white; font-size: 0.9rem;
    }
    .footer-tagline { font-size: 0.82rem; color: var(--text-muted); margin-bottom: 20px; }
    .footer-bottom p { font-size: 0.78rem; color: rgba(255,255,255,0.3); }

    /* ═══════════ RESPONSIVE ═══════════ */
    @media (max-width: 768px) {
      .nav-links { display: none; }
      .features-grid { grid-template-columns: 1fr; }
      .pricing-grid { grid-template-columns: 1fr; }
      .pricing-card.recommended { transform: none; }
      .pricing-card.recommended:hover { transform: translateY(-4px); }
      .hero-stats { flex-direction: column; gap: 16px; }
      .stat-divider { width: 40px; height: 1px; }
      .hero-actions { flex-direction: column; align-items: center; }
    }
  `]
})
export class LandingPageComponent implements OnInit, AfterViewInit {
  plans = signal<Plan[]>([]);
  showCheckoutModal = signal(false);
  checkoutLoading = signal(false);
  checkoutError = signal<string | null>(null);
  selectedPlanId = signal<string>('');
  selectedPlanName = signal<string>('');

  checkoutData = {
    nombre_centro: '',
    nombre_admin: '',
    email: '',
    plan: ''
  };

  features = [
    {
      icon: 'fa-solid fa-building-columns',
      title: 'Multi-Tenant Aislado',
      description: 'Cada centro opera en su propio esquema de base de datos con aislamiento total de información.',
      gradient: 'linear-gradient(135deg, #19734e, #22a06b)',
    },
    {
      icon: 'fa-solid fa-calendar-check',
      title: 'Agenda Inteligente',
      description: 'Gestión de citas, horarios de psicólogos, recordatorios automáticos y calendario visual.',
      gradient: 'linear-gradient(135deg, #0ea5e9, #38bdf8)',
    },
    {
      icon: 'fa-solid fa-video',
      title: 'Teleconsulta Integrada',
      description: 'Videollamadas seguras con Jitsi Meet integrado directamente en la plataforma.',
      gradient: 'linear-gradient(135deg, #8b5cf6, #a78bfa)',
    },
    {
      icon: 'fa-solid fa-notes-medical',
      title: 'Historias Clínicas',
      description: 'Expedientes digitales completos con notas SOAP, consentimientos y seguimiento terapéutico.',
      gradient: 'linear-gradient(135deg, #f97316, #fb923c)',
    },
    {
      icon: 'fa-solid fa-chart-line',
      title: 'Reportes Personalizables',
      description: 'Construye tus propios reportes con filtros, columnas personalizadas y exportación a Excel/PDF.',
      gradient: 'linear-gradient(135deg, #ec4899, #f472b6)',
    },
    {
      icon: 'fa-solid fa-shield-halved',
      title: 'Seguridad y Auditoría',
      description: 'RBAC granular, bitácora encriptada, tokens JWT y cumplimiento de normativas de salud.',
      gradient: 'linear-gradient(135deg, #eab308, #facc15)',
    },
  ];

  constructor(
    private subscriptionService: SubscriptionService,
    private router: Router,
    private route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.loadPlans();
  }

  ngAfterViewInit() {
    // Siempre asegurar que la página inicie en la parte superior (Hero)
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  scrollToSection(sectionId: string, event?: Event) {
    if (event) {
      event.preventDefault();
    }
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      window.history.replaceState(null, '', `/landing#${sectionId}`);
    }
  }

  scrollToTop(event?: Event) {
    if (event) {
      event.preventDefault();
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
    window.history.replaceState(null, '', '/landing');
  }

  loadPlans() {
    this.subscriptionService.getPlans().subscribe({
      next: (plans) => this.plans.set(plans),
      error: () => {
        // Fallback plans si el backend no responde
        this.plans.set([
          {
            id: 'basico', nombre: 'Básico', precio_mensual: 2900, moneda: 'usd',
            max_psicologos: 3, max_pacientes: 50, recomendado: false,
            features: ['Hasta 3 psicólogos', 'Hasta 50 pacientes', 'Historias clínicas', 'Agenda y citas', 'Reportes básicos', 'Soporte por email']
          },
          {
            id: 'profesional', nombre: 'Profesional', precio_mensual: 5900, moneda: 'usd',
            max_psicologos: 10, max_pacientes: 200, recomendado: true,
            features: ['Hasta 10 psicólogos', 'Hasta 200 pacientes', 'Historias clínicas', 'Teleconsulta integrada', 'Reportes personalizables', 'Notas SOAP', 'Soporte prioritario']
          },
          {
            id: 'empresarial', nombre: 'Empresarial', precio_mensual: 9900, moneda: 'usd',
            max_psicologos: 9999, max_pacientes: 99999, recomendado: false,
            features: ['Psicólogos ilimitados', 'Pacientes ilimitados', 'Todas las características', 'Backup/Restore', 'Soporte dedicado 24/7']
          }
        ]);
      }
    });
  }

  onSelectPlan(plan: Plan) {
    this.selectedPlanId.set(plan.id);
    this.selectedPlanName.set(plan.nombre);
    this.checkoutData.plan = plan.id;
    this.checkoutError.set(null);
    this.showCheckoutModal.set(true);
  }

  closeModal() {
    this.showCheckoutModal.set(false);
    this.checkoutError.set(null);
  }

  onCheckout() {
    if (!this.checkoutData.nombre_centro.trim() || !this.checkoutData.email.trim()) {
      this.checkoutError.set('Por favor, completa todos los campos requeridos.');
      return;
    }

    if (!this.checkoutData.nombre_admin.trim()) {
      this.checkoutData.nombre_admin = 'Administrador';
    }

    this.checkoutLoading.set(true);
    this.checkoutError.set(null);

    this.subscriptionService.createCheckout(this.checkoutData).subscribe({
      next: (res) => {
        this.checkoutLoading.set(false);
        // Redirigir a Stripe Checkout
        window.location.href = res.checkout_url;
      },
      error: (err) => {
        this.checkoutLoading.set(false);
        const msg = err.error?.error || err.error?.detail || 'Error al crear la sesión de pago. Intenta de nuevo.';
        this.checkoutError.set(msg);
      }
    });
  }
}
