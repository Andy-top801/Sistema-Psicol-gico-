import { Component, OnInit } from '@angular/core';
import { UserService } from '../../../../services/user.service';
import { RoleService } from '../../../../services/role.service';

@Component({
  selector: 'app-user-list',
  standalone: false,
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.css']
})
export class UserListComponent implements OnInit {
  users: any[] = [];
  roles: any[] = [];
  isLoading = true;

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
      next: (data) => {
        this.users = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error cargando usuarios', err);
        this.isLoading = false;
      }
    });
  }

  getRoleName(roles: number[]): string {
    if (!roles || roles.length === 0) return 'Sin Rol';
    const role = this.roles.find(r => r.id === roles[0]);
    return role ? role.name : 'Desconocido';
  }
}
