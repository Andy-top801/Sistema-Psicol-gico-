import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { PortalHomeComponent } from './components/portal-home/portal-home.component';
import { MisCitasComponent } from './components/mis-citas/mis-citas.component';
import { PortalTeleconsultaComponent } from './components/portal-teleconsulta/portal-teleconsulta.component';
import { PerfilComponent } from './components/perfil/perfil.component';

const routes: Routes = [
  { path: '', component: PortalHomeComponent },
  { path: 'citas', component: MisCitasComponent },
  { path: 'teleconsulta', component: PortalTeleconsultaComponent },
  { path: 'perfil', component: PerfilComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class PortalRoutingModule {}
