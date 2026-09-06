import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';
import { publicGuard } from './core/guards/public.guard';
import { STAFF_ROLES } from './core/models/user.model';

import { PublicLayoutComponent } from './layouts/public-layout/public-layout.component';
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout.component';
import { PatientLayoutComponent } from './layouts/patient-layout/patient-layout.component';

const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'login' },

  // Pantallas públicas (auth) — showcase + formulario.
  {
    path: '',
    component: PublicLayoutComponent,
    canActivate: [publicGuard],
    loadChildren: () =>
      import('./modules/auth/auth.module').then((m) => m.AuthModule),
  },

  // Panel administrativo — staff.
  {
    path: '',
    component: AdminLayoutComponent,
    canActivate: [authGuard, roleGuard],
    data: { roles: STAFF_ROLES },
    loadChildren: () =>
      import(
        './modules/paquete1-admin-seguridad/paquete1-admin-seguridad.module'
      ).then((m) => m.Paquete1AdminSeguridadModule),
  },

  // Portal del paciente.
  {
    path: 'portal',
    component: PatientLayoutComponent,
    canActivate: [authGuard, roleGuard],
    data: { roles: ['paciente'] },
    loadChildren: () =>
      import('./modules/portal/portal.module').then((m) => m.PortalModule),
  },

  { path: '**', redirectTo: 'login' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
