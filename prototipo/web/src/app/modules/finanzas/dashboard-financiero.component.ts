import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { FinanzasService } from '../../core/services/finanzas.service';

@Component({
  selector: 'app-dashboard-financiero',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="dash-page">
      <div class="dash-header">
        <div>
          <h1><i class="fa-solid fa-chart-line"></i> Dashboard Financiero y Centro Integral de Reportes (Bs.)</h1>
          <p class="subtitle">HU-53: Ingreso Bruto vs. Honorarios = Margen Neto Real, estadísticas mínimas de 2 años (24+ meses) y todos los reportes.</p>
        </div>
        <div class="horizonte-bar">
          <button type="button" *ngFor="let h of horizontes" [class.active]="horizonte === h.id" (click)="cambiarHorizonte(h.id)">
            {{ h.label }}
          </button>
        </div>
      </div>

      <div *ngIf="error()" class="alert-err">{{ error() }}</div>

      <div *ngIf="data() as d">
        <!-- 4 KPIs Principales -->
        <div class="kpi-grid">
          <div class="kpi-card">
            <span class="kpi-lbl">Ingreso Bruto Cobrado</span>
            <strong class="kpi-val">Bs. {{ d.kpis.ingreso_bruto | number:'1.2-2' }}</strong>
            <small class="yoy" [class.pos]="d.comparativa_yoy.variacion_pct.ingreso_bruto >= 0">
              YoY: {{ d.comparativa_yoy.variacion_pct.ingreso_bruto >= 0 ? '+' : '' }}{{ d.comparativa_yoy.variacion_pct.ingreso_bruto }}%
            </small>
          </div>
          <div class="kpi-card">
            <span class="kpi-lbl">Honorarios Profesionales</span>
            <strong class="kpi-val">Bs. {{ d.kpis.honorarios_psicologos | number:'1.2-2' }}</strong>
            <small>Comisión retenida: Bs. {{ d.kpis.comision_retenida_centro | number:'1.2-2' }}</small>
          </div>
          <div class="kpi-card highlight-emerald">
            <span class="kpi-lbl">Margen Neto Real del Centro</span>
            <strong class="kpi-val emerald">Bs. {{ d.kpis.margen_neto_centro | number:'1.2-2' }}</strong>
            <small class="yoy" [class.pos]="d.comparativa_yoy.variacion_pct.margen_neto >= 0">
              YoY: {{ d.comparativa_yoy.variacion_pct.margen_neto >= 0 ? '+' : '' }}{{ d.comparativa_yoy.variacion_pct.margen_neto }}%
            </small>
          </div>
          <div class="kpi-card highlight-amber">
            <span class="kpi-lbl">Cuentas por Cobrar / Morosidad</span>
            <strong class="kpi-val amber">Bs. {{ d.kpis.cartera_por_cobrar | number:'1.2-2' }}</strong>
            <small>Índice morosidad: {{ d.kpis.indice_morosidad_pct }}% ({{ d.kpis.pacientes_morosos }} pacientes)</small>
          </div>
        </div>

        <!-- Gráfica Longitudinal >= 24 meses -->
        <div class="card">
          <div class="card-head">
            <h3><i class="fa-solid fa-chart-column"></i> Evolución Mensual ({{ d.rango.meses_cubiertos }} meses: {{ d.rango.fecha_desde }} a {{ d.rango.fecha_hasta }})</h3>
            <div class="legend">
              <span><i class="dot bruto"></i> Ingreso Bruto</span>
              <span><i class="dot hon"></i> Honorarios</span>
              <span><i class="dot neto"></i> Margen Neto</span>
            </div>
          </div>
          <div class="bars-scroll">
            <div class="bar-group" *ngFor="let m of d.serie_mensual">
              <div class="bars">
                <div class="bar bruto" [style.height.%]="calcPct(m.ingreso_bruto)" [title]="'Bruto: Bs. ' + m.ingreso_bruto"></div>
                <div class="bar hon" [style.height.%]="calcPct(m.honorarios)" [title]="'Honorarios: Bs. ' + m.honorarios"></div>
                <div class="bar neto" [style.height.%]="calcPct(m.margen_neto)" [title]="'Margen: Bs. ' + m.margen_neto"></div>
              </div>
              <span class="bar-lbl">{{ m.periodo }}</span>
            </div>
          </div>
        </div>

        <!-- Métodos de Pago + Rendimiento por Psicólogo -->
        <div class="grid-2">
          <div class="card">
            <h3><i class="fa-solid fa-credit-card"></i> Recaudación por Método de Pago</h3>
            <table class="tbl">
              <thead><tr><th>Método</th><th class="num">Pagos</th><th class="num">Total (Bs.)</th></tr></thead>
              <tbody>
                <tr *ngFor="let mp of d.distribucion_metodo_pago">
                  <td><strong>{{ mp.metodo_pago }}</strong></td>
                  <td class="num">{{ mp.cantidad }}</td>
                  <td class="num">Bs. {{ mp.total_bob | number:'1.2-2' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="card">
            <h3><i class="fa-solid fa-user-doctor"></i> Rendimiento Económico por Psicólogo</h3>
            <table class="tbl">
              <thead><tr><th>Psicólogo</th><th class="num">Sesiones</th><th class="num">Bruto</th><th class="num">Honorarios</th><th class="num">Margen</th></tr></thead>
              <tbody>
                <tr *ngFor="let p of d.rendimiento_psicologos">
                  <td>{{ p.nombre }}</td>
                  <td class="num">{{ p.sesiones_realizadas }}</td>
                  <td class="num">{{ p.ingreso_generado_bob | number:'1.2-2' }}</td>
                  <td class="num">{{ p.honorarios_liquidados_bob | number:'1.2-2' }}</td>
                  <td class="num emerald"><strong>{{ p.margen_centro_bob | number:'1.2-2' }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Centro Integral de Todos los Reportes y Consultas -->
        <div class="card">
          <div class="card-head">
            <div>
              <h3><i class="fa-solid fa-folder-tree"></i> Centro Integral de Reportes y Consultas (PDF / Excel / CSV)</h3>
              <p class="subtitle">Acceso unificado a todas las fuentes clínicas, operativas, IA y financieras del centro.</p>
            </div>
            <a routerLink="/finanzas/caja" class="btn-teal">Abrir Extracto Bancario 20 Años</a>
          </div>
          <div class="report-grid">
            <div class="report-tile" *ngFor="let r of d.catalogo_reportes">
              <div class="rep-title">{{ r.label }}</div>
              <div class="rep-actions">
                <a [routerLink]="['/reportes', r.fuente]" class="btn-xs">Ver</a>
                <button type="button" class="btn-xs pdf" (click)="descargar(r.fuente, 'pdf')">PDF</button>
                <button type="button" class="btn-xs xls" (click)="descargar(r.fuente, 'excel')">Excel</button>
                <button type="button" class="btn-xs" (click)="descargar(r.fuente, 'csv')">CSV</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dash-page { padding: 1.5rem; max-width: 1400px; margin: 0 auto; display: flex; flex-direction: column; gap: 1.25rem; }
    .dash-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
    .dash-header h1 { margin: 0; font-size: 1.45rem; color: #0f2922; }
    .subtitle { margin: .25rem 0 0; color: #64748b; font-size: .86rem; }
    .horizonte-bar { display: flex; gap: .4rem; }
    .horizonte-bar button { padding: .45rem .8rem; border: 1px solid #cbd5e1; background: #fff; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: .82rem; }
    .horizonte-bar button.active { background: #0d9488; color: #fff; border-color: #0d9488; }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
    @media (max-width: 980px) { .kpi-grid, .grid-2 { grid-template-columns: 1fr !important; } }
    .kpi-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem 1.2rem; display: flex; flex-direction: column; gap: .25rem; }
    .highlight-emerald { border-left: 4px solid #059669; }
    .highlight-amber { border-left: 4px solid #d97706; }
    .kpi-lbl { font-size: .8rem; color: #64748b; font-weight: 600; }
    .kpi-val { font-size: 1.4rem; color: #0f172a; }
    .emerald { color: #047857 !important; }
    .amber { color: #b45309 !important; }
    .yoy { font-size: .78rem; color: #b91c1c; font-weight: 600; }
    .yoy.pos { color: #047857; }
    .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; }
    .card-head { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: .75rem; margin-bottom: 1rem; }
    .card h3 { margin: 0 0 .75rem; font-size: 1.02rem; color: #0f2922; }
    .card-head h3 { margin: 0; }
    .legend { display: flex; gap: 1rem; font-size: .8rem; color: #475569; }
    .dot { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; }
    .dot.bruto, .bar.bruto { background: #0f2922; }
    .dot.hon, .bar.hon { background: #94a3b8; }
    .dot.neto, .bar.neto { background: #0d9488; }
    .bars-scroll { display: flex; gap: .6rem; overflow-x: auto; padding: .5rem 0; align-items: flex-end; min-height: 190px; }
    .bar-group { display: flex; flex-direction: column; align-items: center; min-width: 44px; }
    .bars { display: flex; gap: 3px; align-items: flex-end; height: 150px; }
    .bar { width: 10px; border-radius: 3px 3px 0 0; min-height: 2px; }
    .bar-lbl { font-size: .68rem; color: #64748b; margin-top: .35rem; white-space: nowrap; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1.3fr; gap: 1.25rem; }
    .tbl { width: 100%; border-collapse: collapse; font-size: .84rem; }
    .tbl th, .tbl td { padding: .5rem; border-bottom: 1px solid #e2e8f0; text-align: left; }
    .tbl .num { text-align: right; }
    .report-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: .75rem; }
    .report-tile { border: 1px solid #e2e8f0; border-radius: 8px; padding: .75rem; background: #f8fafc; display: flex; flex-direction: column; justify-content: space-between; gap: .6rem; }
    .rep-title { font-weight: 600; font-size: .86rem; color: #0f172a; }
    .rep-actions { display: flex; gap: .35rem; flex-wrap: wrap; }
    .btn-xs { padding: .28rem .55rem; border-radius: 5px; border: 1px solid #cbd5e1; background: #fff; font-size: .75rem; cursor: pointer; text-decoration: none; color: #334155; font-weight: 600; }
    .btn-xs.pdf { background: #b91c1c; color: #fff; border-color: #b91c1c; }
    .btn-xs.xls { background: #15803d; color: #fff; border-color: #15803d; }
    .btn-teal { padding: .5rem .9rem; background: #0d9488; color: #fff; border-radius: 8px; text-decoration: none; font-size: .84rem; font-weight: 600; }
    .alert-err { padding: .75rem; background: #fef2f2; color: #991b1b; border-radius: 8px; }
  `]
})
export class DashboardFinancieroComponent implements OnInit {
  data = signal<any | null>(null);
  error = signal('');
  horizonte = '24m';
  maxSerieVal = 1;

  horizontes = [
    { id: '12m', label: '12 Meses' },
    { id: '24m', label: '24 Meses (2 Años)' },
    { id: '36m', label: '36 Meses (3 Años)' },
    { id: 'all', label: 'Todo el Historial' },
  ];

  constructor(private finanzasService: FinanzasService) {}

  ngOnInit(): void {
    this.cargar();
  }

  cambiarHorizonte(h: string): void {
    this.horizonte = h;
    this.cargar();
  }

  cargar(): void {
    this.error.set('');
    this.finanzasService.getDashboardFinanciero({ horizonte: this.horizonte }).subscribe({
      next: (res) => {
        const vals = (res.serie_mensual || []).map((m: any) => Math.max(m.ingreso_bruto || 0, m.honorarios || 0, 1));
        this.maxSerieVal = Math.max(1, ...vals);
        this.data.set(res);
      },
      error: (err) => this.error.set(err?.error?.detail || 'No se pudo cargar el dashboard financiero.'),
    });
  }

  calcPct(val: number): number {
    return Math.max(2, Math.min(100, Math.round(((val || 0) / this.maxSerieVal) * 100)));
  }

  descargar(fuente: string, formato: 'pdf' | 'excel' | 'csv'): void {
    const ext = formato === 'excel' ? 'xlsx' : formato;
    this.finanzasService.descargarReporte(fuente, formato).subscribe({
      next: (blob) => this.finanzasService.triggerBlobDownload(blob, `reporte_${fuente}.${ext}`),
      error: () => this.error.set(`Error al exportar ${fuente} en ${formato.toUpperCase()}.`),
    });
  }
}
