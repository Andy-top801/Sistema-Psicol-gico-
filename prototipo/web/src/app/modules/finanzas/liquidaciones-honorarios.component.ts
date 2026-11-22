import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FinanzasService } from '../../core/services/finanzas.service';
import { ClinicaService } from '../../core/services/clinica.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-liquidaciones-honorarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="liq-page">
      <div class="liq-header">
        <h1><i class="fa-solid fa-file-invoice-dollar"></i> Liquidación de Honorarios a Psicólogos (Bs.)</h1>
        <p class="subtitle">HU-54: Cálculo periódico de sesiones REALIZADAS con retención institucional y boleta oficial PDF.</p>
      </div>

      <div *ngIf="mensaje()" class="alert-box ok">{{ mensaje() }}</div>
      <div *ngIf="error()" class="alert-box err">{{ error() }}</div>

      <!-- Generador (Solo Admin Centro / SuperAdmin) -->
      <div *ngIf="authService.isAdminCentro() || authService.isSuperAdmin()" class="card">
        <h3><i class="fa-solid fa-calculator"></i> Calcular Nueva Liquidación</h3>
        <div class="form-row">
          <div>
            <label>Psicólogo</label>
            <select [(ngModel)]="form.psicologo_id" class="inp">
              <option value="">Seleccione un profesional...</option>
              <option *ngFor="let p of psicologos()" [value]="p.id">{{ p.usuario?.nombre }} {{ p.usuario?.apellido }} ({{ p.numero_colegiado }})</option>
            </select>
          </div>
          <div>
            <label>Desde</label>
            <input type="date" [(ngModel)]="form.fecha_inicio" class="inp" />
          </div>
          <div>
            <label>Hasta</label>
            <input type="date" [(ngModel)]="form.fecha_fin" class="inp" />
          </div>
          <div>
            <label>Comisión Centro (%)</label>
            <input type="number" min="0" max="100" [(ngModel)]="form.porcentaje_comision_centro" class="inp" />
          </div>
          <button type="button" class="btn-outline" (click)="previsualizar()">Previsualizar</button>
          <button type="button" class="btn-teal" (click)="emitir()">Emitir Liquidación</button>
        </div>

        <div *ngIf="preview() as pv" class="preview-box">
          <div class="split-bar">
            <span><strong>{{ pv.psicologo_nombre }}</strong> — {{ pv.total_sesiones }} sesiones pendientes</span>
            <span>Reparto: <strong>{{ 100 - pv.porcentaje_comision_centro }}% Psicólogo</strong> / {{ pv.porcentaje_comision_centro }}% Centro</span>
          </div>
          <div class="kpi-3">
            <div><span>Monto Bruto</span><strong>Bs. {{ pv.monto_bruto | number:'1.2-2' }}</strong></div>
            <div><span>Retención Centro</span><strong>Bs. {{ pv.comision_centro | number:'1.2-2' }}</strong></div>
            <div><span>Neto a Pagar</span><strong class="emerald">Bs. {{ pv.monto_neto_psicologo | number:'1.2-2' }}</strong></div>
          </div>
        </div>
      </div>

      <!-- Historial de Liquidaciones -->
      <div class="card">
        <h3><i class="fa-solid fa-list"></i> Historial de Liquidaciones Emitidas</h3>
        <div class="table-wrap">
          <table class="tbl">
            <thead>
              <tr>
                <th>Código</th>
                <th>Psicólogo</th>
                <th>Periodo</th>
                <th class="num">Sesiones</th>
                <th class="num">Bruto (Bs.)</th>
                <th class="num">Comisión (Bs.)</th>
                <th class="num">Neto (Bs.)</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let l of liquidaciones()">
                <td><strong>{{ l.codigo_liquidacion }}</strong></td>
                <td>{{ l.psicologo_nombre }}</td>
                <td>{{ l.fecha_inicio }} a {{ l.fecha_fin }}</td>
                <td class="num">{{ l.total_sesiones }}</td>
                <td class="num">{{ l.monto_bruto | number:'1.2-2' }}</td>
                <td class="num">{{ l.comision_centro | number:'1.2-2' }}</td>
                <td class="num emerald"><strong>Bs. {{ l.monto_neto_psicologo | number:'1.2-2' }}</strong></td>
                <td><span class="badge" [class.paid]="l.estado === 'PAGADA'">{{ l.estado }}</span></td>
                <td class="actions">
                  <button *ngIf="l.estado === 'GENERADA' && (authService.isAdminCentro() || authService.isSuperAdmin())"
                          type="button" class="btn-xs pay" (click)="marcarPagada(l)">Pagar</button>
                  <button type="button" class="btn-xs pdf" (click)="descargarBoleta(l)">Boleta PDF</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .liq-page { padding: 1.5rem; max-width: 1350px; margin: 0 auto; display: flex; flex-direction: column; gap: 1.25rem; }
    .liq-header h1 { margin: 0; font-size: 1.45rem; color: #0f2922; }
    .subtitle { margin: .25rem 0 0; color: #64748b; font-size: .86rem; }
    .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; }
    .card h3 { margin: 0 0 1rem; color: #0f2922; font-size: 1.02rem; }
    .form-row { display: flex; flex-wrap: wrap; gap: .75rem; align-items: flex-end; }
    .form-row label { display: block; font-size: .75rem; font-weight: 600; color: #475569; margin-bottom: .25rem; }
    .inp { padding: .45rem .65rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: .86rem; }
    .btn-teal { padding: .5rem .9rem; background: #0d9488; color: #fff; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }
    .btn-outline { padding: .5rem .85rem; background: #fff; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer; }
    .preview-box { margin-top: 1rem; padding: .9rem; background: #f0fdfa; border: 1px solid #99f6e4; border-radius: 8px; }
    .split-bar { display: flex; justify-content: space-between; font-size: .86rem; margin-bottom: .75rem; flex-wrap: wrap; }
    .kpi-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: .75rem; }
    .kpi-3 span { display: block; font-size: .75rem; color: #64748b; }
    .kpi-3 strong { font-size: 1.1rem; }
    .emerald { color: #047857; }
    .table-wrap { overflow-x: auto; }
    .tbl { width: 100%; border-collapse: collapse; font-size: .84rem; }
    .tbl th, .tbl td { padding: .55rem .5rem; border-bottom: 1px solid #e2e8f0; text-align: left; }
    .tbl .num { text-align: right; }
    .badge { padding: .2rem .55rem; border-radius: 999px; font-size: .74rem; font-weight: 700; background: #fef3c7; color: #92400e; }
    .badge.paid { background: #d1fae5; color: #065f46; }
    .actions { display: flex; gap: .35rem; }
    .btn-xs { padding: .28rem .55rem; border-radius: 5px; border: none; font-size: .75rem; cursor: pointer; font-weight: 600; }
    .btn-xs.pay { background: #0d9488; color: #fff; }
    .btn-xs.pdf { background: #b91c1c; color: #fff; }
    .alert-box { padding: .75rem 1rem; border-radius: 8px; font-size: .88rem; }
    .alert-box.ok { background: #ecfdf5; color: #065f46; border: 1px solid #6ee7b7; }
    .alert-box.err { background: #fef2f2; color: #991b1b; border: 1px solid #fca5a5; }
  `]
})
export class LiquidacionesHonorariosComponent implements OnInit {
  psicologos = signal<any[]>([]);
  liquidaciones = signal<any[]>([]);
  preview = signal<any | null>(null);
  mensaje = signal('');
  error = signal('');

  form = {
    psicologo_id: '',
    fecha_inicio: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().slice(0, 10),
    fecha_fin: new Date().toISOString().slice(0, 10),
    porcentaje_comision_centro: 30,
  };

  constructor(
    private finanzasService: FinanzasService,
    private clinicaService: ClinicaService,
    public authService: AuthService,
  ) {}

  ngOnInit(): void {
    this.cargarLiquidaciones();
    if (this.authService.isAdminCentro() || this.authService.isSuperAdmin()) {
      this.clinicaService.getPsicologos().subscribe({
        next: (res: any) => this.psicologos.set(Array.isArray(res) ? res : (res.results || [])),
      });
    }
  }

  cargarLiquidaciones(): void {
    this.finanzasService.getLiquidaciones().subscribe({
      next: (rows) => this.liquidaciones.set(rows),
      error: (err) => this.error.set(err?.error?.detail || 'Error al cargar liquidaciones.'),
    });
  }

  previsualizar(): void {
    this.error.set('');
    this.mensaje.set('');
    if (!this.form.psicologo_id) {
      this.error.set('Seleccione un psicólogo.');
      return;
    }
    this.finanzasService.previewLiquidacion(
      this.form.psicologo_id,
      this.form.fecha_inicio,
      this.form.fecha_fin,
      this.form.porcentaje_comision_centro,
    ).subscribe({
      next: (pv) => this.preview.set(pv),
      error: (err) => this.error.set(err?.error?.detail || 'No se pudo previsualizar.'),
    });
  }

  emitir(): void {
    this.error.set('');
    this.mensaje.set('');
    if (!this.form.psicologo_id) {
      this.error.set('Seleccione un psicólogo.');
      return;
    }
    this.finanzasService.generarLiquidacion(this.form).subscribe({
      next: (liq) => {
        this.mensaje.set(`Liquidación ${liq.codigo_liquidacion} emitida por Bs. ${liq.monto_neto_psicologo}.`);
        this.preview.set(null);
        this.cargarLiquidaciones();
      },
      error: (err) => this.error.set(err?.error?.detail || 'Error al emitir liquidación.'),
    });
  }

  marcarPagada(liq: any): void {
    const ref = window.prompt(`Ingrese referencia bancaria para pagar ${liq.codigo_liquidacion} (Bs. ${liq.monto_neto_psicologo}):`);
    if (!ref || !ref.trim()) return;
    this.finanzasService.pagarLiquidacion(liq.id, ref.trim()).subscribe({
      next: () => {
        this.mensaje.set(`Liquidación ${liq.codigo_liquidacion} marcada como PAGADA.`);
        this.cargarLiquidaciones();
      },
      error: (err) => this.error.set(err?.error?.detail || 'No se pudo marcar como pagada.'),
    });
  }

  descargarBoleta(liq: any): void {
    this.finanzasService.descargarBoletaPdf(liq.id).subscribe({
      next: (blob) => this.finanzasService.triggerBlobDownload(blob, `boleta_${liq.codigo_liquidacion}.pdf`),
    });
  }
}
