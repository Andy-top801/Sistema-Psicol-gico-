import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

import { Paquete1AdminSeguridadRoutingModule } from './paquete1-admin-seguridad-routing.module';
import { AdminLayoutComponent } from './components/admin-layout/admin-layout.component';
import { LoginComponent } from './components/login/login.component';
import { RegisterAdminComponent } from './components/register-admin/register-admin.component';
import { PasswordResetComponent } from './components/password-reset/password-reset.component';
import { PasswordResetConfirmComponent } from './components/password-reset-confirm/password-reset-confirm.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { TenantListComponent } from './components/tenant-list/tenant-list.component';
import { TenantFormComponent } from './components/tenant-form/tenant-form.component';
import { CentroConfigComponent } from './components/centro-config/centro-config.component';
import { UserListComponent } from './components/user-list/user-list.component';
import { UserFormComponent } from './components/user-form/user-form.component';
import { RoleListComponent } from './components/role-list/role-list.component';
import { RoleFormComponent } from './components/role-form/role-form.component';

@NgModule({
  declarations: [
    AdminLayoutComponent,
    LoginComponent,
    RegisterAdminComponent,
    PasswordResetComponent,
    PasswordResetConfirmComponent,
    DashboardComponent,
    TenantListComponent,
    TenantFormComponent,
    CentroConfigComponent,
    UserListComponent,
    UserFormComponent,
    RoleListComponent,
    RoleFormComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    Paquete1AdminSeguridadRoutingModule
  ]
})
export class Paquete1AdminSeguridadModule { }
