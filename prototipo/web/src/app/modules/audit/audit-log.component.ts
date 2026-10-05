// ==============================================================================
// MÓDULO: audit-log.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_VisorBitacora / IU_ModalLlaveDesarrollador / IU_VisorBitacoraForense
// CASOS DE USO: CU5: Bitácora Confidencial y Llave Única del Desarrollador (HU-37)
//
// DIAGRAMA DE SECUENCIA UML (CU5 - Bitácora Confidencial y Llave de Desarrollador):
// ------------------------------------------------------------------------------
// 1. SuperAdmin / Developer -> IU_ModalLlaveDesarrollador: 1: ingresar_llave_maestra(developer_key, fecha_consulta, tenant_filtro)
// 2. IU_ModalLlaveDesarrollador -> CTR_AuditLogController: 2: GET /api/v1/audit/log/?date=... (Header: X-Developer-Key)
// 3. CTR_AuditLogController -> CTR_FernetDecryptor: 3: validar_firma_hmac_sha256(developer_key)
// 4. CTR_FernetDecryptor --> CTR_AuditLogController: 4: resultado_validacion_clave(es_valida)
// [Alt: Llave Inválida]
// 5a. CTR_AuditLogController --> IU_ModalLlaveDesarrollador: 5a: HTTP 403 Forbidden ("Llave de Desarrollador Inválida")
// 6a. IU_ModalLlaveDesarrollador --> Developer: 6a: mostrar_alerta_seguridad_bloqueo("Intento auditado y bloqueado")
// [Alt: Llave Válida]
// 5b. CTR_AuditLogController -> CE_EncryptedLogFile: 5b: abrir_archivo_cifrado(audit-YYYY-MM-DD.log.enc, modo=0600)
// 6b. CE_EncryptedLogFile --> CTR_AuditLogController: 6b: stream_lineas_cifradas_bytes()
// 7b. CTR_AuditLogController -> CTR_FernetDecryptor: 7b: decrypt_payload_fernet(linea_cifrada, derived_aes_key)
// 8b. CTR_FernetDecryptor --> CTR_AuditLogController: 8b: json_payload_en_claro(ip, user_id, action, timestamp)
// 9b. CTR_AuditLogController -> CE_Usuario: 9b: resolver_email_y_rol(user_id)
// 10b. CE_Usuario --> CTR_AuditLogController: 10b: datos_usuario(email, rol_tenant)
// 11b. CTR_AuditLogController --> IU_VisorBitacoraForense: 11b: HTTP 200 OK [eventos_descifrados_auditados]
// 12b. IU_VisorBitacoraForense --> Developer: 12b: renderizar_tabla_forense(ip, usuario, accion, hora_gmt4_bolivia)
// ==============================================================================
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
    @media (max-width: 520px) {
      .filters-bar { grid-template-columns: 1fr; }
      .key-filter { grid-column: 1; }
      .date-filter { grid-column: 1; grid-row: auto; }
      .tenant-filter { grid-column: 1; grid-row: auto; }
      .filter-actions {
        grid-column: 1;
        grid-row: auto;
        grid-template-columns: 1fr;
        grid-template-rows: auto;
        gap: 8px;
      }
      .filter-actions .btn {
        width: 100%;
        justify-content: center;
      }
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

  // CU5 Paso 1: ingresar_llave_maestra(developer_key, fecha_consulta, tenant_filtro)
  // CU5 Paso 2: GET /api/v1/audit/log/?date=... (Header: X-Developer-Key)
  loadLogs(): void {
    if (!this.developerKey.trim()) {
      this.events.set([]);
      this.errorMessage.set('Ingresá la clave de desarrollador para consultar la bitácora.');
      return;
    }
    this.request?.unsubscribe();
    this.loading.set(true);
    this.errorMessage.set(null);
    // CU5 Paso 2: Invocar servicio con Header X-Developer-Key
    this.request = this.auditService.getLogs(this.date, this.tenant, this.developerKey).subscribe({
      next: events => {
        if (!this.developerKey || !this.authService.isAuthenticated()) return;
        // CU5 Paso 11b: Recibir HTTP 200 OK [eventos_descifrados_auditados]
        // CU5 Paso 12b: renderizar_tabla_forense(ip, usuario, accion, hora_gmt4_bolivia)
        this.events.set(events);
        this.loading.set(false);
      },
      error: (error: HttpErrorResponse) => {
        this.events.set([]);
        this.loading.set(false);
        // CU5 Paso 5a: HTTP 403 Forbidden ("Llave de Desarrollador Inválida - Acceso Denegado")
        // CU5 Paso 6a: mostrar_alerta_seguridad_bloqueo("Intento de acceso auditado y bloqueado")
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
