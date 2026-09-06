import { NgModule } from '@angular/core';

import { SharedModule } from '../../shared/shared.module';
import { Paquete3AgendaComunicacionRoutingModule } from './paquete3-agenda-comunicacion-routing.module';
import { CitaAgendaComponent } from './components/cita-agenda/cita-agenda.component';
import { TeleconsultaListComponent } from './components/teleconsulta-list/teleconsulta-list.component';

@NgModule({
  declarations: [CitaAgendaComponent, TeleconsultaListComponent],
  imports: [SharedModule, Paquete3AgendaComunicacionRoutingModule],
})
export class Paquete3AgendaComunicacionModule {}
