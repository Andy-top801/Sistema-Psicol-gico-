import { Component, OnInit, signal } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../services/auth.service';
import { ThemeService } from '../../core/services/theme.service';
import { TenantContextService } from '../../core/services/tenant-context.service';
import { PORTAL_NAV_ITEMS, NavItem } from '../nav.config';

@Component({
  selector: 'app-patient-layout',
  standalone: false,
  templateUrl: './patient-layout.component.html',
  styleUrls: ['./patient-layout.component.css'],
})
export class PatientLayoutComponent implements OnInit {
  userName = '';
  centerName = '';
  navItems: NavItem[] = PORTAL_NAV_ITEMS;
  menuOpen = signal(false);

  constructor(
    private authService: AuthService,
    private router: Router,
    private tenant: TenantContextService,
    public theme: ThemeService
  ) {}

  ngOnInit(): void {
    this.userName = this.authService.displayName() || 'Paciente';
    this.centerName = this.tenant.isPublicDomain
      ? 'SIGEPSI'
      : this.tenant.prettyName;
  }

  get initials(): string {
    const parts = this.userName.trim().split(/\s+/);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return this.userName.slice(0, 2).toUpperCase();
  }

  toggleMenu(): void {
    this.menuOpen.update((v) => !v);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
