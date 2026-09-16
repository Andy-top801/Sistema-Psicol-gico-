import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { AuditService } from '../../core/services/audit.service';
import { AuditEvent } from '../../core/models';

@Component({
  selector: 'app-audit-log',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="page-header glass-panel">
      <div>
        <span class="eyebrow">SEGURIDAD</span>
        <h1>Bitácora de auditoría</h1>
        <p>Consulta de eventos registrados del sistema.</p>
      </div>
      <span class="badge badge-primary"><i class="fa-solid fa-eye"></i> Solo lectura</span>
    </section>

    <section class="filters-bar glass-panel" aria-label="Filtros de bitácora">
      <div class="filter-field">
        <label class="form-label" for="audit-date">Fecha</label>
        <input id="audit-date" class="form-control" type="date" [(ngModel)]="date">
      </div>
      <div class="filter-field tenant-filter">
        <label class="form-label" for="audit-tenant">Tenant</label>
        <input id="audit-tenant" class="form-control" type="text" [(ngModel)]="tenant" placeholder="schema_name">
      </div>
      <div class="filter-actions">
        <button class="btn btn-primary" type="button" (click)="loadLogs()" [disabled]="loading()">
          <i class="fa-solid fa-filter"></i> Filtrar
        </button>
        <button class="btn btn-secondary" type="button" (click)="clearFilters()">Limpiar</button>
      </div>
    </section>

    <div *ngIf="errorMessage()" class="alert-box alert-danger mb-4" role="alert">
      <i class="fa-solid fa-triangle-exclamation"></i>
      <span>{{ errorMessage() }}</span>
      <button class="alert-close" type="button" (click)="errorMessage.set(null)" aria-label="Cerrar error">&times;</button>
    </div>

    <div *ngIf="loading()" class="loading-state glass-panel">Cargando bitácora...</div>

    <div *ngIf="!loading() && events().length === 0" class="empty-state glass-panel">
      No hay eventos para los filtros seleccionados.
    </div>

    <div *ngIf="!loading() && events().length > 0" class="table-container">
      <table class="custom-table">
        <thead>
          <tr>
            <th>Fecha y hora</th><th>Usuario</th><th>Tenant</th><th>Método</th>
            <th>Ruta</th><th>Acción</th><th>Estado</th><th>IP</th><th>Error</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let event of events()">
            <td>{{ event.timestamp | date:'dd/MM/yyyy HH:mm:ss' }}</td>
            <td>{{ event.user }}<small *ngIf="event.user_id" class="user-id">{{ event.user_id }}</small></td>
            <td>{{ event.tenant || 'Global' }}</td>
            <td><span class="method">{{ event.method }}</span></td>
            <td class="path">{{ event.path }}</td>
            <td>{{ event.action }}</td>
            <td><span class="status" [class.status-error]="event.status_code >= 400">{{ event.status_code }}</span></td>
            <td>{{ event.ip || '—' }}</td>
            <td>{{ event.error || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  `,
  styles: [`
    .page-header { padding: 24px 28px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
    .page-header h1 { margin: 4px 0; }
    .page-header p { color: var(--text-muted); }
    .eyebrow { color: var(--primary); font-size: .75rem; font-weight: 700; letter-spacing: .08em; }
    .filters-bar { padding: 18px; margin-bottom: 20px; display: flex; align-items: end; gap: 16px; }
    .filter-field { min-width: 190px; }
    .tenant-filter { flex: 1; max-width: 360px; }
    .filter-actions { display: flex; gap: 8px; }
    .loading-state, .empty-state { padding: 32px; text-align: center; color: var(--text-muted); }
    .custom-table { min-width: 1100px; }
    .custom-table td { vertical-align: top; }
    .path, .method, .user-id { font-family: var(--font-mono); font-size: .82rem; }
    .path { white-space: normal; overflow-wrap: anywhere; max-width: 260px; }
    .user-id { display: block; color: var(--text-dim); margin-top: 2px; }
    .method { font-weight: 700; color: var(--primary); }
    .status { color: var(--success); font-weight: 700; }
    .status-error { color: var(--danger); }
    @media (max-width: 700px) {
      .page-header, .filters-bar { flex-direction: column; align-items: stretch; }
      .tenant-filter { max-width: none; }
      .filter-actions .btn { flex: 1; }
    }
  `]
})
export class AuditLogComponent implements OnInit {
  events = signal<AuditEvent[]>([]);
  loading = signal(true);
  errorMessage = signal<string | null>(null);
  date = '';
  tenant = '';

  constructor(private auditService: AuditService) {}

  ngOnInit(): void { this.loadLogs(); }

  loadLogs(): void {
    this.loading.set(true);
    this.errorMessage.set(null);
    this.auditService.getLogs(this.date, this.tenant).subscribe({
      next: events => { this.events.set(events); this.loading.set(false); },
      error: (error: HttpErrorResponse) => {
        this.events.set([]);
        this.loading.set(false);
        this.errorMessage.set(error.status === 400
          ? 'Los filtros no son válidos. Verifica la fecha y vuelve a intentarlo.'
          : error.status === 503
            ? 'La bitácora no está disponible en este momento.'
            : 'No se pudo cargar la bitácora. Intenta nuevamente.');
      }
    });
  }

  clearFilters(): void {
    this.date = '';
    this.tenant = '';
    this.loadLogs();
  }
}
