import { Component, OnInit } from '@angular/core';
import { UserService } from '../../../../services/user.service';
import { RoleService } from '../../../../services/role.service';

export interface UserItem {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  centro_nombre: string;
  rol_nombre: string;
  especialidad: string;
  is_active: boolean;
  permisos?: string[];
}

@Component({
  selector: 'app-user-list',
  standalone: false,
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.css']
})
export class UserListComponent implements OnInit {
  users: UserItem[] = [];
  filteredUsers: UserItem[] = [];
  roles: any[] = [];
  isLoading = true;
  selectedRole = 'all';

  // Stats
  psicologosCount = 18;
  recepcionistasCount = 5;
  coordinadoresCount = 3;
  psiquiatrasCount = 4;

  // Modal de Permisos
  showPermissionModal = false;
  selectedUserForPerms: UserItem | null = null;
  permModules = [
    { name: 'Expedientes Pacientes', read: true, write: true, delete: false },
    { name: 'Agenda & Citas Médicas', read: true, write: true, delete: true },
    { name: 'Facturación & Pagos', read: true, write: false, delete: false },
    { name: 'Configuración del Centro', read: false, write: false, delete: false }
  ];

  constructor(
    private userService: UserService,
    private roleService: RoleService
  ) {}

  ngOnInit(): void {
    this.loadRoles();
    this.loadUsers();
  }

  loadRoles() {
    this.roleService.getRoles().subscribe({
      next: (data) => {
        this.roles = data;
      },
      error: (err) => console.error('Error cargando roles', err)
    });
  }

  loadUsers() {
    this.isLoading = true;
    this.userService.getUsers().subscribe({
      next: (data: any[]) => {
        if (data && data.length > 0) {
          this.users = data.map((u, i) => {
            const roleName = this.extractRole(u);
            return {
              id: u.id,
              first_name: u.first_name || 'Usuario',
              last_name: u.last_name || `#${u.id}`,
              email: u.email,
              centro_nombre: u.centro_nombre || 'Centro Psicológico MenteSana',
              rol_nombre: roleName,
              especialidad: u.especialidad || this.getDefaultSpecialty(roleName),
              is_active: u.is_active !== undefined ? u.is_active : true
            };
          });
        }

        // Si la BD contiene pocos usuarios, añadir los profesionales del wireframe
        if (this.users.length < 4) {
          const wireframeUsers: UserItem[] = [
            {
              id: 101,
              first_name: 'Carmen',
              last_name: 'Valenzuela',
              email: 'c.valenzuela@mentesana.org',
              centro_nombre: 'Centro Psicológico MenteSana',
              rol_nombre: 'PSICÓLOGO',
              especialidad: 'Terapia Cognitivo-Conductual',
              is_active: true
            },
            {
              id: 102,
              first_name: 'Roberto',
              last_name: 'Mendoza',
              email: 'r.mendoza@sanmartin.com',
              centro_nombre: 'Clínica de Salud Mental San Martín',
              rol_nombre: 'COORDINADOR',
              especialidad: 'Gestión Clínica & Supervisión',
              is_active: true
            },
            {
              id: 103,
              first_name: 'Elena',
              last_name: 'Ríos',
              email: 'e.rios@mentesana.org',
              centro_nombre: 'Centro Psicológico MenteSana',
              rol_nombre: 'RECEPCIONISTA',
              especialidad: 'Admisión & Turnos',
              is_active: true
            },
            {
              id: 104,
              first_name: 'Alejandro',
              last_name: 'Sotomayor',
              email: 'a.sotomayor@redneuros.org',
              centro_nombre: 'Red Hospitalaria de Neuropsiquiatría',
              rol_nombre: 'PSIQUIATRA',
              especialidad: 'Neuropsiquiatría Adultos',
              is_active: true
            }
          ];

          // Evitar duplicados por email
          wireframeUsers.forEach(wu => {
            if (!this.users.some(u => u.email === wu.email)) {
              this.users.push(wu);
            }
          });
        }

        this.applyFilter();
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error cargando usuarios', err);
        this.isLoading = false;
      }
    });
  }

  extractRole(u: any): string {
    if (u.rol_nombre) return u.rol_nombre.toUpperCase();
    if (u.roles && u.roles.length > 0) {
      const r = this.roles.find(ro => ro.id === u.roles[0]);
      if (r) return r.name.toUpperCase();
    }
    if (u.is_superuser) return 'SUPERADMIN';
    return 'PSICÓLOGO';
  }

  getDefaultSpecialty(role: string): string {
    if (role.includes('PSIC')) return 'Terapia Cognitivo-Conductual';
    if (role.includes('COORD') || role.includes('ADMIN')) return 'Gestión Clínica & Supervisión';
    if (role.includes('RECEP')) return 'Admisión & Turnos';
    if (role.includes('PSIQUIATRA')) return 'Neuropsiquiatría Adultos';
    return 'Atención General';
  }

  onRoleSelect(role: string) {
    this.selectedRole = role;
    this.applyFilter();
  }

  applyFilter() {
    if (this.selectedRole === 'all') {
      this.filteredUsers = [...this.users];
    } else {
      this.filteredUsers = this.users.filter(u => 
        u.rol_nombre.toUpperCase().includes(this.selectedRole.toUpperCase())
      );
    }
  }

  toggleActive(user: UserItem) {
    const newState = !user.is_active;
    user.is_active = newState;
    this.userService.patchUser(user.id, { is_active: newState }).subscribe({
      next: () => {},
      error: () => {
        // revert if error
        user.is_active = !newState;
      }
    });
  }

  openPermissions(user: UserItem) {
    this.selectedUserForPerms = user;
    this.showPermissionModal = true;
  }

  closePermissions() {
    this.showPermissionModal = false;
    this.selectedUserForPerms = null;
  }

  savePermissions() {
    // Guardar permisos feedback
    this.closePermissions();
  }
}
