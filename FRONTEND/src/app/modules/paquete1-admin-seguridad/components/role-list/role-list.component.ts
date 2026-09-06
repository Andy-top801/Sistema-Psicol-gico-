import { Component, OnInit } from '@angular/core';
import { RoleService } from '../../../../services/role.service';

@Component({
  selector: 'app-role-list',
  standalone: false,
  templateUrl: './role-list.component.html',
  styleUrls: ['./role-list.component.css']
})
export class RoleListComponent implements OnInit {
  roles: any[] = [];
  isLoading = true;

  constructor(private roleService: RoleService) {}

  ngOnInit(): void {
    this.loadRoles();
  }

  loadRoles() {
    this.isLoading = true;
    this.roleService.getRoles().subscribe({
      next: (data) => {
        this.roles = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error cargando roles', err);
        this.isLoading = false;
      }
    });
  }
}
