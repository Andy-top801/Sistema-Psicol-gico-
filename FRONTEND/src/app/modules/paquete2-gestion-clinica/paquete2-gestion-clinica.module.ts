import { NgModule } from '@angular/core';

import { SharedModule } from '../../shared/shared.module';
import { Paquete2GestionClinicaRoutingModule } from './paquete2-gestion-clinica-routing.module';
import { PsicologoListComponent } from './components/psicologo-list/psicologo-list.component';
import { PacienteListComponent } from './components/paciente-list/paciente-list.component';
import { AlertaListComponent } from './components/alerta-list/alerta-list.component';

@NgModule({
  declarations: [
    PsicologoListComponent,
    PacienteListComponent,
    AlertaListComponent,
  ],
  imports: [SharedModule, Paquete2GestionClinicaRoutingModule],
})
export class Paquete2GestionClinicaModule {}
