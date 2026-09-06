import { NgModule } from '@angular/core';

import { SharedModule } from '../../shared/shared.module';
import { Paquete1AdminSeguridadRoutingModule } from './paquete1-admin-seguridad-routing.module';

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
    DashboardComponent,
    TenantListComponent,
    TenantFormComponent,
    CentroConfigComponent,
    UserListComponent,
    UserFormComponent,
    RoleListComponent,
    RoleFormComponent,
  ],
  imports: [SharedModule, Paquete1AdminSeguridadRoutingModule],
})
export class Paquete1AdminSeguridadModule {}
