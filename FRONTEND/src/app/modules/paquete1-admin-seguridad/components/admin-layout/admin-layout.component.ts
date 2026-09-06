import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../../../services/auth.service';

@Component({
  selector: 'app-admin-layout',
  standalone: false,
  templateUrl: './admin-layout.component.html',
  styleUrls: ['./admin-layout.component.css']
})
export class AdminLayoutComponent implements OnInit {
  userName: string = 'Dra. Rosa M. Morales';
  userRole: string = 'SuperAdmin';
  userEmail: string = '';
  centerName: string = 'Centro MenteSana';
  centerSub: string = 'Sede Central Medellín';
  activeSchema: string = 'public';
  searchQuery: string = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const user = this.authService.getUser();
    if (user) {
      if (user.first_name || user.last_name) {
        this.userName = `${user.first_name || ''} ${user.last_name || ''}`.trim();
      } else if (user.email) {
        this.userName = user.email.split('@')[0];
      }
      this.userEmail = user.email || '';
      this.userRole = user.rol_nombre || (user.is_superuser ? 'SuperAdmin Global' : 'Admin Centro');
    }
  }

  get userInitials(): string {
    const parts = this.userName.split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return this.userName.slice(0, 2).toUpperCase();
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
