import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { PsicologoListComponent } from './components/psicologo-list/psicologo-list.component';
import { PacienteListComponent } from './components/paciente-list/paciente-list.component';
import { AlertaListComponent } from './components/alerta-list/alerta-list.component';

const routes: Routes = [
  { path: 'psicologos', component: PsicologoListComponent },
  { path: 'pacientes', component: PacienteListComponent },
  { path: 'alertas', component: AlertaListComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class Paquete2GestionClinicaRoutingModule { }
