import { Component, OnInit, OnDestroy, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { AuditService } from '../../core/services/audit.service';
import { AuditEvent } from '../../core/models';
import { AuthService } from '../../core/services/auth.service';
import { Subscription } from 'rxjs';

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
      <div class="filter-field key-filter">
        <label class="form-label" for="audit-key">Clave de desarrollador</label>
        <div class="key-input">
          <input id="audit-key" class="form-control" [type]="showDeveloperKey ? 'text' : 'password'" autocomplete="off" [(ngModel)]="developerKey" (ngModelChange)="onKeyEdited()" placeholder="Ingresá la clave de auditoría">
          <button class="key-visibility" type="button" (click)="showDeveloperKey = !showDeveloperKey" [attr.aria-label]="showDeveloperKey ? 'Ocultar clave' : 'Mostrar clave'" [attr.title]="showDeveloperKey ? 'Ocultar clave' : 'Mostrar clave'" [attr.aria-pressed]="showDeveloperKey" aria-controls="audit-key">
            <i class="fa-solid" [class.fa-eye]="!showDeveloperKey" [class.fa-eye-slash]="showDeveloperKey" aria-hidden="true"></i>
          </button>
        </div>
      </div>
      <div class="filter-field date-filter">
        <label class="form-label" for="audit-date">Fecha</label>
        <input id="audit-date" class="form-control" type="date" [(ngModel)]="date">
      </div>
      <div class="filter-field tenant-filter">
        <label class="form-label" for="audit-tenant">Tenant</label>
        <input id="audit-tenant" class="form-control" type="text" [(ngModel)]="tenant" placeholder="schema_name">
      </div>
      <div class="filter-actions">
        <button class="btn btn-primary" type="button" (click)="loadLogs()" [disabled]="loading()">
          <i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i> Buscar
        </button>
        <button class="btn btn-secondary" type="button" (click)="clearFilters()">Limpiar</button>
        <button class="btn btn-secondary" type="button" (click)="lock()">Bloquear</button>
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
    .filters-bar { padding: 12px; margin-bottom: 16px; display: grid; grid-template-columns: minmax(0, 180px) minmax(0, 1fr) auto; align-items: end; gap: 8px 12px; }
    .filter-field { min-width: 0; }
    .key-filter { grid-column: 1 / 3; }
    .key-input { position: relative; }
    .filter-field .key-input .form-control { padding-right: 44px; }
    .key-visibility { position: absolute; inset: 0 0 0 auto; width: 38px; display: inline-flex; align-items: center; justify-content: center; border: 0; border-radius: 6px; background: transparent; color: var(--text-muted); cursor: pointer; }
    .key-visibility:hover { color: var(--primary); }
    .key-visibility:focus-visible { outline: 2px solid var(--primary); outline-offset: -3px; }
    .date-filter { grid-column: 1; grid-row: 2; }
    .tenant-filter { grid-column: 2; grid-row: 2; }
    .filter-field .form-label { display: block; margin: 0 0 4px; }
    .filter-field .form-control { width: 100%; min-width: 0; height: 38px; padding: 8px 10px; box-sizing: border-box; }
    .filter-actions { grid-column: 3; grid-row: 1 / 3; align-self: stretch; display: grid; grid-template-columns: max-content; grid-template-rows: repeat(3, 38px); align-content: space-between; padding-top: 24px; gap: 6px; }
    .filter-actions .btn { width: auto; min-height: 38px; padding: 8px 12px; white-space: nowrap; }
    .filter-actions .btn-primary { grid-column: 1 / -1; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
    .table-container { max-width: 100%; min-width: 0; overflow-x: auto; }
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
      .page-header { flex-direction: column; align-items: flex-start; padding: 18px; }
      .filters-bar { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
      .filter-actions { grid-column: 1 / -1; grid-row: 3; grid-template-columns: repeat(3, max-content); grid-template-rows: 38px; justify-content: end; padding-top: 0; }
      .filter-actions .btn-primary { grid-column: 1; }
    }
  `]
})
export class AuditLogComponent implements OnInit, OnDestroy {
  events = signal<AuditEvent[]>([]);
  loading = signal(false);
  errorMessage = signal<string | null>(null);
  date = '';
  tenant = '';
  developerKey = '';
  showDeveloperKey = false;
  private request?: Subscription;

  constructor(private auditService: AuditService, private authService: AuthService) {
    effect(() => {
      if (!this.authService.isAuthenticated()) this.clearProtectedState();
    }, { allowSignalWrites: true });
  }

  ngOnInit(): void {}

  loadLogs(): void {
    if (!this.developerKey.trim()) {
      this.events.set([]);
      this.errorMessage.set('Ingresá la clave de desarrollador para consultar la bitácora.');
      return;
    }
    this.request?.unsubscribe();
    this.loading.set(true);
    this.errorMessage.set(null);
    this.request = this.auditService.getLogs(this.date, this.tenant, this.developerKey).subscribe({
      next: events => { if (!this.developerKey || !this.authService.isAuthenticated()) return; this.events.set(events); this.loading.set(false); },
      error: (error: HttpErrorResponse) => {
        this.events.set([]);
        this.loading.set(false);
        this.errorMessage.set(error.status === 401 || error.status === 403
          ? 'Acceso denegado. Verificá la clave de desarrollador y tu sesión de SuperAdmin.'
          : error.status === 400
          ? 'Los filtros no son válidos. Verifica la fecha y vuelve a intentarlo.'
          : error.status === 503
            ? 'La bitácora no está disponible en este momento.'
            : 'No se pudo cargar la bitácora. Intenta nuevamente.');
      }
    });
  }

  onKeyEdited(): void { this.clearProtectedState(false); }

  lock(): void { this.clearProtectedState(); }

  private clearProtectedState(clearKey = true): void {
    this.request?.unsubscribe();
    this.request = undefined;
    if (clearKey) {
      this.developerKey = '';
      this.showDeveloperKey = false;
    }
    this.events.set([]);
    this.loading.set(false);
  }

  ngOnDestroy(): void { this.clearProtectedState(); }

  clearFilters(): void {
    this.date = '';
    this.tenant = '';
    if (this.developerKey.trim()) this.loadLogs();
  }
}
