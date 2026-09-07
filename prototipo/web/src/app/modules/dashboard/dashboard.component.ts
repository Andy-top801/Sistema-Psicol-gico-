import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { UserService } from '../../core/services/user.service';
import { TenantService } from '../../core/services/tenant.service';
import { RoleService } from '../../core/services/role.service';
import { AgendaService } from '../../core/services/agenda.service';
import { DashboardKPIs, AlertaClinica } from '../../core/models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="dashboard-wrapper">
      <!-- Title Header (Exact to screenshot) -->
      <div class="dashboard-heading mb-4">
        <h1 class="dash-title">Dashboard</h1>
        <p class="dash-subtitle">Resumen general del sistema SIGEPSI.</p>
      </div>

      <!-- Top 4 KPI Cards (Exact to screenshot) -->
      <div class="stats-row mb-4">
        <!-- Card 1: Centros Registrados -->
        <div class="stat-card">
          <div class="stat-icon-box box-mint">
            <i class="fa-solid fa-building"></i>
          </div>
          <div class="stat-data">
            <div class="stat-number">{{ totalCentros() }}</div>
            <div class="stat-label">Centros registrados</div>
          </div>
        </div>

        <!-- Card 2: Usuarios Activos -->
        <div class="stat-card">
          <div class="stat-icon-box box-blue">
            <i class="fa-solid fa-users"></i>
          </div>
          <div class="stat-data">
            <div class="stat-number">{{ totalUsuarios() }}</div>
            <div class="stat-label">Usuarios activos</div>
          </div>
        </div>

        <!-- Card 3: Roles Configurados -->
        <div class="stat-card">
          <div class="stat-icon-box box-peach">
            <i class="fa-solid fa-shield-halved"></i>
          </div>
          <div class="stat-data">
            <div class="stat-number">{{ totalRoles() }}</div>
            <div class="stat-label">Roles configurados</div>
          </div>
        </div>

        <!-- Card 4: Permisos Definidos (Highlighted green outline in screenshot) -->
        <div class="stat-card card-highlight">
          <div class="stat-icon-box box-emerald">
            <i class="fa-solid fa-circle-check"></i>
          </div>
          <div class="stat-data">
            <div class="stat-number">{{ totalPermisos() }}</div>
            <div class="stat-label">Permisos definidos</div>
          </div>
        </div>
      </div>

      <!-- Accesos Rápidos (Exact to screenshot) -->
      <div class="section-block mb-4">
        <h2 class="section-heading mb-3">Accesos rápidos</h2>
        <div class="quick-actions-row">
          <!-- Registrar Centro -->
          <a routerLink="/tenants" class="quick-card">
            <div class="quick-icon-circle">
              <i class="fa-solid fa-plus"></i>
            </div>
            <div class="quick-meta">
              <h4 class="quick-title">Registrar centro</h4>
              <p class="quick-sub">Aprovisionar un nuevo centro</p>
            </div>
          </a>

          <!-- Gestionar Usuarios -->
          <a routerLink="/users" class="quick-card">
            <div class="quick-icon-circle">
              <i class="fa-solid fa-user-plus"></i>
            </div>
            <div class="quick-meta">
              <h4 class="quick-title">Gestionar usuarios</h4>
              <p class="quick-sub">Añadir o editar perfiles</p>
            </div>
          </a>

          <!-- Configurar Roles -->
          <a routerLink="/roles" class="quick-card">
            <div class="quick-icon-circle">
              <i class="fa-solid fa-shield-halved"></i>
            </div>
            <div class="quick-meta">
              <h4 class="quick-title">Configurar roles</h4>
              <p class="quick-sub">Definir accesos del sistema</p>
            </div>
          </a>
        </div>
      </div>

      <!-- Información del Sistema (Exact to screenshot) -->
      <div class="section-block mb-4">
        <h2 class="section-heading mb-3">Información del sistema</h2>
        <div class="system-info-card">
          <div class="info-row">
            <span class="info-label">Versión</span>
            <span class="info-value">SIGEPSI v1.0 — Sprint 0</span>
          </div>
          <div class="info-row">
            <span class="info-label">Arquitectura</span>
            <span class="info-value">Multi-Tenant (django-tenants)</span>
          </div>
          <div class="info-row">
            <span class="info-label">Esquema Activo</span>
            <span class="info-value font-mono">{{ authService.currentTenant()?.schema_name || 'public' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Base de Datos</span>
            <span class="info-value">PostgreSQL (Esquemas Aislados)</span>
          </div>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- SECCIÓN SPRINT 1: MÉTRICAS CLÍNICAS Y OPERATIVAS (CU9 / CU10)        -->
      <!-- ==================================================================== -->
      <div *ngIf="!authService.isSuperAdmin() || authService.isInTenantContext()" class="clinical-section mt-4">
        <div class="section-header-flex mb-3">
          <h2 class="section-heading">
            <i class="fa-solid fa-chart-line text-primary"></i> Métricas Clínicas y Operativas (Sprint 1)
          </h2>
          <span class="badge badge-primary">Mes en Curso</span>
        </div>

        <div class="stats-row mb-4">
          <!-- Citas Hoy -->
          <div class="stat-card">
            <div class="stat-icon-box box-blue">
              <i class="fa-solid fa-calendar-day"></i>
            </div>
            <div class="stat-data">
              <div class="stat-number">{{ kpis()?.citas_hoy || 0 }}</div>
              <div class="stat-label">Citas hoy</div>
            </div>
          </div>

          <!-- Total Citas Mes -->
          <div class="stat-card">
            <div class="stat-icon-box box-mint">
              <i class="fa-solid fa-calendar-check"></i>
            </div>
            <div class="stat-data">
              <div class="stat-number">{{ kpis()?.total_citas_mes || 0 }}</div>
              <div class="stat-label">Total sesiones mes</div>
            </div>
          </div>

          <!-- Ausentismo -->
          <div class="stat-card">
            <div class="stat-icon-box box-peach">
              <i class="fa-solid fa-user-xmark"></i>
            </div>
            <div class="stat-data">
              <div class="stat-number">{{ kpis()?.tasa_ausentismo_pct || 0 }}%</div>
              <div class="stat-label">Tasa de ausentismo</div>
            </div>
          </div>

          <!-- Alertas Clínicas -->
          <div class="stat-card">
            <div class="stat-icon-box box-red">
              <i class="fa-solid fa-triangle-exclamation"></i>
            </div>
            <div class="stat-data">
              <div class="stat-number">{{ kpis()?.alertas_activas?.length || 0 }}</div>
              <div class="stat-label">Alertas activas</div>
            </div>
          </div>
        </div>

        <!-- Panel de Alertas Tempranas (si hay) -->
        <div *ngIf="kpis()?.alertas_activas && (kpis()?.alertas_activas?.length || 0) > 0" class="alerts-panel clean-card mb-4">
          <div class="alerts-header">
            <div class="d-flex align-center gap-2">
              <i class="fa-solid fa-bell text-warning"></i>
              <h3 class="alerts-title">Alertas Clínicas Tempranas de Ausentismo</h3>
            </div>
            <span class="badge badge-warning">Atención Prioritaria Requerida</span>
          </div>

          <div class="alerts-list">
            <div *ngFor="let alerta of kpis()?.alertas_activas" class="alert-item">
              <div class="alert-item-info">
                <span class="badge" [ngClass]="getSeveridadBadgeClass(alerta.severidad)">
                  {{ alerta.severidad }}
                </span>
                <div class="alert-text">
                  <strong>Paciente: {{ alerta.paciente_nombre }}</strong> (Exp: {{ alerta.codigo_expediente }})
                  <p class="mb-0 text-muted">{{ alerta.descripcion }}</p>
                </div>
              </div>
              <button class="btn btn-secondary btn-sm" (click)="resolverAlertaCU10(alerta.id)">
                <i class="fa-solid fa-check-double text-success"></i> Marcar Resuelta
              </button>
            </div>
          </div>
        </div>

        <!-- Gráficos y Tablas Clínicas -->
        <div class="analytics-row mb-4">
          <div class="clean-card p-4">
            <h4 class="card-subtitle mb-3">Distribución de Consultas por Estado</h4>
            <div class="progress-stack" *ngIf="kpis()?.distribucion_estados">
              <div class="status-bar-item">
                <div class="bar-header">
                  <span>Programadas</span>
                  <strong>{{ kpis()?.distribucion_estados?.PROGRAMADA || 0 }}</strong>
                </div>
                <div class="progress-track"><div class="progress-fill fill-cyan" [style.width.%]="calcularPorcentaje(kpis()?.distribucion_estados?.PROGRAMADA)"></div></div>
              </div>

              <div class="status-bar-item">
                <div class="bar-header">
                  <span>Confirmadas</span>
                  <strong>{{ kpis()?.distribucion_estados?.CONFIRMADA || 0 }}</strong>
                </div>
                <div class="progress-track"><div class="progress-fill fill-emerald" [style.width.%]="calcularPorcentaje(kpis()?.distribucion_estados?.CONFIRMADA)"></div></div>
              </div>

              <div class="status-bar-item">
                <div class="bar-header">
                  <span>Realizadas</span>
                  <strong>{{ kpis()?.distribucion_estados?.REALIZADA || 0 }}</strong>
                </div>
                <div class="progress-track"><div class="progress-fill fill-blue" [style.width.%]="calcularPorcentaje(kpis()?.distribucion_estados?.REALIZADA)"></div></div>
              </div>

              <div class="status-bar-item">
                <div class="bar-header">
                  <span>Inasistencias</span>
                  <strong>{{ kpis()?.distribucion_estados?.INASISTENCIA || 0 }}</strong>
                </div>
                <div class="progress-track"><div class="progress-fill fill-amber" [style.width.%]="calcularPorcentaje(kpis()?.distribucion_estados?.INASISTENCIA)"></div></div>
              </div>

              <div class="status-bar-item">
                <div class="bar-header">
                  <span>Canceladas</span>
                  <strong>{{ kpis()?.distribucion_estados?.CANCELADA || 0 }}</strong>
                </div>
                <div class="progress-track"><div class="progress-fill fill-red" [style.width.%]="calcularPorcentaje(kpis()?.distribucion_estados?.CANCELADA)"></div></div>
              </div>
            </div>
          </div>

          <div class="clean-card p-4">
            <h4 class="card-subtitle mb-3">Ocupación y Horas de Terapeutas</h4>
            <div class="table-container">
              <table class="custom-table table-compact">
                <thead>
                  <tr>
                    <th>Terapeuta</th>
                    <th>Citas</th>
                    <th>Horas Atendidas</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let psi of kpis()?.ocupacion_por_psicologo">
                    <td><strong>{{ psi.nombre }}</strong></td>
                    <td><span class="badge badge-info">{{ psi.total_citas }}</span></td>
                    <td>{{ psi.horas_atendidas }} hrs</td>
                  </tr>
                  <tr *ngIf="!kpis()?.ocupacion_por_psicologo || kpis()?.ocupacion_por_psicologo?.length === 0">
                    <td colspan="3" class="text-center text-muted">Sin actividad registrada en el período.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Accesos Rápidos Clínicos -->
        <div class="section-block">
          <h2 class="section-heading mb-3">Módulos Clínicos</h2>
          <div class="quick-actions-row">
            <a routerLink="/agenda" class="quick-card">
              <div class="quick-icon-circle">
                <i class="fa-solid fa-calendar-check text-primary"></i>
              </div>
              <div class="quick-meta">
                <h4 class="quick-title">Agenda y Citas</h4>
                <p class="quick-sub">Calendario y teleconsultas</p>
              </div>
            </a>
            <a routerLink="/psicologos" class="quick-card">
              <div class="quick-icon-circle">
                <i class="fa-solid fa-user-doctor text-primary"></i>
              </div>
              <div class="quick-meta">
                <h4 class="quick-title">Directorio Psicólogos</h4>
                <p class="quick-sub">Especialidades y disponibilidad</p>
              </div>
            </a>
            <a routerLink="/pacientes" class="quick-card">
              <div class="quick-icon-circle">
                <i class="fa-solid fa-folder-open text-primary"></i>
              </div>
              <div class="quick-meta">
                <h4 class="quick-title">Expedientes Pacientes</h4>
                <p class="quick-sub">Fichas clínicas y tutores</p>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-wrapper {
      max-width: 1360px;
      margin: 0 auto;
    }
    .dash-title {
      font-size: 1.85rem;
      font-weight: 800;
      color: #12271f;
      margin-bottom: 2px;
      letter-spacing: -0.02em;
    }
    .dash-subtitle {
      font-size: 0.95rem;
      color: #557164;
    }
    .section-heading {
      font-size: 1.15rem;
      font-weight: 700;
      color: #12271f;
    }

    /* 4 Top KPI Cards */
    .stats-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
    }
    @media (max-width: 1024px) {
      .stats-row { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 600px) {
      .stats-row { grid-template-columns: 1fr; }
    }
    .stat-card {
      background: #ffffff;
      border: 1px solid #e3ebe6;
      border-radius: 20px;
      padding: 22px 24px;
      display: flex;
      align-items: center;
      gap: 18px;
      box-shadow: 0 2px 10px rgba(15, 41, 34, 0.03);
      transition: var(--transition);
    }
    .stat-card:hover {
      border-color: #c4d7cd;
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(15, 41, 34, 0.06);
    }
    .stat-card.card-highlight {
      border: 1.5px solid #1fa158;
    }
    .stat-icon-box {
      width: 48px;
      height: 48px;
      border-radius: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      flex-shrink: 0;
    }
    .box-mint {
      background: #e6f5ed;
      color: #19734e;
    }
    .box-blue {
      background: #e8f1fd;
      color: #2563eb;
    }
    .box-peach {
      background: #fef2e6;
      color: #d97706;
    }
    .box-emerald {
      background: #e6f7ee;
      color: #16a34a;
    }
    .box-red {
      background: #fee2e2;
      color: #dc2626;
    }
    .stat-number {
      font-size: 1.95rem;
      font-weight: 800;
      color: #12271f;
      line-height: 1.1;
      font-family: 'Outfit', sans-serif;
    }
    .stat-label {
      font-size: 0.86rem;
      color: #557164;
      margin-top: 4px;
      font-weight: 500;
    }

    /* Quick Actions */
    .quick-actions-row {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
    }
    @media (max-width: 900px) {
      .quick-actions-row { grid-template-columns: 1fr; }
    }
    .quick-card {
      background: #ffffff;
      border: 1px solid #e3ebe6;
      border-radius: 18px;
      padding: 20px 22px;
      display: flex;
      align-items: center;
      gap: 16px;
      text-decoration: none;
      box-shadow: 0 2px 10px rgba(15, 41, 34, 0.03);
      transition: var(--transition);
      cursor: pointer;
    }
    .quick-card:hover {
      border-color: #19734e;
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(15, 41, 34, 0.06);
    }
    .quick-icon-circle {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: #f4f7f5;
      border: 1px solid #e3ebe6;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1rem;
      color: #12271f;
      flex-shrink: 0;
      transition: var(--transition);
    }
    .quick-card:hover .quick-icon-circle {
      background: #e6f5ed;
      color: #19734e;
      border-color: #c7e6d7;
    }
    .quick-title {
      font-size: 0.98rem;
      font-weight: 700;
      color: #12271f;
      margin-bottom: 2px;
    }
    .quick-sub {
      font-size: 0.82rem;
      color: #557164;
      margin: 0;
    }

    /* System Info Card */
    .system-info-card {
      background: #ffffff;
      border: 1px solid #e3ebe6;
      border-radius: 20px;
      padding: 10px 26px;
      box-shadow: 0 2px 10px rgba(15, 41, 34, 0.03);
    }
    .info-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 0;
      border-bottom: 1px solid #edf3ef;
      font-size: 0.90rem;
    }
    .info-row:last-child {
      border-bottom: none;
    }
    .info-label {
      color: #557164;
      font-weight: 500;
    }
    .info-value {
      font-weight: 700;
      color: #12271f;
    }

    /* Clinical Analytics */
    .analytics-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
    }
    .card-subtitle {
      font-size: 1rem;
      font-weight: 700;
      color: #12271f;
    }
    .progress-stack { display: flex; flex-direction: column; gap: 12px; }
    .status-bar-item { display: flex; flex-direction: column; gap: 4px; }
    .bar-header { display: flex; justify-content: space-between; font-size: 0.84rem; color: #557164; }
    .progress-track { height: 8px; border-radius: 4px; background: #e8f0eb; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 4px; }
    .fill-cyan { background: #06b6d4; }
    .fill-emerald { background: #10b981; }
    .fill-blue { background: #3b82f6; }
    .fill-amber { background: #f59e0b; }
    .fill-red { background: #ef4444; }

    /* Table Compact */
    .table-compact th, .table-compact td { padding: 10px 14px; font-size: 0.85rem; }

    /* Early Warning Alerts */
    .alerts-panel { padding: 20px; border-radius: 16px; border: 1px solid #fde68a; background: #fffdf5; }
    .alerts-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 8px; }
    .alerts-title { font-size: 1.05rem; font-weight: 700; margin: 0; color: #92400e; }
    .alerts-list { display: flex; flex-direction: column; gap: 10px; }
    .alert-item { display: flex; justify-content: space-between; align-items: center; background: #ffffff; padding: 12px 16px; border-radius: 10px; border: 1px solid #fde68a; gap: 12px; flex-wrap: wrap; }
    .alert-item-info { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 220px; }
    .alert-text { font-size: 0.88rem; }
    .section-header-flex { display: flex; justify-content: space-between; align-items: center; }
    .p-4 { padding: 22px; }
    .mb-0 { margin-bottom: 0; }
    .mb-2 { margin-bottom: 8px; }
    .mb-3 { margin-bottom: 14px; }
    .mb-4 { margin-bottom: 24px; }
    .mt-4 { margin-top: 24px; }
    .align-center { align-items: center; }
    .d-flex { display: flex; }
    .gap-2 { gap: 8px; }
    .font-mono { font-family: var(--font-mono); }
    .text-center { text-align: center; }

    @media (max-width: 640px) {
      .p-4 { padding: 16px; }
      .stat-card { padding: 16px 18px; }
      .stat-number { font-size: 1.6rem; }
      .dash-title { font-size: 1.5rem; }
      .alert-item { flex-direction: column; align-items: stretch; }
    }
  `]
})
export class DashboardComponent implements OnInit {
  totalCentros = signal<number>(1);
  totalUsuarios = signal<number>(1);
  totalRoles = signal<number>(3);
  totalPermisos = signal<number>(6);
  kpis = signal<DashboardKPIs | null>(null);

  constructor(
    public authService: AuthService,
    private userService: UserService,
    private tenantService: TenantService,
    private roleService: RoleService,
    private agendaService: AgendaService
  ) {}

  ngOnInit() {
    this.cargarMetricasGlobales();
    if (this.authService.isInTenantContext() || !this.authService.isSuperAdmin()) {
      this.cargarDashboardKPIsCU9CU10();
    }
  }

  cargarMetricasGlobales() {
    this.tenantService.getAll().subscribe({
      next: (list) => this.totalCentros.set(list?.length || 1),
      error: () => {}
    });

    this.userService.getAll().subscribe({
      next: (list) => {
        const activos = list?.filter(u => u.activo)?.length ?? list?.length;
        this.totalUsuarios.set(activos || 1);
      },
      error: () => {}
    });

    this.roleService.getRoles().subscribe({
      next: (list) => this.totalRoles.set(list?.length || 3),
      error: () => {}
    });

    this.roleService.getPermisos().subscribe({
      next: (list) => this.totalPermisos.set(list?.length || 6),
      error: () => {}
    });
  }

  /**
   * CU9 / CU10: Dashboard Clínico y Alertas Tempranas (HU-20, HU-21)
   */
  cargarDashboardKPIsCU9CU10(): void {
    this.agendaService.getDashboardKPIs('mes').subscribe({
      next: (res) => this.kpis.set(res),
      error: (err) => console.error('Error al cargar KPIs del dashboard', err)
    });
  }

  resolverAlertaCU10(alertaId: string): void {
    this.agendaService.resolverAlerta(alertaId).subscribe({
      next: () => this.cargarDashboardKPIsCU9CU10(),
      error: (err) => console.error('Error al resolver alerta clínica', err)
    });
  }

  calcularPorcentaje(cantidad: number | undefined): number {
    const total = this.kpis()?.total_citas_mes || 0;
    if (!total || !cantidad) return 0;
    return Math.round((cantidad / total) * 100);
  }

  getSeveridadBadgeClass(sev: string): string {
    switch (sev) {
      case 'CRITICA': return 'badge-danger';
      case 'ALTA': return 'badge-warning';
      case 'MEDIA': return 'badge-info';
      default: return 'badge-secondary';
    }
  }
}

