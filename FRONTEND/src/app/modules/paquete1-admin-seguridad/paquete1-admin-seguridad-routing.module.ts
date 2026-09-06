import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { roleGuard } from '../../core/guards/role.guard';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { TenantListComponent } from './components/tenant-list/tenant-list.component';
import { TenantFormComponent } from './components/tenant-form/tenant-form.component';
import { CentroConfigComponent } from './components/centro-config/centro-config.component';
import { UserListComponent } from './components/user-list/user-list.component';
import { UserFormComponent } from './components/user-form/user-form.component';
import { RoleListComponent } from './components/role-list/role-list.component';
import { RoleFormComponent } from './components/role-form/role-form.component';

const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  {
    path: 'tenants',
    component: TenantListComponent,
    canActivate: [roleGuard],
    data: { roles: ['superadmin'] },
  },
  {
    path: 'tenants/new',
    component: TenantFormComponent,
    canActivate: [roleGuard],
    data: { roles: ['superadmin'] },
  },
  {
    path: 'centro-config',
    component: CentroConfigComponent,
    canActivate: [roleGuard],
    data: { roles: ['superadmin', 'admincentro'] },
  },
  {
    path: 'users',
    component: UserListComponent,
    canActivate: [roleGuard],
    data: { roles: ['superadmin', 'admincentro'] },
  },
  {
    path: 'users/new',
    component: UserFormComponent,
    canActivate: [roleGuard],
    data: { roles: ['superadmin', 'admincentro'] },
  },
  {
    path: 'roles',
    component: RoleListComponent,
    canActivate: [roleGuard],
    data: { roles: ['superadmin', 'admincentro'] },
  },
  {
    path: 'roles/new',
    component: RoleFormComponent,
    canActivate: [roleGuard],
    data: { roles: ['superadmin', 'admincentro'] },
  },
  {
    path: '',
    loadChildren: () =>
      import('../paquete2-gestion-clinica/paquete2-gestion-clinica.module').then(
        (m) => m.Paquete2GestionClinicaModule
      ),
  },
  {
    path: '',
    loadChildren: () =>
      import(
        '../paquete3-agenda-comunicacion/paquete3-agenda-comunicacion.module'
      ).then((m) => m.Paquete3AgendaComunicacionModule),
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class Paquete1AdminSeguridadRoutingModule {}
