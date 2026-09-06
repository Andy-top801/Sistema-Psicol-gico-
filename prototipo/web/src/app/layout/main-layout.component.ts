import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../core/services/auth.service';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="app-layout">
      <!-- Sidebar -->
      <aside class="app-sidebar">
        <!-- Brand -->
        <div class="sidebar-brand">
          <div class="brand-badge">
            <i class="fa-solid fa-brain"></i>
          </div>
          <div>
            <h2 class="brand-name">SIGEPSI</h2>
            <span class="tenant-badge" [class.superadmin]="authService.isSuperAdmin()">
              {{ authService.currentTenant()?.nombre || 'Plataforma Global' }}
            </span>
          </div>
        </div>

        <!-- Navigation Links -->
        <nav class="sidebar-nav">
          <div class="nav-section-title">Menú Principal</div>
          
          <a routerLink="/dashboard" routerLinkActive="active" class="nav-link">
            <i class="fa-solid fa-chart-pie nav-icon"></i>
            <span>Dashboard</span>
          </a>

          <!-- SuperAdmin Links -->
          <div *ngIf="authService.isSuperAdmin()">
            <div class="nav-section-title">Administración SaaS</div>
            <a routerLink="/tenants" routerLinkActive="active" class="nav-link">
              <i class="fa-solid fa-hospital-user nav-icon"></i>
              <span>Centros Psicológicos</span>
            </a>
          </div>

          <!-- Gestión Institucional: visible para Admin Centro O para SuperAdmin dentro de un tenant -->
          <div *ngIf="!authService.isSuperAdmin() || authService.isInTenantContext()">
            <div class="nav-section-title">Gestión Institucional</div>

            <!-- Botón para que el SuperAdmin salga del contexto del tenant -->
            <div *ngIf="authService.isSuperAdmin() && authService.isInTenantContext()" class="tenant-context-badge">
              <div class="context-info">
                <i class="fa-solid fa-building"></i>
                <span>{{ authService.currentTenant()?.nombre }}</span>
              </div>
              <button class="btn-exit-tenant" (click)="exitTenantContext()" title="Volver a la vista global">
                <i class="fa-solid fa-arrow-left"></i> Salir del Centro
              </button>
            </div>

            <a routerLink="/users" routerLinkActive="active" class="nav-link">
              <i class="fa-solid fa-users-gear nav-icon"></i>
              <span>Personal y Usuarios</span>
            </a>
            <a routerLink="/roles" routerLinkActive="active" class="nav-link">
              <i class="fa-solid fa-id-card-clip nav-icon"></i>
              <span>Roles y Permisos (RBAC)</span>
            </a>
            <a routerLink="/centro" routerLinkActive="active" class="nav-link">
              <i class="fa-solid fa-sliders nav-icon"></i>
              <span>Configuración del Centro</span>
            </a>
          </div>
        </nav>

        <!-- User Footer Profile -->
        <div class="sidebar-footer">
          <div class="user-profile">
            <div class="user-avatar">
              {{ authService.currentUser()?.nombre?.charAt(0) || 'U' }}
            </div>
            <div class="user-info">
              <span class="user-name">{{ authService.currentUser()?.nombre }} {{ authService.currentUser()?.apellido }}</span>
              <span class="user-role">{{ authService.currentUser()?.rol?.nombre || 'SuperAdmin' }}</span>
            </div>
            <button class="btn-logout" (click)="onLogout()" title="Cerrar Sesión">
              <i class="fa-solid fa-right-from-bracket"></i>
            </button>
          </div>
        </div>
      </aside>

      <!-- Main Content Area -->
      <div class="app-main">
        <!-- Top Navbar -->
        <header class="app-header glass-panel">
          <div class="header-left">
            <div class="schema-indicator">
              <span class="schema-dot"></span>
              <span class="schema-text">
                Esquema Activo: <strong>{{ authService.currentTenant()?.schema_name || 'public' }}</strong>
              </span>
            </div>
          </div>
          <div class="header-right">
            <span class="badge badge-info">
              <i class="fa-solid fa-shield"></i> {{ authService.currentUser()?.rol?.nombre || 'SuperAdmin' }}
            </span>
            <button class="btn btn-secondary btn-sm" (click)="onLogout()">
              <i class="fa-solid fa-arrow-right-from-bracket"></i> Salir
            </button>
          </div>
        </header>

        <!-- Router Outlet Container -->
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
    }
    .app-sidebar {
      width: 280px;
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border-glass);
      display: flex;
      flex-direction: column;
      position: fixed;
      top: 0;
      bottom: 0;
      left: 0;
      z-index: 100;
    }
    .sidebar-brand {
      padding: 24px 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid var(--border-glass);
    }
    .brand-badge {
      width: 42px;
      height: 42px;
      background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.3rem;
      color: white;
      box-shadow: 0 4px 15px var(--primary-glow);
    }
    .brand-name {
      font-size: 1.25rem;
      font-weight: 800;
      line-height: 1.1;
    }
    .tenant-badge {
      font-size: 0.72rem;
      color: var(--primary);
      display: block;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 170px;
    }
    .tenant-badge.superadmin {
      color: #a855f7;
    }
    .sidebar-nav {
      flex: 1;
      padding: 20px 14px;
      overflow-y: auto;
    }
    .nav-section-title {
      font-size: 0.72rem;
      font-weight: 800;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.8px;
      padding: 12px 12px 6px;
    }
    .nav-link {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      font-size: 0.92rem;
      font-weight: 600;
      color: var(--text-muted);
      border-radius: 10px;
      text-decoration: none;
      transition: var(--transition);
      margin-bottom: 4px;
    }
    .nav-link:hover {
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-main);
    }
    .nav-link.active {
      background: linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%);
      color: var(--primary);
      border: 1px solid rgba(14, 165, 233, 0.3);
    }
    .nav-icon {
      font-size: 1.1rem;
      width: 22px;
      text-align: center;
    }
    .sidebar-footer {
      padding: 16px;
      border-top: 1px solid var(--border-glass);
      background: rgba(10, 14, 23, 0.6);
    }
    .user-profile {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .user-avatar {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: linear-gradient(135deg, #0ea5e9, #6366f1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      color: white;
    }
    .user-info {
      flex: 1;
      overflow: hidden;
    }
    .user-name {
      display: block;
      font-size: 0.86rem;
      font-weight: 700;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .user-role {
      display: block;
      font-size: 0.72rem;
      color: var(--text-dim);
    }
    .btn-logout {
      background: transparent;
      border: none;
      color: var(--text-dim);
      font-size: 1rem;
      cursor: pointer;
      padding: 6px;
      border-radius: 6px;
      transition: var(--transition);
    }
    .btn-logout:hover {
      color: #f87171;
      background: rgba(239, 68, 68, 0.1);
    }
    .app-main {
      margin-left: 280px;
      flex: 1;
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    .app-header {
      margin: 16px 24px 0;
      padding: 12px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-radius: 12px;
    }
    .schema-indicator {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.84rem;
      color: var(--text-muted);
    }
    .schema-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--success);
      box-shadow: 0 0 10px var(--success);
    }
    .header-right {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .content-body {
      padding: 24px;
      flex: 1;
    }
    .tenant-context-badge {
      background: rgba(168, 85, 247, 0.12);
      border: 1px solid rgba(168, 85, 247, 0.3);
      border-radius: 10px;
      padding: 10px 12px;
      margin: 0 0 10px 0;
    }
    .context-info {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.82rem;
      font-weight: 700;
      color: #c4b5fd;
      margin-bottom: 8px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .context-info i {
      font-size: 0.9rem;
    }
    .btn-exit-tenant {
      display: flex;
      align-items: center;
      gap: 6px;
      width: 100%;
      padding: 6px 10px;
      font-size: 0.78rem;
      font-weight: 700;
      color: #fca5a5;
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.25);
      border-radius: 6px;
      cursor: pointer;
      transition: var(--transition);
    }
    .btn-exit-tenant:hover {
      background: rgba(239, 68, 68, 0.2);
      color: #fecaca;
    }
  `]
})
export class MainLayoutComponent {
  constructor(public authService: AuthService, private router: Router) {}

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
