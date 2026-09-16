import { Routes } from '@angular/router';
import { authGuard, superAdminGuard, adminCentroGuard } from './core/guards/auth.guard';
import { LoginComponent } from './modules/auth/login/login.component';
import { PasswordResetComponent } from './modules/auth/password-reset/password-reset.component';
import { MainLayoutComponent } from './layout/main-layout.component';
import { DashboardComponent } from './modules/dashboard/dashboard.component';
import { TenantListComponent } from './modules/tenants/tenant-list.component';
import { UserListComponent } from './modules/users/user-list.component';
import { RoleListComponent } from './modules/roles/role-list.component';
import { CentroConfigComponent } from './modules/centro/centro-config.component';
import { PsicologoListComponent } from './modules/psicologos/psicologo-list.component';
import { PacienteListComponent } from './modules/pacientes/paciente-list.component';
import { CalendarioAgendaComponent } from './modules/agenda/calendario-agenda.component';
import { TeleconsultaRoomComponent } from './modules/teleconsulta/teleconsulta-room.component';
import { AuditLogComponent } from './modules/audit/audit-log.component';
import { ReportesHubComponent } from './modules/reportes/reportes-hub.component';
import { ReporteVisorComponent } from './modules/reportes/reporte-visor.component';
import { ReportePersonalizadoComponent } from './modules/reportes/reporte-personalizado.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'password-reset', component: PasswordResetComponent },
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'tenants', component: TenantListComponent, canActivate: [superAdminGuard] },
      { path: 'audit', component: AuditLogComponent, canActivate: [superAdminGuard] },
      { path: 'users', component: UserListComponent, canActivate: [adminCentroGuard] },
      { path: 'roles', component: RoleListComponent, canActivate: [adminCentroGuard] },
      { path: 'centro', component: CentroConfigComponent, canActivate: [adminCentroGuard] },
      // Incremento Funcional Sprint 1
      { path: 'agenda', component: CalendarioAgendaComponent },
      { path: 'psicologos', component: PsicologoListComponent },
      { path: 'pacientes', component: PacienteListComponent },
      { path: 'teleconsulta/:id', component: TeleconsultaRoomComponent },
      // Módulo de Reportes Personalizables (Punto 5)
      { path: 'reportes', component: ReportesHubComponent, canActivate: [adminCentroGuard] },
      { path: 'reportes/personalizado', component: ReportePersonalizadoComponent, canActivate: [adminCentroGuard] },
      { path: 'reportes/:fuente', component: ReporteVisorComponent, canActivate: [adminCentroGuard] },
    ]
  },
  { path: '**', redirectTo: 'login' }
];
