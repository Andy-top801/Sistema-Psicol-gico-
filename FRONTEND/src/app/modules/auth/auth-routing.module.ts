import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { LoginComponent } from './components/login/login.component';
import { RegisterAdminComponent } from './components/register-admin/register-admin.component';
import { PasswordResetComponent } from './components/password-reset/password-reset.component';
import { PasswordResetConfirmComponent } from './components/password-reset-confirm/password-reset-confirm.component';

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register-admin', component: RegisterAdminComponent },
  { path: 'password-reset', component: PasswordResetComponent },
  { path: 'password-reset/confirm', component: PasswordResetConfirmComponent },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class AuthRoutingModule {}
