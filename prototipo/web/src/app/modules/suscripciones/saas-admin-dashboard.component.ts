import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SubscriptionService } from '../../core/services/subscription.service';

@Component({
  selector: 'app-saas-admin-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="saas-page">
      <div class="saas-header">
        <div>
          <h1><i class="fa-solid fa-crown"></i> Consola SuperAdmin — Suscripciones SaaS & Facturación (USD)</h1>
          <p class="subtitle">HU-55: Control de planes Stripe (Básico $29, Profesional $59, Empresarial $99), MRR en USD, cupos y FacturaSaaS.</p>
        </div>
        <button type="button" class="btn-outline" (click)="cargar()"><i class="fa-solid fa-rotate"></i> Actualizar</button>
      </div>

      <div *ngIf="mensaje()" class="alert ok">{{ mensaje() }}</div>
      <div *ngIf="error()" class="alert err">{{ error() }}</div>

      <div *ngIf="dashboard() as d">
        <div class="kpi-4">
          <div class="kpi-card emerald-l">
            <span>MRR Mensual (USD)</span>
            <strong>$ {{ d.kpis.mrr_usd | number:'1.2-2' }}</strong>
            <small>ARR Estimado: $ {{ d.kpis.arr_estimado_usd | number:'1.2-2' }}</small>
          </div>
          <div class="kpi-card">
            <span>Centros Activos</span>
            <strong>{{ d.kpis.tenants_activos }} / {{ d.kpis.tenants_totales }}</strong>
            <small>Esquemas PostgreSQL aislados</small>
          </div>
          <div class="kpi-card">
            <span>Total Facturado (USD)</span>
            <strong>$ {{ d.kpis.total_facturado_usd | number:'1.2-2' }}</strong>
            <small>Facturas SaaS verificadas</small>
          </div>
          <div class="kpi-card">
            <span>Distribución de Planes</span>
            <div class="chips">
              <span class="chip">Básico: {{ d.kpis.distribucion_planes.basico || 0 }}</span>
              <span class="chip pro">Pro: {{ d.kpis.distribucion_planes.profesional || 0 }}</span>
              <span class="chip emp">Emp: {{ d.kpis.distribucion_planes.empresarial || 0 }}</span>
            </div>
          </div>
        </div>

        <div class="card">
          <h3><i class="fa-solid fa-building"></i> Centros Psicológicos Tenant y Suscripciones</h3>
          <div class="table-wrap">
            <table class="tbl">
              <thead>
                <tr>
                  <th>Centro / Schema</th>
                  <th>Plan</th>
                  <th>Mensualidad</th>
                  <th>Estado</th>
                  <th>Cupos (Psico / Pac)</th>
                  <th>Renovación</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let t of d.tenants">
                  <td>
                    <strong>{{ t.nombre }}</strong><br />
                    <small class="muted">{{ t.schema_name }} · {{ t.email_contacto }}</small>
                  </td>
                  <td>
                    <select [ngModel]="t.plan_id" (ngModelChange)="cambiarPlan(t, $event)" class="sel">
                      <option value="basico">Básico ($29)</option>
                      <option value="profesional">Profesional ($59)</option>
                      <option value="empresarial">Empresarial ($99)</option>
                    </select>
                  </td>
                  <td><strong>$ {{ t.precio_mensual_usd | number:'1.2-2' }}</strong></td>
                  <td>
                    <span class="badge" [class.act]="t.estado_suscripcion === 'ACTIVA'">{{ t.estado_suscripcion }}</span>
                  </td>
                  <td>
                    <span [class.warn]="t.cupos.alerta_cupo_psicologos">{{ t.cupos.psicologos_activos }}/{{ t.cupos.max_psicologos }} psico</span> ·
                    <span [class.warn]="t.cupos.alerta_cupo_pacientes">{{ t.cupos.pacientes_activos }}/{{ t.cupos.max_pacientes }} pac</span>
                  </td>
                  <td>{{ t.fecha_renovacion || '-' }}</td>
                  <td class="acts">
                    <button type="button" class="btn-xs" (click)="verFacturas(t)">Ver Facturas USD</button>
                    <button type="button" class="btn-xs" [class.danger]="t.activo" (click)="toggleEstado(t)">
                      {{ t.activo ? 'Suspender' : 'Reactivar' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Drawer / Panel de Facturas USD del Tenant -->
        <div *ngIf="tenantFacturas() as tf" class="card drawer">
          <div class="drawer-head">
            <h3><i class="fa-solid fa-file-invoice"></i> Historial de Facturas SaaS (USD) — {{ tf.nombre }}</h3>
            <button type="button" class="btn-outline" (click)="tenantFacturas.set(null)">Cerrar</button>
          </div>
          <table class="tbl">
            <thead>
              <tr><th>N° Factura</th><th>Plan</th><th>Monto (USD)</th><th>Estado</th><th>Stripe Session ID</th><th>Emisión</th><th>Renovación</th></tr>
            </thead>
            <tbody>
              <tr *ngFor="let f of tf.facturas">
                <td><strong>{{ f.numero_factura }}</strong></td>
                <td>{{ f.plan }}</td>
                <td><strong>$ {{ f.monto_usd | number:'1.2-2' }}</strong></td>
                <td><span class="badge act">{{ f.estado }}</span></td>
                <td><code>{{ f.stripe_session_id }}</code></td>
                <td>{{ f.fecha_emision }}</td>
                <td>{{ f.fecha_renovacion || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .saas-page { padding: 1.5rem; max-width: 1400px; margin: 0 auto; display: flex; flex-direction: column; gap: 1.25rem; }
    .saas-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
    .saas-header h1 { margin: 0; font-size: 1.45rem; color: #0f2922; }
    .subtitle { margin: .25rem 0 0; color: #64748b; font-size: .86rem; }
    .kpi-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
    @media (max-width: 980px) { .kpi-4 { grid-template-columns: 1fr; } }
    .kpi-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem 1.2rem; display: flex; flex-direction: column; gap: .3rem; }
    .emerald-l { border-left: 4px solid #0d9488; }
    .kpi-card span { font-size: .78rem; color: #64748b; font-weight: 600; }
    .kpi-card strong { font-size: 1.45rem; color: #0f172a; }
    .chips { display: flex; gap: .35rem; flex-wrap: wrap; margin-top: .25rem; }
    .chip { padding: .2rem .5rem; border-radius: 6px; font-size: .75rem; background: #f1f5f9; font-weight: 600; }
    .chip.pro { background: #ccfbf1; color: #0f766e; }
    .chip.emp { background: #e0e7ff; color: #3730a3; }
    .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; }
    .card h3 { margin: 0 0 1rem; font-size: 1.02rem; color: #0f2922; }
    .table-wrap { overflow-x: auto; }
    .tbl { width: 100%; border-collapse: collapse; font-size: .84rem; }
    .tbl th, .tbl td { padding: .55rem .5rem; border-bottom: 1px solid #e2e8f0; text-align: left; }
    .muted { color: #64748b; }
    .warn { color: #b45309; font-weight: 700; }
    .sel { padding: .3rem .5rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: .82rem; }
    .badge { padding: .2rem .55rem; border-radius: 999px; font-size: .74rem; font-weight: 700; background: #fee2e2; color: #991b1b; }
    .badge.act { background: #d1fae5; color: #065f46; }
    .acts { display: flex; gap: .35rem; }
    .btn-xs { padding: .3rem .6rem; border: 1px solid #cbd5e1; background: #fff; border-radius: 6px; cursor: pointer; font-size: .76rem; font-weight: 600; }
    .btn-xs.danger { color: #b91c1c; border-color: #fca5a5; }
    .btn-outline { padding: .45rem .8rem; background: #fff; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer; }
    .drawer { border: 2px solid #0d9488; }
    .drawer-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: .75rem; }
    .alert { padding: .75rem 1rem; border-radius: 8px; font-size: .88rem; }
    .alert.ok { background: #ecfdf5; color: #065f46; }
    .alert.err { background: #fef2f2; color: #991b1b; }
  `]
})
export class SaasAdminDashboardComponent implements OnInit {
  dashboard = signal<any | null>(null);
  tenantFacturas = signal<any | null>(null);
  mensaje = signal('');
  error = signal('');

  constructor(private subscriptionService: SubscriptionService) {}

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.error.set('');
    this.subscriptionService.getAdminDashboard().subscribe({
      next: (res) => this.dashboard.set(res),
      error: (err) => this.error.set(err?.error?.detail || 'No se pudo cargar la consola SaaS.'),
    });
  }

  cambiarPlan(tenant: any, nuevoPlan: string): void {
    this.subscriptionService.actualizarPlanTenant(tenant.tenant_id, { plan: nuevoPlan }).subscribe({
      next: () => {
        this.mensaje.set(`Plan de ${tenant.nombre} actualizado a ${nuevoPlan.toUpperCase()}.`);
        this.cargar();
      },
      error: (err) => this.error.set(err?.error?.error || 'Error al actualizar plan.'),
    });
  }

  toggleEstado(tenant: any): void {
    const nuevoEstado = tenant.activo ? 'cancelada' : 'activa';
    this.subscriptionService.actualizarPlanTenant(tenant.tenant_id, { estado: nuevoEstado }).subscribe({
      next: () => {
        this.mensaje.set(`Estado de ${tenant.nombre} actualizado a ${nuevoEstado.toUpperCase()}.`);
        this.cargar();
      },
      error: (err) => this.error.set(err?.error?.error || 'Error al actualizar estado.'),
    });
  }

  verFacturas(tenant: any): void {
    this.tenantFacturas.set(tenant);
  }
}
