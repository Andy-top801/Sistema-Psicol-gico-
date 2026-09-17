import { Routes } from '@angular/router';
import { authGuard, superAdminGuard, adminCentroGuard } from './core/guards/auth.guard';
import { LoginComponent } from './modules/auth/login/login.component';
import { PasswordResetComponent } from './modules/auth/password-reset/password-reset.component';
import { ForcePasswordChangeComponent } from './modules/auth/force-password-change/force-password-change.component';
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
// Incremento Funcional Sprint 2 (CU14 a CU19 y HU-35)
import { IntakeConfigComponent } from './modules/intake/intake-config.component';
import { HistoriaClinicaListComponent } from './modules/historias-clinicas/historia-clinica-list.component';
import { HistoriaClinicaDetalleComponent } from './modules/historias-clinicas/historia-clinica-detalle.component';
import { NotaSoapEditorComponent } from './modules/notas-soap/nota-soap-editor.component';
import { TareasGestorComponent } from './modules/tareas/tareas-gestor.component';
import { ConsentimientosHubComponent } from './modules/consentimientos/consentimientos-hub.component';
import { DerivacionFormComponent } from './modules/derivaciones/derivacion-form.component';
// Punto 7+8: Landing Page SaaS con Stripe
import { LandingPageComponent } from './modules/landing/landing-page.component';
import { CheckoutSuccessComponent } from './modules/landing/checkout-success.component';

export const routes: Routes = [
  // Rutas públicas — Landing Page y Suscripción (Punto 7+8)
  { path: 'landing', component: LandingPageComponent },
  { path: 'checkout-success', component: CheckoutSuccessComponent },
  { path: 'login', component: LoginComponent },
  { path: 'password-reset', component: PasswordResetComponent },
  { path: 'force-password-change', component: ForcePasswordChangeComponent, canActivate: [authGuard] },
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
      // Incremento Funcional Sprint 2
      { path: 'intake', component: IntakeConfigComponent },
      { path: 'historias-clinicas', component: HistoriaClinicaListComponent },
      { path: 'historias-clinicas/:id', component: HistoriaClinicaDetalleComponent },
      { path: 'notas-soap/nueva', component: NotaSoapEditorComponent },
      { path: 'notas-soap/:id', component: NotaSoapEditorComponent },
      { path: 'tareas-terapeuticas', component: TareasGestorComponent },
      { path: 'consentimientos', component: ConsentimientosHubComponent },
      { path: 'derivaciones', component: DerivacionFormComponent },
      { path: 'derivaciones/nueva', component: DerivacionFormComponent },
    ]
  },
  { path: '**', redirectTo: 'landing' }
];
