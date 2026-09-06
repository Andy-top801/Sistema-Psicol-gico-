import { Component, HostListener, OnInit, signal } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../services/auth.service';
import { ThemeService } from '../../core/services/theme.service';
import { TenantContextService } from '../../core/services/tenant-context.service';
import { ROLE_LABEL } from '../../core/models/user.model';
import { NAV_ITEMS, NavItem } from '../nav.config';

@Component({
  selector: 'app-admin-layout',
  standalone: false,
  templateUrl: './admin-layout.component.html',
  styleUrls: ['./admin-layout.component.css'],
})
export class AdminLayoutComponent implements OnInit {
  userName = 'Usuario';
  userRole = '';
  userEmail = '';
  centerName = '';

  drawerOpen = signal(false);
  collapsed = signal(this.readCollapsed());
  userMenuOpen = signal(false);

  navItems: NavItem[] = [];

  constructor(
    private authService: AuthService,
    private router: Router,
    private tenant: TenantContextService,
    public theme: ThemeService
  ) {}

  ngOnInit(): void {
    const u = this.authService.currentUser();
    this.userName = this.authService.displayName() || 'Usuario';
    this.userEmail = u?.email ?? '';
    this.userRole = ROLE_LABEL[this.authService.primaryRole()];
    this.centerName = this.tenant.isPublicDomain
      ? 'Plataforma SIGEPSI'
      : this.tenant.prettyName;
    this.navItems = NAV_ITEMS.filter((i: NavItem) =>
      this.authService.hasAnyRole(i.roles)
    );
  }

  get userInitials(): string {
    const parts = this.userName.trim().split(/\s+/);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return this.userName.slice(0, 2).toUpperCase();
  }

  toggleDrawer(): void {
    this.drawerOpen.update((v) => !v);
  }
  closeDrawer(): void {
    this.drawerOpen.set(false);
  }
  toggleCollapsed(): void {
    this.collapsed.update((v) => !v);
    try {
      localStorage.setItem('sigepsi_sidebar_collapsed', String(this.collapsed()));
    } catch {
      /* ignore */
    }
  }
  toggleUserMenu(): void {
    this.userMenuOpen.update((v) => !v);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  @HostListener('document:keydown.escape')
  onEsc(): void {
    this.closeDrawer();
    this.userMenuOpen.set(false);
  }

  private readCollapsed(): boolean {
    try {
      return localStorage.getItem('sigepsi_sidebar_collapsed') === 'true';
    } catch {
      return false;
    }
  }
}
