import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { UserService } from '../../core/services/user.service';
import { TenantService } from '../../core/services/tenant.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="dashboard-wrapper">
      <!-- Welcome Header -->
      <div class="dashboard-header glass-panel mb-4">
        <div>
          <h1 class="page-title">
            ¡Bienvenido, {{ authService.currentUser()?.nombre }}!
          </h1>
          <p class="page-subtitle">
            Estás conectado en el centro <strong>{{ authService.currentTenant()?.nombre || 'Plataforma Global SIGEPSI' }}</strong>
            con el rol de <span class="badge badge-primary">{{ authService.currentUser()?.rol?.nombre || 'SuperAdmin' }}</span>
          </p>
        </div>
        <div class="status-chip">
          <i class="fa-solid fa-circle-check text-success"></i>
          <span>Sistema Operativo 100% Online</span>
        </div>
      </div>

      <!-- KPI Metrics Cards -->
      <div class="kpi-grid mb-4">
        <!-- Card 1: Users / Tenants -->
        <div class="kpi-card glass-panel">
          <div class="kpi-icon icon-cyan">
            <i class="fa-solid fa-users"></i>
          </div>
          <div class="kpi-data">
            <span class="kpi-label">{{ authService.isSuperAdmin() ? 'Centros Registrados' : 'Usuarios del Centro' }}</span>
            <h3 class="kpi-value">{{ totalCount() }}</h3>
          </div>
        </div>

        <!-- Card 2: Architecture -->
        <div class="kpi-card glass-panel">
          <div class="kpi-icon icon-purple">
            <i class="fa-solid fa-database"></i>
          </div>
          <div class="kpi-data">
            <span class="kpi-label">Aislamiento de Datos</span>
            <h3 class="kpi-value">Esquema Dedicado</h3>
          </div>
        </div>

        <!-- Card 3: Security Status -->
        <div class="kpi-card glass-panel">
          <div class="kpi-icon icon-emerald">
            <i class="fa-solid fa-shield-halved"></i>
          </div>
          <div class="kpi-data">
            <span class="kpi-label">Seguridad de Sesión</span>
            <h3 class="kpi-value">JWT HMAC-SHA256</h3>
          </div>
        </div>

        <!-- Card 4: RBAC Status -->
        <div class="kpi-card glass-panel">
          <div class="kpi-icon icon-amber">
            <i class="fa-solid fa-key"></i>
          </div>
          <div class="kpi-data">
            <span class="kpi-label">Control de Acceso</span>
            <h3 class="kpi-value">RBAC Dinámico</h3>
          </div>
        </div>
      </div>

      <!-- Quick Actions Grid -->
      <div class="actions-section">
        <h2 class="section-title mb-3">Accesos Directos del Sprint 0</h2>

        <div class="actions-grid">
          <!-- SuperAdmin Action: Manage Tenants -->
          <div *ngIf="authService.isSuperAdmin()" class="action-card glass-panel" routerLink="/tenants">
            <div class="action-icon">
              <i class="fa-solid fa-hospital-user"></i>
            </div>
            <h4>Gestión de Centros Psicológicos</h4>
            <p>Alta de nuevos centros, configuración de subdominios y suspensión de tenants.</p>
            <span class="action-link">Ir a Gestión de Centros <i class="fa-solid fa-arrow-right"></i></span>
          </div>

          <!-- Admin Centro Action: Users -->
          <div *ngIf="!authService.isSuperAdmin()" class="action-card glass-panel" routerLink="/users">
            <div class="action-icon">
              <i class="fa-solid fa-users-gear"></i>
            </div>
            <h4>Personal y Usuarios</h4>
            <p>Registro de psicólogos, recepcionistas y coordinadores clínicos del centro.</p>
            <span class="action-link">Administrar Personal <i class="fa-solid fa-arrow-right"></i></span>
          </div>

          <!-- Admin Centro Action: Roles & Permissions -->
          <div *ngIf="!authService.isSuperAdmin()" class="action-card glass-panel" routerLink="/roles">
            <div class="action-icon">
              <i class="fa-solid fa-id-card-clip"></i>
            </div>
            <h4>Matriz de Roles y Permisos (RBAC)</h4>
            <p>Configuración granular de accesos por rol para salvaguardar la privacidad clínica.</p>
            <span class="action-link">Configurar Permisos <i class="fa-solid fa-arrow-right"></i></span>
          </div>

          <!-- Admin Centro Action: Clinic Config -->
          <div *ngIf="!authService.isSuperAdmin()" class="action-card glass-panel" routerLink="/centro">
            <div class="action-icon">
              <i class="fa-solid fa-sliders"></i>
            </div>
            <h4>Configuración del Gabinete</h4>
            <p>Horarios de atención, datos institucionales y políticas de cancelación.</p>
            <span class="action-link">Editar Configuración <i class="fa-solid fa-arrow-right"></i></span>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .page-title { font-size: 1.6rem; font-weight: 800; margin-bottom: 4px; }
    .page-subtitle { font-size: 0.92rem; color: var(--text-muted); }
    .dashboard-header { padding: 24px 28px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; }
    .status-chip { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 600; padding: 6px 14px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 20px; color: #34d399; }
    .text-success { color: #34d399; }
    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; }
    .kpi-card { padding: 20px; display: flex; align-items: center; gap: 16px; }
    .kpi-icon { width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; }
    .icon-cyan { background: rgba(14, 165, 233, 0.15); color: #38bdf8; }
    .icon-purple { background: rgba(99, 102, 241, 0.15); color: #a5b4fc; }
    .icon-emerald { background: rgba(16, 185, 129, 0.15); color: #34d399; }
    .icon-amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
    .kpi-label { font-size: 0.78rem; font-weight: 700; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 1.3rem; font-weight: 800; color: var(--text-main); margin-top: 2px; }
    .section-title { font-size: 1.2rem; font-weight: 700; }
    .actions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; }
    .action-card { padding: 24px; cursor: pointer; text-decoration: none; display: flex; flex-direction: column; transition: var(--transition); }
    .action-card:hover { transform: translateY(-3px); border-color: var(--primary); box-shadow: var(--shadow-glow); }
    .action-icon { width: 44px; height: 44px; border-radius: 12px; background: rgba(255, 255, 255, 0.06); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: var(--primary); margin-bottom: 14px; }
    .action-card h4 { font-size: 1.05rem; font-weight: 700; margin-bottom: 6px; }
    .action-card p { font-size: 0.86rem; color: var(--text-muted); line-height: 1.4; flex: 1; margin-bottom: 14px; }
    .action-link { font-size: 0.85rem; font-weight: 600; color: var(--primary); display: flex; align-items: center; gap: 6px; }
    .mb-3 { margin-bottom: 12px; }
    .mb-4 { margin-bottom: 20px; }
  `]
})
export class DashboardComponent implements OnInit {
  totalCount = signal<number>(0);

  constructor(
    public authService: AuthService,
    private userService: UserService,
    private tenantService: TenantService
  ) {}

  ngOnInit() {
    if (this.authService.isSuperAdmin()) {
      this.tenantService.getAll().subscribe({
        next: (list: any[]) => this.totalCount.set(list.length),
        error: () => {}
      });
    } else {
      this.userService.getAll().subscribe({
        next: (list: any[]) => this.totalCount.set(list.length),
        error: () => {}
      });
    }
  }
}
