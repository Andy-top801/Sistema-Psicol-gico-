import { Component, OnInit } from '@angular/core';
import { UserService } from '../../../../services/user.service';
import { RoleService } from '../../../../services/role.service';
import { TenantContextService } from '../../../../core/services/tenant-context.service';
import { normalizeRole } from '../../../../core/models/user.model';

export interface UserItem {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  centro_nombre: string;
  rol_nombre: string;
  is_active: boolean;
}

@Component({
  selector: 'app-user-list',
  standalone: false,
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.css'],
})
export class UserListComponent implements OnInit {
  users: UserItem[] = [];
  filteredUsers: UserItem[] = [];
  roles: any[] = [];
  isLoading = true;
  loadError = false;
  selectedRole = 'all';
  centerName = '';

  psicologosCount = 0;
  recepcionistasCount = 0;
  coordinadoresCount = 0;
  adminCount = 0;

  showPermissionModal = false;
  selectedUserForPerms: UserItem | null = null;
  permModules = [
    { name: 'Expedientes de pacientes', read: true, write: true, delete: false },
    { name: 'Agenda y citas', read: true, write: true, delete: true },
    { name: 'Teleconsulta', read: true, write: false, delete: false },
    { name: 'Configuración del centro', read: false, write: false, delete: false },
  ];

  constructor(
    private userService: UserService,
    private roleService: RoleService,
    tenant: TenantContextService
  ) {
    this.centerName = tenant.isPublicDomain ? 'Plataforma' : tenant.prettyName;
  }

  ngOnInit(): void {
    this.roleService.getRoles().subscribe({
      next: (data) => (this.roles = data ?? []),
      error: () => {},
    });
    this.loadUsers();
  }

  loadUsers(): void {
    this.isLoading = true;
    this.loadError = false;
    this.userService.getUsers().subscribe({
      next: (data: any[]) => {
        this.users = (data ?? []).map((u) => ({
          id: String(u.id),
          first_name: u.first_name || 'Usuario',
          last_name: u.last_name || '',
          email: u.email,
          centro_nombre: this.centerName,
          rol_nombre: this.extractRole(u),
          is_active: u.is_active ?? true,
        }));
        this.recalcStats();
        this.applyFilter();
        this.isLoading = false;
      },
      error: () => {
        this.loadError = true;
        this.isLoading = false;
      },
    });
  }

  private extractRole(u: any): string {
    const details = u.roles_details ?? u.roles;
    if (Array.isArray(details) && details.length) {
      const first = details[0];
      const name = typeof first === 'string' ? first : first?.name;
      if (name) return String(name).toUpperCase();
    }
    if (u.is_superuser) return 'SUPERADMIN';
    return 'SIN ROL';
  }

  private recalcStats(): void {
    const count = (frag: string) =>
      this.users.filter((u) => normalizeRole(u.rol_nombre).includes(frag)).length;
    this.psicologosCount = count('psicolog');
    this.recepcionistasCount = count('recepcion');
    this.coordinadoresCount = count('coordinador');
    this.adminCount = count('admin');
  }

  onRoleSelect(role: string): void {
    this.selectedRole = role;
    this.applyFilter();
  }

  applyFilter(): void {
    if (this.selectedRole === 'all') {
      this.filteredUsers = [...this.users];
    } else {
      const frag = this.selectedRole.toLowerCase();
      this.filteredUsers = this.users.filter((u) =>
        normalizeRole(u.rol_nombre).includes(frag)
      );
    }
  }

  toggleActive(user: UserItem): void {
    const newState = !user.is_active;
    user.is_active = newState;
    this.userService.patchUser(user.id, { is_active: newState }).subscribe({
      next: () => {},
      error: () => (user.is_active = !newState),
    });
  }

  openPermissions(user: UserItem): void {
    this.selectedUserForPerms = user;
    this.showPermissionModal = true;
  }

  closePermissions(): void {
    this.showPermissionModal = false;
    this.selectedUserForPerms = null;
  }

  savePermissions(): void {
    this.closePermissions();
  }
}
