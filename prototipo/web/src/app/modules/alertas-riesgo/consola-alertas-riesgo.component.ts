import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { IaLongitudinalService } from '../../core/services/ia-longitudinal.service';

@Component({
  selector: 'app-consola-alertas-riesgo',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="alert-page">
      <div class="alert-header">
        <div>
          <h1><i class="fa-solid fa-triangle-exclamation"></i> Consola de Alertas Prioritarias de Riesgo IA (CU24)</h1>
          <p class="subtitle">HU-50 & HU-51: Detección longitudinal de riesgo vital/deserción con trazabilidad e intervención clínica obligatoria.</p>
        </div>
        <button type="button" class="btn-teal" [disabled]="evaluando()" (click)="ejecutarBarrido()">
          <i class="fa-solid fa-radar"></i> {{ evaluando() ? 'Analizando...' : 'Ejecutar Barrido IA (CU24)' }}
        </button>
      </div>

      <div *ngIf="mensaje()" class="banner ok">{{ mensaje() }}</div>
      <div *ngIf="error()" class="banner err">{{ error() }}</div>

      <div class="kpi-4" *ngIf="resumen() as r">
        <div class="kpi crit"><span>Críticas Activas</span><strong>{{ r.criticas_abiertas }}</strong></div>
        <div class="kpi"><span>Abiertas</span><strong>{{ r.abiertas }}</strong></div>
        <div class="kpi"><span>En Atención</span><strong>{{ r.en_atencion }}</strong></div>
        <div class="kpi ok-k"><span>Resueltas</span><strong>{{ r.resueltas }}</strong></div>
      </div>

      <div class="tabs">
        <button type="button" [class.active]="filtroEstado === ''" (click)="filtrar('', '')">Todas</button>
        <button type="button" [class.active]="filtroSeveridad === 'CRITICO'" (click)="filtrar('', 'CRITICO')">Críticas</button>
        <button type="button" [class.active]="filtroEstado === 'ABIERTA'" (click)="filtrar('ABIERTA', '')">Abiertas</button>
        <button type="button" [class.active]="filtroEstado === 'EN_ATENCION'" (click)="filtrar('EN_ATENCION', '')">En Atención</button>
        <button type="button" [class.active]="filtroEstado === 'RESUELTA'" (click)="filtrar('RESUELTA', '')">Resueltas</button>
      </div>

      <div class="card">
        <div class="table-wrap">
          <table class="tbl">
            <thead>
              <tr>
                <th>Severidad / Score</th>
                <th>Paciente</th>
                <th>Tipo de Riesgo</th>
                <th>Factores Detectados (Explicabilidad)</th>
                <th>Estado</th>
                <th>Acción Clínica</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let a of alertas()">
                <td>
                  <span class="sev-pill" [ngClass]="a.severidad.toLowerCase()">{{ a.severidad }}</span>
                  <div class="score"><strong>{{ a.score_riesgo }}/100</strong></div>
                </td>
                <td>
                  <strong>{{ a.expediente }}</strong><br />
                  <span>{{ a.paciente_nombre }}</span>
                </td>
                <td><strong>{{ a.tipo }}</strong></td>
                <td>
                  <div class="chips">
                    <span class="chip" *ngFor="let f of a.factores_detectados">{{ f.etiqueta }}</span>
                  </div>
                  <small class="muted">{{ a.explicacion }}</small>
                </td>
                <td>
                  <span class="est-pill">{{ a.estado }}</span>
                  <div *ngIf="a.nota_intervencion" class="nota-prev"><i class="fa-solid fa-clipboard-check"></i> {{ a.nota_intervencion }}</div>
                </td>
                <td>
                  <button type="button" class="btn-xs" (click)="abrirModal(a)">Intervenir / Gestionar</button>
                </td>
              </tr>
              <tr *ngIf="alertas().length === 0">
                <td colspan="6" class="empty">No hay alertas para este filtro. Ejecuta el barrido IA para analizar pacientes.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Modal de Intervención Clínica Obligatoria -->
      <div *ngIf="alertaActiva() as sel" class="modal-backdrop">
        <div class="modal-box">
          <h3>Intervención Clínica — {{ sel.expediente }} ({{ sel.paciente_nombre }})</h3>
          <p class="muted">{{ sel.explicacion }}</p>

          <label>Nuevo Estado</label>
          <select [(ngModel)]="formTransicion.estado" class="inp-full">
            <option value="EN_ATENCION">En Atención</option>
            <option value="RESUELTA">Resuelta (Requiere nota obligatoria)</option>
            <option value="DESCARTADA">Descartada (Requiere justificación)</option>
          </select>

          <label>Bitácora de Intervención Clínica (Obligatoria para Resolver/Descartar)</label>
          <textarea rows="4" [(ngModel)]="formTransicion.nota_intervencion"
                    placeholder="Ej: Llamada de contención telefónica, derivación psiquiátrica o reagendamiento de emergencia..."
                    class="inp-full"></textarea>

          <div class="modal-actions">
            <button type="button" class="btn-outline" (click)="alertaActiva.set(null)">Cancelar</button>
            <button type="button" class="btn-teal" (click)="guardarIntervencion()">Guardar y Auditar en CE_AuditLog</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .alert-page { padding: 1.5rem; max-width: 1400px; margin: 0 auto; display: flex; flex-direction: column; gap: 1.15rem; }
    .alert-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
    .alert-header h1 { margin: 0; font-size: 1.45rem; color: #0f2922; }
    .subtitle { margin: .25rem 0 0; color: #64748b; font-size: .86rem; }
    .kpi-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: .85rem; }
    .kpi { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: .9rem 1.1rem; }
    .kpi span { display: block; font-size: .78rem; color: #64748b; font-weight: 600; }
    .kpi strong { font-size: 1.4rem; color: #0f172a; }
    .kpi.crit { border-left: 4px solid #dc2626; }
    .kpi.ok-k { border-left: 4px solid #059669; }
    .tabs { display: flex; gap: .45rem; flex-wrap: wrap; }
    .tabs button { padding: .45rem .85rem; border: 1px solid #cbd5e1; background: #fff; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: .82rem; }
    .tabs button.active { background: #0f2922; color: #fff; border-color: #0f2922; }
    .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.1rem; }
    .table-wrap { overflow-x: auto; }
    .tbl { width: 100%; border-collapse: collapse; font-size: .84rem; }
    .tbl th, .tbl td { padding: .6rem .5rem; border-bottom: 1px solid #e2e8f0; text-align: left; vertical-align: top; }
    .sev-pill { padding: .2rem .55rem; border-radius: 999px; font-size: .73rem; font-weight: 700; display: inline-block; }
    .sev-pill.critico { background: #fee2e2; color: #991b1b; }
    .sev-pill.alto { background: #ffedd5; color: #9a3412; }
    .sev-pill.medio { background: #fef3c7; color: #92400e; }
    .sev-pill.bajo { background: #e0f2fe; color: #075985; }
    .score { margin-top: .25rem; font-size: .82rem; color: #334155; }
    .chips { display: flex; gap: .3rem; flex-wrap: wrap; margin-bottom: .3rem; }
    .chip { background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 999px; padding: .15rem .5rem; font-size: .73rem; }
    .est-pill { background: #f0fdfa; color: #0f766e; padding: .2rem .5rem; border-radius: 6px; font-size: .75rem; font-weight: 700; }
    .nota-prev { margin-top: .35rem; font-size: .76rem; color: #334155; max-width: 220px; }
    .muted { color: #64748b; font-size: .78rem; }
    .btn-teal { padding: .5rem .95rem; background: #0d9488; color: #fff; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
    .btn-outline { padding: .45rem .85rem; background: #fff; border: 1px solid #cbd5e1; border-radius: 8px; cursor: pointer; }
    .btn-xs { padding: .35rem .65rem; background: #0f2922; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: .76rem; }
    .empty { text-align: center; color: #64748b; padding: 1.5rem; }
    .banner { padding: .75rem 1rem; border-radius: 8px; font-size: .88rem; }
    .banner.ok { background: #ecfdf5; color: #065f46; }
    .banner.err { background: #fef2f2; color: #991b1b; }
    .modal-backdrop { position: fixed; inset: 0; background: rgba(15,23,42,.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
    .modal-box { background: #fff; border-radius: 12px; padding: 1.4rem; width: 520px; max-width: 92vw; display: flex; flex-direction: column; gap: .75rem; }
    .inp-full { width: 100%; box-sizing: border-box; padding: .5rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: .88rem; }
    .modal-actions { display: flex; justify-content: flex-end; gap: .5rem; margin-top: .5rem; }
  `]
})
export class ConsolaAlertasRiesgoComponent implements OnInit {
  alertas = signal<any[]>([]);
  resumen = signal<any | null>(null);
  alertaActiva = signal<any | null>(null);
  evaluando = signal(false);
  mensaje = signal('');
  error = signal('');
  filtroEstado = '';
  filtroSeveridad = '';

  formTransicion = {
    estado: 'EN_ATENCION',
    nota_intervencion: '',
  };

  constructor(private iaService: IaLongitudinalService) {}

  ngOnInit(): void {
    this.cargar();
  }

  filtrar(estado: string, severidad: string): void {
    this.filtroEstado = estado;
    this.filtroSeveridad = severidad;
    this.cargar();
  }

  cargar(): void {
    this.error.set('');
    this.iaService.listarAlertasRiesgo(this.filtroEstado || undefined, this.filtroSeveridad || undefined).subscribe({
      next: (res) => {
        this.resumen.set(res.resumen);
        this.alertas.set(res.alertas || []);
      },
      error: (err) => this.error.set(err?.error?.detail || 'Error al cargar alertas de riesgo IA.'),
    });
  }

  ejecutarBarrido(): void {
    this.evaluando.set(true);
    this.error.set('');
    this.mensaje.set('');
    this.iaService.evaluarAlertasRiesgo().subscribe({
      next: (res) => {
        this.evaluando.set(false);
        this.mensaje.set(`Barrido completado: ${res.pacientes_evaluados} pacientes evaluados, ${res.alertas_activas_actualizadas} alertas actualizadas.`);
        this.cargar();
      },
      error: (err) => {
        this.evaluando.set(false);
        this.error.set(err?.error?.detail || 'No se pudo ejecutar el barrido longitudinal.');
      },
    });
  }

  abrirModal(alerta: any): void {
    this.alertaActiva.set(alerta);
    this.formTransicion = {
      estado: alerta.estado === 'ABIERTA' ? 'EN_ATENCION' : 'RESUELTA',
      nota_intervencion: alerta.nota_intervencion || '',
    };
  }

  guardarIntervencion(): void {
    const sel = this.alertaActiva();
    if (!sel) return;
    this.error.set('');
    this.iaService.transicionarAlerta(sel.id, this.formTransicion.estado, this.formTransicion.nota_intervencion).subscribe({
      next: () => {
        this.alertaActiva.set(null);
        this.mensaje.set('Intervención registrada y auditada en CE_AuditLog.');
        this.cargar();
      },
      error: (err) => this.error.set(err?.error?.detail || 'Error al guardar intervención.'),
    });
  }
}
