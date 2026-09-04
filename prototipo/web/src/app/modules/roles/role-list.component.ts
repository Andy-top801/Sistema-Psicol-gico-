import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RoleService } from '../../core/services/role.service';
import { Rol, Permiso } from '../../core/models';

@Component({
  selector: 'app-role-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="roles-wrapper">
      <div class="page-header d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="page-title">Matriz de Roles y Permisos (RBAC)</h1>
          <p class="page-subtitle">Control de acceso granular por rol para salvaguardar la privacidad clínica</p>
        </div>
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

      <!-- Roles & Permissions Matrix Grid -->
      <div class="roles-grid">
        <div *ngFor="let rol of roles()" class="role-card glass-panel">
          <div class="role-header">
            <div class="role-icon">
              <i class="fa-solid fa-shield-halved"></i>
            </div>
            <div>
              <h3 class="role-name">{{ rol.nombre }}</h3>
              <p class="role-desc">{{ rol.descripcion }}</p>
            </div>
          </div>

          <div class="permissions-section">
            <h4 class="perm-title">Permisos Asignados ({{ rol.permisos?.length || 0 }})</h4>
            
            <div class="permissions-list">
              <div *ngFor="let p of allPermisos()" class="perm-item">
                <label class="perm-checkbox-label">
                  <input 
                    type="checkbox" 
                    [checked]="hasPermission(rol, p.id)" 
                    (change)="togglePermission(rol, p.id, $event)">
                  <div class="perm-info">
                    <span class="perm-name">{{ p.nombre }}</span>
                    <span class="perm-module badge badge-info">{{ p.modulo }}</span>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <div class="role-footer mt-4">
            <button class="btn btn-primary btn-sm btn-block" (click)="saveRolePermissions(rol)">
              <i class="fa-solid fa-floppy-disk"></i> Guardar Permisos de {{ rol.nombre }}
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .page-title { font-size: 1.5rem; font-weight: 800; }
    .page-subtitle { font-size: 0.88rem; color: var(--text-muted); }
    .roles-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 20px; }
    .role-card { padding: 24px; display: flex; flex-direction: column; }
    .role-header { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 18px; border-bottom: 1px solid var(--border-glass); padding-bottom: 16px; }
    .role-icon { width: 44px; height: 44px; border-radius: 12px; background: rgba(99, 102, 241, 0.15); display: flex; align-items: center; justify-content: center; font-size: 1.3rem; color: #a5b4fc; }
    .role-name { font-size: 1.15rem; font-weight: 800; }
    .role-desc { font-size: 0.82rem; color: var(--text-muted); margin-top: 2px; }
    .perm-title { font-size: 0.82rem; font-weight: 700; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }
    .permissions-list { max-height: 280px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding-right: 4px; }
    .perm-item { background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border-glass); border-radius: 8px; padding: 8px 12px; }
    .perm-checkbox-label { display: flex; align-items: center; gap: 10px; cursor: pointer; width: 100%; }
    .perm-info { display: flex; align-items: center; justify-content: space-between; flex: 1; }
    .perm-name { font-size: 0.85rem; font-weight: 600; }
    .perm-module { font-size: 0.68rem; }
    .btn-block { width: 100%; }
    .mb-4 { margin-bottom: 20px; }
    .mt-4 { margin-top: 18px; }
    .d-flex { display: flex; }
    .justify-content-between { justify-content: space-between; }
    .align-items-center { align-items: center; }
    .alert-box { padding: 12px 16px; border-radius: 10px; font-size: 0.88rem; display: flex; align-items: center; gap: 10px; }
    .alert-danger { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; }
    .alert-success { background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #6ee7b7; }
    .alert-close { background: none; border: none; color: inherit; font-size: 1.2rem; cursor: pointer; margin-left: auto; }
  `]
})
export class RoleListComponent implements OnInit {
  roles = signal<Rol[]>([]);
  allPermisos = signal<Permiso[]>([]);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  // Mapa local temporal para edición reactiva: rolId -> Set de permisoIds
  rolePermMap = new Map<number, Set<number>>();

  constructor(private roleService: RoleService) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.roleService.getPermisos().subscribe({
      next: (perms: Permiso[]) => this.allPermisos.set(perms),
      error: () => {
        this.errorMessage.set('Error al cargar los permisos.');
      }
    });

    this.roleService.getRoles().subscribe({
      next: (rolesData: Rol[]) => {
        this.roles.set(rolesData);
        rolesData.forEach((r: Rol) => {
          const ids = new Set<number>((r.permisos || []).map((p: Permiso) => p.id));
          this.rolePermMap.set(r.id, ids);
        });
      },
      error: () => {
        this.errorMessage.set('Error al cargar los roles.');
      }
    });
  }

  hasPermission(rol: Rol, permisoId: number): boolean {
    return this.rolePermMap.get(rol.id)?.has(permisoId) || false;
  }

  togglePermission(rol: Rol, permisoId: number, event: Event) {
    const isChecked = (event.target as HTMLInputElement).checked;
    const currentSet = this.rolePermMap.get(rol.id) || new Set<number>();
    if (isChecked) {
      currentSet.add(permisoId);
    } else {
      currentSet.delete(permisoId);
    }
    this.rolePermMap.set(rol.id, currentSet);
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU4: Gestionar Roles y Permisos (HU-06)
   * Diagrama de Comunicación – Actualización de Permisos de un Rol
   * Participantes:
   *   Actor  → Administrador del Centro
   *   IU     → IU_GestionRoles (Angular)
   *   CTR    → CTR_RolService (Django REST)
   *   CE     → CE_Rol_y_Permiso (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  saveRolePermissions(rol: Rol) {
    // --- Paso 1: Seleccionar permisos para el rol (rol_id, [permiso_ids]) ---
    // El Actor (Admin Centro) marca/desmarca checkboxes de permisos
    const selectedIds = Array.from(this.rolePermMap.get(rol.id) || []);

    // --- Paso 2: PUT /api/roles/{id}/ {permisos: [ids]} + JWT ---
    // IU_GestionRoles envía la lista de permisos seleccionados al CTR_RolService
    this.roleService.updateRole(rol.id, {
      nombre: rol.nombre,
      descripcion: rol.descripcion,
      permiso_ids: selectedIds
    }).subscribe({
      // --- Paso 11: 200 OK {rol_actualizado} ---
      // CTR_RolService confirma la actualización de permisos
      next: () => {
        this.loadData();
        // --- Paso 12: Mostrar confirmación 'Permisos actualizados' ---
        // IU_GestionRoles muestra el mensaje de éxito al Actor
        this.successMessage.set(`Permisos de "${rol.nombre}" actualizados correctamente.`);
        setTimeout(() => this.successMessage.set(null), 4000);
      },
      error: (err: any) => {
        this.errorMessage.set('Error al guardar los permisos del rol.');
        setTimeout(() => this.errorMessage.set(null), 4000);
      }
    });
    // NOTA: Los pasos 3-10 ocurren en el backend (CTR_RolService ↔ CE_Rol_y_Permiso):
    //   Paso 3: Validar JWT, permisos RBAC y esquema tenant
    //   Paso 4: Permisos administrativos verificados
    //   Paso 5: SELECT * FROM accounts_permiso WHERE id IN (?)
    //   Paso 6: Permisos validados
    //   Paso 7: DELETE FROM accounts_rol_permiso WHERE rol_id = ?
    //   Paso 8: Permisos anteriores desvinculados
    //   Paso 9: INSERT INTO accounts_rol_permiso (rol_id, permiso_id)
    //   Paso 10: Nuevos permisos registrados en esquema
  }
}
