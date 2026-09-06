import { NgModule } from '@angular/core';

import { SharedModule } from '../../shared/shared.module';
import { PortalRoutingModule } from './portal-routing.module';

import { PortalHomeComponent } from './components/portal-home/portal-home.component';
import { MisCitasComponent } from './components/mis-citas/mis-citas.component';
import { PortalTeleconsultaComponent } from './components/portal-teleconsulta/portal-teleconsulta.component';
import { PerfilComponent } from './components/perfil/perfil.component';

@NgModule({
  declarations: [
    PortalHomeComponent,
    MisCitasComponent,
    PortalTeleconsultaComponent,
    PerfilComponent,
  ],
  imports: [SharedModule, PortalRoutingModule],
})
export class PortalModule {}
