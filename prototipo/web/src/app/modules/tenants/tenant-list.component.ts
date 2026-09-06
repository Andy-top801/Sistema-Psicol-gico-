import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TenantService } from '../../core/services/tenant.service';
import { AuthService } from '../../core/services/auth.service';
import { Tenant } from '../../core/models';

@Component({
  selector: 'app-tenant-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="tenants-wrapper">
      <!-- Header -->
      <div class="page-header d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="page-title">Gestión de Centros Psicológicos (Tenants)</h1>
          <p class="page-subtitle">Aprovisionamiento y administración de suscripciones multi-tenant</p>
        </div>
        <button class="btn btn-primary" (click)="openCreateModal()">
          <i class="fa-solid fa-plus"></i> Dar de Alta Nuevo Centro
        </button>
      </div>

      <!-- Error Message -->
      <div *ngIf="errorMessage()" class="alert-box alert-danger mb-4">
        <i class="fa-solid fa-triangle-exclamation"></i>
        <span>{{ errorMessage() }}</span>
        <button class="alert-close" (click)="errorMessage.set(null)">&times;</button>
      </div>

      <!-- Success Message -->
      <div *ngIf="successMessage()" class="alert-box alert-success mb-4">
        <i class="fa-solid fa-circle-check"></i>
        <span>{{ successMessage() }}</span>
      </div>

      <!-- Tenants Table -->
      <div class="glass-panel p-4">
        <div class="table-container">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Centro / Gabinete</th>
                <th>Identificador Slug</th>
                <th>Esquema PostgreSQL</th>
                <th>Plan</th>
                <th>Contacto</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let t of tenants()">
                <td>
                  <div class="d-flex align-items-center gap-2">
                    <div class="tenant-icon">
                      <i class="fa-solid fa-hospital"></i>
                    </div>
                    <div>
                      <strong>{{ t.nombre }}</strong>
                      <span class="d-block text-muted text-xs">{{ t.direccion || 'Sin dirección' }}</span>
                    </div>
                  </div>
                </td>
                <td><code>{{ t.slug }}</code></td>
                <td><span class="badge badge-info">{{ t.schema_name }}</span></td>
                <td><span class="badge badge-primary">{{ t.plan }}</span></td>
                <td>
                  <div class="text-xs">
                    <div>{{ t.email_contacto || '-' }}</div>
                    <div class="text-muted">{{ t.telefono || '-' }}</div>
                  </div>
                </td>
                <td>
                  <span class="badge" [class.badge-success]="t.activo" [class.badge-danger]="!t.activo">
                    {{ t.activo ? 'Activo' : 'Suspendido' }}
                  </span>
                </td>
                <td>
                  <div class="d-flex gap-2">
                    <button 
                      class="btn btn-primary btn-sm"
                      (click)="enterTenant(t)" 
                      title="Administrar usuarios, roles y configuración de este centro">
                      <i class="fa-solid fa-right-to-bracket"></i> Administrar
                    </button>
                    <button 
                      class="btn btn-sm" 
                      [class.btn-danger]="t.activo" 
                      [class.btn-success]="!t.activo"
                      (click)="toggleSuspend(t)" 
                      [title]="t.activo ? 'Suspender Centro' : 'Reactivar Centro'">
                      <i class="fa-solid" [class.fa-ban]="t.activo" [class.fa-check]="!t.activo"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr *ngIf="tenants().length === 0">
                <td colspan="7" class="text-center text-muted py-4">No hay centros registrados.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Modal de Alta de Tenant -->
      <div *ngIf="showModal()" class="modal-overlay" (click)="closeModal()">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <h2 class="modal-title mb-3">Alta de Centro Psicológico</h2>
          <p class="text-muted text-sm mb-4">Se creará automáticamente el esquema PostgreSQL y el administrador del centro.</p>

          <form (ngSubmit)="onCreateTenant()">
            <div class="form-group">
              <label class="form-label">Nombre del Centro *</label>
              <input type="text" class="form-control" [(ngModel)]="newTenant.nombre" name="nombre" placeholder="Ej. Gabinete Psicológico San Lucas" (ngModelChange)="autoSlug($event)" required>
            </div>

            <div class="form-group">
              <label class="form-label">Identificador Slug (Esquema PostgreSQL) *</label>
              <input type="text" class="form-control font-mono" [(ngModel)]="newTenant.slug" name="slug" placeholder="san_lucas" required>
            </div>

            <div class="form-group">
              <label class="form-label">Plan de Suscripción</label>
              <select class="form-select" [(ngModel)]="newTenant.plan" name="plan">
                <option value="STANDARD">Standard</option>
                <option value="PRO" selected>Pro</option>
                <option value="ENTERPRISE">Enterprise</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Dirección</label>
              <input type="text" class="form-control" [(ngModel)]="newTenant.direccion" name="direccion" placeholder="Calle / Avenida #123">
            </div>

            <div class="form-group">
              <label class="form-label">Teléfono de Contacto</label>
              <input type="text" class="form-control" [(ngModel)]="newTenant.telefono" name="telefono" placeholder="+591 70000000">
            </div>

            <div class="form-group">
              <label class="form-label">Correo Administrador del Centro</label>
              <input type="email" class="form-control" [(ngModel)]="newTenant.admin_email" name="admin_email" placeholder="admin@centro.com">
            </div>

            <div class="form-group">
              <label class="form-label">Contraseña Administrador *</label>
              <input type="password" class="form-control" [(ngModel)]="newTenant.admin_password" name="admin_password" placeholder="Admin1234*" required>
              <div class="password-hints" *ngIf="newTenant.admin_password">
                <span [class.hint-ok]="newTenant.admin_password.length >= 8" [class.hint-fail]="newTenant.admin_password.length < 8">
                  <i class="fa-solid" [class.fa-check]="newTenant.admin_password.length >= 8" [class.fa-xmark]="newTenant.admin_password.length < 8"></i> Mínimo 8 caracteres
                </span>
                <span [class.hint-ok]="hasUppercase(newTenant.admin_password)" [class.hint-fail]="!hasUppercase(newTenant.admin_password)">
                  <i class="fa-solid" [class.fa-check]="hasUppercase(newTenant.admin_password)" [class.fa-xmark]="!hasUppercase(newTenant.admin_password)"></i> Al menos una mayúscula
                </span>
                <span [class.hint-ok]="hasNumber(newTenant.admin_password)" [class.hint-fail]="!hasNumber(newTenant.admin_password)">
                  <i class="fa-solid" [class.fa-check]="hasNumber(newTenant.admin_password)" [class.fa-xmark]="!hasNumber(newTenant.admin_password)"></i> Al menos un número
                </span>
                <span [class.hint-ok]="hasSpecial(newTenant.admin_password)" [class.hint-fail]="!hasSpecial(newTenant.admin_password)">
                  <i class="fa-solid" [class.fa-check]="hasSpecial(newTenant.admin_password)" [class.fa-xmark]="!hasSpecial(newTenant.admin_password)"></i> Al menos un carácter especial
                </span>
              </div>
            </div>

            <div class="d-flex justify-content-end gap-2 mt-4">
              <button type="button" class="btn btn-secondary" (click)="closeModal()">Cancelar</button>
              <button type="submit" class="btn btn-primary" [disabled]="submitting()">
                <i *ngIf="submitting()" class="fa-solid fa-circle-notch fa-spin"></i>
                <span *ngIf="!submitting()">Crear Esquema y Centro</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .page-title { font-size: 1.5rem; font-weight: 800; }
    .page-subtitle { font-size: 0.88rem; color: var(--text-muted); }
    .tenant-icon { width: 34px; height: 34px; border-radius: 8px; background: rgba(14, 165, 233, 0.15); display: flex; align-items: center; justify-content: center; color: var(--primary); }
    .modal-title { font-size: 1.3rem; font-weight: 800; }
    .p-4 { padding: 20px; }
    .mb-3 { margin-bottom: 12px; }
    .mb-4 { margin-bottom: 20px; }
    .mt-4 { margin-top: 20px; }
    .py-4 { padding-top: 20px; padding-bottom: 20px; }
    .text-xs { font-size: 0.75rem; }
    .text-sm { font-size: 0.85rem; }
    .gap-2 { gap: 8px; }
    .d-flex { display: flex; }
    .d-block { display: block; }
    .justify-content-between { justify-content: space-between; }
    .justify-content-end { justify-content: flex-end; }
    .align-items-center { align-items: center; }
    .text-center { text-align: center; }
    .text-muted { color: var(--text-muted); }
    .font-mono { font-family: var(--font-mono); }
    .alert-box { padding: 12px 16px; border-radius: 10px; font-size: 0.88rem; display: flex; align-items: center; gap: 10px; }
    .alert-danger { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; }
    .alert-success { background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #6ee7b7; }
    .alert-close { background: none; border: none; color: inherit; font-size: 1.2rem; cursor: pointer; margin-left: auto; }
    .password-hints { display: flex; flex-direction: column; gap: 3px; margin-top: 8px; font-size: 0.78rem; }
    .hint-ok { color: #6ee7b7; }
    .hint-fail { color: #fca5a5; }
    .password-hints i { font-size: 0.7rem; margin-right: 4px; }
  `]
})
export class TenantListComponent implements OnInit {
  tenants = signal<Tenant[]>([]);
  showModal = signal<boolean>(false);
  submitting = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  newTenant = {
    nombre: '',
    slug: '',
    plan: 'PRO',
    direccion: '',
    telefono: '',
    admin_email: '',
    admin_password: 'Admin1234*'
  };

  constructor(
    private tenantService: TenantService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadTenants();
  }

  loadTenants() {
    this.tenantService.getAll().subscribe({
      next: (data: Tenant[]) => this.tenants.set(data),
      error: () => {
        this.errorMessage.set('Error al cargar la lista de centros.');
      }
    });
  }

  openCreateModal() {
    this.newTenant = {
      nombre: '',
      slug: '',
      plan: 'PRO',
      direccion: '',
      telefono: '',
      admin_email: '',
      admin_password: 'Admin1234*'
    };
    this.showModal.set(true);
  }

  closeModal() {
    this.showModal.set(false);
  }

  autoSlug(name: string) {
    if (name) {
      this.newTenant.slug = name.toLowerCase()
        .replace(/[^\w ]+/g, '')
        .replace(/ +/g, '_');
    }
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU1: Gestionar Centros Psicológicos y Configuración Multi-Tenant
   *      (HU-03, HU-04, HU-07, HU-08)
   * Diagrama de Comunicación – Alta de Centro Psicológico
   * Participantes:
   *   Actor  → SuperAdministrador
   *   IU     → IU_FormularioCentro (Angular)
   *   CTR    → CTR_TenantService (Django)
   *   CE     → CE_Tenant_y_Dominio (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  onCreateTenant() {
    // --- Paso 1: Ingresar datos de Centro ---
    // El Actor (SuperAdministrador) completa el formulario con los datos del centro

    // Validación de contraseña del admin
    const pwd = this.newTenant.admin_password;
    if (pwd && !this.isPasswordValid(pwd)) {
      this.errorMessage.set('La contraseña del administrador debe tener al menos 8 caracteres, una mayúscula, un número y un carácter especial.');
      setTimeout(() => this.errorMessage.set(null), 6000);
      return;
    }

    this.submitting.set(true);

    // --- Paso 2: POST /api/tenants/ ---
    // IU_FormularioCentro envía los datos del centro al CTR_TenantService
    this.tenantService.create(this.newTenant).subscribe({
      // --- Paso 9: 201 Created ---
      // CTR_TenantService confirma la creación del centro y esquema
      next: () => {
        this.submitting.set(false);
        this.closeModal();
        this.loadTenants();
        // --- Paso 10: Mostrar confirmación ---
        // IU_FormularioCentro muestra el mensaje de éxito al Actor
        this.successMessage.set('Centro psicológico creado exitosamente.');
        setTimeout(() => this.successMessage.set(null), 4000);
      },
      error: (err: any) => {
        this.submitting.set(false);
        const msg = this.extractError(err);
        this.errorMessage.set(msg);
        setTimeout(() => this.errorMessage.set(null), 6000);
      }
    });
    // NOTA: Los pasos 3-8 ocurren en el backend (CTR_TenantService ↔ CE_Tenant_y_Dominio):
    //   Paso 3: Valida disponibilidad Dominio
    //   Paso 4: Dominio disponible
    //   Paso 5: insert(Tenant, Dominio)
    //   Paso 6: Registros creados
    //   Paso 7: CREATE SCHEMA y Migraciones
    //   Paso 8: Esquema creado
  }

  enterTenant(tenant: Tenant) {
    this.authService.setTenant(tenant);
    this.router.navigate(['/users']);
  }

  toggleSuspend(tenant: Tenant) {
    const action$ = tenant.activo ? this.tenantService.suspender(tenant.id) : this.tenantService.activar(tenant.id);
    action$.subscribe({
      next: () => {
        this.loadTenants();
        this.successMessage.set(tenant.activo ? 'Centro suspendido.' : 'Centro reactivado.');
        setTimeout(() => this.successMessage.set(null), 4000);
      },
      error: (err: any) => {
        this.errorMessage.set('Error al cambiar el estado del centro.');
        setTimeout(() => this.errorMessage.set(null), 4000);
      }
    });
  }

  private extractError(err: any): string {
    if (err.error) {
      if (typeof err.error === 'string') return err.error;
      const messages: string[] = [];
      for (const key of Object.keys(err.error)) {
        const val = err.error[key];
        if (Array.isArray(val)) messages.push(`${key}: ${val.join(', ')}`);
        else if (typeof val === 'string') messages.push(`${key}: ${val}`);
      }
      if (messages.length > 0) return messages.join(' | ');
    }
    return 'Ocurrió un error inesperado.';
  }

  // Password validation helpers
  hasUppercase(pwd: string): boolean { return /[A-Z]/.test(pwd); }
  hasNumber(pwd: string): boolean { return /[0-9]/.test(pwd); }
  hasSpecial(pwd: string): boolean { return /[^A-Za-z0-9]/.test(pwd); }
  isPasswordValid(pwd: string): boolean {
    return pwd.length >= 8 && this.hasUppercase(pwd) && this.hasNumber(pwd) && this.hasSpecial(pwd);
  }
}
