import { Component, Input, OnChanges, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { IaLongitudinalService } from '../../core/services/ia-longitudinal.service';
import { FinanzasService } from '../../core/services/finanzas.service';

@Component({
  selector: 'app-resumen-ia-drawer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="ia-panel">
      <div class="ia-head">
        <div>
          <h3><i class="fa-solid fa-wand-magic-sparkles"></i> Resumen Clínico Longitudinal IA (CU23 / HU-49)</h3>
          <p class="sub">Síntesis asistida de notas SOAP, evoluciones, Mood Tracker y adherencia a tareas (con anonimización PII y HITL).</p>
        </div>
        <button type="button" class="btn-teal" [disabled]="generando()" (click)="generar()">
          <i class="fa-solid fa-sparkles"></i> {{ generando() ? 'Generando...' : 'Generar Borrador IA' }}
        </button>
      </div>

      <div *ngIf="mensaje()" class="msg ok">{{ mensaje() }}</div>
      <div *ngIf="error()" class="msg err">{{ error() }}</div>

      <div *ngIf="resumenActivo() as r; else sinResumen" class="resumen-card">
        <div class="compliance-banner" [class.approved]="r.estado === 'APROBADO_HITL'">
          <i class="fa-solid" [ngClass]="r.estado === 'APROBADO_HITL' ? 'fa-circle-check' : 'fa-triangle-exclamation'"></i>
          <strong>{{ r.estado === 'APROBADO_HITL' ? 'Aprobado por Profesional (HITL)' : r.etiqueta_cumplimiento }}</strong>
          <span class="meta-chip">Modelo: {{ r.fuente_modelo }}</span>
          <span class="meta-chip">SHA-256: {{ r.hash_sha256?.slice(0, 14) }}...</span>
        </div>

        <div class="sections-grid" *ngIf="r.contenido_estructurado as sec">
          <div class="sec-box">
            <h4>Motivo Inicial</h4>
            <p>{{ sec.motivo_inicial }}</p>
          </div>
          <div class="sec-box">
            <h4>Tendencia Mood Tracker</h4>
            <p>{{ sec.tendencia_mood_tracker }}</p>
          </div>
          <div class="sec-box">
            <h4>Adherencia a Tareas</h4>
            <p>{{ sec.adherencia_tareas }}</p>
          </div>
        </div>

        <label class="lbl-edit">Texto del Resumen Longitudinal (Editable antes de Aprobar HITL)</label>
        <textarea rows="9" [(ngModel)]="textoEditable" class="txt-edit"></textarea>

        <div class="actions">
          <button type="button" class="btn-teal" (click)="aprobarHitl(r)">
            <i class="fa-solid fa-check-double"></i> Editar y Aprobar (HITL)
          </button>
          <button type="button" class="btn-pdf" (click)="exportarPdf(r)">
            <i class="fa-solid fa-file-pdf"></i> Exportar PDF
          </button>
        </div>
      </div>

      <ng-template #sinResumen>
        <p class="empty">Aún no se ha generado un resumen clínico longitudinal IA para este paciente.</p>
      </ng-template>
    </div>
  `,
  styles: [`
    .ia-panel { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
    .ia-head { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
    .ia-head h3 { margin: 0; font-size: 1.08rem; color: #0f2922; }
    .sub { margin: .25rem 0 0; font-size: .84rem; color: #64748b; }
    .compliance-banner { display: flex; align-items: center; flex-wrap: wrap; gap: .6rem; padding: .75rem 1rem; border-radius: 8px; background: #fef3c7; border: 1px solid #f59e0b; color: #92400e; margin-bottom: 1rem; }
    .compliance-banner.approved { background: #d1fae5; border-color: #10b981; color: #065f46; }
    .meta-chip { font-size: .74rem; background: rgba(255,255,255,.7); padding: .15rem .45rem; border-radius: 4px; }
    .sections-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: .75rem; margin-bottom: 1rem; }
    @media (max-width: 900px) { .sections-grid { grid-template-columns: 1fr; } }
    .sec-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: .75rem; }
    .sec-box h4 { margin: 0 0 .35rem; font-size: .84rem; color: #0d9488; }
    .sec-box p { margin: 0; font-size: .82rem; color: #334155; }
    .lbl-edit { display: block; font-size: .82rem; font-weight: 600; color: #334155; margin-bottom: .35rem; }
    .txt-edit { width: 100%; box-sizing: border-box; padding: .75rem; border: 1px solid #cbd5e1; border-radius: 8px; font-family: inherit; font-size: .86rem; }
    .actions { display: flex; gap: .6rem; margin-top: .85rem; }
    .btn-teal { padding: .5rem 1rem; background: #0d9488; color: #fff; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
    .btn-pdf { padding: .5rem 1rem; background: #b91c1c; color: #fff; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
    .msg { padding: .65rem .9rem; border-radius: 8px; font-size: .85rem; }
    .msg.ok { background: #ecfdf5; color: #065f46; }
    .msg.err { background: #fef2f2; color: #991b1b; }
    .empty { color: #64748b; text-align: center; padding: 1.5rem; }
  `]
})
export class ResumenIaDrawerComponent implements OnChanges {
  @Input() pacienteId = '';

  resumenActivo = signal<any | null>(null);
  generando = signal(false);
  mensaje = signal('');
  error = signal('');
  textoEditable = '';

  constructor(
    private iaService: IaLongitudinalService,
    private finanzasService: FinanzasService,
  ) {}

  ngOnChanges(): void {
    if (this.pacienteId) this.cargar();
  }

  cargar(): void {
    this.error.set('');
    this.iaService.listarResumenesIA(this.pacienteId).subscribe({
      next: (rows) => {
        if (rows && rows.length > 0) {
          this.resumenActivo.set(rows[0]);
          this.textoEditable = rows[0].texto_resumen || '';
        }
      },
      error: (err) => this.error.set(err?.error?.detail || 'No autorizado para consultar resúmenes IA.'),
    });
  }

  generar(): void {
    if (!this.pacienteId) return;
    this.generando.set(true);
    this.error.set('');
    this.mensaje.set('');
    this.iaService.generarResumenIA(this.pacienteId).subscribe({
      next: (r) => {
        this.generando.set(false);
        this.resumenActivo.set(r);
        this.textoEditable = r.texto_resumen || '';
        this.mensaje.set('Borrador clínico IA generado con hash SHA-256. Revise y apruebe (HITL).');
      },
      error: (err) => {
        this.generando.set(false);
        this.error.set(err?.error?.detail || 'Error al generar resumen longitudinal IA.');
      },
    });
  }

  aprobarHitl(r: any): void {
    this.iaService.aprobarResumenHITL(r.id, this.textoEditable).subscribe({
      next: (updated) => {
        this.resumenActivo.set(updated);
        this.mensaje.set('Resumen clínico aprobado (HITL) y registrado en bitácora de auditoría.');
      },
      error: (err) => this.error.set(err?.error?.detail || 'No se pudo aprobar el resumen.'),
    });
  }

  exportarPdf(r: any): void {
    this.iaService.descargarResumenPdf(r.id).subscribe({
      next: (blob) => this.finanzasService.triggerBlobDownload(blob, `resumen_ia_${r.expediente}.pdf`),
    });
  }
}
