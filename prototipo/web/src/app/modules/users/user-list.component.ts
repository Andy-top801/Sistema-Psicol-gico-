import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../core/services/user.service';
import { RoleService } from '../../core/services/role.service';
import { Usuario, Rol } from '../../core/models';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="users-wrapper">
      <div class="page-header d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="page-title">Personal y Usuarios del Centro</h1>
          <p class="page-subtitle">Administra los profesionales, terapeutas y personal administrativo</p>
        </div>
        <button class="btn btn-primary" (click)="openCreateModal()">
          <i class="fa-solid fa-user-plus"></i> Registrar Nuevo Usuario
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

      <!-- Users Table Card -->
      <div class="glass-panel p-4">
        <div class="table-container">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Correo Electrónico</th>
                <th>Rol Asignado</th>
                <th>Teléfono</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let u of users()">
                <td>
                  <div class="d-flex align-items-center gap-2">
                    <div class="user-avatar-sm">
                      {{ u.nombre.charAt(0) }}
                    </div>
                    <div>
                      <strong>{{ u.nombre }} {{ u.apellido }}</strong>
                      <span class="d-block text-muted text-xs">Registrado: {{ u.fecha_creacion | date:'shortDate' }}</span>
                    </div>
                  </div>
                </td>
                <td>{{ u.email }}</td>
                <td>
                  <span class="badge badge-info">{{ u.rol_detalle?.nombre || u.rol?.nombre || 'Sin Rol' }}</span>
                </td>
                <td>{{ u.telefono || '-' }}</td>
                <td>
                  <span class="badge" [class.badge-success]="u.activo" [class.badge-danger]="!u.activo">
                    {{ u.activo ? 'Activo' : 'Inactivo' }}
                  </span>
                </td>
                <td>
                  <div class="d-flex gap-2">
                    <button class="btn btn-secondary btn-sm" (click)="openEditModal(u)" title="Editar Rol y Datos">
                      <i class="fa-solid fa-pen"></i>
                    </button>
                    <button 
                      class="btn btn-sm" 
                      [class.btn-danger]="u.activo" 
                      [class.btn-success]="!u.activo"
                      (click)="toggleUserStatus(u)" 
                      [title]="u.activo ? 'Desactivar Cuenta' : 'Activar Cuenta'">
                      <i class="fa-solid" [class.fa-user-slash]="u.activo" [class.fa-user-check]="!u.activo"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr *ngIf="users().length === 0">
                <td colspan="6" class="text-center text-muted py-4">No hay usuarios registrados en este centro.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Modal Crear/Editar Usuario -->
      <div *ngIf="showModal()" class="modal-overlay" (click)="closeModal()">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <h2 class="modal-title mb-3">{{ isEditing() ? 'Editar Usuario' : 'Registrar Nuevo Usuario' }}</h2>

          <!-- Error en modal -->
          <div *ngIf="modalError()" class="alert-box alert-danger mb-3">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <span>{{ modalError() }}</span>
          </div>

          <form (ngSubmit)="onSaveUser()">
            <div class="form-group">
              <label class="form-label">Nombres *</label>
              <input type="text" class="form-control" [(ngModel)]="currentUserData.nombre" name="nombre" placeholder="Nombre" required>
            </div>

            <div class="form-group">
              <label class="form-label">Apellidos</label>
              <input type="text" class="form-control" [(ngModel)]="currentUserData.apellido" name="apellido" placeholder="Apellidos">
            </div>

            <!-- Email: editable solo al crear, visible (solo lectura) al editar -->
            <div class="form-group" *ngIf="!isEditing()">
              <label class="form-label">Correo Electrónico *</label>
              <input type="email" class="form-control" [(ngModel)]="currentUserData.email" name="email" placeholder="correo@centro.com" required>
            </div>
            <div class="form-group" *ngIf="isEditing()">
              <label class="form-label">Correo Electrónico</label>
              <input type="email" class="form-control input-readonly" [value]="currentUserData.email" readonly disabled>
            </div>

            <!-- Contraseña: obligatoria al crear, opcional al editar -->
            <div class="form-group">
              <label class="form-label">{{ isEditing() ? 'Nueva Contraseña (dejar vacío para no cambiar)' : 'Contraseña *' }}</label>
              <input type="password" class="form-control" [(ngModel)]="currentUserData.password" name="password" 
                     [placeholder]="isEditing() ? 'Dejar vacío para mantener la actual' : 'Mínimo 8 caracteres'" 
                     [required]="!isEditing()">
              <div class="password-hints" *ngIf="currentUserData.password">
                <span [class.hint-ok]="currentUserData.password.length >= 8" [class.hint-fail]="currentUserData.password.length < 8">
                  <i class="fa-solid" [class.fa-check]="currentUserData.password.length >= 8" [class.fa-xmark]="currentUserData.password.length < 8"></i> Mínimo 8 caracteres
                </span>
                <span [class.hint-ok]="hasUppercase(currentUserData.password)" [class.hint-fail]="!hasUppercase(currentUserData.password)">
                  <i class="fa-solid" [class.fa-check]="hasUppercase(currentUserData.password)" [class.fa-xmark]="!hasUppercase(currentUserData.password)"></i> Al menos una mayúscula
                </span>
                <span [class.hint-ok]="hasLowercase(currentUserData.password)" [class.hint-fail]="!hasLowercase(currentUserData.password)">
                  <i class="fa-solid" [class.fa-check]="hasLowercase(currentUserData.password)" [class.fa-xmark]="!hasLowercase(currentUserData.password)"></i> Al menos una minúscula
                </span>
                <span [class.hint-ok]="hasNumber(currentUserData.password)" [class.hint-fail]="!hasNumber(currentUserData.password)">
                  <i class="fa-solid" [class.fa-check]="hasNumber(currentUserData.password)" [class.fa-xmark]="!hasNumber(currentUserData.password)"></i> Al menos un número
                </span>
                <span [class.hint-ok]="hasSpecial(currentUserData.password)" [class.hint-fail]="!hasSpecial(currentUserData.password)">
                  <i class="fa-solid" [class.fa-check]="hasSpecial(currentUserData.password)" [class.fa-xmark]="!hasSpecial(currentUserData.password)"></i> Al menos un carácter especial (!&#64;#$%^&*)
                </span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Rol Clínico / Administrativo *</label>
              <select class="form-select" [(ngModel)]="currentUserData.rol_id" name="rol_id" required>
                <option [ngValue]="null" disabled>Selecciona un rol...</option>
                <option *ngFor="let r of roles()" [ngValue]="r.id">
                  {{ r.nombre }} — {{ r.descripcion }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Teléfono</label>
              <input type="text" class="form-control" [(ngModel)]="currentUserData.telefono" name="telefono" placeholder="+591 70000000">
            </div>

            <div class="d-flex justify-content-end gap-2 mt-4">
              <button type="button" class="btn btn-secondary" (click)="closeModal()">Cancelar</button>
              <button type="submit" class="btn btn-primary" [disabled]="submitting()">
                <i *ngIf="submitting()" class="fa-solid fa-circle-notch fa-spin"></i>
                <span *ngIf="!submitting()">{{ isEditing() ? 'Guardar Cambios' : 'Registrar Usuario' }}</span>
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
    .user-avatar-sm { width: 34px; height: 34px; border-radius: 8px; background: #e6f5ed; color: #19734e; display: flex; align-items: center; justify-content: center; font-weight: 700; }
    .p-4 { padding: 20px; }
    .mb-3 { margin-bottom: 12px; }
    .mb-4 { margin-bottom: 20px; }
    .mt-4 { margin-top: 20px; }
    .py-4 { padding-top: 20px; padding-bottom: 20px; }
    .text-xs { font-size: 0.75rem; }
    .gap-2 { gap: 8px; }
    .d-flex { display: flex; }
    .d-block { display: block; }
    .justify-content-between { justify-content: space-between; }
    .justify-content-end { justify-content: flex-end; }
    .align-items-center { align-items: center; }
    .text-center { text-align: center; }
    .text-muted { color: var(--text-muted); }
    .alert-box { padding: 12px 16px; border-radius: 10px; font-size: 0.88rem; display: flex; align-items: center; gap: 10px; }
    .alert-danger { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
    .alert-success { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
    .alert-close { background: none; border: none; color: inherit; font-size: 1.2rem; cursor: pointer; margin-left: auto; }
    .input-readonly { opacity: 0.6; cursor: not-allowed; }
    .password-hints { display: flex; flex-direction: column; gap: 3px; margin-top: 8px; font-size: 0.78rem; }
    .hint-ok { color: #16a34a; }
    .hint-fail { color: #dc2626; }
    .password-hints i { font-size: 0.7rem; margin-right: 4px; }

    @media (max-width: 640px) {
      .page-header {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 14px;
      }
      .page-header .btn {
        width: 100%;
        justify-content: center;
      }
      .p-4 { padding: 16px; }
      .page-title { font-size: 1.3rem; }
    }
  `]
})
export class UserListComponent implements OnInit {
  users = signal<Usuario[]>([]);
  roles = signal<Rol[]>([]);
  showModal = signal<boolean>(false);
  isEditing = signal<boolean>(false);
  submitting = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);
  modalError = signal<string | null>(null);

  currentUserData: any = {
    id: '',
    nombre: '',
    apellido: '',
    email: '',
    password: '',
    telefono: '',
    rol_id: null
  };

  constructor(
    private userService: UserService,
    private roleService: RoleService
  ) {}

  ngOnInit() {
    this.loadUsers();
    this.loadRoles();
  }

  // --- Password validation helpers ---
  hasUppercase(pwd: string): boolean { return /[A-Z]/.test(pwd); }
  hasLowercase(pwd: string): boolean { return /[a-z]/.test(pwd); }
  hasNumber(pwd: string): boolean { return /[0-9]/.test(pwd); }
  hasSpecial(pwd: string): boolean { return /[^A-Za-z0-9]/.test(pwd); }

  isPasswordValid(pwd: string): boolean {
    return pwd.length >= 8 && this.hasUppercase(pwd) && this.hasLowercase(pwd) && this.hasNumber(pwd) && this.hasSpecial(pwd);
  }

  loadUsers() {
    this.userService.getAll().subscribe({
      next: (data: Usuario[]) => this.users.set(data),
      error: (err: any) => {
        this.errorMessage.set('Error al cargar la lista de usuarios.');
      }
    });
  }

  loadRoles() {
    this.roleService.getRoles().subscribe({
      next: (data: Rol[]) => this.roles.set(data),
      error: () => {
        this.errorMessage.set('Error al cargar los roles disponibles.');
      }
    });
  }

  openCreateModal() {
    this.isEditing.set(false);
    this.modalError.set(null);
    this.currentUserData = {
      nombre: '',
      apellido: '',
      email: '',
      password: '',
      telefono: '',
      rol_id: this.roles().length > 0 ? this.roles()[0].id : null
    };
    this.showModal.set(true);
  }

  openEditModal(user: Usuario) {
    this.isEditing.set(true);
    this.modalError.set(null);
    this.currentUserData = {
      id: user.id,
      nombre: user.nombre,
      apellido: user.apellido,
      email: user.email,
      telefono: user.telefono || '',
      password: '',
      rol_id: user.rol?.id || user.rol_detalle?.id || null
    };
    this.showModal.set(true);
  }

  closeModal() {
    this.showModal.set(false);
    this.modalError.set(null);
  }

  private extractErrorMessage(err: any): string {
    if (err.error) {
      if (typeof err.error === 'string') return err.error;
      const messages: string[] = [];
      for (const key of Object.keys(err.error)) {
        const val = err.error[key];
        if (Array.isArray(val)) {
          messages.push(`${key}: ${val.join(', ')}`);
        } else if (typeof val === 'string') {
          messages.push(`${key}: ${val}`);
        }
      }
      if (messages.length > 0) return messages.join(' | ');
    }
    return 'Ocurrió un error inesperado. Intente nuevamente.';
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU3: Gestionar Usuarios (HU-05)
   * Diagrama de Comunicación – Creación/Edición de Usuario
   * Participantes:
   *   Actor  → Administrador del Centro
   *   IU     → IU_GestionUsuarios (Angular)
   *   CTR    → CTR_UsuarioService (Django REST)
   *   CE     → CE_Usuario_y_Rol (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  onSaveUser() {
    // --- Paso 1: Ingresar datos de nuevo usuario (email, rol, password) ---
    // El Actor (Admin Centro) completa el formulario con datos del usuario

    // Validación de contraseña en frontend
    const pwd = this.currentUserData.password;
    if (!this.isEditing() && !pwd) {
      this.modalError.set('La contraseña es obligatoria.');
      return;
    }
    if (pwd && !this.isPasswordValid(pwd)) {
      this.modalError.set('La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial.');
      return;
    }

    this.submitting.set(true);
    this.modalError.set(null);

    // Construir payload limpio
    let payload: any;
    if (this.isEditing()) {
      payload = {
        nombre: this.currentUserData.nombre,
        apellido: this.currentUserData.apellido,
        telefono: this.currentUserData.telefono,
        rol_id: this.currentUserData.rol_id
      };
      // Solo incluir password si el usuario la cambió
      if (pwd) {
        payload.password = pwd;
      }
    } else {
      const { id, ...rest } = this.currentUserData;
      payload = rest;
    }

    // --- Paso 2: POST /api/users/ + JWT Header ---
    // IU_GestionUsuarios envía los datos del nuevo usuario al CTR_UsuarioService
    const action$ = this.isEditing()
      ? this.userService.update(this.currentUserData.id, payload)
      : this.userService.create(payload);

    action$.subscribe({
      // --- Paso 11: 201 Created {usuario_creado} ---
      // CTR_UsuarioService confirma la creación del usuario
      next: () => {
        this.submitting.set(false);
        this.closeModal();
        this.loadUsers();
        // --- Paso 12: Mostrar confirmación 'Usuario creado' ---
        // IU_GestionUsuarios muestra el mensaje de éxito al Actor
        this.successMessage.set(this.isEditing() ? 'Usuario actualizado correctamente.' : 'Usuario registrado correctamente.');
        setTimeout(() => this.successMessage.set(null), 4000);
      },
      error: (err: any) => {
        this.submitting.set(false);
        this.modalError.set(this.extractErrorMessage(err));
      }
    });
    // NOTA: Los pasos 3-10 ocurren en el backend (CTR_UsuarioService ↔ CE_Usuario_y_Rol):
    //   Paso 3: Validar JWT, TenantMiddleware y rol Admin Centro
    //   Paso 4: Contexto tenant y permisos verificados
    //   Paso 5: Validar datos y unicidad de email
    //   Paso 6: Email disponible
    //   Paso 7: SELECT rol WHERE id = ?
    //   Paso 8: Rol encontrado
    //   Paso 9: INSERT INTO accounts_usuario (email, password_hash, rol_id)
    //   Paso 10: Usuario guardado en esquema tenant
  }

  toggleUserStatus(user: Usuario) {
    this.userService.toggleStatus(user.id).subscribe({
      next: () => this.loadUsers(),
      error: (err: any) => {
        this.errorMessage.set('Error al cambiar el estado del usuario.');
        setTimeout(() => this.errorMessage.set(null), 4000);
      }
    });
  }
}
