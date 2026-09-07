import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../core/services/auth.service';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="app-layout">
      <!-- Backdrop for mobile sidebar drawer -->
      <div 
        class="sidebar-backdrop" 
        *ngIf="isSidebarOpen()" 
        (click)="closeSidebar()"
        aria-hidden="true">
      </div>

      <!-- Sidebar -->
      <aside class="app-sidebar" [class.open]="isSidebarOpen()">
        <!-- Brand Header -->
        <div class="sidebar-brand">
          <div class="brand-badge">
            <span class="psi-symbol">Ψ</span>
          </div>
          <div class="brand-info">
            <h2 class="brand-name">SIGEPSI</h2>
          </div>
          <button 
            type="button" 
            class="btn-sidebar-close" 
            (click)="closeSidebar()" 
            aria-label="Cerrar menú">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>

        <!-- Navigation Links -->
        <nav class="sidebar-nav">
          <div class="nav-section-title">PRINCIPAL</div>
          
          <a routerLink="/dashboard" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}" (click)="closeSidebar()" class="nav-link">
            <i class="fa-solid fa-house nav-icon"></i>
            <span>Inicio</span>
          </a>

          <!-- GESTIÓN ADMINISTRATIVA -->
          <div class="nav-section-title">GESTIÓN ADMINISTRATIVA</div>

          <!-- Centros Psicológicos (SuperAdmin) -->
          <a *ngIf="authService.isSuperAdmin()" routerLink="/tenants" routerLinkActive="active" (click)="closeSidebar()" class="nav-link">
            <i class="fa-solid fa-building nav-icon"></i>
            <span>Centros Psicológicos</span>
          </a>

          <!-- Usuarios -->
          <a routerLink="/users" routerLinkActive="active" (click)="closeSidebar()" class="nav-link">
            <i class="fa-solid fa-users nav-icon"></i>
            <span>Usuarios</span>
          </a>

          <!-- Roles y Permisos -->
          <a routerLink="/roles" routerLinkActive="active" (click)="closeSidebar()" class="nav-link">
            <i class="fa-solid fa-shield-halved nav-icon"></i>
            <span>Roles y Permisos</span>
          </a>

          <!-- MÓDULO CLÍNICO & AGENDA (Sprint 1) -->
          <ng-container *ngIf="!authService.isSuperAdmin() || authService.isInTenantContext()">
            <div class="nav-section-title">CLÍNICA Y CONSULTAS</div>
            <a routerLink="/agenda" routerLinkActive="active" (click)="closeSidebar()" class="nav-link">
              <i class="fa-solid fa-calendar-check nav-icon"></i>
              <span>Agenda y Citas</span>
            </a>
            <a routerLink="/psicologos" routerLinkActive="active" (click)="closeSidebar()" class="nav-link">
              <i class="fa-solid fa-user-doctor nav-icon"></i>
              <span>Directorio Psicólogos</span>
            </a>
            <a routerLink="/pacientes" routerLinkActive="active" (click)="closeSidebar()" class="nav-link">
              <i class="fa-solid fa-folder-open nav-icon"></i>
              <span>Expedientes Pacientes</span>
            </a>
            <a routerLink="/centro" routerLinkActive="active" (click)="closeSidebar()" class="nav-link">
              <i class="fa-solid fa-sliders nav-icon"></i>
              <span>Configuración del Centro</span>
            </a>
          </ng-container>
        </nav>

        <!-- User Footer Profile -->
        <div class="sidebar-footer">
          <div class="user-profile-row">
            <div class="user-avatar-beige">
              {{ (authService.currentUser()?.nombre || 'A').charAt(0).toUpperCase() }}
            </div>
            <div class="user-info">
              <span class="user-name">{{ authService.currentUser()?.nombre || 'Administrador' }}</span>
              <span class="user-role">{{ authService.currentUser()?.rol?.nombre || (authService.isSuperAdmin() ? 'SuperAdmin' : 'Usuario') }}</span>
            </div>
          </div>
          
          <button class="btn-sidebar-logout" (click)="onLogout()" title="Cerrar Sesión">
            <i class="fa-solid fa-arrow-right-from-bracket"></i>
            <span>Cerrar sesión</span>
          </button>
        </div>
      </aside>

      <!-- Main Content Area -->
      <div class="app-main">
        <!-- Sleek Top Navbar -->
        <header class="app-header">
          <div class="header-left">
            <!-- Mobile Hamburger Toggle -->
            <button 
              type="button" 
              class="btn-hamburger" 
              (click)="toggleSidebar()" 
              aria-label="Abrir menú de navegación"
              title="Abrir menú">
              <i class="fa-solid fa-bars"></i>
            </button>

            <!-- Context Indicator -->
            <div *ngIf="authService.isInTenantContext()" class="tenant-context-pill">
              <i class="fa-solid fa-building text-primary"></i>
              <span>{{ authService.currentTenant()?.nombre }}</span>
              <button class="btn-exit-tenant-pill" (click)="exitTenantContext()" title="Volver a la vista global">
                <i class="fa-solid fa-arrow-left"></i> Salir del centro
              </button>
            </div>
            <div *ngIf="!authService.isInTenantContext() && authService.isSuperAdmin()" class="tenant-context-pill global-mode">
              <i class="fa-solid fa-globe"></i>
              <span>SaaS Multi-Tenant Global</span>
            </div>
          </div>

          <div class="header-right">
            <div class="schema-indicator">
              <span class="schema-dot"></span>
              <span class="schema-text">
                Esquema: <strong>{{ authService.currentTenant()?.schema_name || 'public' }}</strong>
              </span>
            </div>
            <span class="badge badge-primary">
              <i class="fa-solid fa-shield"></i> {{ authService.currentUser()?.rol?.nombre || 'SuperAdmin' }}
            </span>
          </div>
        </header>

        <!-- Content Body -->
        <main class="content-body">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styles: [`
    .app-layout {
      display: flex;
      min-height: 100vh;
      background-color: var(--bg-main);
    }
    .app-sidebar {
      width: 260px;
      background: #0f2922;
      display: flex;
      flex-direction: column;
      position: fixed;
      top: 0;
      bottom: 0;
      left: 0;
      z-index: 100;
      border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    .sidebar-brand {
      padding: 24px 20px 20px;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-badge {
      width: 38px;
      height: 38px;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
    }
    .psi-symbol {
      font-size: 1.35rem;
      font-weight: 700;
      line-height: 1;
      font-family: serif;
    }
    .brand-name {
      font-size: 1.22rem;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: 0.5px;
      margin: 0;
    }
    .sidebar-nav {
      flex: 1;
      padding: 10px 14px 20px;
      overflow-y: auto;
    }
    .nav-section-title {
      font-size: 0.72rem;
      font-weight: 700;
      color: #658b7c;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      padding: 16px 12px 6px;
    }
    .nav-link {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 11px 14px;
      font-size: 0.90rem;
      font-weight: 600;
      color: #9cbab0;
      border-radius: 10px;
      text-decoration: none;
      transition: var(--transition);
      margin-bottom: 4px;
    }
    .nav-link:hover {
      background: rgba(255, 255, 255, 0.04);
      color: #ffffff;
    }
    .nav-link.active {
      background: #1a4337;
      color: #ffffff;
    }
    .nav-link.active .nav-icon {
      color: #34d399;
    }
    .nav-icon {
      font-size: 1.05rem;
      width: 20px;
      text-align: center;
      color: #7e998d;
      transition: var(--transition);
    }
    .nav-link:hover .nav-icon {
      color: #ffffff;
    }
    .sidebar-footer {
      padding: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
      background: #0d241e;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .user-profile-row {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .user-avatar-beige {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: #eedec8;
      color: #523618;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.05rem;
      flex-shrink: 0;
    }
    .user-info {
      flex: 1;
      overflow: hidden;
    }
    .user-name {
      display: block;
      font-size: 0.88rem;
      font-weight: 700;
      color: #ffffff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .user-role {
      display: block;
      font-size: 0.74rem;
      color: #8da89d;
    }
    .btn-sidebar-logout {
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 8px 12px;
      font-size: 0.82rem;
      font-weight: 600;
      color: #8da89d;
      background: transparent;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 8px;
      cursor: pointer;
      transition: var(--transition);
      font-family: inherit;
    }
    .btn-sidebar-logout:hover {
      background: rgba(255, 255, 255, 0.05);
      color: #ffffff;
      border-color: rgba(255, 255, 255, 0.22);
    }
    .app-main {
      margin-left: 260px;
      flex: 1;
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    .app-header {
      padding: 16px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-light);
      background: transparent;
    }
    .tenant-context-pill {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 6px 14px;
      background: #ffffff;
      border: 1px solid var(--border-light);
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-main);
      box-shadow: var(--shadow-sm);
    }
    .tenant-context-pill.global-mode {
      color: var(--text-muted);
    }
    .btn-exit-tenant-pill {
      background: #fee2e2;
      border: 1px solid #fca5a5;
      color: #991b1b;
      font-size: 0.74rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
      transition: var(--transition);
    }
    .btn-exit-tenant-pill:hover {
      background: #dc2626;
      color: #ffffff;
      border-color: #dc2626;
    }
    .header-right {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .schema-indicator {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.82rem;
      color: var(--text-muted);
    }
    .schema-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #16a34a;
      box-shadow: 0 0 8px rgba(22, 163, 74, 0.4);
    }
    .content-body {
      padding: 28px 32px;
      flex: 1;
    }

    /* Mobile Hamburger & Controls */
    .btn-hamburger {
      display: none;
      background: #ffffff;
      border: 1px solid var(--border-light);
      border-radius: 10px;
      width: 38px;
      height: 38px;
      align-items: center;
      justify-content: center;
      font-size: 1.15rem;
      color: #12271f;
      cursor: pointer;
      margin-right: 12px;
      box-shadow: var(--shadow-sm);
      transition: var(--transition);
      flex-shrink: 0;
    }
    .btn-hamburger:hover {
      background: #f4f7f5;
      border-color: var(--primary);
    }
    .btn-sidebar-close {
      display: none;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 8px;
      color: #9cbab0;
      width: 32px;
      height: 32px;
      cursor: pointer;
      margin-left: auto;
      align-items: center;
      justify-content: center;
      font-size: 1rem;
      transition: var(--transition);
    }
    .btn-sidebar-close:hover {
      color: #ffffff;
      background: rgba(255, 255, 255, 0.16);
    }
    .sidebar-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(15, 41, 34, 0.55);
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      z-index: 95;
      animation: fadeIn 0.2s ease-out;
    }

    /* Responsive Breakpoints */
    @media (max-width: 992px) {
      .btn-hamburger {
        display: inline-flex;
      }
      .btn-sidebar-close {
        display: inline-flex;
      }
      .app-sidebar {
        transform: translateX(-100%);
        transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 100;
        box-shadow: 0 0 40px rgba(0, 0, 0, 0.35);
      }
      .app-sidebar.open {
        transform: translateX(0);
      }
      .app-main {
        margin-left: 0 !important;
      }
      .app-header {
        padding: 12px 18px;
      }
      .content-body {
        padding: 20px 16px;
      }
      .schema-indicator {
        display: none;
      }
    }

    @media (max-width: 640px) {
      .app-header {
        flex-wrap: wrap;
        gap: 10px;
        padding: 10px 14px;
      }
      .header-left {
        display: flex;
        align-items: center;
        flex: 1;
        min-width: 0;
      }
      .tenant-context-pill {
        font-size: 0.78rem;
        padding: 4px 10px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .header-right {
        margin-left: auto;
      }
    }
  `]
})
export class MainLayoutComponent {
  isSidebarOpen = signal<boolean>(false);

