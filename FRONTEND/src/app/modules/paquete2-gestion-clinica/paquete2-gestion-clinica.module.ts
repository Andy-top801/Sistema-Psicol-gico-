import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { Paquete2GestionClinicaRoutingModule } from './paquete2-gestion-clinica-routing.module';
import { PsicologoListComponent } from './components/psicologo-list/psicologo-list.component';
import { PacienteListComponent } from './components/paciente-list/paciente-list.component';
import { AlertaListComponent } from './components/alerta-list/alerta-list.component';

@NgModule({
  declarations: [
    PsicologoListComponent,
    PacienteListComponent,
    AlertaListComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    Paquete2GestionClinicaRoutingModule
  ]
})
export class Paquete2GestionClinicaModule { }
