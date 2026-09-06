import { Routes } from '@angular/router';
import { authGuard, superAdminGuard, adminCentroGuard } from './core/guards/auth.guard';
import { LoginComponent } from './modules/auth/login/login.component';
import { PasswordResetComponent } from './modules/auth/password-reset/password-reset.component';
import { MainLayoutComponent } from './layout/main-layout.component';
import { DashboardComponent } from './modules/dashboard/dashboard.component';
import { TenantListComponent } from './modules/tenants/tenant-list.component';
import { UserListComponent } from './modules/users/user-list.component';
import { RoleListComponent } from './modules/roles/role-list.component';
import { CentroConfigComponent } from './modules/centro/centro-config.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'password-reset', component: PasswordResetComponent },
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'tenants', component: TenantListComponent, canActivate: [superAdminGuard] },
      { path: 'users', component: UserListComponent, canActivate: [adminCentroGuard] },
      { path: 'roles', component: RoleListComponent, canActivate: [adminCentroGuard] },
      { path: 'centro', component: CentroConfigComponent, canActivate: [adminCentroGuard] },
    ]
  },
  { path: '**', redirectTo: 'login' }
];