  constructor(public authService: AuthService, private router: Router) {}

  toggleSidebar() {
    this.isSidebarOpen.update(v => !v);
  }

  closeSidebar() {
    this.isSidebarOpen.set(false);
  }

  exitTenantContext() {
    this.authService.clearTenant();
    this.router.navigate(['/tenants']);
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
  onLogout() {
    // --- Paso 1: Click en 'Cerrar Sesión' ---
    // El Actor hace click en el botón de logout del Navbar

    // --- Paso 2: POST /api/auth/logout/ {refresh} + Bearer JWT ---
    // IU_Navbar envía el refresh token al CTR_AuthLogout
    this.authService.logout().subscribe({
      // --- Paso 7: 200 OK {"mensaje": "Sesión cerrada"} ---
      // CTR_AuthLogout confirma la invalidación
      next: () => {
        // --- Paso 8: Redirigir a pantalla de Login ---
        // IU_Navbar redirige al Actor a la pantalla de Login
        this.router.navigate(['/login']);
      },
      error: () => {
        // Limpieza local en caso de error de red
        this.authService.clearSession();
        // --- Paso 8: Redirigir a pantalla de Login ---
        this.router.navigate(['/login']);
      }
    });
    // NOTA: Los pasos 3-6 ocurren en el backend (CTR_AuthLogout ↔ CE_TokenBlacklist):
    //   Paso 3: Validar token y autenticación de usuario
    //   Paso 4: Refresh token válido
    //   Paso 5: INSERT INTO token_blacklist (token, fecha)
    //   Paso 6: Token revocado en lista negra
  }
}
