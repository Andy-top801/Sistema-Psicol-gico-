import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { PasswordResetComponent } from './components/password-reset/password-reset.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { TenantFormComponent } from './components/tenant-form/tenant-form.component';
import { UserListComponent } from './components/user-list/user-list.component';
import { UserFormComponent } from './components/user-form/user-form.component';
import { RoleListComponent } from './components/role-list/role-list.component';
import { RoleFormComponent } from './components/role-form/role-form.component';
import { AdminLayoutComponent } from './components/admin-layout/admin-layout.component';

import { PasswordResetConfirmComponent } from './components/password-reset-confirm/password-reset-confirm.component';

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'password-reset', component: PasswordResetComponent },
  { path: 'password-reset/confirm', component: PasswordResetConfirmComponent },
  { 
    path: '', 
    component: AdminLayoutComponent,
    children: [
      { path: 'dashboard', component: DashboardComponent },
      { path: 'tenants/new', component: TenantFormComponent },
      { path: 'users', component: UserListComponent },
      { path: 'users/new', component: UserFormComponent },
      { path: 'roles', component: RoleListComponent },
      { path: 'roles/new', component: RoleFormComponent },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class Paquete1AdminSeguridadRoutingModule { }
