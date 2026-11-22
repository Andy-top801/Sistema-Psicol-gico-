import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FinanzasService } from '../../core/services/finanzas.service';

@Component({
  selector: 'app-caja-clinica',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="fin-page">
      <div class="fin-header">
        <div>
          <h1><i class="fa-solid fa-cash-register"></i> Caja Clínica y Extracto Histórico (Bs.)</h1>
          <p class="subtitle">HU-52: Registro de cobros, recibos PDF verificables y extracto histórico tipo bancario (hasta 20 años).</p>
        </div>
        <div class="tab-pills">
          <button type="button" class="tab-btn" [class.active]="tabActiva() === 'caja'" (click)="tabActiva.set('caja')">
            <i class="fa-solid fa-receipt"></i> Caja y Cobros
          </button>
          <button type="button" class="tab-btn" [class.active]="tabActiva() === 'extracto'" (click)="abrirExtracto()">
            <i class="fa-solid fa-building-columns"></i> Extracto Tipo Banco (20 Años)
          </button>
        </div>
      </div>

      <div *ngIf="mensaje()" class="alert-box success">{{ mensaje() }}</div>
      <div *ngIf="error()" class="alert-box error">{{ error() }}</div>

      <!-- TAB 1: CAJA Y ESTADO DE CUENTA -->
      <div *ngIf="tabActiva() === 'caja'" class="grid-2col">
        <div class="card">
          <div class="card-head">
            <h3><i class="fa-solid fa-wallet"></i> Cuentas de Pacientes (BOB)</h3>
            <div class="search-row">
              <input type="text" [(ngModel)]="busqueda" (keyup.enter)="cargarCuentas()" placeholder="Buscar expediente o paciente..." class="input-sm" />
              <button type="button" class="btn-outline" (click)="cargarCuentas(true)">Sincronizar</button>
            </div>
          </div>

          <div class="table-wrap">
            <table class="fin-table">
              <thead>
                <tr>
                  <th>Expediente</th>
                  <th>Paciente</th>
                  <th class="num">Cargado (Bs.)</th>
                  <th class="num">Pagado (Bs.)</th>
                  <th class="num">Saldo (Bs.)</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let c of cuentas()" [class.selected]="cuentaSeleccionada()?.paciente_id === c.paciente_id">
                  <td><strong>{{ c.codigo_expediente }}</strong></td>
                  <td>{{ c.paciente_nombre }}</td>
                  <td class="num">{{ c.total_cargado | number:'1.2-2' }}</td>
                  <td class="num">{{ c.total_pagado | number:'1.2-2' }}</td>
                  <td class="num" [class.debt]="+c.saldo_pendiente > 0">{{ c.saldo_pendiente | number:'1.2-2' }}</td>
                  <td>
                    <button type="button" class="btn-teal-sm" (click)="seleccionarCuenta(c)">Cobrar / Ver</button>
                  </td>
                </tr>
                <tr *ngIf="cuentas().length === 0">
                  <td colspan="6" class="empty">Sin cuentas registradas. Presiona Sincronizar.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <h3><i class="fa-solid fa-hand-holding-dollar"></i> Registrar Cobro en Bs.</h3>
          <div *ngIf="cuentaSeleccionada() as cta; else seleccionarAviso">
            <div class="kpi-mini-grid">
              <div class="kpi-mini">
                <span>Total Cargado</span>
                <strong>Bs. {{ cta.total_cargado | number:'1.2-2' }}</strong>
              </div>
              <div class="kpi-mini">
                <span>Total Pagado</span>
                <strong class="emerald">Bs. {{ cta.total_pagado | number:'1.2-2' }}</strong>
              </div>
              <div class="kpi-mini">
                <span>Saldo Pendiente</span>
                <strong class="amber">Bs. {{ cta.saldo_pendiente | number:'1.2-2' }}</strong>
              </div>
            </div>

            <div class="form-grid">
              <label>Método de Pago</label>
              <div class="method-pills">
                <button type="button" *ngFor="let m of metodos" [class.active]="pagoForm.metodo_pago === m.value" (click)="pagoForm.metodo_pago = m.value">
                  {{ m.label }}
                </button>
              </div>

              <label>Monto a Cobrar (Bs.)</label>
              <input type="number" step="0.01" min="0.01" [(ngModel)]="pagoForm.monto" class="input-full" />

              <label>Referencia Bancaria / Voucher (opcional)</label>
              <input type="text" [(ngModel)]="pagoForm.referencia_externa" placeholder="Ej: QR-BNB-88412" class="input-full" />

              <label>Observaciones</label>
              <input type="text" [(ngModel)]="pagoForm.observaciones" placeholder="Nota de caja" class="input-full" />

              <button type="button" class="btn-primary-full" [disabled]="guardando()" (click)="confirmarCobro()">
                <i class="fa-solid fa-check-circle"></i> {{ guardando() ? 'Procesando...' : 'Confirmar Cobro y Emitir Recibo' }}
              </button>
            </div>

            <h4 class="sub-head">Pagos Recientes del Paciente</h4>
            <table class="fin-table">
              <thead>
                <tr>
                  <th>Recibo</th>
                  <th>Fecha</th>
                  <th>Método</th>
                  <th class="num">Monto (Bs.)</th>
                  <th>PDF</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let p of pagosPaciente()">
                  <td><strong>{{ p.numero_recibo }}</strong></td>
                  <td>{{ p.fecha_pago | date:'dd/MM/yyyy HH:mm' }}</td>
                  <td>{{ p.metodo_pago_display }}</td>
                  <td class="num">{{ p.monto | number:'1.2-2' }}</td>
                  <td>
                    <button type="button" class="btn-icon" (click)="descargarRecibo(p)" title="Descargar Recibo PDF">
                      <i class="fa-solid fa-file-pdf"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <ng-template #seleccionarAviso>
            <p class="empty">Selecciona un paciente de la tabla izquierda para ver su estado de cuenta y registrar cobros.</p>
          </ng-template>
        </div>
      </div>

      <!-- TAB 2: EXTRACTO HISTÓRICO TIPO BANCO (HASTA 20 AÑOS) -->
      <div *ngIf="tabActiva() === 'extracto'" class="card">
        <div class="card-head wrap">
          <div>
            <h3><i class="fa-solid fa-building-columns"></i> Extracto Histórico de Pagos Tipo Bancario (hasta 20 años)</h3>
            <p class="subtitle">Saldo acumulado cronológico, subtotales anuales y exportación PDF multipágina / Excel streaming.</p>
          </div>
          <div class="export-actions">
            <button type="button" class="btn-pdf" (click)="exportarExtracto('pdf')"><i class="fa-solid fa-file-pdf"></i> PDF Multipágina</button>
            <button type="button" class="btn-excel" (click)="exportarExtracto('excel')"><i class="fa-solid fa-file-excel"></i> Excel Streaming</button>
            <button type="button" class="btn-outline" (click)="exportarExtracto('csv')"><i class="fa-solid fa-file-csv"></i> CSV</button>
          </div>
        </div>

        <div class="filter-bar">
          <div>
            <label>Preset Rango</label>
            <div class="preset-row">
              <button type="button" class="btn-chip" (click)="aplicarRangoAnios(1)">1 Año</button>
              <button type="button" class="btn-chip" (click)="aplicarRangoAnios(2)">2 Años</button>
              <button type="button" class="btn-chip" (click)="aplicarRangoAnios(10)">10 Años</button>
              <button type="button" class="btn-chip active" (click)="aplicarRangoAnios(20)">20 Años</button>
            </div>
          </div>
          <div>
            <label>Desde</label>
            <input type="date" [(ngModel)]="extractoFiltros.fecha_desde" class="input-sm" />
          </div>
          <div>
            <label>Hasta</label>
            <input type="date" [(ngModel)]="extractoFiltros.fecha_hasta" class="input-sm" />
          </div>
          <div>
            <label>Paciente</label>
            <select [(ngModel)]="extractoFiltros.paciente_id" class="input-sm">
              <option value="">Todos (Consolidado del Centro)</option>
              <option *ngFor="let c of cuentas()" [value]="c.paciente_id">{{ c.codigo_expediente }} — {{ c.paciente_nombre }}</option>
            </select>
          </div>
          <button type="button" class="btn-teal-sm" (click)="cargarExtracto(1)">Consultar</button>
        </div>

        <div *ngIf="extracto() as ext">
          <div class="kpi-4grid">
            <div class="kpi-card"><span>Saldo Inicial</span><strong>Bs. {{ ext.resumen.saldo_inicial | number:'1.2-2' }}</strong></div>
            <div class="kpi-card"><span>Total Cargos (Debe)</span><strong>Bs. {{ ext.resumen.total_debe | number:'1.2-2' }}</strong></div>
            <div class="kpi-card"><span>Total Pagos (Haber)</span><strong class="emerald">Bs. {{ ext.resumen.total_haber | number:'1.2-2' }}</strong></div>
            <div class="kpi-card"><span>Saldo Final ({{ ext.resumen.total_registros }} movs.)</span><strong class="amber">Bs. {{ ext.resumen.saldo_final | number:'1.2-2' }}</strong></div>
          </div>

          <div class="table-wrap">
            <table class="fin-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Expediente / Paciente</th>
                  <th>N° Documento</th>
                  <th>Concepto</th>
                  <th>Método</th>
                  <th class="num">Debe (Bs.)</th>
                  <th class="num">Haber (Bs.)</th>
                  <th class="num">Saldo Acumulado</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let m of ext.movimientos">
                  <td>{{ m.fecha }}</td>
                  <td><strong>{{ m.expediente }}</strong> {{ m.paciente_nombre }}</td>
                  <td>{{ m.numero_documento }}</td>
                  <td>{{ m.concepto }}</td>
                  <td>{{ m.metodo_pago }}</td>
                  <td class="num">{{ m.debe ? (m.debe | number:'1.2-2') : '-' }}</td>
                  <td class="num emerald">{{ m.haber ? (m.haber | number:'1.2-2') : '-' }}</td>
                  <td class="num"><strong>Bs. {{ m.saldo_acumulado | number:'1.2-2' }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pager">
            <button type="button" class="btn-outline" [disabled]="ext.paginacion.page <= 1" (click)="cargarExtracto(ext.paginacion.page - 1)">Anterior</button>
            <span>Página {{ ext.paginacion.page }} de {{ ext.paginacion.total_paginas }} ({{ ext.paginacion.total_registros }} registros)</span>
            <button type="button" class="btn-outline" [disabled]="ext.paginacion.page >= ext.paginacion.total_paginas" (click)="cargarExtracto(ext.paginacion.page + 1)">Siguiente</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .fin-page { padding: 1.5rem; max-width: 1400px; margin: 0 auto; }
    .fin-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.25rem; }
    .fin-header h1 { font-size: 1.45rem; color: #0f2922; margin: 0; }
    .subtitle { color: #64748b; font-size: .88rem; margin: .25rem 0 0; }
    .tab-pills { display: flex; gap: .5rem; }
    .tab-btn { padding: .55rem 1rem; border: 1px solid #cbd5e1; background: #fff; border-radius: 8px; cursor: pointer; font-weight: 600; color: #334155; }
    .tab-btn.active { background: #0d9488; color: #fff; border-color: #0d9488; }
    .grid-2col { display: grid; grid-template-columns: 1.2fr 1fr; gap: 1.25rem; }
    @media (max-width: 980px) { .grid-2col { grid-template-columns: 1fr; } }
    .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; }
    .card-head { display: flex; justify-content: space-between; align-items: center; gap: .75rem; margin-bottom: 1rem; }
    .card-head.wrap { flex-wrap: wrap; }
    .search-row, .export-actions, .preset-row { display: flex; gap: .5rem; align-items: center; flex-wrap: wrap; }
    .filter-bar { display: flex; gap: .75rem; flex-wrap: wrap; align-items: flex-end; margin-bottom: 1rem; padding: .75rem; background: #f8fafc; border-radius: 8px; }
    .filter-bar label { display: block; font-size: .75rem; font-weight: 600; color: #475569; margin-bottom: .25rem; }
    .kpi-mini-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: .5rem; margin-bottom: 1rem; }
    .kpi-mini, .kpi-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: .75rem; }
    .kpi-mini span, .kpi-card span { display: block; font-size: .75rem; color: #64748b; }
    .kpi-mini strong, .kpi-card strong { font-size: 1.05rem; color: #0f172a; }
    .kpi-4grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: .75rem; margin-bottom: 1rem; }
    .emerald { color: #047857 !important; }
    .amber, .debt { color: #b45309 !important; font-weight: 700; }
    .form-grid { display: flex; flex-direction: column; gap: .55rem; }
    .method-pills { display: flex; gap: .4rem; flex-wrap: wrap; }
    .method-pills button { padding: .4rem .75rem; border: 1px solid #cbd5e1; background: #fff; border-radius: 999px; cursor: pointer; font-size: .82rem; }
    .method-pills button.active { background: #0f2922; color: #fff; border-color: #0f2922; }
    .input-sm, .input-full { padding: .45rem .65rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: .88rem; }
    .input-full { width: 100%; box-sizing: border-box; }
    .btn-primary-full { margin-top: .5rem; padding: .65rem; background: #0d9488; color: #fff; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
    .btn-teal-sm { padding: .35rem .7rem; background: #0d9488; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: .8rem; }
    .btn-outline { padding: .4rem .75rem; background: #fff; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer; font-size: .82rem; }
    .btn-pdf { padding: .45rem .8rem; background: #b91c1c; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: .82rem; }
    .btn-excel { padding: .45rem .8rem; background: #15803d; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: .82rem; }
    .btn-chip { padding: .3rem .65rem; border: 1px solid #cbd5e1; background: #fff; border-radius: 6px; cursor: pointer; font-size: .78rem; }
    .btn-chip.active { background: #0d9488; color: #fff; border-color: #0d9488; }
    .btn-icon { background: none; border: none; color: #b91c1c; cursor: pointer; font-size: 1rem; }
    .table-wrap { overflow-x: auto; }
    .fin-table { width: 100%; border-collapse: collapse; font-size: .84rem; }
    .fin-table th, .fin-table td { padding: .55rem .5rem; border-bottom: 1px solid #e2e8f0; text-align: left; }
    .fin-table th { background: #f1f5f9; font-weight: 600; color: #334155; }
    .fin-table .num { text-align: right; }
    .fin-table tr.selected { background: #f0fdfa; }
    .pager { display: flex; justify-content: space-between; align-items: center; margin-top: 1rem; font-size: .85rem; }
    .sub-head { margin: 1.25rem 0 .5rem; font-size: .95rem; color: #0f2922; }
    .empty { text-align: center; color: #64748b; padding: 1.5rem; }
    .alert-box { padding: .75rem 1rem; border-radius: 8px; margin-bottom: 1rem; font-size: .88rem; }
    .alert-box.success { background: #ecfdf5; color: #065f46; border: 1px solid #6ee7b7; }
    .alert-box.error { background: #fef2f2; color: #991b1b; border: 1px solid #fca5a5; }
  `]
})
export class CajaClinicaComponent implements OnInit {
  tabActiva = signal<'caja' | 'extracto'>('caja');
  cuentas = signal<any[]>([]);
  cuentaSeleccionada = signal<any | null>(null);
  pagosPaciente = signal<any[]>([]);
  extracto = signal<any | null>(null);
  guardando = signal(false);
  mensaje = signal('');
  error = signal('');
  busqueda = '';

  metodos = [
    { value: 'EFECTIVO', label: 'Efectivo' },
    { value: 'QR_BANCARIO', label: 'QR Bancario' },
    { value: 'TRANSFERENCIA', label: 'Transferencia' },
    { value: 'TARJETA_STRIPE', label: 'Tarjeta' },
  ];

  pagoForm = {
    monto: 150,
    metodo_pago: 'QR_BANCARIO',
    referencia_externa: '',
    observaciones: '',
  };

  extractoFiltros = {
    paciente_id: '',
    fecha_desde: '2007-01-01',
    fecha_hasta: new Date().toISOString().slice(0, 10),
  };

  constructor(private finanzasService: FinanzasService) {}

  ngOnInit(): void {
    this.cargarCuentas();
  }

  cargarCuentas(sync = false): void {
    this.finanzasService.getCuentas({ q: this.busqueda, sync }).subscribe({
      next: (rows) => this.cuentas.set(rows),
      error: (err) => this.error.set(err?.error?.detail || 'Error al cargar cuentas.'),
    });
  }

  seleccionarCuenta(cta: any): void {
    this.error.set('');
    this.mensaje.set('');
    this.finanzasService.getCuentaDetalle(cta.paciente_id).subscribe({
      next: (res) => {
        this.cuentaSeleccionada.set(res.cuenta);
        this.pagosPaciente.set(res.pagos_recientes || []);
        this.pagoForm.monto = Number(res.cuenta.saldo_pendiente) > 0 ? Number(res.cuenta.saldo_pendiente) : 150;
      },
      error: (err) => this.error.set(err?.error?.detail || 'No se pudo cargar el detalle.'),
    });
  }

  confirmarCobro(): void {
    const cta = this.cuentaSeleccionada();
    if (!cta) return;
    this.guardando.set(true);
    this.error.set('');
    this.mensaje.set('');
    this.finanzasService.registrarPago({
      paciente_id: cta.paciente_id,
      monto: Number(this.pagoForm.monto),
      metodo_pago: this.pagoForm.metodo_pago,
      referencia_externa: this.pagoForm.referencia_externa,
      observaciones: this.pagoForm.observaciones,
    }).subscribe({
      next: (pago) => {
        this.guardando.set(false);
        this.mensaje.set(`Cobro registrado con éxito — Recibo ${pago.numero_recibo} (Bs. ${pago.monto}).`);
        this.pagoForm.referencia_externa = '';
        this.pagoForm.observaciones = '';
        this.cargarCuentas();
        this.seleccionarCuenta(cta);
      },
      error: (err) => {
        this.guardando.set(false);
        this.error.set(err?.error?.detail || 'Error al registrar el cobro.');
      },
    });
  }

  descargarRecibo(pago: any): void {
    this.finanzasService.descargarReciboPdf(pago.id).subscribe({
      next: (blob) => this.finanzasService.triggerBlobDownload(blob, `recibo_${pago.numero_recibo}.pdf`),
    });
  }

  abrirExtracto(): void {
    this.tabActiva.set('extracto');
    if (!this.extracto()) this.cargarExtracto(1);
  }

  aplicarRangoAnios(anios: number): void {
    const hoy = new Date();
    const desde = new Date(hoy.getFullYear() - anios, hoy.getMonth(), hoy.getDate());
    this.extractoFiltros.fecha_desde = desde.toISOString().slice(0, 10);
    this.extractoFiltros.fecha_hasta = hoy.toISOString().slice(0, 10);
    this.cargarExtracto(1);
  }

  cargarExtracto(page = 1): void {
    this.error.set('');
    this.finanzasService.getExtractoBancario({
      ...this.extractoFiltros,
      page,
      page_size: 25,
    }).subscribe({
      next: (res) => this.extracto.set(res),
      error: (err) => this.error.set(err?.error?.detail || 'Error al consultar extracto.'),
    });
  }

  exportarExtracto(formato: 'pdf' | 'excel' | 'csv'): void {
    const ext = formato === 'excel' ? 'xlsx' : formato;
    this.finanzasService.descargarExtracto(formato, this.extractoFiltros).subscribe({
      next: (blob) => this.finanzasService.triggerBlobDownload(
        blob,
        `extracto_pagos_${this.extractoFiltros.fecha_desde}_${this.extractoFiltros.fecha_hasta}.${ext}`
      ),
      error: () => this.error.set('No se pudo exportar el extracto.'),
    });
  }
}
