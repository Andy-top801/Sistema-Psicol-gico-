import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CitaAgendaComponent } from './components/cita-agenda/cita-agenda.component';
import { TeleconsultaListComponent } from './components/teleconsulta-list/teleconsulta-list.component';

const routes: Routes = [
  { path: '', redirectTo: 'citas', pathMatch: 'full' },
  { path: 'citas', component: CitaAgendaComponent },
  { path: 'teleconsultas', component: TeleconsultaListComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class Paquete3AgendaComunicacionRoutingModule { }
